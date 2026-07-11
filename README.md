# Grok Daily Digest

用 **Grok Tasks** 每天策展 X 上的科技前沿 → 推到 **Gmail** → 本仓库脚本用 **Gmail API（只读）** 拉取并归档到 `digests/`。

> 阶段 1：本机手动跑通读信。阶段 2 再上 GitHub Actions。  
> 详见 [PROJECT_PLAN.md](./PROJECT_PLAN.md)。

## 你现在需要做的（阶段 1）

### 0. 前提

- 项目根目录已有 `grok_client_secret.json`（OAuth **桌面应用** 客户端）
- Gmail API 已在 Google Cloud 里 **启用**
- 该 Google 账号能收到 Grok Tasks 邮件（建议先手动跑一次 Task 或等每日任务发信）
- **首次授权**时，本机网络需能打开 Google 登录页（部分环境需 VPN）

### 1. 安装依赖

在项目根目录执行（推荐 **Python 3.12+**）。本机已验证路径示例：

```powershell
cd "D:\github项目\grok-daily-digest"
C:\Python\Python312\python.exe -m pip install -r requirements.txt
```

（依赖若已装过可跳过。）

### 2. 首次授权 + 读信

```powershell
cd "D:\github项目\grok-daily-digest"
C:\Python\Python312\python.exe scripts\run_daily.py
```

预期：

1. 浏览器弹出 Google 登录 / 授权（只读 Gmail）
2. 若 OAuth 应用仍是「测试」模式：用 **测试用户** 里添加的同一个 Gmail 登录
3. 成功后根目录生成 `token.json`（**不要提交到 Git**）
4. 若找到邮件：打印预览，并写入 `digests/YYYY-MM-DD.md`

只预览、不写文件：

```powershell
C:\Python\Python312\python.exe scripts\run_daily.py --print-only
```

### 3. 若提示「没有找到匹配的邮件」

说明搜索条件没命中真实来信。请到 Gmail 打开那封 Grok 邮件，看 **发件人** 和 **主题**，然后：

```powershell
C:\Python\Python312\python.exe scripts\run_daily.py --query "from:实际发件人域名"
# 或
C:\Python\Python312\python.exe scripts\run_daily.py --query "subject:主题里的关键词"
```

也可设环境变量：

```powershell
$env:GMAIL_QUERY = "from:x.ai"
C:\Python\Python312\python.exe scripts\run_daily.py
```

### 4. 安全

| 文件 | 可否进 Git |
|------|------------|
| `grok_client_secret.json` | **否**（已在 `.gitignore`） |
| `token.json` | **否** |
| `digests/*.md` | 可以（公开摘要内容） |

## 常用命令

```powershell
# 默认：读最新匹配邮件并归档
C:\Python\Python312\python.exe scripts\run_daily.py

# 自定义凭证路径
C:\Python\Python312\python.exe scripts\run_daily.py --client-secret grok_client_secret.json --token token.json
```

## 目录结构

```text
grok-daily-digest/
├── grok_client_secret.json   # 你放的密钥（本地，不提交）
├── token.json                # 首次授权后生成（本地，不提交）
├── scripts/run_daily.py
├── src/gmail_client.py
├── src/write_digest.py
├── digests/
├── requirements.txt
└── PROJECT_PLAN.md
```

## 阶段进度

| 阶段 | 状态 |
|------|------|
| 0 Prompt / Tasks 说明 | `prompts/daily_task_v1.md` 已就绪 |
| 1 本机 Gmail API 读通 | **已通过**（`from:x.ai`，样例见 `digests/2026-07-11.md`） |
| 2 GitHub Actions | Workflow 已写好；需你创建 Public 仓库并配置 Secrets（见 `docs/GITHUB_ACTIONS_SETUP.md`） |
| 3 打磨 | 去重 / raw 备份 / 索引 / 账号示例已有 |
| 4 Pages | 远期，见 `docs/GITHUB_PAGES.md` |

## 下一步（阶段 2）

1. 本机连续跑通后：创建 **Public** GitHub 仓库并 `git push`  
2. 配置 Secrets：`GMAIL_CLIENT_SECRET_JSON`、`GMAIL_TOKEN_JSON`  
3. Actions → **Daily Grok Digest** → Run workflow  

详见 [docs/GITHUB_ACTIONS_SETUP.md](./docs/GITHUB_ACTIONS_SETUP.md)。
