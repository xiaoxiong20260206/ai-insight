# AI-Insight 知识库

> **版本**: v5.0.0
> **创建时间**: 2026-03-04
> **最后更新**: 2026-03-13
> **维护者**: 林克 (沈浪的AI分身)

---

## 知识库概述

这是AI-Insight项目的结构化知识库，用于系统性沉淀AI行业的知识。

**v5.0更新** (2026-03-13 主动学习+去伪存真):
- ✨ 模型: **DeepSeek V4专题** - ~1T参数MoE，非Nvidia训练（华为昇腾+寒武纪），100万上下文，原生多模态
- ✨ 模型: **中国大模型2026.03格局** - GLM-5(744B)、Qwen 3.5系列、Step-3.5-Flash、MiniMax-M2.5
- ✨ 洞察: **AI驱动裁员追踪** - 3月单月45,000人，9,200+明确因AI
- 🔄 OpenAI画像: 营收更新至$250亿年化、GPT-5.4 Agent OS关键指标、#QuitGPT运动
- 🔄 Anthropic画像: Opus 4.6 exploit里程碑(CVE-2026-2796)、被列为“供应链风险”
- 🔄 GPT-5系列: 补充OSWorld 75%、1M上下文、Tool Search等关键指标
- 🔄 AI融资: 新增3月数据（AMI Labs $10.3亿、Nscale $20亿）
- 🔄 AI Coding: Skills生态爆发（SKILL.md通用格式、1234+技能库、GWS MCP）

**v4.8更新** (2026-03-06 微信公众号主动学习):
- ✨ Agent: **38位中国AI领军人物2026趋势共识** - 来自甲子光年深度访谈
- ✨ 模型: **Gemini 3.1 Flash-Lite详细指标** - 363 tokens/s，GPQA 86.9%
- ✨ 企业: **Max Schwarzer离职动态** - OpenAI后训练核心加入Anthropic
- ✨ 洞察: **Claude App Store下载超越ChatGPT** - 消费端竞争格局变化
- 🔄 周报更新: 新增微信公众号源沿淀

**v4.7更新** (2026-03-06 系统性主动学习):
- 🤖 Agent: **Agentic Engineering Patterns** - Simon Willison的2026编程范式指南
- ⚠️ 安全: **AI安全时间线预测** - MIRI、Jack Clark等对AGI时间线的分析
- 📈 洞察: **周报更新** - November 2025 Inflection Point多方验证
- 📊 模型: 索引更新 - GPT-5.4、Gemini 3.1系列、Qwen 3.5动态
- 🏢 AI企业: Anthropic画像更新 - 2027盈利目标、$700亿2028营收目标

**v4.5更新**: 新增Crawl4AI开源LLM友好爬虫研究：
- 🛠️ 基础设施: **Crawl4AI技术调研** (开源爬虫, 50K+ Star, LLM友好Markdown, MCP集成, Agent数据获取)

**v4.4更新**: 新增市场跟踪文档：
- 📈 洞察: **AI Coding市场跟踪** (实时价格对比、模型评分、GPT 5.3 Instant、Gemini 3.1 Flash-Lite)

**v4.3更新**: 日报深度学习闭环，新增5篇文档：
- 📊 模型: **Gemini 3系列专题** (Flash-Lite、模型迁移指南)
- 🏢 AI企业: **OpenAI画像更新** (GPT-5.3 Instant、Codex桌面App、$8400亿估值)
- 🤖 Agent: **AI编程工具对比更新** (Codex vs Claude Code、Gemini CLI)
- 📈 洞察: **2月AI融资数据** ($1890亿创纪录、资本两极分化)
- 📱 应用: **Gemini for Home** (智能家居AI、Live Search)

---

## 📊 统计概览

| 维度 | 文档数 | 人物 | 新增本次 |
|------|--------|------|----------|
| **模型** | 7 | 3人 | +2 ✨ (DeepSeek V4专题、中国模型格局) |
| **Agent** | 16 | 5人 | 更新Skills生态 |
| **AI企业** | 5 | 5人 | 更新OpenAI/Anthropic画像+融资 |
| **企业AI转型** | 7 | 2人 | - |
| **安全** | 1 | - | - |
| **洞察** | 5 | - | +1 ✨ (AI裁员追踪) |
| **总计** | **43** | **7** | **+3新增 +6更新** |

