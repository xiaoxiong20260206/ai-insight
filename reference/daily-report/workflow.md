# AI日报执行流程 (v7.0 精简版)

> **版本**: v7.0 (2026-05-11: 精简版)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前必读（2条）

1. **续接必须先resume**: `uv run scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD`
2. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`

---

## 流程总览

```
Step 1: 搜索调研 → orchestrator complete --step 1
Step 2: 内容生成 → orchestrator complete --step 2
Step 3+4: finalize → orchestrator finalize（一键命令，内部自动执行5个子步骤）
Step 5: KIM推送 → build_insight_mixcard.py → message(kimMixCard)
Step 6: 知识沉淀(Harvest) → 检查复用价值 → 写入knowledge包（P0#15强制）
```

---

## Step 0.5: 实时热点探针

搜索当日AI热点，识别 Top 3-5 热点关键词。**时间窗口**: N日日报 = N-1日08:00 ~ N日08:00。

搜索关键词必须包含日期锚定词（"today"/"今天"/完整日期），禁止泛日期搜索。

---

## Step 1: 两层搜索 (L1→L2)

**⚠️ 搜索硬限制（P0红线#18d，2026-06-22新增）：总次数≤8，每板块海外1次+微信1次**

| 板块 | 海外关键词 | 国内关键词 |
|------|-----------|-----------|
| 🧠 大模型 | "OpenAI GPT latest news today" | "DeepSeek 最新" |
| ⌨️ AI Coding | "OpenAI Codex, Cursor, Claude Code news" | "Trae 字节 AI编程, CodeGeeX 智谱" |
| 📱 AI应用 | "AI application news today" | "MiniMax 海螺AI, 智谱GLM, Kimi 更新" |
| 🏭 AI行业 | "AI startup funding today" | "AI 融资 中国 2026" |
| 🔄 企业转型 | "enterprise AI transformation" | "企业 AI 转型 案例" |

**重点产品/公司搜索补充**（热点日优先搜，非热点日可跳过）：
- **OpenAI Codex**: "Codex CLI update" / "Codex agent coding"
- **MiniMax**: "MiniMax M2" / "海螺AI 更新"
- **智谱AI**: "智谱 GLM" / "AutoGLM"
- **腾讯研究院**: "腾讯研究院 AI"

**搜索配额（严格执行）**：
- Step 0.5 热点探针：≤2次（1海外+1国内）
- Step 1 板块搜索：5板块×2=10次 → **实际控制在6次以内**（合并相近板块的搜索）
- **总计：≤8次搜索**
- ❌ 超过8次 = P0违规，需要消耗1.2M input的30次搜索绝不会重演

微信公众号搜索：先账号搜索（机器之心/量子位/新智元/宝玉），再话题搜索。

完成标记:
```bash
uv run scripts/ai_daily_orchestrator.py complete --step 1 --context "搜索N个源; 热点: ...; 选定N条(海外N/国内N)"
```

---

## Step 2: 内容生成

生成 `data/daily-content-YYYY-MM-DD.json` (JSON数据) + `01-daily-reports/YYYY-MM/YYYY-MM-DD.md` (Markdown)。

### ⛔ P0铁律：只能用Step 1搜索结果，禁止从训练记忆补充内容

**时间窗口：N日日报 = N-1日08:00 ~ N日08:00 之间的新闻**

- ❌ **禁止**：把Step 1没有搜到的新闻加入日报（即使模型"知道"那条新闻是真实的）
- ❌ **禁止**：把超出时间窗口的旧新闻放入日报（即使内容本身是真实的）
- ❌ **禁止**：用旧新闻的URL + 修改日期来凑数
- ✅ **允许**：对Step 1搜到的条目做提炼、改写、分类
- ✅ **允许**：deep_focus、pattern_insight_html、overview 等分析内容可基于本周期内的新闻自由推理

**执行方式**：Step 2开始前，先列出Step 1拿到的所有原始条目（标题+URL），只从这些条目里选；最终生成的news条目数量≤Step 1原始条目数量。

**JSON必要字段**: tabs(5个板块各含news+deep_focus+pattern_insight_html) + overview + heat_trend + coverage + watch_list

完成标记:
```bash
uv run scripts/ai_daily_orchestrator.py complete --step 2 --context "N条(海外N/国内N), N板块; 微信N条"
```

完成后orchestrator自动执行URL抽检(Step 2.7)。

---

## Step 3+4: Finalize（一键命令）

```bash
uv run scripts/ai_daily_orchestrator.py finalize --date YYYY-MM-DD
```

finalize内部自动执行：
1. URL抽检 → 2. 质量门(硬性阻断/软性警告) → 3. HTML生成+自校验 → 4. 首页更新 → 5. 部署+外部同步+Pages验证

**质量门分级**:
- ❌ 硬性失败（板块缺失/JSON结构错/HTML空壳）= 阻断，必须回到Step 1/2重做
- ⚠️ 软性失败（搜狗URL占比/链接格式/覆盖度略低）= 警告不阻断

**finalize失败时**: 检查错误信息 → 区分硬性/软性 → 硬性重做/软性可继续push

---

## ⛔ P0红线：首页修改唯一入口（2026-06-29 沉淀）

**`index.html` 的所有修改必须通过 `update_homepage.py`，禁止手动编辑。**

根因：2026-06-29 W26周报修复中，cron agent手动编辑index.html导致7类问题（日历映射错误、卡片链接错误、外部版脱敏绕过、内部版身份覆盖等）。手动操作绕过脚本=绕过脱敏流程=绕过验证。

| 操作 | ✅ 正确做法 | ❌ 禁止做法 |
|------|-----------|-----------|
| 更新日历 | `update_homepage.py YYYY-MM-DD` 或 `--type weekly` | 手动编辑weeklyReportsData |
| 更新日报卡片 | `update_homepage.py` 自动处理 | 手动改href/text |
| 更新周报卡片 | `update_homepage.py --type weekly --week-day 周一` | 手动改weekly-report-card |
| 同步外部版 | `update_homepage.py`内自动调用`sanitize_html()` | 手动cp或编辑ai-insight-public/index.html |
| 修复首页问题 | 先修脚本/数据，再重跑`update_homepage.py` | 直接编辑index.html |

**如果`update_homepage.py`执行失败**：报错退出，不尝试手动修复。修复脚本的bug后重跑。

---

## Step 5: KIM推送

```bash
# 0. 同步订阅者（Appwrite → subscribers.json）
uv run --with requests scripts/sync_subscribers.py

