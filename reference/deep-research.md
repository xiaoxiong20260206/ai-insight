# AI深度研究方法论 (v2.6)

> **版本**: v3.0
> **更新时间**: 2026-04-25
> **对齐**: SKILL.md v10.4.0
> **本次更新**: 新增经验#59——三版首页卡片各自独立无自动同步（preserve_block陷阱）；Step 5.5 新增四端首页卡片门控检查命令；双仓发布规则补充

## 概述

深度研究是对特定主题进行系统性、多源信息整合的分析报告，输出具有洞察力的研究结论。

---

## 时效性要求（v2.3新增）

> **教训**: 2026-03-10日报因搜索关键词泛日期导致用旧闻做头条。深度研究同样面临时效性风险：容易使用过时的竞争格局数据、已失效的产品信息。

**深度研究时效性窗口**: 最近1-3个月

**时效性分级**:

| 内容类型 | 时效性要求 | 风险 |
|---------|-----------|------|
| **竞争格局** | ≤3个月 | 用半年前的玩家列表，遗漏新进入者/退出者 |
| **产品功能** | ≤1个月 | 功能已更新但报告仍写旧版本 |
| **融资估值** | 最新报道 | 用去年数据，与实际差距大 |
| **行业趋势** | ≤3个月 | 趋势已反转但报告仍沿用旧判断 |

**自检清单（P0强制）**:
- [ ] 竞争格局分析的信源是否在最近3个月内？
- [ ] 产品功能/定价信息是否已更新？
- [ ] 融资/估值数据是否使用最新报道？
- [ ] 是否标注了关键信息的数据日期？
- [ ] 引用的"最佳实践"是否仍然有效（未被新发展推翻）？

**与日报/周报的区别**:

| 维度 | 日报 | 周报 | 深度研究 |
|------|------|------|---------|
| 时效性窗口 | 当天 | 本周 | 最近1-3个月 |
| 时间锚点词 | "today" | "this week" | "2026 Q1"/"最近3个月" |
| 风险 | 用旧闻做头条 | 拷贝上周内容 | 竞争格局过时 |

---

## 研究类型

| 类型 | 目录 | 说明 | 示例 |
|------|------|------|------|
| 趋势洞察 | `trends/` | AI行业趋势分析 | "从AI大神的深度分享看2026年AI的下半场" |
| 公司调研 | `companies/` | 单一公司深度分析 | "Anthropic 公司深度调研" |
| 人物追踪 | `people/` | 思想领袖观点汇总 | "Barry Zhang Anthropic思想体系总结" |
| 专题研究 | `topics/` | 特定主题深入研究 | "AI Agent 架构演进" |

---

## 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│ 1. 明确问题 │ →  │ 2. 多源搜索 │ →  │ 3. 信息整合 │ →  │ 4. 洞察提炼 │ →  │ 5. 生成报告 │ →  │ 5.5 双版本同步(P0)│ →  │ 6. 首页同步 │ →  │ 7. KIM推送  │ →  │ 8. KIM Doc（可选）│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └──────────────────┘    └─────────────┘    └─────────────┘    └─────────────────┘
```

> **v2.6 新增**: Step 5.5 双版本同步为 P0 强制步骤，不允许跳过。
> **教训**: 2026-04-06 发现 meta-skill-system-2026.html 被直接推送到外部仓库，绕过脱敏管道，
> 导致外部版包含"林克"敏感词且内部版缺失该文件。根因：深度调研工作流没有强制双版本同步步骤。

---

## Step 8: KIM Doc 文章生成（可选，用户明确要求时执行）

> **触发词**：「生成KIM Doc」「写KIM文章」「输出KIM格式」「发布到Docs」
> **执行方式**：直接读取本技能的子技能文档

```
read_file("references/kim-doc/kim-doc.md")
```

**说明**：
- 此步骤将调研内容按《99%的AI产品都做错了》的文档风格，生成完整的专栏文章
- 输出标准：`【林克的AI洞察】[标题]` 格式，含00全文概览 + 核心章节 + 彩蛋 + 了解更多
- 完成后需上传到 KIM Docs，并提供文档链接

---

## Step 1: 明确研究问题

### 问题定义框架
1. **核心问题**: 这个研究要回答什么问题？
2. **范围边界**: 研究包含什么、不包含什么？
3. **预期输出**: 研究完成后应该得到什么？
4. **目标受众**: 这个研究给谁看？

### 示例
```
核心问题: AI Agent 的设计原则是什么？最佳实践有哪些？
范围边界: 聚焦生产级Agent，不包括学术原型
预期输出: 设计原则清单 + 最佳实践指南 + 避坑经验
目标受众: AI应用开发者
```

---

## Step 2: 多源搜索

### 两层搜索架构（v2.2）

深度研究搜索采用与日报相同的两层架构，但**深度和广度要求更高**：

```
深度研究搜索流程:
  Step 2.1 L1 多轮广扫 → 海外+国内多角度搜索
  Step 2.2 L2 精研验证 → fetch_web 提取全文 + 交叉验证
