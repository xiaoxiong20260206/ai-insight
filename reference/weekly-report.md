# AI周报执行流程 (v3.1 精简版)

> **版本**: v3.3 (2026-06-14: 新增踩坑教训+自检强制规则)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前（4条 — 元执行P1保障）

### P1-1: 环境初始化
```bash
export PATH="$HOME/.local/bin:$PATH"
which uv || (curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH")
ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com
```

### P1-2: 技能加载（读完才能动手）
必须**按顺序**读完以下文件后才能执行任何步骤：
1. `SKILL.md`（P0红线9条）
2. `reference/output-format-spec.md`（公共规范：HTML≥50KB+了解更多模块+超链接规则）
3. `reference/weekly-report.md`（本文件：周报6步流程+自检清单）

### P1-3: 踩坑检索
读完本文件「踩坑教训」部分，确认理解：
- W18: 日历正则 `[^}]+` 无法匹配嵌套 `{}` → silent skip → 误判ok
- W22全部6类问题+W24全部4类问题：见踩坑教训部分

### P1-4: 自检声明
执行前输出：`"我已读完SKILL.md+output-format-spec.md+weekly-report.md+踩坑教训，理解9条P0红线，准备执行Step 1"`

1. **确认类型**: 周日出周报，其他出日报。周号计算：`date +%G-W%V`（当前周号，周报cron在周一执行生成当前周的周报）
2. **⚠️ MixCard按钮URL校验**：推送前必须用 `--verify-urls` 确认按钮URL可达（HTTP 200）。如果HTML还没部署完成，不能推送MixCard。

---

## 流程总览

```
Step 1: 读取本周日报 → 日期验证 + URL提取
Step 2: 汇总分析 → Top5 + 洞察 → 周报JSON + MD
Step 3: 生成周报HTML（≥50KB + 来源超链接）— 从JSON自动生成
Step 4: 首页更新 → update_homepage.py --type weekly
Step 5: 部署 + 外部同步 → sync_to_external
Step 6: KIM推送 → build_insight_mixcard.py weekly → message(kimMixCard=inner card, message="")
```

---

## Step 1: 读取本周日报

### 日期计算

```python
from datetime import datetime, timedelta
today = datetime.now()
if today.weekday() == 6:  # 周日
    monday = today - timedelta(days=6)
else:
    monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)
week_num = monday.isocalendar()[1]
```

### 验证清单
- 周一日期是 Monday
- 周日日期是 Sunday
- 周一~周日所有日报文件已定位
- **从日报JSON提取每条新闻的 `url` 字段**（Step 2/3 超链接来源）

---

## Step 2: 汇总分析 → 周报JSON + MD

### ⛔ P0铁律：周报所有新闻条目必须来自本周日报JSON，禁止从训练记忆补充

**时间窗口：周报 = 本周一00:00 ~ 周日23:59 之间的新闻**

- ❌ **禁止**：在周报里加入本周日报中没有的新闻（即使模型"知道"那是真实新闻）
- ❌ **禁止**：把上周或更早的旧新闻以本周日期写入周报
- ❌ **禁止**：用旧URL + 修改日期来凑本周条目
- ✅ **必须**：Step 1 先读取本周一~周日所有 `daily-content-YYYY-MM-DD.json`，提取所有 news 条目（含真实URL）
- ✅ **必须**：Step 2 的 sections.table 每一行的 event/url/date 都要能在某天日报 JSON 里找到对应条目
- ✅ **允许**：Top5描述、洞察分析、pattern_insight 等叙述类内容可自由推理，但不能新增事实性新闻条目

**检验方法**：sections.table 里每条 `date=06-XX` 的条目，必须能在对应 `daily-content-2026-06-XX.json` 里找到相似标题。

### JSON（脚本化输入）
周报内容使用JSON格式输出（约200行），由 `gen_weekly_html.py` 从JSON动态生成HTML。

**JSON生成命令**：
```bash
# 生成空白模板
uv run scripts/gen_weekly_json.py --date YYYY-WXX --template

# LLM填写模板后，验证JSON
uv run scripts/gen_weekly_json.py --date YYYY-WXX --validate
```

