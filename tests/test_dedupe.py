from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.deepseek_client import summarize_tweets
from src.dedupe import (
    TWITTER_EPOCH_MS,
    duplicate_status_ids_for_digest,
    extract_status_id,
    filter_tweets_for_digest,
    published_status_ids,
    recent_digest_titles,
    reference_time_for_date,
    similar_titles_for_digest,
)


def snowflake_id(created: datetime) -> str:
    milliseconds = int(created.timestamp() * 1000)
    return str((milliseconds - TWITTER_EPOCH_MS) << 22)


def tweet(created: datetime, *, text: str = "item") -> dict[str, str]:
    status_id = snowflake_id(created)
    return {
        "id": status_id,
        "url": f"https://x.com/example/status/{status_id}?s=20",
        "text": text,
        "created_at": created.isoformat(),
    }


class DedupeTests(unittest.TestCase):
    def test_extract_status_id_normalizes_url_variants(self) -> None:
        self.assertEqual(extract_status_id("123456"), "123456")
        self.assertEqual(
            extract_status_id("https://twitter.com/user/status/123456?s=20"),
            "123456",
        )
        self.assertEqual(
            extract_status_id("https://x.com/i/web/status/123456"),
            "123456",
        )

    def test_published_ids_exclude_target_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            digest_dir = Path(temp)
            (digest_dir / "2026-07-20.md").write_text(
                "来源：https://x.com/a/status/100\n", encoding="utf-8"
            )
            (digest_dir / "2026-07-21.md").write_text(
                "来源：https://twitter.com/b/status/200\n", encoding="utf-8"
            )
            self.assertEqual(
                published_status_ids(digest_dir, exclude_date="2026-07-21"),
                {"100"},
            )

    def test_filter_removes_history_old_unknown_and_run_duplicates(self) -> None:
        reference = datetime(2026, 7, 22, 4, tzinfo=timezone.utc)
        history_tweet = tweet(reference - timedelta(hours=3), text="history")
        fresh = tweet(reference - timedelta(hours=2), text="fresh")
        fallback = tweet(reference - timedelta(hours=48), text="fallback")
        old = tweet(reference - timedelta(hours=80), text="old")
        unknown = {"id": "not-a-status", "url": "", "text": "unknown"}
        duplicate_variant = dict(fresh)
        duplicate_variant["url"] = fresh["url"].replace("x.com", "twitter.com")

        selected, stats = filter_tweets_for_digest(
            [history_tweet, fresh, duplicate_variant, fallback, old, unknown],
            published_ids={history_tweet["id"]},
            reference_time=reference,
            min_items=2,
            max_items=10,
        )

        self.assertEqual([item["text"] for item in selected], ["fresh", "fallback"])
        self.assertEqual(stats.history_duplicates, 1)
        self.assertEqual(stats.run_duplicates, 1)
        self.assertEqual(stats.too_old, 1)
        self.assertEqual(stats.unknown_timestamp, 1)

    def test_digest_audit_and_topic_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            digest_dir = Path(temp)
            (digest_dir / "2026-07-20.md").write_text(
                "【ITEM1】\n"
                "标题：OpenAI 发布 GPT-Red 自动化红队工具\n"
                "来源：@OpenAI — https://x.com/OpenAI/status/100\n",
                encoding="utf-8",
            )
            current = digest_dir / "2026-07-21.md"
            current.write_text(
                "【ITEM1】\n"
                "标题：OpenAI 推出 GPT-Red 自动化红队工具\n"
                "来源：@OpenAI — https://x.com/OpenAI/status/100\n",
                encoding="utf-8",
            )

            self.assertEqual(duplicate_status_ids_for_digest(current, digest_dir), {"100"})
            self.assertTrue(similar_titles_for_digest(current, digest_dir, threshold=0.7))
            self.assertEqual(
                recent_digest_titles(digest_dir, exclude_date="2026-07-21"),
                ["OpenAI 发布 GPT-Red 自动化红队工具"],
            )

    def test_reference_time_uses_now_for_today_and_end_of_day_for_backfill(self) -> None:
        now = datetime(2026, 7, 22, 12, tzinfo=timezone.utc)
        today = reference_time_for_date("2026-07-22", now=now)
        backfill = reference_time_for_date("2026-07-20", now=now)
        self.assertEqual(today.astimezone(timezone.utc), now)
        self.assertEqual(backfill.hour, 23)
        self.assertEqual(backfill.minute, 59)

    def test_recent_public_titles_are_added_to_prompt_without_network(self) -> None:
        with patch("src.deepseek_client.chat_complete", side_effect=lambda value: value):
            prompt = summarize_tweets(
                "URL: https://x.com/example/status/123",
                date_label="2026-07-22",
                recent_titles=["已公开的历史主题"],
            )
        self.assertIn("已公开的历史主题", prompt)
        self.assertIn("没有明确新增信息时不要重复", prompt)
        self.assertIn("https://x.com/example/status/123", prompt)


if __name__ == "__main__":
    unittest.main()
