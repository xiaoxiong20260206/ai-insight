# AI周报系统性审计报告 (2026-05-25)

> **目标**: AI周报一次性做对 — 不再出现W22级别的问题

---

## 🔴 P0致命问题（必须立即修复，否则W23一定失败）

### P0-1: gen_weekly_html.py 是硬编码W22的静态脚本，不能动态生成新周报

**现状**: `scripts/gen_weekly_html.py` 是一个69554字节的Python文件，整个W22的HTML内容被硬编码为Python字符串常量。脚本不接受任何输入参数（无argparse/sys.argv），不读取JSON/MD文件，不做任何动态内容插入。

**后果**: 
- cron payload已写明"HTML必须用 scripts/gen_weekly_html.py 生成"
- W23周报cron调用此脚本时，只会生成W22的内容——周报标题、日期、Top5全部是W22的旧数据
- 这比没有脚本更糟糕：没有脚本时agent自由拼HTML（至少会用新数据），有了"脚本"但脚本只输出旧数据，agent会信任脚本输出而跳过内容检查

**修复方案**: 重写为动态生成脚本，仿照日报的 `gen_daily_html.py` 架构：
1. 接受 `--date YYYY-WXX` 和 `--input weekly-content.json` 参数
2. 读取JSON内容 + CSS模板(`templates/daily-report-v3.css`) + JS模板(`templates/daily-report-v3.js`) 
3. 动态填充周报各板块内容到W20的HTML骨架
4. 自校验：≥50KB、5板块完整性、{{message}}扫描、class名一致性
5. 输出到 `01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html`

**工作量**: 中等（约2-3小时），需要：
- 定义周报JSON schema（Top5/洞察/各板块表格/统计卡片/日报索引/词汇表/宏观叙事）
- 编写JSON→HTML映射逻辑（参考W20的HTML结构）
- 自动cp到public/目录

### P0-2: 周报没有JSON schema定义和JSON生成脚本

**现状**: 日报有完整的 `gen_daily_json.py` → `gen_daily_html.py` 链路（JSON schema定义 → LLM只需输出~200行JSON → 脚本自动生成~900行HTML）。周报没有这个链路。

**后果**: agent必须在context里手拼完整HTML（约868行、70KB），消耗大量token，且极易出现CSS/class名不匹配问题。

**修复方案**: 
1. 建立 `scripts/gen_weekly_json.py` — 定义周报JSON schema（参考日报schema）
2. cron payload改为"先生成JSON，再用 gen_weekly_html.py 从JSON生成HTML"
3. LLM只需输出~200行JSON（Top5+洞察+板块表格+统计数据），脚本自动填充到~868行HTML骨架

### P0-3: 周报Step 3（生成HTML）没有可执行的脚本化命令

**现状**: `weekly-report.md` Step 3只说"生成周报HTML（≥50KB）"，没有给出具体的脚本命令。cron payload写的"HTML必须用 scripts/gen_weekly_html.py 生成"，但这个脚本实际不能用。

**后果**: agent不知道怎么生成HTML，只能自由拼，导致class名/CSS不匹配。

**修复方案**: weekly-report.md Step 3应明确写：
```bash
# Step 2完成后，先生成JSON
uv run scripts/gen_weekly_json.py --date YYYY-WXX --output data/weekly-content-YYYY-WXX.json
# 再从JSON生成HTML
uv run scripts/gen_weekly_html.py --date YYYY-WXX --input data/weekly-content-YYYY-WXX.json
# 验证
wc -c 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html  # ≥50000
```

---

## 🟡 P1重要问题（W23可能失败但不致命）

### P1-1: weekly-report.md的日期计算逻辑和MixCard日期范围冲突

**现状**: 
- `weekly-report.md` Step 1的日期计算使用 `today.weekday()` 逻辑，cron在周一执行时 `monday=today`（本周一），所以周号是ISO当前周号
- 但 `build_insight_mixcard.py` 的日期范围是从MD内容提取（覆盖范围=上周一到上周日）
- 两者语义矛盾：周报cron在周一09:00执行，收集的是"上周"（已完成一周）的数据，但ISO周号指向"本周"（刚开始的一周）
- W22数据覆盖05/19-05/25，但ISO W22从05/25开始

**后果**: 如果MD里没写明确日期范围，MixCard fallback会用ISO周号-1周=05/18-05/24（少了一天）

**修复方案**: 
- weekly-report.md Step 1改为明确语义："周报覆盖的是**上一周**的数据（上周一到上周日），周号=上周的ISO周号"
- MixCard从MD提取日期范围（已修复），但MD生成时必须包含明确日期格式如"05/19-05/25"

### P1-2: 没有元执行（P1）保障流程

**现状**: 日报cron payload有前置环境初始化步骤（`daily_env_init.sh`），周报cron payload也有环境初始化。但都没有日报那样完整的P1-1→P1-2→P1-3→P1-4元执行保障：

日报cron的教训（2026-05-10连续15次失败）：
- P1-1 环境初始化（uv PATH）
- P1-2 技能加载（必须读5个必读文件后才能动手）
- P1-3 踩坑检索（lessons-learned）
- P1-4 自检声明（确认理解了所有P0红线）

周报cron payload目前只有环境初始化+技能加载，没有踩坑检索和自检声明。

**后果**: agent可能跳过读取关键文档，凭感觉动手——和日报历史上的"不读规范就动手"问题一样

