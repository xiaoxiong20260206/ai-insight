# Barry Zhang (张宇杰) - 思想体系

> **人物定位**: Anthropic Applied AI 团队负责人，Agent设计方法论的奠基者
> **更新时间**: 2026-03-04
> **版本**: v1.0

---

## 基本信息

| 属性 | 内容 |
|------|------|
| **姓名** | Barry Zhang (张宇杰) |
| **职位** | Head of Applied AI, Digital Natives & Strategics @ Anthropic |
| **背景** | 前 Meta AI 产品工程师，前 Shopify、Box 工程师 |
| **社交** | [Twitter/X](https://x.com/barry_zyj) / [LinkedIn](https://www.linkedin.com/in/barry-z) |

---

## 核心贡献

### 1. Agent定义框架

与 Erik Schluntz 共同提出业界最清晰的 Agent 定义框架，解决了"Agent"一词被滥用的问题。

**Agentic Systems分类**：
- **Workflows**: 预定义代码路径编排 LLM 和工具
- **Agents**: LLM 动态指导自己的流程和工具使用

### 2. Agent设计三原则

| 原则 | 核心要点 |
|------|---------|
| **Don't Build Agents for Everything** | 能用简单方案就别用Agent |
| **Keep It Simple** | Agent = Model + Tools + Loop |
| **Think Like Your Agent** | 站在Agent的上下文窗口中思考 |

### 3. Skills范式

2025年11月提出的最新思想演进：

> "Don't Build Agents, Build Skills Instead"

**核心洞察**：
- 底层Agent比想象的更通用
- 差异在于Skills，而非Agent架构
- Skills是可复用的程序性知识包

### 4. Agent-Computer Interface (ACI)

提出ACI概念，强调工具设计与Prompt同等重要：

> "We spent more time optimizing our tools than the overall prompt"

---

## 内容来源清单

| 类型 | 标题 | 时间 | 链接 |
|------|------|------|------|
| 📝 博客 | Building Effective Agents | 2024.12 | [Anthropic](https://www.anthropic.com/research/building-effective-agents) |
| 🎤 演讲 | How We Build Effective Agents | 2025.02 | [YouTube (404K+ views)](https://www.youtube.com/watch?v=D7_ipDqhtwk) |
| 🎤 演讲 | Don't Build Agents, Build Skills Instead | 2025.11 | [YouTube (742K+ views)](https://www.youtube.com/watch?v=CEvIs9y1uog) |
| 📰 采访 | Anthropic Researchers Say More AI Agents Isn't the Answer | 2025.12 | [Business Insider](https://www.businessinsider.com/anthropic-researchers-ai-agent-skills-barry-zhang-mahesh-murag-2025-12) |

---

## 经典语录

### 关于简单优先

> "If you can map out the entire decision tree pretty easily, just build that explicitly and then optimize every node."

> "Agentic systems often trade latency and cost for better task performance, and you should consider when this tradeoff makes sense."

### 关于Agent设计

> "Agents can handle sophisticated tasks, but their implementation is often straightforward. They are typically just LLMs using tools based on environmental feedback in a loop."

> "We have learned the hard way to keep this simple, because any complexity up front is really going to kill iteration speed."

### 关于Skills

> "Skills are organized collections of files that package composable procedural knowledge for agents."

> "The industry doesn't need a flurry of agent-building. Instead, 'skills' can equip a general agent with domain expertise and reusable workflows."

### 关于工具设计

> "While building our agent for SWE-bench, we actually spent more time optimizing our tools than the overall prompt."

---

## 思想演进脉络

```
2024.12.19  "Building Effective Agents" 博客发布
            ├── 定义 Agentic Systems、Workflows vs Agents
            ├── 提出 Augmented LLM 概念
            └── 引入 Agent-Computer Interface (ACI) 概念

2025.02     AI Engineer Summit 演讲
            ├── 三大核心原则深化
            ├── Agent 设计检查清单
            └── 未来三大开放问题

2025.11     AI Engineer Code Summit 演讲
            ├── 从"多Agent"到"单Agent+多Skills"的范式转变
            ├── Claude Code 作为通用 Agent 的定位
            └── "Agent 为 Agent 写 Skills" 的未来愿景
```

---

## 影响力数据

| 指标 | 数据 |
|------|------|
| "How We Build Effective Agents" 演讲观看量 | 404K+ |
| "Don't Build Agents, Build Skills" 演讲观看量 | 742K+ |
| 入选"2025年度50个最受关注软件工程演讲" | ✅ |
| Skills 发布后5周内创建数量 | 数千个 |

---

## 追踪建议

- **主要渠道**: Twitter @barry_zyj
- **检查频率**: 每周1次
- **重点关注**: Agent设计方法论更新、Skills生态进展、Anthropic官方博客