```

### Step 2.1 L1 多轮广扫（核心步骤）

> 深度研究比日报需要更多轮搜索，确保多角度覆盖

**工具**: `search_web` + `weixin_search`

```
搜索策略（4步法）:
1. 官方源: search_web("[主题] site:official-domain.com") → 先查官方博客、文档、演讲
2. 专家观点: search_web("[主题] expert analysis deep dive") → 查找领域专家的分析
3. 社区反馈: search_web("[主题] reddit OR hackernews review") → 了解实际使用者的评价
4. 对比分析: search_web("[主题] vs [竞品] comparison") → 搜索竞品/替代方案的比较

国内补充:
5. search_web("[中文主题] 最新 分析 深度") → 中文深度分析
6. weixin_search("[主题关键词]") → 机器之心、量子位等对该主题的深度分析
7. get_weixin_article_content([URL]) → 提取公众号文章全文用于深度分析
```

### Step 2.2 L2 精研验证（关键事实核查）

> 对 L1 收集的关键事实和源内容，用 fetch_web 做深入验证

**工具**: `search_web` + `fetch_web`

```
1. 全文提取: fetch_web([关键文章URL]) → 获取完整内容（而非搜索片段）
2. 事实验证: search_web("[具体事实或数字]") → 多源交叉确认
3. 一手源回溯: fetch_web([官方博客/论文URL]) → 验证二手信息是否与原文一致
```

**验证重点**:
- 关键数据/结论 → 验证是否有原始来源支撑
- 融资金额/估值数据 → 至少2个独立来源交叉确认
- 竞争格局判断 → 确认信源时效性≤3个月

### 信息源优先级

| 优先级 | 来源类型 | 示例 |
|--------|----------|------|
| P0 | 一手资料 | 官方博客、演讲视频、论文 |
| P1 | 深度分析 | 技术博客、行业报告 |
| P2 | 行业报道 | TechCrunch、The Verge |
| P3 | 社区讨论 | Twitter/X、Reddit、HN |

### 搜索策略（总结）
1. **L1 多轮广扫**: 用 search_web + weixin_search 多角度搜索（海外+国内）
2. **L2 全文精研**: 用 fetch_web 提取关键文章全文做深入分析
3. **交叉验证**: 对关键事实用 search_web 做定向验证
4. **P0 回溯**: 对报告中的核心结论，回溯到官方/一手来源确认

### 搜索关键词示例
```
主题: Anthropic Agent 设计原则

L1 广扫:
搜索词:
- "Anthropic agent design principles"
- "Barry Zhang agent"
- "Claude agent best practices"
- "anthropic.com/research agent"
- "Building effective agents Anthropic"
微信搜索:
- weixin_search("Anthropic Agent 最佳实践")
- weixin_search("Claude Agent 设计原则")

L2 精研:
- fetch_web("https://anthropic.com/research/building-effective-agents") → 提取官方原文
- search_web("Anthropic agent design principles review") → 多源验证
```

---

## Step 3: 信息整合

### 信息分类
```
收集到的信息
├── 核心观点 (直接回答研究问题)
├── 支撑数据 (量化证据)
├── 案例实例 (具体应用)
├── 争议/反面观点 (平衡视角)
└── 延伸线索 (值得深入的方向)
```

### 交叉验证
- 同一观点是否有多个独立来源支持？
- 数据来源是否可靠？
- 是否有反面证据需要考虑？

---

## Step 4: 洞察提炼

### 洞察标准
1. **非显而易见**: 不是常识，有分析价值
2. **有数据支撑**: 不是纯观点，有证据
3. **可操作**: 读者看完知道该怎么做
4. **前瞻性**: 不只是描述现状，还有趋势判断

### 洞察模板
```markdown
**洞察**: [一句话核心观点]

**支撑**:
- [数据/案例1]
- [数据/案例2]

**为什么重要**: [影响分析]

