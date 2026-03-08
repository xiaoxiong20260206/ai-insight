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
| `send_ai_daily.py` | AI日报推送到KIM群 | `python3 scripts/send_ai_daily.py [日期] [--dry-run]` |
| `send_ai_weekly.py` | AI周报推送到KIM | `python3 scripts/send_ai_weekly.py --to-user shenlang` |
| `send_deep_research_card.py` | 深度调研专题推送 | `python3 scripts/send_deep_research_card.py --to-user shenlang` |
| `send_openclaw_card.py` | OpenClaw深度洞察推送 | `python3 scripts/send_openclaw_card.py --to-user shenlang` |
| `send_ai_daily_enhanced_preview.py` | 日报v3.4增强预览 (一次性) | `python3 scripts/send_ai_daily_enhanced_preview.py preview` |

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
├── send_ai_daily.py                       # 日报推送
├── send_ai_daily_enhanced_preview.py      # 日报v3.4增强预览
├── send_ai_weekly.py                      # 周报推送
├── send_deep_research_card.py             # 深度调研推送
├── send_openclaw_card.py                  # OpenClaw推送
├── sync_to_public.py                      # 脱敏同步
├── sync_to_external.py                    # 外部仓库同步
├── fix_deep_research_footers.py           # 底部修复工具
├── com.codeflicker.ai-daily-report.plist  # 日报定时任务
├── com.codeflicker.ai-weekly-report.plist # 周报定时任务
├── run-ai-daily-report.sh                 # 日报执行脚本
├── run-ai-weekly-report.sh                # 周报执行脚本
└── logs/                                  # 运行日志 (不入Git)
```
