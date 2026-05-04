# AI 日报 - 人物与信息源追踪清单

> **版本**: v2.1.0
> **更新时间**: 2026-03-09
> **维护规则**: 每月 Review 一次，根据输出质量和频率动态调整优先级

---

## 追踪体系说明

```
三层人物矩阵:
  L1 实践者/构建者 → 在一线做产品、写代码、有原创思想框架
  L2 深度观察者    → 有最深入的行业解读，Newsletter/播客
  L3 战略决策者    → CEO/首席科学家，定方向
```

| 层级 | 追踪方式 | 搜索频率 | 价值密度 |
|------|---------|---------|---------|
| L1 | 定向人物搜索 + 源直查 | 每日 | ★★★★★ |
| L2 | 源直查(博客/Newsletter) | 每日 | ★★★★☆ |
| L3 | 官方博客 + 采访搜索 | 每周 | ★★★☆☆ |

### 覆盖均衡性原则

**每日 L1 轮换搜索必须覆盖以下至少 4 组**（防止信息窄化）：
1. 海外头部实验室（OpenAI / Anthropic / Google / Meta）至少 2 组
2. AI Coding 产品方（Cursor / Replit / Cognition 等）至少 1 家
3. 独立研究者 / AI Coding 实践者 至少 1 人
4. 中国 AI 团队（DeepSeek / 智谱 / Moonshot / 百度 等）至少 1 家

---

## L1 实践者/构建者

### OpenAI

| 人物 | 角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|------|------|---------|-----------|---------|
| **Jason Wei** | Research Lead | X, Papers | `"Jason Wei" OpenAI` | Chain-of-thought, 模型能力研究 |
| **Mark Chen** | VP of Research | X, 采访 | `"Mark Chen" OpenAI` | GPT/o-系列路线图, 代码生成 |
| **Noam Brown** | Research (推理方向) | X, Papers | `"Noam Brown" OpenAI reasoning` | o1/o3 推理模型方法论 |
| — | 官方 Blog + Changelog | openai.com/blog | `site:openai.com/blog` | 产品发布, 模型更新 |

### Anthropic (Claude / Claude Code)

| 人物 | 角色 | 主要渠道 | 搜索关键词 | 代表输出 |
|------|------|---------|-----------|---------|
| **Barry Zhang** (张宇杰) | Head of Applied AI | X @barry_zyj, YouTube 演讲 | `"Barry Zhang" anthropic` | Agent 设计原则, Skills 范式 |
| **Amanda Askell** | Alignment/Prompt 专家 | X @amandaaskell | `"Amanda Askell" anthropic prompt` | Claude System Prompt 设计者 |
| **Alex Albert** | Claude Relations | X @alexalbert__ | `"Alex Albert" claude` | Claude 使用技巧, 功能更新 |

### Google DeepMind

| 人物 | 角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|------|------|---------|-----------|---------|
| **Jeff Dean** | Chief Scientist | X, 演讲 | `"Jeff Dean" Google AI` | AI 系统架构方向 |
| **Oriol Vinyals** | VP Research | X, Papers | `"Oriol Vinyals" deepmind gemini` | Gemini 系列研究 |
| — | 官方研究页 | deepmind.google/research | `site:deepmind.google` | 论文, 技术突破 |
| — | Google AI Blog | blog.google/technology/ai | `site:blog.google AI` | 产品集成, 应用 |

### Meta AI (FAIR)

| 人物 | 角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|------|------|---------|-----------|---------|
| **Yann LeCun** | 首席科学家 | X @ylecun | `"Yann LeCun"` | 技术路线争鸣, 开源策略 |
| **Joelle Pineau** | VP of AI Research | 采访, Papers | `"Joelle Pineau" meta AI` | FAIR 研究方向 |
| — | 官方 Blog | ai.meta.com/blog | `site:ai.meta.com/blog` | Llama 系列, 开源模型 |

### Cursor / Anysphere

| 人物 | 角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|------|------|---------|-----------|---------|
| **Michael Truell** | CEO, Anysphere | 采访, Podcast | `"Michael Truell" cursor anysphere` | Cursor 产品愿景 |
| **Aman Sanger** | CTO, Anysphere | X, 技术演讲 | `"Aman Sanger" cursor` | 技术架构, Agent 模式 |
| — | 官方 Blog + Changelog | cursor.com/blog, cursor.com/changelog | `site:cursor.com/blog OR site:cursor.com/changelog` | 产品更新 |

### AI Coding 领域关键实践者

