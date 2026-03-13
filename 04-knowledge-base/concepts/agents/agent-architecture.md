# Agent架构与设计模式

> **知识类型**: 概念
> **来源**: Barry Zhang (Anthropic)、Harrison Chase (LangChain)、姚顺雨 (OpenAI) 深度分享
> **更新时间**: 2026-03-13
> **版本**: v1.1 - 新增Skills范式、GPT-5.4 Tool Search、IETF Agent Gateway

---

## 核心概念

### Agent定义框架 (Barry Zhang)

```
Agentic Systems (智能系统)
├── Workflows (工作流)
│   └── 通过预定义代码路径编排 LLM 和工具
│   └── 特点：可预测、一致性强、适合明确定义的任务
│   └── 适用：当需要可预测性和一致性时
└── Agents (智能体)
    └── LLM 动态指导自己的流程和工具使用
    └── 特点：自主性强、灵活性高、适合开放问题
    └── 适用：当需要模型驱动决策和规模化灵活性时
```

**Agent本质公式**：
```
Agent = Model + Tools + Loop (环境反馈)
```

**2026.03演进**：
```
Agent = Model + Skills + Tool Search + Loop
其中 Skills = 可复用的能力单元 (SKILL.md通用格式)
     Tool Search = 智能工具发现 (解决上下文爆炸)
```

### Augmented LLM (增强型LLM)

构建所有 agentic systems 的基础构建块：

| 增强能力 | 描述 | 实现方式 |
|---------|------|---------|
| **Retrieval (检索)** | 生成搜索查询，获取外部知识 | RAG、向量数据库 |
| **Tools (工具)** | 选择并调用合适的工具 | Function Calling |
| **Memory (记忆)** | 决定保留哪些信息 | 上下文管理、长期记忆 |

---

## 设计原则

### 原则一：简单优先 (Keep It Simple)

> "If you can map out the entire decision tree pretty easily, just build that explicitly and then optimize every node." — Barry Zhang

**决策检查清单**：

| 维度 | 适合 Agent ✅ | 适合 Workflow/简单调用 ⚡ |
|------|-------------|------------------------|
| **任务复杂度** | 问题空间模糊，难以预测所需步骤数 | 可以轻松画出完整决策树 |
| **任务价值** | 高价值产出，不限 token 预算 | 低预算（如每任务 $0.10）|
| **关键能力** | 核心能力已验证，无明显瓶颈 | 存在基础能力短板 |
| **错误成本** | 低风险、错误易发现和恢复 | 高风险、错误难以检测 |
| **可验证性** | 结果可通过测试或反馈验证 | 结果难以客观评估 |

### 原则二：像Agent一样思考 (Think Like Your Agent)

Agent 在每一步推理时，所知道的关于世界的一切都只有 **10-20K tokens**。调试方法：

| 方法 | 具体操作 |
|------|---------|
| **让模型检查Prompt** | 问："这个 prompt 有歧义吗？如果是你会怎么理解？" |
| **让模型评估工具描述** | 问："这个工具描述清楚吗？你知道什么时候该用吗？" |
| **分析Agent轨迹** | 把 Agent 的决策历史喂给模型，问："你为什么在第3步选择了这个工具？" |

### 原则三：Skills优于多Agent

> "We used to think agents in different domains will look very different. The agent underneath is actually more universal than we thought." — Barry Zhang

**范式转变**：
```
旧范式: 为每个领域/用例构建不同的 Agent
   ↓
新范式: 单一通用 Agent + 可扩展的 Skills 库
```

**Skills定义**：
> "Skills are organized collections of files that package composable procedural knowledge for agents."

---

## 五大工作流模式

### 1. Prompt Chaining (提示链)

```
输入 → LLM₁ → [检查] → LLM₂ → [检查] → LLM₃ → 输出
```

**适用场景**：任务可干净地分解为固定子任务
**示例**：生成营销文案 → 翻译成中文

### 2. Routing (路由)

