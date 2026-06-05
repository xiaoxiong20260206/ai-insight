#!/bin/bash
# ============================================================
# AI日报一键部署脚本 deploy_daily.sh
# ============================================================
# 解决问题: 6处联动更新靠记忆容易遗漏，一个脚本全搞定
# 用法: ./scripts/deploy_daily.sh 2026-03-09
# ============================================================

set -euo pipefail

DATE="${1:?用法: $0 <YYYY-MM-DD> [--historical]}"
MONTH=$(echo "$DATE" | cut -d- -f1-2)
DAY=$(echo "$DATE" | cut -d- -f3 | sed 's/^0//')
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 从 config.py 动态读取外部仓库名称（SSoT，根治硬编码 — 经验#73）
EXTERNAL_REPO_NAME=$(python3 -c "import sys; sys.path.insert(0,'$PROJECT_DIR/scripts'); from config import EXTERNAL_REPO_NAME; print(EXTERNAL_REPO_NAME)" 2>/dev/null || echo "ai-insight-public")

# --historical 旗标：补跑历史日报时设置，自动豁免"6处联动首页指向"检查
# 因为首页应永远指向最新日报，而非历史日报，质量门对历史日报的此项检查是设计误判
HISTORICAL=0
for arg in "$@"; do
    if [ "$arg" = "--historical" ]; then
        HISTORICAL=1
    fi
done

echo "🚀 AI日报一键部署: $DATE$([ $HISTORICAL -eq 1 ] && echo ' [历史补跑模式]' || true)"
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

# ===== 0c. 内部版首页完整性自检（v9.11修复：脱敏版index.html不含"林克"是正常行为，改用AI洞察特征检查）=====
# v9.11: index.html 是从 public/index.html (脱敏版) 同步来的，不含"林克"是正确行为
# 改为检查"AI洞察"等通用内容标志，而非"林克"
echo ""
echo "🔍 Step 0c: 内部版首页完整性自检"
AI_COUNT=$(grep -c "AI洞察\|AI行业\|日报\|大模型" index.html 2>/dev/null || echo "0")
# 确保 AI_COUNT 是纯整数（去除可能的换行符或空格）
AI_COUNT=$(echo "$AI_COUNT" | tr -d '[:space:]')
if [ "${AI_COUNT:-0}" -eq 0 ] 2>/dev/null; then
    echo "  ❌ [WARNING] 内部版首页index.html内容异常（未找到AI洞察/日报等关键词）"
    echo "     请检查文件是否损坏: head -5 index.html"
    if [ "${SKIP_INDEX_CHECK:-0}" != "1" ] && [ "${FORCE_DEPLOY:-0}" != "1" ]; then
        exit 1
    fi
    echo "     ⚠️ 已跳过首页内容检查，继续部署..."
else
    echo "  ✅ 内部版首页内容正常（AI相关内容: ${AI_COUNT}处）"
fi

# ===== 0b. 质量门检查（阻断式，不通过则禁止部署） =====
echo ""
echo "🔍 Step 0b: 质量门检查（阻断式）"
{ python3 scripts/daily_quality_gate.py "$DATE" 2>&1 || true; } | tee /tmp/gate_result_deploy.txt || true
GATE_RESULT=$(cat /tmp/gate_result_deploy.txt)

# 检查是否通过（只有全部通过或仅有warning级别的失败才放行）
# v2.1修复: 使用 tee+文件读取替代$()子shell，防止shell管道截断
# HARD_FAIL检测: 只匹配具体失败条目，排除末尾总结行"❌ 质量门未通过 (N项失败)"
# v2.2修复: --historical 模式下额外豁免"6处联动"失败（历史日报首页指向最新日期是正确行为）
if echo "$GATE_RESULT" | grep -q "❌ 质量门未通过"; then
    # 排除末尾总结行，只看具体的"^❌ XX: ..."失败条目（排除"可修复"标注的fixable项）
    HARD_FAIL=$(echo "$GATE_RESULT" | grep "^❌" | grep -v "质量门未通过" | grep -v "⚠️" | grep -v "(可修复)" | head -1 || true)
    # --historical 模式：额外豁免"6处联动"失败（首页始终指向最新日报，不应指向历史日报）
    if [ $HISTORICAL -eq 1 ] && [ -n "$HARD_FAIL" ] && echo "$HARD_FAIL" | grep -q "6处联动"; then
        echo "  ⚠️ [历史补跑模式] 豁免 6处联动 检查（首页指向最新日报是正确行为）"
        HARD_FAIL=""
    fi
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
        # v6.2: MD文件缺失时自动尝试从JSON生成（gen_daily_html.py不生成MD）
        if [[ "$f" == *.md ]]; then
            echo "  ⚠️ 缺少MD: $f，尝试自动生成..."
            python3 scripts/gen_md_from_json.py "$DATE" 2>&1
            if [ -f "$f" ]; then
                echo "  ✅ MD文件已自动生成: $f"
            else
                echo "  ❌ 自动生成MD失败，请手动执行: python3 scripts/gen_md_from_json.py $DATE"
                exit 1
            fi
        else
            echo "  ❌ 缺少: $f"
            exit 1
        fi
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
    <p>正在跳转至 <a href="$DATE-v3.html">AI 日报 $DATE (v3.2)</a>...</p>
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
sed -i "s|<div class=\"stat-value\">[0-9]*</div><div class=\"stat-label\">日报|<div class=\"stat-value\">$REPORT_COUNT</div><div class=\"stat-label\">日报|" "$REPORT_INDEX"
# 更新最新日期
sed -i "s|<div class=\"stat-value\">[0-9-]*</div><div class=\"stat-label\">最新|<div class=\"stat-value\">$DATE</div><div class=\"stat-label\">最新|" "$REPORT_INDEX"
echo "  ✅ 日报索引已更新 (共${REPORT_COUNT}篇)"