| 人物 | 公司/角色 | 主要渠道 | 搜索关键词 | 代表输出 |
|------|----------|---------|-----------|---------|
| **Addy Osmani** | Google Chrome 工程总监 | addyosmani.com/blog | `"Addy Osmani" AI coding LLM` | LLM Coding Workflow |
| **Kent Beck** | 极限编程之父 | X, Pragmatic Engineer | `"Kent Beck" AI coding TDD` | TDD + AI Agent 方法论 |
| **Steve Yegge** | Sourcegraph | sourcegraph.com/blog | `"Steve Yegge" AI coding` | AI 对开发者影响 |
| **Amjad Masad** | Replit CEO | X, replit.com/blog | `"Amjad Masad" replit agent` | AI Agent 编程 |
| **Scott Wu** | Cognition (Devin+Windsurf) CEO | X, cognition.ai/blog | `"Scott Wu" cognition devin` | 自主编程 Agent |
| — | Windsurf | windsurf.com | `site:windsurf.com/blog` | AI IDE, 被 Cognition 收购 |
| — | Claude Code | anthropic.com | `"Claude Code" update` | Anthropic 编程 Agent |

### 国内 AI Coding 产品 (v2.1 新增)

> 2026-03-07 追踪体系扩展时发现国内AI Coding品类覆盖为零，一次性补齐完整梯队。

| 产品/公司 | 定位 | 搜索关键词 | 追踪重点 |
|-----------|------|-----------|---------|
| **通义灵码** (阿里) | Tier1, VS Code/JetBrains插件 | `通义灵码 最新 更新` | 国内装机量最大 |
| **CodeGeeX** (智谱) | Tier1, 全IDE覆盖 | `CodeGeeX 智谱 最新` | 基于GLM系列, 开源 |
| **Fitten Code** | Tier1, 轻量多语言 | `Fitten Code 最新` | 独立AI Coding产品 |
| **豆包MarsCode** (字节) | Tier2, Cloud IDE | `MarsCode 豆包 AI编程` | 字节AI编程入口 |
| **文心快码** (百度) | Tier2, 企业级 | `文心快码 Comate 百度` | 百度AI Coding |
| **CodeArts Snap** (华为) | Tier2, 企业级 | `CodeArts Snap 华为 AI编程` | 华为云AI编程 |
| **aiXcoder** | Tier3, 企业私有化 | `aiXcoder 最新` | 私有化部署 |
| **CodeFuse** (蚂蚁) | Tier3, 蚂蚁开源 | `CodeFuse 蚂蚁 开源` | 开源代码大模型 |

| 人物 | 公司/角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|------|----------|---------|-----------|---------|
| **Andrej Karpathy** | 独立 (前 OpenAI/Tesla) | YouTube, X @karpathy | `"Andrej Karpathy"` | 最通俗的技术深度解读 |
| **Jim Fan** | NVIDIA | X @DrJimFan | `"Jim Fan" NVIDIA AI` | 物理 AI, 具身智能 |
| **Tri Dao** | Together AI | X, Papers | `"Tri Dao" FlashAttention` | 推理效率, 架构创新 |
| **François Chollet** | ARC-AGI 创始人 | X @fchollet | `"François Chollet" ARC AGI` | AGI 评测, 批判性思考 |

### 中国 AI 团队核心人物

| 人物/团队 | 公司/角色 | 主要渠道 | 搜索关键词 | 追踪重点 |
|-----------|----------|---------|-----------|---------|
| **梁文锋** | DeepSeek 创始人 | 采访, 公司博客 | `DeepSeek 梁文锋`, `deepseek-ai latest` | 开源大模型, MoE 架构 |
| **杨植麟** | Moonshot AI / Kimi 创始人 | 采访, 演讲 | `Moonshot 杨植麟 kimi` | 长上下文, 消费级 AI |
| **唐杰** | 智谱AI 首席科学家 | 论文, 演讲 | `智谱 GLM 唐杰` | GLM 系列, Agent |
| **王小川** | 百川智能 CEO | X, 公众号 | `百川智能 王小川` | 搜索增强, 企业AI |
| **文心一言团队** | 百度 | 采访, 发布会 | `文心一言 百度 最新`, `ERNIE latest` | 国产大模型标杆 |
| **通义千问团队** | 阿里 | 官方博客 | `通义千问 阿里 最新`, `Qwen latest` | 开源, 多模态 |
| **豆包团队** | 字节跳动 | 产品更新 | `豆包 字节 AI 最新` | 消费级AI产品 |
| — | DeepSeek 官方 | github.com/deepseek-ai | `site:github.com/deepseek-ai` | 模型发布, 开源 |

---

## L2 深度观察者

### 必读 Newsletter / 博客