# 1. 生成mixCard（脚本自带6锚点校验+kimMd格式校验+{{message}}扫描）
uv run scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary

# 2. 只给 {{OWNER_KIM_USERNAME}} 发MixCard全文版（P0 强制，防超时）
# message(channel=kim, action=send, kimMixCard=<inner card JSON>, target="{{OWNER_KIM_USERNAME}}", message="")
# ⚠️ kimMixCard必须传inner card格式（{config, blocks, updateMulti}在顶层），禁止传双层{card: {...}}
# ⚠️ message参数必须传空字符串""，禁止同时传message和kimMixCard（会导致{{message}}模板注入泄露）

# 3. 其他活跃订阅者：用子agent并行推送MixCard精简版（spawn一次，payload含订阅者列表+卡片JSON路径）
# ⚠️ 如果订阅者≤5人，可以直接逐一发送；如果>5人，必须用子agent并行，防止超时
# ⚠️ 子agent推送不阻断主流程，主流程发完{{OWNER_KIM_USERNAME}}后直接进入Step 5.5

# 4. 标记完成
uv run scripts/ai_daily_orchestrator.py complete --step 5
```

**推送策略（防超时，2026-06-18 修订）**：
- **{{OWNER_KIM_USERNAME}}**：主流程直接发送MixCard全文版（P0强制，不超时）
- **其他订阅者**：如果≤5人，逐一发送；如果>5人，spawn子agent并行推送，主流程不等
- **禁止群发**：所有推送均为私发
- **超时根因**：25人逐一发送=每人2-3分钟推理=50-75分钟=远超3600秒限制

### Step 5.5: 交付链接（P0 强制，每次日报完成必须输出）

推送完成后，**必须**向用户输出以下四个链接，方便自检内外版本是否都正确发布：

```
内部版：
1. 📄 当日日报：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/YYYY-MM/YYYY-MM-DD.html
2. 🏠 AI洞察首页：https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/