**建议**: [可执行的行动建议]
```

---

## Step 5: 生成报告

### ⚡ HTML样式规范（P0强制）

- 深度调研HTML **必须使用清爽调研报告风格**（样式已内置在各HTML生成脚本中）
- 必须包含: Mesh Gradient背景 + 毛玻璃Tab导航 + 五色语义调色板 + 章节概览图 + SVG Favicon
- **⚠️ Tab 导航 P0 禁止项（v2.7新增）**：
  - **禁止**使用 emoji 作为 Tab 按钮图标（如 `👤 研究概览`、`💡 核心发现`）
  - **必须**使用 SVG icon + 文字分离结构：`<span class="tab-icon"><svg>...</svg></span><span class="tab-label">文字</span>`
  - Tab 按钮必须有 `touch-action: manipulation` + `min-height: 44px`（移动端可触控）
  - Tab 按钮必须有 `:focus-visible` Emerald 焦点环
  - 移动端 (<768px) 必须隐藏 `.tab-label`，只显示 SVG icon
  - 详见记忆「深度调研HTML必须严格遵循P0样式规范」的 Tab 导航专项细节

### ⚡ 产品官网图片直引规范（v2.5新增）

> **成功案例**: 钉钉悟空深度调研，直接引用官网CDN图片展示四大核心能力，效果远超截图。
> **核心收益**: 高分辨率 + 无需本地存储 + 与官网一致的专业视觉

**适用场景**:
- 产品/公司深度调研中需要展示产品界面、核心能力、Demo效果
- 被调研产品有官网且图片托管在CDN

**获取方法（三步法）**:
```
Step 1: 用 browser_agent 访问官网，获取图片资源URL列表
Step 2: 识别CDN域名（如 gw.alicdn.com、img.qcloud.com）
Step 3: 在HTML中直接 <img src="CDN_URL"> 引用
```

**常见CDN域名**:
| 平台 | CDN域名 |
|------|---------|
| 阿里系 | gw.alicdn.com |
| 腾讯系 | img.qcloud.com |
| 字节系 | p*.douyinpic.com |

**布局建议**:
- 产品主视觉放在章节开头（作为hero image）
- 核心能力采用左右交替布局（图文对照）
- 每个能力卡片包含：图标 + 标题 + 描述 + 演示截图
- 添加移动端响应式适配（grid → 单列）

**禁止事项**:
- 禁止截图后上传（CDN图片分辨率更高）
- 禁止使用动态链接/临时URL（确保链接长期有效）
- 禁止引用需登录才能访问的图片

### 报告结构
```markdown
# [研究主题]

## 研究背景
- 为什么要研究这个主题？
- 研究范围和方法

## 核心发现
### 发现1: [洞察标题]
...

### 发现2: [洞察标题]
...

### 发现3: [洞察标题]
...

## 详细分析
[按主题/时间线/重要性组织]

## 数据支撑
[关键数据和图表]

## 趋势判断与建议
[前瞻性分析 + 行动建议]

## 参考来源
[所有引用来源的链接]
```

### ⚡ 底部"了解更多"模块（P0强制）

> **教训**: 2026-03-10纳瓦尔AI调研，"了解更多"模块只有相关链接，缺少林克介绍+首页入口按钮。
> **根因**: 声明式规则 ≠ 可执行指令，技能文档说"保留了解更多"但没给具体模板。

**所有深度调研HTML报告底部必须使用统一的"了解更多"模块**，包含：

1. **林克介绍段落**（"我是林克，沈浪的AI分身..."）
2. **首页入口按钮**（"🏠 访问AI洞察首页"）
3. **相关资源列表**（深度调研页面需要列出参考来源链接）

**完整HTML模板详见 `references/footer-template.md`。**

生成HTML时，直接从模板复制HTML代码，确保格式一致。

**禁止出现**: 其他footer、返回链接（如"← 返回深度调研首页"、"← 返回AI洞察首页"之类的文字导航）、版本号、打印按钮等。深度调研报告是长页面阅读体验，左侧已有锚点目录，不需要额外的页面跳转导航链接。

### 文件输出
```
../AI-Insight/02-deep-research/
├── trends/
│   └── 研究标题.md
├── companies/
│   └── 公司名称.md
├── people/
│   └── 人物名称.md
└── topics/
    └── 专题名称.md
```

---

## Step 5.5: 双版本同步（P0 强制步骤）

> **v2.6 新增 (2026-04-06)**
> **教训**: meta-skill-system-2026.html 被直接推送到外部仓库，绕过脱敏管道。
> 导致：(1) 外部版包含"林克"敏感词；(2) 内部版缺失该文件；(3) 首页引用不一致。
> **根因**: 深度调研工作流没有强制的双版本同步步骤，外部版同步是"可选"的。

### 操作步骤

1. **确认内部版文件已保存**
   - 报告 HTML 位于 `02-deep-research/[category]/[filename].html`
   - 内部版首页 `index.html` 已更新（如果 Step 6 在前则此处先完成）

2. **手动复制报告文件到 public/ 并执行全量同步**

   > ⚠️ `sync_to_public.py` **不接受** `--deep-research` 等参数（会报 `unrecognized arguments`）。
   > 深度调研文件需要先手动 cp，再运行脚本做全量同步和脱敏验证。

   ```bash
   # 1. 手动复制报告文件到 public/
   cp AI-Insight/02-deep-research/[category]/[filename].html \
      AI-Insight/public/02-deep-research/[category]/[filename].html

   # 2. 运行全量同步（含日报 + 首页脱敏 + 验证）
   cd AI-Insight && python3 scripts/sync_to_public.py 2>&1
   ```

3. **验证 public/ 中已生成脱敏版本**
   - 检查 `public/02-deep-research/[category]/[filename].html` 存在
   - 确认敏感词零残留（脚本 `--verify` 自动检查）

4. **推送到外部仓库**
   ```bash
   cd AI-Insight && python3 scripts/sync_to_external.py --full --verify
   ```

### 红线规则

- **禁止直接向外部仓库推送内容**（必须通过 sync_to_public.py 脱敏管道）
- **禁止跳过此步骤**（完成摘要表格中"双版本同步"必须为 ✅）
- **禁止 raw cp**（会泄漏未脱敏内容）
- **⛔ 禁止用 public/index.html 覆盖根目录 index.html**（v2.7新增 — 经验#65）
  - public/ 是脱敏版，反向覆盖会污染内部版
  - 内部版 header 必须保留「林克的AI洞察」
  - 同步方向固定：内部版 → public/ → 外部仓库，永不反向
- **⛔ sync_to_public.py 会用 public/index.html 的旧内容覆盖内部版新增的首页卡片**（v2.8新增 — 2026-04-25踩坑）
  - `sync_to_public.py` 的 `preserve_block` 机制会保留 public/index.html 中的深度调研区块，即使内部版 index.html 已新增卡片
  - **正确做法**：Step 6 修改首页卡片后，必须同时修改内部版 `AI-Insight/index.html` 和公开版 `AI-Insight/public/index.html`
  - 运行 `sync_to_public.py --full --force` 同步报告文件后，手动验证 `public/index.html` 是否包含新卡片：
    ```bash
    grep -c "new-report-filename" AI-Insight/public/index.html  # 应 ≥1
    ```

### ⛔ 部署后必须验证线上 URL（v2.8新增 — 2026-04-25踩坑）

> **教训**：sync_to_external.py 脚本输出的"外部版本"URL 写的是 `ai-insight/`，但实际仓库是 `ai-insight-public/`，两者不同。
> 不验证线上就关闭流程，会导致 KIM 卡片按钮链接 404。

**正确验证命令**（Step 5.5 完成后必做）：
```bash
# 验证深度调研报告页
curl -s -o /dev/null -w "%{http_code}" \
  "https://xiaoxiong20260206.github.io/ai-insight-public/02-deep-research/[category]/[filename].html"