| 人物/媒体 | 平台 URL | 检查频率 | 搜索关键词 | 价值定位 |
|-----------|---------|---------|-----------|---------|
| **Gergely Orosz** | newsletter.pragmaticengineer.com | 每周2次 | `site:pragmaticengineer.com AI coding` | 最深入的工程视角 |
| **Swyx ([USER] Wang)** | latent.space | 每周1次 | `site:latent.space` | AI 工程前沿, 深度访谈 |
| **Simon Willison** | simonwillison.net | 每日 | `site:simonwillison.net` | 最及时的工具评测 |
| **Ethan Mollick** | oneusefulthing.org | 每周2次 | `"Ethan Mollick" AI` | AI 对工作方式的影响 |
| **Ben Thompson** | stratechery.com | 每周1次 | `"Ben Thompson" stratechery AI` | 商业战略分析 |

### 中文圈关键声音

| 人物/媒体 | 平台 | 检查频率 | 搜索关键词 | 价值定位 |
|-----------|------|---------|-----------|---------|
| **李沐** | YouTube / B站 | 每周1次 | `"李沐" 论文 AI` | 中文世界最好的论文解读 |
| **宝玉** | X @dotey, 微信公众号 | 每日 | `"宝玉" AI 翻译` | 最快的海外AI信息翻译 |
| **机器之心** | jiqizhixin.com | 每日 | `site:jiqizhixin.com` | 最全面的AI技术媒体 |
| **量子位** | qbitai.com | 每日 | `site:qbitai.com` | 国内AI新闻, 产品评测 |
| **36氪** | 36kr.com | 每日 | `36氪 AI 融资`, `site:36kr.com AI` | AI 投融资, 商业分析 |
| **虎嗅** | huxiu.com | 每日 | `虎嗅 AI 大模型`, `site:huxiu.com AI` | 深度商业评论 |
| **AI新智元** | — | 每日 | `AI新智元 最新` | 国内AI综合资讯 |

### 投融资/产业信息源

| 媒体 | 平台 | 检查频率 | 搜索关键词 | 价值定位 |
|------|------|---------|-----------|---------|
| **CB Insights** | cbinsights.com | 每周1次 | `CB Insights AI funding` | 全球 AI 投融资数据 |
| **PitchBook** | pitchbook.com | 每周1次 | `AI startup funding latest` | 融资轮次, 估值 |
| **IT桔子** | itjuzi.com | 每周1次 | `AI 融资 IT桔子` | 国内 AI 投融资 |
| **TechCrunch** | techcrunch.com | 每日 | `site:techcrunch.com AI funding` | 海外科技融资新闻 |

### 企业 AI 转型研究源（企业AI转型 Tab 优先使用）

| 媒体/机构 | 平台 | 检查频率 | 搜索关键词 | 价值定位 |
|-----------|------|---------|-----------|---------|
| **Deloitte** | deloitte.com | 每季度 | `Deloitte "state of AI" enterprise` | 企业 AI 采纳权威调研 |
| **McKinsey** | mckinsey.com | 每季度 | `McKinsey AI enterprise productivity` | AI 生产力影响分析 |
| **Faros AI** | faros.ai/blog | 每月 | `Faros AI coding ROI developer` | AI 编程 ROI 度量 |
| **CCF** | ccf.org.cn | 每月 | `CCF 研发质效 AI 落地` | 国内研发效能实践 |
| **IDC** | idc.com | 每季度 | `IDC AI enterprise adoption` | 企业 AI 采纳数据 |

### 必听播客

| 播客名 | 主持人 | 平台 | 检查频率 | 价值定位 |
|--------|-------|------|---------|---------|
| **Latent Space** | Swyx + Alessio | Apple/Spotify/YouTube | 每周 | AI 工程最前沿访谈 |
| **Pragmatic Engineer Podcast** | Gergely Orosz | Apple/Spotify | 每周 | 工程视角 AI 深度对话 |
| **Lex Fridman Podcast** | Lex Fridman | YouTube | 按嘉宾 | 长对话, 深度思想交流 |
| **硅谷101** | 泓君 | Apple/Spotify | 每周 | 中文圈最好的硅谷科技播客 |

---

## L3 战略决策者

### 公司级追踪