---

## 四大维度索引

### 📊 01-模型 (Models) → [详情](01-models/README.md)

大模型技术、架构演进、训练方法、能力评估

| 文档 | 内容 | 来源 |
|------|------|------|
| `gpt-5-series-evolution.md` ✨ | **GPT-5系列演进**: GPT-5.4 OSWorld 75%超越人类、Tool Search省47%、1M上下文 | AI日报 2026-03-13 |
| `deepseek-v4.md` ✨ | **DeepSeek V4专题**: ~1T参数MoE，非Nvidia训练，100万上下文，原生多模态 | 网络调研 2026-03-13 |
| `china-models-landscape-2026-03.md` ✨ | **中国大模型格局**: GLM-5、Qwen 3.5、Step-3.5-Flash、MiniMax-M2.5 | 网络调研 2026-03-13 |
| `ai-history-and-capability-matrix.md` | AI发展史、海外/国内大模型能力矩阵、竞争焦点演进 | 字节AI指南 |
| `ai-second-half-task-environment.md` | AI下半场理论、底层原理、趋势洞察 | AI大神分析 |
| `reasoning-models.md` | **推理模型专题**: OpenAI o系列、DeepSeek-R1、CoT技术 | 网络调研 |

**日报关联**: 新模型发布、能力评测、技术创新

---

### 🤖 02-Agent → [详情](02-agents/README.md) ⭐核心维度

Agent架构设计、工作流模式、开发实践、落地应用

| 类型 | 数量 | 核心内容 |
|------|------|---------|
| AI Coding | 3篇 | **Agentic Engineering Patterns** ✨, AI Coding工具演进, Agent基础设施 |
| 人物画像 | 5人 | Barry Zhang, 姚顺雨, Harrison Chase, Jim Fan, Simon Willison |
| 概念文档 | 5个 | Agent架构、Agent矩阵、Ambient Agents、Physical AI、**MCP协议** |
| 最佳实践 | 4个 | AI编程工作流、金融Agent、团队落地、Agent基础设施 |

**新增**: `agentic-engineering-patterns-2026.md` - Simon Willison的Agentic Engineering Patterns，Vibe Coding vs Agentic Engineering区分，核心模式（代码成本低、Red/Green TDD、线性走读、技能囤积）

**日报关联**: Agent框架、开发实践、应用案例

---

### 🏢 03-AI企业 (AI Companies) → [详情](03-ai-companies/README.md)

AI原生企业画像、商业模式、竞争格局

| 类型 | 数量 | 核心内容 |
|------|------|---------|
| 行业分析 | 1篇 | **2026年AI投融资动态** ✨ (2月$1890亿创历史记录) |
| 公司画像 | 4家 | 幻方量化、字节跳动、OpenAI、Anthropic |
| 关联人物 | 5人 | 按公司归类 |

**新增**: `ai-funding-2026.md` - 2月融资$1890亿创历史, 83%流向三巨头, 美国占92%

**日报关联**: 公司融资、产品发布、战略动态

---

### 🏭 04-企业AI转型 (Enterprise AI) → [详情](04-enterprise-ai/README.md)

传统企业AI应用、数字化转型、组织变革

| 类型 | 数量 | 核心内容 |
|------|------|---------|
| 概念文档 | 2个 | 软件工程3.0、AI编程实践 |
| 最佳实践 | 5个 | AI Studio、数字员工、落地路线图、**转型方法论** ✨ |

**新增**: `enterprise-ai-transformation-methodology.md` - 三步走策略、提效场景全景图、安全合规要点

**日报关联**: 企业案例、研发提效、数字员工

---

## 本次新增内容摘要

### 📊 模型维度

1. **推理模型专题** ✨ (v4.2新增)
   - OpenAI o系列: o1、o3、o4-mini演进，视觉推理、工具使用
   - DeepSeek-R1: 671B参数MoE架构，MIT开源，4阶段RL训练
   - 核心技术: Chain-of-Thought、Test-Time Compute、强化学习
   - 应用: Codex CLI、推理vs传统LLM选择指南

