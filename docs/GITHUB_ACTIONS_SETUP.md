# 阶段 2：GitHub Actions 配置

本机已成功生成 `token.json` 之后再做。

## 1. 创建 Public 仓库并推送代码

```powershell
cd "D:\github项目\grok-daily-digest"
git init
git add .
git status   # 确认没有 grok_client_secret.json / token.json
git commit -m "feat: stage1 gmail digest pipeline + actions workflow"
# 用 gh 或网页创建 public repo 后：
# git remote add origin https://github.com/<you>/grok-daily-digest.git
# git branch -M main
# git push -u origin main
```

## 2. 配置 Secrets

仓库 → **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|--------|
| `GMAIL_CLIENT_SECRET_JSON` | `grok_client_secret.json` **全文**（整份 JSON 粘贴） |
| `GMAIL_TOKEN_JSON` | `token.json` **全文**（必须含 `refresh_token`） |

可选 **Variables**：

| Name | Value |
|------|--------|
| `GMAIL_QUERY` | 你实测后的搜索，如 `from:x.ai newer_than:2d` |

## 3. 手动触发验证

Actions → **Daily Grok Digest** → **Run workflow**

成功后应出现 commit：`chore(digest): archive daily digest …`

## 4. 定时

默认 cron：`30 0 * * *`（UTC）≈ 北京时间 08:30。  
按你的 Grok Tasks 发信时间，改 `.github/workflows/daily-digest.yml`。

## 5. 注意

- OAuth 应用若为「测试」模式，refresh token 可能约 7 天失效 → 本机重新授权后更新 `GMAIL_TOKEN_JSON`
- Public 仓库只公开 `digests/` 正文，**切勿**把密钥文件 commit 上去
