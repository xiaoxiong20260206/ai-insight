# Harrison Chase

> **知识类型**: 人物画像
> **身份**: LangChain CEO & 联合创始人
> **领域**: Agent架构、Ambient Agents、LangGraph生态
> **更新时间**: 2026-03-13
> **版本**: v1.1 - 新增MCP生态演进、IETF标准化、Google A2A协议

---

## 人物简介

Harrison Chase是LangChain的CEO和联合创始人，也是Agent架构领域最具影响力的实践者之一。他创建的LangChain框架成为LLM应用开发的事实标准。他对Agent演进方向的洞察（Ambient Agents、Deep Agents）深刻影响了行业发展。

| 维度 | 信息 |
|------|------|
| **所属机构** | LangChain |
| **职位** | CEO & 联合创始人 |
| **专注领域** | Agent架构、LLM应用框架、工作流编排 |
| **核心贡献** | LangChain框架、Ambient Agents概念、Agent Inbox、Deep Agents |

---

## 核心思想体系

### 一、Ambient Agents (环境Agent) 概念

> **"Ambient agents operate on a fundamentally different paradigm"**
> 环境Agent在根本不同的范式上运行

Harrison Chase提出的Ambient Agents是对传统对话式Agent的范式升级：

| 维度 | 传统对话Agent | Ambient Agent |
|------|-------------|---------------|
| **触发方式** | 人类显式发起 | 事件驱动，后台监听 |
| **运行模式** | 同步、实时响应 | 异步、后台持续运行 |
| **运行数量** | 单一会话 | 数千个并行 |
| **延迟要求** | 低延迟 | 延迟宽松 |
| **交互模式** | 对话式 | 通过Inbox协作 |

**Ambient Agents的四大特征**：
1. **Event-driven**: 由事件触发而非人类命令
2. **Scalable**: 可以并行运行数千个
3. **Relaxed latency**: 不需要即时响应
4. **Complex operations**: 可执行长时间复杂任务

### 二、Agent Inbox 概念

> **人机协作的新范式：Agent通过Inbox与人类异步沟通**

Harrison Chase提出的Agent Inbox改变了人机交互模式：

```
传统模式:
用户 ←→ Agent (同步对话)

Inbox模式:
用户 ← Agent Inbox ← Agent (异步消息)
        ↓
    用户在方便时处理
```

| 组件 | 作用 |
|------|------|
| **Agent** | 后台运行，执行任务 |
| **Inbox** | 汇集Agent的消息、问题、成果 |
| **Human** | 按自己的节奏处理Inbox |

**核心价值**：
- 人类不需要实时响应Agent
- Agent可以并行处理多个任务
- 人类只在关键决策点介入

### 三、Deep Agents 架构

> **"Deep agents本质是: Prompt + Tools + Subagents"**

Harrison Chase定义的Deep Agents架构：

```
Deep Agent = Prompt + Tools + Subagents
           (核心指令) (能力) (子Agent)
```

| 组件 | 作用 | 关键洞察 |
|------|------|---------|
| **Prompt** | 定义Agent的角色、目标、行为 | "复杂度应该放在Prompt里，而不是架构里" |
| **Tools** | 给Agent赋予具体能力 | 工具是Agent的手脚 |
| **Subagents** | 处理特定子任务 | 分而治之 |

**关键原则**：
- 复杂度放在Prompt里，架构保持简单
- 与Barry Zhang的"Skills > Multi-Agent"观点一致

### 四、LangGraph作为运行时

> **"LangGraph is the runtime. LangChain is the abstraction."**

Harrison Chase对LangChain生态的定位：

| 层级 | 组件 | 作用 |
|------|------|------|
| **抽象层** | LangChain | 统一的LLM交互抽象 |
| **运行时** | LangGraph | Agent工作流编排和执行 |
| **应用层** | Deep Agents | 端到端的Agent应用 |

### 五、文件系统作为状态管理

> **"File systems are a natural and powerful way to represent an agent's state"**

Harrison Chase的状态管理洞察：

| 方案 | 复杂度 | 适用场景 |
|------|--------|---------|
| **内存** | 低 | 短期会话 |
| **数据库** | 中 | 结构化持久存储 |
| **文件系统** | 低-中 | Agent状态管理（推荐） |

**为什么文件系统是自然的选择**：
- 开发者熟悉文件操作
- 易于版本控制和调试
- 与代码仓库自然集成

---

## 金句集锦

