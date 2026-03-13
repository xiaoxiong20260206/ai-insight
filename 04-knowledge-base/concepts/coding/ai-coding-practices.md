# AI编程实践知识库

> **知识类型**: 最佳实践
> **来源**: Andrej Karpathy、Simon Willison、Addy Osmani 深度分享
> **更新时间**: 2026-03-13
> **版本**: v1.1 - 新增Skills生态、Agent安全测试、GWS MCP

---

## 核心概念

### Vibe Coding vs Vibe Engineering

| 概念 | 定义者 | 特点 |
|------|-------|------|
| **Vibe Coding** | Andrej Karpathy | 快速、松散、不看代码，适合原型和学习 |
| **Vibe Engineering** | Simon Willison | 严谨、负责、全面监督，适合生产环境 |
| **Agentic Engineering** | Simon Willison (2026.02更新) | AI Agent辅助的严谨工程实践 |

**关键区分**：
> "Vibe Engineering: 资深工程师用LLM加速工作，同时保持对软件的骄傲和负责" — Simon Willison

### Software 3.0

Andrej Karpathy 提出的软件演进框架：

| 版本 | 描述 |
|------|------|
| **Software 1.0** | 传统代码，人工编写的显式逻辑 |
| **Software 2.0** | 神经网络权重，通过数据训练而非编程 |
| **Software 3.0** | LLM驱动的软件，用自然语言"编程" |

> "The hottest new programming language is English" — Andrej Karpathy

---

## 核心原则

### 原则一：上下文为王 (Context is King)

> "Most of the craft of getting good results out of an LLM comes down to managing its context" — Simon Willison

**上下文管理策略**：

| 策略 | 工具/方法 | 作用 |
|------|---------|------|
| **代码库压缩** | gitingest, repo2txt | 将整个代码库压缩成可摄取的格式 |
| **规则文件** | CLAUDE.md, GEMINI.md | 定义项目规范、编码标准 |
| **文档喂给模型** | 手动粘贴或RAG | 提供官方文档作为上下文 |
| **错误信息** | 完整堆栈跟踪 | 帮助模型定位问题 |

### 原则二：测试驱动的AI开发

> "If your project has a robust test suite, agentic coding tools can FLY with it" — Simon Willison

**TDD + AI Agent 循环**：
```
编写测试 → AI生成代码 → 运行测试 → AI修复失败 → 循环直到通过
```

**测试在AI时代的新价值**：
- 测试不再只是质量保障，而是**Agent的训练数据**
- 没有测试套件的项目无法发挥AI编程的全部潜力
- 测试定义了"正确"的边界，AI负责达到这个边界

### 原则三：人类负责，AI执行

> "AI will happily produce plausible-looking code, but YOU are responsible for quality" — Addy Osmani

**责任分配**：

| 人类负责 | AI执行 |
|---------|-------|
| 架构决策 | 代码生成 |
| 安全审查 | 初稿编写 |
| 质量把关 | 批量修改 |
| 业务判断 | 模板填充 |
| 最终验收 | 测试覆盖 |

---

## 工作流最佳实践

### Simon Willison 的工作流

1. **小步快跑**：每次对话专注一个具体任务
2. **保持上下文新鲜**：避免在过长对话中迷失
3. **利用测试**：让AI生成测试，然后生成代码
4. **版本控制**：频繁提交，每个AI协助的改动单独提交
5. **审查输出**：永远不要盲目接受生成的代码

### Addy Osmani 的工作流

> "我的方法是'AI增强软件工程'而非'AI自动化软件工程'"

**核心步骤**：
1. **先想清楚**：在使用AI之前，先有清晰的设计
2. **提供充分上下文**：代码、文档、约束条件
3. **分步执行**：把大任务拆成小任务
4. **迭代精炼**：第一次输出很少完美，持续调整
5. **测试验证**：每个改动都要测试

---

## AI Coding工具选型

### 工具分类

| 类型 | 代表产品 | 适用场景 |
|------|---------|---------|
| **IDE集成** | Cursor, GitHub Copilot, Codeium | 日常编码，实时补全 |
| **对话式** | ChatGPT, Claude, Gemini | 设计讨论，问题解答 |
| **Agent式** | Claude Code, Devin, Codex CLI | 复杂任务，多文件修改 |
| **CLI工具** | aider, OpenAI Codex CLI | 终端爱好者，脚本集成 |

### 选型建议

> "Claude Code在更新我团队的某个历史遗留配置文件时，是唯一成功的AI Agent。Cursor和Codex在这个任务上都失败了。" — Steve Krouse

**核心洞察**：不同AI Coding工具在特定场景下表现差异显著，工具选型需要根据实际代码库特点测试验证。

---

## 常见陷阱

### 陷阱一：过度信任

**问题**：接受AI生成的代码而不审查
**解决**：建立代码审查习惯，AI代码和人写代码同等对待

### 陷阱二：上下文污染

**问题**：在过长对话中，早期信息被"遗忘"
**解决**：开始新对话，或显式重申关键约束

### 陷阱三：复杂度转移

**问题**：以为AI消除了复杂度，实际只是转移了
**解决**：认识到复杂度从"写代码"转移到了"管理AI"

> "使用LLM编程不是按按钮的魔法体验——它是'困难且反直觉的'" — Addy Osmani

### 陷阱四：工具隐藏上下文

**问题**：某些工具隐藏了发送给模型的内容
**解决**：选择透明的工具，或检查发送的实际内容

> "LLM tools that obscure context from me are LESS effective" — Simon Willison

---

## 效率提升策略

### 1. 使用规则文件

创建项目级的规则文件（如 `CLAUDE.md`），包含：
- 项目结构说明
- 编码规范
- 禁止的模式
- 偏好的实现方式

### 2. 构建个人Prompt库

收集并维护常用的Prompt模式：
- 代码审查Prompt
- 重构建议Prompt
- 测试生成Prompt
- 文档生成Prompt

### 3. 利用文件系统

> "File systems are a natural and powerful way to represent an agent's state" — Harrison Chase

让Agent通过文件系统管理状态，而非复杂的内存机制。

---

## 参考资料

- [Software 3.0 - Andrej Karpathy](https://www.latent.space/p/s3)
- [Vibe Engineering - Simon Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/)
- [Here's How I Use LLMs to Help Me Write Code - Simon Willison](https://simonwillison.net/2025/Mar/11/using-llms-for-code/)
- [My LLM Coding Workflow Going Into 2026 - Addy Osmani](https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026-52fe1681325e)
