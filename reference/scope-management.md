# 调研范围管理指南 (v1.2)

> **版本**: v1.2
> **更新时间**: 2026-03-10
> **对齐**: SKILL.md v7.5.0

## 概述

管理AI-Insight追踪的人物、公司和信息源，确保调研覆盖全面且聚焦。

---

## 时效性维护（v1.2新增，P1强制）

> **教训**: 2026-03-10日报因搜索关键词配置过时（仍列MarsCode为独立产品，实际已更名为Trae），导致竞争格局判断错误。信息源管理同样面临时效性风险。

### 配置保鲜的必要性

追踪体系是"活的"，需要定期更新：
- 公司会更名/合并/停运（如 MarsCode → Trae）
- 信息源URL会失效
- 人物会跳槽/退休
- 竞争格局会变化

### 月度配置保鲜检查（每月1日，P1）

**自检清单**:
- [ ] 公司列表中是否有已更名/合并/停运的？
- [ ] 信息源URL是否仍然有效？
- [ ] 人物是否仍在原岗位？
- [ ] 搜索关键词配置是否反映当前竞争格局？
- [ ] 过去一月日报实际引用的来源，是否有新的质量问题？

**更新触发条件**:
- 日报/周报中发现产品更名/合并/停运
- 搜索时发现URL 404
- 用户反馈信息过时

**更新原则**:
- 发现即更新，不要等月度检查
- 更新后同步到所有相关文件（三文件原子同步）
- 标注更新日期和原因

---

## 追踪体系结构

```
../AI-Insight/03-tracking-registry/
├── people/index.md       # 人物追踪
├── companies/index.md    # 公司追踪
└── sources/index.md      # 信息源追踪
```

---

## 人物追踪 (people/index.md)

### 分层定义

| 层级 | 定义 | 追踪频率 |
|------|------|----------|
| L1 实践者 | 直接构建AI产品的人 | 每日 |
| L2 观察者 | 深度分析AI趋势的人 | 每周 |
| L3 决策者 | AI行业重要决策者/投资人 | 每周 |

### L1 实践者示例
- Andrej Karpathy (前Tesla AI总监，AI教育者)
- Barry Zhang (Anthropic PM，Agent专家)
- Greg Brockman (OpenAI联创)
- Dario Amodei (Anthropic CEO)

### L2 观察者示例
- Simon Willison (AI工具链分析)
- Ethan Mollick (AI应用研究)
- swyx (AI工程化布道)

### L3 决策者示例
- Sam Altman (OpenAI CEO)
- Jensen Huang (NVIDIA CEO)
- Satya Nadella (Microsoft CEO)

### 条目格式
```markdown
## [人物姓名]

- **角色**: [职位/身份]
- **层级**: L1/L2
- **追踪原因**: [为什么追踪]
- **主要来源**: [博客/Twitter/等]
- **最近动态**: YYYY-MM-DD - [简要描述]
```

### 添加新人物的标准
1. 在AI领域有持续输出
2. 观点有独特价值（不是单纯转述）
3. 有可追踪的公开信息源

---

## 公司追踪 (companies/index.md)

### 分类

| 类别 | 说明 |
|------|------|
| 大模型 | OpenAI, Anthropic, Google, DeepSeek等 |
| AI Coding | Cursor, Replit, GitHub Copilot等 |
| AI 应用 | Perplexity, Notion AI, Midjourney等 |
| 基础设施 | NVIDIA, CoreWeave等 |

### 条目格式
```markdown
## [公司名称]

- **领域**: [大模型/AI Coding/AI应用/基础设施]
- **追踪原因**: [为什么追踪]
- **主要来源**: [官网/博客/新闻]
- **关键人物**: [CEO/CTO等]
- **最近动态**: YYYY-MM-DD - [简要描述]
```

---

## 信息源追踪 (sources/index.md)

### 分类

| 类别 | 优先级 | 说明 |
|------|--------|------|
| 官方源 | P0 | 公司官方博客、文档 |
| 技术博客 | P1 | 开发者博客、技术分析 |
| 行业媒体 | P2 | TechCrunch、The Verge等 |
| 中文媒体 | P2 | 36kr、机器之心等 |
| 社区 | P3 | Twitter/X、Reddit、HN |

### 海外源示例
```
官方:
- openai.com/blog
- anthropic.com/news
- blog.google/technology/ai
- cursor.com/changelog

技术:
- simonwillison.net
- latent.space
- every.to/chain-of-thought

媒体:
- techcrunch.com/category/artificial-intelligence
- theverge.com/ai-artificial-intelligence
```

### 国内源示例
```
媒体:
- 36kr.com/topic/AI
- jiqizhixin.com (机器之心)
- oschina.net/news (开源中国)

行业:
- mp.weixin.qq.com (AI相关公众号)
- zhihu.com/topic/AI
```

### 条目格式
```markdown
## [信息源名称]

- **URL**: [链接]
- **类型**: [官方/技术/媒体/社区]
- **优先级**: P0/P1/P2/P3
- **语言**: [中文/英文]
- **更新频率**: [每日/每周/不定期]
- **关注点**: [侧重什么内容]
```