外部版：
3. 📄 当日日报：https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/YYYY-MM-DD.html
4. 🏠 AI洞察首页：https://xiaoxiong20260206.github.io/ai-insight-public/
```

**目的**：快速自检内部版（frontend-cloud）和外部版（GitHub Pages）是否都正常发布，防止某个版本静默失败而不知。

### Step 5.6: 首页完整性验证（P0 强制，2026-06-29 新增）

部署完成后，**必须**运行首页验证脚本，全部通过才算任务完成：

```bash
uv run scripts/verify_homepage.py --date YYYY-MM-DD
```

**准出标准**：所有 HARD 检查通过 = ✅ 准出；任何 HARD 失败 = 🚫 阻断，必须修复后重跑。

验证项包括：
- 三个版本首页文件存在（内部版/public/外部版）
- 内部版保留林克身份（头像/CSS class/文字）
- 外部版零敏感词（林克/沈浪/corp.kuaishou.com/快手/MyFlicker）
- 日历日报数据包含当日
- 日历周报数据包含本周周一+下周周一
- 日历无幽灵条目（引用的周报文件必须存在）
- 周报大卡片链接指向存在的文件
- 订阅按钮指向正确内网URL
- 内部版和public/内容一致
- 日历无重复周号、key格式正确

---

## Step 6: 知识沉淀（Harvest）— P0#15 强制，不可跳过

日报完成后，**必须**检查本次是否有复用价值的分析/对比/洞察：

```
□ 本次日报有复用价值的分析/对比/洞察吗？
  → 有 → 写入 knowledge/packages/ai-insight/ + 更新 INDEX.md + 更新 MEMORY.md 指针
  → 没有 → 简短声明"本次无 Harvest"并继续
```

**写入路径**：`knowledge/packages/ai-insight/wiki/insights-YYYY-MM-DD-daily-insights.md`（MyKnowledge KnowledgePackage 格式）

**典型Harvest内容**：
- 新出现的行业模式/规律（如"AI从聊天竞赛转向企业生产力平台"）
- 跨板块共同主题（如"成本战→结构性定价"）
- 人物/公司动态需更新追踪体系（如"Anthropic首超OpenAI企业采用率"）
- 新术语/新概念需记录

**不做 Harvest = P2 不通过**

---

## 搜索策略优化（2026-05-11新增）

### 问题：搜狗链接占比44%超阈值、URL截断、source篡改

### 优化措施:
1. **精准搜索优先**: 具体产品名+日期锚定 > 泛搜索
2. **微信账号搜索为主**: 机器之心/量子位/新智元/宝玉 > 话题搜索
3. **搜狗URL占比硬限制≤30%**: 超过则替换为微信公众号原文链接
4. **同报URL去重**: JSON生成后自动检测同一URL出现多次，保留一条
5. **URL可达性校验**: orchestrator Step 2.7自动抽检3个URL

---

## 失败自修复原则

1. 任何步骤失败 = 立即尝试修复，不停下来汇报
2. 修复路径优先级: 环境问题→直接替换重试; 数据问题→回步骤重做; 推送问题→切换路径
3. 最多重试3次
4. 完成优先于完美
5. fail loud, don't fail silent

---

_更新于 2026-05-11 · v7.0 · 精简版，529行→核心流程_