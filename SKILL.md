---
name: sl-ai-insight
description: AI行业洞察平台专属技能。唤醒：「AI洞察」「AI日报」「AI周报」「跑一下日报」「AI有什么动态」「AI深度调研」。不唤醒：研发效能用sl-rd-efficiency-insight。
export:
  policy: never
  reason: 快手AI洞察项目，公司绑定+个人定制
---

# sl-ai-insight — AI行业洞察

> 系统化追踪AI行业动态，每日/每周输出调研洞察。

## 项目信息

- **内部版**: https://xiaoxiong20260206.github.io/ai-insight/
- **外部版**: https://xiaoxiong20260206.github.io/ai-insight-public/
- **项目路径**: `user-skills/sl-ai-insight/`

## 子技能路由表

| 子技能 | 触发词 | 文档 |
|--------|--------|------|
| 调研范围管理 | 添加/管理AI追踪 | `reference/scope-management.md` |
| AI日报 | AI日报/跑日报 | `reference/daily-report/` |
| AI周报 | AI周报 | `reference/weekly-report.md` |
| 深度研究 | AI深度调研/专题 | `reference/deep-research.md` |
| 知识沉淀 | 沉淀AI知识 | `reference/knowledge-accumulation.md` |
| 首页更新 | 更新首页 | `reference/homepage-update.md` |
| 双版本同步 | 同步公开版 | `reference/dual-version-sync.md` |
| 国内信源 | 微信/小红书搜AI | `reference/domestic-sources.md` |
| 学术论文监控 | arXiv/学术动态 | `reference/arxiv-monitor.md` |

> **路由原则**：找到子技能编号 → 去 reference 读详细流程 → 不要在入口文件找执行步骤。

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

## P0红线（6条核心红线，脚本自动校验其余）

> ⚠️ 只有6条需要Agent自觉遵守。其余校验已内置到脚本（mixCard自校验、HTML校验、首页更新脚本）。

### 1. 续接必须先 resume — 无例外
```bash
python3 scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD
```

### 2. KIM卡片必须用脚本生成 — 禁止手写
脚本自带6锚点校验+{{message}}扫描+kimMd格式校验，手写=必错。
```bash
python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
```

### 3. mixCard只推一次 — 禁止重复
preview和正式推送是同一个命令，不要执行两次。

### 4. 质量门硬性失败=重做 — 禁止绕过
硬性失败（板块缺失/JSON结构错/HTML空壳）必须回到对应步骤重做。
软性失败（搜狗URL占比/微信链接格式/覆盖度略低）= 警告不阻断。

### 5. 环境前置检查 — 每次执行必做
```bash
# 项目目录+Git连通+SSH key
ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | grep "successfully"
```
任何项MISSING = 先恢复环境再执行日报。

### 6. fail loud, don't fail silent
找不到文件时报错退出，禁止静默降级为空内容兜底卡片。

---

## 脚本自校验清单（Agent不需要手动检查，脚本自动执行）

| 脚本 | 校验项 | 失败时行为 |
|------|--------|-----------|
| `build_insight_mixcard.py` | 6锚点完整性 + kimMd格式 + {{message}}扫描 + URL格式 | ❌硬性报错退出 |
| `gen_daily_html.py` | ≥50KB底线 + 5板块存在 + {{message}}扫描 + overview/深度聚焦存在 | ❌硬性报错退出 |
| `update_homepage.py` | 内部版+public+索引页包含当天日期 | ❌报错退出 |
| `daily_quality_gate.py` | 硬性:板块+JSON+HTML; 软性:URL+覆盖+链接 | 硬性阻断/软性警告 |

---

## 推送范围（脚本参数控制，不再靠Agent判断）

| 类型 | 推送范围 | 脚本参数 |
|------|---------|---------|
| 日报 | 私发订阅者（禁止群发） | `--scope daily` |
| 周报 | 发所有群 | `--scope weekly` |

---

## 一次到位执行流程（精简版）

```
Step 1: 搜索调研 → orchestrator complete --step 1
Step 2: 内容生成 → orchestrator complete --step 2
Step 3+4: finalize → orchestrator finalize（自动:质量门→HTML→首页更新→部署→外部同步）
Step 5: KIM推送 → build_insight_mixcard.py → message(kimMixCard)
```

> **finalize = 一键命令**，内部自动执行：质量门→HTML生成→首页更新→部署→外部同步→Pages验证。

---

## 订阅系统

KIM DM「订阅AI日报」/「取消订阅AI日报」→ AGENTS.md订阅协议自动处理。数据：`data/subscribers.json`

## 踩坑经验（归档，不加载）

完整踩坑经验见 `reference/lessons-learned.md`（733行），但**执行时不主动加载**。
关键教训已内置到脚本校验逻辑中，不需要Agent逐条检索。