#!/usr/bin/env bash
# verify_4positions.sh — AI日报部署完成条件强制验证 (v1.0)
#
# 用途：Subagent C (daily-deploy-agent) 完成部署后必须调用，
#       验证四个位置全部正确更新后才写 completed.flag。
#       任何一个位置不通过 → 输出修复指令 → exit 1（不写 flag）
#
# 解决问题：
#   - E7: 部署日志含 [ABORT] 但末尾显示 ✅，确认偏误导致外部版未 push
#
# 用法：
#   bash scripts/verify_4positions.sh YYYY-MM-DD
#   echo $?   # 0=全通过, 1=有失败
#
# 输出格式：
#   ✅ [1] 内部版日报: 已存在, 1234 行
#   ✅ [2] 内部版首页: 含 "林克" 字样 (出现 5 次)
#   ✅ [3] 外部版日报: 已存在, 890 行
#   ✅ [4] 外部版首页: 含日期 YYYY-MM-DD 引用 (3 处)
#   ✅ [5] 外部仓库 Git: HEAD commit 含日期 YYYY-MM-DD
#   ════════════════════════════════════════
#   ✅ 4位置验证通过！可以写 completed.flag

set -uo pipefail

# ==================== 配置 ====================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
# 从 config.py 动态读取外部仓库名称（SSoT，根治硬编码 — 经验#73）
EXTERNAL_REPO_NAME=$(python3 -c "import sys; sys.path.insert(0,'$SCRIPT_DIR'); from config import EXTERNAL_REPO_NAME; print(EXTERNAL_REPO_NAME)" 2>/dev/null || echo "ai-insight-public")
EXTERNAL_REPO="$(dirname "$BASE_DIR")/$EXTERNAL_REPO_NAME"
INTERNAL_REPO="$BASE_DIR"

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
    echo -e "${YELLOW}⚠️  未指定日期，使用今日: ${DATE}${RESET}"
else
    DATE="$1"
fi

# 从日期提取 YYYY-MM
MONTH="${DATE:0:7}"

echo -e "\n${BOLD}${CYAN}═══ AI日报四位置验证: ${DATE} ═══${RESET}\n"

FAILURES=0
FIXES=""

ok() { echo -e "  ${GREEN}✅${RESET} ${1}"; }
fail() {
    echo -e "  ${RED}❌${RESET} ${1}"
    FAILURES=$((FAILURES + 1))
    FIXES="${FIXES}\n  🔧 ${2}"
}
warn() { echo -e "  ${YELLOW}⚠️${RESET}  ${1}"; }

# ==================== 1. 内部版日报 ====================

echo -e "${BOLD}[1] 内部版日报${RESET}"
INTERNAL_REPORT="${INTERNAL_REPO}/01-daily-reports/${MONTH}/${DATE}-v3.html"
if [ -f "$INTERNAL_REPORT" ]; then
    LINE_COUNT=$(wc -l < "$INTERNAL_REPORT" | tr -d ' ')
    if [ "$LINE_COUNT" -gt 50 ]; then
        ok "内部版日报存在: ${INTERNAL_REPORT##*/}，${LINE_COUNT} 行"
    else
        fail "内部版日报行数太少: ${LINE_COUNT} 行（可能生成失败）" \
             "重新运行: python3 scripts/gen_daily_html.py ${DATE}"
    fi
else
    fail "内部版日报不存在: ${INTERNAL_REPORT}" \
         "运行: python3 scripts/gen_daily_html.py ${DATE}"
fi

# ==================== 2. 内部版首页 ====================

echo -e "\n${BOLD}[2] 内部版首页${RESET}"
INTERNAL_INDEX="${INTERNAL_REPO}/index.html"
if [ -f "$INTERNAL_INDEX" ]; then
    DATE_COUNT=$(grep -c "${DATE}" "$INTERNAL_INDEX" 2>/dev/null || echo "0")
    LINK_COUNT=$(grep -c "${DATE}-v3.html\|${DATE}.html" "$INTERNAL_INDEX" 2>/dev/null || echo "0")
    if [ "$DATE_COUNT" -gt 0 ]; then
        ok "内部版首页含日期 ${DATE} (出现 ${DATE_COUNT} 次，含链接 ${LINK_COUNT} 处)"
    else
        fail "内部版首页未包含日期 ${DATE}（6处联动漏更新首页日历）" \
             "运行: python3 scripts/ai_daily_orchestrator.py finalize --fix --date ${DATE}"
    fi
else
    fail "内部版首页不存在: ${INTERNAL_INDEX}" \
         "检查仓库根目录是否有 index.html"
fi

# ==================== 3. 外部版日报 ====================

