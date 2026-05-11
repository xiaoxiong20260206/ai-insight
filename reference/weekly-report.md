# AI周报执行流程 (v3.0 精简版)

> **版本**: v3.0 (2026-05-11: 精简版，从539行→核心流程)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。

---

## ⚠️ 执行前（2条）

1. **确认类型**: 周日出周报，其他出日报。周号用 `date -d "next sunday" +%G-W%V` 计算
2. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`

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

_更新于 2026-05-11 · v3.0 · 精简版，539行→核心流程_