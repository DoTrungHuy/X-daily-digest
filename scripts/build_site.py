#!/usr/bin/env python3
"""Build a minimal static site from digests/*.md into docs/ for GitHub Pages."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIGESTS = ROOT / "digests"
OUT = ROOT / "docs" / "site"


def md_to_simple_html(md: str) -> str:
    """Very small markdown-ish converter for our digests."""
    lines = md.splitlines()
    out: list[str] = []
    in_pre = False
    for line in lines:
        if line.startswith("```"):
            if not in_pre:
                out.append("<pre>")
                in_pre = True
            else:
                out.append("</pre>")
                in_pre = False
            continue
        if in_pre:
            out.append(html.escape(line))
            continue
        if line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("- "):
            out.append(f"<li>{_inline(line[2:].strip())}</li>")
        elif line.strip() == "---":
            out.append("<hr/>")
        elif not line.strip():
            out.append("")
        else:
            out.append(f"<p>{_inline(line)}</p>")
    # wrap consecutive li
    joined = "\n".join(out)
    joined = re.sub(
        r"(?:<li>.*?</li>\n?)+",
        lambda m: "<ul>\n" + m.group(0) + "</ul>\n",
        joined,
        flags=re.S,
    )
    return joined


def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(
        r"`([^`]+)`",
        r"<code>\1</code>",
        s,
    )
    s = re.sub(
        r"(https?://[^\s<]+)",
        r'<a href="\1" rel="noopener" target="_blank">\1</a>',
        s,
    )
    return s


def page_shell(title: str, body: str, *, active: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="style.css"/>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">X Daily Digest</a>
    <nav>
      <a href="index.html">首页</a>
      <a href="https://github.com/DoTrungHuy/grok-daily-digest">GitHub</a>
    </nav>
  </header>
  <main class="container">
{body}
  </main>
  <footer class="foot">
    <p>免费管线：X (twitter-cli / Agent-Reach Cookie) → DeepSeek → GitHub Pages</p>
    <p>Generated {html.escape(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))}</p>
  </footer>
</body>
</html>
"""


def build_site() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(DIGESTS.glob("????-??-??.md"), reverse=True)

    # CSS
    (OUT / "style.css").write_text(
        """
:root { --bg:#0b0f14; --card:#121a22; --text:#e7eef7; --muted:#8aa0b5; --acc:#3d9cf0; --line:#1e2a36; }
* { box-sizing: border-box; }
body { margin:0; font-family: ui-sans-serif, system-ui, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }
a { color:var(--acc); text-decoration:none; }
a:hover { text-decoration:underline; }
.top { display:flex; justify-content:space-between; align-items:center; padding:1rem 1.25rem; border-bottom:1px solid var(--line); position:sticky; top:0; background:rgba(11,15,20,.92); backdrop-filter:blur(8px); }
.brand { font-weight:700; color:var(--text); font-size:1.1rem; }
nav a { margin-left:1rem; color:var(--muted); }
.container { max-width:820px; margin:0 auto; padding:1.5rem 1.25rem 3rem; }
.hero { margin-bottom:1.5rem; }
.hero h1 { margin:0 0 .5rem; font-size:1.75rem; }
.hero p { color:var(--muted); margin:0; }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1rem 1.1rem; margin:.75rem 0; }
.card h2 { margin:0 0 .35rem; font-size:1.15rem; }
.meta { color:var(--muted); font-size:.9rem; }
.article h1 { font-size:1.5rem; }
.article h2 { margin-top:1.4rem; border-bottom:1px solid var(--line); padding-bottom:.3rem; }
.article li { margin:.25rem 0; }
.article code { background:#0b1219; padding:.1rem .35rem; border-radius:4px; }
.foot { border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; padding:1.5rem; text-align:center; }
.badge { display:inline-block; background:#16324d; color:#9fd0ff; font-size:.75rem; padding:.15rem .5rem; border-radius:999px; }
""".strip()
        + "\n",
        encoding="utf-8",
    )

    # index
    cards = []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        first_p = ""
        for line in raw.splitlines():
            if line.startswith("# "):
                continue
            if line.startswith("- **") or line.strip() == "---" or not line.strip():
                continue
            first_p = line.strip()
            break
        cards.append(
            f"""<article class="card">
  <h2><a href="{f.stem}.html">{html.escape(f.stem)}</a></h2>
  <p class="meta"><span class="badge">digest</span></p>
  <p>{html.escape(first_p[:180])}{"…" if len(first_p) > 180 else ""}</p>
</article>"""
        )

    index_body = f"""
<section class="hero">
  <h1>每日 X 精读</h1>
  <p>免费采集 X（Agent-Reach / twitter-cli Cookie）→ DeepSeek 总结 → 自动发布。不使用付费 X API。</p>
</section>
<section>
  {"\n".join(cards) if cards else "<p class='meta'>暂无 digest，等待首次流水线运行。</p>"}
</section>
"""
    (OUT / "index.html").write_text(
        page_shell("X Daily Digest", index_body), encoding="utf-8"
    )

    for f in files:
        body_html = md_to_simple_html(f.read_text(encoding="utf-8"))
        page = page_shell(
            f"Digest {f.stem}",
            f'<article class="article card"><p class="meta"><a href="index.html">← 返回列表</a></p>{body_html}</article>',
        )
        (OUT / f"{f.stem}.html").write_text(page, encoding="utf-8")

    # Publish under docs/ for GitHub Pages "Deploy from branch → /docs"
    docs_root = ROOT / "docs"
    for item in OUT.iterdir():
        if item.is_file() and (
            item.name in ("index.html", "style.css") or item.suffix == ".html"
        ):
            (docs_root / item.name).write_text(
                item.read_text(encoding="utf-8"), encoding="utf-8"
            )

    return OUT


if __name__ == "__main__":
    print(build_site())