echo -e "\n${BOLD}[3] 外部版日报${RESET}"
EXTERNAL_REPORT="${EXTERNAL_REPO}/01-daily-reports/${MONTH}/${DATE}.html"
if [ -d "$EXTERNAL_REPO" ]; then
    if [ -f "$EXTERNAL_REPORT" ]; then
        EXT_LINE_COUNT=$(wc -l < "$EXTERNAL_REPORT" | tr -d ' ')
        if [ "$EXT_LINE_COUNT" -gt 50 ]; then
            ok "外部版日报存在: ${EXTERNAL_REPORT##*/}，${EXT_LINE_COUNT} 行"
        else
            fail "外部版日报行数太少: ${EXT_LINE_COUNT} 行（可能脱敏未执行）" \
                 "运行: python3 scripts/sync_to_external.py --full --verify"
        fi
    else
        fail "外部版日报不存在: ${EXTERNAL_REPORT}" \
             "运行: python3 scripts/sync_to_external.py --full --verify"
    fi
else
    fail "外部仓库不存在: ${EXTERNAL_REPO}" \
         "克隆仓库: git clone <external-repo-url> ${EXTERNAL_REPO}"
fi

# ==================== 4. 外部版首页 ====================

echo -e "\n${BOLD}[4] 外部版首页${RESET}"
EXTERNAL_INDEX="${EXTERNAL_REPO}/index.html"
if [ -d "$EXTERNAL_REPO" ] && [ -f "$EXTERNAL_INDEX" ]; then
    EXT_DATE_COUNT=$(grep -c "${DATE}" "$EXTERNAL_INDEX" 2>/dev/null || echo "0")
    if [ "$EXT_DATE_COUNT" -gt 0 ]; then
        ok "外部版首页含日期 ${DATE} (出现 ${EXT_DATE_COUNT} 次)"
    else
        fail "外部版首页未包含日期 ${DATE}（外部版首页未同步）" \
             "运行: python3 scripts/sync_to_external.py --full --verify"
    fi
else
    if [ ! -d "$EXTERNAL_REPO" ]; then
        : # 已在位置3报错
    else
        fail "外部版首页不存在: ${EXTERNAL_INDEX}" \
             "运行: python3 scripts/sync_to_external.py --full --verify"
    fi
fi

# ==================== 5. 外部仓库 Git push 验证 ====================

echo -e "\n${BOLD}[5] 外部仓库 Git Commit 验证${RESET}"
if [ -d "${EXTERNAL_REPO}/.git" ]; then
    # 检查 HEAD commit message 是否包含日期
    HEAD_MSG=$(cd "$EXTERNAL_REPO" && git log -1 --format="%s" 2>/dev/null || echo "")
    HEAD_TIME=$(cd "$EXTERNAL_REPO" && git log -1 --format="%ar" 2>/dev/null || echo "")
    
    if echo "$HEAD_MSG" | grep -q "$DATE"; then
        ok "外部仓库 HEAD commit 含 ${DATE}: \"${HEAD_MSG}\" (${HEAD_TIME})"
    else
        # 更宽泛检查：最近 3 次 commit 内是否有今日相关
        RECENT_COMMITS=$(cd "$EXTERNAL_REPO" && git log -3 --format="%s" 2>/dev/null || echo "")
        if echo "$RECENT_COMMITS" | grep -q "$DATE"; then
            ok "外部仓库近期 commit 含 ${DATE} (HEAD: \"${HEAD_MSG}\", ${HEAD_TIME})"
        else
            fail "外部仓库最近 commit 未包含日期 ${DATE}（可能本地已同步但未 push）" \
                 "运行: cd ${EXTERNAL_REPO} && git add -A && git commit -m 'feat: AI日报 ${DATE}' && git push origin main"
        fi
    fi

    # 额外检查：本地是否有未 push 的 commit
    UNPUSHED=$(cd "$EXTERNAL_REPO" && git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNPUSHED" -gt 0 ]; then
        fail "外部仓库有 ${UNPUSHED} 个本地 commit 未 push（E7 根因！）" \
             "运行: cd ${EXTERNAL_REPO} && git push origin main"
    else
        ok "外部仓库无未 push 的 commit ✓"
    fi
elif [ -d "$EXTERNAL_REPO" ]; then
    warn "外部仓库存在但未初始化 git（${EXTERNAL_REPO}）"
    FAILURES=$((FAILURES + 1))
    FIXES="${FIXES}\n  🔧 初始化: cd ${EXTERNAL_REPO} && git init && git remote add origin <url>"
fi

# ==================== 汇总 ====================

echo -e "\n${BOLD}══════════════════════════════════════════════════${RESET}"

if [ "$FAILURES" -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✅ 4位置验证通过！所有部署位置正确更新。${RESET}"
    echo -e "${CYAN}可以写 completed.flag 并在主会话执行 Step 5。${RESET}\n"
    exit 0
else
    echo -e "\n${RED}${BOLD}❌ 验证失败：${FAILURES} 个问题${RESET}"
    echo -e "\n${YELLOW}${BOLD}修复清单：${RESET}"
    echo -e "$FIXES"
    echo -e "\n${YELLOW}修复后重新运行本脚本验证：${RESET}"
    echo -e "  bash scripts/verify_4positions.sh ${DATE}\n"
    echo -e "${RED}⛔ 不写 completed.flag，禁止进入 Step 5${RESET}\n"
    exit 1
fi