### MD（KIM Doc + MixCard源文件）
**⚠️ MD文件必须同时生成** — `build_insight_mixcard.py` 从MD提取Top5+洞察+日期范围。不生成MD → MixCard内容为空 → 推送失败。

MD文件路径：`01-daily-reports/YYYY-MM/weekly-YYYY-WXX.md`

MD内容结构：
- **Top 5**: 5条最重要事件（行业影响力+关注度+趋势信号+数据冲击+政策意义）
- **周度洞察**: 跨板块共同主题 + 趋势强化/反转 + 数据/事件含义（至少2条）
- **林克的洞察**: 独立判断段落
- **日报索引**: 周一到周日所有已有日报
- **技术词汇表**: 8-10条新术语（≥50KB补充）
- **宏观叙事**: 本周主题叙事段落（≥50KB补充）

标题格式必须是 `# 📊 AI 洟察周报 · YYYY年第XX周（MM/DD - MM/DD）` — MixCard从标题提取日期范围。

### 质量规则
- JSON必须通过 `gen_weekly_json.py --validate` 校验
- **table行的event字段必须是纯文本，禁止Markdown语法 `[text](url)`**（#124防复发）
- **table行必须有url字段，且为合法URL**（#124防复发）
- Top5每条source行必须包含超链接（URL来自日报JSON）
- 禁止KIM Doc内部链接（docs.corp.kuaishou.com）
- 外部版深度调研链接文案="深度调研"，不加"完整版"

---

## Step 3: 生成周报HTML（≥50KB）— 从JSON自动生成

**脚本化流程（不再手拼HTML）**：
```bash
# 从JSON生成HTML（自动：CSS模板+JS模板+自校验+cp到public）
uv run scripts/gen_weekly_html.py --date YYYY-WXX --input data/weekly-content-YYYY-WXX.json

# 脏检查：≥50KB + 5板块 + {{message}}=0 + 8个class名 + 了解更多模块 + Markdown泄漏=0 + 空href=0
# 脚本已自动完成，无需手动验证
```

**如果JSON校验或HTML校验失败**：回到Step 2修复JSON内容，重新运行。

### 手动备选方案（脚本不可用时）
- 使用W20的HTML作为CSS/JS模板骨架
- 只替换 `<body>` 内的内容部分
- 禁止自创class名（必须使用映射表中的class名）
- 手动验证：`wc -c *.html` 必须≥50000字节 + 手动cp到public/

---

## Step 4: 首页更新（统一脚本）

```bash
uv run scripts/update_homepage.py YYYY-WXX --type weekly \
  --week-title "第XX周（MM/DD - MM/DD）" \
  --week-desc "覆盖N条资讯 · 事件1 · 事件2" \
  --week-month YYYY-MM --week-day DD
```

---

## Step 5: 部署 + 外部同步

```bash
# 5a. 内部版 git push
git add -A && git commit -m "📊 AI周报 YYYY-WXX" && git push origin main

# ⚠️ gen_weekly_html.py已自动cp周报HTML到public/
# update_homepage.py已自动cp首页到public/
# 只需验证大小一致：
wc -c 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
wc -c index.html public/index.html

# 5b. 外部版同步（自动脱敏+URL替换+push）
# ⛔ 禁止手动cp HTML到外部仓库——必须走脚本，脚本自动做URL替换
# 手动cp = 所有链接都指向内部URL = 外部用户点进去跳SSO = P0违规
uv run scripts/sync_to_external.py --full --verify

# 验证外部版零残留internal URL
grep -c "ai-insight-internal" ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html  # 必须=0

# 5c. 内部版 frontend-cloud 部署（P0 — W24踩坑教训）
# ⚠️ git push只更新GitHub仓库，不触发frontend-cloud部署
# frontend-cloud必须单独部署，否则内部版首页不会更新
cd public && npx -y --registry https://npm.corp.kuaishou.com @codeflicker/frontend-cloud-cli@latest deploy && cd ..
```

### 四位置验证
```
①内部周报(frontend-cloud) ②内部首页(frontend-cloud) ③外部周报(GitHub Pages) ④外部首页(GitHub Pages)
```