# ===== 4. 更新主页 index.html =====
echo ""
echo "📋 Step 3: 更新首页（日历+最新日报描述）"

# 4a. 更新日历数组
# v2.1修复: 通过环境变量传参（AI_MONTH/AI_DAY/AI_DATE），避免 << 'PYEOF' 单引号 heredoc
# 中 shell 变量不展开导致字面量 '$MONTH': [$DAY] 被写入 index.html 的 bug（经验#63）
if ! grep -qE "'$MONTH':.*\b$DAY\b" index.html; then
    AI_MONTH="$MONTH" AI_DAY="$DAY" AI_DATE="$DATE" python3 - << 'PYEOF'
import re, sys, os
month_str = os.environ['AI_MONTH']   # e.g. "2026-03"
day_str   = os.environ['AI_DAY']     # e.g. "31"
date_str  = os.environ['AI_DATE']    # e.g. "2026-03-31"
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
# 在当月数组末尾追加日期（若当月数组已存在）
pattern = r"('" + re.escape(month_str) + r"': \[)([^\]]+)(\])"
if re.search(pattern, content):
    def add_day(m):
        existing = m.group(2).strip().rstrip(',')
        return m.group(1) + existing + ', ' + day_str + m.group(3)
    new_content = re.sub(pattern, add_day, content)
else:
    # 新月第一天：在上一个月数组后插入新月条目
    if re.search(r"'" + re.escape(month_str) + r"'", content):
        print('  ⚠️  当月数组已存在但未匹配，请手动检查')
        sys.exit(1)
    # 在 reportsData 第一个月条目前插入新月
    new_content = re.sub(
        r"(const reportsData = \{)\s*\n(\s*')",
        r"\1\n            '" + month_str + r"': [" + day_str + r"],  // " + month_str + r"日报日期 (最新: " + date_str + r")\n\2",
        content
    )
    if new_content == content:
        print('  ❌ 无法自动插入新月日历数组，请手动更新 index.html')
        sys.exit(1)
    print(f'  ✅ 新月 {month_str} 日历数组已创建，第一条日期: {day_str}')
# 同时更新注释中的最新日期
new_content = re.sub(r'最新: \d{4}-\d{2}-\d{2}', '最新: ' + date_str, new_content)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f'  ✅ 日历数据已添加 {day_str}，注释已更新为 {date_str}')
PYEOF
else
    echo "  ⏭️ 日历数据已包含 $DAY"
fi

# 4a-guard. 防退化检查：确认 currentMonth 使用动态 todayMonth，而非硬编码数字
# 经验#62 (2026-04-02): currentMonth 曾被硬编码为 3，月份变更后日历默认停在旧月
if grep -qE "let currentMonth\s*=\s*[0-9]" index.html; then
    echo "  ❌ [ABORT] index.html 中 currentMonth 被硬编码为数字！请改为使用 todayMonth（动态）"
    echo "     错误行: $(grep -n 'let currentMonth' index.html | head -3)"
    if [ "${SKIP_GATE:-0}" != "1" ]; then
        exit 1
    fi
    echo "  ⚠️ SKIP_GATE=1 已设置，跳过此检查..."
else
    echo "  ✅ currentMonth 已动态化（非硬编码）"
