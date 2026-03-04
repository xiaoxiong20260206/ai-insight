# AI编程最佳实践指南

> **知识类型**: 最佳实践 + 方法论
> **来源**: Simon Willison、Addy Osmani、Andrej Karpathy等业界领袖的工作流分享
> **更新时间**: 2026-03-04
> **版本**: v2.0 - 完整版

---

## 一、核心理念：从Vibe Coding到Agentic Engineering

### 1.1 AI编程的两种模式

| 模式 | 定义者 | 特征 | 适用场景 |
|------|-------|------|---------|
| **Vibe Coding** | Andrej Karpathy | 快速、松散、不看代码、"见招拆招" | 原型开发、学习探索、一次性脚本 |
| **Vibe Engineering** | Simon Willison | 严谨、负责、全面监督、保持工程师骄傲 | 生产环境、团队协作、长期维护 |

### 1.2 Agentic Engineering定义（2026.02）

> **Simon Willison更新**："Agentic Engineering"将成为2026年的主流术语

Agentic Engineering = Vibe Engineering + Agent协作能力

核心特征：
- 资深工程师用LLM加速工作
- 保持对软件的骄傲和负责任态度
- 利用Agent处理重复性工作，但人类保持全面监督
- 充分利用测试套件验证AI生成的代码

### 1.3 核心金句

| 来源 | 核心表述 |
|------|---------|
| **Andrej Karpathy** | "最热门的新编程语言是英语" (Vibe Coding的定义者) |
| **Simon Willison** | "LLM工具是困难且反直觉的。它需要大量努力来弄清楚使用它们的技巧" |
| **Addy Osmani** | "使用LLM编程不是按按钮的魔法体验——它是'困难且反直觉的'" |
| **Addy Osmani** | "我的方法是'AI增强软件工程'而非'AI自动化软件工程'" |

---

## 二、Simon Willison的AI编程工作流

### 2.1 核心原则

> "Most of the craft of getting good results out of an LLM comes down to managing its context"

**上下文管理是获得良好结果的核心技艺。**

### 2.2 实践方法

#### 方法一：测试驱动的AI编程

> "If your project has a robust test suite, agentic coding tools can FLY with it"

**工作流**：
```
1. 编写测试用例（人类定义期望行为）
2. 让AI生成实现代码
3. 运行测试验证
4. AI根据测试结果修复
5. 循环直到所有测试通过
```

**关键洞察**：
- 测试不再只是质量保障，而是**Agent的训练数据**
- 没有测试套件的项目无法发挥AI编程的全部潜力
- TDD + AI Agent 形成完美循环

#### 方法二：上下文透明原则

> "LLM tools that obscure context from me are LESS effective"

**关键实践**：
- 使用工具如 gitingest、repo2txt 将代码库转为LLM可理解的上下文
- CLAUDE.md / GEMINI.md 等规则文件将普及
- 文件系统作为Agent状态管理的标准方案

#### 方法三：人类监督原则

> "If you're going to exploit these tools, you need to be operating at the top of your game"

**要点**：
- AI会愉快地生成看似合理的代码，但**你要负责质量**
- 越是资深工程师，越能有效利用AI
- 监督不意味着逐行审查，而是把握关键架构和决策

### 2.3 工具选择

Simon Willison的推荐工具链：
- **Claude Code / Cursor**：核心编程助手
- **gitingest**：将Git仓库转为可用上下文
- **repo2txt**：类似功能，代码库文档化
- **测试框架**：pytest / jest 等

---

## 三、Addy Osmani的LLM编程工作流

### 3.1 核心原则

> "LLMs are only as good as the context you provide — show them the relevant code, docs, and constraints"

**AI只有在你提供良好上下文时才能发挥作用。**

### 3.2 六步工作流（Going Into 2026）

#### Step 1: 明确任务边界
- 清晰定义要解决的问题
- 拆解为可管理的小任务
- 设定验收标准

#### Step 2: 准备上下文
- 提供相关代码文件
- 包含文档和约束条件
- 说明代码风格和架构

#### Step 3: 迭代对话
- 从高层设计开始
- 逐步细化到实现
- 每步验证理解正确性

#### Step 4: 代码审查
- 人类审查AI生成的代码
- 不盲目信任任何输出
- 关注安全性和边界情况

#### Step 5: 测试验证
- 编写或生成测试用例
- 运行验证功能正确性
- 覆盖边界情况和异常

#### Step 6: 重构优化
- 清理代码风格
- 优化性能
- 添加必要注释

### 3.3 关键原则

| 原则 | 说明 |
|------|------|
| **AI增强而非AI替代** | 使用AI加速工作，但不放弃人类判断 |
| **投资测试** | 测试放大了AI的实用性和对结果的信心 |
| **上下文质量** | 提供的上下文质量决定了输出质量 |
| **保持怀疑** | AI会生成看似合理的代码，你负责质量 |

### 3.4 关键金句

> "AI will happily produce plausible-looking code, but YOU are responsible for quality"

> "Invest in tests — it amplifies the AI's usefulness and confidence in the result"

---

## 四、Andrej Karpathy的Software 3.0视角

### 4.1 软件范式演进

| 版本 | 特征 | 代表 |
|------|------|------|
| **Software 1.0** | 人类手写代码 | 传统编程 |
| **Software 2.0** | 神经网络学习规则 | 深度学习模型 |
| **Software 3.0** | LLM驱动的开发 | 自然语言编程 |

### 4.2 核心观点

> "Software 3.0 is eating Software 1.0 and 2.0 — 大量现有软件将被重写"

