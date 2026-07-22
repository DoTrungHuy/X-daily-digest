#!/usr/bin/env python3
"""
Daily pipeline (main entry):

  twitter-cli (X Cookie, free) → x_raw/
  → DeepSeek → digests/
  → build GitHub Pages files under docs/

Usage:
  set DEEPSEEK_API_KEY=...
  set TWITTER_AUTH_TOKEN=...
  set TWITTER_CT0=...
  python scripts/run_daily.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.deepseek_client import summarize_tweets  # noqa: E402
from src.dedupe import (  # noqa: E402
    duplicate_status_ids_for_digest,
    published_status_ids,
    recent_digest_titles,
    reference_time_for_date,
    similar_titles_for_digest,
)
from src.digest_writer import write_digest_md  # noqa: E402
from src.x_fetch import (  # noqa: E402
    collect_tweets,
    filter_tweet_payload,
    load_accounts_config,
    save_raw_tweets,
    tweets_to_prompt_block,
)


def _build_site() -> Path:
    module_name = "build_site"
    spec = importlib.util.spec_from_file_location(
        module_name, ROOT / "scripts" / "build_site.py"
    )
    if not spec or not spec.loader:
        raise RuntimeError("cannot load scripts/build_site.py")

    mod = importlib.util.module_from_spec(spec)
    # Python 3.12 dataclasses expects dynamically loaded modules to be present
    # in sys.modules while class decorators are executed.
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod.build_site()


def main() -> int:
    parser = argparse.ArgumentParser(description="X (cookie) → DeepSeek → digests → site")
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-summarize", action="store_true")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    date_slug = args.date or datetime.now().astimezone().strftime("%Y-%m-%d")
    cfg = load_accounts_config()
    digest_dir = ROOT / "digests"
    reference_time = reference_time_for_date(date_slug)
    history_ids = published_status_ids(digest_dir, exclude_date=date_slug)

    if args.skip_fetch:
        raw_path = ROOT / "x_raw" / f"{date_slug}.json"
        if not raw_path.is_file():
            print(f"Missing {raw_path}", file=sys.stderr)
            return 2
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        print(f"Loaded raw: {payload.get('count')} tweets from {raw_path}")
        payload = filter_tweet_payload(
            payload,
            cfg,
            published_ids=history_ids,
            reference_time=reference_time,
        )
    else:
        print("Collecting X via twitter-cli (no paid X API)...")
        try:
            payload = collect_tweets(
                cfg,
                published_ids=history_ids,
                reference_time=reference_time,
            )
        except Exception as e:
            print(f"X fetch failed: {e}", file=sys.stderr)
            return 1
        raw_path = save_raw_tweets(payload, date_slug)
        print(f"Saved {raw_path} count={payload.get('count')}")
        for err in (payload.get("errors") or [])[:15]:
            print(f"  warn: {err}")

    stats = payload.get("filter_stats") or {}
    print(
        "Filter: "
        f"input={stats.get('input_count', 0)} "
        f"selected={stats.get('selected', payload.get('count', 0))} "
        f"run_duplicates={stats.get('run_duplicates', 0)} "
        f"history_duplicates={stats.get('history_duplicates', 0)} "
        f"too_old={stats.get('too_old', 0)} "
        f"unknown_time={stats.get('unknown_timestamp', 0)}"
    )

    tweets = payload.get("tweets") or []
    if not tweets:
        print("No tweets; abort.", file=sys.stderr)
        return 3

    if args.skip_summarize or args.dry_run:
        if args.dry_run:
            print(tweets_to_prompt_block(tweets)[:2500])
        return 0

    print(f"DeepSeek summarizing {len(tweets)} tweets...")
    try:
        body = summarize_tweets(
            tweets_to_prompt_block(tweets),
            date_label=date_slug,
            recent_titles=recent_digest_titles(
                digest_dir,
                exclude_date=date_slug,
                max_digests=7,
            ),
        )
    except Exception as e:
        print(f"DeepSeek failed: {e}", file=sys.stderr)
        return 4

    path = write_digest_md(
        date_slug,
        body,
        tweet_count=len(tweets),
        errors=list(payload.get("errors") or []),
    )
    print(f"Digest: {path}")

    duplicate_ids = duplicate_status_ids_for_digest(path, digest_dir)
    if duplicate_ids:
        print(
            "Duplicate guard failed: "
            f"{len(duplicate_ids)} source status ID(s) already appeared in history.",
            file=sys.stderr,
        )
        return 5

    similar_titles = similar_titles_for_digest(path, digest_dir)
    if similar_titles:
        print(
            "Topic warning: "
            f"{len(similar_titles)} title pair(s) resemble recent topics; "
            "exact source IDs are new."
        )

    site = _build_site()
    print(f"Site: {site}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