fi
# 同时检查是否有未替换的 \$MONTH 模板变量残留（经验#63）
if grep -qE "'\\\\\\$MONTH'" index.html 2>/dev/null || grep -q "'\$MONTH'" index.html 2>/dev/null; then
    echo "  ❌ [ABORT] index.html 中存在未替换的 '\$MONTH' 模板变量！"
    if [ "${SKIP_GATE:-0}" != "1" ]; then
        exit 1
    fi
else
    echo "  ✅ 无未替换的 \$MONTH 模板变量残留"
fi

# 4b. 更新最新日报的 list-item 链接+标题+描述
# 从JSON提取描述（取heat_trend.summary前100字，或overview[0].headline的前N个用·拼接）
DESC=$(python3 - << PYEOF
import json, re
try:
    with open('data/daily-content-$DATE.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    ht = data.get('heat_trend', {})
    
    # 兼容多种heat_trend格式提取描述
    # 格式1: ht.summary (旧版)
    # 格式2: ht.top_items[].title (05-11格式)
    # 格式3: ht.trend_summary + ht.top_keywords (05-15格式)
    # 格式4: ht.topics[].name (cron早期格式)
    
    summary = ht.get('summary', '') or ht.get('trend_summary', '')
    top_items = ht.get('top_items', []) or ht.get('topics', [])
    
    # 截取前100字，去除HTML标签
    summary = re.sub(r'<[^>]+>', '', summary)
    
    # 从overviews提取headline
    overviews = data.get('overview', [])
    parts = []
    for ov in overviews[:4]:
        hl = ov.get('headline', '')
        if hl:
            clean = re.sub(r'<[^>]+>', '', hl)[:20]
            parts.append(clean)
    
    # 如果overviews没内容，从top_items提取
    if not parts and top_items:
        for item in top_items[:4]:
            name = item.get('name', '') or item.get('title', '')
            if name:
                clean = re.sub(r'<[^>]+>', '', name)[:20]
                parts.append(clean)
    desc = ' · '.join(parts) if parts else summary[:80]
    print(desc)
except Exception as e:
    print('今日AI行业动态汇总')
PYEOF
)

AI_DATE="$DATE" AI_MONTH="$MONTH" AI_DESC="$DESC" python3 - << 'PYEOF'
import re, os
date_str = os.environ['AI_DATE']
month_str = os.environ['AI_MONTH']
desc = os.environ['AI_DESC']

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新 list-item href
content = re.sub(
    r'href="01-daily-reports/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}\.html"(\s+target="_blank"\s+class="list-item")',
    f'href="01-daily-reports/{month_str}/{date_str}.html"\\1',
    content
)
# 更新 list-item-title 日期（从DATE变量解析中文格式）
from datetime import datetime
d = datetime.strptime(date_str, '%Y-%m-%d')
date_cn = f'{d.year}年{d.month}月{d.day}日'
content = re.sub(
    r'\d{4}年\d{1,2}月\d{1,2}日( AI日报)',
    date_cn + r'\1',
    content
)
# 更新 list-item-desc
content = re.sub(
    r'(<div class="list-item-desc">)[^<]*(</div>)',
    lambda m: m.group(1) + desc + m.group(2),
    content
)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('  ✅ 首页最新日报卡片已更新')
PYEOF

# 4c. 验证首页关键字段
echo "  📋 验证首页："
grep -o "list-item-desc\">.[^<]*" index.html | head -1 | cut -c1-80
grep -o "'$MONTH': \[[^\]]*\]" index.html | head -1 || true

# ===== 5. 先同步public版（因为public/index.html需要被commit进去） =====
echo ""
echo "📋 Step 4: 同步公开版（先于commit，确保public/index.html纳入提交）"
python3 scripts/sync_to_public.py --full --force
# 强制敏感词二次核查（不依赖sync_to_public自检）—— 发现残留直接abort，禁止继续推送
# v12.0修复: 敏感词检查只对外部版(ai-insight-public/)执行
# public/ 是内部版，包含"林克"是正确行为（经验#114: public/是内部站Pages部署源）
# 外部版脱敏由 sync_to_external.py 完成，这里做二次核查
EXTERNAL_REPO_DIR="${PROJECT_DIR}/../ai-insight-public"
if [ -d "$EXTERNAL_REPO_DIR" ]; then
    SENSITIVE_COUNT=$( (grep -rl --include="*.html" --include="*.md" --include="*.json" --include="*.js" --include="*.txt" -E "沈浪|林克|快手|Kuaishou|CodeFlicker|KATE|天策|天玑|KwaiBI|小无相功|shenlang|MyFlicker|myflicker|AI分身|让我负责|link-avatar|docs\.corp\.kuaishou" "$EXTERNAL_REPO_DIR/" 2>/dev/null || true) | wc -l | tr -d ' ')
    if [ "$SENSITIVE_COUNT" -gt 0 ]; then
        echo "  ❌ [ABORT] 外部版(ai-insight-public/)有 ${SENSITIVE_COUNT} 个文件含敏感词，禁止推送！"
        grep -rl --include="*.html" --include="*.md" --include="*.json" -E "沈浪|林克|shenlang|MyFlicker" "$EXTERNAL_REPO_DIR/" | head -5
        exit 1
    else
        echo "  ✅ 外部版敏感词验证通过（0处残留）"
    fi
else
    echo "  ⚠️ 外部版仓库目录不存在($EXTERNAL_REPO_DIR)，跳过敏感词检查"
fi

# ===== 6. Git提交+推送（包含public/index.html） =====
echo ""
echo "📋 Step 5: Git提交推送（含public目录）"
git add -A
if git diff --cached --quiet; then
    echo "  ⏭️ 无变更需要提交"
else
    git commit -m "feat: AI日报 $DATE 部署（自动化）"
    echo "  ⏳ 推送到GitHub（通常需 20-60s，超时上限120s）..."
    PUSH_START=$SECONDS
    # macOS 无内置 timeout 命令，用 python3 实现超时控制
    # v9.8修复: 捕获 TimeoutExpired 并 kill 子进程，防止僵尸 git push 进程占用连接
    if python3 -c "
import subprocess, sys
try:
    r = subprocess.run(['git','push','origin','main'], timeout=120)
    sys.exit(r.returncode)
except subprocess.TimeoutExpired as e:
    if e.process:
        e.process.kill()
        e.process.wait()
    print('git push timeout after 120s', file=sys.stderr)
    sys.exit(124)
" 2>&1; then
        echo "  ✅ 已推送到GitHub (耗时$((SECONDS - PUSH_START))s，含public/index.html)"
    else
        echo "  ❌ git push 超时或失败（超过120s），请检查网络后手动 git push"
        exit 1
    fi
fi

# ===== 7. 同步外部版（ai-insight-public） =====
# ⭐ 修复(2026-04-03经验): SKIP_GATE=1 不应跳过外部同步！
# SKIP_GATE 仅用于绕过质量门，外部版同步始终需要执行。
# 旧逻辑误将 SKIP_GATE=1 等同于"由orchestrator调用，跳过外部同步"，
# 导致每次强制部署后 ai-insight-public 不更新。
# ⭐ 修复(2026-04-07经验#70): 加前置 git 仓库健康检查，失败立即阻断（不静默跳过）
echo ""
echo "📋 Step 6: 同步外部版（ai-insight-public）"
if [ "${SKIP_EXTERNAL:-0}" = "1" ]; then
    echo "  ⏭️ SKIP_EXTERNAL=1，跳过外部版同步（由调用方明确控制）"
else
    # 前置健康检查：确认 ai-insight-public 是有效 git 仓库
    EXTERNAL_REPO_DIR="$(dirname "$PROJECT_DIR")/$EXTERNAL_REPO_NAME"
    if [ ! -d "$EXTERNAL_REPO_DIR/.git" ]; then
        echo "  ❌ [ABORT] 外部仓库 .git 目录不存在: $EXTERNAL_REPO_DIR/.git"
        echo "     部署已阻断，请先修复外部仓库。"
        exit 1
    fi
    # 检查 .git 是否完整（HEAD 文件必须存在，否则是空壳）
    if [ ! -f "$EXTERNAL_REPO_DIR/.git/HEAD" ] || [ ! -f "$EXTERNAL_REPO_DIR/.git/config" ]; then
        echo "  ❌ [ABORT] 外部仓库 .git 目录损坏（缺少 HEAD 或 config）"
        # 自动检查是否有 .git_disabled 备份
        if [ -f "$EXTERNAL_REPO_DIR/.git_disabled/HEAD" ]; then
            echo "  🔧 发现 .git_disabled 备份，正在自动恢复..."
            rm -rf "$EXTERNAL_REPO_DIR/.git"
            mv "$EXTERNAL_REPO_DIR/.git_disabled" "$EXTERNAL_REPO_DIR/.git"
            echo "  ✅ .git 已从 .git_disabled 恢复，继续同步..."
        else
            echo "     未找到 .git_disabled 备份，请手动修复或重新克隆："
            echo "     git clone https://github.com/xiaoxiong20260206/$EXTERNAL_REPO_NAME.git $EXTERNAL_REPO_DIR"
            exit 1
        fi
    fi
    # 用 git rev-parse 做终态验证
    if ! git -C "$EXTERNAL_REPO_DIR" rev-parse --git-dir > /dev/null 2>&1; then
        echo "  ❌ [ABORT] 外部仓库 git 状态异常（rev-parse 失败），部署已阻断"
        exit 1
    fi
    echo "  ✅ 外部仓库 git 健康检查通过"
    echo "---"
    # 执行同步，捕获退出码，失败时阻断（而非静默继续）
    if ! python3 scripts/sync_to_external.py --full --verify; then
        echo ""
        echo "  ❌ [ABORT] 外部版同步失败！部署已阻断，请修复后重试。"
        echo "     手动修复：python3 scripts/sync_to_external.py --full --verify"
        exit 1
    fi
fi

# ===== 8. 验证 =====
echo ""
echo "📋 Step 7: 部署验证"
echo "  内部日报(v3):  $(wc -l < "01-daily-reports/$MONTH/$DATE-v3.html" | tr -d ' ') 行"
echo "  明日关注:  $(grep -c '值得关注' "01-daily-reports/$MONTH/$DATE-v3.html") 个板块标题"
echo "  明日内容:  $(grep -o '• [^<]*' "01-daily-reports/$MONTH/$DATE-v3.html" | wc -l | tr -d ' ') 条条目"
echo "  public敏感词: ${SENSITIVE_COUNT} 处"
echo "  内部首页日历:  $(grep -o "'$MONTH': \[[^\]]*\]" index.html | head -1)"