> **⚠️ W22踩坑教训**: 修改了 01-daily-reports/ 下的文件但忘了cp到 public/ 对应路径 → Pages返回截断旧版27KB而非完整70KB。public/是Pages部署源，不是可选步骤。

> **⚠️ W24踩坑教训**: 周报cron只执行了git push + sync_to_external，遗漏了frontend-cloud deploy。内部版首页停留在上一版，用户看到旧首页。git push ≠ 网页部署，frontend-cloud必须单独执行。

### Step 5.5: 交付链接（P0 强制 — 每次周报完成必须输出）

周报部署完成后，**必须**输出以下四个链接，方便自检内外版本是否都正确发布：

```
内部版：
1. 📄 本周周报：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
2. 🏠 AI洞察首页：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/

外部版：
3. 📄 本周周报：https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
4. 🏠 AI洞察首页：https://xiaoxiong20260206.github.io/ai-insight-public/
```

> ⚠️ 周报内外版文件名一致（无-v3后缀），URL SSoT = scripts/config.py。

---

## Step 6: KIM推送

```bash
# 1. 生成mixCard（脚本自带6锚点校验+kimMd格式校验）
uv run scripts/build_insight_mixcard.py weekly --date YYYY-WXX --output /tmp/card.json --with-summary

# 2. 先私发预览给 {{OWNER_KIM_USERNAME}}
# message(channel=kim, action=send, kimMixCard=<inner card JSON>, target="{{OWNER_KIM_USERNAME}}", message="")
# ⚠️ kimMixCard必须传inner card格式（{config, blocks, updateMulti}在顶层），禁止传双层{card: {...}}
# ⚠️ message参数必须传空字符串""

# 3. 等沈浪确认后再群发AI生产力中心全员群
# message(channel=kim, action=send, kimMixCard=<inner card JSON>, target="space:3705455482343722", message="")
```

### 推送P0红线
- MixCard只用脚本生成，禁止手写
- 发MixCard时不传 `message` 字段（防{{message}}泄露）
- 群发必须用 `target: "space:<groupId>"` 格式
- preview只执行一次
- API报错后先去群确认是否收到，不要立即重试

### 推送范围
| 类型 | 范围 | 说明 |
|------|------|------|
| 周报 | **先私发预览给{{OWNER_KIM_USERNAME}}** → 确认后再群发AI生产力中心全员群 | ❌禁止不确认就群发 |
| 日报 | 私发订阅者 | ❌禁止群发 |

### 默认推送群
> **2026-05-25 更新**：周报只发到AI生产力中心全员群，不再发其他群。

| 群名 | groupId |
|------|---------|
| AI生产力中心 全员群 | `3705455482343722` |

---

## 交付物（P0强制）

```
📊 周报四链接自检：
🔒 内部版：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
🌐 外部版：https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
🏠 内部首页：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/
🌐 外部首页：https://xiaoxiong20260206.github.io/ai-insight-public/
```

---

## ⚠️ 周报交付强制自检（P0 — 每次执行必须完成）

> **2026-05-18 新增**：W20周报首页日历+外部版同步失败，根因是脚本 silent skip + 验证不覆盖日历/外部版。

周报执行完成后，**必须逐项验证以下清单**，任何一项失败 = hard fail，不能标记任务完成：

| # | 自检项 | 验证方法 | 失败= |
|---|--------|----------|-------|
| 1 | 日历数据包含本周周号 | `grep "weekly-{week_id}" index.html`，必须在 `weeklyReportsData` 行出现 | ❌ hard fail |
| 2 | 内部版首页包含周报链接 | `grep "weekly-{week_id}.html" index.html` | ❌ hard fail |
| 3 | 外部版周报HTML存在 | `ls ai-insight-public/01-daily-reports/{month}/weekly-{week_id}.html` | ❌ hard fail |
| 4 | 外部版首页包含本周周号 | `grep "{week_id}" ai-insight-public/index.html` | ❌ hard fail |
| 5 | 四链接可达 | 逐一访问4个URL确认HTTP 200 | ❌ hard fail |
| 6 | MixCard校验通过 | `build_insight_mixcard.py weekly --date {week_id} --verify` | ❌ hard fail |
| 7 | 外部版零残留internal URL | `grep -c "ai-insight-internal" ai-insight-public/01-daily-reports/{month}/weekly-{week_id}.html` =0 | ❌ hard fail |
| 8 | Header副标题间距≥14px | 检查HTML中副标题div的margin-top | ❌ hard fail |

