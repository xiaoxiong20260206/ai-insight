# AI洞察子技能详细内容

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

详见 `reference/scope-management.md`

---

## 子技能 2: AI日报

### 触发词
"AI日报"、"跑一下AI日报"、"今日AI调研"

> **⚠️ 唯一执行参考**: `reference/daily-report/workflow.md` (v6.0单体化版)
> 其他文件（如 `daily-report.md`）为历史遗留，不作为执行依据。

### 编排工作流 (v9.9)

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

### ⛔ P0红线: KIM推送只执行一次（v10.0 经验55）
> **2026-04-22教训**: 连续执行了两次旧版send_ai_daily.py（已废弃）（先 `--preview` 再正式发送），
> 导致同一日报重复发送给用户。
>
> **根因**: `--preview` 参数仅为语义标记，与无参数行为完全相同（都是私发给 shenlang）。
> 执行两次 = 发送两次。
>
> **强制规则**:
> ```bash
> # 正确：只执行一次
> python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
>
> # 错误：执行两次
> python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json # 生成卡片
> # ❌ 禁止重复发送！旧版 send_ai_daily 已废弃
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
- 执行流程: `reference/daily-report/workflow.md`
- 搜索关键词: `reference/daily-report/search-keywords.md`
- 质量规则: `reference/daily-report/quality-rules.md`

---

## 子技能 3: AI周报

### 触发词
"AI周报"、"生成AI周报"、"推送AI周报"

### 快速执行
```bash
python3 scripts/build_insight_mixcard.py weekly --date YYYY-Www --output /tmp/card.json --with-summary # 先预览
message(channel=kim, kimMixCard=<card>, ...)  # 确认后发群
```

### P0规则
- Top5和周度洞察格式统一
- 首页日历+周报入口卡片必须更新
- 自审环节不可省略
- **推送范围: 所有群**（区别于日报只发2个群）

详见 `reference/weekly-report.md`

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
- KIM推送使用标准深度调研卡片模板（含分享背景+核心发现+双按钮）

详见 `reference/deep-research.md`（含 Step 7 KIM推送完整模板）

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

详见 `reference/knowledge-accumulation.md`

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

详见 `reference/homepage-update.md`

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
> cd <skill_directory>
> git clone https://github.com/xiaoxiong20260206/ai-insight-public.git ai-insight-public
> ```
> **sync_to_external.py 会检测仓库是否存在，不存在会报错并给出克隆命令。**

### 版本体系（v9.5 更正）
| 版本 | 路径 | GitHub Pages |
|------|------|--------------|
| 内部版 | `<skill_directory>` | xiaoxiong20260206.github.io/ai-insight/ |
| public | `<skill_directory>public/` | （同上，部署源） |
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

### ⛔ P0红线: 外部版首页禁止订阅按钮（v10.1 2026-04-25）
> **原因**: 外部版首页是公开页面，订阅功能需要用户认证，外部版不提供此能力。
>
> **强制规则**: 外部版首页 `index.html` 必须删除订阅按钮区块：
> - 删除 `<div style="margin-top: 24px; text-align: center;">...</div>` 订阅按钮
> - 删除 `<a href="./subscribe/">` 链接及相关样式
>
> **位置**: 外部版首页头部（header）区域，`header-title` 和 `header-subtitle` 之后

### ⛔ P0红线: 内部版订阅页面架构（v10.2 2026-04-25）
> **背景**: Appwrite 前端云不支持快手 OAuth Provider，直接调用 `account.createOAuth2Session('kuaishou', ...)` 会报错 `Missing required parameter: "provider"`。
>
> **替代方案**: 订阅页面使用**工号输入模式**：
> - 用户直接输入快手工号（如 `shenlang` 或邮箱前缀）
> - 使用 Appwrite Database API 直接写入订阅表
> - 绕过 OAuth 依赖，简化实现
>
> **技术栈**:
> ```javascript
> // 正确的订阅写入方式（无需 OAuth）
> const appwrite = new AppwriteClient();
> await appwrite.createDocument({
>     username: 'shenlang',
>     is_active: true,
>     subscribed_at: new Date().toISOString()
> });
> ```
>
> **位置**: `subscribe/index.html` - 使用工号输入表单，不依赖 Appwrite Account API

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