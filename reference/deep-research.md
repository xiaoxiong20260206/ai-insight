# AI深度调研执行流程 (v3.0 精简版)

> **版本**: v3.1 (2026-05-14: 新增HTML/KIM Doc/MixCard/修复策略4组P0强制规则，从5-14复盘血的教训沉淀)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前（5条，强制，不读完不能动手）

1. **明确研究问题**: 核心问题+范围边界+预期输出+目标受众，不能模糊
2. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`
3. **读公共规范**: `reference/output-format-spec.md` — 逐条列出关键格式要点（≥10条），确认理解后再动手
4. **读KIM Doc写作标准**: `reference/kim-doc/writing-style.md` — 对照§0.2格式清单逐条确认
5. **读标杆HTML源码**: `02-deep-research/topics/colleague-skill-anti-distill-2026.html` — 提取CSS骨架+导航结构+tab逻辑，确认骨架一致后再填入内容

---

## 研究类型

| 类型 | 目录 | 示例 |
|------|------|------|
| 趋势洞察 | `trends/` | "AI下半场" |
| 公司调研 | `companies/` | "Anthropic深度调研" |
| 人物追踪 | `people/` | "Barry Zhang思想体系" |
| 专题研究 | `topics/` | "AI Agent架构演进" |

---

## 流程总览

```
Step 1: 明确问题 + 多源搜索
Step 2: 信息整合 + 洞察提炼 → 调研MD+HTML
Step 3: 质量自检（HTML≥50KB + 时效性 + 超链接）
Step 4: 双版本同步（P0强制，不可跳过）
Step 5: 首页更新 → update_homepage.py --type weekly
Step 6: KIM推送 → build_insight_mixcard.py research
```

---

## Step 1: 明确问题 + 多源搜索

### 问题定义框架
- **核心问题**: 要回答什么？
- **范围边界**: 包含什么/不包含什么
- **预期输出**: 报告/卡片/行动建议
- **目标受众**: 开发者/管理层/投资人

### 搜索策略
- 海外: tavily-search（3-5轮精准搜索）
- 国内: quark-search + 微信账号搜索
- 学术: `python3 scripts/fetch_arxiv.py`（可选）
- **时间锚定**: 搜索关键词必须含日期（"2026 Q1"/"最近3个月"），禁止泛日期

### 时效性要求
| 内容类型 | 时效窗口 | 风险 |
|---------|---------|------|
| 竞争格局 | ≤3个月 | 遗漏新进入者 |
| 产品功能 | ≤1个月 | 功能已更新 |
| 融资估值 | 最新报道 | 数据差距大 |
| 行业趋势 | ≤3个月 | 趋势已反转 |

---

## Step 2: 信息整合 + 洞察提炼

### HTML实现规则（P0强制）

> ⚠️ 历史上因不遵守这些规则导致页面白屏、布局错误、反复修改8+轮。以下每条都是血的教训。

**标杆文件**：`02-deep-research/topics/colleague-skill-anti-distill-2026.html`
**所有深度调研HTML必须完全复制标杆的CSS+JS骨架，只替换body内容区域（hero标题+nav按钮+各tab-pane内容+了解更多模块）。**

1. **布局结构**：`editorial-hero → sticky nav-wrap → tab-pane`。❌禁止sidebar布局、❌禁止任何非标杆结构
2. **导航按钮数量**：≤7个。按钮文案简洁无emoji无编号（如"正在发生什么"而非"01 同质化"）
3. **animate-on-scroll规则**：所有元素**默认opacity:1（可见）**。Observer只做动画增强（入场渐显），❌绝对禁止用Observer控制可见性（会导致切换tab后白屏）
4. **tab切换逻辑**：切换tab时，新tab内容必须立即可见，不依赖Observer触发
5. **CSS来源**：从标杆HTML提取完整CSS+JS，不自己发明CSS变量或布局系统
6. **了解更多模块**：直接复制标杆的HTML格式（林克介绍+首页按钮），❌禁止手写格式
7. **脱敏**：外部版必须运行`sync_to_external.py`自动脱敏，❌禁止手动脱敏（遗漏率极高）
8. **文件大小**：≥50KB。不够时补充案例扩充+数据表格+词汇表，不靠空行撑

### KIM Doc实现规则（P0强制）

1. **写前必须读**：`reference/kim-doc/writing-style.md` 逐条对照§0.2格式清单
2. **图片机制**：Docs push API不支持CDN URL图片自动转换。KIM Doc图片必须：
   - 方法A：push MD后，在Docs编辑器手动插入图片（推荐）
   - 方法B：先pull获取已有is-docsfile签名URL，替换到MD中再push
   - ❌禁止：在push的MD里直接写`![描述](cdnfile链接)`——不会被渲染
3. **表格格式**：分隔线`| --- |`后直接跟内容行，❌禁止加空行`| | | |`（KIM Doc会渲染出多余空行）
4. **配图位置**：章节末尾（下个`#`标题前），包括📖引子也需要配图。❌不是标题前面
5. **段落间距**：全文0空行紧凑排版，❌不用`---`分割线
6. **加粗**：几乎不加粗，让📌做标识。❌禁止大量`**加粗**`
7. **📌格式**：`📌 纯文本`，❌禁止`📌 **加粗**`