**重要**：`update_homepage.py` 如果输出 `❌` 或 `⚠️`，等于验证未通过，**不能继续推送**。必须排查并修复后再继续。

---

## 踩坑教训

### 2026-05-18: W20周报首页日历更新失败 + 外部版同步阻塞

**问题**: 周报cron标记ok，但首页日历点击W20不跳转，外部版W20文件缺失。

**根因链**:

1. **`update_homepage.py` 日历正则 `[^}]+` 无法匹配嵌套 `{}`** — 首页 `weeklyReportsData` 的值是 `'2026-05': {4: ..., 11: ...}`，内层 `}` 先被拒绝匹配，正则命中第一个 `}` 就停止。从W18开始日历更新永远被跳过，脚本输出 `⚠️ 未找到weeklyReportsData，跳过周报日历更新` 并返回 True（silent skip）。

2. **`sync_to_public.py` 一致性验证阻塞同步** — `public/02-deep-research/topics/ai-org-moat-v2.html` 是历史残留（内部版不存在），一致性检查 sys.exit(1) 阻塞了整条同步管道，外部版 W20 从未同步。

3. **cron 误判成功** — 脚本 silent skip + 退出码 0 = cron 标记 ok。交付物自检六项 ✅ 但实际日历和外部版都没更新。

**修复**:
- 重写日历更新函数：三策略（非贪婪匹配+月份行直接搜索+已存在快速返回），跳过 = hard fail
- 一致性验证降级为 warning（sys.exit → 打印警告继续）
- 增强验证：检查日历数据+外部版文件+外部首页

**举一反三**:
- **脚本跳过步骤 = hard fail，不能 silent return True** — cron ok ≠ 任务完成
- **四位置验证必须纳入交付物自检** — 不能只检查"文件存在"，还要检查"日历有周号""外部版到位"
- **一致性验证应该是 warning 不是 blocker** — 历史残留不应阻止新内容上线

### 2026-05-25: W22周报6类问题全面复盘

**问题1: cron不按规范执行，直接群发跳过私发确认**
- 根因：cron payload含"只推一次"指令 → agent理解为"一次性推完" → 直接群发大群
- 修复：删除"只推一次"，改为"先私发预览给{{OWNER_KIM_USERNAME}}，不自动群发"，群发是手动步骤
- 举一反三：cron payload措辞必须精确，避免歧义指令

**问题2: 周报HTML CSS和class名不匹配**
- 根因：没有gen_weekly_html.py动态生成脚本 → agent自由拼HTML → 使用了card-badge/top5-card/overview-grid等和CSS不匹配的class名 → 所有样式失效
- 修复：建立class名映射表（news-card/stat-card/insight-card/callout等），强制使用W20一致的class名
- 举一反三：没有脚本化保障的输出=高风险输出，agent自由拼HTML是不可靠的

**问题3: public/目录未同步导致内部版截断**
- 根因：修改了01-daily-reports/下的源文件但没cp到public/对应路径 → Pages从public/部署返回27KB截断旧版
- 修复：Step 5增加强制cp命令+大小验证
- 举一反三：public/是Pages部署源不是可选步骤，每次修改必须同步

**问题4: 首页周报pills链接错误**
- 根因：cron session修改首页pills时全部指向同一个错误URL weekly-2026-05-21.html
- 修复：pills是首页静态HTML，脚本不自动维护（需手动更新或脚本化）
- 举一反三：首页有多个手工维护区域（pills/日历/卡片），脚本只更新部分，其余需明确标注

**问题5: MixCard日期范围错误（05/25-05/31而非05/19-05/25）**
- 根因：build_insight_mixcard.py用ISO当前周号计算日期范围（W22从05/25开始），但周报数据覆盖的是上一周（05/19-05/25）
- 修复：改为从MD内容提取日期范围（最准确），兜底用ISO周号-1周
- 举一反三：周报的"周号"和"数据覆盖范围"语义不同，ISO周号≠数据覆盖周