# 验证 public/ 内部日报是否存在（经验#56：手动sync漏force导致旧版本残留）
DEPLOY_FAIL=0
if [ -f "public/01-daily-reports/$MONTH/$DATE.html" ]; then
    echo "  外部日报(public):  $(wc -l < "public/01-daily-reports/$MONTH/$DATE.html" | tr -d ' ') 行"
else
    echo "  ❌ 外部日报(public): 文件不存在！public/01-daily-reports/$MONTH/$DATE.html 未生成"
    DEPLOY_FAIL=1
fi

# 验证外部仓库是否存在该日期日报（⭐ v2.0: 从 warn 升级为硬性阻断）
if [ "${SKIP_EXTERNAL:-0}" != "1" ]; then
    EXTERNAL_REPO_DIR="$(dirname "$PROJECT_DIR")/ai-insight-public"
    if [ -d "$EXTERNAL_REPO_DIR/01-daily-reports/$MONTH" ]; then
        if [ -f "$EXTERNAL_REPO_DIR/01-daily-reports/$MONTH/$DATE.html" ]; then
            echo "  外部仓库日报:  $(wc -l < "$EXTERNAL_REPO_DIR/01-daily-reports/$MONTH/$DATE.html" | tr -d ' ') 行"
        else
            echo "  ❌ [VERIFY FAIL] 外部仓库日报文件不存在: $DATE.html"
            echo "     这意味着外部同步虽然执行了，但文件未正确写入外部仓库！"
            DEPLOY_FAIL=1
        fi
    else
        echo "  ❌ [VERIFY FAIL] 外部仓库目录不存在: $EXTERNAL_REPO_DIR/01-daily-reports/$MONTH"
        DEPLOY_FAIL=1
    fi
