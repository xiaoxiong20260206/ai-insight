# AI周报执行流程 (v3.1 精简版)

> **版本**: v3.1 (2026-05-18: 新增踩坑教训+自检强制规则)
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
- W22全部6类问题：cron直接群发跳过确认、CSS/class名不匹配、public/截断版、首页pills错误、MixCard日期错误、外部版暴露内部内容

### P1-4: 自检声明
执行前输出：`"我已读完SKILL.md+output-format-spec.md+weekly-report.md+踩坑教训，理解9条P0红线，准备执行Step 1"`

1. **确认类型**: 周日出周报，其他出日报。周号计算：`date +%G-W%V`（当前周号，周报cron在周一执行生成当前周的周报）
2. **⚠️ MixCard按钮URL校验**：推送前必须用 `--verify-urls` 确认按钮URL可达（HTTP 200）。如果HTML还没部署完成，不能推送MixCard。

---

## 流程总览

```
Step 1: 读取本周日报 → 日期验证 + URL提取
Step 2: 汇总分析 → Top5 + 洞察 → 周报MD
Step 3: 生成周报HTML（≥50KB + 来源超链接）
Step 4: 首页更新 → update_homepage.py --type weekly
Step 5: 部署 + 外部同步 → sync_to_external
Step 6: KIM推送 → build_insight_mixcard.py weekly → message(kimMixCard)
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

## Step 2: 汇总分析 → 周报MD

### 内容结构
- **Top 5**: 5条最重要事件（行业影响力+关注度+趋势信号+数据冲击+政策意义）
- **周度洞察**: 跨板块共同主题 + 趋势强化/反转 + 数据/事件含义（至少2条）
- **林克的洞察**: 独立判断段落
- **日报索引**: 周一到周日所有已有日报
- **技术词汇表**: 8-10条新术语（≥50KB补充）
- **宏观叙事**: 本周主题叙事段落（≥50KB补充）

### 质量规则
- Top5和洞察必须有 `[文字](URL)` 超链接（URL来自日报JSON）
- 禁止KIM Doc内部链接（docs.corp.kuaishou.com）
- 外部版深度调研链接文案="深度调研"，不加"完整版"

---

## Step 3: 生成周报HTML（≥50KB）

文件路径：`01-daily-reports/YYYY-MM/weekly-YYYY-WXX.md` + `.html`

### HTML规范
- 清爽调研风格 v5.0（复用日报CSS/JS模板：`templates/daily-report-v3.css` + `.js`）
- **HTML结构必须使用W20一致的class名体系**（news-card/stat-card/insight-card/callout/doc-chapter-label/daily-index/table-wrap）
- Top5卡片source行有 `<a href>` 链接
- 各板块事件表格有 `<a href>` 链接
- `<50KB时补充技术词汇表+宏观叙事`
- 底部"了解更多"模块（P0强制，见 output-format-spec.md）

### MD→HTML class名映射表（强制遵守）

| MD结构 | HTML结构 | class名 |
|--------|----------|---------|
| ## 📋 本周概览 | `#overview` section | — |
| 概览表格 | `.table-wrap` + `<table>` | — |
| 统计数字 | `.stats-grid` + `.stat-card .stat-value/.stat-label` | `.stat-info/.stat-success/.stat-warning/.stat-purple/.stat-danger` |
| ### 1. [Top5标题] | `.news-card` | `style="--card-accent: var(--color-purple/info/success/danger/warning)"` |
| Top5排名 | `.news-card-rank` | — |
| Top5标题 | `.news-card-title` | — |
| Top5来源 | `.news-card-source` | — |
| Top5摘要 | `.news-card-desc` | — |
| Top5为什么重要 | `.news-card-why` | — |
| ## 💡 周度洞察 | `#insight` section | `.insight-card` + `.insight-tag/title/trend` |
| ## 🧠 林克的洞察 | `#linkinsight` section | `.callout.callout-purple/info/success/warning` |
| 板块事件表格 | `.table-wrap` + `<table>` | — |
| ## 📅 日报索引 | `#dailyindex` section | `.daily-index` + `.daily-item` |
| ## 📖 技术词汇 | `#vocab` section | `.table-wrap` + `<table>` |
| ## 🌊 宏观叙事 | `#narrative` section | `.callout` 系列 |

### 生成方式

**优先使用脚本**（如果 `gen_weekly_html.py` 已改造为动态版本）：
```bash
uv run scripts/gen_weekly_html.py --date YYYY-WXX --input data/weekly-content-YYYY-WXX.json
```

**手动生成时**：使用W20的HTML作为CSS/JS模板骨架，只替换 `<body>` 内的内容部分。禁止自创class名。

验证：`wc -c *.html` 必须 ≥50000字节

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
# 内部版 git push
git add -A && git commit -m "📊 AI周报 YYYY-WXX" && git push origin main

# ⚠️ 必须同步 public/ 目录（Pages部署源）
cp 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html public/01-daily-reports/YYYY-MM/weekly-2026-WXX.html
cp index.html public/index.html  # 首页也必须同步
wc -c 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html  # 验证大小一致

# 外部版同步（自动脱敏）
uv run scripts/sync_to_external.py --full --verify

# 确认外部首页也更新了
# 如果 sync_to_external.py 输出"无变更需要提交"，说明外部首页可能没同步
# 需要手动同步：sanitize_html(index.html) → ai-insight-public/index.html
```

### 四位置验证
```
①内部周报 ②内部首页(含周报入口) ③public/周报 ④外部仓库周报+首页
```

> **⚠️ W22踩坑教训**: 修改了 01-daily-reports/ 下的文件但忘了cp到 public/ 对应路径 → Pages返回截断旧版27KB而非完整70KB。public/是Pages部署源，不是可选步骤。

---

## Step 6: KIM推送

```bash
# 1. 生成mixCard（脚本自带6锚点校验+kimMd格式校验）
uv run scripts/build_insight_mixcard.py weekly --date YYYY-WXX --output /tmp/card.json --with-summary

# 2. 先私发预览给 shenlang03
# message(channel=kim, kimMixCard=<card>, target="username:shenlang03")

# 3. 等沈浪确认后再群发
# message(channel=kim, kimMixCard=<card>, target="space:<groupId>")
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
| 周报 | **先私发预览给shenlang03** → 确认后再群发AI生产力中心大群 | ❌禁止不确认就群发 |
| 日报 | 私发订阅者 | ❌禁止群发 |

### 默认推送群
> **2026-05-25 更新**：周报只发到AI生产力中心大群，不再发其他群。

| 群名 | groupId |
|------|---------|
| AI生产力中心大群 | `6783643915686960` |

---

## 交付物（P0强制）

```
📊 周报四链接自检：
🔒 内部版：https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
🌐 外部版：https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
🏠 内部首页：https://xiaoxiong20260206.github.io/ai-insight/
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
- 修复：删除"只推一次"，改为"先私发预览给shenlang03，不自动群发"，群发是手动步骤
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

---

_更新于 2026-05-18 · v3.1 · 新增P0自检清单+踩坑教训_