# 期望结果：200

# 验证首页
curl -s -o /dev/null -w "%{http_code}" \
  "https://xiaoxiong20260206.github.io/ai-insight-public/"
# 期望结果：200
```

**正确 URL 格式（双仓两端均需验证）**：

| 端 | URL |
|---|---|
| ✅ 内部版报告 | `https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/[category]/[filename].html` |
| ✅ 内部版首页 | `https://xiaoxiong20260206.github.io/ai-insight/` |
| ✅ 外部版报告 | `https://xiaoxiong20260206.github.io/ai-insight-public/02-deep-research/[category]/[filename].html` |
| ✅ 外部版首页 | `https://xiaoxiong20260206.github.io/ai-insight-public/` |

> ⚠️ `sync_to_external.py` 脚本末尾输出的 URL 有时写的是 `ai-insight/`（内部版），容易与外部版混淆。两端都需要单独验证。

### ⛔ 双仓发布规则（v2.9新增 — 2026-04-25踩坑）

> **教训**：深度调研 HTML 文件和首页卡片变更，只运行 `sync_to_external.py` 推送了外部版（`ai-insight-public`），
> 却忘记对内部版主仓库（`ai-insight.git`）做 `git add + commit + push`，
> 导致内部版 GitHub Pages 页面 404，首页卡片链接也死链。

**两个仓库的职责**：

| 仓库 | 路径 | GitHub Pages | 职责 |
|---|---|---|---|
| `ai-insight.git` | `个人助理_V1/AI-Insight/` | `xiaoxiong20260206.github.io/ai-insight/` | 内部完整版（含林克字样） |
| `ai-insight-public.git` | `个人助理_V1/ai-insight-public/` | `xiaoxiong20260206.github.io/ai-insight-public/` | 外部脱敏版（KIM卡片链接用这个） |

**Step 5.5 + Step 6 完成后必须同时提交两个仓库**：

```bash
# 步骤 A: 内部版主仓库提交（通常被遗忘！）
cd AI-Insight
git add 02-deep-research/[category]/[filename].html index.html
git commit -m "feat: 新增 [报告名称] 深度调研报告 + 首页卡片入口"
git push origin main

# 步骤 B: 外部版同步（sync_to_external 已在 Step 5.5 执行）
# 通过 sync_to_external.py --full --verify 完成，无需手动 push ai-insight-public
```

> 💡 记忆口诀：**sync 推外部，push 推内部**，两步缺一不可。

### ⛔ public/index.html 和外部版首页卡片必须手动同步（v3.0新增 — 2026-04-25踩坑）

> **教训（经验#59）**：Step 6 在内部版 `AI-Insight/index.html` 新增了卡片，但：
> 1. `AI-Insight/public/index.html` —— `sync_to_public.py` 有 `preserve_block` 机制，**不会覆盖**公开版里的深度调研区块，新卡片不会被自动同步进去。
> 2. `ai-insight-public/index.html` —— 独立仓库，**不会**跟随 AI-Insight 主仓库自动更新。
>
> **结果**：两个首页的深度调研列表没有新卡片，用户从首页找不到新报告（等于未发布）。
>
> **根因**：文档（v2.8）只说"必须同时修改内部版和公开版"，但没有**检查命令**和**门控验证步骤**，容易被遗漏。

**Step 5.5 完成后，必须执行四端首页卡片检查（P0门控）**：

