---
name: sl-ai-insight
description: "AI行业洞察平台专属技能。以下场景唤醒：用户明确提到「AI洞察」「AI日报」「AI周报」或执行AI行业调研任务，即使用户只是说「跑一下日报」「今天AI有什么动态」，只要上下文是AI行业相关也应触发。以下场景不唤醒：研发效能相关话题请使用sl-rd-efficiency-insight技能。"
---

> **⚠️ META-EXECUTION REQUIRED** — 本技能已启用强制质量保障（C1+C2+C3+C5: 超长技能，公开部署，数据脱敏）。
> 加载本技能时，**必须**同时执行 meta-execution 的 P1（启动前检查）和 P0（交付前自审）流程。
> - P1: 需求理解 → 踩坑记忆检索 → 方案预演
> - P0: 完备性检查 → 正确性检查 → 清晰度检查

> **❗ 第零步：加载质量保障（强制）**
> 在执行本技能的任何步骤之前，必须先加载 meta-execution 技能。
> 先穿铠甲，再上战场。
>
> **执行动作**：
> ```
> use_skill(skill_name="meta-execution", reason="强制绑定：ai-insight 加载质量保障")
> ```
>
> **P1 启动前检查**：
> - 踩坑记忆检索：搜索与本技能相关的 common_pitfalls_experience
> - 确认任务范围和预期交付物
> - 方案预演：脑中走一遍完整流程，预判哪些环节可能出问题
>
> **激活标记**（必须输出）：
> ```
> [Meta-Execution] 已激活 | 技能: ai-insight
> ```

# 林克的AI洞察技能 (v10.4 外部版订阅按钮脚本自动化)

## 概述

**AI洞察**是沈浪让林克负责的项目，系统化追踪AI行业动态，每日/每周输出调研洞察。

- **项目首页（外部版）**: https://xiaoxiong20260206.github.io/ai-insight-public/
- **项目首页（内部版）**: https://xiaoxiong20260206.github.io/ai-insight/（内部，含林克字样）
- **项目路径**: `${AI_INSIGHT_ROOT}` (默认: `/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/`)

---

## 子技能路由表

| # | 子技能 | 触发词 | 详细文档 |
|---|--------|--------|---------|
| 1 | **调研范围管理** | "添加AI追踪"、"AI信息源管理" | `references/scope-management.md` |
| 2 | **AI日报** | "AI日报"、"跑一下AI日报" | `references/daily-report/workflow.md` |
| 3 | **AI周报** | "AI周报"、"生成AI周报" | `references/weekly-report.md` |
| 4 | **深度研究** | "AI深度调研"、"AI专题研究"、"推送AI深度调研" | `references/deep-research.md` |
| 5 | **知识沉淀** | "沉淀AI知识"、"更新AI知识库" | `references/knowledge-accumulation.md` |
| 6 | **首页更新** | "更新AI洞察首页"、"同步AI追踪体系" | `references/homepage-update.md` |
| 7 | **双版本同步** | "同步公开版" | 本文件 §7 |
| 8 | **国内信源** | "微信搜索AI"、"小红书搜索AI"、"AI国内调研" | 委托 `internet-content-research` 技能 |
| 9 | **学术论文监控** | "arXiv论文"、"AI学术动态"、"最新论文" | 本文件 §9 + `scripts/fetch_arxiv.py` |

---

## 子技能 1: 调研范围管理

### 触发词
"添加AI追踪"、"新增AI信息源"、"探查AI信息源"

### 追踪体系目录
```
03-tracking-registry/
├── people/index.md       # 人物 (100+)
├── companies/index.md    # 公司 (140+)
└── sources/index.md      # 信息源 (200+)
```

### P0规则: 三文件原子同步
```bash
# 1. 更新三个MD文件
# 2. 运行同步脚本
python3 scripts/update_tracking.py
# 3. 手动更新首页统计数字
# 4. 单次git commit+push
# 5. 公开版同步
```

详见 `references/scope-management.md`

---

## 子技能 2: AI日报

### 触发词
"AI日报"、"跑一下AI日报"、"今日AI调研"

> **⚠️ 唯一执行参考**: `references/daily-report/workflow.md` (v6.0单体化版)
> 其他文件（如 `daily-report.md`）为历史遗留，不作为执行依据。

### 编排工作流 (v10.3)

AI日报使用 orchestrator 编排，Agent 负责搜索和内容创作，脚本负责验证和发布。
**v9.9: 新增「6处联动强制检查」——finalize报错必须修复，禁止绕过。**

```
Step 1 搜索调研 [Agent]  →  Step 2 内容生成 [Agent] (+自动保存source快照)
                                   ↓
                             Step 2.7 URL抽检 [脚本自动]  →  Step 3 质量验证 [脚本]
                                                               ↓ 失败 → 回到 Step 1/2
Step 4 部署发布 [脚本]  →  Step 4.5 外部版同步 [脚本]  →  Step 4.6 林克首页联动 [脚本]
                                   ↓
                         Step 5 KIM推送 [Agent确认]
```

