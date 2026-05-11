#!/usr/bin/env bash
# daily_agent_runner.sh — AI日报 Subagent 编排脚本 (v1.0)
#
# 用途：在主会话中调用，依次编排三个 Subagent 完成 AI 日报
#       Step 1（搜索）→ Step 2（内容生成）→ Step 3-4（部署验证）
#
# 注意：此脚本本身不直接执行 Subagent，而是作为主会话 Agent 的
#       执行指南。主会话 Agent 应按照此脚本的逻辑依次调用
#       use_subagent 工具。
#
# 用法（主会话执行逻辑）：
#   1. DATE=$(date +%Y-%m-%d)  # 或指定日期
#   2. 清理旧 flag
#   3. use_subagent("daily-search-agent", task="执行AI日报搜索, DATE={DATE}")
#   4. 检查 step1-completed.flag
#   5. use_subagent("daily-content-agent", task="执行AI日报内容生成, DATE={DATE}")
#   6. 检查 step2-completed.flag
#   7. use_subagent("daily-deploy-agent", task="执行AI日报部署验证, DATE={DATE}")
#   8. 检查 deployment-completed.flag
#   9. 主会话执行 Step 5: python3 scripts/build_insight_mixcard.py daily --date {DATE} --output /tmp/card.json --with-summary
#
# 直接执行此脚本（调试/日志用途）：
#   bash scripts/daily_agent_runner.sh [YYYY-MM-DD]

set -uo pipefail

# ==================== 配置 ====================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
FLAGS_DIR="${BASE_DIR}/data/flags"

# 颜色
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

# ==================== 参数处理 ====================