```bash
REPORT_SLUG="[filename-without-ext]"

echo "=== 四端首页卡片检查 ==="
echo "[1] 内部版 AI-Insight/index.html"
grep -c "$REPORT_SLUG" AI-Insight/index.html && echo "✅" || echo "❌ 缺失！"

echo "[2] 公开版 AI-Insight/public/index.html"
grep -c "$REPORT_SLUG" AI-Insight/public/index.html && echo "✅" || echo "❌ 缺失！"

echo "[3] 外部仓库 ai-insight-public/index.html"
grep -c "$REPORT_SLUG" ai-insight-public/index.html && echo "✅" || echo "❌ 缺失！"
```

**四端卡片同步操作顺序**：
1. Step 6：修改 `AI-Insight/index.html`（内部版首页）— 新增卡片
2. **手动同步**：将同一卡片（脱敏版，去掉林克/沈浪）写入 `AI-Insight/public/index.html`
3. **手动同步**：将同一卡片（脱敏版）写入 `ai-insight-public/index.html`
4. 运行四端检查命令确认全部 ≥1
5. 再执行 push（先内部版，再外部版）

**外部版卡片脱敏要点**：
- 不含"林克"字样（tag/desc/title 均需检查）
- 不含"沈浪"字样
- 不含"快手"字样
- "最新"tag（红色标签）保留

**反模式**：
> ❌ 只更新 `AI-Insight/index.html`，以为 sync 脚本会自动传播 → **不会传播**
> ❌ 以为 `sync_to_external.py` 也会更新 `ai-insight-public/index.html` 的卡片 → **只同步报告HTML文件，不修改首页卡片**

### 反向覆盖检测（v2.7新增）

Step 5.5 完成后，必须执行以下检测：

```bash
# 检查内部版 header 完整性
grep -c "林克" index.html
# 输出应 ≥1，若=0则说明内部版被污染

# 若被污染，从最近正确commit恢复
git log --oneline -5 -- index.html
git checkout [correct-commit] -- index.html
```

---

## Step 6: 首页同步（P0 强制步骤）

> **规则**: 每次新增或更新深度调研页面后，**必须**同步更新根目录 `index.html` 的"深度调研"Tab 对应位置。
> 此步骤为 P0 强制步骤，不可跳过。

### 同步操作
1. 打开根目录 `index.html`，定位到 `<!-- 2. 深度调研 -->` 区域
2. 根据调研类型，在对应分类（趋势洞察/公司调研/专题调研）的 `content-grid` 中**新增卡片**
3. 新卡片放在该分类列表**最前面**（最新优先）
4. 卡片模板：
```html
<a href="02-deep-research/[类型]/[目录或文件]" target="_blank" class="content-card">
    <div class="content-card-header">
        <span class="content-card-icon">[emoji]</span>
        <span class="content-card-title">[标题]</span>
        <span class="content-card-tag green">NEW</span>
    </div>
    <div class="content-card-desc">[一句话描述]</div>
    <div class="content-card-meta">📅 [日期] · [标签]</div>
</a>
```
5. 本地预览验证卡片显示正确且跳转正常
6. 提交并推送到 GitHub Pages，线上验证

### 为什么是 P0
- 首页是用户发现调研内容的**唯一入口**
- 不同步 = 调研产出无法被访问 = 等于没做
- 历史教训：多次调研完成后忘记更新首页，导致数据漂移

---

## Step 7: KIM推送（深度调研卡片）

> **场景**: 深度调研完成并部署后，通过KIM卡片分享给群/个人。
> **⚠️ P0红线**: 必须使用 mixCard 卡片，禁止纯文本降级。凭证缺失时走 mixCard 路径。

### 推送双路径

**路径A（推荐）：mixCard 通过 message 工具**
```bash
python3 scripts/build_insight_mixcard.py research --slug <slug> --output /tmp/card.json
# 然后用 message(channel=kim, kimMixCard=<card>, ...) 发送
# 或: python3 scripts/build_insight_mixcard.py product --output /tmp/card.json (产品本质研究)
```

**路径B（旧版）：直连 KIM API**
```bash
python3 scripts/send_deep_research_card.py --preview  # 预览
python3 scripts/send_deep_research_card.py --to-groups # 发群
```

> **依赖**: 路径B需先加载 `ks-linke-kim-message` 技能获取凭证和发送能力。路径A不需要额外凭证。

### 卡片结构（标准模板）

深度调研KIM卡片的标准Block布局：

