# AI洞察 踩坑经验汇总
> **版本**: v2.1
> **更新时间**: 2026-05-20 (v2.1: 新增 #115 首页日历周报入口+外部版身份泄露+Stats过时)
> **用途**: 踩坑经验归档记录。**关键教训已提取到 `daily-report/workflow.md` 对应Step中**。
> **定位**: 本文件是历史归档，执行时以 `workflow.md` 为唯一参考。
> **注意**: 这些经验同时存在于记忆系统（common_pitfalls_experience），meta-execution启动时会自动检索。
---

> **归档说明 (v11.0)**: 早期链接处理规则已归档到 。本文件只保留 #63 及之后的经验（2026年4月以后），关键教训已提炼到 workflow/p0-redlines/quality-rules 中。

## 经验#65 — 2026-04-09 — 内部版首页被深度调研脱敏版整体覆盖

### 问题描述
2026-04-09 用户发现内部版首页（`AI-Insight/index.html`）header 从「林克的AI洞察」变成了「AI洞察·持续追踪AI行业动态」，内部版被脱敏版覆盖。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | Step 5.5 双版本同步完成后，某步骤将 `public/index.html`（脱敏版）复制回根目录 `index.html` |
| **第二层** | `deep-research.md` Step 5.5 只说「同步到 public/」，没有明确禁止「反向覆盖」 |
| **第三层** | 历史上曾有过 `cp public/index.html index.html` 的调试操作残留 |

### 暴露时机
用户访问内部版首页，发现 header 变成外部版样式，林克品牌消失。

### 修复动作（已执行）
1. 恢复 `index.html` header 为「林克的AI洞察」
2. 修复 `public/` 下11个子页面的语法错误
3. 修复 `public/` 下4个周报的括号语法错误

### 系统性修复
1. **SKILL.md** 新增经验 #65 + Critical Rules 新增红线
2. **deep-research.md** Step 5.5 新增「禁止反向覆盖」门控
3. **sync_to_public.py** 新增反向覆盖检测警告

### 核心教训
> **内部版是「主」，public/ 是「从」。只允许内部版 → public/ 的单向同步，禁止任何反向操作。**
>
> **所有同步脚本的输出方向必须固定：源=内部版，目标=public/或外部仓库。**
>
> **工作流文档的每个步骤必须明确数据流向：只说"同步"不够，必须说"从哪到哪"。**

### 举一反三
1. **禁止用 cp/rsync 的 --delete 参数跨版本同步**
2. **任何涉及 public/ 的操作后必须检查内部版 header 完整性**
3. **deep-research.md Step 5.5 是「同步到 public/」，不是「同步到内部版」**

### 防护措施（已加入）
1. **deploy_daily.sh / deep-research 工作流**: Step 5.5 完成后新增反向覆盖检测
2. **sync_to_public.py**: 若检测到 `index.html` 比 `public/index.html` 修改时间更早且内容不同，输出警告
3. **SKILL.md Critical Rules**: 明确禁止 `cp public/index.html index.html`

---

## 经验#63 — 2026-03-31 — 外部版首页三层联动遗漏

### 问题描述
外部版网站 https://my-ai-research-lab.github.io/ai-insight-public/ 的首页未更新：日历上没有当天日期高亮，最新日报链接仍指向昨天。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | `sync_to_external.py` 推送到 `my-ai-research-lab` 仓库（origin）时失败，被静默吞掉，主流程未中断 |
| **第二层** | 外部首页 `index.html` 的日历数组 `reportsData` 漏追加当日日期数字 |
| **第三层** | 外部首页最新日报 `list-item` 的 href 仍指向前一天日期 |

### 暴露时机
用户直接访问外部版网站，发现首页日历当天无高亮，点击最新日报跳转到错误页面。

### 修复动作
1. 手动追加日历数组当日数字
2. 手动更新最新日报链接
3. `sync_to_external.py` 新增 remote 验证（推送前检查 origin 是否指向 my-ai-research-lab）
4. 新增推送失败阻断（任何 git push 失败 = exit 1，不静默吞掉）

### 举一反三
- `sync_to_external.py` 原来对 git push 失败无感知，shell 层面需要 `set -e` 或显式检查返回码
- 外部首页更新逻辑与内部首页是两套代码，有时只更新了内部版，外部版悄悄落后

---

## 经验#64 — 2026-04-03 — SKIP_GATE=1 静默跳过外部同步（反复出现根因系统性归档）

### 问题描述
每次用 `SKIP_GATE=1 bash scripts/deploy_daily.sh` 强制部署时，外部版 https://xiaoxiong20260206.github.io/ai-insight-public/ 不更新。

### 根因（直接）
```bash
# deploy_daily.sh 旧逻辑（错误）
if [ "${SKIP_GATE:-0}" = "1" ]; then
    echo "  ⏭️ 由orchestrator调用，外部版同步由orchestrator负责，此处跳过"
else
    uv run scripts/sync_to_external.py --full --verify
fi
```
`SKIP_GATE=1` 本来的语义是"绕过质量门强制部署"，但经验#53修复双重同步时，把"跳过外部同步"的逻辑也绑定到了这个变量上。

### 根因（深层 — 反复出现的三类系统性缺陷）

**第一类：一个变量承担多种语义（代码设计缺陷）**
- `SKIP_GATE` 被先后赋予：绕过质量门、跳过外部同步、orchestrator调用信号 三种语义

**第二类：联动位置分散 × 无端到端防护（架构设计缺陷）**
- 需要同步 6 处：内部日报、内部首页、外部日报、外部首页、日报索引、外部仓库
- 任意一处断裂 = 用户可见不一致

**第三类：长工作流尾部松懈（执行行为缺陷）**
- 工作流越长（5步、≥15分钟），末尾步骤越容易在报错时被绕过
- 质量门报错压力最大时，恰好是最容易选择"先推了再说"的时刻

### 修复
```bash
# deploy_daily.sh 新逻辑（正确）
if [ "${SKIP_EXTERNAL:-0}" = "1" ]; then
    echo "  ⏭️ SKIP_EXTERNAL=1，跳过外部版同步（由调用方明确控制）"
else
    uv run scripts/sync_to_external.py --full --verify
fi
```

### 核心教训
> **一个变量只能有一种语义。**
>
> **修复会引入新 bug，尤其是在同一变量上叠加语义时。**
>
> **外部版每次部署后必须执行 4位置自检。**

---

## 经验#74 — 2026-04-16 — 会话中断恢复后重复搜索 + 微信临时URL传递

### 问题描述
会话因 context 溢出中断后，主会话恢复时没有检查 Step 0.5/Step 1 是否已完成，直接重新执行了 12 次 web 搜索 + 4 次微信搜索，与上一轮会话大量重叠。

### 根因链

| 层级 | 具体原因 |
|------|----------|
| **第一层** | 恢复时没有检查 `data/flags/step1-completed.flag` 是否存在 |
| **第二层** | Step 0.5 热点探针没有对应的 orchestrator flag，无法自动检测是否已完成 |
| **第三层** | 微信 `real_url` 字段在部分结果中为带时间戳的临时 URL，未在传递给 subagent 前过滤 |

### 修复规则
1. **会话恢复时**：先执行 `uv run scripts/ai_daily_orchestrator.py status` + 检查 `data/flags/step1-completed.flag` → 已存在则直接跳到 Step 2
2. **微信链接过滤**：`real_url` 字段判断，`mp.weixin.qq.com/s?src=11&timestamp=` 开头的全部替换为 sogou 格式
3. **subagent task 描述**：必须明确注明「禁止将临时微信URL写入JSON，必须转换为 sogou 格式」

### 已沉淀到
- `sl-ai-insight/SKILL.md` Critical Rules 新增两条红线（经验#74）

---

## 经验#75 — 2026-04-30 — 容器重建后日报404：环境恢复+SSH优先原则

### 问题描述
04-30日报KIM卡片推送成功，但点击跳转链接返回404：
`https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/2026-04/2026-04-30.html`

### 根因链（四层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | 容器重建后本地仓库丢失（Work模式下项目在 `/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/`） |
| **第二层** | GitHub HTTPS(443)端口不通，`git clone https://...` 全部超时失败 |
| **第三层** | 日报cron session发现仓库不存在，跳过了orchestrator、HTML生成、6处联动、git push——只完成了KIM推送和MD保存 |
| **第四层** | 缺少容器重建后的环境恢复前置检查——日报流程未在Step 0验证项目目录是否存在 |

### 修复动作
1. 发现SSH(22)端口可连通GitHub，生成ed25519 SSH key
2. 用户手动添加到GitHub → SSH clone成功恢复两个仓库
3. 从workspace残留的MD手动构建JSON → gen_daily_html.py生成HTML
4. 手动执行6处联动 + sync_to_public + sync_to_external + git push两个仓库
5. SSH key备份到workspace `.ssh-backup/`，HEARTBEAT.md新增恢复流程

### 系统性修复
1. **workflow.md** Step 0新增环境前置检查（项目目录+Git连通性+SSH key）
2. **p0-redlines.md** 新增红线#15（容器重建环境恢复）和#16（SSH优先原则）
3. **HEARTBEAT.md** 新增SSH key健康检查+备份恢复+项目仓库SSH clone流程

### 根本教训
> **容器重建 = 全部非workspace目录清零。日报流程不能假设本地仓库永远存在。**
>
> **GitHub连通性不是假设——HTTPS和SSH可能只有一条通路通。部署前必须验证Git可达性。**
>
> **SSH key是持久化凭证，必须像git-credentials一样备份到workspace。**

### 举一反三
1. **所有依赖本地目录的cron任务**（日报、周报、深度调研）都需要前置检查项目目录是否存在
2. **git clone优先走SSH**：`git@github.com:...` 而非 `https://github.com/...`——在快手内网环境HTTPS 443经常不通
3. **SSH key与git-credentials同级别备份**：容器重建后两个都需要恢复
4. **cron任务失败不应静默继续**：如果项目目录丢失，应该明确标记失败并通知用户，而非"只推送KIM卡片，跳过所有部署"

### 已沉淀到
- `reference/daily-report/workflow.md` Step 0新增环境前置检查
- `reference/p0-redlines.md` 新增红线#15、#16
- `HEARTBEAT.md` 新增SSH key+项目仓库恢复流程

---

## 经验#17 — 2026-05-04 — 失败必须自修复，不能停下来等用户处理

### 问题描述
AI日报cron连续多日失败（python命令找不到、权限问题、空壳JSON、质量门失败后仍推送），每次都是用户发现后手动要求"重跑"或"修复"。5/4这天cron标记为"ok"但实际JSON数据是空壳（tabs全空、date=None），子代理在搜索环节后停在了"需要获取微信文章的公开转载链接"就不再继续。

### 根因链

| 层级 | 具体原因 |
|------|----------|
| **第一层** | 子代理遇到困难就停下来，不尝试修复也不继续后续步骤 |
| **第二层** | workflow没有"失败自修复"机制——所有规则都是"怎么做对"，没有"做错了怎么办" |
| **第三层** | state.json标记completed但实际产出是空壳——验证机制只看标记不看实际内容 |

### 修复动作（已执行）
1. 补跑5/4日报（子代理正在执行）
2. P0红线新增#17：失败自修复原则
3. workflow.md v6.5新增失败自修复协议
4. cron prompt更新：加入6条自修复提醒
5. lessons-learned归档此经验

### 系统性修复
1. **p0-redlines.md #17**: 6条强制规则——立即修复、修复路径优先级、最多3次重试、完成优先于完美、禁止半成品、修复后通知
2. **workflow.md v6.5**: 执行前必读新增失败自修复协议引用+自我诊断清单
3. **cron prompt**: 明确要求"任何步骤失败立即尝试修复，不要停下来等用户处理"

### 核心教训
> **失败不是终点，停下来才是。遇到问题时：修复→继续→完成→通知。不要做"只会汇报问题的AI"。**

---

## 经验#88 — 2026-05-04 — 脚本PROJECT_ROOT指向skill目录而非仓库→空内容兜底卡片

### 问题描述
周报发群后，三个群收到的卡片内容全是"(周报尚未生成，请先生成周报后再推送)"——空内容兜底卡片。MD/HTML 文件都在仓库里，但脚本找不到。

### 根因链

| 层级 | 具体原因 |
|------|----------|
| **第一层** | `build_insight_mixcard.py` 的 PROJECT_ROOT = `Path(__file__).parent.parent`，指向 skill 目录 |
| **第二层** | skill 目录里没有周报 MD/HTML 文件（只有日报），仓库 `/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight` 才有 |
| **第三层** | 脚本只搜 skill 目录下两个路径，都不匹配→fallback 空内容兜底 |

### 修复
脚本 PROJECT_ROOT 优先从 `/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight` 读取（真正仓库），skill 目录仅作 fallback。

### 核心教训
> **脚本的"根目录"必须与实际文件存放位置一致。假设文件在 skill 目录但实际在仓库 = 必然空壳。**

---

## 经验#89 — 2026-05-04 — 按钮URL缺年月子目录→404

### 问题描述
周报卡片"深度阅读完整周报"按钮点击后 404。URL 是 `01-daily-reports/weekly-2026-W18.html`，缺少 `2026-04/` 子目录。

### 根因链
脚本 URL 生成逻辑没有按文件实际落盘规则（`YYYY-MM/weekly-...`）拼接路径。

### 修复
URL 格式改为 `{base}/{monday_month}/weekly-{year}-W{week}.html`，`monday_month` = ISO周周一所在月份（W18周一=04/27→`2026-04`）。

### 核心教训
> **按钮URL必须与文件实际路径严格一致。路径规则不能靠猜测——必须按落盘规则计算。**

---

## 经验#90 — 2026-05-04 — 正则截断林克洞察→品牌内容丢失

### 问题描述
周报卡片里没有"林克的洞察"——用户专门要求加的品牌差异化内容被正则吃掉了。

### 根因链
脚本用 `## .*洞察.*?\n...\n## ` 匹配洞察，但"周度洞察"匹配后，正则吃到下一个 `## ` 就停了——后面的"林克洞察"被截断。

### 修复
v3.0 脚本用独立正则提取林克洞察（匹配 `🔥 林克的洞察` 或 `## .*林克.*洞察`），不再与周度洞察混在一起。

### 核心教训
> **正则提取多个同名 section 时，必须用独立匹配——贪心匹配会把后面的 section 吃掉。品牌内容丢了比一般内容丢了更严重。**

---

## 经验#91 — 2026-05-04 — Top 5 太长无视觉锚点→10屏纯文本轰炸

### 问题描述
用户评价周报卡片"效果不如之前，内容太简要"。排查后发现不是内容太少，而是**结构太密**——每个 Top 5 事件展开为标题+3段正文+3条来源链接，5条堆在一起就是10屏纯文本，没有节奏感。

### 根因链
卡片从 MD 原样搬运 Top 5 section，没有针对卡片场景（手机、快扫）做信息密度优化。

### 修复
v3.0 卡片 Top 5 重构为"结论先行"：标题→影响一句话→1条核心链接。每条半屏而非2屏。

### 核心教训
> **MD 全文≠卡片内容。卡片是快扫场景，必须"结论先行、一句论证、一条来源"。MD 是深度阅读场景，可以展开。两者结构必须不同。**

---

## 经验#92 — 2026-05-04 — 发群groupId vs space:groupId→群3失败

### 问题描述
第一次发群时第3个群失败，提示"发送者不是群成员"。第二次用 `space:<groupId>` 格式后三个群都成功了。

### 根因
KIM 群聊消息的 target 格式是 `space:<groupId>`，不能裸传 groupId。

### 修复
v3.0 workflow 统一规定 `target=f"space:{group_id}"`。

### 核心教训
> **KIM群聊地址格式是 `space:<groupId>`，不是裸 groupId。发群失败时先检查格式。**

---

## 经验#93 — 2026-05-04 — 手动构造kimMixCard JSON格式错误→text应为kimMd object

### 问题描述
手动构造卡片 JSON 时，`text` 字段写成纯字符串 `"内容..."`，但 KIM MixCard 要求 `text` 是 `{"type": "kimMd", "content": "..."}` object。导致群收到空卡片。

### 根因
不了解 kimMixCard 的 text 字段格式规范。

### 修复
v3.0 规定：kimMixCard 必须传脚本生成的 JSON object（脚本已用正确的 `{"type": "kimMd", "content": ...}` 格式），禁止手动构造。

### 核心教训
> **kimMixCard 的 text 字段必须是 {"type": "kimMd", "content": "..."}，不能是纯字符串。永远用脚本生成，永远不要手写。**

---

## 经验#94 — 2026-05-04 — 旧版send_ai_weekly.py vs build_insight_mixcard.py不一致（send_ai_weekly已废弃）→改错文件

### 问题描述
优化卡片样式时改了 `build_insight_mixcard.py`，但旧版推送用的是 `send_ai_weekly.py`（已废弃）——改了半天改错文件，推送出去的还是旧版。

### 根因
两个脚本功能重叠但路径不同，没有明确的唯一入口。

### 修复
v3.0 废弃 `send_ai_weekly.py`和`send_ai_daily.py`（全部场景），唯一入口：`build_insight_mixcard.py` + message 工具。

### 核心教训
> **功能重叠的两个脚本 = 必然有一天改错文件。锁定唯一入口，废弃旧脚本。**

---

## 经验#95 — 2026-05-04 — 洞察缺一句话结论→不符合"以终为始"

### 问题描述
周报卡片里三条洞察都是分析先行——先讲现象再给判断。用户是 INTJ 人格，写作习惯是"以终为始"，结论先行再论证。

### 修复
v3.0 卡片每条洞察标题即结论（如"商业化进入冲刺期：四巨头资本支出暴涨"），后面才展开论证。

### 核心教训
> **洞察标题=结论，不是主题。读者扫标题就知道你站哪边，不需要读完3段才找到判断。**

---

## 经验#96 — 2026-05-04 — 缺少概览定调句→30秒入口缺失

### 问题描述
MD 开头的五维度概览表格是"以终为始"的入口——30秒抓住本周核心信号。卡片没有这个，读者要滚10屏才看到第一个结论。

### 修复
v3.0 卡片开头加定调句：概览5维度合并为关键词（如"本周关键词：霸主更替 · 成本革命 · 规则重塑"）。

### 核心教训
> **卡片的第一屏必须给读者一个锚——定调句、关键词、一句话总结。没有锚的卡片就是信息洪流。**

---

## 经验#97 — 2026-05-04 — Work模式路径迁移：旧路径引用残留→rebase覆盖→二次修复

### 问题描述
从Code模式切换到Work模式后，13个文件仍引用旧路径 `~/Documents/Codeflicker/AI-Insight/` 和 `~/Documents/Codeflicker/个人助理_V1/`。逐个修复后，git rebase 解决冲突时选择了 origin/main 版本（未修复版），导致 3 个文件（SKILL.md、deep-research.md、orchestrator.py）的修复被回退。

### 修复
1. 技能目录从脚本子集升级为完整git仓库（含 .git + 全量内容）
2. 外部仓库克隆到 workspace/user-skills/ai-insight-public/
3. 旧仓库 ~/Documents/Codeflicker/ 已删除
4. rebase后必须二次确认所有修改是否被还原

### P0红线新增
- **路径迁移后，git rebase 必须二次验证所有文件修改未被覆盖**
- **所有路径引用禁止硬编码绝对路径，使用 config.py 动态计算（PROJECT_ROOT/EXTERNAL_REPO）**

### 核心教训
> **rebase 不是安全操作——它会用远端版本覆盖你的本地修改。修复后必须 grep 全量验证，不能假设 rebase --ours 一定生效。**

---

## 经验#98 — 2026-05-04 — 周报mixCard缺footer/subtitle→卡片不完整

### 问题描述
build_insight_mixcard.py 的 build_weekly() 函数组装卡片时遗漏了 _footer() 和 subtitle block，导致周报卡片没有签名行和概览行。日报卡片有完整的 header→subtitle→heat→sections→capability→footer→buttons 结构，但周报只有 header→top5→insight→buttons。

### 修复
- build_weekly() 新增 _footer("周报") 和 _content("subtitle", "📅 04/27-05/03 | Top 5 + 周度洞察 + 林克的洞察")
- 所有卡片类型（daily/weekly/research/product）必须包含完整结构：header→subtitle→content blocks→footer→buttons

### P0红线新增
- **mixCard 卡片结构锚定：所有场景必须包含 header + subtitle + footer + buttons，缺一=阻断**

### 核心教训
> **卡片结构不能靠"函数里写了什么"来保证，必须靠锚定清单来验证。日报有但周报没有 = 没有统一骨架约束。**

---

## 经验#99 — 2026-05-04 — 周报卡片URL指向扁平路径→404

### 问题描述
build_weekly() 生成的周报URL为 `01-daily-reports/weekly-2026-W18.html`（扁平路径），但实际文件存储在 `01-daily-reports/2026-05/weekly-2026-W18.html`（月份目录）。按钮"查看完整周报"点击后404。

### 修复
- weekly_url 从 `REPORT_BASE_URL/weekly-{year}-W{week_num}.html` 改为 `REPORT_BASE_URL/{month_str}/weekly-{year}-W{week_num}.html`
- month_str 使用周日的月份（周报通常存在周日所在月份目录）

### P0红线新增
- **mixCard 按钮 URL 必须与实际文件路径一致，生成后必须 `curl -I` 验证 HTTP 200**

### 核心教训
> **URL和文件路径是两个独立系统——脚本算出来的URL不等于文件实际存储位置。必须用文件系统验证，不能只看代码逻辑。**

---

## 经验#100 — 2026-05-04 — 周报文件查找硬编码月份→后续周报全找不到

### 问题描述
build_weekly() 的 weekly_patterns 只搜索两个路径：
- `01-daily-reports/weekly-2026-W18.md`（根目录）
- `01-daily-reports/2026-04/weekly-2026-W18.md`（硬编码2026-04）

W18 的周报实际在 `2026-05/` 目录，W19 在 `2026-05/`，但硬编码只查 `2026-04/`。所有不在4月的周报都会找不到。

### 修复
- 搜索路径改为动态计算：按周一和周日的月份目录搜索
- 保留根目录搜索作为兼容fallback

### 核心教训
> **硬编码月份 = 写代码时刚好是对的，但1个月后必错。路径搜索必须动态，不能靠"当前月份"假设。**

---

## 经验#101 — 2026-05-04 — 深度聚焦截断100字→只保留30%内容→洞察价值打折

### 问题描述
build_insight_mixcard.py 和 build_daily_mixcard.py 的深度聚焦 summary 截断上限为100字符。每个板块的 deep_focus 实际有 269-347 字的内容，100字截断只保留约30%，关键论证被大量砍掉。

### 修复
- 截断上限从 100 → 200 字
- takeaway（关键判断）永远不截断

### P0红线新增
- **深度聚焦 summary 截断上限 ≥ 200字，关键判断(takeaway)禁止截断**

### 核心教训
> **截断不是"精简"，是"价值损失"。100字只能保留结论框架，200字才能保留论证骨架。判断永远不截——它是一句话，不是一段话。**

---

## 经验#102 — 2026-05-04 — Work模式无KIM凭证→路径B(KIM直连)完全不可用→workflow误导

### 问题描述
workflow.md Step 5 写"两种推送路径（二选一）"，路径B（send_ai_daily.py直连KIM API）需要 KIM_APP_KEY/SECRET_KEY 环境变量。Work模式容器没有这些凭证，路径B完全不可用。但文档让Agent以为可以选路径B，浪费时间尝试后失败。

### 修复
- workflow.md 标注"Work模式唯一路径A"
- send_ai_daily.py、send_ai_weekly.py 等6个KIM直连脚本归档到 _archive/deprecated-work-mode/
- orchestrator.py cmd_push 从调用 send_ai_daily.py 改为生成 mixCard JSON
- 全量文档标注旧脚本为"⚠️已废弃"

### P0红线新增
- **Work模式唯一推送路径: build_insight_mixcard.py → mixCard JSON → message(kimMixCard)**
- **禁止尝试KIM直连脚本（无凭证=必失败），禁止纯文本降级**

### 核心教训
> **"二选一"的前提是两个选项都可用。如果环境决定只有一个能工作，写成"二选一"就是误导——Agent会浪费时间试错。文档必须标注当前环境下的唯一可行路径。**

---

## 经验#103 — 2026-05-04 — 两套mixcard脚本并存→维护成本翻倍→改错文件风险

### 问题描述
build_daily_mixcard.py 和 build_insight_mixcard.py 功能重叠（日报mixCard生成），逻辑几乎相同但各自独立迭代。修改卡片样式时可能改了 build_insight_mixcard.py，但 cron 任务用的是 build_daily_mixcard.py——改错文件，推送出去的还是旧版。（与#94同一类问题）

### 修复
- build_daily_mixcard.py 归档到 _archive/deprecated-work-mode/
- build_insight_mixcard.py 成为唯一mixCard生成器（覆盖 daily/weekly/research/product）
- 15个Work模式无用脚本全部归档（send_*、kim_client、plist、subscription_*等）

### P0红线新增
- **唯一mixCard入口: build_insight_mixcard.py，禁止维护多个mixCard脚本**
- **功能重叠脚本 = 必然有一天改错文件。锁定唯一入口，废弃旧脚本。**

### 核心教训
> **和#94一样的根因：两套脚本做同一件事，维护时必然改错。解决方案不是"小心点"，是"只留一个入口"。**

---

## 经验#104 — 2026-05-04 — deploy_daily.sh sed -i '' macOS语法→Linux报错

### 问题描述
deploy_daily.sh 使用 `sed -i ''`（macOS语法）修改 index.html。Linux的sed要求 `sed -i`（不加空字符串参数），macOS版会报 "can't read s|...|: No such file or directory"。

### 修复
- `sed -i ''` → `sed -i`

### 核心教训
> **macOS 和 Linux 的 sed -i 语法不同。容器是 Linux，脚本必须用 Linux 语法。macOS 专有语法属于"Code模式遗留"，Work模式必须清理。**

---

## 经验#105 — 2026-05-04 — orchestrator cmd_push 调用已废弃脚本→推送失败

### 问题描述
ai_daily_orchestrator.py 的 cmd_push() 函数调用 `send_ai_daily.py --preview`，但该脚本已废弃（归档到 _archive/）。如果 orchestrator 自动执行推送步骤，会因找不到脚本而失败。

### 修复
- cmd_push() 从调用 send_ai_daily.py 改为调用 build_insight_mixcard.py 生成 mixCard JSON
- 推送逻辑变为：生成JSON → Agent读取并通过 message 工具发送

### P0红线新增
- **orchestrator 自动推送必须调用 build_insight_mixcard.py，禁止调用已归档脚本**

### 核心教训
> **废弃脚本不只影响手动调用——orchestrator等自动化流程也可能引用它。废弃时必须同步更新所有引用方。**

---

## 经验#106 — 2026-05-05 — MixCard {{message}} 占位符泄露为明文

### 问题描述
用户反馈部分 KIM 卡片消息末尾会错误地显示 `{{message}}` 纯文本，破坏卡片视觉。

### 根因
KIM MixCard 渲染机制：当 `message` 工具同时传了 `kimMixCard` 和 `message` 文本参数时，系统会将 `message` 内容注入到卡片模板中 `{{message}}` 占位符位置。如果：
- 卡片模板里包含 `{{message}}`，但没传 `message` 参数 → 占位符原样渲染为 `{{message}}`
- 卡片模板里不该有 `{{message}}`，但使用了带占位符的旧模板 → 占位符也会原样渲染

### 修复
- 发 MixCard 时**不传 `message` 字段**（只传 `kimMixCard` + `target`），或保证 `message` 为单个空格 `" "`
- 生成卡片 JSON 时，确保 kimMd 内容中**完全不含** `{{message}}` 占位符
- 如果需要动态内容注入，在 Python 脚本里完成字符串拼接，不留模板占位符

### P0红线新增
- **发 MixCard 时不传 `message` 字段（或只传单个空格），禁止传任何有意义文本——否则会被渲染为卡片顶部/底部的额外文案，或触发 `{{message}}` 泄露**
- **卡片 kimMd 内容中禁止包含 `{{message}}` / `{{...}}` 等模板占位符**

### 核心教训
> **MixCard 不是"卡片+消息"双通道，而是"卡片即全文"。任何 `message` 字段内容都会以不可控方式泄露到渲染结果中。只传 kimMixCard，不传 message。**

---

## 经验#107 — 2026-05-05 — 发群用 groupId 直传 vs space:<groupId> 格式不一致导致第3群失败

### 问题描述
用 `target: "6646213728505891"` 发群失败（提示"发送者不是群成员"），换成 `target: "space:6646213728505891"` 后成功。

### 根因
KIM message 工具对群聊的 `target` 格式有要求：
- 群聊**必须**用 `space:<groupId>` 格式
- 私聊用 `username:<username>` 或直接 username
- 直接传 groupId 会被识别为用户而非群，导致权限校验失败

### 修复
- 统一所有群发使用 `target: "space:<groupId>"` 格式

### P0红线新增
- **KIM 发群必须用 `target: "space:<groupId>"` 格式，禁止直接传 groupId 数字**

### 核心教训
> **私聊和群聊的 target 格式不同。群聊不加 `space:` 前缀 = 被当作用户处理 = 权限失败。这不是"可选优化"，是硬性格式要求。**

---

## 经验#108 — 2026-05-05 — 手动构造 kimMixCard JSON 对象格式错误（text 应为 kimMd object）

### 问题描述
手动在 message 工具参数里写 `kimMixCard` JSON 时，`text` 字段直接写了纯字符串，而非 `{"type": "kimMd", "content": "..."}` 对象格式，导致卡片内容为空或渲染异常。

### 根因
MixCard blocks 中 `type: "content"` 的 `text` 字段要求特定结构：
```json
"text": {"type": "kimMd", "content": "实际内容"}
```
手动构造时容易写成：
```json
"text": "实际内容"  ← 错误
```

### 修复
- **禁止手动构造 kimMixCard JSON**——必须通过 `build_insight_mixcard.py` 脚本生成 JSON 文件，然后用 `read` 读取文件内容，将 JSON object 传给 `kimMixCard` 参数

### P0红线新增
- **禁止手动内联编写 kimMixCard JSON——必须用脚本生成文件、读取后传入。手动构造 = 格式错 = 空卡片**

### 核心教训
> **MixCard 的嵌套 JSON 格式（config/blocks/actions/text 对象）太复杂，人类/Agent 手写必然出错。脚本生成 = 格式正确 = 可维护。唯一入口，不接受内联。**

---

## 经验#109 — 2026-05-05 — PROJECT_ROOT 指向 skill 目录而非仓库 → 脚本找不到周报文件 → 发出空内容兜底卡片

### 问题描述
build_insight_mixcard.py 的 `PROJECT_ROOT = Path(__file__).resolve().parent.parent` 指向 skill 目录（`user-skills/sl-ai-insight/`），而非实际的 AI-Insight 仓库（`user-skills/sl-ai-insight/` 下有 `01-daily-reports/` 等目录的仓库）。

脚本找不到 `weekly-2026-W18.md`，走空内容兜底逻辑，发出 "(周报尚未生成)" 卡片。

### 根因
脚本假设自己所在目录的 parent parent 就是项目根目录，但 Work 模式下 skill 目录和仓库目录的层级关系不同：
- skill 脚本路径: `user-skills/sl-ai-insight/scripts/build_insight_mixcard.py`
- `parent.parent` = `user-skills/sl-ai-insight/`（skill 目录 = 仓库目录 ✅，但之前容器里路径不对）

实际问题是容器重建后目录结构变化，脚本里的硬编码路径不再正确。

### 修复
- PROJECT_ROOT 优先检测多个候选路径（仓库目录 > skill 目录），动态选择包含 `01-daily-reports/` 的路径
- 如果所有候选路径都不包含日报目录，则报错退出而非静默兜底

### P0红线新增
- **脚本的项目根目录必须动态检测（检查 `01-daily-reports/` 是否存在），禁止硬编码路径**
- **找不到文件时必须报错退出，禁止静默降级为空内容兜底卡片——空卡片比报错更危险**

### 核心教训
> **静默兜底是 Agent 推送场景的毒药。找不到源文件时"发个空卡片"比"报错不推"更糟——用户看到空卡片会以为内容真没了，报错反而能触发修复。fail loud, don't fail silent。**

---

## 经验#110 — 2026-05-05 — 卡片内容结构 ≠ MD全文：快扫场景必须结论先行、精简有锚

### 问题描述
W18 周报卡片直接复用 MD 全文内容，Top 5 每条展开3段正文+3条来源链接，5条堆在一起 = 10屏纯文本轰炸。用户反馈"内容太简要"实际是"没有视觉锚点、扫不到结论"。

### 根因
**卡片阅读场景（手机KIM、快扫）≠ 网页阅读场景（浏览器、深度阅读）**。MD 全文适合后者，但直接搬到卡片里信息密度过高、节奏感缺失。

### 修复
重构 `build_weekly()` 函数的卡片内容提取逻辑：

| 维度 | 旧版（直接复用MD） | 新版（卡片专用结构） |
|------|-------------------|---------------------|
| **开头** | 无定调 | 本周关键词（概览表格5维度合并） |
| **Top 5** | 标题→3段正文→来源×3（每条2屏） | **结论先行**：标题→影响一句话→1条核心链接（每条半屏） |
| **洞察** | 分析段直接开始 | **标题即结论** → 一句话结论(120字) → 1条支撑链接 |
| **林克洞察** | 被正则截断/不出现 | 独立提取，去 `>` 符号，完整呈现 |
| **按钮** | `📄 查看完整周报 >>` | `📖 深度阅读完整周报 >>` / `📬 订阅AI洞察 · 每周一报` |
| **大小** | 14KB | 4.2KB（紧凑但信息密度更高） |

### P0红线新增
- **卡片内容结构 ≠ MD全文。Top 5 卡片版 = 标题 + 影响一句话 + 1条核心链接，禁止把3段正文+3条来源全搬进卡片**
- **洞察卡片版 = 一句话结论 + 1条支撑链接，禁止把完整分析搬进卡片**
- **卡片必须以"本周关键词"定调句开头，30秒入口不可省**

### 核心教训
> **同一个信息，不同场景需要不同结构。网页版是"展开论证"，卡片版是"结论先行+入口链接"。把全文塞进卡片不是"更丰富"，是"更难读"。密度 ≠ 长度。**

---

## 经验#111 — 2026-05-05 — 日报误群发→日报只私发、周报才群发

---

## 经验#112 — 2026-05-18 — 周报日历更新silent skip + 外部同步阻塞 = cron误判ok但首页+外部版都没更新

### 问题描述
W20周报cron标记ok，交付物自检六项✅，但首页日历点击W20不跳转（日历数据从未更新），外部版连W20 HTML文件都缺失。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | `update_homepage.py` 的 `update_calendar_weekly()` 正则 `[^}]+` 无法匹配嵌套 `{}`，每周日历更新都被跳过，但函数返回 True（silent skip） |
| **第二层** | `sync_to_public.py` 发现 `public/` 有反向泄漏文件，一致性验证 sys.exit(1) 阻塞了整条同步管道，外部版 W20 从未同步 |
| **第三层** | cron 只看退出码 0 判定成功，脚本内部分步骤被跳过 + 验证只检查"字符串包含"不检查日历数据+外部版文件 |

### 暴露时机
用户发现首页周报日历点击无响应，外部版链接404。

### 修复动作（已执行）
1. 重写 `update_calendar_weekly()`：三策略（非贪婪匹配 weeklyReportsData 整块 + 月份行直接搜索 + 已存在快速返回），跳过 = hard fail（返回 False）
2. `sync_to_public.py` 一致性验证降级：sys.exit(1) → 打印 ⚠️ 继续
3. `update_homepage.py` 验证增强：周报模式检查日历数据包含本周周号、外部版HTML存在、外部首页包含周号
4. `weekly-report.md` 新增 P0 强制自检清单（6项）

### 举一反三
- **脚本跳过步骤必须 hard fail，不能 silent return True** — cron ok ≠ 任务完成
- **四位置验证必须纳入交付物自检** — 不能只检查"文件存在"，还要检查"日历有周号""外部版到位"
- **一致性验证应该是 warning 不是 blocker** — 历史残留不应阻止新内容上线
- **所有"跳过并返回True"的代码路径都是定时炸弹** — 只要有一个步骤被跳过但返回成功，cron就会误判

### 问题描述
5月5日日报完成后，Agent将日报卡片群发到3个群聊——这是周报的推送逻辑，日报不应该群发。skill文档里已写明"AI日报→shenlang+订阅者私发，AI周报→所有群"，但刚做完周报群发操作后惯性沿用。

### 根因链
1. 周报群发刚执行完（3个群逐一发卡），操作记忆最强
2. 切到日报时没重新检查"推送范围说明"表格
3. skill文档里推送范围表格只是一个说明性段落，没有P0红线级别的醒目度

### 修复
1. workflow.md Step 5 推送范围升级为 ⛔P0 红线，加醒目标注和根因溯源
2. Step 5 禁止列表新增"禁止日报群发"条目
3. 完成摘要里"KIM推送"行改为明确"私发shenlang+订阅者（日报不群发）"

### P0红线新增
- **⛔ 日报只私发，绝不群发。群发日报 = P0违规，即使内容完整也是错的**
- **做完周报群发后切日报，必须重新确认推送范围——惯性是最大的敌人**

### 核心教训
> **日报和周报的推送逻辑完全不同，但操作高度相似。相似性导致惯性错误——最危险的不是不知道规则，而是刚做完类似操作后"顺手"沿用。必须在切换时设置显式检查点。**

---

## #113 日报首页/索引不更新 = 404体验 + 用户信任损耗（2026-05-08）

### 问题描述
5月7日和5月8日的日报HTML文件已生成并部署，但：
- 外部版首页（xiaoxiong20260206.github.io/ai-insight-public/）日历注释写着"最新: 2026-05-07"，日报索引页"最新"条目停在2026-05-05
- 用户点击首页日报链接，跳到旧日期或找不到最新日报
- 内部版首页同样问题

### 根因链
1. orchestrator finalize 脚本更新了 HTML/MD 产物和首页"最新日报链接"，但**没有更新日历注释中的日期标记**和**日报索引页的最新条目**
2. sync_to_external.py 的 --verify 模式因为 SSH vs HTTPS URL 不匹配而 abort，导致外部仓库同步文件复制了但没 git push（5月8日修复后 push 成功，但索引数据仍是旧的）
3. 每次日报完成后，首页和索引页的更新依赖人工或 orchestrator 的一次性写入，缺少"二次校验"机制

### 修复
1. 手动更新内外版 index.html 日历注释：`最新: 2026-05-07` → `最新: 2026-05-08`
2. 手动更新内外版 01-daily-reports/index.html 最新条目：2026-05-05 → 2026-05-08
3. 修复 sync_to_external.py 的 SSH/HTTPS URL 验证逻辑（接受两种格式）
4. **自动化修复**：在 orchestrator finalize 流程末尾增加"首页索引二次校验"步骤，确保：
   - 日历注释中的"最新"日期与当天一致
   - 日报索引页"最新"条目指向当天日期
   - 如果不一致，自动更新

### P0红线新增
- **⛔ 日报完成后，首页和索引页必须同步更新到当天日期。首页数据滞后 = 用户看到的404 = P0级体验故障**
- **⛔ 部署完成后的验收标准：首页"最新日报"日期 == 当天日期 + 日报索引页最新条目 == 当天日期 + 两个站都能200访问**

### 核心教训
> **部署≠发布。文件 push 了不代表用户能看到正确的入口。首页和索引是用户找到内容的唯一路径，它们必须和内容同步更新——否则产出了等于没产出。**

---

## 2026-05-08: 内部站 Pages 404 根因与修复（教训 #114）

---

## #115 首页日历周报入口缺失 + 外部版身份泄露 + Stats过时（2026-05-20）

### 问题描述
沈浪要求"日历上既能找到周报又能找到日报"。排查后发现三类问题：

1. **日历交互缺陷**：同一天既有日报又有周报时，点击只跳日报，周报入口丢失
2. **外部版身份泄露**：`sync_to_public.py` 脱敏正则未覆盖 Header 区的 `<img>` + `<div>` 结构，外部版仍展示林克头像、"林克的AI洞察"、"沈浪让我负责的AI洞察项目"
3. **首页数据过时**：Stats 区域"47知识文档""26深度调研"与实际不符，周报卡片描述写的"测试"，本质洞察区块日期硬编码"2026-03-06"

### 根因链

| 问题 | 根因 |
|------|------|
| 日历周报入口丢失 | JS 逻辑 `hasReport && hasWeekly` 时 `url = reportUrl`，周报 URL 被忽略 |
| 外部版身份泄露 | `sanitize_html()` 正则只匹配"林克的AI洞察"等文本模式，不匹配 Header 区 `<img src="link-avatar-small.webp">` + `<span>林克的AI洞察</span>` 的嵌套 HTML 结构 |
| Stats 过时 | 首页数字硬编码，无数据源联动，无人定期维护 |
| 本质洞察日期硬编码 | 写死"2026-03-06更新"，之后多次知识库更新都没改 |

### 修复（已执行）

**第一轮 — 日历日报+周报双入口**：
1. 日历点击同天 → 弹窗选择菜单（日报/周报二选一）
2. 新增往期周报 pill 列表（W10→W20）
3. 日历图例改为四种：日报 / 日报+周报 / 仅周报 / 今天
4. 周报卡片描述"测试"→"一周AI行业动态深度汇总"

**第二轮 — 整体检查优化**：
5. 日报最新条目描述去重（原有两个重复 `list-item-desc`）
6. Stats 更新：80+日报/周报、28深度调研
7. 日历菜单弹窗改为向下弹出（避免顶部越界）
8. 渐变日期格 hover 时小条颜色适配
9. 本质洞察区块日期改为"持续迭代"
10. Footer 新增外部版链接

**第三轮 — 外部版脱敏**：
11. 手动移除外部版林克头像 `<img>`
12. "林克的AI洞察"→"AI行业洞察"
13. 标题→"AI洞察 · 持续追踪AI行业动态"
14. "林克实现"→"AI实现"

### 举一反三

1. **外部版脱敏不能只靠正则** — 正则匹配文本模式，但 HTML 结构变化时（新增 img/div/span 嵌套）可能不命中。每次改首页后必须 `grep -n '林克\|沈浪' ai-insight-public/index.html` 事后验证
2. **首页硬编码数字需要维护节奏** — 不是"写一次就不管了"，每月至少检查一次
3. **日历交互逻辑要在设计时就考虑双内容** — "同一格有两种内容"是日历的常见需求，不是边缘情况
4. **"测试"文案不能上线** — 周报卡片描述是用户第一眼看到的，必须正式

### P0红线新增

- **⛔ 外部版每次 push 前必须 grep 验证零身份泄露（林克/沈浪/AI分身/link-avatar-small）**
- **⛔ 日历同天有日报+周报时必须提供双入口，禁止只跳日报**
- **⛔ 首页禁止出现"测试"等非正式文案**
- **⛔ 首页禁止硬编码日期（如"2026-03-06更新"），用"持续迭代"或动态生成**

### 已沉淀到

- `reference/homepage-spec.md` v2.0：新增日历双入口规范、Stats 维护规则、外部版验证命令
- `reference/lessons-learned.md` #115

- **现象**: 05-07/05-08 日报在内部站（ai-insight）404，外部站（ai-insight-public）200
- **根因链**:
  1. GitHub Pages native deployment 的 `Upload artifact` 步骤持续失败（3次）
  2. peaceiris/actions-gh-pages workflow 成功部署了 gh-pages 分支内容
  3. 但 `public/01-daily-reports/` 里只有跳转页 `.html`（指向 `-v3.html`），没有完整版
  4. 完整版 `-v3.html` 只在仓库根目录的 `01-daily-reports/` 里，不在 `public/` 里
  5. Pages 只部署 `public/` 目录 → 跳转页部署成功但跳转目标 404
- **修复**:
  1. 删除 `public/` 里所有 `-v3.html`（含内网敏感信息，不应在 public/ 中）
  2. 确保 `sync_to_public.py` 正确生成脱敏完整版 `.html`（不带 -v3 后缀）
  3. 手动触发 gh-pages 重建
  4. orchestrator v9.12 新增 Pages 可达性验证（finalize 后 curl 验证 + 失败自动重建）
- **关键认知**: `public/` 目录的双重角色——既是内部站 Pages 部署源，又是外部版同步源。v3 文件不能进 public/（敏感词泄露），但 public/ 的日报 HTML 必须是完整版（不是跳转页）
- **⛔ 红线**: `public/` 里禁止存在 `-v3.html` 文件（敏感词泄露 + Pages 跳转死链）；`public/` 里的日报 `.html` 必须是脱敏完整版（≥50KB，不是跳转页）
- **⛔ 红线**: finalize 后必须验证 Pages 可达性（curl 200），失败时自动触发重建最多3次

---

## 经验#118 — 2026-05-26 — sync_to_external覆盖外部首页脱敏版

### 问题描述
外部首页 `https://xiaoxiong20260206.github.io/ai-insight-public/` 定期被更新为"脱敏状态"，内部版和外部版内容切换。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | `sync_to_external.py` 的 `sync_all()` 无差别复制 `public/` 所有文件到 `ai-insight-public/`，包括 `index.html` |
| **第二层** | `public/index.html` 是内部原始版（含林克×4、沈浪、快手等），v3.0 设计为"保留原始内容用于内部Pages部署" |
| **第三层** | `sync_to_public.py` 的 `sync_index()` 单独写入脱敏版到 `ai-insight-public/index.html`，但被 `sync_all()` 覆盖 |

### 暴露时机
每次 AI洞察日报 cron (08:00) 或手动 finalize 执行后，外部 GitHub Pages 出现敏感词泄露。

### 修复动作（已执行）
1. 修改 `sync_to_external.py` v2.1 → v2.2：`sync_all()` 跳过根级 `index.html`
2. 回滚今日错误推送（commit 4219855），重新推送正确脱敏版
3. 验证：GitHub 仓库 index.html = 126KB，敏感词零残留

### 关键认知
- `public/` 目录的双重角色：**内部Pages部署源**（保留原始）+ **外部版同步源**（需脱敏）
- 外部版 `index.html` 必须由 `sync_to_public.py` 单独处理，不能走 `sync_all()` 批量复制

### ⛔ 红线（新增）
**`sync_to_external.py` 的 `sync_all()` 禁止复制根级 `index.html`**——外部首页由 `sync_to_public.py` 单独脱敏写入。

---

## 经验#119 — 2026-06-05 — frontend-cloud部署失败被当非阻断 → MixCard按钮指向过期内容/404

### 问题描述
用户点击AI洞察日报KIM MixCard按钮「查看完整日报」后无法打开日报页面。内部版frontend-cloud未更新，MixCard按钮URL指向过期内容。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | `deploy_daily.sh` Step 8 frontend-cloud部署失败只打⚠️警告，不阻断流程 |
| **第二层** | cron agent绕过deploy_daily.sh做"手动部署"，跳过了frontend-cloud部署步骤 |
| **第三层** | MixCard按钮URL硬编码指向frontend-cloud内部版，但没有任何机制验证该URL是否可达 |

### 暴露时机
用户点击MixCard按钮无法打开日报。state.json记录"手动部署+git push成功+外部同步完成+GitHub Pages推送成功"，唯独缺"frontend-cloud部署成功"。

### 修复动作（已执行）
1. `deploy_daily.sh` Step 8：frontend-cloud部署失败从⚠️非阻断→❌硬性阻断（DEPLOY_FAIL=1）
2. 手动执行frontend-cloud deploy恢复服务
3. `build_insight_mixcard.py` 已有--verify-urls校验（HTTP可达性），但cron环境可能跳过

### 关键认知
- MixCard按钮URL = frontend-cloud内部版 → **frontend-cloud部署失败 = 用户无法查看日报**
- "非阻断"逻辑在此场景下是错误的：外部版(GitHub Pages)能用≠内部版能用
- cron agent的"手动部署"模式容易遗漏步骤，必须依赖脚本而非手动操作

### ⛔ 红线（新增）
**`deploy_daily.sh` frontend-cloud部署失败=硬性阻断**（设DEPLOY_FAIL=1），禁止当作warning继续。MixCard按钮依赖frontend-cloud内部版URL，部署失败=用户404。

---

## 经验#120 — 2026-06-05 — 周报badge链接全部指向同一URL（全部→W21）

### 问题描述
AI洞察首页「往期周报」区域的12个周报badge（W10-W21）点击后全部打开同一份周报（W21），而非各自对应的周报。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | 所有badge的href硬编码为`weekly-2026-W21.html`，未逐个区分 |
| **第二层** | 首页更新时使用批量替换，新周报上线只改了"最新"卡片，未同步更新往期badge链接 |
| **第三层** | 无自动化校验机制检查badge href与显示文本是否匹配 |

### 暴露时机
用户发现W10、W14等历史周报badge点击后打开的是W21周报，无法查看对应期数。

### 修复动作（已执行）
1. 逐个修正badge href：W10→W10.html, W11→W11.html, ... , W21→W21.html
2. 补回W21 badge（W22成为最新后W21应出现在往期但缺失）
3. 修正weeklyReportsData日历映射：5月{4:W19, 11:W20, 18:W21, 25:W22}
4. 修正最新周报卡片链接：W21→W22

### 关键认知
- **badge文本≠badge链接**：显示"W14"但href可以指向任何URL，必须逐对验证
- **周报更新三联动**：最新卡片→往期badge补旧→日历weeklyReportsData映射
- **日历映射用周一起始日**：W19起05/04(Mon)，不是05/05

### ⛔ 红线（新增）
**周报更新必须三联动**：①最新卡片→新周报URL ②往期badge→补上一期 ③weeklyReportsData→修正映射。任何一环遗漏=链接错误。

---

## 经验#121 — 2026-06-05 — 日报footer首页链接内部版用外部URL / 外部版用内部URL

### 问题描述
日报HTML footer的「访问AI洞察首页」链接指向错误：
- 内部版（frontend-cloud服务）：3天链接到错误外部URL（`ai-insight/`少了`-public`），2天链接到外部URL
- 外部版（GitHub Pages）：30+天链接到内部URL（corp.kuaishou.com）

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **第一层** | gen_daily_html.py模板正确使用INTERNAL_PAGES_BASE，但cron agent手动编辑覆盖了footer URL |
| **第二层** | 外部版同步(sync_to_external)时未区分footer URL，内部URL原样复制到外部仓库 |
| **第三层** | 无自动化校验区分内部版和外部版的footer URL应该不同 |

### 暴露时机
全面排查发现：73个日报HTML文件的footer链接不一致。

### 修复动作（已执行）
1. 内部版public/所有日报footer→统一用`https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/`
2. 外部版ai-insight-public/所有日报footer→统一用`https://xiaoxiong20260206.github.io/ai-insight-public/`
3. 源目录v3文件footer→统一用内部URL
4. 重新部署frontend-cloud + push外部仓库

### 关键认知
- **双版本footer URL不同**：内部版→内部首页URL，外部版→外部首页URL
- **gen_daily_html.py模板是对的**：它用INTERNAL_PAGES_BASE生成内部版footer
- **问题出在cron agent手动覆盖**：agent修改HTML时可能用了错误的URL
- **sync_to_external.py需要加footer URL替换**：同步外部版时自动替换footer URL

### ⛔ 红线（新增）
**内部版日报footer→内部首页URL，外部版日报footer→外部首页URL**。sync_to_external.py同步时必须替换footer URL。cron agent禁止手动修改footer URL（必须用gen_daily_html.py重新生成）。

---

## 经验#122 — 2026-06-07 — 手动修复绕过脚本遗漏 frontend-cloud 部署 + state.json 虚假标记

### 问题描述
cron 日报流程 deploy 步骤失败后，手动修复时遗漏了 frontend-cloud 部署和 KIM MixCard 推送，导致内部版首页/日报在 frontend-cloud 上未更新，用户点击 KIM 卡片按钮仍 404。同时 state.json 被手动标记为 deploy completed，掩盖了实际遗漏。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **L1** | cron agent deploy 步骤失败，但错误信息只有"部署失败"，无具体子步骤/exit code/stderr |
| **L2** | 手动修复时绕过 deploy_daily.sh 脚本直接分步执行，遗漏了 Step 8（frontend-cloud deploy）和 Step 5（KIM推送） |
| **L3** | state.json 被手动标记为 deploy/push completed，撤销了自动恢复能力 |

### 与经验#119的关系
**同源复发**：6月5日 #119 也是手动绕过脚本遗漏 frontend-cloud → 用户 404。同一个坑踩两次。根本原因是"手动修复走记忆不走脚本"的模式没有被制度化阻断。

### 修复动作（已执行）
1. 执行 `npx @codeflicker/frontend-cloud-cli@latest deploy`（在 public/ 目录）恢复内部版
2. 重新生成 KIM MixCard 并推送给用户
3. 本次复盘 + 举一反三

### ⛔ 红线（新增）

**红线 1：修复 deploy 失败必须走脚本，禁止手动分步拼凑**
- ✅ `bash scripts/deploy_daily.sh YYYY-MM-DD`（一步到位，含所有校验）
- ✅ `python3 scripts/ai_daily_orchestrator.py finalize --date YYYY-MM-DD`
- ❌ 手动执行 gen_daily_html + sync + git push（遗漏概率高）

**红线 2：state.json 禁止手动标记 completed**
- 修复完成后让脚本自己更新 state.json
- 如果必须手动修复，只标记实际完成的步骤，pending 的保持 pending
- 虚假 completed = 比"状态未知"更危险（撤销了系统自我恢复能力）

**红线 3：deploy 失败的错误信息必须包含子步骤、exit code、stderr**
- 现状：只有 `"error": "部署失败"` → 无法定位根因
- 要求：记录失败的具体子步骤名、exit code、stderr 前 500 字

---

## 经验#123 — 2026-06-08 — MixCard按钮URL指向内部版→SSO拦截→用户看到"无法跳转"

### 问题描述
用户连续两天（6/7、6/8）点击AI日报KIM MixCard按钮后无法跳转到日报网站。按钮看似正常但点击后被快手SSO拦截，跳转到登录页，看起来像"按钮失效"。

### 根因链（三层）

| 层级 | 具体原因 |
|------|----------|
| **L1** | MixCard按钮URL指向 `ai-insight-internal.frontend-cloud.corp.kuaishou.com`（内部版），需要快手SSO登录才能访问 |
| **L2** | KIM WebView没有快手SSO cookie → 点击按钮 → frontend-cloud accessproxy拦截 → 302跳转SSO登录页 |
| **L3** | P0 #13规则设计为"私发用内部版"——以为快手员工在KIM里能自动SSO，但实际上KIM WebView和浏览器是两个独立会话 |

### 与经验#119/#122的关系
- #119/#122：frontend-cloud部署失败→按钮404（部署层面）
- #123：frontend-cloud部署成功→但SSO拦截→按钮"无法跳转"（访问层面）
- **同源但不同层**：前两个是部署问题，这次是URL选择问题

### 修复动作（已执行）

1. **脚本修复**：`build_insight_mixcard.py` 所有按钮URL统一使用外部版（GitHub Pages）
   - REPORT_BASE_URL 从 `INTERNAL_BASE` 改为 `EXTERNAL_BASE`
   - PROJECT_URL 从 `INTERNAL_BASE` 改为 `EXTERNAL_BASE`
   - build_research() 和 build_product_essence() 的 report_url 也改为 `EXTERNAL_BASE`
   - --target 参数仅控制 footer 文本（private=林克身份, group=脱敏身份），不再控制按钮URL

2. **规则修复**：P0 #13 从"私发用内部版"推翻为"统一用外部版"
   - 内部版URL仅适合在已登录快手SSO的浏览器里直接访问（首页浏览等）
   - MixCard按钮场景必须用外部版，因为KIM WebView无法自动继承SSO会话

3. **deploy_daily.sh 结构修复**：Step 8（frontend-cloud部署）从 exit 1 之后移到之前
   - 旧版：验证失败→exit 1→frontend-cloud部署永远不执行
   - 新版：frontend-cloud部署→验证→exit（确保部署总是被执行）

4. **手动部署frontend-cloud**：重新部署 internal 版确保首页和日报在内部版也可访问

5. **重新推送修正MixCard给shenlang03**：按钮URL改为外部版

### ⛔ 红线（修正/新增）

**红线修正：P0 #13 — MixCard按钮URL统一使用外部版（GitHub Pages）**
- ❌ 旧规则：私发用内部版，群发用外部版
- ✅ 新规则：所有MixCard按钮统一用外部版——因为内部版需要SSO，KIM WebView无法自动继承SSO会话
- --target 仅控制 footer 文本，不控制按钮URL

**红线新增：frontend-cloud部署必须在最终验证之前**
- ✅ deploy → validate → exit
- ❌ validate → exit → deploy（deploy永远不执行）
- 根因：deploy_daily.sh Step 8 放在 exit 1 之后，验证失败时frontend-cloud部署被跳过

### 核心教训

> **"私发用内部版"的设计假设是快手员工在KIM里能自动SSO——这个假设是错的。KIM WebView和浏览器是两个独立会话，SSO cookie不会自动继承。**

> **需要SSO的URL不适合做按钮跳转目标。按钮是给所有点击场景准备的，必须零门槛可达。**

> **脚本步骤顺序是隐性逻辑——放在exit之后的步骤等于不存在。结构审查不仅要看功能，还要看执行顺序。**