### 🤖 Agent维度

2. **MCP协议专题** ✨ (v4.2新增)
   - 定位: "AI的USB-C"，连接AI与外部系统的开放标准
   - 生态: 10,000+ MCP Server、97M+月SDK下载、75+ Claude Connector
   - 采用: ChatGPT、Cursor、Gemini、VS Code等主流产品
   - AAIF: Linux Foundation下的Agentic AI Foundation
   - 创始项目: MCP (Anthropic)、goose (Block)、AGENTS.md (OpenAI)

### 🏢 AI企业维度

3. **OpenAI公司画像** ✨ (v4.2新增)
   - 估值: $5,000亿 (2025.10)，全球最高估值私有公司
   - 收入: $120亿年化 (2025)
   - 产品矩阵: ChatGPT、GPT-5.2、o3、Sora、Codex CLI等
   - 战略: Stargate项目($5000亿)、Microsoft合作、政府合同
   - 争议: 版权诉讼、安全团队流失、2023董事会危机

4. **Anthropic公司画像** ✨ (v4.2新增)
   - 估值: $3,800亿 (2026.02)
   - 收入: $140亿 (2025)，Claude Code $10亿年化收入
   - 产品: Claude系列 (4.6最新)、Claude Code、Claude Cowork
   - 技术特色: Constitutional AI、可解释性研究、MCP协议
   - 安全立场: 拒绝国防部取消AI安全限制要求 (2026.02)
   - 收购: Bun (JavaScript运行时)

---

## 知识资产详情

### 👤 人物画像 (14人)

| 人物 | 公司 | 核心贡献 | 主要维度 |
|------|------|---------|---------|
| **Sam Altman** ✨ | OpenAI | ChatGPT帝国、Stargate计划、$8400亿估值 | AI企业 |
| **Dario Amodei** ✨ | Anthropic | 安全AI领袖、Constitutional AI、$3800亿估值 | AI企业+安全 |
| **Jensen Huang** ✨ | NVIDIA | AI芯片帝国、$3.4万亿市值、"We run them all" | AI企业 |
| **Satya Nadella** ✨ | Microsoft | Agentic Web、Copilot生态、OpenAI战略绑定 | AI企业+企业AI |
| **梁文峰** ✨ | DeepSeek | 效率革命、R1"Sputnik时刻"、开源信仰 | 模型+AI企业 |
| **李开复** ✨ | 零一万物 | 企业多Agent元年、To B转型 | 企业AI |
| **Yann LeCun** ✨ | AMI Labs | 图灵奖、世界模型、$10.3亿种子轮 | 模型 |
| **Barry Zhang** | Anthropic | Agent定义、五大工作流、Skills范式 | Agent |
| **姚顺雨** | OpenAI | AI下半场理论、代码即affordance | Agent+模型 |
| **Andrej Karpathy** | 前OpenAI/Tesla | Software 3.0、Vibe Coding | 模型+Agent |
| **Simon Willison** | 独立开发者 | Agentic Engineering、上下文管理 | Agent+企业AI |
| **Harrison Chase** | LangChain | Ambient Agents、Agent协议格局 | Agent+AI企业 |
| **Jim Fan** | NVIDIA | Physical Turing Test、Simulation 2.0 | Agent+AI企业 |
| **Addy Osmani** | Google | AI增强工程、六步工作流 | 企业AI |

### 🏢 公司画像 (12家)

| 公司 | 领域 | 核心内容 |
|------|------|---------|
| **OpenAI** | 大模型领导者 | $8400亿估值、$250亿年化收入、GPT-5系列、Stargate |
| **Anthropic** | AI安全公司 | $3800亿估值、Claude系列、MCP协议、安全立场 |
| **NVIDIA** ✨ | AI算力基础设施 | $3.4万亿市值、$1305亿收入、AI芯片90%+份额 |
| **Google DeepMind** ✨ | AI研究+产品 | Gemini系列、AlphaFold诺贝尔奖、GWS MCP |
| **Meta AI** ✨ | 开源大模型 | Llama系列、MTIA芯片、LeCun离职后转向 |
| **Microsoft** ✨ | AI平台化 | Copilot生态、Azure AI、OpenAI 27%股权 |
| **DeepSeek** ✨ | 极致效率开源 | ~1T参数V4、非Nvidia训练、$557万训练R1 |
| **智谱AI** ✨ | 国产AI国家队 | GLM-5(744B)、港股上市、清华系 |
| **Cursor/Anysphere** ✨ | AI编程工具 | $293亿估值、$20亿ARR、增长最快的企业软件 |
| **MiniMax** ✨ | 多模态AI | 港股上市、$1.5亿ARR、"坚决不做豆包" |
| **字节跳动** | 大模型/AI应用 | 全栈布局、豆包2.27亿MAU、产品矩阵 |
| **幻方量化** | 量化投资 | DeepSeek孵化、AI应用、竞争力分析 |