### MixCard实现规则（P0强制）

1. **必须用脚本生成+校验**：`python3 scripts/build_insight_mixcard.py research --slug <slug> --title ... --subtitle ...`
2. **如果脚本不支持所需内容**：先扩展脚本参数，再生成。❌禁止手写MixCard JSON绕过脚本
3. **按钮URL**：绿按钮指向报告HTML页面，蓝按钮指向AI洞察首页`https://xiaoxiong20260206.github.io/ai-insight/`
4. **推送时不传message字段**（会导致{{message}}泄露）

### 修复策略（P0强制）

1. **修复用edit精确手术**：定位到具体行/具体文本做替换。❌禁止用write重写整个文件（风险：丢失内容、子agent超时、引入新bug）
2. **只有结构彻底不对时才重写**：且必须先读标杆源码，提取骨架后再填入内容
3. **子agent不适合50KB+HTML生成**：大文件直接在主会话用write/edit工具，不依赖子agent

### 生成文件
- `02-deep-research/<type>/<slug>.md`（Markdown）
- `02-deep-research/<type>/<slug>.html`（HTML，≥50KB）
- `02-deep-research/<type>/<slug>-kimdoc.md`（KIM Doc版本）

### ⚠️ KIM Doc写作标准（必须先读！）
**写KIM Doc之前，必须先读 `reference/kim-doc/writing-style.md`！**

核心格式规律（从沈浪修改定稿版学习）：
1. 标题两行：`# 【林克的AI洞察】主标题` + `## 副标题`
2. 封面大图在标题+Web链接后面（高密度信息大图，一张图看清核心）
3. 章节配图在章节末尾（下个`#`标题前），包括📖引子也需要配图
4. 全文0空行紧凑排版，不用`---`分割线
5. 几乎不加粗，让📌做标识
6. 📌格式：`📌 纯文本`（不加粗）
7. 每个章节必须有副标题：`# 01 主标题——副标题`
8. 配图描述有信息量：`![三件事正在同质化：收敛趋势]`
9. 了解更多一条链接即可（文章专题）
10. 表格分隔线后直接跟内容，不要加空行 `| | | |`
11. **URL格式**：Web交互版链接用外部版域名 `ai-insight-public`，slug不含冗余词（如 `-deep-research-2026`）

### 洞察提炼框架
1. **现象层**: 行业正在发生什么？
2. **规律层**: 底层驱动力和模式是什么？
3. **映射层**: 这个规律如何映射到我们的场景？
4. **演变层**: 未来可能怎么发展？
5. **行动层**: 我们应该做什么？

### 禁止项
- ❌ 禁止 `docs.corp.kuaishou.com` 内部链接
- ❌ 禁止外部版含"林克/沈浪/快手/Kuaishou"等敏感词
- ❌ 外部版深度调研链接文案="深度调研"，不加"完整版"

---

## Step 3: 质量自检

| 检查项 | 标准 | 失败处理 |
|--------|------|---------|
| HTML ≥50KB | ≥50000字节 | 补充技术词汇表/宏观叙事 |
| 时效性 | 关键信源≤3个月 | 重新搜索最新数据 |
| 超链接 | 来源都有 `<a href>` | 补充URL |
| 无内部链接 | 无 docs.corp.kuaishou | 删除 |
| 脱敏完整性 | 外部版零敏感词 | 运行sync脱敏 |

---

## Step 4: 双版本同步（P0强制）

**⚠️ 此步骤不可跳过！历史上多次因跳过导致外部版含敏感词。**

```bash
# 1. 同步到public/（内部版保留林克）
python3 scripts/sync_to_public.py --full --force

# 2. 同步到外部版（自动脱敏+验证零敏感词）
python3 scripts/sync_to_external.py --full --verify

# 3. Git push内部版+外部版
git add -A && git commit -m "📚 深度调研 <slug>" && git push origin main
cd ../ai-insight-public && git add -A && git commit -m "📚 深度调研 <slug> (public)" && git push origin main
```

---

## Step 5: 首页更新

```bash
python3 scripts/update_homepage.py <date> --type weekly \
  --week-title "深度调研·<title>" \
  --week-desc "<一句话描述>" \
  --week-month YYYY-MM --week-day DD
```

---

## Step 6: KIM推送

```bash
python3 scripts/build_insight_mixcard.py research --slug <slug> --output /tmp/card.json --with-summary
# 然后读取 card.json，用 message(channel=kim, kimMixCard=<card>) 发送
```

---

_更新于 2026-05-14 · v3.1 · 新增4组P0强制规则（从5-14复盘沉淀）_