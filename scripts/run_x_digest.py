#!/usr/bin/env python3
"""
Main free pipeline:
  Agent-Reach / twitter-cli (cookie) → raw tweets
  → DeepSeek summarize (full text)
  → digests/YYYY-MM-DD.md
  → build GitHub Pages site under docs/

Usage:
  set DEEPSEEK_API_KEY=...
  set TWITTER_AUTH_TOKEN=...
  set TWITTER_CT0=...
  python scripts/run_x_digest.py

On GitHub Actions, use Secrets with the same names.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.deepseek_client import summarize_tweets  # noqa: E402
from src.x_fetch import (  # noqa: E402
    collect_tweets,
    load_accounts_config,
    save_raw_tweets,
    tweets_to_prompt_block,
)
from src.write_digest import digests_dir  # noqa: E402


def write_digest_md(
    date_slug: str,
    body: str,
    *,
    tweet_count: int,
    errors: list[str],
) -> Path:
    path = digests_dir() / f"{date_slug}.md"
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    header = [
        f"# Daily Digest — {date_slug}",
        "",
        f"- **Generated at**: {now}",
        f"- **Pipeline**: twitter-cli / Agent-Reach (cookie) → DeepSeek",
        f"- **Raw tweets fed to LLM**: {tweet_count}",
        f"- **X API**: not used (free cookie path)",
        "",
    ]
    if errors:
        header.append(f"- **Fetch warnings**: {len(errors)} (see raw json)")
        header.append("")
    header.extend(["---", "", body.strip(), "", "---", ""])
    header.append("_Auto-generated for GitHub Pages. Source: X via free cookie CLI + DeepSeek._")
    header.append("")
    path.write_text("\n".join(header), encoding="utf-8")
    return path


def rebuild_digest_index() -> None:
    d = digests_dir()
    files = sorted(d.glob("????-??-??.md"), reverse=True)
    lines = ["# Digests", "", "Newest first.", ""]
    for f in files:
        lines.append(f"- [{f.stem}](./{f.name})")
    lines.append("")
    (d / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="X (free) → DeepSeek → digests → site")
    parser.add_argument("--skip-fetch", action="store_true", help="Use existing x_raw/DATE.json")
    parser.add_argument("--skip-summarize", action="store_true", help="Only fetch raw tweets")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today local)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    date_slug = args.date or datetime.now().astimezone().strftime("%Y-%m-%d")
    cfg = load_accounts_config()

    if args.skip_fetch:
        raw_path = ROOT / "x_raw" / f"{date_slug}.json"
        if not raw_path.is_file():
            print(f"Missing {raw_path}", file=sys.stderr)
            return 2
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        print(f"Loaded raw tweets: {payload.get('count')} from {raw_path}")
    else:
        print("Collecting tweets via twitter-cli (Agent-Reach free X path)...")
        try:
            payload = collect_tweets(cfg)
        except Exception as e:
            print(f"X fetch failed: {e}", file=sys.stderr)
            return 1
        raw_path = save_raw_tweets(payload, date_slug)
        print(f"Saved raw: {raw_path} count={payload.get('count')}")
        if payload.get("errors"):
            print("Warnings:")
            for err in payload["errors"][:20]:
                print(f"  - {err}")

    tweets = payload.get("tweets") or []
    if not tweets:
        print("No tweets collected; abort summarize.", file=sys.stderr)
        return 3

    if args.skip_summarize:
        return 0

    if args.dry_run:
        print(tweets_to_prompt_block(tweets)[:2000])
        return 0

    print(f"Summarizing {len(tweets)} tweets with DeepSeek...")
    try:
        body = summarize_tweets(tweets_to_prompt_block(tweets), date_label=date_slug)
    except Exception as e:
        print(f"DeepSeek failed: {e}", file=sys.stderr)
        return 4

    path = write_digest_md(
        date_slug,
        body,
        tweet_count=len(tweets),
        errors=list(payload.get("errors") or []),
    )
    rebuild_digest_index()
    print(f"Wrote digest: {path}")

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_site", ROOT / "scripts" / "build_site.py"
    )
    if not spec or not spec.loader:
        print("Site build skipped: cannot load build_site.py", file=sys.stderr)
        return 0
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.build_site()
    print(f"Built site: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
