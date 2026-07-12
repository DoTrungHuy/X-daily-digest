# 主路径设置：免费读 X → DeepSeek → GitHub Pages

按计划书 v2 实施。**Grok Tasks 已停用。**

## 你需要准备的 Secrets

仓库 → **Settings → Secrets and variables → Actions**

| Secret | 必填 | 说明 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | 是 | [DeepSeek 开放平台](https://platform.deepseek.com/) 申请 |
| `TWITTER_AUTH_TOKEN` | 是 | 浏览器登录 x.com 后 Cookie 里的 `auth_token` |
| `TWITTER_CT0` | 是 | 同上 Cookie 里的 `ct0` |
| `HTTPS_PROXY` | 否 | **A1 先测直连**；失败再填廉价代理，如 `http://user:pass@host:port` |
| `HTTP_PROXY` / `ALL_PROXY` | 否 | 按代理商要求 |

### 如何导出 X Cookie（本机一次）

1. 用 Chrome 登录 [https://x.com](https://x.com)  
2. 安装扩展 **Cookie-Editor**（或 DevTools → Application → Cookies）  
3. 复制 `auth_token`、`ct0` 的值到上述 Secrets  
4. **不要**把 Cookie 发到聊天或提交进 Git  

Cookie 失效后：重新导出并更新 Secrets 即可。

## 本机试跑（阶段 0～2）

```powershell
cd "D:\github项目\grok-daily-digest"
C:\Python\Python312\python.exe -m pip install pyyaml
# 安装 twitter-cli（Agent-Reach 推荐栈）
C:\Python\Python312\python.exe -m pip install twitter-cli
# 若命令名是 twitter：
# 设置环境变量后：
$env:TWITTER_AUTH_TOKEN = "你的auth_token"
$env:TWITTER_CT0 = "你的ct0"
$env:DEEPSEEK_API_KEY = "你的key"

C:\Python\Python312\python.exe scripts\run_x_digest.py
```

成功后应有：

- `x_raw/YYYY-MM-DD.json` — 原始推文  
- `digests/YYYY-MM-DD.md` — 完整精读  
- `docs/index.html` 等 — 网站文件  

## 云端日更（阶段 3）

Workflow：`.github/workflows/daily-x-digest.yml`  

- 时间：**每天北京时间 08:00**（`cron: 0 0 * * *` UTC）  
- 代理策略：**A1 先直连测**；若连续失败再配置 `HTTPS_PROXY`  

手动试跑：Actions → **Daily X Digest** → Run workflow  

## 网站（阶段 4）

1. 仓库 **Settings → Pages**  
2. Source： **Deploy from a branch**  
3. Branch：`main`，文件夹：**`/docs`**  
4. 保存后等待 1～2 分钟  

站点地址类似：

`https://dotrunghuy.github.io/grok-daily-digest/`

## 内容列表

默认：`config/accounts.yaml`（CS/AI 账号 + 关键词）。  
读通后你再改账号/搜索词精进即可。

## 代理策略 A1

1. 先不配 PROXY，跑满 3～7 天 Actions  
2. 看是否经常「0 条推文 / 403」  
3. 再决定是否买廉价住宅代理并写入 `HTTPS_PROXY`  

## 失败时

| 现象 | 处理 |
|------|------|
| No tweets / CLI error | 更新 Cookie；本机先验证 twitter-cli |
| DeepSeek 401 | 检查 `DEEPSEEK_API_KEY` |
| Actions 绿但站不更新 | 确认 Pages 指向 `/docs` 且有 `index.html` |
| 云端采不到、本机能采 | 考虑 PROXY（A1 后的 P1） |

## 与旧 Grok 路径

旧邮件/Playwright 代码保留在仓库中但**非主路径**。日常只跑 `run_x_digest.py` / `daily-x-digest` workflow。