---

## 操作指南

### 添加新追踪项
1. 确定类型（人物/公司/信息源）
2. 打开对应的index.md文件
3. 按照条目格式添加
4. 提交到Git

### 更新动态
1. 定期更新"最近动态"字段
2. 保持日期格式一致 (YYYY-MM-DD)

### 删除追踪项
1. 评估是否还有追踪价值
2. 直接删除条目或标记为"已停止追踪"

---

## ⭐ 追踪体系批量扩展工作流 (2026-03-07沉淀)

> **经验来源**: 国内AI Coding完整梯队(10家)+4家大模型公司一次性扩展实战

### 适用场景
- 发现追踪体系存在**整个品类缺失**（不是个别公司遗漏）
- 需要一次性新增一个**完整赛道/垂直领域**
- 例如：国内AI Coding、具身智能、AI安全、AI音乐等

### 核心方法：Gap-Driven Discovery（间隙驱动发现法）

```
❌ 错误方式：有什么加什么（零散补漏）
✅ 正确方式：缺什么找什么（结构性补全）

Step 1: 绘制现有覆盖地图
  → 读取三个追踪文件，列出已覆盖的品类和公司
  → 按"海外/国内 × 品类"矩阵标注

Step 2: 识别结构性空白
  → 找到整个品类缺失的区域（如国内AI Coding = 0家）
  → 区分"个别遗漏"和"系统性盲区"

Step 3: 用空白区域作为搜索框架
  → 针对缺失品类做专项调研
  → 关键词："国内AI编程工具 排名"、"AI Coding tools China"
  → 搜索维度：产品榜单、融资新闻、用户评测、开源热度

Step 4: 梯队分级（复用现有框架）
  → Tier1=头部（用户量/知名度最高）
  → Tier2=主力（大厂方案/有明确定位）
  → Tier3=新锐（小众/特色/观察期）
  → 保持与现有分级体系的结构一致性
```

### 渠道映射模板（Channel Mapping）

> **原则**: 每新增一家公司，必须同时完成渠道映射，不能只加公司不加信源

每家公司的完整渠道画像：

| 渠道类型 | 获取方法 | 必要性 |
|---------|---------|--------|
| **官方网站** | 搜索"[产品名]"直接找到 | ✅ 必须 |
| **GitHub仓库** | 搜索"[产品名] github"或"[公司名] github" | ⚡ 开源产品必须 |
| **微信公众号** | 搜索"[公司/产品名] 公众号"或"[公司名] 微信" | ✅ 国内公司必须 |
| **技术博客** | 通常在官网/blog路径 | 🔶 有则加 |
| **X/Twitter** | 搜索"[公司名] twitter" | 🔶 海外公司必须 |
| **Discord/社区** | 搜索"[产品名] discord/community" | 🔶 有则加 |

### 多维渠道三角验证法

```
验证一家公司信息的三条路径：
路径A: 产品名 → 官方网站 → 确认产品定位和功能
路径B: 产品名 + "GitHub" → 开源仓库 → 确认技术栈和活跃度
路径C: 公司名 + "公众号" → 微信 → 确认官方运营渠道
三条路径交叉验证，避免信息遗漏或错误
```

### 三文件原子同步 + 首页联动

```
追踪体系 = companies + sources + people 三个文件组成的系统
规则：一次性更新三文件 + 单次原子提交 + 首页同步

更新顺序（推荐）：
1. companies/index.md → 新增公司梯队
2. sources/index.md → 新增官方渠道 + 微信公众号
3. people/index.md → 新增核心人物
4. 版本号全部递增
5. ⭐ 更新 scripts/update_tracking.py 中对应的数据
6. ⭐ 运行 uv run scripts/update_tracking.py → 同步首页HTML
7. ⭐ 手动更新 index.html 统计卡片数字 (.stats-grid)
8. git add 全部文件 → 单次commit → push

⚠️ 禁止：只更新MD文件不同步首页（会导致数据漂移）
⚠️ 禁止：手动编辑 index.html 的追踪 section（应修改脚本后重跑）
```

### 扩展检查清单

- [ ] 现有覆盖地图已绘制
- [ ] 结构性空白已识别（不是零散遗漏）
- [ ] 新品类按Tier1/2/3分级
- [ ] 每家公司的渠道映射已完成（官网+公众号+GitHub）
- [ ] companies/index.md 已更新 + 版本号递增
- [ ] sources/index.md 官方博客区已更新
- [ ] sources/index.md 微信公众号区已更新
- [ ] people/index.md 核心人物已补充
- [ ] 快速索引已更新且无重复
- [ ] **scripts/update_tracking.py 脚本数据已同步更新**
- [ ] **已运行 `uv run scripts/update_tracking.py` 同步首页HTML**
- [ ] **index.html 统计卡片数字已手动更新**
- [ ] **本地预览验证追踪体系展开内容正确**
- [ ] 三文件 + 首页 原子提交

---

## 触发词

- "添加追踪 [人物/公司名]"
- "新增信息源 [URL]"
- "更新追踪列表"
- "查看追踪体系"