**问题6: 外部版暴露内部内容（追踪体系/知识库/人物追踪）**
- 根因：sync_to_public.py的sanitize_html()只做关键词替换不做区块级删除 → 首页仍包含追踪体系Tab、知识库Tab、人物追踪分类按钮
- 修复：增加_remove_tab()函数+区块级正则删除
- 举一反三：关键词替换不够，HTML删除必须用区块级操作（删除整个article/section/div）

**系统根因总结**：周报没有专用gen_weekly_html.py动态生成脚本 → 一切问题从这里开始。有了脚本+JSON schema，CSS/class名不匹配、public/截断、手动拼HTML等问题都不会发生。

### 2026-06-01: W22周报首页+HTML全面修复（5类问题·3轮迭代）

**问题1: 首页周报链接全部指向同一文件（3轮迭代才修复）**
- **Round 1**: 12个往期周报href全指向 `weekly-2026-W22.html`，只修了链接URL，**没注意到同一区域的日期标签也全错（每个偏移1天）**——半截修复
- **Round 2**: 修了日期和描述，**但只改了根目录 `index.html`，没改 `public/index.html`**——GitHub Pages workflow paths filter 只监听 `public/**`，构建没触发，线上无变化
- **Round 3**: 同步 `public/index.html`，构建生效
- **教训①**: 修一个区域时，**通读整个区域所有字段**，不只修最显眼的那一个点。链接URL和日期标签是同一块HTML里的两类错误，不该分两轮发现
- **教训②**: push后**必须curl线上验证**，不是只看本地文件。"本地改了"≠"线上生效"，中间有构建流程+CDN缓存+paths filter三层阻断
- **教训③**: **先看workflow.yml搞清构建路径再动手**。内部版从 `public/` 构建、外部版从根目录构建——两个仓库部署方式不同

**问题2: 周报HTML Markdown语法泄漏+格式混乱**
- 5处 `<strong>关键判断</strong>：**关键判断**` 重复标签（HTML+Markdown双写）
- 16处 `**text**` 未渲染（浏览器直接显示星号）
- 106处 `[text](url)` Markdown链接未转为 `<a>` 标签
- 45处 `<a href="">链接</a>` 空href无效链接
- 38处 inline style散落、animate-on-scroll过度使用(63处)、正文无行宽限制
- **教训④**: **生成周报HTML的脚本必须自动完成 Markdown→HTML 转换**，不能依赖手动拼接。当前 `gen_weekly_html.py` 从JSON生成时不会遇到这个问题，但手动修改/子agent直接写入时容易遗漏

**问题3: 卡片视觉层级扁平（"文字墙"问题）**
- Top5事件卡片：rank/标题/来源/正文/关键判断全部同一字号字重，5个元素挤成一堵墙
- 来源链接拥挤：`📅 📎 [Anthropic Blog](url) · [Champaign Magazine](url)` 一行塞太多
- "关键判断"和正文混排无区隔，扫读时容易跳过
- **教训⑤**: **卡片必须有清晰的视觉层级**——rank pill(12px) → 标题(18px/600) → meta行(13px/SVG icon) → 正文(14px/68ch) → 关键判断独立框(左边框+浅背景)。每个层级字号/字重/颜色都要拉开差距
- **教训⑥**: **emoji不能当UI图标用**——清爽调研报告风格要求用SVG icon替代emoji。结构元素(导航/标题/meta行)用SVG，正文内容的emoji保留

**问题4: 容器级max-width导致右侧大片留白**
- `max-width: 68ch` 被加在了 `.callout`、`.news-card-why`、`.insight-card` 等容器上——容器被限制宽度，卡片右侧空白
- **教训⑦**: **容器撑满父宽度(100%)，只有段落文字限行宽(68ch)**。这是一条不可违反的CSS原则：容器管布局宽度，文字管可读宽度，两者职责不同

**问题5: 外部版特有问题（4项）**
- 林克的洞察章节：外部版不应包含个人AI分身内容 → 合并到周度洞察
- 日报链接指向内部版URL：`ai-insight/` → 应改为 `ai-insight-public/`
- 日报链接带 `-v3.html` 后缀：外部版文件名不带 `-v3` → 导致404
- 首页底部按钮指向内部版首页 → 应改为外部版首页
- **教训⑧**: **外部版修改必须同时检查三项URL替换**：
  1. `ai-insight/` → `ai-insight-public/`（域名/仓库切换）
  2. `-v3.html` → `.html`（文件名后缀去除）
  3. 所有"回到首页"按钮指向对应版本首页