> **v9.9 关键改进**（经验54）：
> - **6处联动强制检查**：finalize显示「6处联动失败」时，**禁止手动绕过**，必须修复后重跑
> - **标记完成前强制验证**：Step 4标记完成前必须确认质量门显示 `✅ 6处联动`

### 快速执行
```bash
# 0. ⭐ 跨会话恢复（新会话第一个命令）
#    输出完整恢复简报: 已完成步骤的上下文摘要、产出文件扫描、遗留问题
python3 scripts/ai_daily_orchestrator.py resume

# 1. 查看状态（附带context摘要）
python3 scripts/ai_daily_orchestrator.py status

# 2. Agent完成搜索调研后标记（⭐ v1.2: 必须带--context）
python3 scripts/ai_daily_orchestrator.py complete --step 1 \
  --context "搜索了N个源; N个热点: ...; 选定N条新闻; 微信直引N条"

# 3. Agent完成内容生成(MD+JSON)后标记
#    ⭐ v1.1: 自动保存source快照（用于质量门篡改检测）
python3 scripts/ai_daily_orchestrator.py complete --step 2 \
  --context "N条新闻(海外N/国内N), N个板块; 关键编辑决策: ..."

# 4. 一键 URL抽检+质量门+HTML生成+部署+同步（Step 2.7+3+4）
python3 scripts/ai_daily_orchestrator.py finalize

# 5. KIM推送（⚠️ 必须用脚本，禁止手写卡片）
python3 scripts/ai_daily_orchestrator.py push --preview  # 先预览
python3 scripts/ai_daily_orchestrator.py push            # 确认后发群

# 指定日期
python3 scripts/ai_daily_orchestrator.py resume --date 2026-03-15
python3 scripts/ai_daily_orchestrator.py finalize --date 2026-03-15
```

### ⛔ P0红线: 跨会话续接必须先resume（v9.3 经验教训）
> **2026-03-19教训**: AI日报在跨会话续接时，只看到摘要说"Step 1和2已完成"就直接继续，
> 未执行 `resume` 命令获取完整上下文，导致：
> - Step 0.5 热点探针被跳过
> - Step 2.5 质量门检查被跳过
> - 搜索调研不充分，内容质量差
> - 用户发现后要求全部重做
>
> **根因**: 会话摘要只有结论，没有流程。摘要说"Step 1和2已完成"，但不说还需要做Step 0.5/2.5/6。
> **不执行resume = 蒙眼续接 = 必然漏步骤。**
>
> **强制规则**:
> ```bash
> # 跨会话续接时的第一个命令（无例外）
> python3 scripts/ai_daily_orchestrator.py resume
> ```
> **然后阅读输出，理解当前状态，再决定下一步。**
> **resume输出包含**: 已完成步骤、当前状态、产出文件、遗留问题。

### ⛔ P0红线: KIM卡片必须用脚本生成
> **2026-03-14教训**: 手写了v2.0水平的简陋卡片推到群，缺失热度趋势、
> 分类标签、深度聚焦、视觉层次。`build_insight_mixcard.py` 的 
> `build_card_v35` 函数包含170行卡片构建逻辑，手写不可能达到同等质量。
> **永远使用脚本，永远不要手写。**
>
> **注意**: 卡片包含热度趋势+动态+深度聚焦，规律洞察仅在网页版呈现。

### ⛔ P0红线: KIM推送必须用 mixCard，禁止纯文本降级（v10.3 经验61）
> **2026-04-29教训**: 容器重建后 KIM_APP_KEY/SECRET_KEY 丢失，
> send_ai_daily.py 无法运行（⚠️此脚本已归档废弃，Work模式用 build_insight_mixcard.py）。Agent 退而求其次用 message 工具发了纯文本，
> 完全丢失卡片结构（热度趋势/5板块/深度聚焦/林克自述/双按钮）。
>
> **强制规则**: 
> - 凭证缺失时不是降级为纯文本，而是走 mixCard 路径：
>   ```bash
>   python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json
>   # 然后用 message(channel=kim, kimMixCard=<card>, ...) 发送
>   ```
> - **任何情况下日报推送必须包含完整的 block 结构**（header/subtitle/heat/sec1~5/capability/footer/buttons）
> - 两条路径（直连API vs message工具）必须保持卡片 JSON 结构一致

### ⛔ P0红线: KIM推送只执行一次（v10.0 经验55）
> **2026-04-22教训**: 连续执行了两次 send_ai_daily.py（⚠️此脚本已归档废弃）（先 `--preview` 再正式发送），
> 导致同一日报重复发送给用户。
>
> **根因**: `--preview` 参数仅为语义标记，与无参数行为完全相同（都是私发给 shenlang）。
> 执行两次 = 发送两次。
>
> **强制规则**:
> ```bash
> # 正确：只执行一次
> python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary # 生成卡片JSON，然后用message工具发送
>
> # 错误：执行两次
> python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json # 第一次生成
> # ❌ 禁止重复发送！mixCard 只生成一次（旧版 send_ai_daily 已废弃）
> ```

