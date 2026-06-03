---
name: sl-ai-insight
description: AI行业洞察平台专属技能。唤醒：「AI洞察」「AI日报」「AI周报」「跑一下日报」「AI有什么动态」「AI深度调研」。不唤醒：研发效能用sl-rd-efficiency-insight。
export:
  policy: never
  reason: 快手AI洞察项目，公司绑定+个人定制
---

# sl-ai-insight — AI行业洞察

> 系统化追踪AI行业动态，每日/每周输出调研洞察。

## 项目目标

AI洞察是一个**AI驱动的行业研究平台**，核心做四件事：

1. **产出**：AI日报、周报、深度调研——稳定、准确、持续地输出行业洞察
2. **沉淀**：每次跑完报告/调研，对应的知识自动沉淀到追踪体系和知识库，保持新鲜度
3. **呈现**：所有信息同步更新到内外部首页，首页必须能看到最新的日报、周报、深度调研（按月呈现）、追踪体系、知识库
4. **订阅**：内部同学可订阅AI日报，订阅后自动接收推送

### 双版本体系

| 版本 | URL | 说明 |
|------|-----|------|
| 内部版 | `https://ai-insight-internal.frontend-cloud.corp.kuaishou.com` | 林克品牌+订阅按钮+内部链接 |
| 外部版 | `https://xiaoxiong20260206.github.io/ai-insight-public` | 通用品牌，零敏感词，GitHub Pages 托管 |

每次新增内容，必须同时生成内部版和外部版，并同步更新两个首页。

**内部版 vs 外部版的设计分界线**：

| 元素 | 内部版 | 外部版 |
|------|--------|--------|
| 林克头像 | ✅ `link-avatar-small.webp` | ❌ 隐藏 |
| 标题 | "我是林克，这是沈浪让我负责的AI洞察项目" | "AI洞察 · 持续追踪AI行业动态" |
| Badge | "林克的AI洞察" | "AI行业洞察" |
| Highlight卡片 | "林克：AI不是工具，是项目成员" + "我是林克，沈浪的AI分身。" | "AI不是工具，是项目成员" + 去身份描述 |
| 订阅按钮 | ✅ | ❌ 外部不可订阅 |
| 外部版入口 | ✅ | ❌ 不需要 |
| Footer | "❤️‍🔥 林克 · 你负责往前走，记忆这种事我来" | "❤️🔥 AI洞察 · 持续追踪 · 深度洞察" |

**原则**：内部版让人看到"林克在帮沈浪做AI洞察"，外部版让人看到"一个专业的AI行业洞察平台"。

### 闭环约束

- **报告产出 → 知识沉淀**：日报/周报/调研跑完后，必须检查是否有知识需要沉淀到追踪体系或知识库
- **知识沉淀 → 首页更新**：每次内容变更后，必须同步更新两个首页
- **首页 → 订阅推送**：首页是信息的窗口，订阅推送是信息的渠道，两者联动

### 时间轴归档规则（P0 — 2026-06-03 血泪教训）

**根因**：深度调研产出后，手工添加到首页时间轴时，卡片日期和归档月份经常写错——5月报告归到4月，日期写4月20日而非实际5月7日。

**硬规则**：

1. **卡片日期必须从HTML文件提取，禁止手写** — 新增调研卡片时，先从HTML的 `editorial-hero-badge` 或 `📅` 标记提取真实日期
2. **归档月份=日期的年月，不靠猜** — 日期是5月7日，就归到5月；日期是4月8日，就归到4月
3. **没有对应月份的分组就新建** — 不要把5月报告塞进4月分组
4. **计数必须与实际卡片数一致** — 修改后必须验证 `timeline-month-count` 值

**长期方案**：`gen_timeline.py` 脚本可从HTML文件自动提取日期并按月分组，但目前手动调整仍需严格遵守以上规则。

## ⚠️ 元执行保障（必加载）

本技能命中绑定标准 C1+C2+C3+C4+C5（多阶段+外部可见+部署发布+无人值守+数据完整性），**最高优先级**绑定 evo-meta-execution。