```
输入 → 分类器 → ┬→ 处理路径 A
               ├→ 处理路径 B
               └→ 处理路径 C
```

**适用场景**：有明确分类且各类需要不同处理
**示例**：客服问题分流（常见问题 → 退款 → 技术支持）

### 3. Parallelization (并行化)

```
        ┌→ LLM₁ →┐
输入 → ─├→ LLM₂ →├→ 聚合 → 输出
        └→ LLM₃ →┘
```

**两种变体**：
- **Sectioning**: 拆分为独立子任务并行执行
- **Voting**: 同一任务多次执行取共识

### 4. Orchestrator-Workers (协调者-工作者)

```
任务 → Orchestrator → ┬→ Worker₁ →┐
                      ├→ Worker₂ →├→ 合成 → 输出
                      └→ Worker₃ →┘
```

**适用场景**：子任务由输入决定，不是预定义的
**示例**：代码 Agent 修改多个文件

### 5. Evaluator-Optimizer (评估-优化)

```
任务 → 生成器 LLM → 评估器 LLM → ┬→ 通过 → 输出
                    ↑           └→ 不通过 → 反馈
                    └────────────────────────┘
```

**适用场景**：有明确评估标准，人类反馈能提升质量
**示例**：文学翻译捕捉细微差别

---

## Agent-Computer Interface (ACI)

类比人机交互 (HCI)，Barry Zhang 提出了 Agent-Computer Interface 概念：

> "One rule of thumb is to think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)."

### 工具设计原则

| 原则 | 说明 | 反例 |
|------|------|------|
| **给模型思考空间** | 让模型有足够 tokens 计划后再行动 | 要求模型直接输出 diff |
| **贴近自然文本** | 格式应接近模型在训练数据中见过的 | 高度结构化的自定义 DSL |
| **避免格式开销** | 无需精确计数或转义 | JSON 中的代码需要转义 |

### 工具定义最佳实践

- 站在模型角度：问自己"仅看描述和参数，工具用法明显吗？"
- 写优质文档：像给初级开发者写 docstring
- 包含示例：提供使用示例、边界情况
- Poka-yoke 设计：改变参数设计使错误难以发生

---

## Ambient Agents (环境Agent)

> "Ambient agents operate on a fundamentally different paradigm" — Harrison Chase

**核心特点**：
- **Event-driven**: 事件驱动，不需要人类显式触发
- **Scalable**: 可扩展，数千个Agent并行运行
- **Relaxed latency**: 放松的延迟要求
- **Complex operations**: 复杂操作，后台异步执行

**人机协作方式**：Agent Inbox
- Agent 完成任务后通知人类
- 人类审批/修改后 Agent 继续执行

---

## Coding 是 Agent 的最佳用例

| 维度 | 分析 |
|------|------|
| **复杂性** ✅ | 从设计文档到 PR，过程高度模糊和复杂 |
| **价值** ✅ | 优质代码价值极高，值得消耗大量 tokens |
| **能力验证** ✅ | Claude 等模型已证明编码能力出色 |
| **可验证性** ✅ | 通过单元测试、CI/CD 自动验证结果正确性 |
| **反馈循环** ✅ | 测试结果提供明确的环境反馈 |

---

## 未来开放问题

1. **预算感知 (Budget-Aware Agents)**: 如何让 Agent 自己感知和管理预算约束
2. **自进化工具 (Self-Evolving Tools)**: 让 Agent 设计和改进自己的工具
3. **多Agent协作 (Multi-Agent Collaboration)**: Agent 间如何通信和协作

---

## 参考资料

- [Building Effective Agents - Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [Don't Build Agents, Build Skills Instead - YouTube](https://www.youtube.com/watch?v=CEvIs9y1uog)
- [Ambient Agents - Harrison Chase](https://inferencebysequoia.substack.com/p/ambient-agents-and-the-new-agent)
- [姚顺雨 3小时播客访谈](https://www.xiaoyuzhoufm.com/episode/68c29ca12c82c9dccadba127)