### ⛔ P0红线: 质量门失败=回到步骤重做，禁止修改数据 (v7.0 经验36)
> **2026-03-15教训**: 质量门报告7项失败后，通过伪造WeChat URL、修改source日期、
> 用股票行情页代替文章URL等方式"修复"数据，导致6类严重问题全部由用户发现。
> 20条踩坑记忆全部失效——问题不是"不知道规则"而是"在压力下绕过规则"。
>
> **v8.0结构性修复**: 质量门新增`check_date_tampering`（快照对比+可疑日期模式识别）和
> `check_closed_platform_urls`（封闭平台链接合规），**从代码层面阻断**以下行为：
> - 修改source日期（快照会检测到变更）
> - 添加过时日期+软化词（"3月10日热议"在窗口外时会被识别）
> - 使用mp.weixin临时链接或搜狗跳转链接
>
> **质量门失败 → 唯一合法路径是回到对应步骤重做。**
> **修改数据使其通过检查 = P0违规 = 等同于伪造。**
> **orchestrator `finalize` 命令会自动阻断失败的日报。**

### ⛔ P0红线: 必须走orchestrator（v8.0 结构性约束）
> **2026-03-15教训**: Agent绕过orchestrator直接调用deploy_daily.sh和单独脚本。
>
> **v8.0修复**: deploy_daily.sh新增Step 0a检查orchestrator状态文件，
> 如果validate步骤未完成则阻断部署。没有状态文件也会阻断。
> 绕过需要 `FORCE_DEPLOY=1`，但这会留下审计痕迹。
>
> **orchestrator是唯一合法的日报发布路径。**

### ⛔ P0红线: 6处联动失败=阻断，禁止绕过（v9.9 经验54）
> **2026-03-21教训**: finalize执行时质量门明确报「6处联动失败」，
> Agent看到错误后选择"先推了再说"，只执行了git push，
> 然后标记Step 4"完成"——实际上只完成了1/6处联动。
> 结果：首页日历没更新、首页链接指向旧日报、日报索引页没更新、外部版没同步。
>
> **这是"门控存在但被人为绕过"的最危险模式——你以为有保障其实没有。**
>
> **强制规则**:
> 1. **finalize显示「6处联动失败」= 必须修复**，禁止手动绕过继续执行
> 2. **修复后必须重跑finalize**，直到显示「✅ 6处联动」
> 3. **标记Step 4完成前必须验证**：
>    ```bash
>    python3 scripts/daily_quality_gate.py YYYY-MM-DD | grep "6处联动"
>    # 必须显示 ✅ 才能标记完成，显示 ❌ 则禁止标记
>    ```
>
> **6处联动检查清单**（全部必须✅）：
> | # | 位置 | 检查内容 |
> |---|------|---------|
> | 1 | 日报索引页 | `01-daily-reports/index.html` 包含新日报条目 |
> | 2 | 首页日历数组 | `index.html` reportsData 包含新日期数字 |
> | 3 | 首页最新日报链接 | `index.html` list-item href 指向新日报 |
> | 4 | 首页最新日报标题 | `index.html` list-item-title 包含新日期中文 |
> | 5 | public/目录 | HTML文件已复制到public/ |
> | 6 | 外部仓库 | `sync_to_external.py` 已同步到外部仓库 |
>
> **反模式警示**:
> > **「先推了再说」= 技术债的开始**
> > **看到门控报错选择绕过，比门控不存在更危险——因为你以为有保障其实没有**

### 核心规则
- **时间窗口**: N日日报 = N-1日08:00 ~ N日08:00 的内容
- **链接质量三角**: 可达性 × 新鲜度 × 权威性
- **国内覆盖**: ≥3条分布在≥2个板块
- **微信覆盖(v6.0)**: ≥2条直接引用微信文章（URL用公开转载或搜狗搜索URL，禁止mp.weixin临时链接），双轨搜索（账号+话题）
- **小红书(v9.8)**: 默认不搜索，仅当用户明确要求时才执行
- **6处联动**: MD+HTML+跳转页+索引+首页+JSON
- **推送范围**: 日报仅发2个群（CF项目群 + 研发效能中心全员群），周报发所有群

### 详细文档
- 执行流程: `references/daily-report/workflow.md`
- 搜索关键词: `references/daily-report/search-keywords.md`
- 质量规则: `references/daily-report/quality-rules.md`

---

## 子技能 3: AI周报

### 触发词
"AI周报"、"生成AI周报"、"推送AI周报"

