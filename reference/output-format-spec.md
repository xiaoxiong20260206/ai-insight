# AI洞察输出格式公共规范 (v1.0)

> **版本**: v1.0 (2026-05-11)
> **原则**: 三种输出（HTML网页/KIM卡片/KIM Doc）的公共规范统一在此文件。每个子技能只写差异化部分。
> **使用**: 所有子技能（日报/周报/深度调研）生成输出前，先读此文件了解公共规范，再读对应子技能的差异化部分。

---

## 一、HTML网页公共规范

### 1.1 视觉风格

所有AI洞察HTML统一使用**清爽调研风格**（通过 `qingshuang-research-style` skill 引用）：

**CSS引用关系**：
- **公共层**：CSS变量+基础样式 → `qingshuang-research-style/references/base-styles.css`（动态读取）
- **定制层**：AI洞察项目特有组件样式 → `templates/ai-insight-custom.css`
- **日报生成**：`gen_daily_html.py` 自动合并公共层+定制层
- **首页**：CSS内联在 `<style>` 中，修改时必须对照 qingshuang skill 最新规范同步更新CSS变量

CSS模板：`templates/daily-report-v3.css`（日报/周报共用）

### 1.2 底部"了解更多"模块（P0强制）

**所有HTML页面底部必须包含此模块，格式统一**：

```html
<div style="max-width:100%;margin:0 auto;padding:0 0 48px;">
<div style="background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);
  border:1px solid #E7E5E4;border-radius:14px;padding:24px 28px;
  box-shadow:0 2px 8px rgba(31,35,40,.06)">
  <div style="font-size:16px;font-weight:700;margin-bottom:8px">💡 了解更多</div>
  <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">
    我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是系统化追踪AI行业动态的项目，
    覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。
  </p>
  <a href="{{HOMEPAGE_URL}}" target="_blank"
    style="display:inline-flex;padding:8px 16px;
    background:linear-gradient(135deg,#059669,#10B981);
    color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
    🏠 访问AI洞察首页
  </a>
</div>
</div>
```

> ⚠️ **`{{HOMEPAGE_URL}}` 由脚本自动替换**：内部版=INTERNAL_PAGES_BASE，外部版=EXTERNAL_PAGES_BASE。禁止硬编码具体URL。

| 页面类型 | 模块内容 | 差异 |
|---------|---------|------|
| 日报 | 林克介绍 + 首页按钮 | 无相关资源 |
| 周报 | 林克介绍 + 首页按钮 | 无相关资源 |
| 深度调研 | 林克介绍 + 首页按钮 + 参考来源列表 | 有相关资源 |

### 1.3 文件大小底线

- **所有HTML ≥50KB**（50000字节）。低于此 = 内容缺失，禁止推送
- 验证命令：`wc -c <file>.html`

### 1.4 超链接规则

- 所有来源/引用必须有 `<a href="URL" target="_blank">文字</a>` 格式
- 禁止纯文字来源列（无URL = 不可追溯）
- 禁止 `docs.corp.kuaishou.com` 内部链接出现在任何HTML中
- 外部版深度调研链接文案="深度调研"，不加"完整版"（暗示有内部版本）

### 1.5 禁止项

- ❌ 禁止 {{message}} / {{...}} 占位符出现在HTML中
- ❌ 禁止 `docs.corp.kuaishou.com` 内部链接
- ❌ 禁止外部版含"林克/沈浪/快手/Kuaishou"等敏感词（由sync_to_public.py脱敏）
- ❌ 禁止结构元素（TOC、meta行、章节标签）使用emoji代替图标
- ❌ 禁止 `[text](url)` Markdown语法出现在HTML中（必须转为 `<a>` 标签）
- ❌ 禁止 `href=""` 空链接
- ❌ 禁止在 `.callout`/`.news-card-why`/`.insight-card` 等容器上加 `max-width: 68ch`
- ❌ 禁止在content-inner内给子容器加独立max-width约束（双约束=更窄，子元素跟随父容器宽度）

