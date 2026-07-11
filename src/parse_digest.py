"""Optional structured parsing of Grok Tasks email bodies."""

from __future__ import annotations

import re
from typing import Any


ITEM_RE = re.compile(
    r"【ITEM(?P<n>\d+)】\s*(?P<body>.*?)(?=【ITEM\d+】|\Z)",
    re.DOTALL | re.IGNORECASE,
)
HOOK_RE = re.compile(r"【HOOK】\s*(?P<body>.*?)(?=【ITEM|\Z)", re.DOTALL | re.IGNORECASE)


def parse_structured_body(body: str) -> dict[str, Any]:
    """
    Parse 【HOOK】 / 【ITEMn】 blocks if present.
    Always safe: missing structure returns empty items and full body as raw.
    """
    text = body or ""
    hook_m = HOOK_RE.search(text)
    hook = (hook_m.group("body").strip() if hook_m else "")

    items: list[dict[str, str]] = []
    for m in ITEM_RE.finditer(text):
        block = m.group("body").strip()
        items.append(
            {
                "index": m.group("n"),
                "raw": block,
                "title": _field(block, "标题"),
                "quote": _field(block, "原文摘录"),
                "takeaway": _field(block, "实用点"),
                "source": _field(block, "来源"),
            }
        )

    return {
        "structured": bool(hook or items),
        "hook": hook,
        "items": items,
        "raw": text,
    }


def _field(block: str, label: str) -> str:
    # 标题：... until next known label or end
    pattern = rf"{re.escape(label)}\s*[:：]\s*(.*?)(?=\n(?:标题|原文摘录|实用点|来源)\s*[:：]|\Z)"
    m = re.search(pattern, block, re.DOTALL)
    return m.group(1).strip() if m else ""