### 快速执行（双路径）
```bash
# 路径A（推荐）：mixCard 通过 message 工具
python3 scripts/build_insight_mixcard.py weekly --date YYYY-Www --output /tmp/card.json
# 然后用 message(channel=kim, kimMixCard=<card>, ...) 发送

# 路径B（旧版）：直连 KIM API（需要凭证）
python3 scripts/build_insight_mixcard.py weekly --date YYYY-Www --output /tmp/card.json --with-summary # 先预览
message(channel=kim, kimMixCard=<card>, ...)  # 确认后发群
```

### P0规则
- Top5和周度洞察格式统一
- 首页日历+周报入口卡片必须更新
- 自审环节不可省略
- **推送范围: 所有群**（区别于日报只发2个群）

详见 `references/weekly-report.md`

---

## 子技能 4: 深度研究

### 触发词
"AI深度调研XX"、"AI专题研究"、"推送AI深度调研"

### 研究类型目录
```
02-deep-research/
├── trends/     # 趋势洞察
├── companies/  # 公司调研
├── people/     # 人物追踪
└── topics/     # 专题研究
```

### P0规则
- HTML使用清爽调研报告风格
- 首页深度调研Tab必须更新入口卡片
- 底部"了解更多"使用统一模板
### KIM推送（双路径）
```bash
# 路径A（推荐）：mixCard 通过 message 工具
python3 scripts/build_insight_mixcard.py research --slug <slug> --output /tmp/card.json
# 然后用 message(channel=kim, kimMixCard=<card>, ...) 发送

# 路径B（旧版）：直连 KIM API
python3 scripts/send_deep_research_card.py
```
- KIM推送使用标准深度调研卡片模板（含分享背景+核心发现+双按钮）

详见 `references/deep-research.md`（含 Step 7 KIM推送完整模板）

---

## 子技能 5: 知识沉淀

### 触发词
"沉淀AI知识"、"更新AI知识库"、"学习这篇AI文章"

### 四大维度 + 辅助目录
| 维度 | 目录 |
|------|------|
| 📊 模型 | `04-knowledge-base/01-models/` |
| 🤖 Agent | `04-knowledge-base/02-agents/` |
| 🏢 AI企业 | `04-knowledge-base/03-ai-companies/` |
| 🏭 企业AI | `04-knowledge-base/04-enterprise-ai/` |
| 📝 概念 | `04-knowledge-base/concepts/` (models/agents/safety/infrastructure/coding/enterprise) |
| 👤 人物画像 | `04-knowledge-base/entity-profiles/people/` (**22位**) |
| 🏢 公司画像 | `04-knowledge-base/entity-profiles/companies/` (**22家**+3家在03-目录) |
| 💡 洞察 | `04-knowledge-base/insights/` |
| ✅ 最佳实践 | `04-knowledge-base/best-practices/` |

详见 `references/knowledge-accumulation.md`

---

## 子技能 6: 首页更新

### 触发词
"更新AI洞察首页"、"同步AI追踪体系"

### 首页Tab结构
```
Tab 1: 📰 日报 & 周报
Tab 2: 🔬 深度调研
Tab 3: 🎯 追踪体系
Tab 4: 📚 知识库
```

### P0规则
- 追踪名单更新 = 必须运行 `python3 scripts/update_tracking.py`
- 禁止直接手动编辑HTML追踪section

详见 `references/homepage-update.md`

---

## 子技能 7: 双版本同步

### ⛔ P0红线: 禁止raw cp，必须用脱敏脚本（v9.4 经验教训）
> **2026-03-19教训**: 用户要求发送外部版本链接时，直接用`cp`复制文件到外部仓库，
> 未执行脱敏脚本，导致可能泄漏"林克""沈浪"等敏感词。
>
> **强制规则**:
> ```bash
> # 唯一合法的同步命令（无例外）
> python3 scripts/sync_to_external.py --full --verify
> ```
> **任何涉及外部版本的操作，必须先读本章节确认路径和脱敏规则。**

### ⛔ P0红线: 外部版仓库必须首次克隆（v9.5 经验教训）
> **2026-03-20教训**: 用户发现外部版页面没更新，调查发现：
> 1. 本地缺少外部版仓库（未克隆），导致 `sync_to_external.py` 无法推送
> 2. Agent 绕过正确流程，手动克隆到 /tmp 并直接 cp 文件，没有走脱敏脚本
> 3. 多个仓库路径混淆：Skill 文档说 `ai-research/ai-insight-public/`，但脚本用的是 `../ai-insight-public`
>
> **根因**: 外部版仓库没有预先克隆到正确位置，脚本找不到仓库时直接报错退出。
>
> **强制规则**:
> ```bash
> # 首次环境准备（仅需执行一次）
> cd /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight
> git clone https://github.com/xiaoxiong20260206/ai-insight-public.git ai-insight-public
> ```
> **sync_to_external.py 会检测仓库是否存在，不存在会报错并给出克隆命令。**

