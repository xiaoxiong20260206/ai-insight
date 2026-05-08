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
| `wechat-articles` | 微信文章 |
| `quark-search` | 国内搜索 |
| `sl-ai-insight/reference/kim-doc/` | KIM Doc格式规范 |

## P0红线速查（完整版见 `reference/p0-redlines.md`）

1. 续接必须先 `resume` — 无例外
2. KIM卡片必须用脚本生成 — 禁止手写
3. mixCard只推一次 — 禁止重复
4. 质量门失败 = 重做 — 禁止绕过
5. 必须走 orchestrator — 禁止直接 deploy
6. 6处联动失败 = 阻断
7. 日报只私发订阅者 — 严禁群发
8. 外部版禁止 raw cp — 必须走脱敏脚本

## 踩坑经验（完整见 `reference/lessons-learned.md`）

高频必读：#36 质量门博弈、#54 联动绕过、#61 KIM退化纯文本、#111 误群发

## 订阅系统

KIM DM「订阅AI日报」/「取消订阅AI日报」→ AGENTS.md订阅协议自动处理。数据：`data/subscribers.json`