```
┌─────────────────────────────────┐
│ # 🔬 AI洞察 · 深度调研          │  ← title (kimMd)
│ **[调研主题名称]**               │  ← subtitle (kimMd)
│ 📅 YYYY-MM-DD（周X）            │  ← date (kimMd)
├─────────────────────────────────┤  ← divider
│ 💬 **林克的分享背景**             │  ← background (kimMd)
│ [用林克口吻写2-3句话，说明      │
│  为什么分享这个调研、价值在哪]    │
├─────────────────────────────────┤  ← divider
│ 👤 **人物/主体介绍**（如适用）    │  ← who (kimMd)
│ [被调研对象的关键背景信息]       │
├─────────────────────────────────┤  ← divider
│ 💡 **核心发现**                  │  ← highlights (kimMd)
│ 🔹 发现1: 一句话摘要            │
│ 🔹 发现2: 一句话摘要            │
│ 🔹 发现3: 一句话摘要            │
│ 🔹 发现4: 一句话摘要            │
├─────────────────────────────────┤  ← divider
│ 🎯 **核心结论**                  │  ← conclusion (kimMd)
│ [一段话总结核心洞察]             │
├─────────────────────────────────┤  ← divider
│ 🧠 **林克的本质洞察**              │  ← insight (kimMd) ⬅️ 新增默认模块
│ [本质规律 + 类比 + 趋势推演]       │
├─────────────────────────────────┤  ← divider
│ 🤖 *林克（沈浪的AI分身）· AI洞察* │  ← footer (kimMd)
│ [📄 查看完整解读 >>] [💡 了解AI洞察项目] │  ← buttons (action, layout: two)
└─────────────────────────────────┘
```

### Block清单（JSON结构）

```python
blocks = [
    # 1. 标题
    {"blockId": "title", "type": "content",
     "text": {"type": "kimMd", "content": "# 🔬 AI洞察 · 深度调研"}},

    # 2. 副标题（调研主题）
    {"blockId": "subtitle", "type": "content",
     "text": {"type": "kimMd", "content": "**[调研主题名称]**"}},

    # 3. 日期
    {"blockId": "date", "type": "content",
     "text": {"type": "kimMd", "content": "📅 YYYY-MM-DD（周X）"}},

    # 4. 分割线
    {"blockId": "d1", "type": "divider"},

    # 5. 林克分享背景（核心亮点，用林克口吻）
    {"blockId": "bg", "type": "content",
     "text": {"type": "kimMd",
              "content": "💬 **林克的分享背景**\n\n[用林克口吻写2-3句话，说明调研来源、为什么值得分享、核心价值点]"}},

    # 6. 分割线
    {"blockId": "d2", "type": "divider"},

    # 7. 被调研对象介绍（人物/公司/产品，可选）
    {"blockId": "who", "type": "content",
     "text": {"type": "kimMd",
              "content": "👤 **[人物/公司名]**\n[身份]\n[关键标签，用 · 分隔]"}},

    # 8. 分割线
    {"blockId": "d3", "type": "divider"},

    # 9. 核心发现（3-5条，用🔹列表）
    {"blockId": "highlights", "type": "content",
     "text": {"type": "kimMd",
              "content": "💡 **核心发现**\n\n🔹 **发现1标题**: 一句话摘要\n🔹 **发现2标题**: 一句话摘要\n🔹 **发现3标题**: 一句话摘要\n🔹 **发现4标题**: 一句话摘要"}},

    # 10. 分割线
    {"blockId": "d4", "type": "divider"},

    # 11. 核心结论
    {"blockId": "conclusion", "type": "content",
     "text": {"type": "kimMd",
              "content": "🎯 **核心结论**\n\n[一段话总结，包含关键观点和行动建议]"}},

    # 12. 分割线
    {"blockId": "d5", "type": "divider"},

    # === 林克本质洞察（所有卡片默认模块，见 linke-kim-message SKILL.md） ===
    {"blockId": "insight", "type": "content",
     "text": {"type": "kimMd",
              "content": "🧠 **林克的本质洞察**\n\n"
                         "[表面→本质: 一句话点明底层规律]\n\n"
                         "[类比: 用一个生活化类比帮助理解]\n\n"
                         "[趋势推演: 基于这个规律，往前看会发生什么]"}},

    # 分割线
    {"blockId": "d6", "type": "divider"},

    # 13. 林克签名
    {"blockId": "footer", "type": "content",
     "text": {"type": "kimMd", "content": "🤖 *林克（沈浪的AI分身）· AI洞察*"}},

    # 14. 双按钮（P0惯例：按钮1=当期内容，按钮2=了解AI洞察项目）
    {"blockId": "buttons", "type": "action",
     "actions": [
         {"type": "button",
          "text": {"type": "plainText", "content": "📄 查看完整解读 >>"},
          "style": "green",
          "url": "[深度调研页面URL]"},
         {"type": "button",
          "text": {"type": "plainText", "content": "💡 了解AI洞察项目"},
          "style": "blue",
          "url": "https://[GITHUB_USER].github.io/ai-insight-public/"}
     ],
     "layout": "two"}
]
```

### 内容撰写规范

**分享背景（bg block）写作要求**：
- 用林克的口吻（第一人称）
- 说明调研的来源/背景（如"上周我们XX部门请到了..."）
- 点出核心价值（如"12人团队干出50人的活，这个效率很值得研究"）
- 2-3句话，不要太长

**核心发现（highlights block）写作要求**：
- 3-5条，每条一行
- 每条格式: `🔹 **关键词**: 一句话摘要`
- 从调研报告的核心发现中提炼，不照搬原文
- 信息量要足，避免过于笼统

**核心结论（conclusion block）写作要求**：
- 一段话，2-3句
- 包含核心判断 + 关键前提/建议
- 加粗关键词