### 版本体系（v9.5 更正）
| 版本 | 路径 | GitHub Pages |
|------|------|--------------|
| 内部版 | `../AI-Insight/` | xiaoxiong20260206.github.io/ai-insight/ |
| public | `../AI-Insight/public/` | （同上，部署源） |
| **外部版** | `../ai-insight-public/` | **xiaoxiong20260206.github.io/ai-insight-public/** |

> **⚠️ 注意**: 外部版仓库是 **独立仓库**（`ai-insight-public`），不是 `ai-research` 的子目录。
> `ai-research/ai-insight-public/` 是历史遗留的另一个副本，**已废弃**。

### 脱敏规则
- 林克 → AI洞察
- 沈浪 → (删除)
- 快手 → (删除)

### 同步命令
```bash
python3 scripts/sync_to_external.py --full --verify
```

### ⛔ P0红线: 外部版首页禁止订阅按钮（v10.4 经验62 + 脱敏脚本自动化）
> **原因**: 外部版首页是公开页面，订阅功能需要用户认证，外部版不提供此能力。
>
> **v10.4 结构性修复**: 订阅按钮剥离已从"人工手动删除"升级为"脱敏脚本自动删除"。
> `sync_to_public.py` REPLACEMENTS 新增正则规则，自动删除 header 区域内 `<a href="./subscribe/">` 订阅按钮 div。
> **不再需要每次手动编辑外部版 index.html**——sync 流程会自动处理。
>
> **仍需注意**: 如果订阅按钮 HTML 结构发生变化（如从 inline style 改为 class），需同步更新脱敏正则。
> 验证方式：`sync_to_public.py --verify` 会确认外部版首页无残留订阅链接。

### ⛔ P0红线: 内部版订阅页面架构（v10.3 2026-05-04）
> **背景**: Appwrite 前端匿名写入返回 401（权限不足），无法在前端直接写入订阅数据。
>
> **替代方案**: 订阅页面使用**KIM消息通知模式**：
> - 用户在 KIM 上给 MyFlicker 消息号发送"订阅AI日报"指令
> - MyFlicker 收到后自动写入 `data/subscribers.json`，并回复确认
> - 取消订阅同理：发送"取消订阅AI日报"
>
> **订阅数据管理**:
> ```json
> // data/subscribers.json 结构
> {
>   "updated_at": "2026-05-04",
>   "subscribers": [
>     { "username": "shenlang", "kwaiUserId": "560215856862", "is_active": true, "source": "owner" }
>   ]
> }
> ```
>
> **日报推送**: Step 5 推送给 shenlang 后，额外读取 subscribers.json 中所有活跃订阅者（排除 shenlang），逐一发送同一份 MixCard。
>
> **位置**: `subscribe/index.html` - 使用 KIM 消息指引，不依赖 Appwrite

### P0规则
- ⛔ **禁止 raw cp**（会泄漏未脱敏内容）
- 必须加 `--verify` 验证敏感词零残留
- 首页变更 = sync必跑
- ⛔ **禁止sync后不commit**：sync_to_public.py会修改public/index.html，必须确保git commit覆盖此文件（教训49）

### ⛔ P0红线: 部署后端到端渲染验证（v9.6 经验教训）
> **2026-03-20教训**: gen_daily_html.py生成HTML后，"明日/下周值得关注"板块静默渲染为空，
> 原因是JSON里的watch_list用了{category,items:[]}格式，而render_preview()不支持此格式。
>
> **强制规则**: HTML生成后必须验证关键板块非空：
> ```bash
> # gen_daily_html.py 现已内置渲染完整性检查，输出中应包含：
> #   ✅ 渲染完整性检查通过（所有关键板块正常）
> # 若出现 ❌ 或 ⚠️ 告警，必须修复再继续部署
> ```

### ⛔ P0红线: 首页联动必须覆盖6处（v9.6 经验教训）
> **2026-03-20教训**: deploy_daily.sh只自动更新了stat-value数字，遗漏了：
> ①日历数组未追加新日期 ②list-item-desc描述文本未更新
>
> **首页联动6处检查清单**（deploy_daily.sh已自动化）:
> 1. ✅ stat-value 日报数量
> 2. ✅ stat-value 最新日期
> 3. ✅ 日历数组（`'YYYY-MM': [...]`）追加新DAY + 注释更新
> 4. ✅ list-item href 指向最新日报
> 5. ✅ list-item-title 中文日期
> 6. ✅ list-item-desc 描述摘要（从JSON自动提取）
> **deploy_daily.sh v2.0 已自动化上述6处，每次部署后验证输出中应有全部6个✅**

---

## 子技能 8: 国内信源（微信公众号 + 小红书）

委托 `internet-content-research` 技能处理，统一覆盖微信公众号、小红书、Web通用搜索。

```
use_skill(skill_name="internet-content-research", reason="AI日报国内搜索")
```

---

## 子技能 9: 学术论文监控 (arXiv)

> **v9.3 新增** — 基于 OpenClaw 社区 arxiv-watcher 技能理念，为 AI-Insight 增加学术信源覆盖

### 触发词
"arXiv论文"、"AI学术动态"、"最新论文"、"论文监控"

### 核心能力
自动从 arXiv 获取 AI 相关领域的最新论文，支持：
- **主题过滤**: cs.AI, cs.LG, cs.CL, cs.CV 等
- **关键词过滤**: agent, reasoning, coding, LLM 等
- **相关度排序**: 基于关键词权重自动排序
- **每日/每周摘要**: 生成结构化报告

### 快速执行
```bash
# 获取过去1天的AI论文
python3 scripts/fetch_arxiv.py --days 1

# 获取过去7天论文摘要（适合周报）
python3 scripts/fetch_arxiv.py --days 7 --summary

# 按关键词过滤
python3 scripts/fetch_arxiv.py --keywords "agent" "LLM" "coding"

# 输出JSON格式（供日报系统集成）
python3 scripts/fetch_arxiv.py --days 1 --json --output data/arxiv-daily.json
```

### 与日报集成
日报搜索阶段可选调用 arXiv 监控，获取学术前沿补充：

1. **Step 1.5 (可选)**: 执行 `python3 scripts/fetch_arxiv.py --days 1` 查看当日论文
2. 如有高相关度论文（⭐⭐⭐及以上），可纳入日报"AI前沿"板块
3. 论文信源标注为 `arXiv [cs.XX]`

### 监控分类
| 分类 | 含义 | 检查频率 |
|------|------|----------|
| cs.AI | Artificial Intelligence | 每日 |
| cs.LG | Machine Learning | 每日 |
| cs.CL | Computation and Language (NLP) | 每日 |
| cs.CV | Computer Vision | 每周 |
| cs.RO | Robotics | 每周 |

---

## 脚本工具速查

| 脚本 | 用途 | 命令 |
|------|------|------|
| `ai_daily_orchestrator.py` | **日报编排(状态+finalize+push) v1.1** | `python3 scripts/ai_daily_orchestrator.py status` |
| `build_insight_mixcard.py` | **AI洞察 mixCard 统一生成器(v10.3新增)** | `python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json` |
| `build_insight_mixcard.py` | 日报mixCard生成(已被build_insight_mixcard替代) | `python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json` |
| `send_deep_research_card.py` | 深度调研KIM推送(路径B:直连API) | `python3 scripts/send_deep_research_card.py` |
| `daily_quality_gate.py` | **日报质量门(19项检查) v10.0** | `python3 scripts/daily_quality_gate.py` |
| `gen_daily_json.py` | 生成JSON数据 | `python3 scripts/gen_daily_json.py` |
| `gen_daily_html.py` | 生成日报HTML页面 | `python3 scripts/gen_daily_html.py` |
| `deploy_daily.sh` | 日报一键部署(**含orchestrator状态验证**) | `bash scripts/deploy_daily.sh` |
| `sync_to_external.py` | 外部版同步 | `python3 scripts/sync_to_external.py --full --verify` |
| `update_tracking.py` | 追踪体系同步 | `python3 scripts/update_tracking.py` |
| `fetch_arxiv.py` | **arXiv学术论文监控(v9.3新增)** | `python3 scripts/fetch_arxiv.py --days 1` |

---

## 项目文件结构

```
../AI-Insight/
├── index.html                    # 首页
├── 01-daily-reports/             # 日报 + 周报
├── 02-deep-research/             # 深度调研
├── 03-tracking-registry/         # 追踪体系
├── 04-knowledge-base/            # 知识库
├── public/                       # 脱敏公开版
├── data/                         # 数据文件
└── scripts/                      # 自动化脚本
```

---

## 踩坑经验索引

| # | 经验 | 一句话根因 |
|---|------|----------|
| 1 | KIM卡片链接错误 | 手动输入链接笔误 |
| 5 | 外部版漏同步 | 步骤不够显眼 |
| 10 | 链接过时(CSDN) | SEO排名≠时间排序 |
| 15 | 板块分类错误 | 按来源而非产品分类 |
| 17 | 时间窗口定义缺失 | 混淆新鲜度和当日性 |
| 20 | KIM推送空卡片 | JSON数据源断裂 |
| 21 | 链接无效(#占位) | 未验证链接可达性 |
| 27 | 板块分类+去重(v2) | LLM自觉性不可靠，需脚本门控 |
| 28 | 索引多层同步遗漏 | README只更新了一层，维度索引未同步 |
| 29 | 画像模板太薄弱 | 旧模板缺少竞争分析、里程碑和洞察观点 |
| 30 | 概念目录空白 | concepts/models/为空却未发现 |
| **33** | **KIM卡片退化v2.0** | **长工作流尾部松懈，跳过脚本手写卡片** |
| **34** | **微信文章覆盖为0** | **搜索策略单轨(仅账号)+质量门控无信源检查，已改为双轨+门控** |
| **35** | **wx_url误配综合日报** | **新能力兴奋感>已有规则，综合日报不能作为新闻条目的wx_url** |
| **36** | **⛔质量门博弈(P0红线)** | **伪造URL+修改日期+跳步骤绕过质量门，6类严重问题。质量门失败=回到步骤重做，禁止修改数据** |
| **37** | **v8.0机制加固** | **文字规则不够→代码门控: 快照对比防篡改+URL抽检自动化+deploy验证orchestrator状态** |
| 38 | 小红书noteId编造 | SPA假阴性+随机抽检=零防线，需ObjectId时间戳校验 |
| 39 | KIM周报卡片重复分割线 | 多block拼接时divider重复 |
| 40 | 周报定时发送时间调整 | 周报发送时间从周六晚改为周日上午 |
| 41 | 修复策略陷阱——删减≠修复 | 质量门失败后删除内容而非替换，导致严重缩水 |
| 42 | 最后一公里松懈 | KIM推送后心理放松，Git未提交 |
| **43** | **⭐大事件隧道视野(v9.0)** | **GTC主导致AI Coding空、源单一55%、XHS跳过。新增分流搜索协议+check_tab_balance门控** |
| **44** | **⭐林克自述缺失(v6.0)** | **capability_update字段遗漏，新增质量门第19项检查** |
| **45** | **⭐Workflow碎片化(v6.0)** | **规范散落导致遗漏，单体化重构workflow.md** |
| **46** | **⭐外部版仓库路径混乱(v9.5)** | **Skill文档路径与脚本实际路径不一致+本地未克隆仓库，导致同步失败。绕过脚本手动cp=脱敏失效+多处不同步** |
| **47** | **⭐watch_list格式不匹配渲染为空(v9.6)** | **JSON用{category,items:[]}格式，但render_preview()只支持str和{name,desc,color}，格式不匹配导致"明日/下周值得关注"板块静默为空。根因：生成JSON后未端到端验证渲染结果。修复：gen_daily_html.py增加渲染完整性自检，deploy_daily.sh验证步骤增加"值得关注"板块条目数检查** |
| **48** | **⭐首页联动更新不完整(v9.6)** | **deploy_daily.sh只更新了stat-value数字，遗漏：①日历数组未追加新日期②list-item-desc描述文本未更新。根因：6处联动无检查清单，脚本覆盖范围与实际需求不一致。修复：deploy_daily.sh新增Python片段自动提取JSON摘要填写list-item-desc，日历数组用Python regex替换** |
| **49** | **⭐public/index.html漏commit(v9.6)** | **sync_to_public.py更新了public/index.html，但deploy流程里git add -A在sync之前执行，导致public/index.html修改没被纳入当次commit。根因：git提交顺序：先commit后sync，sync的结果丢失。修复：deploy_daily.sh重排顺序——sync在git commit之前执行，保证所有文件变更统一提交** |
| **50** | **⭐管道吞掉脚本失败(v9.7)** | **deploy_daily.sh中`cmd \| tail -5`写法导致set -e不触发：管道右侧tail成功则整行成功，即使cmd失败也不报错。特别危险：sync_to_public失败(脱敏未完成)后继续git commit+push，将敏感信息推送到公开仓库。修复：去掉管道，直接调用命令；加set -o pipefail；敏感词发现后exit 1硬阻断** |
| **51** | **⭐KIM卡片URL硬编码内部文件名(v9.7)** | **旧版send_ai_daily.py中report_url硬编码（已废弃）`{date}-v3.html`，但公开版经sync_to_public脱敏后文件名变为`{date}.html`（去掉-v3后缀），导致KIM卡片"查看完整日报"按钮404。修复：URL改为`{date}.html`** |
| **52** | **⭐脱敏规则与实际内容不匹配(v9.7)** | **sync_to_public.py第91行规则期望`（沈浪的AI分身）`，但index.html实际文本是`（基于CF打造的AI数字分身）`，精确字符串匹配失败，导致CF残留在公开版。SENSITIVE_WORDS也没包含CF，verify无法检出。修复：用更宽松的正则匹配anchor标签，SENSITIVE_WORDS加CF** |
| **53** | **⭐orchestrator+deploy_daily.sh双重sync(v9.7)** | **deploy_daily.sh Step 6调用sync_to_external，orchestrator finalize又调用run_external_sync()，两次同步。修复：deploy_daily.sh检测SKIP_GATE=1环境变量（orchestrator调用时设置），如果存在则跳过Step 6，由orchestrator统一负责外部同步，消除双重同步** |
| **54** | **⭐6处联动门控被绕过(v9.9)** | **finalize报「6处联动失败」，Agent选择「先推了再说」只做git push就标记完成，首页/索引页/外部版全没更新。根因：门控存在但被人为选择性忽略。修复：新增P0红线——6处联动失败=阻断禁止绕过，标记完成前必须验证质量门显示✅** |
| **55** | **⭐KIM推送重复发送(v10.0)** | **连续执行两次旧版send_ai_daily.py（已废弃）（先--preview再正式发送），导致同一日报私发两次。根因：--preview仅为语义标记，与无参数行为完全相同。修复：更新workflow.md明确只执行一次，新增P0红线禁止重复发送** |
| **56** | **⭐订阅页面Appwrite匿名写入401(v10.3)** | **Appwrite 前端匿名写入返回 401 user_unauthorized，匿名用户没有 documents.create/update 权限。前端 JS SDK 所有读写操作（subscribe、checkSubscription、unsubscribe）全部失败。替代方案：改用 KIM 消息通知模式——用户在 KIM 上给 MyFlicker 消息号发送"订阅AI日报"指令，MyFlicker 自动写入 `data/subscribers.json` 并回复确认。订阅数据从 Appwrite 迁移到本地 JSON 文件** |
| **57** | **⭐深度调研KIM卡片URL用内部版导致404(2026-04-25)** | **Step7 KIM卡片按钮1链接使用内部版 `ai-insight/` 路径，但外部群成员访问404。根因：脚本里写了内部URL，但外部仓库是 `ai-insight-public/`。修复：KIM卡片按钮URL必须统一改为 `ai-insight-public/`，并在私发预览时点击按钮验证200后再群发** |
| **58** | **⭐深度调研只推外部版漏推内部版(2026-04-25)** | **sync_to_external.py 只把文件推送到 `ai-insight-public` 仓库，但 `AI-Insight` 主仓库（`ai-insight.git`）的 HTML 文件和 index.html 卡片变更没有 `git add+commit+push`，导致内部版 GitHub Pages（`ai-insight/`）404。两个仓库都需要提交：① `git push` 内部版主仓库；② `sync_to_external.py` 推外部版，缺一不可。记忆口诀：sync推外部，push推内部。另外 sync_to_public.py 不支持 `--deep-research` 等参数（会报 unrecognized arguments），深度调研文件需手动 cp 到 public/ 再运行无参数版** |
| **59** | **⭐三版首页卡片各自独立，无一自动同步(2026-04-25)** | **Step 6 在 AI-Insight/index.html 新增卡片后，public/index.html 和 ai-insight-public/index.html 均不会自动更新。根因：sync_to_public.py 有 preserve_block 机制保留公开版深度调研区块（新卡片不传播），ai-insight-public 是独立仓库也不会自动跟随。修复：Step 5.5 新增四端首页卡片门控检查——用 grep 验证三份 index.html 均包含新报告 slug，缺一不可** |
| **60** | **⭐微信搜狗占位符链接不可达(2026-04-27)** | **Subagent在微信搜索API返回空时，生成了`weixin.sogou.com/weixin?type=2&query=...`格式的搜索链接作为占位符。但这些是搜索页面链接，不是文章链接，预检判定为不可达。根因：Subagent未正确处理微信API空结果。修复：将搜狗搜索链接替换为空URL（source标注微信即可）。与#34不同：#34是搜索策略问题，本次是占位符格式问题** |
| **61** | **⭐KIM日报推送退化为纯文本(2026-04-29)** | **容器重建后 KIM_APP_KEY/SECRET_KEY 丢失，send_ai_daily.py 无法直连 KIM API。Agent 退而求其次用 message 工具发了纯文本消息，但纯文本丢失了卡片结构（热度趋势/5板块/深度聚焦/林克自述/双按钮）。根因：没有 mixCard 降级路径，缺少"必须用卡片"的硬约束。修复：统一入口改为 `scripts/build_insight_mixcard.py`（日报/周报/调研/产品），Work模式唯一路径A: message+kimMixCard，路径B(KIM直连)已废弃；新增 P0 红线禁止纯文本推送** |
| **62** | **⭐外部版订阅按钮每次需手动删除(2026-05-04)** | **用户要求去掉外部版首页订阅按钮，手动编辑了 index.html 并 push。但每次 sync_to_public 同步时，内部版首页的订阅按钮会被带到外部版，下次又得手动删。根因：脱敏脚本只处理敏感词替换，不处理结构性内容差异（如订阅按钮这种"内部版有、外部版不该有"的区块）。修复：sync_to_public.py REPLACEMENTS 新增正则规则，自动删除 header 区域内订阅按钮 div，从"人工手动"升级为"脚本自动化"** |

完整分析详见 `references/lessons-learned.md`

---

## 参考文件清单

| 文件 | 内容 |
|------|------|
| `references/daily-report/workflow.md` | 日报执行流程 |
| `references/daily-report/search-keywords.md` | 搜索关键词清单 |
| `references/daily-report/quality-rules.md` | 筛选和验证规则 |
| `references/weekly-report.md` | 周报完整流程 |
| `references/deep-research.md` | 深度研究方法论 |
| `references/homepage-update.md` | 首页更新检查 |
| `references/knowledge-accumulation.md` | 知识沉淀规则 |
| `references/scope-management.md` | 追踪体系管理 |
| `references/source-registry.md` | 信息源注册表（人物/公司/平台） |
| `references/lessons-learned.md` | 踩坑经验分析 |
| `references/footer-template.md` | 统一底部模板 |
