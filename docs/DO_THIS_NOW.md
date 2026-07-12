# 现在请你做这 3 件事

## 我已经做好的

| 项 | 状态 |
|----|------|
| 代码主路径 | ✅ |
| GitHub Pages（`main` + `/docs`） | ✅ |
| 站点 | https://dotrunghuy.github.io/X-daily-digest/ |
| 每天北京 **08:00** 自动跑 | ✅ `daily.yml` |
| 默认账号列表 | ✅ `config/accounts.yaml` |

---

## 必须你做（网页配 Secrets）

### ① DeepSeek API Key

1. https://platform.deepseek.com/  
2. 登录 → **API Keys** → 创建 → 复制  

### ② X Cookie

1. https://x.com 登录  
2. `F12` → **Application** → **Cookies** → `https://x.com`  
3. 复制：`auth_token`、`ct0`  

### ③ 写入 GitHub Secrets

打开：  
https://github.com/DoTrungHuy/X-daily-digest/settings/secrets/actions  

**New repository secret**，创建：

| Name | Value |
|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek Key |
| `TWITTER_AUTH_TOKEN` | Cookie `auth_token` |
| `TWITTER_CT0` | Cookie `ct0` |

然后：  
https://github.com/DoTrungHuy/X-daily-digest/actions  

→ **Daily X Digest** → **Run workflow** → Run  

---

## 成功标准

1. Actions **绿色**  
2. `digests/` 有新 md  
3. 站点能打开今日内容  

失败时看日志：缺 Secret / Cookie 错 / DeepSeek 401。