| 人物 | 公司/角色 | 主要渠道 | 搜索关键词 | 信号权重 |
|------|----------|---------|-----------|---------|
| **Sam Altman** | OpenAI CEO | Blog, X | `"Sam Altman" OpenAI` | GPT 路线图 |
| **Dario Amodei** | Anthropic CEO | 长文 Essays, 采访 | `"Dario Amodei"` | Claude 战略方向 |
| **Sundar Pichai** | Google CEO | 采访, GTC | `"Sundar Pichai" AI Gemini` | Google AI 战略 |
| **Satya Nadella** | Microsoft CEO | 采访, LinkedIn | `"Satya Nadella" AI copilot` | Copilot 战略 |
| **Jensen Huang** | NVIDIA CEO | GTC 主题演讲 | `"Jensen Huang" NVIDIA` | AI 基础设施方向 |
| **Mark Zuckerberg** | Meta CEO | 公开信, 采访 | `"Zuckerberg" meta AI open source` | 开源 AI 策略 |
| **Guillermo Rauch** | Vercel CEO | X, Blog | `"Guillermo Rauch" vercel AI` | AI 前端 / v0.dev |
| **李彦宏** | 百度 CEO | 演讲, 采访 | `李彦宏 AI 百度` | 国内 AI 战略 |

### 官方博客/研究页

| 公司 | URL | 检查频率 | 内容类型 |
|------|-----|---------|---------|
| **OpenAI** | openai.com/blog | 每周2次 | 产品发布, 安全研究 |
| **Anthropic** | anthropic.com/research | 每周2次 | 研究论文, 产品博客 |
| **Google DeepMind** | deepmind.google/research | 每周1次 | 研究论文, 技术突破 |
| **Meta AI** | ai.meta.com/blog | 每周1次 | Llama 系列, 开源 |
| **Cursor** | cursor.com/blog | 每周2次 | 产品更新, 技术博客 |
| **GitHub (Copilot)** | github.blog | 每周1次 | Copilot 更新 |
| **Replit** | replit.com/blog | 每周1次 | Agent 编程 |
| **Cognition** | cognition.ai/blog | 每周1次 | Devin 进展 |
| **DeepSeek** | github.com/deepseek-ai | 每周2次 | 开源模型, 论文 |
| **Mistral** | mistral.ai/news | 每周1次 | 开源模型, 商业化 |

---

## 搜索执行策略

> **注意**: 以下搜索策略内容与 `daily-report/search-keywords.md` 有重叠。
> 如有冲突，以 `search-keywords.md` 为准。

### 两层搜索架构（v3.8）

| 层级 | 工具 | 定位 | 耗时 | 何时用 |
|------|------|------|------|--------|
| L1 广扫 | `search_web` + `weixin_search` | 广度优先，快速覆盖 | 秒级 | 日报常规搜索、国内信源 |
| L2 精研 | 多轮 `search_web` + `fetch_web` | 深度优先，多角度分析 | 分钟级 | 热点话题深入、专题研究 |

### L1: 每日必做 (Daily Required)

```
# ============ L1 定向人物搜索 (轮换, 每天覆盖至少4组) ============

# OpenAI 团队 (每日至少查1项)
搜索: site:openai.com/blog (最新文章)
搜索: "Jason Wei" OpenAI latest 2026
搜索: "Mark Chen" OpenAI latest

# Anthropic 团队 (每日至少查1项)
搜索: "Barry Zhang" anthropic 2026
搜索: "Amanda Askell" anthropic claude
搜索: "Alex Albert" claude latest

# Google DeepMind (每日至少查1项)
搜索: site:deepmind.google (最新)
搜索: site:blog.google/technology/ai (最新)
搜索: "Gemini" google AI latest

# Meta AI (每周至少查2次)
搜索: site:ai.meta.com/blog (最新)
搜索: "Yann LeCun" latest
搜索: "Llama" meta AI latest

# Cursor 团队 (每日必查)
搜索: site:cursor.com/blog
搜索: site:cursor.com/changelog

# AI Coding 实践者 (每日轮换2个)
搜索: "Addy Osmani" AI coding latest
搜索: "Andrej Karpathy" latest 2026
搜索: "Scott Wu" cognition devin

# 中国 AI 团队 (每日至少查2项)
搜索: DeepSeek 最新 发布
搜索: site:github.com/deepseek-ai (最新)
搜索: Moonshot kimi 最新
搜索: 智谱 GLM 最新
搜索: 通义千问 阿里 最新
搜索: 文心一言 百度 最新
搜索: 豆包 字节 AI 最新

# ============ L2 源直查 (每日必做) ============

直查: simonwillison.net (最近文章)
搜索: site:simonwillison.net (最近7天)
搜索: site:pragmaticengineer.com AI (最近7天)
搜索: site:latent.space (最近7天)
搜索: "宝玉" AI coding 最新
搜索: site:jiqizhixin.com (今日)
搜索: site:qbitai.com (今日)
搜索: 36氪 AI 融资 大模型
搜索: AI startup funding latest

# ============ 通用高热度搜索 ============

# 海外
搜索: AI LLM breakthrough latest {today_date}
搜索: AI coding agent latest news
搜索: AI application launch product {today_date}
搜索: AI enterprise transformation R&D latest

# 国内
搜索: 大模型 最新 发布 动态
搜索: AI编程 代码助手 最新动态
搜索: AI应用 产品 最新 发布
搜索: AI研发效能 企业转型 最新
搜索: AI 融资 收购 投资 最新

# ============ 开源/评测 专项 ============
搜索: AI model benchmark latest leaderboard
搜索: open source LLM release github
搜索: 大模型 开源 评测 排行
搜索: Hugging Face trending models
```

