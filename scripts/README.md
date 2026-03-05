# AI-Insight Scripts

此目录包含 AI-Insight 项目的自动化脚本。

## 📤 send_ai_daily.py - AI日报推送脚本

将 AI 日报推送到林克所在的所有 KIM 群。

### 使用方式

```bash
# 推送今天的日报
python scripts/send_ai_daily.py

# 推送指定日期的日报
python scripts/send_ai_daily.py 2026-03-05

# 试运行（不实际发送）
python scripts/send_ai_daily.py --dry-run
python scripts/send_ai_daily.py 2026-03-05 --dry-run
```

### 功能特性

- ✅ **自动读取日报** - 从 `01-daily-reports/{YYYY-MM}/{YYYY-MM-DD}.md` 提取内容
- ✅ **重试机制** - 遇到频率限制(42900)自动重试，最多3次
- ✅ **间隔控制** - 群间发送间隔2.5秒，避免触发频率限制
- ✅ **群名显示** - 正确显示群名而非"未知群"
- ✅ **DRY-RUN模式** - 测试脚本逻辑而不实际发送

### 配置

脚本中已预配置林克应用凭证，无需额外配置即可使用。

### 依赖

```bash
pip install httpx
```

## 📁 目录结构

```
scripts/
├── README.md            # 本文件
└── send_ai_daily.py     # AI日报推送脚本
```

## 🔮 计划中

- [ ] 周报推送脚本
- [ ] 定时任务配置
- [ ] 推送历史记录