- **教训⑨**: **外部版删除内部专属章节时，内容要合并到相邻章节而非直接丢弃**——"林克的洞察"的洞察内容仍有价值，合并到"周度洞察"

**章节概览图位置错误**：
- SVG概览图放在标题上方（概览图→标签→标题），视觉上banner飘在两个章节之间
- 正确顺序：标签→标题→概览图（先读标题理解主题，再看概览图获取数据要点）
- **教训⑩**: **概览图/配图放在标题之后，不是之前**。标题是语义锚点，图片是补充说明

**系统根因总结**：今天的所有问题都指向同一个根本缺陷——**没有从脚本流程生成/修改，而是手动操作绕过了脚本**。`sync_to_public.py` 本身包含 `-v3→plain` 和 URL 替换规则，但手动修改时这些保障全部失效。正确做法：修改通过脚本流程完成，或者手动修改后必须过脚本验证。

### 2026-06-14: W24周报3类问题全面复盘

**问题1: git push ≠ 网页部署（frontend-cloud漏部署）**
- 根因：周报cron Step 5只有git push + sync_to_external，**没有frontend-cloud deploy**。git push只更新GitHub仓库文件，frontend-cloud是内部版CDN托管平台，必须单独执行`cd public && npx @codeflicker/frontend-cloud-cli@latest deploy`。内部版首页永远不会自动更新。
- 对比：日报通过deploy_daily.sh自动包含frontend-cloud部署（state.json确认"frontend-cloud已部署"），周报没有对应的部署脚本。
- 修复：
  1. weekly-report.md Step 5拆为5a(git push)+5b(sync_to_external)+5c(frontend-cloud deploy)三步
  2. 周报cron payload更新，Step 5明确三步部署+标注"git push ≠ 网页部署"
- **教训①**: **git push只更新代码仓库，不触发CDN部署。每个部署目标需要自己的部署步骤。** 内部版靠frontend-cloud，外部版靠GitHub Pages（由push触发），两者机制不同。

**问题2: update_homepage.py pills href全局替换（#124复发）**
- 根因：`update_weekly_card`的href替换用`re.sub`全局匹配`href="01-daily-reports/...weekly-...html"`——没有count限制，也没有限定HTML区域。每次更新新周报，所有pills的href都被替换成最新周报URL。W22的标签指向W24的链接，W10的标签也指向W24的链接。
- 对比：日报的href替换(行77)有`class="list-item"`限定——只有卡片区域被替换，pills区域不受影响。
- 修复：
  1. href替换正则限定在`class="weekly-report-card"`的`<a>`标签内（注意HTML中href在class前面）
  2. 手动修复13个pills链接（按W10-W22各自指向正确月份目录）
  3. 添加W23 pill
- **教训②**: **re.sub不加count=1就是全量替换。HTML有多个同结构区域时，必须用上下文限定（class/id），不能靠全局模式。**

**问题3: update_homepage.py pill标签和日期格式错误**
- 根因层1：pill模板用`{week_id}`作为标签文本，但week_id传入的是"2026-W23"完整格式 → 生成">2026-W23<"而非">W23<"
- 根因层2：date_range通过`title.replace("第","").replace("周（","").replace("）","")`提取，"第23周（06/01 - 06/07）"→"23周（06/01 - 06/07）"→replace"周（"→"2306/01 - 06/07）"→前面多了"23"
- 修复：
  1. pill标签改为"W" + week_id.split("-W")[1]，只取W+数字部分
  2. date_range改为从title正则提取括号内容：`re.search(r"（([^）]+)）", title)` → "06/08 - 06/14" → replace(" - ", "-") → "06/08-06/14"
- **教训③**: **字符串replace链是脆弱的提取方式。有固定格式时用正则提取括号内容更可靠。**

