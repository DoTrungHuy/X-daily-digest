# X Daily Digest（免费读 X → DeepSeek → GitHub Pages）

每天自动：用 **Cookie + twitter-cli（Agent-Reach 路线）** 免费读 X → **DeepSeek** 生成完整精读 → 写入 `digests/` → **GitHub Pages** 网站更新。

- **不付 X 官方 API**  
- **电脑可关机**（GitHub Actions 日更）  
- **Grok Tasks 已停用**（旧路径仅作 legacy）

## 快速链接

| 文档 | 内容 |
|------|------|
| [docs/FEASIBILITY_AND_PLAN.md](./docs/FEASIBILITY_AND_PLAN.md) | 可行性 + 计划书 |
| [docs/SETUP_X_DEEPSEEK_PAGES.md](./docs/SETUP_X_DEEPSEEK_PAGES.md) | **配置 Secrets / 本机试跑 / 开 Pages** |

## 你需要配置的 Secrets（一次）

1. `DEEPSEEK_API_KEY`  
2. `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`（x.com Cookie）  
3. 可选：`HTTPS_PROXY`（**A1：先不配，测 3～7 天直连**）

## 本机一条命令

```powershell
$env:DEEPSEEK_API_KEY="..."
$env:TWITTER_AUTH_TOKEN="..."
$env:TWITTER_CT0="..."
C:\Python\Python312\python.exe -m pip install pyyaml twitter-cli
C:\Python\Python312\python.exe scripts\run_x_digest.py
```

## 自动更新

- Workflow：`.github/workflows/daily-x-digest.yml`  
- 时间：**每天北京时间 08:00**  
- Pages：Settings → Pages → Branch `main` → folder **`/docs`**

## 默认内容列表

`config/accounts.yaml` — CS/AI 默认账号与关键词；跑通后再改。

## 架构

```text
twitter-cli (Cookie) → x_raw/日期.json
        → DeepSeek → digests/日期.md
        → build_site → docs/*.html
        → Actions commit → Pages
```

## Legacy

旧 Grok 邮件 / Playwright 代码仍在仓库，**非主路径**。见 `docs/FULL_CHAT_SETUP.md` 等。
