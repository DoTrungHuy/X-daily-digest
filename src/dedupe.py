"""Privacy-preserving freshness and cross-day duplicate controls."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo


TWITTER_EPOCH_MS = 1_288_834_974_657
STATUS_PATH_RE = re.compile(r"/status/(\d+)(?:\D|$)", re.IGNORECASE)
STATUS_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:x\.com|twitter\.com)/"
    r"(?:[^/\s)]+/)*status/(\d+)",
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"^标题：\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class FilterStats:
    input_count: int = 0
    run_duplicates: int = 0
    history_duplicates: int = 0
    too_old: int = 0
    unknown_timestamp: int = 0
    future_timestamp: int = 0
    fresh_candidates: int = 0
    fallback_candidates: int = 0
    selected: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True)
class SimilarTitle:
    current: str
    previous: str
    score: float


def extract_status_id(value: Any) -> str | None:
    """Return a canonical numeric X status ID from an ID or status URL."""
    raw = str(value or "").strip()
    if raw.isdigit():
        return raw
    match = STATUS_PATH_RE.search(raw)
    return match.group(1) if match else None


def extract_status_ids(text: str) -> set[str]:
    """Extract public X/Twitter status IDs from digest Markdown."""
    return set(STATUS_URL_RE.findall(text or ""))


def tweet_status_id(tweet: Mapping[str, Any]) -> str | None:
    return extract_status_id(tweet.get("id")) or extract_status_id(tweet.get("url"))


def canonical_tweet_key(tweet: Mapping[str, Any]) -> str:
    """Normalize same-run duplicates across X/Twitter URL variants."""
    status_id = tweet_status_id(tweet)
    if status_id:
        return f"status:{status_id}"

    url = str(tweet.get("url") or "").strip()
    if url:
        url = url.split("#", 1)[0].split("?", 1)[0].rstrip("/")
        return f"url:{url}"

    text = " ".join(str(tweet.get("text") or "").split())
    return f"text:{text[:200]}"


def published_status_ids(
    digest_dir: Path,
    *,
    exclude_date: str | None = None,
) -> set[str]:
    """Read only IDs that are already public in committed digest files."""
    seen: set[str] = set()
    for path in sorted(digest_dir.glob("????-??-??.md")):
        if exclude_date and path.stem == exclude_date:
            continue
        seen.update(extract_status_ids(path.read_text(encoding="utf-8")))
    return seen


def reference_time_for_date(
    date_slug: str,
    *,
    timezone_name: str = "Asia/Shanghai",
    now: datetime | None = None,
) -> datetime:
    """Use current local time for today and end-of-day for a backfill date."""
    local_zone = ZoneInfo(timezone_name)
    local_now = now or datetime.now(local_zone)
    if local_now.tzinfo is None:
        local_now = local_now.replace(tzinfo=local_zone)
    else:
        local_now = local_now.astimezone(local_zone)

    target = date.fromisoformat(date_slug)
    if target == local_now.date():
        return local_now
    return datetime.combine(target, time.max, tzinfo=local_zone)


def _snowflake_datetime(status_id: str | None) -> datetime | None:
    if not status_id or not status_id.isdigit():
        return None
    try:
        milliseconds = (int(status_id) >> 22) + TWITTER_EPOCH_MS
        created = datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    if created.year < 2010 or created.year > 2100:
        return None
    return created


def _parse_created_at(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None

    iso_value = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError:
        parsed = None

    if parsed is None:
        for fmt in ("%a %b %d %H:%M:%S %z %Y", "%Y-%m-%d %H:%M:%S%z"):
            try:
                parsed = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def tweet_created_at(tweet: Mapping[str, Any]) -> datetime | None:
    """Prefer the status snowflake, then fall back to the CLI timestamp."""
    return _snowflake_datetime(tweet_status_id(tweet)) or _parse_created_at(
        tweet.get("created_at")
    )


def filter_tweets_for_digest(
    tweets: Iterable[Mapping[str, Any]],
    *,
    published_ids: set[str],
    reference_time: datetime,
    preferred_hours: float = 36,
    max_hours: float = 72,
    min_items: int = 6,
    max_items: int = 40,
) -> tuple[list[dict[str, Any]], FilterStats]:
    """Select fresh, unpublished tweets while preserving source priority order."""
    if preferred_hours <= 0 or max_hours < preferred_hours:
        raise ValueError("freshness hours must satisfy 0 < preferred <= maximum")
    if min_items < 0 or max_items <= 0:
        raise ValueError("item limits must satisfy min >= 0 and max > 0")

    ref = reference_time
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    ref = ref.astimezone(timezone.utc)

    materialized = [dict(tweet) for tweet in tweets]
    seen_keys: set[str] = set()
    fresh: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    run_duplicates = history_duplicates = too_old = 0
    unknown_timestamp = future_timestamp = 0

    for tweet in materialized:
        key = canonical_tweet_key(tweet)
        if key in seen_keys:
            run_duplicates += 1
            continue
        seen_keys.add(key)

        status_id = tweet_status_id(tweet)
        if status_id and status_id in published_ids:
            history_duplicates += 1
            continue

        created = tweet_created_at(tweet)
        if created is None:
            unknown_timestamp += 1
            continue

        age_hours = (ref - created.astimezone(timezone.utc)).total_seconds() / 3600
        if age_hours < -6:
            future_timestamp += 1
        elif age_hours <= preferred_hours:
            fresh.append(tweet)
        elif age_hours <= max_hours:
            fallback.append(tweet)
        else:
            too_old += 1

    selected = fresh[:max_items]
    target_minimum = min(min_items, max_items)
    if len(selected) < target_minimum:
        needed = target_minimum - len(selected)
        selected.extend(fallback[:needed])

    stats = FilterStats(
        input_count=len(materialized),
        run_duplicates=run_duplicates,
        history_duplicates=history_duplicates,
        too_old=too_old,
        unknown_timestamp=unknown_timestamp,
        future_timestamp=future_timestamp,
        fresh_candidates=len(fresh),
        fallback_candidates=len(fallback),
        selected=len(selected),
    )
    return selected, stats


def recent_digest_titles(
    digest_dir: Path,
    *,
    exclude_date: str | None = None,
    max_digests: int = 7,
) -> list[str]:
    """Return titles from recent public digests for prompt-level topic guidance."""
    files = [
        path
        for path in sorted(digest_dir.glob("????-??-??.md"), reverse=True)
        if not exclude_date or path.stem != exclude_date
    ][:max_digests]
    titles: list[str] = []
    for path in files:
        titles.extend(TITLE_RE.findall(path.read_text(encoding="utf-8")))
    return titles


def duplicate_status_ids_for_digest(path: Path, digest_dir: Path) -> set[str]:
    current_ids = extract_status_ids(path.read_text(encoding="utf-8"))
    history_ids = published_status_ids(digest_dir, exclude_date=path.stem)
    return current_ids & history_ids


def _normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(char for char in normalized if char.isalnum())


def similar_titles_for_digest(
    path: Path,
    digest_dir: Path,
    *,
    max_digests: int = 7,
    threshold: float = 0.88,
) -> list[SimilarTitle]:
    """Return advisory title matches; callers must not hard-block on these."""
    current_titles = TITLE_RE.findall(path.read_text(encoding="utf-8"))
    previous_titles = recent_digest_titles(
        digest_dir,
        exclude_date=path.stem,
        max_digests=max_digests,
    )
    matches: list[SimilarTitle] = []
    for current in current_titles:
        current_key = _normalize_title(current)
        if not current_key:
            continue
        for previous in previous_titles:
            previous_key = _normalize_title(previous)
            score = SequenceMatcher(None, current_key, previous_key).ratio()
            if score >= threshold:
                matches.append(SimilarTitle(current, previous, score))
    return sorted(matches, key=lambda item: item.score, reverse=True)
