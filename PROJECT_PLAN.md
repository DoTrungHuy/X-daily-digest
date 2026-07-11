# Grok Daily Digest — 方向与方案（v2）

> 状态：**按最新对话重定方向**，可进入实现  
> 依据：  
> - [意图与需求对话](https://grok.com/share/bGVnYWN5LWNvcHk_6a45adab-829d-45bc-b26b-7ba6e2296468)  
> - [Gmail / Cloud 开通过程](https://grok.com/share/bGVnYWN5LWNvcHk_83edebcf-a09e-4461-bedf-da5796ade9bc)  
> - [后续：API 已启用 + 凭证与授权](https://grok.com/share/bGVnYWN5LWNvcHk_b8d46bfe-0ed8-42f2-ad19-fb5746a78209)  
> - 以及你对本仓库大纲前半部分的修订  
> 仓库：`grok-daily-digest`（目标：**Public**）

---

## 0. 最新结论（先看这个）

### 0.1 你现在实际卡在哪、已经完成了什么

| 节点 | 状态 |
|------|------|
| 目标：被动每日科技 digest | 不变 |
| Grok Tasks 当「大脑」 | 不变（不用 xAI API） |
| 交付：邮件通知 + GitHub 归档 | 不变（不做发 X） |
| Google Cloud 项目 | 已能创建 |
| **Gmail API** | **已真正启用**（界面显示「已启用 / 停用 API」） |
| OAuth 桌面客户端 + `client_secret_*.json` | **已拿到，需本地妥善保存** |
| `token.json` 首次授权 | **尚未完成**（下一动作） |
| 本仓库脚本 / Actions | **未开始写** |

### 0.2 读邮件技术选型（v2 拍板）

此前因 Cloud **账单 / 绑卡** 卡壳，一度倾向 **IMAP**。  
最新对话显示你已走通 **Gmail API 启用 + 客户端密钥**，不必为绑卡再去申请外卡。

| 路径 | 角色 | 说明 |
|------|------|------|
| **Gmail API + OAuth（主路径）** | 默认实现 | 你已启用 API、已有 `client_secret`；只读 scope |
| **IMAP + 应用专用密码（备用）** | 兜底 | 若本机 OAuth / Actions 刷 token 搞不定，再切；不占主工期 |

**不再推荐**：为 Cloud 去办 Visa/虚拟卡、地址造假等——没必要，风险大，且你已过「启用 API」关。

### 0.3 和对话里 Grok 建议的差异（刻意保留）

对话后半 Grok 仍常提「读邮件 → **自动发 X**」。  
按你在本仓库的修订，**本项目不做发 X**，落点是：

```text
Grok Tasks → Gmail → 脚本读取 → digests/ → GitHub Actions 定时归档
                                         →（远期）GitHub Pages
```

---

## 1. 目标（不变的核心）

### 1.1 痛点

- 每天想看 **X 上科技 / AI 前沿 + 大佬动态** 的高质量总结  
- 不想每天手动打开 Grok  
- **不要** 按 token 计费的 xAI（等）API 做主生成  
- 尽量 **被动**：邮件通知 + 仓库里自动有一份 digest  

### 1.2 P0

| 层级 | 目标 |
|------|------|
| P0 | 每日自动生成 digest（Grok Tasks，来源以 X 为主） |
| P0 | 免费路径：复用 Tasks / 手机推送，不用 LLM token API |
| P0 | 全自动接收：邮件通知 + 脚本读信归档到 GitHub |

### 1.3 一句话

> **Grok Tasks 策展 → 推到 Gmail → 本仓库用 Gmail API 读取并结构化 → GitHub Actions 每日落库。**  
> 原则：**免费、被动、可迭代；先个人可用，远期 Pages 再谈「公开展示」。**

### 1.4 内容标准（策展）

- 大佬 / 官方：OpenAI、Anthropic、xAI、Musk、levelsio 等（可扩展）  
- 工具：Notion、Obsidian、Google、Tabbit 等  
- 科技前沿 + 中国相关（X 上有高质量讨论时）  
- 视角：CS（项目、工程、职业 / side hustle、**agent 开发**）  
- 形式：5–8 条，**高价值 + 高热度**，**尽量保留 X 原推文**  
- 不做：hype 文案账号、自动发 X  

---

## 2. 总体架构（v2）

```
┌──────────────────────┐
│ Grok Tasks（每日）    │  搜 X + 生成 digest（订阅/免费额度内）
└──────────┬───────────┘
           │ Email
           ▼
┌──────────────────────┐
│ Gmail 收件箱          │  通知 + 原始存档
└──────────┬───────────┘
           │ Gmail API (readonly)  ← 主路径（你已启用）
           │ IMAP 备用
           ▼
┌──────────────────────┐
│ Python（本仓库）      │
│ · OAuth / 读最新邮件  │
│ · 解析正文            │
│ · 写 digests/日期.md  │
└──────────┬───────────┘
           │ cron
           ▼
┌──────────────────────┐
│ GitHub Actions        │  无本机常开；Secrets 存凭证
│ commit 归档（Public） │
└──────────┬───────────┘
           │ 远期
           ▼
┌──────────────────────┐
│ GitHub Pages（可选）  │  浏览历史；暂不实现
└──────────────────────┘
```

### 2.1 各层职责

| 组件 | 职责 | 费用 |
|------|------|------|
| Grok Tasks | 搜索 + 策展 | 现有能力，无 xAI token |
| Gmail | 投递 / 通知 | 免费 |
| Gmail API | 程序只读邮件 | 个人只读额度内免费；**不绑卡也能用你已启用的 API** |
| Python | 鉴权、拉取、解析、落盘 | 免费 |
| GitHub Actions | 定时跑 + 写回仓库 | Public 额度通常够 |
| Pages | 远期展示 | 免费；延后 |

### 2.2 明确不做

| 不做 | 原因 |
|------|------|
| xAI / 其它 LLM token API 生成摘要 | 额度不可控；你要求永不考虑 |
| 自动发帖到 X | 目标已删；Grok 对话里的发 X 仅作背景，不采纳 |
| 为 Cloud 办外卡 / 虚拟卡硬闯账单 | 已无必要；风险高 |
| 浏览器自动化硬控 Grok App | 脆弱 |
| 一上来做 Pages / 复杂前端 | 先管道 |

### 2.3 中国网络注意（对话里确认的运维现实）

| 场景 | 建议 |
|------|------|
| **首次**浏览器 OAuth 授权 | 需要能打开 Google 的网络（常见需 VPN） |
| 之后本机用已有 `token.json` 刷 refresh | 多数情况仍建议稳定可访问 Google 的网络 |
| GitHub Actions（美国机房） | 访问 Gmail API **通常不需要你本机 VPN**；凭证用 Secrets 注入 |
| 若改 IMAP 连 Gmail | 本机同样常需可访问 Google 的网络；Actions 上一般可用 |

---

## 3. 凭证与安全（你当前进度）

### 3.1 你手里该有什么

| 文件 | 作用 | 是否提交到 Git |
|------|------|----------------|
| `client_secret_*.json` | OAuth 客户端密钥（「钥匙」） | **否**（用 Secrets / 本地 env） |
| `token.json` | 用户授权后的 access + **refresh** token（「通行证」） | **否**；Actions 用 Secret 注入 |
| 应用专用密码 | 仅 IMAP 备用路径 | **否** |

保留 `client_secret`：token 丢了 / 过期无法刷新时，要用它重新走授权。

### 3.2 Public 仓库怎么放 Secrets（阶段 2）

建议 Secrets 名（实现时可微调）：

- `GMAIL_CLIENT_SECRET_JSON`：client_secret 文件全文  
- `GMAIL_TOKEN_JSON`：本地授权成功后的 token.json 全文（含 refresh_token）  

Workflow 启动时写入临时文件，**绝不** commit。

### 3.3 OAuth 范围

只用：

```text
https://www.googleapis.com/auth/gmail.readonly
```

只读，不写信、不改设置。

---

## 4. 分阶段计划（重排后的可执行版）

### 阶段 0：Grok Tasks 内容（可与 1 并行）

- [ ] Daily Task + Prompt v1（见 §6）  
- [ ] 确认推到 **Email + 手机通知**  
- [ ] 记下真实 **发件人 / 主题**（供搜索 query）  
- [ ] 抽查 2–3 天质量（原推文、热度、中外覆盖）  

**验收**：愿意主要靠这份摘要看前沿。

---

### 阶段 1：本机 Gmail API 读通（当前主攻）

**目的**：证明「用你已启用的 Gmail API，能稳定读到 Tasks 邮件并写成 md」。

- [ ] 本地放好 `client_secret_*.json`（勿提交）  
- [ ] Python 依赖：`google-api-python-client`、`google-auth-oauthlib`、`google-auth-httplib2`  
- [ ] 脚本：`scripts/run_daily.py`（或拆 `src/gmail_client.py` 等）  
  - 首次：`InstalledAppFlow` → 浏览器授权 → 生成 `token.json`  
  - 之后：refresh 自动续期  
  - `users.messages.list` 查询最新 Grok Tasks 邮件  
  - 解析 `text/plain`（必要时 fallback html）  
  - 写出 `digests/YYYY-MM-DD.md`  
- [ ] `.gitignore`：`client_secret*.json`、`token.json`、`.env`  
- [ ] `README`：授权步骤、VPN 首次说明、query 如何改  
- [ ] **本机手动跑通**（不做 Actions）  

**验收**：

```bash
python scripts/run_daily.py
# → digests/当天日期.md 有可读正文
```

**若阶段 1 卡死**（授权页打不开、refresh 无效、测试用户限制等）→ 启用 **§7 备用 IMAP 方案**，不阻塞整体目标。

---

### 阶段 2：GitHub Actions 每日落库

- [ ] 推 Public 仓库  
- [ ] Secrets 配置 client_secret + token（含 refresh）  
- [ ] `schedule` cron：比 Tasks 发信 **晚 30–90 分钟**（按时区换 UTC）  
- [ ] `workflow_dispatch` 可手动跑  
- [ ] 成功则 commit `digests/YYYY-MM-DD.md`（或 open PR，二选一，默认直接 bot commit）  
- [ ] 失败靠 Actions 邮件/通知  

**验收**：连续 3 天仓库自动多一份 digest，本机可关机。

**Actions 注意**：

- 首次 token 必须在**本机**授权生成（带 refresh_token）；Actions **不能**弹浏览器  
- OAuth 同意屏幕若是「测试」模式：测试用户列表里要有你的 Gmail；token 长期策略按 Google 测试 app 规则（可能 7 天过期）→ 若频繁过期，再评估发布状态或改 IMAP  

---

### 阶段 3：打磨（仍不发 X）

- [ ] Prompt 入库 `prompts/`  
- [ ] 解析容错 + 始终保存原始正文备份  
- [ ] 去重（同一天不写两遍）  
- [ ] 可选 `config/accounts.example.yaml`（**仅清单备忘**，不参与拉信；搜谁仍由 Tasks prompt 决定）  
- [ ] digests 索引  

---

### 阶段 4：GitHub Pages（远期）

- 用已有 md 做极简列表 + 单日页  
- **阶段 2 稳定前不动**

---

## 5. 建议仓库结构

```text
grok-daily-digest/
├── PROJECT_PLAN.md
├── README.md
├── prompts/
│   └── daily_task_v1.md
├── src/
│   ├── gmail_client.py      # OAuth + list/get message
│   ├── parse_digest.py      # 正文 → 结构
│   └── write_digest.py      # digests/YYYY-MM-DD.md
├── scripts/
│   └── run_daily.py         # 入口
├── digests/
│   └── .gitkeep
├── .github/workflows/
│   └── daily-digest.yml     # 阶段 2
├── requirements.txt
└── .gitignore
```

阶段 1 **不强制**建 `config/`。

---

## 6. Prompt 策略（Grok Tasks）

> 代码只是管道；**搜谁、写什么**由 Tasks prompt 决定。

### 6.1 Prompt v1（可贴 Tasks）

```text
你是专业的科技与 AI 新闻策展专家，面向 CS 开发者（项目、工程实践、职业/side hustle、agent 开发）。

任务：总结过去 24 小时内 X 平台上的重要科技前沿消息和大佬动态。

覆盖范围（优先级）：
1. 科技/AI 大佬及官方（如 @elonmusk、@OpenAI、@AnthropicAI、@xai、@sama、@levelsio）
2. 生产力/笔记/AI 工具（@NotionHQ、@obsdmd、@Google、@GoogleAI、Tabbit 等）
3. 模型发布、工具更新、基准、融资、争议、行业趋势
4. 中国相关（X 上有高质量讨论时）

搜索：x_search 指定账号 + semantic search 高热话题。

输出：
- 每天 5–8 条，高价值 + 高热度
- 每条：一句话事实 + 尽量摘录原推文关键句（保留原文语言）+ CS 实用点（有则写）+ 来源 @/链接
- 中立、简洁、不 hype
- 开头一句今日总览

请生成可直接归档的每日 digest。
```

可选：让输出带 `【HOOK】/【ITEM1】…` 标签，方便脚本解析（阶段 3 再加强）。

---

## 7. 备用方案：IMAP（仅当 Gmail API 走不通）

| 步骤 | 内容 |
|------|------|
| 1 | Google 账号两步验证 |
| 2 | 生成应用专用密码 |
| 3 | Gmail 设置打开 IMAP |
| 4 | `imaplib` 连接 `imap.gmail.com`，Secrets：`GMAIL_ADDRESS` + `GMAIL_APP_PASSWORD` |

本机在中国连 IMAP 也常需可访问 Google 的网络；**Actions 上通常更稳**。  
与主路径二选一即可，避免两套长期并行维护。

---

## 8. 风险

| 风险 | 缓解 |
|------|------|
| OAuth 测试应用 token 短期失效 | 本机重新授权更新 Secret；或改 IMAP |
| 首次授权 / 本机访问 Google 失败 | VPN；或 IMAP |
| 邮件格式变化 | 原始正文落盘 + 宽松解析 |
| Secrets 泄露 | 永不 commit；Public 仓只放 digests 正文 |
| Tasks 比 Actions 晚发 | cron 延后；按日期搜「今天」的信 |
| Grok 摘要幻觉 | 强制来源；你抽查 |

---

## 9. 成功标准

1. 工作日不用开 Grok/X，也能靠 **邮件 + 仓库 digests** 看到当天摘要  
2. **零** xAI / LLM token 生成费用  
3. **Gmail API 主路径** 本机跑通，再上 Actions  
4. 内容：原推文可见、CS/agent 相关、5–8 条高热  
5. 不发 X、不做 Pages（直到阶段 4）  

---

## 10. 立刻下一步（建议顺序）

| 顺序 | 谁 | 做什么 |
|------|----|--------|
| 1 | 你 | 确认 `client_secret_*.json` 已备份到安全本地目录 |
| 2 | 你 | Grok Tasks 至少产出 **1 封** 样例邮件（有发件人/主题更好） |
| 3 | 我 | 写阶段 1：授权 + 读信 + 写 `digests/` + README + gitignore |
| 4 | 你 | 本机开可访问 Google 的网络，跑通首次授权 |
| 5 | 双方 | 通过后再做阶段 2 Actions |

---

## 11. 已拍板汇总

| # | 项 | 结论 |
|---|----|------|
| 1 | 生成摘要 | **仅 Grok Tasks**，永不 xAI API |
| 2 | 读邮件 | **主：Gmail API**（已启用）；**备：IMAP** |
| 3 | 交付 | 邮件通知 + **GitHub digests 归档** |
| 4 | 仓库 | **Public**；密钥只进 Secrets |
| 5 | 发 X | **不做** |
| 6 | Pages | **远期**，阶段 2 后 |
| 7 | 阶段序 | 0 内容 → 1 本机 API 读通 → 2 Actions → 3 打磨 → 4 Pages |
| 8 | 绑卡办外卡 | **不做** |

---

## 12. 意图复述（v2）

你要的是一套 **免费、被动的个人科技 digest 管道**：

1. **Grok Tasks** 每天在 X 上策展（大佬、工具、中外科技、CS/agent 视角，偏原推文与高热）  
2. 结果进 **Gmail**（手机可通知）  
3. 你已开通 **Gmail API**，本仓库用 **只读 OAuth** 拉信、结构化、写入 **GitHub**  
4. **Actions** 定时跑，电脑不用开  
5. **不**用 LLM token API，**不**自动发 X；远期若公开，用 **Pages** 展示历史  

若与你最新想法仍有出入，直接改 §0–§1 或回复差异；确认后从 **阶段 1 代码**开工。
