# 设置说明（唯一主文档）

## 架构

```text
twitter-cli + X Cookie  →  x_raw/
DeepSeek API            →  digests/
build_site              →  docs/*.html
GitHub Actions 08:17 北京 → 自动 commit digests/docs
GitHub Actions deploy-pages → 主动发布 GitHub Pages
```

也就是“双线更新”：

```text
第一条线：生成后的 digests/ 和 docs/ commit 回仓库
第二条线：把 docs/ 上传为 Pages artifact，并由 deploy-pages 发布网站
```

## Secrets（仓库 Settings → Actions）

| Secret | 说明 |
|--------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `TWITTER_AUTH_TOKEN` | x.com Cookie `auth_token` |
| `TWITTER_CT0` | x.com Cookie `ct0` |
| `HTTPS_PROXY` | 可选；**A1 先不配**，直连失败再加 |

### 导出 Cookie

1. 浏览器登录 https://x.com  
2. Cookie-Editor / DevTools 复制 `auth_token`、`ct0`  
3. 粘贴到 Secrets（勿提交到 Git、勿发聊天）

## 本机试跑

```powershell
cd 仓库目录
pip install -r requirements.txt
$env:DEEPSEEK_API_KEY="..."
$env:TWITTER_AUTH_TOKEN="..."
$env:TWITTER_CT0="..."
python scripts/run_daily.py
```

## Pages

Settings → Pages → Source → **GitHub Actions**

不要再使用旧方式：

```text
Deploy from a branch → main → /docs
```

改成 GitHub Actions 后，网站由 `.github/workflows/daily.yml` 中的 `deploy-pages` 步骤发布。

访问：`https://<user>.github.io/X-daily-digest/`

## 手动验证

进入 Actions → **Daily X Digest** → **Run workflow**。

如果在改造分支上验证，选择对应分支运行；如果已经合并到 `main`，选择 `main` 运行。

验收时看四个点：

```text
1. Run daily pipeline 成功
2. Commit generated files 成功，或者输出 No changes to commit
3. Deploy to GitHub Pages 成功
4. 网站首页显示最新内容
```

## 改「想看的内容」

编辑 `config/accounts.yaml`（账号 + 搜索词），提交即可。

## 代理（A1）

先直连跑 3～7 天 Actions；常失败再设 `HTTPS_PROXY`。

## 定时

`.github/workflows/daily.yml`：UTC `17 0 * * *` = 北京/新加坡 **08:17**。

选择 08:17 是为了避开 GitHub Actions 整点高峰，减少定时任务延迟或丢弃的概率。