### 1.6 HTML视觉格式标准（v2.0 · 2026-06-08 升级）

以下标准已在 `gen_daily_html.py` + `gen_weekly_html.py` 中代码化，脚本生成时自动遵循。手工修改HTML时也必须遵守。

#### 1.6.1 SVG icon替代emoji

**原则**：结构元素（导航、meta行、章节标签）用内联SVG，正文内容保留emoji。

| 位置 | ❌ 旧版（emoji） | ✅ 新版（SVG icon） |
|------|----------------|-------------------|
| 侧边栏TOC | `📋 本周概览` | `<svg class="meta-icon">...</svg> 本周概览` |
| Top5 meta日期 | `📅 06/01-06/07` | `<svg class="meta-icon">日历SVG</svg> 06/01-06/07` |
| Top5 meta来源 | `📎 Anthropic Blog` | `<a class="meta-link"><svg>链接SVG</svg> Anthropic Blog</a>` |

SVG icon定义见 `scripts/gen_weekly_html.py` 的 `SVG_ICONS` 字典（12个标准icon）。

#### 1.6.2 Top5卡片视觉层级

```
rank pill (12px/背景色) → 标题 (18px/600) → meta行 (13px/SVG icon) → 正文 (14px/68ch) → 关键判断独立框
```

关键元素：
- meta行用 `news-card-meta` + `<span class="meta-item">` + `<a class="meta-link">`
- 来源URL必须是超链接 `<a class="meta-link" href="URL" target="_blank">`
- 关键判断用 `<div class="judgment-label">关键判断</div>` 而非 `<strong>关键判断</strong>：`

#### 1.6.3 行宽限制（容器vs文字）

- **容器**：`width: 100%`，撑满父宽度（`.callout`, `.news-card-why`, `.insight-card` 等）
- **段落文字**：`max-width: 68ch`，提高可读性（`.news-card-desc`, `.callout > p`, `.insight-card p` 等）
- CSS规则在 `gen_weekly_html.py` 的 `LINE_WIDTH_CSS` 中定义
- **⚠️ W24踩坑**: 在content-inner(max-width:960px)内，子容器不需要再加max-width——双约束=更窄=和上面内容不对齐

#### 1.6.4 概览图/配图位置

- 概览图放在标题**之后**（标签 → 标题 → 概览图），不是之前
- 标题是语义锚点，图片是补充说明

#### 1.6.5 Markdown自清洁（防御性）

- `gen_weekly_html.py` 的 `md_link_to_html()` 函数自动将 `[text](url)` 转为 `<a>` 标签
- `validate_html()` 自动检测HTML中残留的Markdown语法和空href
- 即使JSON输入包含Markdown，输出HTML也能自清洁

#### 1.6.6 Header副标题（定调句）

- **定位**：副标题是"本周一句话定调"，不是badge或meta的附属
- **视觉**：字号13px（比badge小1px），颜色`var(--color-text-muted)`（淡于正文），margin-top:14px（与h1标题拉开间距），letter-spacing:0.01em
- **宽度**：`max-width:100%`（跟随content-inner，不额外限制）
- **⚠️ 禁止**：margin-top<10px（与标题太挤）、字号≥14px（和badge同层级）、max-width<960px（在已有容器内再约束=更窄）

#### 1.6.7 底部模块对齐

- 了解更多外层div：`max-width:100%`（不设独立max-width，跟随content-inner），`padding:0 0 48px`（无水平padding，让内层卡片自定宽）
- doc-footer：`max-width:100%`，跟随content-inner宽度
- **核心原则**：content-inner已有max-width:960px约束，子元素只管内容不管布局宽度

---

## 二、KIM MixCard 公共规范

### 2.1 卡片骨架（所有类型共享）

```json
{
  "config": {"forward": true, "forwardType": 3, "wideSelfAdaptive": true},
  "updateMulti": 1,
  "blocks": [...]
}
```

### 2.2 六锚点（所有类型必须有）

