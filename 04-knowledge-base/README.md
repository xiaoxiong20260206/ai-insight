# AI-Insight 知识库

> **版本**: v4.3.0
> **创建时间**: 2026-03-04
> **最后更新**: 2026-03-05
> **维护者**: 林克 (沈浪的AI分身)

---

## 知识库概述

这是AI-Insight项目的结构化知识库，用于系统性沉淀AI行业的知识。

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
| **模型** | 4 | 3人 | +1 ✨ |
| **Agent** | 14 | 5人 | - (更新) |
| **AI企业** | 4 | 5人 | - (更新) |
| **企业AI转型** | 7 | 2人 | - |
| **应用** | 1 | - | +1 ✨ |
| **洞察** | 3 | - | - (更新) |
| **总计** | **35** | **7** | **+2新增, 3更新** |

---

## 四大维度索引

### 📊 01-模型 (Models) → [详情](01-models/README.md)

大模型技术、架构演进、训练方法、能力评估

| 文档 | 内容 | 来源 |
|------|------|------|
| `ai-history-and-capability-matrix.md` | AI发展史、海外/国内大模型能力矩阵、竞争焦点演进 | 字节AI指南 |
| `ai-second-half-task-environment.md` | AI下半场理论、底层原理、趋势洞察 | AI大神分析 |
| `reasoning-models.md` ✨ | **推理模型专题**: OpenAI o系列、DeepSeek-R1、CoT技术 | 网络调研 |

**日报关联**: 新模型发布、能力评测、技术创新

---

### 🤖 02-Agent → [详情](02-agents/README.md) ⭐核心维度

Agent架构设计、工作流模式、开发实践、落地应用

| 类型 | 数量 | 核心内容 |
|------|------|---------|
| 人物画像 | 5人 | Barry Zhang, 姚顺雨, Harrison Chase, Jim Fan, Simon Willison |
| 概念文档 | 5个 | Agent架构、Agent矩阵、Ambient Agents、Physical AI、**MCP协议** ✨ |
| 最佳实践 | 4个 | AI编程工作流、金融Agent、团队落地、Agent基础设施 |

**新增**: `model-context-protocol.md` - MCP标准与生态、AAIF基金会、10,000+ MCP Server

**日报关联**: Agent框架、开发实践、应用案例

---

### 🏢 03-AI企业 (AI Companies) → [详情](03-ai-companies/README.md)

AI原生企业画像、商业模式、竞争格局

| 类型 | 数量 | 核心内容 |
|------|------|---------|
| 公司画像 | 4家 | 幻方量化、字节跳动、**OpenAI** ✨、**Anthropic** ✨ |
| 关联人物 | 5人 | 按公司归类 |

**新增**: 
- `openai-profile.md` - OpenAI全景: 产品矩阵、$5000亿估值、Stargate项目
- `anthropic-profile.md` - Anthropic全景: Claude系列、AI安全理念、MCP协议创建者

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

### 👤 人物画像 (7人)

| 人物 | 公司 | 核心贡献 | 主要维度 |
|------|------|---------|---------|
| **Barry Zhang** | Anthropic | Agent定义、五大工作流、Skills范式 | Agent |
| **姚顺雨** | OpenAI | AI下半场理论、代码即affordance | Agent+模型 |
| **Andrej Karpathy** | 前OpenAI/Tesla | Software 3.0、Vibe Coding | 模型+Agent |
| **Simon Willison** | 独立开发者 | Vibe Engineering、上下文管理、TDD复兴 | Agent+企业AI |
| **Harrison Chase** | LangChain | Ambient Agents、Agent Inbox | Agent+AI企业 |
| **Jim Fan** | NVIDIA | Physical Turing Test、Simulation 2.0 | Agent+AI企业 |
| **Addy Osmani** | Google | AI增强工程、六步工作流 | 企业AI |

### 🏢 公司画像 (4家)

| 公司 | 领域 | 核心内容 |
|------|------|---------|
| **OpenAI** ✨ | 大模型领导者 | 产品矩阵、$5000亿估值、Stargate项目、政府合作 |
| **Anthropic** ✨ | AI安全公司 | Claude系列、Constitutional AI、MCP协议、安全立场 |
| **字节跳动** | 大模型/AI应用 | 全栈布局、产品矩阵、战略分析 |
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
│   └── weekly/
└── entity-profiles/             # 实体画像
    ├── people/
    └── companies/
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v4.3.0 | 2026-03-05 | 日报深度学习闭环，新增Gemini 3系列、Gemini for Home，更新OpenAI/AI编程/融资数据 |
| v4.2.0 | 2026-03-05 | 主动网上学习，新增推理模型、MCP协议、OpenAI/Anthropic画像共4篇 |
| v4.1.0 | 2026-03-04 | 按四大维度重新提取知识，新增5篇维度专属文档 |
| v4.0.0 | 2026-03-04 | 引入四大维度结构，与日报方向对齐 |
| v3.0.0 | 2026-03-04 | 新增6个人物画像、2个概念专题 |
| v2.1.0 | 2026-03-04 | 补充字节AI Agent指南 |
| v2.0.0 | 2026-03-04 | 全面重新沉淀，确保信息质量 |
| v1.0.0 | 2026-03-04 | 初始版本 |

---

*最后更新: 2026-03-05*
