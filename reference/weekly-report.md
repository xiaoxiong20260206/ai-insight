# AI周报执行流程 (v3.1 精简版)

> **版本**: v3.1 (2026-05-18: 新增踩坑教训+自检强制规则)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前（2条）

1. **确认类型**: 周日出周报，其他出日报。周号计算：`date +%G-W%V`（当前周号，周报cron在周一执行生成当前周的周报）
2. **⚠️ MixCard按钮URL校验**：推送前必须用 `--verify-urls` 确认按钮URL可达（HTTP 200）。如果HTML还没部署完成，不能推送MixCard。
3. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`

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
- 清爽调研风格 v5.0
- Top5卡片source行有 `<a href>` 链接
- 各板块事件表格有 `<a href>` 链接
- `<50KB时补充技术词汇表+宏观叙事`

验证：`wc -c *.html` 必须 ≥50000字节

---

## Step 4: 首页更新（统一脚本）

```bash
python3 scripts/update_homepage.py YYYY-WXX --type weekly \
  --week-title "第XX周（MM/DD - MM/DD）" \
  --week-desc "覆盖N条资讯 · 事件1 · 事件2" \
  --week-month YYYY-MM --week-day DD
```

---

## Step 5: 部署 + 外部同步

```bash
# 内部版 git push
git add -A && git commit -m "📊 AI周报 YYYY-WXX" && git push origin main

# 外部版同步（自动脱敏）
python3 scripts/sync_to_external.py --full --verify
```

### 四位置验证
```
①内部周报 ②内部首页(含周报入口) ③public/周报 ④外部仓库周报
```

---

## Step 6: KIM推送

```bash
# 1. 生成mixCard（脚本自带6锚点校验+kimMd格式校验）
python3 scripts/build_insight_mixcard.py weekly --date YYYY-WXX --output /tmp/card.json --with-summary

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
| 类型 | 范围 | 禁止 |
|------|------|------|
| 周报 | 发所有群 | 正常 |
| 日报 | 私发订阅者 | ❌禁止群发 |

### 默认推送群
| 群名 | groupId |
|------|---------|
| 研发效能中心全员群 | `3705455482343722` |
| 【AI生产力】MyFlicker产研 | `6724050835415361` |
| 【L5项目】研发线AI-Ready | `6646213728505891` |

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

---

_更新于 2026-05-18 · v3.1 · 新增P0自检清单+踩坑教训_