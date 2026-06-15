#!/usr/bin/env python3
"""
W24周报视觉问题修复 v2
基于清爽调研报告v3.2.0规范 + 日报实际效果对照
"""
import re, shutil, os

BASE = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight'
HTML_PATH = f'{BASE}/01-daily-reports/2026-06/weekly-2026-W24.html'
PUBLIC_PATH = f'{BASE}/public/01-daily-reports/2026-06/weekly-2026-W24.html'

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

fixes = []

# ============================================================
# FIX 1: Header渐变标题 + 精致badge
# ============================================================
# 当前header-title没有渐变效果（纯色），日报用的是gradient-hero
old_header_title_css = '.header-title {\n    font-size: 34px;\n    font-weight: 800;\n    line-height: 1.3;\n    margin-bottom: 12px;\n    letter-spacing: -0.02em;\n    background: var(--gradient-hero);\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    background-clip: text;\n}'

# 检查当前header-title CSS
ht_idx = html.find('.header-title')
if ht_idx > 0:
    ht_end = html.find('}', ht_idx) + 1
    current = html[ht_idx:ht_end]
    if '-webkit-background-clip' in current and 'gradient-hero' in current:
        fixes.append("✅ header-title渐变已有")
    else:
        # 替换为渐变版
        new_css = """.header-title {
    font-size: 34px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}"""
        html = html[:ht_idx] + new_css + html[ht_end:]
        fixes.append("✅ header-title → 渐变文字")

# ============================================================
# FIX 2: deep-focus-label和title的opacity提升（白色文字在渐变背景上偏淡）
# ============================================================
html = html.replace(
    'opacity: .85;',
    'opacity: 1;'
)
fixes.append("✅ deep-focus-label opacity 0.85 → 1.0")

# ============================================================
# FIX 3: deep-focus-header内inline style的color:#fff → 确保可读性
# （检查渐变背景对比度——purple/info/success色值上的白字对比度）
# purple #7C3AED vs #fff → ~4.5:1 (刚好AA)
# info #2563EB vs #fff → ~4.6:1 (刚好AA)
# success #059669 vs #fff → ~4.6:1 (刚好AA)
# 但CC后缀(80%透明度)会降低对比度！
# 修复：去掉CC后缀，用100%不透明渐变
# ============================================================
html = html.replace(
    'var(--color-purple)CC 100%',
    'var(--color-purple) 100%'
)
html = html.replace(
    'var(--color-info)CC 100%',
    'var(--color-info) 100%'
)
html = html.replace(
    'var(--color-success)CC 100%',
    'var(--color-success) 100%'
)
fixes.append("✅ deep-focus-header渐变去掉CC后缀(80%→100%不透明，提升白字对比度)")

# ============================================================
# FIX 4: overview-item emoji icon → SVG icon（清爽规范禁止emoji做UI图标）
# ============================================================
SVG_ICONS = {
    '🧠': '<svg class="overview-item-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-purple)" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    '💻': '<svg class="overview-item-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-info)" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    '📱': '<svg class="overview-item-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
    '🏭': '<svg class="overview-item-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M2 20h20V8l-5 4V8l-5 4V4H2z"/></svg>',
    '🔄': '<svg class="overview-item-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>',
}

for emoji, svg in SVG_ICONS.items():
    html = html.replace(
        f'<span class="overview-item-icon">{emoji}</span>',
        f'<span class="overview-item-icon">{svg}</span>'
    )
fixes.append("✅ overview-item emoji → SVG icon（5个）")

# ============================================================
# FIX 5: 五大板块标题的emoji → SVG
# ============================================================
BOARD_SVG_MAP = {
    '🧠': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-purple)" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    '💻': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-info)" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    '📱': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
    '🏭': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M2 20h20V8l-5 4V8l-5 4V4H2z"/></svg>',
    '🔄': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>',
}

for emoji, svg in BOARD_SVG_MAP.items():
    html = html.replace(
        f'<span style="font-size:18px;">{emoji}</span>',
        svg
    )
fixes.append("✅ 五大板块标题 emoji → SVG")

# ============================================================
# FIX 6: doc-chapter-label增强（添加左侧色条，提升视觉层级）
# ============================================================
html = html.replace(
    '.doc-chapter-label {',
    '.doc-chapter-label { position: relative; padding-left: 14px;'
)
# 在doc-chapter-label::after之前添加::before
html = html.replace(
    '.doc-chapter-label::after {',
    '.doc-chapter-label::before { content: ""; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 16px; background: var(--gradient-hero); border-radius: 2px; }\n        .doc-chapter-label::after {'
)
fixes.append("✅ doc-chapter-label 添加左侧渐变色条")

# ============================================================
# FIX 7: overview-item增强视觉效果
# - label颜色多样化（5个板块5种色）
# - 添加hover上浮效果
# - 增加icon-svg的CSS
# ============================================================
# 追加overview-item-svg CSS到WEEKLY_EXTRA_CSS段末
extra_css = """
/* ===== overview SVG icon ===== */
.overview-item-svg { vertical-align: middle; }
.overview-item { transition: all .25s cubic-bezier(.4,0,.2,1); }
.overview-item:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(5,150,105,0.1); border-color: var(--color-success-light); }
"""

