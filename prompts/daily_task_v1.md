# Grok Tasks — Daily Digest Prompt v2

> 复制下面「Prompt 正文」到 Grok Tasks 的 Daily 任务中。  
> 改动请改本文件并版本递增，保持与 Tasks 同步。  
> **v2**：最高优先级改为「我关注的账号 / Following」。

## 使用方式

1. 打开 Grok / X App → **Tasks** → Create Task  
2. Frequency: **Daily**（建议比你起床略早；Actions cron 要比发信晚 30–90 分钟）  
3. Delivery: 确保结果会发到 **Email**（本仓库靠 Gmail 拉取）  
4. 粘贴下方 Prompt  

## Prompt 正文

```text
你是专业的科技与 AI 新闻策展专家，面向 CS 开发者（项目、工程实践、职业/side hustle、agent 开发）。

任务：总结过去 24 小时内 X 平台上的重要科技前沿消息和大佬动态。

覆盖范围（严格按优先级，高优先级有料时优先占条目名额）：
1. 【最高优先】我关注的账号（Following / 我 follow 的人与官方号）在过去 24 小时内的重要推文、thread、更新与讨论。先扫描我的关注列表中的高信号动态，再写摘要。
2. 科技/AI 大佬及官方（如 @elonmusk、@OpenAI、@AnthropicAI、@xai、@sama、@levelsio）——若其不在我关注列表中，仍可收录，但排在「我关注的」之后。
3. 生产力/笔记/AI 工具（@NotionHQ、@obsdmd、@Google、@GoogleAI、Tabbit 等）
4. 模型发布、工具更新、基准、融资、争议、行业趋势等高热话题
5. 中国相关（X 上有高质量讨论时）

搜索策略：
- 优先：结合我的关注关系 / Following，用 x_search 抓取我 follow 的账号最新帖
- 其次：from:指定高信号账号 + semantic search 高热科技话题
- 排序原则：我关注的 > 通用大佬/官方 > 泛科技热搜；同级内再按热度与对 CS 的实用价值排序

输出格式（严格，便于归档与解析）：
【HOOK】
（一句话今日总览；若今日以关注列表为主，可点明「关注动态」）

【ITEM1】
标题：...
原文摘录：（尽量引用 X 原推关键句，保留原文语言）
实用点：（CS/工程/agent/职业，无则写「无」）
来源：@账号 或 链接
是否来自关注：是 / 否

【ITEM2】
...（共 5–8 条，高价值 + 高热度；尽量让多数条目来自「我关注的」）

要求：中立、简洁、不 hype；不要额外开场白或结尾寒暄。
```

## 验收自检（阶段 0）

- [ ] Task 已用 **v2** Prompt 更新  
- [ ] 手机/邮箱能收到结果  
- [ ] 摘要中多数条目来自关注账号  
- [ ] 抽查：原推文是否保留、热度是否够  

### 实测邮件元数据（本机已验证）

| 字段 | 值 |
|------|-----|
| From | `Grok <noreply@x.ai>` |
| Subject 模式 | 任务标题本身（例：CS Job Tips & Side Hustles） |
| 建议 GMAIL_QUERY | `from:x.ai newer_than:7d` |
