# AI周报生成完整流程 (v2.2 硬性门控版)

> **版本**: v3.2 (超链接强制要求 + MixCard推送P0红线 + 卡片结构≠MD全文 + fail loud原则 + space:groupId格式 + 踩坑#106-#111)
> **更新时间**: 2026-05-06
> **变更说明**: v3.2 新增：(1) 周报HTML必须携带来源超链接（Top 5 卡片+各板块表格），与日报HTML和KIM卡片保持一致；(2) Step 1 新增URL提取步骤；(3) 踩坑#111

---

## ⚠️ 执行前强制阅读

> **🔴 如果你不读这个文档就执行，你一定会出错。**
> 
> 今天的教训：有workflow文档但不遵守，比没有文档更危险。

---

## 工作流程概览 (v2.1)

```
Step -1: 执行前踩坑召回（P0强制）
Step 0:  确认任务类型（日报vs周报）
Step 1:  读取本周日报，计算正确日期范围
Step 2:  汇总分析，生成周报MD
Step 3:  生成周报HTML（必须存在才能推送）
Step 4:  执行 --preview（仅一次，然后停止）
Step 5:  输出提示等待用户确认
Step 6:  用户确认后发送群消息
Step 7:  同步首页 + 外部版 + Git推送
Step 8:  输出四链接交付
```

---

## Step -1: 执行前踩坑召回（P0强制）

**🔴 此步骤不可跳过！**

### 强制执行命令

```bash
# 在开始任何周报任务前，必须先执行：
search_memory(
  query="周报推送 相关错误",
  keywords="周报,KIM,推送,preview,confirm,重复发送"
)
```

### 输出格式

```
📋 相关踩坑经验提醒：
- #74: KIM API返回错误≠消息未投递，错误后不要立即重试
- #75: 日期范围算错 → 使用 Step 1 日期计算公式
- #76: 重复preview → 只执行一次 preview
- #77: 未确认就发群 → Step 5 必须等待用户确认
- #78: Git未推送 → Step 7 必须执行 git push
- #79: 日报索引缺失 → 检查周一到周日所有日报
- #81: preview后重复sync → --preview 已自动完成 sync+push，Step 7 只需验证

⚠️ 我已知晓以上风险，开始执行...
```

---

## Step 0: 确认任务类型

**问自己：用户说的是"日报"还是"周报"？**

| 用户说的话 | 执行的文档 |
|-----------|-----------|
| "跑一下AI周报" | 本文档 |
| "跑一下AI日报" | `daily-report/workflow.md` |
| "跑一下" | 周日出周报，其他日出日报 |

### ✅ Step 0 退出条件

- [ ] 已确认任务是"周报"（不是日报）
- [ ] 已确定周号（如 W16）
- [ ] 已确定日期范围（如 04/13-04/19）

---

## Step 1: 读取本周日报（含日期验证）

### 日期计算（P0强制）

```python
from datetime import datetime, timedelta

today = datetime.now()
# 如果今天是周日（周报日），计算本周
if today.weekday() == 6:  # 周日
    monday = today - timedelta(days=6)
else:
    monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

week_num = monday.isocalendar()[1]
print(f"W{week_num} = {monday.strftime('%Y-%m-%d')}（周一）到 {sunday.strftime('%Y-%m-%d')}（周日）")
```

### 验证清单（必须全部打勾）

- [ ] 周报标题格式：`YYYY年第WW周（MM/DD - MM/DD）`
- [ ] 起始日期是周一（不是周二或其他）
- [ ] 结束日期是周日（不是周六）
- [ ] 日报索引包含周一到周日的所有已有日报

### ✅ Step 1 退出条件

- [ ] 已运行日期计算脚本
- [ ] 周一日期确认正确
- [ ] 周日日期确认正确
- [ ] 所有日报文件已定位
- [ ] **已从日报JSON提取每条新闻的 `url` 字段**（超链接来源，Step 2/3 必须使用）

---

## Step 2: 汇总分析

### 统计各板块资讯数
```python
section_stats = {
    "大模型": 0, "AI编程": 0, "AI应用": 0,
    "AI行业": 0, "企业AI转型": 0
}
```

### 提炼 Top 5
从全周资讯中选出最重要的5件事，标准：
1. 行业影响力最大
2. 用户关注度最高
3. 趋势信号最强
4. 数据最具冲击力
5. 政策/战略意义最重

### 周度洞察（周报独有价值）

> 与日报趋势洞察的区别：日报是当日即时判断，周报是跨7天的模式识别和趋势确认

**周度洞察三问**：
1. 本周有哪些**跨板块的共同主题**？
2. 本周有哪些**趋势得到强化或反转**？
3. 本周的数据/事件**意味着什么**？

### ✅ Step 2 退出条件

- [ ] Top 5 已选出
- [ ] 周度洞察已提炼（至少2条）
- [ ] 日报索引已完整列出（周一到周日）
- [ ] 周报MD已生成
- [ ] **MD中所有事件表格的"事件"列和"来源"列都有 `[文字](URL)` 超链接**（URL来自Step 1提取的日报JSON `url` 字段）
- [ ] **Top 5 每条的"来源"行都有 `[来源名](URL)` 超链接**

---

## Step 3: 生成周报HTML（P0，不可跳过）

### 文件路径
```
01-daily-reports/YYYY-MM/
├── weekly-YYYY-WXX.md       # Markdown版本（先生成）
└── weekly-YYYY-WXX.html    # HTML版本（必须生成，>50KB）
```

### HTML规范（v3.0）

- 使用清爽调研风格 v5.0
- 左侧TOC + 右侧内容区
- 各章节为锚点Section
- 日期格式统一：`2026-04-13 周一`
- **🔴 超链接强制要求（v3.0新增）**：与日报HTML和KIM卡片一致，周报HTML必须携带来源超链接：
  - **Top 5 卡片**：`news-card-source` 行改为 `<div class="news-card-source">📎 <a href="URL" target="_blank">来源名</a> · 日期</div>`
  - **各板块事件表格**：事件 `<td>` 改为 `<td><a href="URL" target="_blank">事件描述</a></td>`；来源 `<td>` 改为 `<td><a href="URL" target="_blank">来源名</a></td>`
  - URL 来自 Step 1 从日报JSON提取的 `url` 字段
  - 无 URL 的条目（如行业报告、综合统计）可不加链接，但事件描述保持纯文字

### 验证命令

```bash
wc -c 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
# 必须 > 50000 字节（50KB）
```

### ⚠️ HTML 不足 50KB 时的补充策略

> **常见陷阱**：基于 W16 模板替换内容后，文件大小可能在 49KB 附近，差几百字节不达标

**推荐补充节（按优先级）**：
1. **技术词汇表** — 本周出现的新技术术语及含义（8~10 条，约 2KB）
2. **宏观叙事** — 本周的主题叙事段落（500~800字，约 1.5KB）
3. **企业影响分析** — 扩展某个Top5事件对企业的具体影响（约 1KB）

```html
<!-- 添加到 watchlist 和 dailyindex 之间 -->
<section style="margin-top:40px;">
    <div class="doc-chapter-label">技术词汇表</div>
    <h2>📖 本周关键技术词汇</h2>
    ...
</section>
<section style="margin-top:20px;margin-bottom:48px;">
    <div class="doc-chapter-label">宏观叙事</div>
    <h2>🌐 本周的宏观叙事</h2>
    ...
</section>
```

### ✅ Step 3 退出条件

- [ ] HTML文件已生成
- [ ] 文件大小 > 50KB（用 `wc -c` 验证，确保 > 50000）
- [ ] 浏览器打开无样式错误
- [ ] **Top 5 卡片的 source 行有 `<a href>` 链接**（与日报HTML格式一致）
- [ ] **各板块事件表格的事件列和来源列有 `<a href>` 链接**

---

## Step 4: 执行 --preview（仅一次，Work模式唯一路径）

> ⚠️ **Work模式说明**: 运行环境无 KIM_APP_KEY/SECRET_KEY，旧版直连 KIM API（路径B）**不可用**。

```bash
# 生成 mixCard JSON（统一生成器）
python3 scripts/build_insight_mixcard.py weekly --date YYYY-Www --output /tmp/card.json --with-summary
# 然后读取 /tmp/card.json，用 message(channel=kim, kimMixCard=<card>, ...) 发送给 shenlang 预览
```
> ⚠️ 旧版路径B（`send_ai_weekly.py --preview`）需要 KIM 凭证，Work 模式下不可用。如 Code 模式下有凭证可用：
> ```bash
> ⚠️ python3 scripts/send_ai_weekly.py YYYY-WXX --preview  （此脚本已归档废弃，仅Code模式下有KIM凭证时可用）
> ```

**🔴 强制规则**：
- **只执行一次**
- 如果之前已执行过preview，**不要再执行**
- 如果同步出问题，修复后**不需要再preview**

### ⚠️ 重要：--preview 脚本的自动级联行为（经验 #81）

> **发现时间**: 2026-04-27（W17周报实测确认）

`--preview` 执行后，脚本**会自动完成以下 Step 7 的工作**：
```
步骤5（脚本内）: 自动更新首页联动（weeklyReportsData + 入口卡片 + public/ 同步）
步骤6（脚本内）: 同步外部版（ai-insight-public）并推送 git
```

**因此**：
- ✅ `--preview` 输出 `Send OK!` + 四链接后，Step 7 的 sync/push 已经**自动完成**
- ⚠️ **不要在 Step 7 再次执行 sync_to_external.py**，否则会导致 double-sync
- ✅ Step 7 只需验证四位置是否正确，不需要重新执行同步命令

脚本输出确认标志：
```
✅ 已推送到 xiaoxiong20260206/ai-insight-public
📋 YYYY-WXX 周报已完成 ✅
```

### ✅ Step 4 退出条件

- [ ] 命令输出包含 `Send OK!`
- [ ] 只执行了一次 preview
- [ ] 没有重复执行
- [ ] 确认脚本是否已自动完成 sync（看输出末尾是否有 `已推送到 ai-insight-public`）

---

## Step 5: 输出提示并停止（P0门控）

**必须输出以下文字，然后停止等待用户确认**：

```
📋 W{XX} 周报预览已发送，请查看KIM卡片确认内容。
确认无误后告诉我「发群」，我再执行群发。

当前发送状态：
- [x] 个人预览已发送
- [ ] 三个群未发送（等待确认）

⚠️ 我现在停止，等待你的确认。
```

**🔴 强制停止点**：输出上述内容后，必须等待用户回复。

### ✅ Step 5 退出条件

- [ ] 已输出等待提示
- [ ] 已停止，等待用户输入
- [ ] 未跳过此步骤进入 Step 6

---

## Step 6: 用户确认后发送群消息

### 用户回复「发群」或「确认」后，执行：

```bash
# 用 message 工具 + kimMixCard 发送到各群（需逐群发送）
```

### 发送到单个群的完整流程

如果用户只要求发送某个群：

**Step 6.1**: 用脚本生成 MixCard JSON
```bash
python3 scripts/build_insight_mixcard.py weekly --date YYYY-Www --output /tmp/card.json
```

**Step 6.2**: 读取 JSON，逐群发送

> 🔴 **MixCard 推送 P0 红线（#106-#110 教训汇总）**：
>
> 1. **target 格式**：群聊必须用 `target: "space:<groupId>"`，禁止直接传 groupId 数字
> 2. **禁止手动构造 kimMixCard JSON**：必须用脚本生成文件 → `read` 读取 → 传入 `kimMixCard` 参数。手动内联 = 格式错 = 空卡片
> 3. **不传 `message` 字段**：发 MixCard 时只传 `kimMixCard` + `target` + `channel`，不传 `message`（否则会泄露为卡片顶部/底部额外文案，或触发 `{{message}}` 占位符泄露）
> 4. **卡片内容结构 ≠ MD 全文**：Top 5 卡片版 = 标题 + 影响一句话 + 1条核心链接（禁止3段正文+3条来源全搬进卡片）；洞察卡片版 = 一句话结论 + 1条支撑链接
> 5. **卡片必须以"本周关键词"定调句开头**，30秒入口不可省
> 6. **林克洞察独立提取**，确保不被正则截断
> 7. **找不到源文件时报错退出**，禁止静默降级为空内容兜底卡片（空卡片比报错更危险）

```python
# 示例：逐群发送（伪代码，Agent 实际用 message 工具）
import json
with open("/tmp/card.json") as f:
    card = json.load(f)

groups = [
    ("研发效能中心全员群", "space:3705455482343722"),
    ("【AI生产力】MyFlicker产研", "space:6724050835415361"),
    ("【L5项目】研发线AI-Ready", "space:6646213728505891"),
]
for name, target in groups:
    message(channel="kim", target=target, kimMixCard=card)
    # 注意：不传 message 参数！
```

**Step 6.3**: 如果 API 返回错误
- ❌ **不要立即重试**
- ✅ 去群里确认是否已收到
- ✅ 如果已收到，向用户报告"已发送"
- ✅ 如果未收到，再考虑重试

### 禁止行为
- ❌ 禁止 API 错误后立即重试（会导致重复发送）
- ❌ 禁止手动内联编写 kimMixCard JSON（必须用脚本生成文件）
- ❌ 禁止发 MixCard 时传 `message` 字段（会导致 `{{message}}` 泄露或额外文案）
- ❌ 禁止用 `target: "<groupId>"` 发群（必须 `target: "space:<groupId>"`）

### ✅ Step 6 退出条件

- [ ] 所有目标群已发送（或用户指定的单个群已发送）
- [ ] 没有重复发送任何群
- [ ] 如有API错误，已确认群是否收到

---

## Step 7: 同步首页 + 外部版 + Git推送

### Step 7.1: 更新首页周报入口（P0，不可跳过）

```bash
# 自动更新内外版首页的周报入口卡片 + 日历JS数据
python3 scripts/update_homepage_weekly.py \
  --week YYYY-WXX \
  --title "第XX周（MM/DD - MM/DD）" \
  --desc "覆盖XX条资讯 · 关键事件1 · 关键事件2 · ..." \
  --month YYYY-MM \
  --day DD
```

**验证命令**：

```bash
for path in index.html public/index.html; do
    echo "$path: $(grep -c 'weekly-YYYY-WXX' $path) 处引用"
done
# 外部版也必须验证
echo "ai-insight-public/index.html: $(grep -c 'weekly-YYYY-WXX' ../ai-insight-public/index.html) 处引用"
```

### Step 7.2: 同步到public/ + 外部版

```bash
# 1. 同步到public/
cp 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html public/01-daily-reports/YYYY-MM/

# 2. 同步到外部仓库（会自动处理脱敏）
python3 scripts/sync_to_external.py --full --verify
```

### Step 7.3: Git推送

```bash
# 内部版
git add -A
git commit -m "📊 AI周报 YYYY-WXX"
git push origin main

# 外部版
cd ../ai-insight-public
git add -A
git commit -m "📊 AI周报 YYYY-WXX (public)"
git push origin main
```

### 验证四位置

```bash
WEEK=weekly-2026-W16; MONTH=2026-04
echo "① 内部周报: $([ -f "01-daily-reports/$MONTH/$WEEK.html" ] && wc -l < "01-daily-reports/$MONTH/$WEEK.html" | tr -d ' ' || echo '❌ 不存在') 行"
echo "② 内部首页: $(grep -c "$WEEK" index.html 2>/dev/null || echo 0) 处引用"
echo "③ 外部周报(public): $([ -f "public/01-daily-reports/$MONTH/$WEEK.html" ] && wc -l < "public/01-daily-reports/$MONTH/$WEEK.html" | tr -d ' ' || echo '❌ 不存在') 行"
echo "④ 外部仓库周报: $([ -f "../ai-insight-public/01-daily-reports/$MONTH/$WEEK.html" ] && wc -l < "../ai-insight-public/01-daily-reports/$MONTH/$WEEK.html" | tr -d ' ' || echo '❌ 不存在') 行"
```

### ✅ Step 7 退出条件

- [ ] 四位置验证全部通过
- [ ] Git push 成功（无冲突）
- [ ] 外部版同步成功（verify通过）

---

## Step 8: 输出四链接交付（P0强制）

**必须按此格式输出**：

```
## 📋 W{XX} 周报已完成 — 四链接自检

### 📊 周报
🔒 内部版周报：https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
🌐 外部版周报：https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html

### 🏠 首页
🔒 内部版首页：https://xiaoxiong20260206.github.io/ai-insight/
🌐 外部版首页：https://xiaoxiong20260206.github.io/ai-insight-public/
```

### ✅ Step 8 退出条件

- [ ] 四链接已输出
- [ ] 链接可点击访问
- [ ] 用户已收到最终交付

---

## 错误恢复指南

| 错误场景 | 恢复操作 | 注意事项 |
|----------|----------|----------|
| HTML不存在 | 执行 Step 3 生成HTML | 检查文件大小>50KB |
| preview已执行过 | 直接跳到 Step 5 输出等待提示 | 不要再执行preview |
| API返回错误 | 先去群里确认是否已收到 | 不要立即重试 |
| Git推送失败 | 检查网络，执行 `git pull --rebase` 后重试 | 解决冲突后继续 |
| 日期范围错误 | 重新执行 Step 1 日期计算 | 用Python脚本验证 |
| 日报索引缺失 | 检查周一到周日所有日报文件 | 补充缺失日期 |
| 群里收到重复消息 | 向用户承认错误，已记录到踩坑经验 | 下次不再犯 |

---

## 质量检查清单（全部打勾才算完成）

### 内容质量
- [ ] 日期范围正确（周一到周日）
- [ ] Top 5 有代表性、不重复、覆盖多个板块
- [ ] 周度洞察有深度，不是日报洞察的简单罗列
- [ ] Top5和周度洞察格式统一（列表项格式）
- [ ] 日报索引完整（周一到周日所有已有日报）

### 技术质量
- [ ] HTML文件存在且 > 50KB
- [ ] 所有链接可达（无404）
- [ ] **Top 5 卡片有来源超链接**（`<a href>` 格式）
- [ ] **各板块事件表格的事件列和来源列有超链接**
- [ ] 内部版首页git push成功
- [ ] 外部版同步成功（verify通过）
- [ ] 四位置验证全部通过

### 推送质量
- [ ] preview只执行了一次
- [ ] 发送前用户已确认
- [ ] API错误时没有立即重试
- [ ] 没有重复发送任何群

---

## 踩坑经验索引

| # | 错误 | 预防措施 |
|---|------|----------|
| 74 | KIM API返回错误≠消息未投递 | API错误后先确认群是否收到 |
| 75 | 日期范围算错 | Step 1 强制日期验证 |
| 76 | 重复preview | Step 4 明确"仅一次" |
| 77 | 未确认就发群 | Step 5 强制停止点 |
| 78 | Git未推送 | Step 7 推送验证 |
| 79 | 日报索引缺失 | Step 2 完整性检查 |
| 80 | 执行前未召回踩坑 | Step -1 强制召回 |
| 81 | preview后重复sync | --preview 已自动完成 sync+push，Step 7 只需验证不需重跑 |
| 106 | MixCard {{message}} 占位符泄露为明文 | 发 MixCard 时不传 message 字段；卡片 kimMd 内容中禁止 {{message}} 占位符 |
| 107 | 群发用 groupId 直传 vs space:前缀格式不一致 | KIM 发群必须用 `target: "space:<groupId>"`，禁止直接传 groupId |
| 108 | 手动构造 kimMixCard JSON 对象格式错误 | 禁止手动内联编写，必须用脚本生成文件 → read → 传入 |
| 109 | PROJECT_ROOT 指向错误目录 → 找不到文件 → 空内容兜底卡片 | 动态检测项目根目录（检查 01-daily-reports/），找不到文件报错退出而非静默兜底 |
| 110 | 卡片内容直接复用 MD 全文 → 10屏纯文本无锚点 | 卡片版结论先行+精简有锚；Top5=标题+1句话+1链接；洞察=结论+1链接 |
| 111 | 周报HTML无来源超链接 → 事件表格纯文字，与日报HTML/KIM卡片不一致 | Step 1提取URL → Step 2 MD带链接 → Step 3 HTML `<a href>` 链接；Top 5卡片source行+各板块表格事件/来源列 |
| 112 | 周报HTML/MD包含KIM Doc链接 → 外发页面不应包含内部平台链接 | 周报生成时禁止在HTML/MD中添加 docs.corp.kuaishou.com 链接；KIM Doc链接只在KIM MixCard推送时使用（卡片内也不放，已于W19确认删除） |
| 113 | 外部版周报"深度调研"链接文案问题 → "完整版"暗示有内部版本 | 外部版周报中深度调研链接文案统一为"深度调研"，不加"完整版"后缀，避免暗示存在内部版本 |
| 114 | 外部版周报含"林克/沈浪/快手"等内部身份 → 外发页面不应暴露内部人员/组织信息 | 外部版周报HTML中所有"林克"→"Link"，"沈浪"/"快手"/内部平台链接全部清除；内部版保留原署名；脱敏脚本需覆盖周报HTML（目前只处理首页） |
| 115 | 外部版全量脱敏遗漏 → 深度调研/日报/首页/订阅页等也含敏感词 | 每次发布前必须全量扫描 public/ 和 ai-insight-public/ 下所有HTML/MD/JSON文件，确保零残留；脱敏规则15类（林克→AI洞察, 沈浪→空, 快手→某公司, KATE→Agent平台, 天策→数据平台, 天玑→数据分析平台, KwaiBI→BI平台, CodeFlicker→AI IDE, Titi→数据Agent, SKILL.md→技能定义文件, 小无相功→自进化体系, docs.corp→#internal-link, KIM Doc→内部文档, shenlang→空） |

---

## 默认推送群（v1.0）

| 群名 | groupId |
|------|---------|
| 研发效能中心全员群 | `3705455482343722` |
| 【AI生产力】MyFlicker产研 | `6724050835415361` |
| 【L5项目】研发线AI-Ready | `6646213728505891` |

---

## 关键教训

> **"有workflow文档但不遵守，比没有文档更危险——因为你以为有保障其实没有。"**

今天的根本问题不是"不知道规则"，而是"在压力下绕过规则"。长工作流尾部心态急躁，想一步到位，反而一步错步步错。

**结构性保障**：
- Step -1 的"执行前踩坑召回"不是建议，是强制门控
- Step 5 的"强制停止点"不是建议，是门控
- Step 6 的"禁止立即重试"不是提醒，是红线
- 四链接输出不是可选项，是交付标准

**一遍做对的秘密**：
- 不是靠个人努力
- 而是靠结构性保障
- 每一步都有退出条件
- 每一个错误都有恢复指南