| 锚点 | blockId | type | 说明 |
|------|---------|------|------|
| header | "header" | content | `# 📡/📊/📚/🧠 标题` |
| subtitle | "subtitle" | content | 覆盖范围/板块数简述 |
| footer | "footer" | content | `*林克（沈浪的AI分身）· AI洞察 · 类型*` |
| buttons | "buttons" | action | 绿按钮(当期内容) + 蓝按钮(了解AI洞察项目) |

> ⚠️ 缺少任何一个锚点 = `build_insight_mixcard.py` 自动报错退出

### 2.3 kimMd格式规则

- **所有content block的text必须是 `{"type": "kimMd", "content": "..."}` object**
- ❌ 禁止纯字符串text（必导致卡片渲染异常）
- ❌ 禁止 `{{message}}` / `{{...}}` 占位符
- ❌ 禁止发送MixCard时传 `message` 字段（会导致 {{message}} 泄露）

### 2.4 卡片内容原则

- **结论先行**：每个板块一句话结论 + 关键判断，不是MD全文搬运
- **深度聚焦≤200字**：截断后加 "..."
- **关键判断不截断**：`**关键判断**：...` 必须完整保留
- **10屏纯文本 = 禁止**：卡片是入口不是全文

### 2.5 按钮URL规范

> **⚠️ 链接体系锁定，不再变更**：
> - 内部版：`https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/`（快手内网，SSO）
> - 外部版：`https://xiaoxiong20260206.github.io/ai-insight-public/`（GitHub Pages，公开）
> - ❌ 旧内部版 `xiaoxiong20260206.github.io/ai-insight/` 已废弃
> - 所有脚本URL从 `config.py` SSoT 派生，禁止硬编码

- 绿按钮：当期内容HTML链接（如 `01-daily-reports/2026-05/2026-05-11.html`）
- 蓝按钮：AI洞察首页（私发→内部版URL，群发→外部版URL）
- URL必须以 `http` 开头
- ❌ 禁止404 URL（由脚本 `--verify-urls` 自动校验）

### 2.6 推送P0红线

- MixCard只用 `build_insight_mixcard.py` 生成，❌禁止手写
- mixCard只推一次
- 发MixCard时不传 `message` 字段
- 群发必须用 `target: "space:<groupId>"` 格式
- API报错后先去群确认是否收到，❌不要立即重试

| 类型 | 推送范围 | 禁止 |
|------|---------|------|
| 日报 | 私发订阅者 | ❌群发 |
| 周报 | 发所有群 | 正常 |
| 深度调研 | 私发/按需 | 按需 |

---

## 三、KIM Doc 公共规范

### 3.1 文章结构（所有类型共享）

```
00 全文概览（2-3句话总结核心结论，无引子章节）
01-X 各章节+子章节（每章/每子章节标题后紧跟AI生成配图+论证+数据支撑+来源链接）
最后 林克彩蛋/了解更多
```

详细规范见 `reference/kim-doc/kim-doc.md` 和 `reference/kim-doc/writing-style.md`

**注意**：已废弃📖引子章节，文章直接从00概览开始。

### 3.2 格式规范

- 标题格式：`【林克的AI洞察】<主标题>`
- 来源标注：每个关键论点后标注 `[来源]`
- 禁止内部链接：❌ `docs.corp.kuaishou.com`
- 字数范围：3000-8000字（专题类）/ 8000-15000字（深度调研类）

### 3.3 写作风格（所有类型共享）

- **调研五步法**：正文遵循表象→规律→类比→回验→预测的逻辑推进（详见 `writing-style.md` §0.6）
- **刻刀与画笔**：先删减噪声（刻刀），再增添洞察（画笔）
- **隐喻建造**：复杂概念用日常类比解释（五步法第③步）
- **深度调研聚焦解读和预测**：不含行动清单。专题/周报类可含行动建议
- 详见 `reference/kim-doc/writing-style.md`

### 3.4 章节配图（P0强制，所有类型共享）

