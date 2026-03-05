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

## 🔄 sync_to_public.py - 双版本同步脚本

将内部版日报同步到公开版本（public目录），自动移除敏感信息。

### 使用方式

```bash
# 同步今天的日报
python scripts/sync_to_public.py

# 同步指定日期
python scripts/sync_to_public.py 2026-03-05

# 同步所有日报
python scripts/sync_to_public.py --all

# 强制覆盖已存在的文件
python scripts/sync_to_public.py --all --force

# 同时同步首页
python scripts/sync_to_public.py --with-index
```

### 脱敏规则

- 移除"林克"、"沈浪"等个人标识
- 替换内部话术为中性表达
- 保持内容和样式一致

## 📁 目录结构

```
scripts/
├── README.md              # 本文件
├── send_ai_daily.py       # AI日报推送脚本 (内部KIM群)
├── send_deep_research_card.py  # 深度调研推送
└── sync_to_public.py      # 双版本同步脚本 (NEW)
```

## 🔮 计划中

- [ ] 周报推送脚本
- [ ] 定时任务配置
- [ ] 推送历史记录
- [x] 双版本同步脚本