if [ $# -lt 1 ]; then
    DATE=$(date +%Y-%m-%d)
else
    DATE="$1"
fi

echo -e "\n${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║  AI日报 Subagent 编排器  DATE=${DATE}  ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${RESET}\n"

# ==================== 辅助函数 ====================

log_step() {
    echo -e "\n${BOLD}${CYAN}▶ $1${RESET}"
}

check_flag() {
    local flag_file="$1"
    local step_name="$2"
    
    if [ -f "${FLAGS_DIR}/${flag_file}" ]; then
        TIMESTAMP=$(head -1 "${FLAGS_DIR}/${flag_file}" 2>/dev/null || echo "")
        DETAIL=$(tail -1 "${FLAGS_DIR}/${flag_file}" 2>/dev/null || echo "")
        echo -e "  ${GREEN}✅${RESET} ${step_name} 已完成: ${TIMESTAMP}"
        echo -e "     ${DETAIL}"
        return 0
    fi
    
    # 检查失败 flag
    local failed_flag="${flag_file/completed/failed}"
    if [ -f "${FLAGS_DIR}/${failed_flag}" ]; then
        echo -e "  ${RED}❌${RESET} ${step_name} 已失败:"
        cat "${FLAGS_DIR}/${failed_flag}" | sed 's/^/     /'
        return 2
    fi
    
    echo -e "  ${YELLOW}⏳${RESET} ${step_name} 尚未完成（flag 不存在）"
    return 1
}

# ==================== Step 0: 清理旧 flag ====================

log_step "Step 0: 清理旧 flag"
mkdir -p "${FLAGS_DIR}"
OLD_FLAGS=(
    "${FLAGS_DIR}/step1-completed.flag"
    "${FLAGS_DIR}/step1-failed.flag"
    "${FLAGS_DIR}/step2-completed.flag"
    "${FLAGS_DIR}/step2-failed.flag"
    "${FLAGS_DIR}/deployment-completed.flag"
    "${FLAGS_DIR}/deployment-failed.flag"
)
REMOVED=0
for f in "${OLD_FLAGS[@]}"; do
    if [ -f "$f" ]; then
        # 检查是否是今日的 flag
        FLAG_DATE=$(head -1 "$f" 2>/dev/null | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}" | head -1 || echo "")
        if [ "$FLAG_DATE" != "$DATE" ]; then
            rm -f "$f"
            REMOVED=$((REMOVED + 1))
        fi
    fi
done
echo -e "  ${GREEN}✅${RESET} 清理了 ${REMOVED} 个旧 flag（今日: ${DATE}）"

# ==================== 状态检查（主会话调用前查看） ====================

log_step "当前 flag 状态"
check_flag "step1-completed.flag" "Step 1 搜索" || true
check_flag "step2-completed.flag" "Step 2 内容生成" || true
check_flag "deployment-completed.flag" "Step 3-4 部署" || true

# ==================== 打印 Subagent 调用指南 ====================

echo -e "\n${BOLD}══════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}主会话执行顺序（依次调用 use_subagent 工具）：${RESET}"
echo -e "${BOLD}══════════════════════════════════════════════════${RESET}\n"

echo -e "${CYAN}【Step 1】调用 Subagent A - 搜索调研${RESET}"
echo -e "  use_subagent("
echo -e "    subagent_name=\"daily-search-agent\","
echo -e "    task=\"执行AI日报搜索调研, DATE=${DATE}\","
echo -e "    reason=\"AI日报 Step 0.5+1: 热点探针+两层搜索\""
echo -e "  )"
echo -e "  → 等待完成，确认 step1-completed.flag 存在\n"

echo -e "${CYAN}【Step 2】调用 Subagent B - 内容生成${RESET}"
echo -e "  use_subagent("
echo -e "    subagent_name=\"daily-content-agent\","
echo -e "    task=\"执行AI日报内容生成, DATE=${DATE}\","
echo -e "    reason=\"AI日报 Step 2: 冷启动schema验证+JSON生成\""
echo -e "  )"
echo -e "  → 等待完成，确认 step2-completed.flag 存在\n"

echo -e "${CYAN}【Step 3-4】调用 Subagent C - 部署验证${RESET}"
echo -e "  use_subagent("
echo -e "    subagent_name=\"daily-deploy-agent\","
echo -e "    task=\"执行AI日报HTML生成和部署验证, DATE=${DATE}\","
echo -e "    reason=\"AI日报 Step 3-4: HTML生成+6处联动+4位置验证\""
echo -e "  )"
echo -e "  → 等待完成，确认 deployment-completed.flag 存在\n"

echo -e "${CYAN}【Step 5】主会话执行（禁止委托给 Subagent）${RESET}"
echo -e "  python3 scripts/build_insight_mixcard.py daily --date ${DATE} --output /tmp/card.json --with-summary"
echo -e "  → 输出四链接（私发 KIM + 四链接自检）\n"

echo -e "${BOLD}══════════════════════════════════════════════════${RESET}"
echo -e "${YELLOW}⚠️  Step 5 必须由主会话执行，禁止委托给任何 Subagent${RESET}"
echo -e "${YELLOW}⚠️  三个 Subagent 之间有依赖，必须顺序执行（不可并行）${RESET}"
echo -e "${BOLD}══════════════════════════════════════════════════${RESET}\n"

# ==================== 快速状态摘要 ====================

log_step "当前进度摘要"

S1=0; S2=0; S3=0
check_flag "step1-completed.flag" "Step 1" > /dev/null 2>&1 && S1=1 || true
check_flag "step2-completed.flag" "Step 2" > /dev/null 2>&1 && S2=1 || true
check_flag "deployment-completed.flag" "Step 3-4" > /dev/null 2>&1 && S3=1 || true

[ $S1 -eq 1 ] && echo -e "  ${GREEN}✅${RESET} Step 1 搜索: 完成" || echo -e "  ${YELLOW}⏳${RESET} Step 1 搜索: 待执行"
[ $S2 -eq 1 ] && echo -e "  ${GREEN}✅${RESET} Step 2 内容: 完成" || echo -e "  ${YELLOW}⏳${RESET} Step 2 内容: 待执行"
[ $S3 -eq 1 ] && echo -e "  ${GREEN}✅${RESET} Step 3-4 部署: 完成" || echo -e "  ${YELLOW}⏳${RESET} Step 3-4 部署: 待执行"

TOTAL=$((S1 + S2 + S3))
if [ $TOTAL -eq 3 ]; then
    echo -e "\n  ${GREEN}${BOLD}✅ 三个 Subagent 全部完成！可执行 Step 5。${RESET}"
else
    echo -e "\n  ${CYAN}进度: ${TOTAL}/3 步完成${RESET}"
fi
