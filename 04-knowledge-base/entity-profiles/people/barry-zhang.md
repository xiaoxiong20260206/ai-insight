# Barry Zhang (Anthropic) 思想体系与内容总结

> **知识类型**: 人物画像 + 概念体系
> **来源**: Barry Zhang 博客、演讲、采访的完整整理
> **更新时间**: 2026-03-04
> **版本**: v2.0 - 完整版

---

> **作者**: Barry Zhang (张宇杰)
> **职位**: Anthropic Applied AI 团队成员 (Head of Applied AI, Digital Natives & Strategics)
> **背景**: 前 Meta AI 产品工程师，前 Shopify、Box 工程师
> **社交**: [Twitter/X](https://x.com/barry_zyj) | [LinkedIn](https://www.linkedin.com/in/barry-z)

---

## 📋 内容来源清单

| 内容类型 | 标题 | 平台 | 时间 | 链接 |
|---------|------|------|------|------|
| 📝 博客文章 | Building Effective AI Agents | Anthropic 官方 | 2024.12.19 | https://www.anthropic.com/research/building-effective-agents |
| 🎤 演讲 | How We Build Effective Agents | AI Engineer Summit 2025 | 2025.02 | https://www.youtube.com/watch?v=D7_ipDqhtwk |
| 🎤 演讲 | Don't Build Agents, Build Skills Instead | AI Engineer Code Summit | 2025.11 | https://www.youtube.com/watch?v=CEvIs9y1uog |
| 🎥 视频 | Tips for building AI agents | Anthropic 官方 | 2025.02 | https://www.youtube.com/watch?v=LP5OCa20Zpg |
| 📰 采访 | Anthropic Researchers Say More AI Agents Isn't the Answer | Business Insider | 2025.12.08 | https://www.businessinsider.com/anthropic-researchers-ai-agent-skills-barry-zhang-mahesh-murag-2025-12 |

---

## 🧠 核心思想体系

### 一、Agent 定义与分类框架

Barry Zhang 与 Erik Schluntz 共同提出了业界最清晰的 Agent 定义框架，解决了"Agent"一词在行业中被滥用的问题：

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

**关键概念：Augmented LLM (增强型LLM)**

这是构建所有 agentic systems 的基础构建块：

| 增强能力 | 描述 | 实现方式 |
|---------|------|---------|
| **Retrieval (检索)** | 生成搜索查询，获取外部知识 | RAG、向量数据库 |
| **Tools (工具)** | 选择并调用合适的工具 | Function Calling |
| **Memory (记忆)** | 决定保留哪些信息 | 上下文管理、长期记忆 |

> **关键洞察**: "Our current models can actively use these capabilities—generating their own search queries, selecting appropriate tools, and determining what information to retain."

这个概念填补了"简单 LLM 调用"和"完整 Agent"之间的空白，是 Barry Zhang 框架的核心基础。

---

### 二、Agent 设计三大核心原则

#### 原则一：Don't Build Agents for Everything (不要为所有事情构建 Agent)

这是 Barry Zhang 最核心的观点之一。他强调在构建 LLM 应用时，应该**找到最简单的解决方案**，只有在必要时才增加复杂度。

**决策检查清单（详细版）：**

| 维度 | 适合 Agent ✅ | 适合 Workflow/简单调用 ⚡ |
|------|-------------|------------------------|
| **任务复杂度** | 问题空间模糊，难以预测所需步骤数 | 可以轻松画出完整决策树 |
| **任务价值** | 高价值产出，不限 token 预算 | 低预算（如每任务 $0.10）|
| **关键能力** | 核心能力已验证，无明显瓶颈 | 存在基础能力短板 |
| **错误成本** | 低风险、错误易发现和恢复 | 高风险、错误难以检测 |
| **可验证性** | 结果可通过测试或反馈验证 | 结果难以客观评估 |

**经典引用：**
> "If you can map out the entire decision tree pretty easily, just build that explicitly and then optimize every node."
> 
> "Agentic systems often trade latency and cost for better task performance, and you should consider when this tradeoff makes sense."

**反模式警示：**
- 不要因为"Agent"是热词就使用它
- 很多应用优化单次 LLM 调用 + 检索 + 上下文示例就足够了
- 框架可能诱导你添加不必要的复杂度

---

#### 原则二：Keep It Simple (保持简单)

这是 Barry Zhang 反复强调的原则。Agent 的本质定义惊人地简单：

```
Agent = Model + Tools + Loop (环境反馈)
```

**三大核心组件（详细解析）：**

| 组件 | 作用 | 设计要点 |
|------|------|---------|
| **Environment (环境)** | Agent 运行的系统和上下文 | 定义清晰的边界和能力范围 |
| **Tools (工具)** | Agent 采取行动和获取反馈的接口 | 文档清晰、返回值明确 |
| **System Prompt (系统提示)** | 定义目标、约束和理想行为 | 简洁但完整，包含示例 |

**关键洞察：**
> "We have learned the hard way to keep this simple, because any complexity up front is really going to kill iteration speed."

> "Agents can handle sophisticated tasks, but their implementation is often straightforward. They are typically just LLMs using tools based on environmental feedback in a loop."

**框架使用建议：**

| 场景 | 建议 |
|------|------|
| 快速原型 | 可以使用框架（如 Claude Agent SDK, Strands SDK）|
| 生产部署 | 减少抽象层，用基础组件构建 |
| 调试问题 | 必须理解框架底层代码 |

> "We suggest that developers start by using LLM APIs directly: many patterns can be implemented in a few lines of code."

---

#### 原则三：Think Like Your Agents (像你的 Agent 一样思考)

这是 Barry Zhang 最具洞察力的建议。

**核心方法：将自己置于 Agent 的上下文窗口中**

Agent 在每一步推理时，所知道的关于世界的一切都只有 **10-20K tokens**。你需要体验这种受限的视角。

**Computer Use Agent 视角实验（具体步骤）：**

想象你在使用电脑，但：
1. 你**只能看到静态截图**（没有动画、没有实时反馈）
2. 每次点击后**闭眼 3-5 秒**（等待下一帧）
3. 你**不知道动作是否成功**（没有即时确认）
4. 你**不知道当前 URL、窗口状态**

这就是 Agent 看到的世界！

**调试技巧（实践指南）：**

| 方法 | 具体操作 |
|------|---------|
| **让 Claude 检查 System Prompt** | 问："这个 prompt 有歧义吗？如果是你会怎么理解？" |
| **让 Claude 评估工具描述** | 问："这个工具描述清楚吗？你知道什么时候该用吗？" |
| **分析 Agent 轨迹** | 把 Agent 的决策历史喂给 Claude，问："你为什么在第3步选择了这个工具？" |
| **直接询问模型** | 问："根据当前上下文，你觉得下一步应该做什么？为什么？" |

---

### 三、五大工作流模式 (Workflow Patterns) 详解

Barry Zhang 总结了五种在生产环境中常见的 agentic 模式：

#### 1. Prompt Chaining (提示链)

```
输入 → LLM₁ → [检查] → LLM₂ → [检查] → LLM₃ → 输出
```

**核心思想**：将任务分解为顺序步骤，每个 LLM 处理前一个的输出。

| 特点 | 说明 |
|------|------|
| **优势** | 用延迟换取更高准确率，每步更简单 |
| **适用** | 任务可干净地分解为固定子任务 |
| **示例** | 1. 生成营销文案 → 翻译成中文 |
|         | 2. 写文档大纲 → 检查大纲 → 基于大纲写全文 |

#### 2. Routing (路由)

```
输入 → 分类器 → ┬→ 处理路径 A
               ├→ 处理路径 B
               └→ 处理路径 C
```

**核心思想**：分类输入并路由到专门处理流程。

| 特点 | 说明 |
|------|------|
| **优势** | 关注点分离，每条路径可深度优化 |
| **适用** | 有明确分类且各类需要不同处理 |
| **示例** | 1. 客服问题分流（常见问题 → 退款 → 技术支持）|
|         | 2. 简单问题用 Haiku，复杂问题用 Sonnet |

#### 3. Parallelization (并行化)

```
        ┌→ LLM₁ →┐
输入 → ─├→ LLM₂ →├→ 聚合 → 输出
        └→ LLM₃ →┘
```

**两种变体：**

| 变体 | 描述 | 示例 |
|------|------|------|
| **Sectioning** | 拆分为独立子任务并行执行 | 多页面 OCR、guardrails 与主响应分离 |
| **Voting** | 同一任务多次执行取共识 | 代码漏洞多角度审查 |

#### 4. Orchestrator-Workers (协调者-工作者)

```
任务 → Orchestrator → ┬→ Worker₁ →┐
                      ├→ Worker₂ →├→ 合成 → 输出
                      └→ Worker₃ →┘
```

**核心思想**：中央 LLM 动态分解任务，委派给工作 LLM，综合结果。

| 特点 | 说明 |
|------|------|
| **优势** | 灵活性高，子任务由输入决定 |
| **区别于并行化** | 子任务不是预定义的 |
| **示例** | 1. 代码 Agent 修改多个文件 |
|         | 2. 多源搜索并综合信息 |

#### 5. Evaluator-Optimizer (评估-优化)

```
任务 → 生成器 LLM → 评估器 LLM → ┬→ 通过 → 输出
                    ↑           └→ 不通过 → 反馈
                    └────────────────────────┘
```

**核心思想**：一个 LLM 生成，另一个 LLM 评估并提供反馈，循环优化。

| 特点 | 说明 |
|------|------|
| **优势** | 迭代精炼，类似人类写作过程 |
| **适用条件** | 1. 有明确评估标准 2. 人类反馈能提升质量 |
| **示例** | 1. 文学翻译捕捉细微差别 |
|         | 2. 复杂搜索任务多轮深入 |

---

### 四、为什么 Coding 是 Agent 的最佳用例

Barry Zhang 详细解释了为什么编码是 Agent 应用的"甜点"：

| 维度 | 分析 |
|------|------|
| **复杂性** ✅ | 从设计文档到 PR，过程高度模糊和复杂，难以预定义所有步骤 |
| **价值** ✅ | 优质代码价值极高，值得消耗大量 tokens |
| **能力验证** ✅ | Claude 等模型已证明编码能力出色（SWE-bench 表现）|
| **可验证性** ✅ | 通过单元测试、CI/CD 自动验证结果正确性 |
| **反馈循环** ✅ | 测试结果提供明确的环境反馈 |

**Anthropic 实践案例：**
- **SWE-bench Agent**：根据任务描述编辑多个文件解决 GitHub issue
- **Computer Use Agent**：Claude 使用电脑完成各种任务

> "In our own implementation, agents can now solve real GitHub issues in the SWE-bench Verified benchmark based on the pull request description alone."

---

### 五、Agent-Computer Interface (ACI) 设计

类比人机交互 (HCI)，Barry 提出了 **Agent-Computer Interface (ACI)** 概念——这是被严重低估但至关重要的领域。

**核心洞察：**
> "One rule of thumb is to think about how much effort goes into human-computer interfaces (HCI), and plan to invest just as much effort in creating good agent-computer interfaces (ACI)."

**工具格式设计原则：**

| 原则 | 说明 | 反例 |
|------|------|------|
| **给模型思考空间** | 让模型有足够 tokens 计划后再行动 | 要求模型直接输出 diff（需先知道行数变化）|
| **贴近自然文本** | 格式应接近模型在训练数据中见过的 | 高度结构化的自定义 DSL |
| **避免格式开销** | 无需精确计数或转义 | JSON 中的代码需要转义换行和引号 |

**工具定义最佳实践：**

| 做法 | 具体建议 |
|------|---------|
| **站在模型角度** | 问自己："仅看描述和参数，工具用法明显吗？" |
| **写优质文档** | 像给初级开发者写 docstring |
| **包含示例** | 提供使用示例、边界情况、输入格式要求 |
| **明确边界** | 区分相似工具的使用场景 |
| **反复测试** | 在 Workbench 运行多种输入看模型犯什么错 |
| **Poka-yoke 设计** | 改变参数设计使错误难以发生 |

**实践案例（SWE-bench）：**
> "While building our agent for SWE-bench, we actually spent more time optimizing our tools than the overall prompt."
> 
> "We found that the model would make mistakes with tools using relative filepaths after the agent had moved out of the root directory. To fix this, we changed the tool to always require absolute filepaths—and we found that the model used this method flawlessly."

---

### 六、Agent 实践应用场景

Barry Zhang 总结了两个特别有价值的 Agent 应用领域：

#### A. 客户服务 (Customer Support)

| 特点 | 为何适合 Agent |
|------|---------------|
| **自然对话流** | 支持交互天然是对话形式 |
| **工具集成** | 可拉取客户数据、订单历史、知识库 |
| **可编程操作** | 退款、更新工单等可自动化 |
| **明确成功指标** | 用户定义的问题解决率 |

> "Several companies have demonstrated the viability of this approach through usage-based pricing models that charge only for successful resolutions."

#### B. 编码 Agent (Coding Agents)

| 特点 | 为何适合 Agent |
|------|---------------|
| **可验证性** | 代码方案可通过自动测试验证 |
| **迭代反馈** | Agent 可利用测试结果迭代优化 |
| **结构化问题** | 问题空间虽复杂但定义明确 |
| **客观评估** | 输出质量可客观衡量 |

---

### 七、Agent 未来三大开放问题

Barry Zhang 在演讲中提出了三个尚待解决的关键问题：

#### 1. 预算感知 (Budget-Aware Agents)

| 维度 | 挑战 |
|------|------|
| **问题** | Agent 的成本和延迟难以预测和控制 |
| **复杂性** | 如何定义"预算"？时间？金钱？tokens？ |
| **权衡** | 如何在质量和成本之间动态平衡？ |
| **方向** | 让 Agent 自己感知和管理预算约束 |

#### 2. 自进化工具 (Self-Evolving Tools)

| 维度 | 展望 |
|------|------|
| **概念** | Meta-tool：让 Agent 设计和改进自己的工具 |
| **意义** | 使 Agent 更加通用化，减少人工工具设计 |
| **挑战** | 如何确保自创工具的安全性和有效性？ |

#### 3. 多 Agent 协作 (Multi-Agent Collaboration)

| 维度 | 分析 |
|------|------|
| **预测** | 2025 年内将大量进入生产环境 |
| **优势** | 并行化、关注点分离、保护主 Agent 上下文 |
| **挑战** | Agent 间如何通信？如何从同步转向异步？ |
| **关键问题** | 角色识别、任务分配、结果合成 |

---

### 八、"Don't Build Agents, Build Skills Instead" 新范式

这是 Barry Zhang 在 2025 年 11 月 AI Engineer Code Summit 上提出的最新思想演进，与 Mahesh Murag 联合发表。

#### 核心思想转变

```
旧范式: 为每个领域/用例构建不同的 Agent
         ↓
新范式: 单一通用 Agent + 可扩展的 Skills 库
```

**关键引用：**
> "We used to think agents in different domains will look very different. The agent underneath is actually more universal than we thought."

> "The industry doesn't need a flurry of agent-building. Instead, 'skills' can equip a general agent with domain expertise and reusable workflows."

#### Skills 的定义

> "Skills are organized collections of files that package composable procedural knowledge for agents."

**Skills 的本质：**
- 一个 Markdown 文件告诉模型如何做某事
- 可选地附带额外文档和预写脚本
- 模型可以运行这些脚本来完成任务

**技术实现（来自 Simon Willison 分析）：**
```
Skills = Markdown + YAML 元数据 + 可选脚本
```

会话开始时，Claude 的各种 harness 可以：
1. 扫描所有可用 skill 文件
2. 从 YAML frontmatter 读取简短说明
3. 每个 skill 只占用几十个 tokens
4. 仅在用户请求相关任务时加载完整内容

#### Skills 的优势

| 优势 | 说明 |
|------|------|
| **可复用性** | 技能可以跨 Agent、跨项目共享 |
| **网络效应** | 技能越多，Agent 能力增长越快 |
| **专业化** | 每个 Skill 可以深度优化 |
| **低门槛** | 非技术人员也能创建 skill |
| **Token 高效** | 按需加载，节省上下文 |

#### 实际采用情况

根据 Business Insider 报道：
- 发布 5 周内用户创建了**数千个 skills**
- 会计、法律、招聘等**非技术领域**都有人创建 skills
- **Fortune 100 公司**正在使用 skills "教 Agent 组织最佳实践"
- 大公司把 skills 当作 **AI 的内部 playbook**

#### Skills vs MCP 对比

| 维度 | Skills | MCP |
|------|--------|-----|
| **复杂度** | 极简（Markdown + 脚本）| 完整协议规范 |
| **Token 消耗** | 按需加载，高效 | GitHub MCP 消耗数万 tokens |
| **依赖** | 需要代码执行环境 | 可独立运行 |
| **实现门槛** | 写 Markdown 即可 | 需要实现服务器 |
| **灵活性** | 脚本可做任何事 | 受限于协议能力 |

**Barry Zhang 的观点：**
> "Skills actually came out of a prototype I built demonstrating that Claude Code is a general-purpose agent :-)"
> 
> "It was a natural conclusion once we realized that bash + filesystem were all we needed."

#### 当前 Agent 的问题

> "Despite their intelligence, today's agents 'lack expertise' and often miss important context in real-world use cases."

Skills 正是为了解决这个问题——给 Agent 填补领域知识和可复用工作流的空白。

#### 未来展望

> "Agents writing skills for other agents"

这预示着一个自我进化的生态系统：
1. Agent 使用 skills 完成任务
2. Agent 发现现有 skills 不足
3. Agent 创建新的 skills
4. 新 skills 被其他 Agent 使用
5. 整体能力螺旋上升

---

## 📊 思想演进脉络

```
2024.12.19  "Building Effective Agents" 博客发布 (与 Erik Schluntz 合著)
            ├── 定义 Agentic Systems、Workflows vs Agents
            ├── 提出 Augmented LLM 概念
            ├── 总结五大工作流模式
            ├── 强调简单优先原则
            └── 引入 Agent-Computer Interface (ACI) 概念

2025.02     AI Engineer Summit 演讲 "How We Build Effective Agents"
            ├── 三大核心原则深化（不要为所有事构建Agent、保持简单、像Agent一样思考）
            ├── Agent 设计检查清单（复杂度、价值、能力、错误成本）
            ├── Coding Agent 案例详解
            ├── 调试方法论
            └── 未来三大开放问题（预算感知、自进化工具、多Agent协作）

2025.11     AI Engineer Code Summit 演讲 "Don't Build Agents, Build Skills Instead"
            ├── 从"多Agent"到"单Agent+多Skills"的范式转变
            ├── Skills 的定义和技术实现
            ├── Skills 的网络效应观察
            ├── Claude Code 作为通用 Agent 的定位
            └── "Agent 为 Agent 写 Skills" 的未来愿景
```

---

## 💡 实践启示

### 对开发者的建议

#### 起步阶段

| 建议 | 具体做法 |
|------|---------|
| **从简单开始** | 先用 LLM API 直接调用，验证单点能力 |
| **避免过早框架** | 框架可以快速启动，但先理解底层 |
| **小步迭代** | 先让行为正确，优化放到后期 |

#### 设计阶段

| 建议 | 具体做法 |
|------|---------|
| **评估是否需要 Agent** | 使用决策检查清单判断 |
| **选择合适模式** | 从五大工作流模式中选择 |
| **投资工具设计** | 在工具上花的时间可能超过 prompt |

#### 调试阶段

| 建议 | 具体做法 |
|------|---------|
| **站在 Agent 角度** | 体验受限上下文的视角 |
| **让模型自检** | 让 Claude 评估 prompt 和工具描述 |
| **分析轨迹** | 把 Agent 决策历史喂给模型分析 |

#### 测试阶段

| 建议 | 具体做法 |
|------|---------|
| **沙盒测试** | 在隔离环境充分测试 |
| **设置 Guardrails** | 定义明确的边界和停止条件 |
| **渐进式权限** | 从只读开始，逐步增加自主权 |

### 对产品的建议

| 维度 | 建议 |
|------|------|
| **用例选择** | 高价值、高复杂度、错误可发现可恢复 |
| **信任建立** | 展示 Agent 规划步骤，保持透明 |
| **能力边界** | 明确告诉用户 Agent 能做什么、不能做什么 |
| **反馈循环** | 让用户能够纠正 Agent 并提供反馈 |

### 对组织的建议

| 维度 | 建议 |
|------|------|
| **Skills 策略** | 开始创建组织专属 skills 库 |
| **知识沉淀** | 将最佳实践转化为 skills |
| **共享机制** | 建立 skills 共享和评价体系 |

---

## 🔗 参考资源

### 官方资源
- [Building Effective Agents - Anthropic Blog](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic Cookbook - Agent Patterns](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Agent Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Claude Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)

### 视频演讲
- [How We Build Effective Agents - YouTube](https://www.youtube.com/watch?v=D7_ipDqhtwk) (404K+ views)
- [Don't Build Agents, Build Skills Instead - YouTube](https://www.youtube.com/watch?v=CEvIs9y1uog) (742K+ views)
- [Tips for building AI agents - Anthropic](https://www.youtube.com/watch?v=LP5OCa20Zpg)

### 深度解读
- [Simon Willison - Building Effective Agents](https://simonwillison.net/2024/Dec/20/building-effective-agents/)
- [Simon Willison - Claude Skills are awesome](https://simonw.substack.com/p/claude-skills-are-awesome-maybe-a)
- [Business Insider - Anthropic Researchers Say More AI Agents Isn't the Answer](https://www.businessinsider.com/anthropic-researchers-ai-agent-skills-barry-zhang-mahesh-murag-2025-12)

### 社交媒体
- [Barry Zhang Twitter/X](https://x.com/barry_zyj)
- [Barry Zhang LinkedIn](https://www.linkedin.com/in/barry-z)

---

## 📈 影响力数据

| 指标 | 数据 |
|------|------|
| "How We Build Effective Agents" 演讲观看量 | 404K+ |
| "Don't Build Agents, Build Skills" 演讲观看量 | 742K+ |
| 入选"2025年度50个最受关注软件工程演讲" | ✅ |
| Skills 发布后5周内创建数量 | 数千个 |
| 使用 Skills 的 Fortune 100 公司 | 多家 |

---

*原始文档生成时间: 2026-02-28*
*知识库沉淀时间: 2026-03-04*
*整理者: 林克 AI 助手*
*版本: v2.0 - 完整版*