### URL规则（P0）

> ⚠️ **v2.8 关键修正（2026-04-25踩坑）**：KIM 卡片按钮使用**外部公开版 URL**，而非内部版！
> 内部版（`ai-insight/`）是 GitHub Pages 私有部署，外部用户访问可能返回 404。
> **必须用 `ai-insight-public/`**（这是公开仓库，所有外部用户均可访问）。

- **按钮1 URL（报告链接）**: 使用**外部公开版**，`https://[GITHUB_USER].github.io/ai-insight-public/02-deep-research/topics/xxx.html`
  - ❌ 错误：`https://[GITHUB_USER].github.io/ai-insight/...`（内部版，群成员访问可能404）
  - ✅ 正确：`https://[GITHUB_USER].github.io/ai-insight-public/...`
- **按钮2 URL（首页链接）**: 也使用**外部公开版首页**，`https://[GITHUB_USER].github.io/ai-insight-public/`
- **⛔ 禁止使用内部版 `ai-insight/` 链接放入群发卡片**（内部版仅用于开发调试和自检）
- **禁止使用跳转页URL**（KIM WebView不支持meta refresh）
- **禁止使用#占位符**
- **⛔ P0 验证**：每次生成 KIM 卡片脚本后，必须先用 `--preview` 私发预览，自己在 KIM 里点击按钮验证链接 200，再群发

### 默认推送群（v2.6 沈浪确认，2026-04-05）

> 深度调研卡片的默认推送目标为以下 **3 个群**，后续所有深度调研推送直接发这3群，无需每次确认。

| 群名 | groupId | 人数 |
|------|---------|------|
| 研发效能中心全员群 | `3705455482343722` | 135 |
| 【AI生产力】MyFlicker产研 | `6724050835415361` | 50 |
| 【L5项目】研发线AI-Ready | `6646213728505891` | 48 |

```python
# 深度调研卡片默认推送群列表（已由用户确认）
DEFAULT_DEEP_RESEARCH_GROUPS = [
    {"groupId": "3705455482343722", "name": "研发效能中心全员群"},
    {"groupId": "6724050835415361", "name": "【AI生产力】MyFlicker产研"},
    {"groupId": "6646213728505891", "name": "【L5项目】研发线AI-Ready"},
]
```

### 发送流程

```python
import sys
sys.path.insert(0, 'scripts')
from kim_client import KimConfig, get_access_token, send_to_user, send_to_group_with_retry
import asyncio

async def send_deep_research_card(card: dict):
    token = await get_access_token()

    # Step 1: 先私发给沈浪预览
    print("发送预览给 shenlang...")
    await send_to_user(token, "shenlang", card)
    print("✅ 预览已发送，请在 KIM 中查看")

    # Step 2: 用户确认后，发送到默认3个群
    for g in DEFAULT_DEEP_RESEARCH_GROUPS:
        print(f"  发送到: {g['name']} ...", end=" ", flush=True)
        ok = await send_to_group_with_retry(token, g["groupId"], g["name"], card)
        print("✅" if ok else "❌")
        await asyncio.sleep(1.5)  # 限流保护，间隔 >= 1.5s

asyncio.run(send_deep_research_card(card))
```

**P0规则**：
- 深度调研卡片**必须先发给用户预览**，确认后再发群
- 群发间隔 >= 1.5秒（防限流）
- 限流(42900)不自动重试，报告给用户确认
- **默认发 3 个群**（见上表），用户未另行指定时直接发这3群，无需等待确认

### 实战示例（Pine AI 深度调研卡片）

