# 现在请你做这 3 件事（我这边已弄好的 / 必须你做的）

## 我已经替你做好的

| 项 | 状态 |
|----|------|
| 代码主路径（读 X → DeepSeek → digests → 网站） | ✅ 已推仓库 |
| GitHub Pages 已开启（`main` + `/docs`） | ✅ |
| 站点地址 | https://dotrunghuy.github.io/grok-daily-digest/ |
| 定时任务 workflow | ✅ `daily.yml`，北京时间 **08:00** |
| 默认账号列表 | ✅ `config/accounts.yaml` |
| 本机安装 `twitter-cli` | ✅ |
| 代理 | A1：先不配 |

当前站点若已打开，可能先看到**旧 digests 样例页**（之前 Grok 预览内容）。等 Secrets 配好并跑通流水线后，会变成「完整 DeepSeek 精读」。

---

## 必须你本人做（我拿不到你的密钥）

### ① DeepSeek API Key（约 2 分钟）

1. 打开：https://platform.deepseek.com/  
2. 登录 → **API Keys** → 创建 Key → 复制  

### ② X Cookie（约 3 分钟）

1. 打开：https://x.com 并**登录**  
2. 按 `F12` → **Application（应用程序）** → **Cookies** → `https://x.com`  
3. 找到并复制：  
   - `auth_token`  
   - `ct0`  

（或用 Cookie-Editor 扩展导出这两项。）

### ③ 写入 GitHub Secrets（约 2 分钟）

**方式 A（推荐，脚本引导）：** 在本机 PowerShell 执行：

```powershell
cd "D:\github项目\grok-daily-digest"
$env:Path = "C:\Program Files\GitHub CLI;" + $env:Path
gh auth status
# 若未登录: gh auth login
powershell -ExecutionPolicy Bypass -File scripts\set_secrets_interactive.ps1
```

按提示粘贴 3 个值即可，脚本会自动 `gh secret set` 并触发 workflow。

**方式 B（网页）：**

打开：  
https://github.com/DoTrungHuy/grok-daily-digest/settings/secrets/actions  

点 **New repository secret**，建这三个：

| Name | Value |
|------|--------|
| `DEEPSEEK_API_KEY` | 你的 DeepSeek Key |
| `TWITTER_AUTH_TOKEN` | Cookie 里的 auth_token |
| `TWITTER_CT0` | Cookie 里的 ct0 |

然后打开 Actions：  
https://github.com/DoTrungHuy/grok-daily-digest/actions  

→ **Daily X Digest** → **Run workflow** → Run。

---

## 成功长什么样

1. Actions 跑完是 **绿色**  
2. 仓库 `digests/` 出现/更新当天 md  
3. 打开 https://dotrunghuy.github.io/grok-daily-digest/ 能看到当天精读  

若 Actions 红了：点进日志  
- 缺 Secret → 回到 ③  
- twitter 未登录 / 0 条 → Cookie 错或过期，重做 ②  
- DeepSeek 401 → Key 错，重做 ①  
- 云端一直采不到、本机却可以 → 再考虑代理（A1 之后）

---

## 本机快速验证（可选）

```powershell
cd "D:\github项目\grok-daily-digest"
$env:Path = "C:\Python\Python312\Scripts;" + $env:Path
$env:DEEPSEEK_API_KEY = "粘贴"
$env:TWITTER_AUTH_TOKEN = "粘贴"
$env:TWITTER_CT0 = "粘贴"
twitter status
python scripts/run_daily.py
```

`twitter status` 显示 `ok: true` 再跑流水线。
