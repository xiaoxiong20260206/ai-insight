# AI洞察 踩坑经验汇总
> **版本**: v1.6
> **更新时间**: 2026-05-04
> **用途**: 踩坑经验归档记录。**关键教训已提取到 `daily-report/workflow.md` 对应Step中**。
> **定位**: 本文件是历史归档，执行时以 `workflow.md` 为唯一参考。
> **注意**: 这些经验同时存在于记忆系统（common_pitfalls_experience），meta-execution启动时会自动检索。
---
## [迁移自记忆 2026-03-28] AI日报链接处理核心规则（合并版v8.2）
> 原记忆ID: 927ee0d2296a8424 | 迁移原因: skill_coupled，内容专属于 sl-ai-insight 技能
### 链接处理规则
1. **单一数据源**：所有链接从源文件（日报MD）自动提取，禁止手动输入/硬编码
2. **链接提取模式**：`r'[🔴🟡]\s*\*\*\[([^\]]+)\]\(([^)]+)\)\*\*'`
3. **禁止裸 URL 含下划线**：必须用 `[描述](URL)` 格式
4. **微信来源链接**：用搜狗搜索URL `weixin.sogou.com/weixin?type=2&query=...`
5. **小红书来源链接**：用权威公开链接（如36氪、VentureBeat），热度数据仅作标注
6. **禁止**：xiaohongshu.com/explore 或...

---

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
    python3 scripts/sync_to_external.py --full --verify
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
    python3 scripts/sync_to_external.py --full --verify
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
1. **会话恢复时**：先执行 `python3 scripts/ai_daily_orchestrator.py status` + 检查 `data/flags/step1-completed.flag` → 已存在则直接跳到 Step 2
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
