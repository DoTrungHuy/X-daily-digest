#!/usr/bin/env python3
"""
Stage 1 entrypoint: authorize (first run) → fetch latest Grok Tasks email → write digests/YYYY-MM-DD.md

Usage (from project root, Python 3.10+ recommended):
  py -3.13 -m pip install -r requirements.txt
  py -3.13 scripts/run_daily.py

First run opens a browser for Google OAuth (need network access to Google).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python scripts/run_daily.py` without installing package
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gmail_client import (  # noqa: E402
    DEFAULT_CLIENT_SECRET,
    DEFAULT_TOKEN,
    env_query,
    fetch_latest_message,
    get_gmail_service,
)
from src.write_digest import write_digest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch latest Grok Tasks email and archive as digest")
    parser.add_argument(
        "--client-secret",
        default=DEFAULT_CLIENT_SECRET,
        help=f"OAuth client secret JSON (default: {DEFAULT_CLIENT_SECRET})",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help=f"Token cache path (default: {DEFAULT_TOKEN})",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Gmail search query (default: env GMAIL_QUERY or built-in Grok-oriented query)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print body to stdout only; do not write digests/",
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=2000,
        help="How many body chars to print (default 2000)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite digest even if same Gmail message id already archived",
    )
    args = parser.parse_args()

    query = args.query if args.query is not None else env_query()

    print("Connecting to Gmail API (readonly)...")
    try:
        service = get_gmail_service(
            client_secret_path=args.client_secret,
            token_path=args.token,
        )
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Authorization / connection failed: {e}", file=sys.stderr)
        print(
            "提示：首次授权需能打开 Google 的网络（部分网络环境需 VPN）。",
            file=sys.stderr,
        )
        return 1

    print(f"Searching mail with query: {query!r}")
    message = fetch_latest_message(service, query=query)
    if not message:
        print("没有找到匹配的邮件。")
        print("请确认：1) Grok Tasks 已发到此 Gmail  2) 用 --query 调整搜索条件")
        return 2

    print("=== 匹配到邮件 ===")
    print(f"From   : {message.get('from')}")
    print(f"Subject: {message.get('subject')}")
    print(f"Date   : {message.get('date')}")
    print(f"Id     : {message.get('id')}")
    body = message.get("body") or ""
    preview = body[: args.preview_chars]
    print("--- body preview ---")
    print(preview)
    if len(body) > args.preview_chars:
        print(f"... ({len(body) - args.preview_chars} more chars)")

    if args.print_only:
        return 0

    path, status = write_digest(message, force=args.force)
    if status == "skipped_same_id":
        print(f"\n已存在相同邮件 id，跳过写入: {path}")
    elif status == "overwritten":
        print(f"\n已覆盖写入: {path}")
    else:
        print(f"\n已写入: {path}")
    print(f"原始备份: digests/raw/{path.stem}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
