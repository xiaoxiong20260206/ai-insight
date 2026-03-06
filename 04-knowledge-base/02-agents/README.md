# Agent

> **维度定义**: Agent架构设计、工作流模式、开发实践、落地应用
> **更新时间**: 2026-03-06
> **状态**: 核心维度，内容丰富

---

## 维度概述

本维度是知识库的**核心维度**，聚焦AI Agent的理论与实践：
- **架构理论**: Agent定义、工作流模式、Skills范式
- **开发实践**: 上下文管理、TDD复兴、工具设计
- **AI Coding**: 多Agent并行、工具趋同进化
- **新兴范式**: Ambient Agents、Physical AI
- **落地应用**: 企业Agent、金融Agent、编程Agent

---

## 内容索引

### AI Coding工具 (2篇)

| 类型 | 内容 | 来源 | 位置 |
|------|------|------|------|
| **工具演进** | AI Coding工具演进与多Agent实践 | AI日报 2026-03-06 | [→链接](ai-coding-tools-evolution-2026-03.md) |
| **最佳实践** | Agent基础设施与调优方法论 | 字节AI开挂指南 | [→链接](agent-infra-and-optimization.md) |

核心内容 (2026-03-06更新)：
- **多Agent并行**: Codex Windows版标配，同时运行多个Agent处理不同任务
- **工具趋同进化**: Claude Code创新功能被Cursor/Codex快速学习
- **GPT-5.4+Codex**: 编程能力与推理能力深度整合

### 核心人物画像 (5人)

| 人物 | 背景 | 核心贡献 | 位置 |
|------|------|---------|------|
| **Barry Zhang** | Anthropic | Agent = Model + Tools + Loop，五大工作流，Skills范式 | [→链接](../entity-profiles/people/barry-zhang.md) |
| **姚顺雨** | OpenAI | AI下半场理论，代码即affordance | [→链接](../entity-profiles/people/shunyu-yao.md) |
| **Harrison Chase** | LangChain | Ambient Agents，Agent Inbox，Deep Agents | [→链接](../entity-profiles/people/harrison-chase.md) |
| **Jim Fan** | NVIDIA | Physical Turing Test，Simulation 2.0 | [→链接](../entity-profiles/people/jim-fan.md) |
| **Simon Willison** | Django创始人 | Vibe Engineering，上下文管理 | [→链接](../entity-profiles/people/simon-willison.md) |

### 概念文档 (4个)

| 概念 | 内容 | 位置 |
|------|------|------|
| **Agent架构** | Agent定义框架、设计原则、五大工作流 | [→链接](../concepts/agents/agent-architecture.md) |
| **Agent类型矩阵** | 9种Agent类型、岗位匹配、建设优先级 | [→链接](../concepts/agents/agent-types-matrix.md) |
| **Ambient Agents** | 环境Agent、事件驱动、Agent Inbox | [→链接](../concepts/agents/ambient-agents.md) |
| **Physical AI** | 物理AI、具身智能、Simulation 2.0 | [→链接](../concepts/agents/physical-ai.md) |

### 最佳实践 (3个)

| 实践 | 内容 | 位置 |
|------|------|------|
| **AI编程工作流** | Simon Willison等人的方法论 | [→链接](../best-practices/ai-coding-workflow.md) |
| **金融AI Agent** | 9种金融Agent详细规格 | [→链接](../best-practices/financial-ai-agent-design.md) |
| **AI Agent团队落地** | 四阶段路线图 | [→链接](../best-practices/ai-agent-team-implementation.md) |

---

## 知识体系图

```
Agent知识体系
├── 理论框架
│   ├── Barry Zhang: Agent = Model + Tools + Loop
│   ├── 姚顺雨: AI下半场，环境定义是瓶颈
│   └── 五大工作流: Prompt Chaining → Router → Parallelization → Orchestrator → Evaluator
│
├── 开发实践
│   ├── 开发方案: 零码 → 低码 → 全码
│   ├── 工具全家桶: Eino、veADK、扣子、CozeLoop
│   └── 评测·观测·调优三件套
│
├── 架构演进
│   ├── 对话Agent → Ambient Agent → Physical Agent
│   └── Multi-Agent → Single Agent + Skills
│
├── 上下文管理
│   ├── Context is King
│   ├── TDD复兴 (测试驱动Agent)
│   └── ACI设计 (Agent Computer Interface)
│
└── 垂直应用
    ├── 编程Agent (Cursor/Claude Code)
    ├── 金融Agent (9种类型)
    └── 企业Agent (数字员工)
```

---

## 相关日报方向

当日报涉及以下内容时，应沉淀到此维度：
- Agent框架/工具发布
- Agent开发最佳实践
- Agent应用案例
- 人物访谈/深度分享

---

*创建时间: 2026-03-04*
