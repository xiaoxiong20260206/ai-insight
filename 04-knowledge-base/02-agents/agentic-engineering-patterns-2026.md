# Agentic Engineering Patterns - 2026年编程范式

> **知识类型**: Agent工程实践
> **来源**: Simon Willison's Agentic Engineering Patterns Guide (2026.02)
> **更新时间**: 2026-03-06
> **状态**: 核心实践文档

---

## 概述

Simon Willison 在2026年2月正式启动了 **Agentic Engineering Patterns** 项目，旨在系统化收集和记录这个新时代编程代理开发的最佳实践。

**关键区分**：
- **Vibe Coding**: 完全放弃关注代码，让AI自主编写，适合非程序员或快速原型
- **Agentic Engineering**: 专业软件工程师使用编程代理，通过放大现有专业知识来提升效率

> "I'm using **Agentic Engineering** to refer to building software using coding agents - tools like Claude Code and OpenAI Codex, where the defining feature is that they can both generate and _execute_ code - allowing them to test that code and iterate on it independently of turn-by-turn guidance from their human supervisor."

---

## 核心模式

### 模式一：代码写作成本已经很低 (Writing Code is Cheap Now)

> "The biggest challenge in adopting agentic engineering practices is getting comfortable with the consequences of the fact that writing code is cheap now."

**核心挑战**：
- 代码一直是昂贵的资源
- 我们的工程习惯（宏观和微观层面）都建立在这个核心约束之上
- 现在产出初始可工作代码的成本已降至接近零

**影响**：
- 宏观层面：需要重新评估功能开发的投资回报
- 微观层面：重新思考代码审查、测试策略
- 团队层面：调整估算和规划方式

### 模式二：红绿TDD (Red/Green TDD)

> "Use red/green TDD" is a pleasingly succinct way to get better results out of a coding agent.

**核心实践**：
1. 先写测试，确认测试失败（红色）
2. 让Agent编写实现代码
3. 运行测试直到通过（绿色）
4. Agent可以独立迭代修复问题

**为什么有效**：
- 测试提供了完美的反馈循环
- Agent可以自主验证和迭代
- 减少人工审查的负担

### 模式三：线性代码走读 (Linear Walkthroughs)

> "Sometimes it's useful to have a coding agent give you a structured walkthrough of a codebase."

**应用场景**：
- 理解现有代码库
- 理解自己遗忘的代码
- 理解完全由vibe coding产生的代码

**Prompt模板**：
```
请对这个代码库进行线性走读，解释：
1. 项目的整体结构
2. 关键组件及其职责
3. 数据流和交互方式
```

### 模式四：囤积技能清单 (Hoard Things You Know How to Do)

> "A big part of the skill in building software is understanding what's possible and what isn't."

**核心思想**：
- 持续积累"知道如何做"的技能清单
- 这些知识在使用Agent时特别有价值
- Agent可以执行你知道可能但不知道具体细节的任务

**示例问题**：
- 网页能否在纯JavaScript中运行OCR？
- iPhone应用能否在不运行时配对蓝牙设备？
- Python能否处理100GB JSON文件而不全部加载到内存？

---

## 新兴概念

### Claw（爪子）

Andrej Karpathy 提出的新术语，指代OpenClaw类的Agent系统：
- 运行在个人硬件上的AI Agent
- 通过消息协议通信
- 既能响应直接指令，也能调度任务

> "Claw" is becoming a term of art for the entire category of OpenClaw-like agent systems - AI agents that generally run on personal hardware, communicate via messaging protocols and can both act on direct instructions and schedule tasks.

**特点**：
- 个人硬件上运行
- 通过消息协议通信
- 支持直接指令和计划任务
- 甚至有了专属emoji：🦞

### Cognitive Debt（认知债务）

> "When we lose track of how code written by our agents works we take on cognitive debt."

**定义**：当我们失去对Agent编写的代码如何工作的跟踪时，就积累了认知债务。

**影响**：
- 如果应用核心变成黑盒，就无法自信地推理它
- 规划新功能变得困难
- 最终像技术债务一样拖慢进度

---

## November 2025 转折点

Simon Willison 和多位工程师都观察到2025年11月是一个关键拐点：

### Paul Ford (NYT文章)

> "November was, for me and many others in tech, a great surprise. Before, A.I. coding tools were often useful, but halting and clumsy. Now, the bot can run for a full hour and make whole, designed websites and apps that may be flawed, but credible."

**成本对比**：
- 重建个人网站：以前估价$25,000，现在几小时完成
- 数据集转换：以前估价$350,000（含PM、设计师、2名工程师、4-6个月），现在周末搞定
- 代价：Claude $200/月订阅

### Andrej Karpathy

> "It is hard to communicate how much programming has changed due to AI in the last 2 months: not gradually and over time in the 'progress as usual' way, but specifically this last December."

**关键观察**：
- 编程代理在12月前基本不工作
- 12月后基本可以工作
- 模型质量显著提高
- 长期连贯性和韧性大幅提升

### Donald Knuth

> "Shock! Shock! I learned yesterday that an open problem I'd been working on for several weeks had just been solved by Claude Opus 4.6 - Anthropic's hybrid reasoning model."

计算机科学泰斗 Donald Knuth 承认需要重新评估对生成式AI的看法。

---

## 工具生态更新 (2026.03)

### 模型更新
| 模型 | 发布时间 | 特点 |
|-----|---------|------|
| **GPT-5.4** | 2026.03 | 超越Codex编程能力，强化电子表格/文档 |
| **Gemini 3.1 Pro** | 2026.02 | 思考模式，SVG动画能力 |
| **Gemini 3.1 Flash-Lite** | 2026.03 | 1/8价格，四级思考 |
| **Claude Opus 4.6** | 2025.11 | 混合推理，November拐点标志 |
| **Codex 5.3** | 2025.12 | 1200 tokens/s |
| **Qwen 3.5** | 2026.02 | 开放权重新标杆 |

### 工具更新
- **Claude Code Remote Control**: 手机遥控桌面Agent
- **Cowork Scheduled Tasks**: 定时任务调度
- **ggml.ai → Hugging Face**: 本地模型生态整合

---

## 技术细节

### Prompt Caching

> "Long running agentic products like Claude Code are made feasible by prompt caching which allows us to reuse computation from previous roundtrips and significantly decrease latency and cost."

Claude Code 团队围绕prompt缓存构建整个架构，高缓存命中率直接影响成本和速率限制。

### Present App案例

Simon用Swift vibe coding了一个演示应用，展示了：
- 快速构建（45分钟）
- 跨语言能力（不懂Swift也能构建）
- 实用功能（URL序列演示、远程控制）

> "I didn't have to open Xcode even once!"

---

## 相关链接

- [Agentic Engineering Patterns Guide](https://simonwillison.net/guides/agentic-engineering-patterns/)
- [Simon Willison's Newsletter](https://simonw.substack.com/)
- [November 2025 Inflection Point](https://simonwillison.net/2026/Jan/4/inflection/)

---

*创建时间: 2026-03-06*
*来源: 系统性主动学习*
