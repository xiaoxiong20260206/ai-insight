# AI-Insight 知识库

> **版本**: v1.0.0
> **创建时间**: 2026-03-04
> **维护者**: 林克 (沈浪的AI分身)

---

## 知识库概述

这是AI-Insight项目的结构化知识库，用于系统性沉淀AI行业的概念、最佳实践、洞察和实体画像。知识来源于：
1. **每日日报**: 自动提取趋势洞察、新概念
2. **深度调研**: 拆解后分散到各分类
3. **用户文章**: 手动触发提取

---

## 知识索引

### 📚 概念库 (concepts/)

| 分类 | 已有文档 | 内容概述 |
|------|---------|---------|
| **agents/** | agent-architecture.md | Agent定义框架、设计原则、五大工作流模式、ACI设计 |
| **agents/** | agent-types-matrix.md | 企业AI Agent类型定义、岗位场景匹配、建设优先级 |
| **coding/** | ai-coding-practices.md | Vibe Coding vs Vibe Engineering、TDD复兴、上下文管理 |
| **enterprise/** | software-engineering-3.md | 软件工程3.0范式、L1-L2-L3成熟度模型、AI研发提效陷阱 |

### 🛠️ 最佳实践 (best-practices/)

| 文档 | 内容概述 |
|------|---------|
| enterprise-ai-product-design.md | 企业AI数字员工产品设计、从工具到员工转变、主动服务设计 |
| financial-ai-agent-design.md | 金融AI Agent产品设计、Quant/Research/Data Agent详细规格 |

### 💡 洞察 (insights/)

| 分类 | 文档 | 内容概述 |
|------|------|---------|
| **根目录** | ai-industry-principles.md | 复杂度守恒、泛化是压缩、反馈环路、AI下半场 |
| **weekly/** | 2026-03-week1.md | 2026年3月第1周核心信号、关键数据、趋势洞察 |

### 👤 实体画像 (entity-profiles/)

| 分类 | 文档 | 内容概述 |
|------|------|---------|
| **people/** | barry-zhang.md | Barry Zhang (Anthropic) 思想体系、Agent设计原则、Skills范式 |
| **companies/** | high-flyer-quant.md | 幻方量化公司画像、AI应用场景、DeepSeek孵化 |

---

## 知识关系图谱

```
concepts/agents/agent-architecture.md
├── 引用自: Barry Zhang 思想体系
├── 相关: agent-types-matrix.md (Agent类型定义)
└── 相关: enterprise-ai-product-design.md (产品设计)

concepts/coding/ai-coding-practices.md
├── 引用自: Simon Willison, Andrej Karpathy, Addy Osmani
├── 相关: software-engineering-3.md (SE3.0与AI研发)
└── 相关: 2026-03-week1.md (Cursor更新洞察)

concepts/enterprise/software-engineering-3.md
├── 引用自: 快手AI研发实践、朱少民理论
├── 相关: enterprise-ai-product-design.md (产品设计)
└── 相关: ai-industry-principles.md (复杂度守恒原理)

best-practices/financial-ai-agent-design.md
├── 引用自: 金融企业数字人产品架构设计
├── 相关: agent-types-matrix.md (Agent类型)
└── 相关: high-flyer-quant.md (幻方量化实践)

insights/ai-industry-principles.md
├── 引用自: 多位AI大神深度分享
├── 相关: agent-architecture.md (Agent = Model + Tools + Loop)
└── 相关: software-engineering-3.md (AI下半场)

entity-profiles/people/barry-zhang.md
├── 核心贡献: agent-architecture.md
└── 相关: insights/ai-industry-principles.md

entity-profiles/companies/high-flyer-quant.md
├── 相关: financial-ai-agent-design.md (金融AI设计)
└── 参考调研: 幻方量化AI应用调研报告.md
```

---

## 待填充目录

以下目录已创建但尚无内容，待后续调研时填充：

- `concepts/models/` - 大模型技术、训练方法
- `concepts/applications/` - AI应用设计、产品模式
- `concepts/infrastructure/` - AI基础设施、部署、算力
- `concepts/safety/` - AI安全、对齐、伦理
- `insights/quarterly/` - 季度趋势分析

---

## 使用指南

### 查询知识
```
"知识库里关于Agent的内容有哪些？"
"回顾一下Barry Zhang的核心观点"
"AI编程的最佳实践是什么？"
```

### 新增知识
- 日报/调研完成后自动触发
- 用户分享文章后说"学习这篇文章"

### 知识更新原则
1. **增量更新**: 新内容追加，不覆盖原有
2. **版本记录**: 重大更新标注时间和来源
3. **交叉引用**: 相关概念间建立链接
4. **来源标注**: 所有知识点必须标注来源

---

## 统计信息

| 指标 | 数量 |
|------|------|
| 概念文档 | 4 |
| 最佳实践文档 | 2 |
| 洞察文档 | 2 |
| 实体画像 | 2 |
| **总计** | **10** |

---

*最后更新: 2026-03-04*
