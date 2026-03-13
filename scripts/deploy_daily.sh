#!/bin/bash
# ============================================================
# AI日报一键部署脚本 deploy_daily.sh
# ============================================================
# 解决问题: 6处联动更新靠记忆容易遗漏，一个脚本全搞定
# 用法: ./scripts/deploy_daily.sh 2026-03-09
# ============================================================

set -e

DATE="${1:?用法: $0 <YYYY-MM-DD>}"
MONTH=$(echo "$DATE" | cut -d- -f1-2)
DAY=$(echo "$DATE" | cut -d- -f3 | sed 's/^0//')
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 AI日报一键部署: $DATE"
echo "=================================================="

# ===== 0. 质量门检查（阻断式，不通过则禁止部署） =====
echo ""
echo "🔍 Step 0: 质量门检查（阻断式）"
GATE_RESULT=$(python3 scripts/daily_quality_gate.py "$DATE" 2>&1)
echo "$GATE_RESULT"

# 检查是否通过（只有全部通过或仅有warning级别的失败才放行）
if echo "$GATE_RESULT" | grep -q "❌ 质量门未通过"; then
    # 检查是否所有失败项都是warning级别（可放行）
    HARD_FAIL=$(echo "$GATE_RESULT" | grep "^❌" | grep -v "⚠️" | head -1)
    if [ -n "$HARD_FAIL" ]; then
        echo ""
        echo "🚫 质量门硬性失败，部署已阻断。请先修复问题后重试。"
        echo "   如需强制部署: SKIP_GATE=1 $0 $DATE"
        if [ "${SKIP_GATE:-0}" != "1" ]; then
            exit 1
        fi
        echo "   ⚠️ SKIP_GATE=1 已设置，跳过门控继续部署..."
    else
        echo "  ⚠️ 仅有warning级别问题，继续部署..."
    fi
fi
echo "  ✅ 质量门通过"

# ===== 1. 检查文件存在 =====
echo ""
echo "📋 Step 1: 检查必要文件"
REQUIRED_FILES=(
    "01-daily-reports/$MONTH/$DATE-v3.html"
    "01-daily-reports/$MONTH/$DATE.md"
)
for f in "${REQUIRED_FILES[@]}"; do
    if [ -f "$f" ]; then
        echo "  ✅ $f"
    else
        echo "  ❌ 缺少: $f"
        exit 1
    fi
done

# ===== 2. 确保redirect文件存在 =====
REDIRECT="01-daily-reports/$MONTH/$DATE.html"
if [ ! -f "$REDIRECT" ]; then
    echo "  ➕ 创建redirect: $REDIRECT"
    cat > "$REDIRECT" << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AI 日报 - $DATE</title>
    <meta http-equiv="refresh" content="0;url=$DATE-v3.html">
    <style>body{font-family:-apple-system,system-ui,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#F8FAFB;color:#57534E}a{color:#059669}</style>
</head>
<body>
    <p>正在跳转至 <a href="$DATE-v3.html">AI 日报 $DATE (v3.1)</a>...</p>
</body>
</html>
EOF
fi

# ===== 3. 更新01-daily-reports/index.html =====
echo ""
echo "📋 Step 2: 更新日报索引页"
REPORT_INDEX="01-daily-reports/index.html"
# 更新统计数字
REPORT_COUNT=$(ls -1 01-daily-reports/$MONTH/*-v3.html 2>/dev/null | wc -l | tr -d ' ')
sed -i '' "s|<div class=\"stat-value\">[0-9]*</div><div class=\"stat-label\">日报|<div class=\"stat-value\">$REPORT_COUNT</div><div class=\"stat-label\">日报|" "$REPORT_INDEX"
# 更新最新日期
sed -i '' "s|<div class=\"stat-value\">[0-9-]*</div><div class=\"stat-label\">最新|<div class=\"stat-value\">$DATE</div><div class=\"stat-label\">最新|" "$REPORT_INDEX"
echo "  ✅ 日报索引已更新 (共${REPORT_COUNT}篇)"

# ===== 4. 更新主页 index.html =====
echo ""
echo "📋 Step 3: 更新首页"
# 更新日历数据
if ! grep -q "'$MONTH'.*$DAY" index.html; then
    # 日历reportsData中追加日期
    sed -i '' "s|'$MONTH': \[\\([^]]*\\)\]|'$MONTH': [\\1, $DAY]|" index.html
    echo "  ✅ 日历数据已添加 $DAY"
else
    echo "  ⏭️ 日历数据已包含 $DAY"
fi

# ===== 5. Git提交+推送 =====
echo ""
echo "📋 Step 4: Git提交推送"
git add -A
if git diff --cached --quiet; then
    echo "  ⏭️ 无变更需要提交"
else
    git commit -m "feat: AI日报 $DATE 部署（自动化）"
    git push origin main
    echo "  ✅ 已推送到GitHub"
fi

# ===== 6. 同步公开版+外部版 =====
echo ""
echo "📋 Step 5: 同步公开版+外部版"
python3 scripts/sync_to_public.py --full --force 2>&1 | tail -5
echo "---"
python3 scripts/sync_to_external.py 2>&1 | tail -5

# ===== 7. 验证 =====
echo ""
echo "📋 Step 6: 部署验证"
echo "  日报HTML:  $(wc -l < "01-daily-reports/$MONTH/$DATE-v3.html" | tr -d ' ') 行"
echo "  公开版:    $(ls -la "public/01-daily-reports/$MONTH/$DATE.html" 2>/dev/null | awk '{print $5}') bytes"
echo "  首页日历:  $(grep "'$MONTH'" index.html | head -1 | tr -d ' ')"

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "  📄 日报: https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/$MONTH/$DATE.html"
echo "  🏠 首页: https://xiaoxiong20260206.github.io/ai-insight/"
echo ""
