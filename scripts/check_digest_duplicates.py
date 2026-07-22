#!/usr/bin/env python3
"""Audit one generated digest against already published source IDs."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dedupe import (  # noqa: E402
    duplicate_status_ids_for_digest,
    similar_titles_for_digest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a digest for repeated X sources and similar recent topics."
    )
    parser.add_argument("--date", required=True, help="Digest date in YYYY-MM-DD format")
    args = parser.parse_args()

    try:
        parsed_date = date.fromisoformat(args.date)
    except ValueError:
        print("Invalid --date; expected YYYY-MM-DD.", file=sys.stderr)
        return 2
    if parsed_date.isoformat() != args.date:
        print("Invalid --date; expected zero-padded YYYY-MM-DD.", file=sys.stderr)
        return 2

    digest_dir = ROOT / "digests"
    path = digest_dir / f"{args.date}.md"
    if not path.is_file():
        print(f"Missing digest: {path}", file=sys.stderr)
        return 2

    duplicate_ids = duplicate_status_ids_for_digest(path, digest_dir)
    similar_titles = similar_titles_for_digest(path, digest_dir)
    print(
        f"Digest audit: exact_source_duplicates={len(duplicate_ids)} "
        f"similar_title_warnings={len(similar_titles)}"
    )
    if duplicate_ids:
        print("Duplicate source guard failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