| 主题 | 金句 |
|------|------|
| **Ambient Agents** | "Ambient agents operate on a fundamentally different paradigm" |
| **架构简化** | "复杂度应该放在Prompt里，而不是架构里" |
| **Deep Agents** | "Deep agents本质是: Prompt + Tools + Subagents" |
| **状态管理** | "File systems are a natural and powerful way to represent an agent's state" |
| **层级定位** | "LangGraph is the runtime. LangChain is the abstraction." |

---

## 概念贡献

### 创造的概念

| 概念 | 定义 | 影响 |
|------|------|------|
| **Ambient Agents** | 事件驱动、后台运行的Agent | 定义了Agent交互的新范式 |
| **Agent Inbox** | Agent与人类异步沟通的收件箱 | 改变了人机协作模式 |
| **Deep Agents** | Prompt + Tools + Subagents的架构 | 简化了Agent设计 |

### 与其他大神观点的交叉

| 对照 | Harrison Chase | 他人 | 关系 |
|------|---------------|------|------|
| **Agent范式** | Ambient Agents | 姚顺雨: 环境式Agent | 概念呼应 |
| **架构简化** | 复杂度放Prompt里 | Barry Zhang: Skills > Multi-Agent | 共识 |
| **上下文管理** | 文件系统管理状态 | Simon Willison: Context is King | 互补 |

---

## 内容来源

| 来源 | 类型 | 时间 | 链接 |
|------|------|------|------|
| Ambient Agents and the New Agent Inbox | 演讲/文章 | 2025.05 | [Sequoia AI Ascent](https://inferencebysequoia.substack.com/p/ambient-agents-and-the-new-agent) |
| Deep Agents: The Next Evolution | 演讲 | 2025.11 | [ODSC](https://opendatascience.com/harrison-chase-on-deep-agents-the-next-evolution-in-autonomous-ai/) |

---

## 实践应用

### Ambient Agent设计检查清单

**规划阶段**：
- [ ] 识别哪些任务适合后台运行
- [ ] 设计事件触发机制
- [ ] 定义人类介入点（需要审批的决策）

**实现阶段**：
- [ ] 使用LangGraph编排工作流
- [ ] 实现Agent Inbox界面
- [ ] 设置适当的超时和重试机制

**运营阶段**：
- [ ] 监控Agent运行状态
- [ ] 定期审查Inbox积压
- [ ] 迭代优化Prompt

### Deep Agent架构模板

```python
deep_agent = {
    "prompt": """
    你是一个[角色]，专注于[领域]。
    你的目标是[具体目标]。
    
    工作原则：
    1. [原则1]
    2. [原则2]
    
    遇到不确定时，询问人类。
    """,
    "tools": [
        "file_read",
        "file_write",
        "web_search",
        "code_execute"
    ],
    "subagents": [
        "research_agent",
        "writing_agent",
        "review_agent"
    ]
}
```

---

## 思想应用

### 对Agent开发者
1. **拥抱异步**：设计Agent时考虑异步执行模式
2. **Inbox优先**：为长任务建立人机协作的Inbox机制
3. **Prompt承担复杂度**：架构保持简单，让Prompt定义行为

### 对企业
1. **识别Ambient场景**：哪些业务流程适合后台Agent
2. **设计审批流程**：关键决策仍需人类把关
3. **投资LangGraph生态**：利用成熟的Agent运行时

---

## 2026.03 最新动态

### Agent协议生态演进

Harrison Chase的LangChain/LangGraph生态在2026年3月面临新的协议格局：

| 协议 | 发起方 | 定位 | 状态 |
|------|--------|------|------|
| **MCP** | Anthropic → Linux Foundation | Agent与工具连接 | 10,000+ Server |
| **A2A** | Google | Agent间互操作 | 生态扩展中 |
| **UCP** | Google | Agent商务交易 | 新发布 |
| **IETF Agent Gateway** | IETF | 国际标准化 | 草案阶段 |

### Skills范式对LangGraph的影响

Barry Zhang的Skills范式和Harrison Chase的Agent框架正在融合：
- LangGraph提供Agent运行时和编排能力
- Skills提供可复用的能力单元
- SKILL.md格式可与LangGraph的Tool定义互补

### Ambient Agents概念的市场验证

- OpenAI的GPT-5.4 computer-use (OSWorld 75%超人类)验证了Harrison对Ambient Agent的预判
- Google Workspace Gemini深度整合是Ambient Agent的企业级实现

---

*创建时间: 2026-03-04*
*最后更新: 2026-03-13*
*整理者: 林克 AI 助手*
