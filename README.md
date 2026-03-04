# AI-Insight 持续洞察项目

> **建立一个系统化、可持续的AI行业追踪学习平台**

---

## 项目定位

AI-Insight 是一个**AI行业深度追踪与洞察输出平台**，整合了：
- 📰 **AI日报** - 每日AI行业动态汇总
- 🔬 **深度调研** - 公司调研、专题研究、趋势洞察
- 🎯 **追踪体系** - AI公司/大神分级追踪清单
- 📚 **知识沉淀** - 概念、最佳实践、洞察结论
- 📤 **对外输出** - 报告、演示、文章

---

## 目录结构

```
AI-Insight/
├── README.md                    # 本文件
├── CHANGELOG.md                 # 项目更新日志
│
├── 01-daily-reports/            # AI日报（每日产出）
│   └── 2026-03/                 # 按月归档
│       └── 2026-03-03.md
│
├── 02-deep-research/            # 深度调研
│   ├── trends/                  # 趋势洞察
│   │   ├── 从AI大神的深度分享看2026年AI的下半场.md
│   │   ├── 从AI大神的深度分享看2026年AI发展趋势.md
│   │   └── Barry_Zhang_Anthropic_思想体系总结.md
│   │
│   ├── companies/               # 公司调研
│   │   └── bytedance-ai-guide/  # 字节AI开挂指南
│   │
│   └── topics/                  # 专题调研
│       ├── ai-agent-guide/      # AI Agent团队落地指南
│       ├── ai-studio/           # 企业AI工程师产品体系
│       │   ├── 1-ai-engineer-analysis/  # 用户场景分析
│       │   ├── 2-ai-workbench/          # 产品设计方案
│       │   └── 3-agent-infra/           # 技术架构设计
│       ├── ai-tools-analysis/   # AI工具场景分析
│       └── ai-financial/        # AI金融应用调研
│
├── 03-tracking-registry/        # 追踪体系（核心知识库）
│   ├── people/index.md          # 人物追踪清单
│   ├── companies/index.md       # 公司追踪清单
│   └── sources/index.md         # 信息源清单
│
├── 04-knowledge-base/           # 知识沉淀
│   ├── concepts/                # 概念/框架
│   │   └── financial/           # 金融概念学习
│   ├── best-practices/          # 最佳实践
│   └── insights/                # 洞察结论
│
├── 05-outputs/                  # 对外输出
│   ├── reports/                 # 报告产出
│   ├── presentations/           # 演示文稿
│   └── articles/                # 文章发布
│
├── templates/                   # 模板
│   ├── daily-report-template.md # 日报模板
│   └── deep-research-template.md# 调研模板
│
├── docs/                        # 项目文档
│   └── skill-relationship.md    # 与Skill关系说明
│
└── scripts/                     # 自动化脚本
```
│   └── articles/                # 文章发布
│
└── scripts/                     # 自动化脚本
```

---

## 深度调研内容一览

### 趋势洞察 (`02-deep-research/trends/`)

| 内容 | 说明 |
|------|------|
| AI大神深度分享解读 | 9位AI领域思想领袖的核心观点提炼 |
| Barry Zhang思想体系 | Anthropic Applied AI负责人的Agent设计原则 |

### 公司调研 (`02-deep-research/companies/`)

| 内容 | 说明 |
|------|------|
| 字节AI开挂指南 | 字节跳动AI能力全景解析 |

### 专题调研 (`02-deep-research/topics/`)

| 目录 | 内容 | 说明 |
|------|------|------|
| `ai-agent-guide/` | AI Agent团队落地指南 | 4章节完整落地手册，面向产品经理 |
| `ai-studio/` | 企业AI工程师产品体系 | 从场景分析到产品设计到架构设计的完整方法论 |
| `ai-tools-analysis/` | AI工具场景分析 | AI工程师48个工作任务+9种Agent映射 |
| `ai-financial/` | AI金融应用调研 | 幻方量化调研、金融数字人产品架构 |

---

## 追踪体系 (v1.1.0)

### 人物分级 (`03-tracking-registry/people/`)
- **L1 实践者/构建者** (30+人): Barry Zhang, Andrej Karpathy, Ilya Sutskever, 姚顺雨, Addy Osmani, Percy Liang...
- **L2 深度观察者** (20+人): Simon Willison, Gergely Orosz, Swyx, 宝玉, 李沐, Yannic Kilcher...
- **L3 战略决策者** (10+人): Sam Altman, Dario Amodei, Jensen Huang, Sundar Pichai...

### 公司分类 (`03-tracking-registry/companies/`)
**多维度分类体系**:
- **模型实验室**: OpenAI, Anthropic, Google DeepMind, Meta, SSI, DeepSeek, 智谱...
- **AI Coding**: Cursor, Cognition, Replit, GitHub Copilot, Codeium...
- **AI 应用**: Perplexity, Midjourney, Runway, Jasper, Notion AI...
- **AI 基础设施**: Hugging Face, LangChain, Scale AI, Groq, Together AI...
- **中国公司**: DeepSeek, 智谱, Moonshot, 百川, 阿里Qwen, 字节豆包...

### 信息源 (`03-tracking-registry/sources/`)
- **官方博客**: 20+公司博客
- **Newsletter**: 10+订阅源
- **YouTube**: 6个重要频道
- **播客**: 10+中英文播客
- **学术源**: ArXiv, Papers With Code, LMSYS
- **社区**: GitHub Trending, HN, Reddit

---

## 使用指南

### 查找信息

1. **找特定人物/公司**: 查看 `03-tracking-registry/` 下对应文件
2. **查阅日报**: 进入 `01-daily-reports/YYYY-MM/` 找对应日期
3. **查阅深度调研**: 进入 `02-deep-research/` 按类型查找

### 日常维护

1. **每日**: 生成AI日报，存入 `01-daily-reports/`
2. **每周**: 产出1-2篇深度调研，存入 `02-deep-research/`
3. **每月**: Review追踪体系，更新 `03-tracking-registry/`

---

## 与其他项目的关系

| 项目 | 关系 |
|------|------|
| `codeflicker-homepage` | 日报同步展示 |
| `kim-ai-bot` | 日报群推送 |
| `Knowledge/` | 知识输出同步（保持兼容） |

---

## 里程碑

- [x] 2026-03-04: 项目初始化，完成目录结构和追踪体系
- [x] 2026-03-04: 迁移整合所有AI相关调研项目
  - 分身项目(AI Agent指南) → `topics/ai-agent-guide/`
  - CF0201_AIStudio → `topics/ai-studio/`
  - CF0201_AITools → `topics/ai-tools-analysis/`
  - CF0201_Financial → `topics/ai-financial/`
  - AIFinLearn → `knowledge-base/concepts/financial/`
  - 字节AI调研 → `companies/bytedance-ai-guide/`
- [ ] 本周: 日报生成脚本迁移
- [ ] 本周: 主页同步自动化
- [ ] 本月: 第一次追踪体系月度Review

---

## 维护者

**林克** (沈浪基于CodeFlicker打造的数字分身)

---

*让AI行业洞察变得系统化、可持续*