**修复方案**: 周报cron payload增加P1-3踩坑检索和P1-4自检声明：
```
**P1-3 踩坑检索**: 读取 reference/weekly-report.md 的「踩坑教训」部分，确认理解W18日历正则bug和W22全部6类问题
**P1-4 自检声明**: 执行前输出"我已读完weekly-report.md+output-format-spec.md+踩坑教训，理解9条P0红线，准备执行Step 1"
```

### P1-3: public/目录同步没有自动化保障

**现状**: cron payload写了"public/目录必须同步"，但这是靠agent自觉遵守的文字指令，没有脚本自动化保障。

**后果**: agent修改了 `01-daily-reports/` 下的文件但忘了cp到 `public/`（W22就是这个原因导致内部版截断）

**修复方案**: 
1. `gen_weekly_html.py` 生成HTML后自动cp到 `public/` 对应路径
2. `update_homepage.py` 更新首页后自动同步到 `public/index.html`
3. 验证步骤：`diff <(wc -c src) <(wc -c public/src)` 大小应一致（或public版略大因为脱敏替换）

### P1-4: update_homepage.py周报模式没有自动同步到public/和外部仓库

**现状**: `update_homepage.py --type weekly` 只更新内部版首页（`index.html`），不自动：
1. cp到 `public/index.html`（然后走sanitize流程）
2. 同步到 `ai-insight-public/index.html`

**后果**: 首页更新了内部版，但外部版首页没同步（W20就是这个原因导致外部首页没有W20入口）

**修复方案**: 
1. `update_homepage.py` 在weekly模式完成后自动调用 `sync_to_public.py` 和 `sync_to_external.py`
2. 或者在weekly-report.md Step 4后增加明确的同步命令

### P1-5: 周报MD模板(weekly-report-template.md)和HTML结构不匹配

**现状**: MD模板是标准Markdown格式，但HTML用的是W20的清爽调研风格（侧边栏+卡片+动画+阅读进度条）。MD结构和HTML结构没有对应映射关系。

**后果**: agent从MD转HTML时没有明确的映射规则，容易自创class名体系

**修复方案**: 在 `output-format-spec.md` 或新建 `reference/weekly-html-mapping.md` 中建立MD→HTML映射表：

| MD结构 | HTML class | 说明 |
|--------|-----------|------|
| ## 📋 本周概览 | `#overview` section + `.stats-grid` + `.stat-card` | |
| ### 1. [标题] (Top5) | `.news-card` + `.news-card-rank/title/source/desc/why` | |
| ## 💡 周度洞察 | `#insight` section + `.insight-card` + `.insight-tag/title/trend` | |
| ## 🧠 林克的洞察 | `#linkinsight` + `.callout.callout-purple/info/success` | |
| 表格 | `.table-wrap` + `<table>` | |

---

## 🟢 P2小问题（不影响正确性但影响体验）

### P2-1: 首页往期周报pills不是脚本动态维护

首页pills（W10/W14/W18/W20链接列表）是静态HTML，每次新周报后需要手动更新或靠agent手动修改。应考虑脚本化。

### P2-2: sync_to_external.py不自动同步首页到外部仓库

`ai-insight-public/index.html` 需要手动cp或单独步骤同步。应增加自动化。

### P2-3: 周报没有质量门脚本

日报有 `daily_quality_gate.py`（hard/soft分级），周报没有。周报的质量检查完全依赖P0自检6项，没有脚本化的质量门。

### P2-4: weekly-report.md的"推送范围"表格和P0红线矛盾

weekly-report.md的推送范围表格写"周报发所有群（正常）"，但P0红线和cron payload要求"先私发预览给shenlang03，不自动群发"。两者矛盾，agent可能误解为"群发是正常流程"。

---

## 📊 修复优先级排序

| 优先级 | 修复项 | 预估工作量 | 对W23的影响 |
|--------|--------|-----------|-------------|
| **P0** | gen_weekly_html.py改为动态生成 | 2-3小时 | 不修=W23必然失败 |
| **P0** | 建立周报JSON schema+gen_weekly_json.py | 1-2小时 | 不修=agent手拼HTML |
| **P0** | weekly-report.md Step 3明确脚本命令 | 0.5小时 | 不修=agent不知道怎么执行 |
| **P1** | 日期语义对齐 | 0.5小时 | 不修=MixCard可能显示错误日期 |
| **P1** | 元执行P1-3/P1-4保障 | 0.5小时 | 不修=agent可能跳过关键文档 |
| **P1** | public/自动同步 | 0.5小时 | 不修=内部版可能截断 |
| **P1** | 首页同步自动化 | 1小时 | 不修=外部首页可能没新周报 |
| **P1** | MD→HTML映射表 | 0.5小时 | 不修=class名可能不匹配 |
| **P2** | pills脚本化 | 0.5小时 | 低 |
| **P2** | 首页外部仓库自动同步 | 0.5小时 | 低 |
| **P2** | 周报质量门脚本 | 1小时 | 低 |
| **P2** | 推送范围矛盾修复 | 5分钟 | 低 |

---

## ✅ 今天已完成修复

| 修复项 | 状态 |
|--------|------|
| cron payload删除"只推一次"→改为先私发预览 | ✅ |
| MixCard日期bug修复（从MD提取日期范围） | ✅ |
| sanitize_html()区块级删除增强（_remove_tab函数） | ✅ |
| public/同步红线写入cron payload | ✅ |
| 外部首页追踪体系/知识库/人物追踪完整移除 | ✅ |

---

_审计完成于 2026-05-25 15:35_