**关键洞察**：
- 最热门的新编程语言是**英语**
- 编码能力是AI操作数字世界的主要方式
- 未来的"Coding Agent"将成为所有Agent的基础设施

### 4.3 实践建议

1. **拥抱自然语言**：学会用清晰的英语描述技术需求
2. **理解而非记忆**：AI时代更重要的是理解原理而非记忆语法
3. **系统思维**：AI更适合执行明确任务，人类专注系统设计

---

## 五、三大共识总结

### 5.1 共识一：上下文为王

| 来源 | 核心表述 |
|------|---------|
| **Simon Willison** | "Most of the craft comes down to managing context" |
| **Addy Osmani** | "LLMs are only as good as the context you provide" |
| **Harrison Chase** | "File systems are a natural way to represent agent state" |

**实践工具**：
- gitingest / repo2txt：代码库上下文化
- CLAUDE.md / GEMINI.md：项目规则文件
- MCP (Model Context Protocol)：标准化上下文协议

### 5.2 共识二：测试驱动开发复兴

| 来源 | 核心表述 |
|------|---------|
| **Simon Willison** | "If your project has a robust test suite, agentic coding tools can FLY with it" |
| **Addy Osmani** | "Invest in tests — it amplifies AI's usefulness" |

**实践要点**：
- 测试是Agent的训练数据
- TDD + AI = 完美循环
- 没有测试的项目无法发挥AI潜力

### 5.3 共识三：人类保持控制

| 来源 | 核心表述 |
|------|---------|
| **Simon Willison** | "You need to be operating at the top of your game" |
| **Addy Osmani** | "YOU are responsible for quality" |
| **Barry Zhang** | "Code Review from LLM is useful but not as valuable" |

**实践要点**：
- AI增强，不是AI替代
- 资深工程师更能有效利用AI
- 保持对代码质量的最终责任

---

## 六、工具矩阵

### 6.1 编程助手

| 工具 | 特点 | 适用场景 |
|------|------|---------|
| **GitHub Copilot** | 集成度高，补全为主 | 日常编码辅助 |
| **Cursor** | Composer功能强大，上下文管理好 | 复杂项目开发 |
| **Claude Code** | 推理能力强，对话自然 | 架构设计、复杂逻辑 |
| **Windsurf (Codeium)** | 免费可用，功能完整 | 个人开发者 |

### 6.2 上下文工具

| 工具 | 功能 |
|------|------|
| **gitingest** | 将Git仓库转为LLM可用的上下文 |
| **repo2txt** | 代码库文档化 |
| **MCP** | Model Context Protocol标准化 |

### 6.3 规则文件

| 文件 | 用途 |
|------|------|
| **CLAUDE.md** | Claude工具的项目规则 |
| **GEMINI.md** | Gemini工具的项目规则 |
| **AGENTS.md** | 多Agent项目的角色定义 |
| **Rules文件** | Cursor等IDE的项目规则 |

---

## 七、反模式警告

### 7.1 避免的做法

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **盲目信任** | AI生成的代码未经验证 | 测试驱动，人工审查 |
| **上下文遗漏** | 提供的信息不完整 | 充分准备项目上下文 |
| **过度自动化** | 完全依赖AI，放弃判断 | AI增强，保持控制 |
| **忽视测试** | 不写测试直接用AI | 先写测试再生成代码 |
| **复杂提示** | 一次性给出过多要求 | 分步迭代，逐步细化 |

### 7.2 Simon Willison的警告

> "LLM tools that obscure context from me are LESS effective"

不要使用那些隐藏上下文的工具——透明性很重要。

---

## 八、2026年趋势预判

### 8.1 技术趋势

| 趋势 | 说明 |
|------|------|
| **Agentic Engineering普及** | 从Vibe Coding向工程化演进 |
| **上下文协议标准化** | MCP等协议成为行业标准 |
| **测试套件价值提升** | TDD成为AI编程的基础设施 |
| **IDE深度集成** | AI能力与IDE无缝融合 |

### 8.2 能力趋势

| 趋势 | 说明 |
|------|------|
| **上下文管理能力** | 成为核心竞争力 |
| **任务拆解能力** | 将复杂需求分解为AI可执行的任务 |
| **验证审查能力** | 快速审查AI输出的能力 |
| **系统设计能力** | AI执行细节，人类把控架构 |

---

## 九、实践检查清单

### 9.1 开始新项目

- [ ] 创建CLAUDE.md或类似规则文件
- [ ] 建立基础测试框架
- [ ] 准备项目上下文文档
- [ ] 定义代码风格约定

### 9.2 日常开发

- [ ] 先写测试，再让AI生成代码
- [ ] 提供充分的上下文
- [ ] 审查所有AI生成的代码
- [ ] 关注安全和边界情况

### 9.3 代码审查

- [ ] 不盲目信任AI的代码审查建议
- [ ] 重点审查业务逻辑和安全性
- [ ] 验证测试覆盖率
- [ ] 检查性能和可维护性

---

## 参考资料

- Simon Willison. Vibe Engineering. 2025.10
- Simon Willison. Here's How I Use LLMs to Help Me Write Code. 2025.03
- Addy Osmani. My LLM Coding Workflow Going Into 2026. 2025.12
- Andrej Karpathy. Software 3.0: Software in the Age of AI. 2025.06
- Barry Zhang. Building Effective Agents. Anthropic. 2025.10
- Harrison Chase. Ambient Agents and the New Agent Inbox. 2025.05

---

*原始调研时间: 2026-02-01*
*知识库沉淀时间: 2026-03-04*
*整理者: 林克 AI 助手*
*版本: v2.0 - 完整版*
