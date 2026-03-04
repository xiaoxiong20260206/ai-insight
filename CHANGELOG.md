# AI-Insight 更新日志

所有重要变更将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.0.0] - 2026-03-04

### 新增

- **项目初始化**: 创建完整的目录结构
  - `01-daily-reports/` - AI日报目录
  - `02-deep-research/` - 深度调研目录
  - `03-tracking-registry/` - 追踪体系目录
  - `04-knowledge-base/` - 知识沉淀目录
  - `05-outputs/` - 对外输出目录
  - `scripts/` - 自动化脚本目录

- **迁移现有内容**:
  - AI日报 (2026-03-03) 迁移至 `01-daily-reports/2026-03/`
  - AI大神分享深度分析 迁移至 `02-deep-research/trends/`
  - Barry Zhang思想体系总结 迁移至 `02-deep-research/trends/`
  - 字节AI调研 迁移至 `02-deep-research/companies/bytedance-ai-guide/`

- **追踪体系初始化**:
  - `03-tracking-registry/people/index.md` - L1/L2/L3人物清单
  - `03-tracking-registry/companies/index.md` - 公司分级清单
  - `03-tracking-registry/sources/index.md` - 信息源清单

- **项目文档**:
  - `README.md` - 项目说明
  - `CHANGELOG.md` - 更新日志

---

## [1.1.0] - 2026-03-04

### 新增

- **整合迁移所有AI调研项目**:
  - `分身/ai-agent-report/` → `02-deep-research/topics/ai-agent-guide/`
  - `CF0201_AIStudio/` → `02-deep-research/topics/ai-studio/`
  - `CF0201_AITools/` → `02-deep-research/topics/ai-tools-analysis/`
  - `CF0201_Financial/` → `02-deep-research/topics/ai-financial/`
  - `CF0201_agent_infra_docs/` → 合并到 `topics/ai-studio/3-agent-infra/`
  - `AIFinLearn/` → `04-knowledge-base/concepts/financial/`
  
- **深度调研索引**: 创建 `02-deep-research/index.md`

### 删除

- 清理CodeFlicker根目录已迁移的老文件夹:
  - `分身/`、`CF0201_AIStudio/`、`CF0201_AITools/`
  - `CF0201_Financial/`、`CF0201_agent_infra_docs/`
  - `AIFinLearn/`、`ai-daily-report/`、`字节AI调研/`

### 待办

- [ ] 日报生成脚本迁移
- [ ] 索引页自动生成
- [ ] 第一次月度Review

---

## [1.2.0] - 2026-03-04

### 新增

- **追踪体系大幅增强** (v1.1.0):
  - **人物清单** 新增15+人物:
    - SSI: Ilya Sutskever
    - Anthropic: Jan Leike
    - 学术界: Percy Liang, Sasha Rush, Jonathan Frankle
    - 中国: 朱松纯, 颜水成, 刘知远, 贾扬清
    - 独立: Chris Lattner
    - YouTube: Yannic Kilcher, AI Explained
    - Newsletter: Jack Clark, Andrew Ng, Nathan Lebenz
    - 中文: 潘乱, 海外独角兽, 张小珺, 晚点
  
  - **公司清单** 新增30+公司，重构分类体系:
    - 改为多维度分类 (地区/类型/规模)
    - 新增SSI, Perplexity, Hugging Face, Scale AI, Groq等
    - 补充AI应用公司 (搜索/写作/设计/视频/音乐)
    - 补充AI基础设施 (开源平台/推理/数据/芯片)
    - 补充垂直行业 (机器人/医疗)
  
  - **信息源清单** 新增50+信息源:
    - YouTube频道 (6个)
    - 学术源 (ArXiv, Papers With Code, LMSYS)
    - 社区源 (GitHub Trending, HN, Reddit)
    - 中文播客 (5个)
    - Newsletter (4个新增)

- **模板系统**:
  - `templates/daily-report-template.md` - AI日报模板
  - `templates/deep-research-template.md` - 深度调研模板

- **与Skill关系文档**:
  - `docs/skill-relationship.md` - 明确项目与Skill的职责边界

### 变更

- 人物清单版本升级至 v1.1.0
- 公司清单版本升级至 v1.1.0
- 信息源清单版本升级至 v1.1.0