### L1: 每周深度 (Weekly Deep Dive)

```
# L3 官方博客检查
直查: anthropic.com/research (新文章)
直查: openai.com/blog (新文章)
直查: deepmind.google/research (新文章)
直查: ai.meta.com/blog (新文章)
直查: mistral.ai/news (新文章)

# 长文/播客
搜索: "Dario Amodei" essay interview 2026
搜索: "Sam Altman" blog interview 2026
搜索: "Lex Fridman" AI podcast latest
搜索: site:stratechery.com AI
搜索: "Ethan Mollick" one useful thing AI

# 投融资专项
搜索: AI startup funding round 2026
搜索: AI 融资 投资 2026
搜索: AI company valuation unicorn latest

# 政策/监管
搜索: AI regulation policy 2026
搜索: AI 政策 监管 中国 最新
搜索: EU AI Act implementation latest
```

### L2: 精研策略 (v3.8新增，按需触发)

> L2 在 L1 发现热点后触发，用多轮 `search_web` + `fetch_web` 做深入分析。
> 纯内置工具，无需额外API Key。

```
# ============ L2 触发条件 ============
# 多源共振≥3 / 突发事件 / 用户要求深入分析

# ============ L2 执行方式（4步法） ============

# 1. 定向精搜: 多角度关键词搜索
search_web: "[热点话题] latest analysis 2026"
search_web: "[热点话题] expert opinion deep dive"
search_web: "[热点话题] 深度分析 最新"

# 2. 全文提取: fetch_web 获取top 3-5文章完整内容
fetch_web: [top 3-5 URLs from step 1]

# 3. LLM综合: 基于全文内容做综合分析
# 输出→「深度聚焦」素材

# 4. 交叉验证: 对关键事实做定向搜索验证
search_web: "[具体事实或数字] verify source"
```

### 搜索工具选择决策树

```
收到搜索需求
├── 需要国内公众号内容？
│   └── YES → weixin_search（不可替代）
├── 常规新闻扫描？
│   └── YES → search_web（最快覆盖）
├── 需要深入分析某个热点？
│   └── YES → 多轮 search_web + fetch_web（L2精研）
└── 需要验证具体事实？
    └── YES → search_web 定向搜索 + fetch_web 全文验证
```

---

## 内容展示规则

### 人物观点如何进入日报

| 条件 | 处理方式 |
|------|---------|
| L1 人物发表新博客/演讲 | → 作为「深度聚焦」的素材，提炼核心论点融入分析 |
| L2 媒体发布新一期 | → 提炼关键洞察，标注出处 |
| L3 人物重大发言 | → 进入对应领域的「最近动态」，有深度内容可作为「深度聚焦」的素材 |
| 产品 Changelog 更新 | → 进入对应领域的「最近动态」，标注版本号 |
| 无新输出 | → 不强制填充，跳过 |

### 「深度聚焦」人物引用格式 (v3.0)

> v3.0起，人物观点不再作为独立栏目，而是融入「深度聚焦」的分析正文中。
> 以下格式可在深度聚焦正文中引用人物观点：

```html
<!-- 在深度聚焦卡片的body内引用人物观点 -->
<p>Barry Zhang在AI Engineer Summit上提到：<strong>“Skills actually came out of a prototype...”</strong>——这种从实践中生长出来的产品特性，往往比自上而下的设计更有生命力。</p>
```

---

## 优先级动态调整规则

| 信号 | 动作 |
|------|------|
| 某人连续 2 周无新输出 | 降低搜索频率到每周 |
| 某人发布重大内容 (>10K浏览) | 下一期重点追踪 |
| 新发现有影响力的声音 | 加入 L1 或 L2 清单 |
| 追踪名单超过 40 人 | Review 清除低频低质源 |
| 某领域覆盖持续偏薄 | 主动补充该领域信息源 |

---

*清单由林克维护，每月 Review 一次*
