# AI深度调研执行流程 (v3.0 精简版)

> **版本**: v3.0 (2026-05-11: 精简版)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前（2条）

1. **明确研究问题**: 核心问题+范围边界+预期输出+目标受众，不能模糊
2. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`

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

_更新于 2026-05-11 · v3.0 · 精简版，881行→核心流程_