**问题4: update_homepage.py 验证脚本pills正则顺序错误**
- 根因：验证正则`r'>W(\d+)<.*?href="..."'`假设>W21<在href前面，但HTML结构是href在>W21<前面（`<a href="...">W22<span>`）→ 验证永远报"pills链接不匹配"的假阳性
- 修复：正则改为`r'href="([^"]*weekly-2026-W(\d+)\.html)"[^>]*>[^<]*>W(\d+)<'`，提取href中的W编号和标签中的W编号做匹配
- **教训④**: **验证脚本的假阳性比没有验证更危险——它浪费调试时间，还可能掩盖真问题。**

**系统根因总结**：W24的三类问题都指向同一个根因——**update_homepage.py是"能跑就行"的粗粒度脚本，没有考虑HTML多区域隔离**。href全局替换、pill标签格式、date_range提取、验证正则——四个独立bug叠加，导致每次周报更新后首页都被破坏，而cron agent误判为成功。

**彻底修复清单（已全部完成）**：
1. ✅ Step 5三步部署(5a git push + 5b sync_to_external + 5c frontend-cloud deploy)
2. ✅ update_weekly_card href替换限定class="weekly-report-card"
3. ✅ pill标签改为W+数字格式
4. ✅ date_range从title正则提取括号内容
5. ✅ 验证脚本pills正则匹配HTML实际结构
6. ✅ 首页pills手动修复(W10-W23各自指向正确月份)
7. ✅ 三步部署验证通过

**下次周报一步到位验证清单**：
| # | 验证项 | 命令/方法 | 预期 |
|---|--------|-----------|------|
| 1 | update_homepage.py 执行无❌ | 脚本输出 | ✅ 首页更新完成！|
| 2 | 卡片标题=最新周 | `grep "wrc-title" index.html` | 第24周（06/08 - 06/14）|
| 3 | pills链接和标签匹配 | `grep ">W[0-9]*<" index.html` | W10-W23各自对应 |
| 4 | frontend-cloud部署成功 | `cd public && npx frontend-cloud-cli deploy` | ✅ 部署成功！|
| 5 | 外部版push成功 | sync_to_external输出 | ✅ 已推送到外部仓库 |
| 6 | 四链接HTTP 200 | curl验证 | 302(内部)/200(外部) |

### 2026-06-15: W24周报Header副标题+底部对齐+内外版URL分离

**问题1: Header副标题文字太挤、辨识度差**
- 根因：副标题紧跟在h1渐变标题下方，margin-top仅2px，字号14px与badge/meta同级，且max-width:640px使文字被挤压
- 修复：字号14px→13px，颜色secondary→muted（更淡），margin-top:2px→14px，去640px max-width限制
- **教训①**: Header副标题是"定调句"不是"备注行"——需要独立视觉空间，与标题拉开间距、降低视觉权重（muted色+小字号）

**问题2: 底部"了解更多"区域宽度与上面内容区不对齐**
- 根因：了解更多外层div有独立的`max-width:var(--content-max)`在content-inner里面又套了一层max-width，加上padding:16px 20px使容器比内容区窄。doc-footer没有max-width约束。
- 修复：外层div去掉`max-width:var(--content-max)`改为`max-width:100%`，padding改为`0 0 48px`（让内层卡片自定宽），doc-footer加`max-width:100%`
- **教训②**: **在已有max-width容器（content-inner）内，子元素不需要再加独立max-width——双约束=更窄。子元素跟随父容器宽度，只管内容不管布局**

**问题3: 外部版所有链接都指向内部版URL（最关键）**
- 根因：本次周报手动编辑HTML时跳过了`sync_to_external.py`的URL替换流程。脚本本身包含`INTERNAL_PAGES_BASE→EXTERNAL_PAGES_BASE`的自动替换，但手动修改→手动cp到外部仓库→没有过脚本=所有14处链接都还是internal URL
- 修复：`sync_to_external.py --full --verify` 自动替换，验证外部版零残留internal URL
- **教训③**: **外部版部署必须走sync_to_external.py脚本，禁止手动cp HTML到外部仓库。脚本不只做文件复制，更做URL替换——手动cp = URL全错**
- **教训④**: **内外版本分离原则：内部版HTML所有链接指向internal域名，外部版HTML所有链接指向external域名。"了解更多"按钮、日报链接、首页按钮都必须区分**

