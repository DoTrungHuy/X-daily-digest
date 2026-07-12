"""DeepSeek API client (OpenAI-compatible) for daily digest summarization."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")


SYSTEM_PROMPT = """你是资深科技与 AI 新闻策展人，面向 CS / agent 开发者。
你会收到一组从 X（Twitter）抓取的原始推文（已含原文与链接）。
请只根据这些材料策展，不要编造未出现的事实；材料不足就少写条目。

输出必须是完整可发布的每日 digest，使用以下结构（全部写出，不要截断）：

【HOOK】
1-2 句今日总览

【META】
时间窗：过去约 24 小时
条目数：N
来自关注账号优先：说明是否优先了 following/指定账号
信号强度：强/中/弱

【ITEM1】
标题：
类别：关注动态 / 大佬官方 / 工具更新 / 行业趋势 / 中国相关 / 其他
原文摘录：（保留原文语言，可短引）
实用点：（对 CS/agent/工程/职业；无则写无）
来源：@handle — 链接

【ITEM2】
...（共 6-10 条，按价值排序）

【CLOSE】
一句话：今天若只点开一条，点哪条。

要求：中文说明 + 原文摘录；中立、不 hype；条目完整写完。"""


def chat_complete(
    user_content: str,
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_KEY")
    if not key:
        raise RuntimeError(
            "缺少 DEEPSEEK_API_KEY。请在环境变量或 GitHub Secrets 中配置。"
        )

    url = base_url.rstrip("/") + "/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API HTTP {e.code}: {detail[:800]}") from e

    try:
        return payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected DeepSeek response: {payload!r}") from e


def summarize_tweets(tweets_block: str, *, date_label: str = "") -> str:
    user = (
        f"日期：{date_label or '今天'}\n\n"
        f"以下是从 X 抓取的原始材料，请生成完整每日 digest：\n\n"
        f"{tweets_block}"
    )
    return chat_complete(user)
