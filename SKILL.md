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

## ⚠️ 元执行保障（必加载）

本技能命中绑定标准 C1+C2+C3+C4+C5（多阶段+外部可见+部署发布+无人值守+数据完整性），**最高优先级**绑定 evo-meta-execution。

**映射关系**：
- **P1 启动** → 环境前置检查(#5) + 技能路由表加载 + 踩坑检索(#1-#11) + 自检声明
- **P0 交付** → 质量门(#4) + fail loud(#6) + 首页脱敏(#7) + 外部版三项替换(#10) + {{message}}禁令(#11)
- **P2 事后** → skill_calls日志 + token记录 + 5项自举扫描

**P1 踩坑清单（从11条P0红线提炼高频失败项）**：
1. ❌ 续接必须先resume(#1) — 无例外
2. ❌ MixCard必须用脚本生成(#2) — 禁止手写
3. ❌ uv run替代python/python3(#9)
4. ❌ MixCard {{message}}绝对禁止(#11)
5. ❌ 外部版三项URL替换必须同时完成(#10)
6. ❌ 首页修改必须读homepage-spec.md(#7)
7. ❌ KIM消息发送必须指定target=username:shenlang03

**自检声明格式**："我已读完SKILL.md+对应子技能workflow+11条P0红线+踩坑7条，准备执行Step X"

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

## P0红线（11条核心红线）

> ⚠️ 只有11条需要Agent自觉遵守。其余校验已内置到脚本。

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

## 踩坑经验（归档，不加载）

完整踩坑经验见 `reference/daily-report/lessons-learned.md`，但**执行时不主动加载**。
关键教训已内置到脚本校验逻辑中。