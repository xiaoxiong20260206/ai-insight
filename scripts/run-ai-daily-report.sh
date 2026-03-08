#!/bin/bash
# AI日报定时执行脚本
# 由 launchd 在每日 08:00 触发
# 配置文件: com.codeflicker.ai-daily-report.plist

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$SCRIPT_DIR/logs/daily-report-$(date +%Y-%m-%d).log"

# 确保日志目录存在
mkdir -p "$SCRIPT_DIR/logs"

echo "========================================" >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI日报定时任务启动" >> "$LOG_FILE" 2>&1

# 激活 Python 环境（如有 venv）
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# 执行日报推送
cd "$PROJECT_DIR"
python3 scripts/send_ai_daily.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI日报定时任务完成" >> "$LOG_FILE" 2>&1
echo "========================================" >> "$LOG_FILE" 2>&1