# 在</style>之前追加
html = html.replace('</style>\n</head>', extra_css + '</style>\n</head>')
fixes.append("✅ overview-item SVG icon CSS + hover上浮")

# ============================================================
# FIX 8: overview-item-label 多色（按板块）
# 当前5个overview-item-label都继承绿色，需要按板块不同色
# ============================================================
# 第1个大模型→purple, 第2个AI Coding→info, 第3个AI应用→warning, 第4个AI行业→success, 第5个企业→danger
label_colors = ['purple', 'info', 'warning', 'success', 'danger']
color_vars = {
    'purple': 'var(--color-purple)',
    'info': 'var(--color-info)',
    'warning': 'var(--color-warning)',
    'success': 'var(--color-success)',
    'danger': 'var(--color-danger)',
}

# 逐个替换overview-item-label
overview_items = list(re.finditer(r'<span class="overview-item-label">(.*?)</span>', html))
for i, m in enumerate(overview_items[:5]):
    color_name = label_colors[i % len(label_colors)]
    color_val = color_vars[color_name]
    old = m.group(0)
    new = f'<span class="overview-item-label" style="color:{color_val};">{m.group(1)}</span>'
    html = html.replace(old, new, 1)
fixes.append("✅ overview-item-label 5色语义区分")

# ============================================================
# FIX 9: header-badge渐变效果增强
# ============================================================
# 当前header-badge可能是plain，改为渐变背景
hb_idx = html.find('.header-badge {')
if hb_idx > 0:
    hb_end = html.find('}', hb_idx) + 1
    current_hb = html[hb_idx:hb_end]
    if 'gradient-badge' not in current_hb or 'border' not in current_hb:
        new_hb = """.header-badge {
    display: inline-flex;
    align-items: center;
    background: var(--gradient-badge);
    color: var(--color-success);
    padding: var(--spacing-xs) 12px;
    border-radius: var(--radius-full);
    font-size: var(--caption);
    font-weight: 500;
    letter-spacing: 0.02em;
    margin-bottom: 12px;
    border: 1px solid rgba(5,150,105,0.12);
    box-shadow: var(--shadow-xs);
}"""
        html = html[:hb_idx] + new_hb + html[hb_end:]
        fixes.append("✅ header-badge渐变+边框+阴影")

# ============================================================
# FIX 10: Top5 news-card 颜色区分增强（5个card分别用5种accent色）
# ============================================================
# 当前Top5可能都继承success色左边框，改为rank对应色
RANK_COLORS = {
    '1': 'var(--color-danger)',
    '2': 'var(--color-purple)',
    '3': 'var(--color-info)',
    '4': 'var(--color-warning)',
    '5': 'var(--color-success)',
}

top5_cards = list(re.finditer(r'class="news-card animate-on-scroll"', html))
for i, m in enumerate(top5_cards[:5]):
    rank = str(i + 1)
    color = RANK_COLORS[rank]
    old = m.group(0)
    new = f'class="news-card animate-on-scroll" style="--card-accent:{color};border-left-color:{color};"'
    html = html.replace(old, new, 1)
fixes.append("✅ Top5 news-card 5色左边框区分（红>紫>蓝>橙>绿）")

# 对应的rank badge和judgment-label也改色
for i, m in enumerate(list(re.finditer(r'class="news-card-rank">TOP (\d+)', html))[:5]):
    rank = m.group(1)
    color = RANK_COLORS.get(rank, 'var(--color-success)')
    # 改rank badge背景色
    pass  # rank badge的色已由CSS控制，通过--card-accent覆盖

# ============================================================
# FIX 11: 日报索引区域视觉增强
# ============================================================
# 当前daily-item是flat列表，增加连接线感觉和日期强调
di_css = """
/* ===== 日报索引时间线 ===== */
.daily-index { position: relative; padding-left: 24px; }
.daily-index::before { content: ""; position: absolute; left: 8px; top: 12px; bottom: 12px; width: 2px; background: linear-gradient(to bottom, var(--color-success), var(--color-info)); border-radius: 1px; }
.daily-item { position: relative; padding-left: 20px; }
.daily-item::before { content: ""; position: absolute; left: -20px; top: 50%; transform: translateY(-50%); width: 8px; height: 8px; background: var(--color-success); border-radius: 50%; border: 2px solid var(--color-bg-card); }
.daily-item:nth-child(even)::before { background: var(--color-info); }
"""

html = html.replace('</style>\n</head>', di_css + '</style>\n</head>')
fixes.append("✅ 日报索引时间线样式（竖线+圆点）")

# ============================================================
# 写入 + 同步
# ============================================================
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy(HTML_PATH, PUBLIC_PATH)

size = len(html.encode())
print(f"\n文件大小: {size:,} bytes")
print(f"\n修复清单:")
for f in fixes:
    print(f"  {f}")

# 合规检查
issues = []
if '{{' in html: issues.append("模板变量")
if 'href=""' in html: issues.append("空href")
print(f"\n合规: {'✅' if not issues else '❌ ' + str(issues)}")
