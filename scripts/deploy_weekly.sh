#!/bin/bash
# ============================================================
# AI周报一键部署脚本 deploy_weekly.sh
# ============================================================
# 基于日报 deploy_daily.sh 框架，适配周报全链路
# 用法: ./scripts/deploy_weekly.sh 2026-W26
# ============================================================

set -euo pipefail

WEEK="${1:?用法: $0 <YYYY-WXX>}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 从 config.py 读取
EXTERNAL_REPO_NAME=$(python3 -c "import sys; sys.path.insert(0,'$PROJECT_DIR/scripts'); from config import EXTERNAL_REPO_NAME; print(EXTERNAL_REPO_NAME)" 2>/dev/null || echo "ai-insight-public")

echo "🚀 AI周报一键部署: $WEEK"
echo "=================================================="

# ===== Step 0: 前置验证 =====
echo ""
echo "🔍 Step 0a: JSON 数据验证"
JSON_FILE="data/weekly-content-${WEEK}.json"
if [ ! -f "$JSON_FILE" ]; then
    echo "❌ JSON文件不存在: $JSON_FILE"
    exit 1
fi
echo "✅ JSON文件存在: $JSON_FILE ($(wc -c < "$JSON_FILE") bytes)"

# Step 0b: JSON schema 验证
echo ""
echo "🔍 Step 0b: JSON Schema 验证"
uv run scripts/validate_weekly_json.py "$WEEK" 2>&1 || {
    echo "❌ JSON Schema验证失败 — 阻断部署"
    exit 1
}

# ===== Step 1: 生成HTML =====
echo ""
echo "📝 Step 1: 生成周报HTML"
uv run scripts/gen_weekly_html.py --date "$WEEK" 2>&1 | tail -3

# 检查HTML文件
HTML_FILE="01-daily-reports/2026-06/weekly-${WEEK}.html"
if [ ! -f "$HTML_FILE" ]; then
    echo "❌ HTML文件未生成"
    exit 1
fi
HTML_SIZE=$(wc -c < "$HTML_FILE")
echo "✅ HTML已生成: $HTML_FILE ($HTML_SIZE bytes)"
if [ "$HTML_SIZE" -lt 50000 ]; then
    echo "❌ HTML太小（<50KB），可能内容缺失"
    exit 1
fi

# ===== Step 2: HTML 展示验证 =====
echo ""
echo "🔍 Step 2: HTML 展示完整性验证"
uv run scripts/validate_weekly_html.py "$WEEK" 2>&1 || {
    echo "❌ HTML展示验证失败 — 阻断部署"
    exit 1
}

# ===== Step 3: 首页更新 =====
echo ""
echo "📝 Step 3: 首页更新"
uv run scripts/update_homepage.py --type weekly "$WEEK" 2>&1 | tail -3

# ===== Step 4: 同步到 public/ =====
echo ""
echo "📝 Step 4: 同步到 public/"
cp -f "$HTML_FILE" "public/$HTML_FILE" 2>/dev/null || true
# 首页也同步
cp -f index.html public/index.html 2>/dev/null || true
echo "✅ public/ 已同步"

# ===== Step 5: 外部版同步 =====
echo ""
echo "📝 Step 5: 外部版同步 + 脱敏"
uv run scripts/sync_to_external.py --verify 2>&1 | tail -5

# 外部版敏感词检查
echo ""
echo "🔍 Step 5b: 外部版敏感词检查"
EXT_FILE="../$EXTERNAL_REPO_NAME/01-daily-reports/2026-06/weekly-${WEEK}.html"
if [ -f "$EXT_FILE" ]; then
    for word in 林克 沈浪 AI分身 MyFlicker corp.kuaishou; do
        cnt=$(grep -c "$word" "$EXT_FILE" 2>/dev/null || echo 0)
        if [ "$cnt" -gt 0 ]; then
            echo "❌ 外部版敏感词: $word × $cnt"
            exit 1
        fi
    done
    echo "✅ 零敏感词"
else
    echo "⚠️ 外部版文件不存在: $EXT_FILE"
fi

# ===== Step 6: 内部版部署 =====
echo ""
echo "📝 Step 6: 内部版 frontend-cloud 部署"
cd public
npm_config_registry=https://npm.corp.kuaishou.com/ npx -y @codeflicker/frontend-cloud-cli@latest deploy 2>&1 | tail -3
cd "$PROJECT_DIR"

# ===== Step 7: 首页完整性验证 =====
echo ""
echo "🔍 Step 7: 首页完整性验证"
uv run scripts/verify_homepage.py 2>&1 | tail -5

echo ""
echo "=================================================="
echo "✅ AI周报部署完成: $WEEK"
echo "🔗 内部版: https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/2026-06/weekly-${WEEK}.html"
echo "🔗 外部版: https://xiaoxiong20260206.github.io/$EXTERNAL_REPO_NAME/01-daily-reports/2026-06/weekly-${WEEK}.html"