> **核心原则**：每个章节（`#`）和子章节（`##`）都必须在标题后紧跟AI生成配图，配图内容与对应章节内容一致。这不是装饰——是信息压缩工具，30秒入口。

**配图位置**：标题后紧跟（最开头），格式为 `![图片描述](CDN链接)`，标题→配图→正文之间0空行。

**章节配图**：
- 一级章节（`#`）：高密度信息图（infographic），用 `designai-Infographic-image` 技能生成
- 二级子章节（`##`）：信息图或概念插画，根据内容复杂度选择
- 彩蛋章节：概念插画风格，用 `designai-generate-image` 技能
- 封面大图：高密度信息图，一张图看清全文核心

**什么是高密度信息大图**：
- 不是插画/不是风景图/不是抽象概念图——是**结构化信息图**（infographic）
- 一张图包含：标题 + 核心结论 + 3-5个关键数据点 + 结构关系（层级/对比/流程/矩阵）
- 读者看完图 = 看完章节80%的信息量
- 图中文字极简化（每个标签2-4个中文字），防止AI生图乱码

**配图生成方式**：`designai-Infographic-image` 技能

**配图质量标准**：
| 标准 | 要求 |
|------|------|
| 信息密度 | 一张图 ≥ 章节3段文字的信息量 |
| 文字可读 | 中文标签≤4字/条，无乱码（生成后必须用read工具检查） |
| 结构清晰 | 层级/对比/流程/矩阵等结构关系一目了然 |
| 风格统一 | 清爽风格（白底+绿强调），与HTML页面风格一致 |
| 尺寸 | 宽度≥800px，适配手机横屏阅读 |

**配图防乱码P0红线**：
1. 中文标签极简：每条2-4字（如"重复输出"、"响应慢"、"成本高"）
2. 结构用英文描述（布局/颜色/层级），中文只做标签
3. 金句≤15字
4. 生成后必须检查：用 `read` 查看图片，确认无乱码再插入
5. 如果首次生图有乱码 → 修改prompt减少中文 → 重生成 → 再检查
6. 最多重试3次，3次后仍有乱码 → 用纯英文标签版本（宁可英文标签也不要乱码中文）

**何时配图**：
| 场景 | 判断 | 必须？ |
|------|------|--------|
| 每个一级章节（`#`） | **必须配1张高密度信息图** | ✅ 必须 |
| 每个二级子章节（`##`） | **必须配1张信息图或概念插画** | ✅ 必须 |
| 概览章节 | 必须配全局概览图（5板块/5痛点/5趋势） | ✅ 必须 |
| 彩蛋/比喻章节 | 必须配比喻插画（用designai-generate-image） | ✅ 必须 |
| 表格已覆盖内容 | **仍然配图**——图和表格是互补而非冗余。图做全局压缩，表格做细节展开 | ✅ 必须 |

> ⚠️ 旧版策略"只有一级章节配图"+"配图在章节末尾"已废弃。新策略：**每个章节和子章节标题后必须紧跟配图**，配图在标题后（最开头），不是章节末尾。

---

## 四、各子技能差异化部分

| 维度 | 日报 | 周报 | 深度调研 |
|------|------|------|---------|
| **HTML结构** | 5板块Tab切换+热度趋势+明日关注+林克自述 | Top5卡片+周度洞察+日报索引+词汇表+宏观叙事 | 五步法论证（表象→规律→类比→回验→预测）+竞争格局+案例+趋势预测 |
| **HTML模板** | `templates/daily-report-v3.css/js` | 清爽调研风格（手动生成） | 清爽调研风格（手动生成） |
| **HTML≥50KB补充** | 已内置充分 | 词汇表+宏观叙事 | 案例扩充+数据表格 |
| **MixCard标题** | `# 📡 AI 日报（日期，星期）` | `# 📊 AI 周报（年第N周，日期范围）` | `# 📚 深度调研·标题` / `# 🧠 AI产品本质研究` |
| **MixCard板块** | 热度趋势+5板块(动态+深度聚焦+关键判断)+林克自述 | Top5+周度洞察+林克洞察 | 核心结论+趋势+原理+来源(可参数化) |
| **MixCard按钮1** | `📄 查看完整日报 >>` | `📄 查看完整周报 >>` | `📄 查看完整报告 >>` |
| **MixCard按钮1URL** | `01-daily-reports/YYYY-MM/YYYY-MM-DD.html` | `01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html` | `02-deep-research/<slug>.html` |
| **KIM Doc触发** | 不生成 | 按需 | 按需（用户明确要求时） |
| **KIM Doc字数** | - | 3000-5000 | 8000-15000 |
| **KIM Doc章节配图** | - | 每章节和子章节标题后1张信息图/插画 | 每章节和子章节标题后1张信息图/插画 |
| **底部模块** | 简化版(无相关资源) | 简化版(无相关资源) | 完整版(含参考来源) |

