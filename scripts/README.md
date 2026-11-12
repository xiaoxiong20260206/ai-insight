# AI-Insight Scripts

此目录包含 AI-Insight 项目的自动化脚本。

## 配置

KIM OpenAPI 直连推送已废弃并删除。日报/周报推送统一通过 `build_insight_mixcard.py` 生成卡片，再由 Agent 使用当前平台的 message 能力发送。

## 脚本列表

### 📤 推送脚本

| 脚本 | 用途 | 使用方式 |
|------|------|---------|
| `build_insight_mixcard.py` | 统一mixCard生成器(日报/周报/调研/产品) | `python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD` |

### 🔄 同步脚本

| 脚本 | 用途 | 使用方式 |
|------|------|---------|
| `sync_to_public.py` | 内部版→public目录脱敏 | `python3 scripts/sync_to_public.py --all --force` |
| `sync_to_external.py` | public目录→外部仓库同步 | `python3 scripts/sync_to_external.py` |

## 目录结构

```
scripts/
├── README.md                              # 本文件
├── gen_daily_html.py                      # 日报HTML生成器
├── sync_to_public.py                      # 脱敏同步
├── sync_to_external.py                    # 外部仓库同步
├── deploy_daily.sh                        # 日报部署脚本
├── update_tracking.py                     # 追踪体系更新
└── logs/                                  # 运行日志 (不入Git)
```
