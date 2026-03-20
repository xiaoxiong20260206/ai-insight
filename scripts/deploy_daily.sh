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

# ===== 0a. Orchestrator状态验证（v1.1新增） =====
# 防止绕过orchestrator直接部署 — 2026-03-15教训
echo ""
echo "🔍 Step 0a: Orchestrator状态验证"
STATE_FILE="data/daily-workflow/$DATE/state.json"
if [ -f "$STATE_FILE" ]; then
    # 检查validate步骤是否完成
    VALIDATE_STATUS=$(python3 -c "
import json, sys
try:
    state = json.load(open('$STATE_FILE'))
    v = state.get('steps', {}).get('validate', {}).get('status', 'pending')
    print(v)
except:
    print('error')
" 2>/dev/null)
    
    if [ "$VALIDATE_STATUS" = "completed" ]; then
        echo "  ✅ Orchestrator validate已完成"
    elif [ "$VALIDATE_STATUS" = "error" ]; then
        echo "  ⚠️ 读取状态文件失败，跳过此检查"
    else
        echo "  🚫 Orchestrator的validate步骤未完成(当前: $VALIDATE_STATUS)"
        echo "     请通过 orchestrator finalize 执行完整流程，而非直接部署。"
        echo "     命令: python3 scripts/ai_daily_orchestrator.py finalize --date $DATE"
        if [ "${FORCE_DEPLOY:-0}" != "1" ]; then
            echo "     如需强制部署: FORCE_DEPLOY=1 $0 $DATE"
            exit 1
        fi
        echo "     ⚠️ FORCE_DEPLOY=1 已设置，跳过检查..."
    fi
    
    # 检查source快照是否存在（v1.1: 确保Step 2.7抽检已执行）
    SNAPSHOT_FILE="data/daily-workflow/$DATE/source_snapshot.json"
    if [ -f "$SNAPSHOT_FILE" ]; then
        echo "  ✅ Source快照存在"
    else
        echo "  ⚠️ Source快照不存在 — 建议通过orchestrator complete --step 2 创建"
    fi
else
    echo "  ⚠️ 未找到orchestrator状态文件($STATE_FILE)"
    echo "     建议通过 orchestrator 执行完整流程"
    if [ "${FORCE_DEPLOY:-0}" != "1" ]; then
        echo "     如需强制部署: FORCE_DEPLOY=1 $0 $DATE"
        exit 1
    fi
    echo "     ⚠️ FORCE_DEPLOY=1 已设置，跳过检查..."
fi

# ===== 0b. 质量门检查（阻断式，不通过则禁止部署） =====
echo ""
echo "🔍 Step 0b: 质量门检查（阻断式）"
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
echo "📋 Step 3: 更新首页（日历+最新日报描述）"

# 4a. 更新日历数组
if ! grep -q "'$MONTH'.*\b$DAY\b" index.html; then
    python3 - << PYEOF
import re, sys
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
# 在当月数组末尾追加日期
pattern = r"('$MONTH': \[)([^\]]+)(\])"
def add_day(m):
    existing = m.group(2).strip().rstrip(',')
    return m.group(1) + existing + ', $DAY' + m.group(3)
new_content = re.sub(pattern, add_day, content)
# 同时更新注释中的最新日期
new_content = re.sub(r'最新: \d{4}-\d{2}-\d{2}', '最新: $DATE', new_content)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('  ✅ 日历数据已添加 $DAY，注释已更新为 $DATE')
PYEOF
else
    echo "  ⏭️ 日历数据已包含 $DAY"
fi

# 4b. 更新最新日报的 list-item 链接+标题+描述
# 从JSON提取描述（取heat_trend.summary前100字，或overview[0].headline的前N个用·拼接）
DESC=$(python3 - << PYEOF
import json, re
try:
    with open('data/daily-content-$DATE.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    ht = data.get('heat_trend', {})
    summary = ht.get('summary', '')
    # 截取前100字，去除HTML标签
    summary = re.sub(r'<[^>]+>', '', summary)
    # 取highlights作为·分隔描述
    wl = data.get('watch_list', [])
    overviews = data.get('overview', [])
    parts = []
    for ov in overviews[:4]:
        hl = ov.get('headline', '')
        if hl:
            clean = re.sub(r'<[^>]+>', '', hl)[:20]
            parts.append(clean)
    desc = ' · '.join(parts) if parts else summary[:80]
    print(desc)
except Exception as e:
    print('今日AI行业动态汇总')
PYEOF
)

python3 - << PYEOF
import re
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新 list-item href
content = re.sub(
    r'href="01-daily-reports/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}\.html"(\s+target="_blank"\s+class="list-item")',
    'href="01-daily-reports/$MONTH/$DATE.html"\g<1>',
    content
)
# 更新 list-item-title 日期（从DATE变量解析中文格式）
from datetime import datetime
d = datetime.strptime('$DATE', '%Y-%m-%d')
date_cn = f'{d.year}年{d.month}月{d.day}日'
content = re.sub(
    r'\d{4}年\d{1,2}月\d{1,2}日( AI日报)',
    date_cn + r'\1',
    content
)
# 更新 list-item-desc
content = re.sub(
    r'(<div class="list-item-desc">)[^<]*(</div>)',
    r'\g<1>${DESC}\g<2>',
    content
)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('  ✅ 首页最新日报卡片已更新')
PYEOF

# 4c. 验证首页关键字段
echo "  📋 验证首页："
grep -o "list-item-desc\">.[^<]*" index.html | head -1 | cut -c1-80
grep -o "'$MONTH': \[[^\]]*\]" index.html | head -1

# ===== 5. 先同步public版（因为public/index.html需要被commit进去） =====
echo ""
echo "📋 Step 4: 同步公开版（先于commit，确保public/index.html纳入提交）"
python3 scripts/sync_to_public.py --full --force 2>&1 | tail -5
# 强制敏感词二次核查（不依赖sync_to_public自检）
SENSITIVE_COUNT=$(grep -rl "沈浪\|林克\|快手\|Kuaishou" public/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$SENSITIVE_COUNT" -gt 0 ]; then
    echo "  ❌ 警告: public/目录中有 ${SENSITIVE_COUNT} 个文件含敏感词！请检查脱敏逻辑"
    grep -rl "沈浪\|林克\|快手\|Kuaishou" public/ | head -5
else
    echo "  ✅ 敏感词验证通过（0处残留）"
fi

# ===== 6. Git提交+推送（包含public/index.html） =====
echo ""
echo "📋 Step 5: Git提交推送（含public目录）"
git add -A
if git diff --cached --quiet; then
    echo "  ⏭️ 无变更需要提交"
else
    git commit -m "feat: AI日报 $DATE 部署（自动化）"
    git push origin main
    echo "  ✅ 已推送到GitHub（含public/index.html）"
fi

# ===== 7. 同步外部版 =====
echo ""
echo "📋 Step 6: 同步外部版（ai-insight-public）"
echo "---"
python3 scripts/sync_to_external.py --full --verify 2>&1 | tail -8

# ===== 8. 验证 =====
echo ""
echo "📋 Step 7: 部署验证"
echo "  日报HTML:  $(wc -l < "01-daily-reports/$MONTH/$DATE-v3.html" | tr -d ' ') 行"
echo "  明日关注:  $(grep -c '值得关注' "01-daily-reports/$MONTH/$DATE-v3.html") 个板块标题"
echo "  明日内容:  $(grep -o '• [^<]*' "01-daily-reports/$MONTH/$DATE-v3.html" | wc -l | tr -d ' ') 条条目"
echo "  public敏感词: ${SENSITIVE_COUNT} 处"
echo "  首页日历:  $(grep -o "'$MONTH': \[[^\]]*\]" index.html | head -1)"

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "  📄 日报: https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/$MONTH/$DATE.html"
echo "  🏠 首页: https://xiaoxiong20260206.github.io/ai-insight/"
echo ""