**映射关系**：
- **P1 启动** → 环境前置检查(#5) + 技能路由表加载 + 踩坑检索(#1-#11) + 自检声明
- **P0 交付** → 质量门(#4) + fail loud(#6) + 首页脱敏(#7) + 外部版三项替换(#10) + {{message}}禁令(#11) + 知识库禁md链接(#12) + MixCard URL区分场景(#13) + 首页按钮绝对URL(#14)
- **P2 事后** → skill_calls日志 + token记录 + 知识沉淀(Harvest) + 5项自举扫描

**P1 踩坑清单（从14条P0红线提炼高频失败项）**：
1. ❌ 续接必须先resume(#1) — 无例外
2. ❌ MixCard必须用脚本生成(#2) — 禁止手写
3. ❌ uv run替代python/python3(#9)
4. ❌ MixCard {{message}}绝对禁止(#11)
5. ❌ 外部版三项URL替换必须同时完成(#10)
6. ❌ 首页修改必须读homepage-spec.md(#7)
7. ❌ KIM消息发送必须指定target=username:shenlang03
8. ❌ 知识库Tab禁止<a href=*.md>链接(#12) — 用<span>
9. ❌ MixCard群发按钮URL必须用外部版(#13) — 私发用内部版
10. ❌ 订阅按钮禁止./subscribe/相对路径(#14) — 用绝对URL

**自检声明格式**："我已读完SKILL.md+对应子技能workflow+14条P0红线+踩坑10条，准备执行Step X"

## 项目信息

- **内部版**: https://ai-insight-internal.frontend-cloud.corp.kuaishou.com
- **外部版**: https://xiaoxiong20260206.github.io/ai-insight-public
- **项目路径**: `user-skills/sl-ai-insight/`

## 子技能路由表

| 子技能 | 触发词 | 文档 |
|--------|--------|------|
| 输出格式规范 | HTML/卡片/Doc格式 | `reference/output-format-spec.md` ← **公共规范，所有子技能先读此** |
| AI日报 | AI日报/跑日报 | `reference/daily-report/` |
| AI周报 | AI周报 | `reference/weekly-report.md` |
| 深度调研 | AI深度调研/专题 | `reference/deep-research.md` |
| 首页更新 | 更新首页 | `update_homepage.py --type daily/weekly` |
| 首页规范 | 修改首页**必读** | `reference/homepage-spec.md` ← **防改坏规范** |
| 双版本同步 | 同步公开版 | `reference/dual-version-sync.md` |
| 国内信源 | 微信/小红书搜AI | `reference/domestic-sources.md` |
| 学术论文监控 | arXiv/学术动态 | `reference/arxiv-monitor.md` |
| 知识沉淀 | 沉淀AI知识 | `reference/knowledge-accumulation.md` |
| 调研范围管理 | 添加/管理AI追踪 | `reference/scope-management.md` |

> **路由原则**：生成任何输出前 → 先读 `output-format-spec.md`（公共规范） → 再读对应子技能的差异化部分。

## 底层依赖

| 技能 | 用途 |
|------|------|
| `designai-generate-image` | 封面/彩蛋AI生图 |
| `designai-Infographic-image` | 章节配图（信息图） |
| `docs-shuttle` | Docs平台发布 |
| `kim-message-send` | KIM推送 |
| `upload-cdn` | CDN链接 |
| `tavily-search` | 海外搜索 |
| `quark-search` | 国内搜索 |

## P0红线（14条核心红线）

> ⚠️ 只有14条需要Agent自觉遵守。其余校验已内置到脚本。

### 1. 续接必须先 resume — 无例外
```bash
uv run scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD
```

### 2. KIM卡片必须用脚本生成 — 禁止手写
```bash
uv run scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
```

### 3. mixCard只推一次 — 禁止重复

### 4. 质量门硬性失败=重做 — 禁止绕过
硬性失败（板块缺失/JSON结构错/HTML空壳）必须回到对应步骤重做。
软性失败（搜狗URL占比/微信链接格式/覆盖度略低）= 警告不阻断。

### 5. 环境前置检查 — 每次执行必做
```bash
ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com
```

### 6. fail loud, don't fail silent
找不到文件时报错退出，禁止静默降级为空内容兜底卡片。

### 7. 首页修改必须读 homepage-spec.md — 禁止裸复制
- ❌ `cp index.html ai-insight-public/index.html` = 敏感词泄露
- ✅ 必须走 `sanitize_html()` 脱敏流程
- 详见 `reference/homepage-spec.md`

### 7.1 sync_to_external.py 的 sync_all() 禁止复制根级 index.html
- ❌ `sync_all()` 无差别复制 public/ → 覆盖外部脱敏版 = 敏感词泄露（经验#118）
- ✅ `sync_all()` 必须跳过 `index.html`，外部版由 `sync_to_public.py` 单独脱敏
- 已修复：v2.2 版本 `sync_all()` 会自动跳过

### 8. 深度调研执行前必须读完3个规范文件+1个标杆 — 禁止凭感觉动手
- `reference/output-format-spec.md`（公共规范）
- `reference/deep-research.md`（深度调研流程+4组P0规则）
- `reference/kim-doc/writing-style.md`（KIM Doc写作标准）
- `02-deep-research/topics/colleague-skill-anti-distill-2026.html`（标杆HTML源码）
- 不读完不能动手。历史上因不读规范就动手导致反复修改8+轮。

### 9. 所有Python命令必须用 uv run — 禁止 python/python3
- `uv run scripts/xxx.py` ✅
- `python3 scripts/xxx.py` ❌ — 容器中没有python命令，会直接报错
- `uv run skills/quark-search/scripts/agent.py news "关键词"` ✅
- `python skills/quark-search/scripts/agent.py news "关键词"` ❌

### 10. 外部版HTML修改必须完成三项URL替换+线上验证 — 禁止只改一处
修改外部版(`ai-insight-public`)周报/日报HTML时（无论手动还是子agent），必须同时完成：

| 替换项 | 内部版 | 外部版 | 验证方法 |
|--------|--------|--------|---------|
| 仓库域名 | `ai-insight/` | `ai-insight-public/` | `grep -c "ai-insight/"` 在日报链接区域 = 0 |
| 文件后缀 | `-v3.html` | `.html` | `grep -c "\-v3\.html"` = 0 |
| 首页按钮 | 内部版首页URL | 外部版首页URL | 检查所有"访问首页"链接 |

- ❌ 只替换域名但遗漏 `-v3` 后缀 → 外部版日报链接404
- ❌ 只替换后缀但遗漏域名 → 外部版链接跳到内部版
- ✅ 三项都替换 + curl线上验证生效 → 才算完成
- **每次修改外部版HTML后，push之前必须跑 `grep -c "\-v3\.html" file.html` 确认返回0**
- **内部版修改后必须同步到 `public/` 对应路径**（GitHub Pages从public/构建）

### 10.1 容器管布局宽度，文字管可读宽度 — 不可违反
- 卡片/框等容器：`width: 100%`（撑满父宽度，等宽排列）
- 段落/正文文字：`max-width: 68ch`（限制行宽，提高可读性）
- ❌ 在 `.callout`/`.news-card-why`/`.insight-card` 等容器上加 `max-width: 68ch` → 右侧留白参差不齐
- ✅ 在 `.news-card-desc`/`.callout p`/`.insight-text` 等文字节点上加 `max-width: 68ch` → 等宽卡片+可读行宽

### 11. MixCard {{message}} 绝对禁止 — 已记录（见TOOLS.md）

### 12. 知识库Tab禁止可点击的md链接 — 浏览器无法渲染
- ❌ `<a href="04-knowledge-base/*.md">` — Markdown文件浏览器无法渲染，且 `public/` 下不存在
- ✅ `<span class="kb-item">` 展示标题，不可点击
- 2026-06-04：37个链接全部改为span，首页已部署

### 13. MixCard按钮URL区分推送场景
- **私发订阅者**：按钮URL用**内部版**（`ai-insight-internal.frontend-cloud.corp.kuaishou.com`）
- **群发**：按钮URL用**外部版**（`xiaoxiong20260206.github.io/ai-insight-public`）— 群内可能有无法访问内部版的用户
- `build_insight_mixcard.py` 需根据 `--target private|group` 自动选择URL

### 14. 首页按钮必须使用绝对URL — 禁止相对路径
- **订阅按钮**：`https://aidailyinsight-subscribe.frontend-cloud.corp.kuaishou.com`（禁止 `./subscribe/`，frontend-cloud会拦截触发SSO 302）
- **外部版入口**：`https://xiaoxiong20260206.github.io/ai-insight-public/`
- **根因**：frontend-cloud对 `/subscribe/` 路径做SSO认证拦截，点击→302→登录页而非订阅页

---

## 脚本自校验清单

| 脚本 | 校验项 | 失败时行为 |
|------|--------|-----------|
| `build_insight_mixcard.py` | 6锚点+kimMd格式+{{message}}扫描+URL格式 | ❌硬性报错退出 |
| `gen_daily_html.py` | ≥50KB+5板块+{{message}}扫描+overview/深度聚焦 | ❌硬性报错退出 |
| `update_homepage.py` | 内部版+public+索引页包含当天日期 + 周报模式额外检查：日历数据含周号+外部版HTML存在+外部首页含周号 | ❌报错退出 |
| `daily_quality_gate.py` | hard/soft分级 | 硬性阻断/软性警告 |

---

## 核心脚本清单（精简后）

| 脚本 | 用途 |
|------|------|
| `ai_daily_orchestrator.py` | 日报状态机+finalize一键命令 |
| `daily_quality_gate.py` | 质量门（hard/soft分级） |
| `build_insight_mixcard.py` | MixCard生成+自校验 |
| `gen_daily_html.py` | HTML生成+自校验 |
| `gen_weekly_json.py` | 周报JSON模板+schema验证 |
| `gen_weekly_html.py` | 周报HTML生成（从JSON动态生成+自校验≥50KB+5板块+class名一致性+自动cp到public） |
| `update_homepage.py` | 首页更新（统一入口，支持daily+weekly） |
| `deploy_daily.sh` | 日报一键部署 |
| `sync_to_public.py` | 内部版→public+外部版同步 |
| `sync_to_external.py` | 外部版仓库同步+脱敏 |
| `gen_daily_json.py` | JSON模板生成+schema校验（按需） |
| `gen_md_from_json.py` | MD生成（按需） |
| `inject_weekly_links.py` | 周报超链接注入（按需） |
| `update_tracking.py` | 追踪体系更新（低频） |
| `update_weekly_index.py` | 周报首页联动（已归档→update_homepage.py --type weekly） |
| `fetch_arxiv.py` | arXiv论文监控 |
| `daily_env_init.sh` | 环境初始化 |
| `validate_daily_schema.py` | JSON schema校验（按需） |
| `config.py` | 全局配置SSoT |

> 已归档的脚本：fix_0508_json/fix_deep_research_footers/fix_json_quotes/fix_weixin_links/verify_4positions/daily_agent_runner/update_homepage_weekly → `_archive/`

---

## 推送范围

| 类型 | 推送范围 | 禁止 |
|------|---------|------|
| 日报 | 私发订阅者 | ❌禁止群发 |
| 周报 | 仅发AI生产力中心大群(space:6783643915686960) | ❌禁止发其他群 |

---

## 一次到位执行流程（日报）

```
Step 1: 搜索调研 → orchestrator complete --step 1
Step 2: 内容生成 → orchestrator complete --step 2
Step 3+4: finalize → orchestrator finalize（自动:质量门→HTML→首页更新→部署→外部同步）
Step 5: KIM推送 → build_insight_mixcard.py → message(kimMixCard, message="")

**⚠️ MixCard发送格式（P0红线）**：
- `kimMixCard`参数必须传**inner card格式**（`{config, updateMulti, blocks}`直接在顶层）
- ❌禁止传双层格式`{card: {...}, summary: "..."}` — KIM找不到blocks字段会渲染为空消息
- `message`参数必须传空字符串`""`，禁止同时传message和kimMixCard（会导致{{message}}模板注入泄露）
- 脚本输出已改为inner card格式，读取JSON后直接传给message工具即可
```

---

## 订阅系统

- **Web 订阅页面**：https://aidailyinsight-subscribe.frontend-cloud.corp.kuaishou.com （快手 SSO 登录 → 一键订阅/取消）
- **内部首页入口**：`public/subscribe/index.html` 重定向到 Web 订阅页面
- **数据存储**：Appwrite TablesDB（`subscribers` 库 → `daily_subscribers` 表，行级安全）
- **同步脚本**：`scripts/sync_subscribers.py`（Appwrite → `data/subscribers.json`，cron 执行前调用）
- **订阅者推送**：日报 Step 5 读取 `data/subscribers.json`，遍历 `is_active=true` 的用户逐一私发
- **owner 保留**：shenlang03 始终在订阅列表中（source=owner），不可取消
- **⚠️ 订阅按钮路径**：内部首页的订阅按钮**必须直接指向** `https://aidailyinsight-subscribe.frontend-cloud.corp.kuaishou.com`，**禁止使用** `./subscribe/` 相对路径——frontend-cloud会拦截 `/subscribe/` 路径触发SSO 302重定向，导致用户看到登录页而非订阅页（2026-06-03教训）

## 首页规则（补充P0红线）

### P0 #12: 知识库Tab禁止可点击链接
- ❌ `<a href="04-knowledge-base/*.md">` — Markdown文件浏览器无法渲染，且 `public/` 下不存在这些文件
- ✅ `<span class="kb-item"><span class="item-icon">📄</span><span class="item-text">标题</span></span>`
- 适用于内部版和外部版（外部版通过 `sanitize_html()` 自动转换）
- `homepage-spec.md` 已同步更新此规则

### P0 #13: MixCard按钮URL区分推送场景
- **私发订阅者**：MixCard按钮URL使用**内部版**链接（`ai-insight-internal.frontend-cloud.corp.kuaishou.com`），订阅者均为内部员工可访问
- **群发**：MixCard按钮URL使用**外部版**链接（`xiaoxiong20260206.github.io/ai-insight-public`），群内可能有无法访问内部版的用户
- `build_insight_mixcard.py` 需根据推送范围（`--target private|group`）自动选择URL

### P0 #14: 首页按钮必须使用绝对URL
- **订阅按钮**：必须用 `https://aidailyinsight-subscribe.frontend-cloud.corp.kuaishou.com`（见订阅系统⚠️说明）
- **外部版入口**：必须用 `https://xiaoxiong20260206.github.io/ai-insight-public/`
- **禁止相对路径**（`./subscribe/`、`../`等）— frontend-cloud会拦截部分路径触发SSO重定向

### P0 #15: 知识沉淀(Harvest)是P2强制步骤 — 不可跳过
- 日报/周报/深度调研完成后，**必须**检查本次是否有复用价值的洞察/对比/模式
- 有 → 写入 `knowledge/packages/ai-insight/` + 更新 INDEX.md + 更新 MEMORY.md 指针
- 没有 → 简短声明"本次无 Harvest"并继续
- **不做 Harvest = P2 不通过**
- 当前断档：6/2、6/3日报均未做Harvest，需要补做

### 首页统计卡片维护规则（P1 — 定期校准）
- 统计卡片数字是硬编码，无数据源联动
- **每月至少校准一次**：追踪人物/公司/信息源/深度调研/日报周报
- 校准方法：`grep -c '<tr><td><strong>' index.html`（追踪条目）、`find public/02-deep-research -name '*.html' ! -name 'index.html' | wc -l`（深度调研）、`find public/01-daily-reports -name '2026-*.html' ! -name 'weekly-*' | wc -l`（日报）
- 当前值（2026-06-04）：人物100+、公司140+、深度调研30、日报95+周报13

### 日历数据维护规则（P1 — cron自动+手动补漏）
- 日报cron的 `update_homepage.py daily` 会自动更新日历日期数组
- **但以下情况需手动修复**：漏日期（如5/28）、周报映射错误（如W22重复标记31号）、周报缺失（如W21）
- 周报日历映射规则：`weeklyReportsData['YYYY-MM'] = {周一日期: 'weekly-YYYY-Wxx'}`
- ISO周号计算：`date.fromisocalendar(YYYY, W, 1)` → 起始周一日期

## 系统健康检查（2026-06-04 全面复盘）

### 闭环验证结果

| 子系统 | 状态 | 问题 | 修复 |
|--------|------|------|------|
| 日报cron(08:00) | ✅ 运行稳定 | 知识沉淀6/2-6/3断档 | P0#15: Harvest列为P2强制步骤 |
| 周报cron(周一09:00) | ✅ 运行稳定 | W21缺失 | ✅ 补跑完成 |
| 订阅系统 | ✅ 6人活跃 | 非owner推送未验证 | 待08:00 cron验证 |
| 内部首页 | ✅ | 统计失真(22→100+) | ✅ 校准 |
| 外部首页 | ✅ 零敏感词 | — | — |
| 双版本同步 | ✅ | — | — |
| 知识库Tab | ⚠️ | 37个链接→span(临时方案) | 长期: 知识渲染为HTML |
| 追踪体系 | ⚠️ | 无自动保鲜机制 | P1: 待设计cron |
| 时间轴 | ⚠️ | 新调研需手动添加 | P1: gen_timeline.py待集成 |
| 统计卡片 | ⚠️ | 需手动校准 | P1: 月度检查 |

### 知识沉淀断档分析

**现状**：知识沉淀(Harvest)仅在6/1日报执行了一次，6/2-6/3均未执行。
**根因**：日报workflow.md的6步流程中没有明确的Harvest步骤——P2阶段只写了skill_calls日志+token记录，遗漏了知识沉淀。
**修复**：
1. workflow.md Step 5之后增加 Step 6: 知识沉淀(Harvest)
2. SKILL.md P2事后步骤增加Harvest（P0#15）
3. cron payload增加Harvest提示

### 待建设能力（P1优先级排序）

1. **日报workflow增加Harvest步骤** — 已修
2. **追踪体系自动保鲜cron** — 定期扫描新人物/公司，更新追踪清单
3. **时间轴自动生成** — `gen_timeline.py` 集成到 `update_homepage.py`
4. **统计卡片自动校准** — `update_homepage.py` 自动计算实际数值
5. **知识库HTML渲染** — 将md转为可浏览的HTML页面
6. **非owner订阅推送验证** — 08:00 cron后检查3位新订阅者是否收到

## 踩坑经验（归档，不加载）

完整踩坑经验见 `reference/daily-report/lessons-learned.md`，但**执行时不主动加载**。
关键教训已内置到脚本校验逻辑中。