---

## 日报→知识库映射

| 日报内容类型 | 沉淀维度 | 示例 |
|-------------|---------|------|
| 新模型发布/评测 | **模型** | GPT-5发布、Claude 4评测 |
| 模型技术突破 | **模型** | 新训练方法、推理优化 |
| Agent框架/工具 | **Agent** | LangGraph更新、新Agent框架 |
| Agent开发实践 | **Agent** | 工作流设计、上下文管理 |
| 公司融资/动态 | **AI企业** | OpenAI融资、Anthropic发布 |
| 企业AI应用案例 | **企业AI** | XX公司AI转型、研发提效 |
| 人物访谈/分享 | **人物画像** | 新增人物或更新观点 |

---

## 目录结构

```
04-knowledge-base/
├── README.md                    # 本文件
├── 01-models/                   # 模型维度
│   ├── README.md
│   ├── ai-history-and-capability-matrix.md
│   ├── ai-second-half-task-environment.md
│   └── reasoning-models.md              ✨ v4.2新增
├── 02-agents/                   # Agent维度
│   ├── README.md
│   ├── agent-infra-and-optimization.md
│   └── model-context-protocol.md        ✨ v4.2新增
├── 03-ai-companies/             # AI企业维度
│   ├── README.md
│   ├── bytedance-ai-landscape.md
│   ├── openai-profile.md                ✨ v4.2新增
│   └── anthropic-profile.md             ✨ v4.2新增
├── 04-enterprise-ai/            # 企业AI转型维度
│   ├── README.md
│   └── enterprise-ai-transformation-methodology.md
├── concepts/                    # 概念文档
│   ├── agents/
│   ├── applications/           # AI应用 ✨
│   ├── coding/
│   └── enterprise/
├── best-practices/              # 最佳实践
├── insights/                    # 洞察
│   ├── ai-coding-market-tracking.md   ✨ v4.4新增
│   ├── ai-industry-trends-2026.md
│   └── weekly/
└── entity-profiles/             # 实体画像
    ├── people/
    └── companies/
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v4.7.0 | 2026-03-06 | 系统性主动学习：Agentic Engineering Patterns、AI安全时间线、周报更新 |
| v4.6.0 | 2026-03-06 | 日报知识沉淀：GPT-5系列演进、融资动态、多Agent并行 |
| v4.5.0 | 2026-03-05 | 新增Crawl4AI开源LLM友好爬虫技术调研(基础设施维度) |
| v4.4.0 | 2026-03-05 | 新增AI Coding市场跟踪文档 |
| v4.3.0 | 2026-03-05 | 日报深度学习闭环，新增Gemini 3系列、Gemini for Home，更新OpenAI/AI编程/融资数据 |
| v4.2.0 | 2026-03-05 | 主动网上学习，新增推理模型、MCP协议、OpenAI/Anthropic画像共4篇 |
| v4.1.0 | 2026-03-04 | 按四大维度重新提取知识，新增5篇维度专属文档 |
| v4.0.0 | 2026-03-04 | 引入四大维度结构，与日报方向对齐 |
| v3.0.0 | 2026-03-04 | 新增6个人物画像、2个概念专题 |
| v2.1.0 | 2026-03-04 | 补充字节AI Agent指南 |
| v2.0.0 | 2026-03-04 | 全面重新沉淀，确保信息质量 |
| v1.0.0 | 2026-03-04 | 初始版本 |

---

*最后更新: 2026-03-13*
