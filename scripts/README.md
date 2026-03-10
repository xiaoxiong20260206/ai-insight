# AI-Insight Scripts

此目录包含 AI-Insight 项目的自动化脚本。

## 配置

脚本凭证通过环境变量加载，优先级: 环境变量 > `.env` 文件。

```bash
# 首次使用：从模板创建 .env 文件
cp scripts/.env.template scripts/.env
# 编辑 .env 填入实际凭证
```

## 脚本列表

### 📤 推送脚本

| 脚本 | 用途 | 使用方式 |
|------|------|---------|
| `send_ai_daily.py` | AI日报推送到KIM群(v3.5) | `python3 scripts/send_ai_daily.py [日期] [--preview] [--dry-run]` |
| `send_ai_weekly.py` | AI周报推送到KIM | `python3 scripts/send_ai_weekly.py --to-user shenlang` |
| `send_deep_research_card.py` | 深度调研专题推送 | `python3 scripts/send_deep_research_card.py --to-user shenlang` |
| `send_openclaw_card.py` | OpenClaw深度洞察推送 | `python3 scripts/send_openclaw_card.py --to-user shenlang` |

**日报推送参数**:
- `--preview` 先发给自己预览（推荐首次使用）
- `--dry-run` 试运行，不实际发送
- 无参数时推送到所有群

### 🔄 同步脚本

| 脚本 | 用途 | 使用方式 |
|------|------|---------|
| `sync_to_public.py` | 内部版→public目录脱敏 | `python3 scripts/sync_to_public.py --all --force` |
| `sync_to_external.py` | public目录→外部仓库同步 | `python3 scripts/sync_to_external.py` |

### 🔧 工具脚本

| 脚本 | 用途 | 使用方式 |
|------|------|---------|
| `fix_deep_research_footers.py` | 深度调研报告底部统一修复 | `python3 scripts/fix_deep_research_footers.py` |
| `kim_client.py` | KIM API 公共客户端模块 | (被其他脚本导入使用) |

### ⏰ 定时任务

| 文件 | 用途 | 触发时间 |
|------|------|---------|
| `com.codeflicker.ai-daily-report.plist` | 日报定时配置 | 每日 08:00 |
| `com.codeflicker.ai-weekly-report.plist` | 周报定时配置 | 每周一 10:00 |
| `run-ai-daily-report.sh` | 日报执行脚本 | 被plist调用 |
| `run-ai-weekly-report.sh` | 周报执行脚本 | 被plist调用 |

**执行架构（委托模式）**:
```
launchd (每日08:00)
  → 个人助理_V1/scripts/run-ai-daily-report.sh  (统一入口)
    → AI-Insight/scripts/run-ai-daily-report.sh  (实际执行)
      → python3 send_ai_daily.py                 (推送)
```
- 所有定时任务由 `个人助理_V1` 统一管理 plist 和日志
- 项目内的 plist 文件已与 `~/Library/LaunchAgents/` 中的实际加载版本保持一致
- 日志输出到 `个人助理_V1/data/logs/`，项目本地 `scripts/logs/` 作为备用

**注意**: 定时任务只负责**推送**已生成的日报，不负责**生成**。
日报内容需要在 CodeFlicker 中手动触发「跑一下AI日报」生成。

安装定时任务:
```bash
cp scripts/com.codeflicker.ai-daily-report.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.codeflicker.ai-daily-report.plist

cp scripts/com.codeflicker.ai-weekly-report.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.codeflicker.ai-weekly-report.plist
```

## 依赖

```bash
pip install httpx
```

## 目录结构

```
scripts/
├── README.md                              # 本文件
├── kim_client.py                          # KIM API 公共客户端模块
├── .env.template                          # 凭证配置模板
├── .env                                   # 实际凭证 (不入Git)
├── send_ai_daily.py                       # 日报推送 v3.5（支持JSON/MD双数据源）
├── send_ai_weekly.py                      # 周报推送
├── send_deep_research_card.py             # 深度调研推送
├── send_openclaw_card.py                  # OpenClaw推送
├── gen_daily_html.py                      # 日报HTML生成器
├── sync_to_public.py                      # 脱敏同步
├── sync_to_external.py                    # 外部仓库同步
├── fix_deep_research_footers.py           # 底部修复工具
├── fix_json_quotes.py                     # JSON中文引号修复
├── deploy_daily.sh                        # 日报部署脚本
├── update_tracking.py                     # 追踪体系更新
├── update_tracking_section.py             # 追踪区块更新
├── com.codeflicker.ai-daily-report.plist  # 日报定时任务
├── com.codeflicker.ai-weekly-report.plist # 周报定时任务
├── run-ai-daily-report.sh                 # 日报执行脚本
├── run-ai-weekly-report.sh                # 周报执行脚本
└── logs/                                  # 运行日志 (不入Git)
```