```python
# Pine AI 深度调研卡片 — 2026-03-13 实际使用
blocks = [
    {"blockId": "title", "type": "content",
     "text": {"type": "kimMd", "content": "# 🔬 AI洞察 · 深度调研"}},
    {"blockId": "subtitle", "type": "content",
     "text": {"type": "kimMd", "content": "**Pine AI 创业实践与 AI 原生开发范式**"}},
    {"blockId": "date", "type": "content",
     "text": {"type": "kimMd", "content": "📅 2026-03-13（周三）"}},
    {"blockId": "d1", "type": "divider"},
    {"blockId": "bg", "type": "content",
     "text": {"type": "kimMd",
              "content": "💬 **林克的分享背景**\n\n上周我们主站技术部请到了 Pine AI 创始人李博杰做了一场深度技术对话（约2万字文字稿）。这是我见过的关于「AI 原生团队到底怎么建」最接地气的一手实践分享。没有空洞的理论，全是真金白银的踩坑经验 —— 12 人团队干出 50 人的活，这个效率很值得研究。我结合外部公开资料做了一份深度解读，分享给大家。"}},
    {"blockId": "d2", "type": "divider"},
    {"blockId": "who", "type": "content",
     "text": {"type": "kimMd",
              "content": "👤 **李博杰**（Dr. Bojie Li）\nPine AI 首席科学家 / 联合创始人\n中科大少年班 · MSRA博士 · 华为天才少年"}},
    {"blockId": "d3", "type": "divider"},
    {"blockId": "highlights", "type": "content",
     "text": {"type": "kimMd",
              "content": "💡 **核心发现**\n\n🔹 **概念完整性革命**: 1人+AI 端到端完成，消灭沟通损耗，效率提升 5-10x\n🔹 **架构师不可替代**: 隐性约束、历史坑点，这些只有人知道\n🔹 **三类未来人才**: 0→1创造者、1→100维护者、前沿竞赛者\n🔹 **先Plan后Code**: 确认架构再交AI写代码，禁止AI修改测试用例"}},
    {"blockId": "d4", "type": "divider"},
    {"blockId": "conclusion", "type": "content",
     "text": {"type": "kimMd",
              "content": "🎯 **核心结论**\n\nAI时代的核心竞争力是 **context**，最佳工作模式是 **1人 + N个AI Agent** 的 virtual team。关键前提：文档化、沙盒化、evaluation体系完善。"}},
    {"blockId": "d5", "type": "divider"},
    {"blockId": "footer", "type": "content",
     "text": {"type": "kimMd", "content": "🤖 *林克（沈浪的AI分身）· AI洞察*"}},
    {"blockId": "buttons", "type": "action",
     "actions": [
         {"type": "button",
          "text": {"type": "plainText", "content": "📄 查看完整解读 >>"},
          "style": "green",
          "url": "https://[GITHUB_USER].github.io/ai-insight-public/02-deep-research/topics/pine-ai-native-team.html"},
         {"type": "button",
          "text": {"type": "plainText", "content": "💡 了解AI洞察项目"},
          "style": "blue",
          "url": "https://[GITHUB_USER].github.io/ai-insight-public/"}
     ],
     "layout": "two"}
]
```

---

## 质量标准

- [ ] 研究问题明确且有价值
- [ ] 信息来源多元且可靠
- [ ] 洞察有数据支撑
- [ ] 分析有深度，不只是信息堆砌
- [ ] 建议具体可执行
- [ ] 所有引用注明来源
- [ ] **（P0）HTML使用清爽调研报告风格**
- [ ] **（P0）Tab 导航按钮使用 SVG icon，禁止 emoji 图标（逐项对照 tab-icon+tab-label 分离结构）**
- [ ] **（P0）首页已同步更新深度调研卡片入口**
- [ ] **（P0）线上已验证首页入口可用且跳转正常**
- [ ] **（P0）完成摘要表格已输出并逐项确认**
- [ ] **（P0）KIM卡片使用标准深度调研模板（双按钮+分享背景+核心发现+本质洞察）** ← 详见本文件 Step 7
- [ ] **（P0）底部"了解更多"模块使用统一模板（含林克介绍+首页按钮）** ← 详见 `references/footer-template.md`
- [ ] **（P0）双版本同步已完成（内部版 + public脱敏版 + 外部仓库）** ← Step 5.5
- [ ] **（P0）外部版敏感词零残留验证通过**

---

## ⚡ 完成摘要（P0强制输出）

> **教训**: 2026-03-10纳瓦尔深度调研任务，完成了调研分析但遗漏了生成HTML页面步骤，被用户纠正后补充。
> **根因**: 只关注核心产出物是否完成，忽略了技能定义的完整工作流。
> **预防**: 深度调研完成后**必须**输出以下完成摘要表格，逐项打勾确认。

```markdown
| 步骤 | 状态 |
|------|------|
| 调研分析（核心内容完成） | ✅ |
| 生成HTML页面（清爽调研报告风格） | ✅ |
| 底部"了解更多"模块符合统一模板 | ✅ |
| 更新首页深度调研Tab | ✅ |
| 部署（git push） | ✅ |
| 双版本同步（P0强制，不允许跳过） | ✅ |
| KIM私发预览给 shenlang | ✅ / ⏭️ 用户未要求 |
| KIM群发到默认3群（研发效能全员/MyFlicker产研/AI-Ready） | ✅ / ⏭️ 用户未要求 |
| KIM Doc 文章生成（如需） | ✅ / ⏭️ 用户未要求 |

📎 页面地址: [内部版链接]
📎 线上地址: [GitHub Pages链接]
```

**规则**:
1. **P0阻断**: 未输出完成摘要表格，不得声称任务完成
2. **逐项确认**: 每个步骤必须是✅或⏭️（合理跳过），不能是"待完成"
3. **链接必填**: 页面地址必须填写，否则等于没做
4. **双版本同步不可跳过**: "双版本同步"步骤必须为✅，不接受⏭️。教训：2026-04-06 meta-skill事件

---

## 示例研究

### "从AI大神的深度分享看2026年AI的下半场"

**研究问题**: 2026年AI行业的发展趋势是什么？

**信息源**:
- 9位AI领域思想领袖的演讲/博客
- Anthropic、OpenAI官方博客
- 行业报告数据

**核心发现**:
1. Agent是2026年最重要的产品形态
2. 代码审查将被Spec-driven开发取代
3. AI安全与商业化的张力加剧
4. 头部公司形成寡头格局

**输出**: 趋势分析报告 + 行动建议
