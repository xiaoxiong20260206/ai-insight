# AI洞察附录：脚本速查 + 项目结构 + 踩坑索引

## 脚本工具速查

| 脚本 | 用途 | 命令 |
|------|------|------|
| `ai_daily_orchestrator.py` | **日报编排(状态+finalize+push) v1.1** | `python3 scripts/ai_daily_orchestrator.py status` |
| `send_ai_daily.py` | 日报KIM推送(仅发2个目标群) | `python3 scripts/send_ai_daily.py [日期]` |
| `send_ai_weekly.py` | 周报KIM推送(发所有群) | `python3 scripts/send_ai_weekly.py` |
| `send_deep_research_card.py` | 深度调研KIM推送 | `python3 scripts/send_deep_research_card.py` |
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
<skill_directory>
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
| **51** | **⭐KIM卡片URL硬编码内部文件名(v9.7)** | **send_ai_daily.py中report_url硬编码`{date}-v3.html`，但公开版经sync_to_public脱敏后文件名变为`{date}.html`（去掉-v3后缀），导致KIM卡片"查看完整日报"按钮404。修复：URL改为`{date}.html`** |
| **52** | **⭐脱敏规则与实际内容不匹配(v9.7)** | **sync_to_public.py第91行规则期望`（沈浪的AI分身）`，但index.html实际文本是`（基于CF打造的AI数字分身）`，精确字符串匹配失败，导致CF残留在公开版。SENSITIVE_WORDS也没包含CF，verify无法检出。修复：用更宽松的正则匹配anchor标签，SENSITIVE_WORDS加CF** |
| **53** | **⭐orchestrator+deploy_daily.sh双重sync(v9.7)** | **deploy_daily.sh Step 6调用sync_to_external，orchestrator finalize又调用run_external_sync()，两次同步。修复：deploy_daily.sh检测SKIP_GATE=1环境变量（orchestrator调用时设置），如果存在则跳过Step 6，由orchestrator统一负责外部同步，消除双重同步** |
| **54** | **⭐6处联动门控被绕过(v9.9)** | **finalize报「6处联动失败」，Agent选择「先推了再说」只做git push就标记完成，首页/索引页/外部版全没更新。根因：门控存在但被人为选择性忽略。修复：新增P0红线——6处联动失败=阻断禁止绕过，标记完成前必须验证质量门显示✅** |
| **55** | **⭐KIM推送重复发送(v10.0)** | **连续执行两次send_ai_daily.py（先--preview再正式发送），导致同一日报私发两次。根因：--preview仅为语义标记，与无参数行为完全相同。修复：更新workflow.md明确只执行一次，新增P0红线禁止重复发送** |
| **56** | **⭐订阅页面OAuth失败(v10.2)** | **Appwrite 前端云不支持快手 OAuth Provider，调用 `createOAuth2Session('kuaishou', ...)` 报错 `Missing required parameter: "provider"`。替代方案：使用工号输入模式，绕过 OAuth 依赖，直接写入订阅表** |
| **57** | **⭐深度调研KIM卡片URL用内部版导致404(2026-04-25)** | **Step7 KIM卡片按钮1链接使用内部版 `ai-insight/` 路径，但外部群成员访问404。根因：脚本里写了内部URL，但外部仓库是 `ai-insight-public/`。修复：KIM卡片按钮URL必须统一改为 `ai-insight-public/`，并在私发预览时点击按钮验证200后再群发** |
| **58** | **⭐深度调研只推外部版漏推内部版(2026-04-25)** | **sync_to_external.py 只把文件推送到 `ai-insight-public` 仓库，但 `AI-Insight` 主仓库（`ai-insight.git`）的 HTML 文件和 index.html 卡片变更没有 `git add+commit+push`，导致内部版 GitHub Pages（`ai-insight/`）404。两个仓库都需要提交：① `git push` 内部版主仓库；② `sync_to_external.py` 推外部版，缺一不可。记忆口诀：sync推外部，push推内部。另外 sync_to_public.py 不支持 `--deep-research` 等参数（会报 unrecognized arguments），深度调研文件需手动 cp 到 public/ 再运行无参数版** |
| **59** | **⭐三版首页卡片各自独立，无一自动同步(2026-04-25)** | **Step 6 在 AI-Insight/index.html 新增卡片后，public/index.html 和 ai-insight-public/index.html 均不会自动更新。根因：sync_to_public.py 有 preserve_block 机制保留公开版深度调研区块（新卡片不传播），ai-insight-public 是独立仓库也不会自动跟随。修复：Step 5.5 新增四端首页卡片门控检查——用 grep 验证三份 index.html 均包含新报告 slug，缺一不可** |
| **60** | **⭐微信搜狗占位符链接不可达(2026-04-27)** | **Subagent在微信搜索API返回空时，生成了`weixin.sogou.com/weixin?type=2&query=...`格式的搜索链接作为占位符。但这些是搜索页面链接，不是文章链接，预检判定为不可达。根因：Subagent未正确处理微信API空结果。修复：将搜狗搜索链接替换为空URL（source标注微信即可）。与#34不同：#34是搜索策略问题，本次是占位符格式问题** |

完整分析详见 `reference/lessons-learned.md`

---

## 参考文件清单

| 文件 | 内容 |
|------|------|
| `reference/daily-report/workflow.md` | 日报执行流程 |
| `reference/daily-report/search-keywords.md` | 搜索关键词清单 |
| `reference/daily-report/quality-rules.md` | 筛选和验证规则 |
| `reference/weekly-report.md` | 周报完整流程 |
| `reference/deep-research.md` | 深度研究方法论 |
| `reference/homepage-update.md` | 首页更新检查 |
| `reference/knowledge-accumulation.md` | 知识沉淀规则 |
| `reference/scope-management.md` | 追踪体系管理 |
| `reference/source-registry.md` | 信息源注册表（人物/公司/平台） |
| `reference/lessons-learned.md` | 踩坑经验分析 |
| `reference/footer-template.md` | 统一底部模板 |