fi

echo ""
echo "=================================================="
if [ "$DEPLOY_FAIL" -eq 0 ]; then
    echo "✅ 部署完成！"
    echo "  📄 日报: https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/$MONTH/$DATE.html"
    echo "  🏠 首页: https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/"
else
    echo "❌ 部署验证失败！请查看上方的 ❌ 条目并手动修复。"
    echo "   外部同步手动补跑: python3 scripts/sync_to_external.py --full --verify"
    exit 1
fi

# ===== 9. 部署到 frontend-cloud =====
echo ""
echo "📋 Step 8: 部署内部首页到 frontend-cloud"
if [ "${SKIP_FRONTEND_CLOUD:-0}" != "1" ]; then
    cd "$PROJECT_DIR/public"
    if npx -y --registry https://npm.corp.kuaishou.com @codeflicker/frontend-cloud-cli@latest deploy 2>&1; then
        echo "  ✅ 内部首页已部署到 frontend-cloud"
    else
        echo "  ❌ frontend-cloud 部署失败！内部版URL将指向过期内容或404。"
        echo "     MixCard按钮链接的是 frontend-cloud 内部版URL，部署失败=用户无法查看日报。"
        echo "     修复方法：cd public && npx @codeflicker/frontend-cloud-cli@latest deploy"
        DEPLOY_FAIL=1
    fi
    cd "$PROJECT_DIR"
else
    echo "  ⏭️ SKIP_FRONTEND_CLOUD=1，跳过 frontend-cloud 部署"
fi
echo ""
