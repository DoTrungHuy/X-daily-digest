# 阶段 4：GitHub Pages（远期）

**当前不启用。** 等 Actions 稳定落库几天后再做。

## 思路

`digests/*.md` 已是静态内容，可任选：

1. **最简**：仓库 Settings → Pages → Deploy from branch → `/docs` 或 `/ (root)`，把 digests 链到简单 `index.md`
2. **稍好看**：用 Jekyll / 任意静态生成器把 `digests/` 列成日期列表

## 验收

浏览器打开 Pages URL，能按日期打开历史 digest。