**系统根因总结**：三个问题都指向同一个根因——**手动操作绕过了脚本自动化保障**。gen_weekly_html.py生成时用的是INTERNAL_PAGES_BASE（正确），但手动修改HTML后直接cp到外部仓库，跳过了sync_to_external.py的URL替换=外部版14处链接全错。

---

_更新于 2026-06-15 · v3.4 · 新增W24 Header/底部对齐/URL分离复盘（3类问题+4条教训）_
### 2026-06-22: W25周报6类格式问题全面修复（#128）

**问题1: 了解更多模块模板变量未替换（P0）**
- 根因：`LEARN_MORE`常量直接用`{SVG_ICONS["insight"]}`和`{INTERNAL_BASE}`，但常量不在f-string上下文中，Python不会求值=输出原始文本`{SVG_ICONS["insight"]}`
- 修复：改用占位符模板`__SVG_INSIGHT__`/`__HOMEPAGE_URL__`，在`generate_html()`中显式替换
- **教训①**: **Python变量`{var}`只在f-string上下文内求值。字符串常量中写花括号变量=原始文本输出。用占位符+显式替换替代。**

**问题2: insight trend_links日报链接带`-v3.html`后缀（P0）**
- 根因：JSON中trend_links的URL用了内部版后缀`-v3.html`，但外部版文件名无此后缀→外部用户404
- 修复：新增`_clean_daily_url()`函数自动去除`-v3.html`
- **教训②**: **内部版和外部版的日报文件名不同（`-v3.html` vs `.html`），脚本必须自动清理后缀，不能假设JSON数据格式正确。**

**问题3: Top5来源无超链接（P1→升为P0）**
- 根因：JSON的`source`字段合并了3个来源为纯文字`"Fortune · 36氪 · Axios"`，`source_url`为空，脚本渲染为`<span>`=不可追溯
- 修复：JSON新增`sources[]`数组（每来源独立name+url），脚本优先读sources逐个渲染为`<a class="meta-link">`
- **教训③**: **来源不可追溯=违反output-format-spec 1.4。多来源必须逐个配URL，不能合并为一个纯文字span。**

**问题4: 双`<strong>`嵌套（P1）**
- 根因：JSON的`intro_callout`自带`<strong>本周核心判断：...</strong>`，脚本又包了一层`<strong>`=双层
- 修复：`_strip_double_strong()`清理+自动检测解包JSON自带`<strong>`后脚本再加
- **教训④**: **JSON内容可能自带HTML标签，脚本渲染时必须检查并避免与自身模板标签重叠。**

**问题5: insight-card内联`font-family:var(--font-family-cn)`（P2）**
- 根因：`--font-family-cn`变量未定义（会fallback），内联style和全局body字体冲突
- 修复：删除内联style，统一用CSS class
- **教训⑤**: **内联style是最脆弱的样式方式——无法被覆盖、与全局样式冲突、变量可能未定义。优先用CSS class。**

**问题6: stats-grid 5卡但CSS固定4列（P1）**
- 根因：`.stats-grid`桌面端`repeat(4, 1fr)`固定4列，第5卡折行+1/4宽=视觉孤岛
- 修复：改为`repeat(auto-fit, minmax(160px, 1fr))`自适应
- **教训⑥**: **固定列数CSS假设卡片数量固定。用auto-fit/adaptiv布局更健壮。**

**系统根因总结**：6类问题中5类指向**脚本生成逻辑缺乏防御性**——脚本假设JSON数据格式干净、字段完整、不带HTML标签、文件名统一，但实际数据有`-v3`后缀、空URL、自带`<strong>`标签、合并文字来源。脚本需要防御性处理，不能依赖数据质量。

**3条新P0红线**：
1. **#27: 模板变量禁止嵌入f-string上下文外的字符串常量** — 用占位符+显式替换
2. **#28: Top5来源必须逐个配超链接** — `sources[]`数组，禁止纯文字合并
3. **#29: 脚本必须防御JSON脏数据** — `-v3`自动清理/双`<strong>`去嵌套/空URL fallback

---

_更新于 2026-06-22 · v3.5 · 新增W25 6类格式问题复盘+3条P0红线(#27-#29)_