---

## 五、外部版脱敏规则

所有外部版（ai-insight-public/）必须脱敏，由 `sync_to_public.py` 自动执行：

| 内部词 | 外部词 | 适用范围 |
|--------|--------|---------|
| 林克 | AI洞察 | 首页署名/页脚/介绍 |
| 沈浪 | （删除） | 身份介绍 |
| 快手 | 某公司 | 机构名 |
| Kuaishou | Company | 英文机构名 |
| CodeFlicker | AI IDE | 产品名 |
| KATE | Agent平台 | 产品名 |
| 天策 | 数据平台 | 产品名 |
| 天玑 | 数据分析平台 | 产品名 |
| KwaiBI | BI平台 | 产品名 |
| 小无相功 | 自进化体系 | 方法论名 |
| MyFlicker/myflicker | AI洞察/ai-insight | 平台名 |
| AI分身 | AI洞察 | 身份描述 |
| 让我负责 | （删除） | 身份暗示 |
| link-avatar | ai-insight-logo | 头像文件名 |

> ⚠️ "CF"、"SKILL.md"、"林克"（在CSS类名/文件名中）不是敏感词，不应误报。
> 内部版(public/)包含"林克"是正确行为，不应被敏感词检查误杀。

### 5.1 内外版URL分离（P0 — 2026-06-15 新增）

**根因**：W24周报外部版所有14处链接都指向内部版URL（ai-insight-internal.frontend-cloud），用户点击后从公网跳到内网SSO=体验断裂。根因是手动修改HTML后直接cp到外部仓库，跳过了sync_to_external.py的URL自动替换。

**硬规则**：

| 版本 | 域名 | 所有链接基础URL |
|------|------|----------------|
| 内部版（frontend-cloud） | `ai-insight-internal.frontend-cloud.corp.kuaishou.com` | `INTERNAL_PAGES_BASE` |
| 外部版（GitHub Pages） | `xiaoxiong20260206.github.io/ai-insight-public` | `EXTERNAL_PAGES_BASE` |

**必须替换的范围**：
- ✅ 了解更多按钮的`href`（"访问AI洞察首页"）
- ✅ 日报链接（`01-daily-reports/YYYY-MM/YYYY-MM-DD.html`）
- ✅ 深度调研链接（`02-deep-research/...`）
- ✅ 首页链接
- ✅ 任何`<a>`标签中的`href`包含`ai-insight-internal`的

**禁止**：
- ❌ 手动cp HTML到外部仓库（绕过脚本=URL全错）
- ❌ 外部版包含`ai-insight-internal.frontend-cloud.corp.kuaishou.com`
- ❌ 内部版包含`xiaoxiong20260206.github.io/ai-insight-public`

**正确流程**：
```bash
# 外部版必须走脚本
uv run scripts/sync_to_external.py --full --verify

# 验证：外部版零残留internal URL
grep -c "ai-insight-internal" ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html  # 必须=0
```

---

_更新于 2026-06-15 · v1.2 · 新增§5.1内外版URL分离P0规则+Header副标题规范(1.6.6)+底部对齐(1.6.7)+容器双约束禁止(1.5)_