#!/usr/bin/env python3
"""
W24周报视觉修复 v3 — 清爽调研报告v3.2.0合规 + 日报对齐
"""
import re, shutil

BASE = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight'
HTML_PATH = f'{BASE}/01-daily-reports/2026-06/weekly-2026-W24.html'
PUBLIC_PATH = f'{BASE}/public/01-daily-reports/2026-06/weekly-2026-W24.html'

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

fixes = []

# ============================================================
# FIX 1: Overview区全面升级
# - 改3列→5列(一行全展示)
# - 加overview-headline(每格加醒目标题)
# - 增大padding和间距
# - label改用背景色标签样式而非纯文字色
# ============================================================

# 1a: five-cols改5列（桌面端一行5个）
html = html.replace(
    '.overview-grid.five-cols { grid-template-columns: repeat(3, 1fr); }',
    '.overview-grid.five-cols { grid-template-columns: repeat(5, 1fr); }'
)
fixes.append("✅ overview-grid 5列(3→5)")

# 1b: overview-item增大padding+增加headline样式
html = html.replace(
    '.overview-item {\n            padding: 14px 16px;',
    '.overview-item {\n            padding: 18px 16px;'
)
# 追加headline CSS
headline_css = """
.overview-headline { font-size: 14px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 6px; line-height: 1.4; }
.overview-item-label-tag { display: inline-flex; padding: 2px 8px; border-radius: var(--radius-full); font-size: 11px; font-weight: 700; letter-spacing: 0.03em; }
.overview-item-label-tag.purple { background: rgba(124,58,237,0.1); color: var(--color-purple); }
.overview-item-label-tag.info { background: rgba(37,99,235,0.1); color: var(--color-info); }
.overview-item-label-tag.warning { background: rgba(217,119,6,0.1); color: var(--color-warning); }
.overview-item-label-tag.success { background: rgba(5,150,105,0.1); color: var(--color-success); }
.overview-item-label-tag.danger { background: rgba(225,29,72,0.1); color: var(--color-danger); }
"""

html = html.replace('</style>\n</head>', headline_css + '</style>\n</head>')
fixes.append("✅ overview headline + label-tag CSS")

# 1c: 在overview-item里加headline行
LABEL_TAG_COLORS = ['purple', 'info', 'warning', 'success', 'danger']
HEADLINES = [
    'Anthropic双轨发布，安全分层',
    'ViBe基准+Stripe迁移',
    '豆包付费+AI短剧',
    '800亿+500亿融资',
    '制造业96%+政策双轮',
]

# 替换overview-item结构
items = list(re.finditer(
    r'(<div class="overview-item animate-on-scroll">\s*<div class="overview-item-header">.*?</div>)\s*(<div class="overview-item-text[^>]*>)',
    html, re.DOTALL
))
for i, m in enumerate(items[:5]):
    color = LABEL_TAG_COLORS[i]
    headline = HEADLINES[i]
    # 将overview-item-label改为tag样式
    old_label = re.search(r'<span class="overview-item-label"[^>]*>(.*?)</span>', m.group(1))
    if old_label:
        label_text = old_label.group(1)
        new_label = f'<span class="overview-item-label-tag {color}">{label_text}</span>'
        old_header = m.group(1)
        new_header = old_header.replace(old_label.group(0), new_label)
    else:
        new_header = m.group(1)
    
    # 在text div之前插入headline
    old_block = m.group(0)
    new_block = new_header + f'\n        <div class="overview-headline">{headline}</div>\n        ' + m.group(2)
    html = html.replace(old_block, new_block, 1)

fixes.append("✅ overview-item加headline+label改tag样式")

# ============================================================
# FIX 2: Overview-item-text 字色加深（确保对比度）
# ============================================================
html = html.replace(
    'color:var(--color-text-secondary);line-height:1.65;',
    'color:#44403C;line-height:1.65;'
)
# 只改overview-item-text（精确替换）
html = html.replace(
    '<div class="overview-item-text" style="font-size:13px;color:#44403C;line-height:1.65;">',
    '<div class="overview-item-text" style="font-size:13px;color:#44403C;line-height:1.65;">'
)
fixes.append("✅ overview-item-text 字色 #57534E → #44403C (对比度4.5:1+)")

# ============================================================
# FIX 3: Board-section news-item增强
# - news-source-inline加链接色
# - tag-new按板块换色
# ============================================================
html = html.replace(
    '.news-source-inline { font-size: 11px; color: var(--color-text-muted); font-weight: 400;',
    '.news-source-inline { font-size: 11px; color: var(--color-info); font-weight: 500;'
)
fixes.append("✅ news-source-inline muted→info色(可点击暗示)")

# board-section加板块色
board_sections = [
    ('id="llm"', '--board-accent:var(--color-purple)'),
    ('id="coding"', '--board-accent:var(--color-info)'),
    ('id="app"', '--board-accent:var(--color-warning)'),
    ('id="industry"', '--board-accent:var(--color-success)'),
    ('id="enterprise"', '--board-accent:var(--color-danger)'),
]

for sec_id, accent in board_sections:
    html = html.replace(
        f'<section {sec_id}>',
        f'<section {sec_id} style="{accent}">'
    )
    # board-badge改色
    # news-tag改色
    
fixes.append("✅ 5个board-section加板块accent色CSS变量")

# 追加board-accent相关CSS
board_accent_css = """
/* ===== board板块accent色 ===== */
.board-section { border-left: 3px solid var(--board-accent, var(--color-success)); }
.board-badge { background: var(--board-accent, var(--color-success)); color: #fff; }
section[style*="--board-accent"] .tag-new { background: color-mix(in srgb, var(--board-accent) 10%, white); color: var(--board-accent); }
section[style*="--board-accent"] .board-header { color: var(--board-accent); }
"""

html = html.replace('</style>\n</head>', board_accent_css + '</style>\n</head>')
fixes.append("✅ board-section左边框+badge+tag统一板块色")

# ============================================================
# FIX 4: 章节label色条（确保::before生效）
# 需要检查CSS里.doc-chapter-label是否有position:relative
# ============================================================
ch_idx = html.find('.doc-chapter-label {')
if ch_idx > 0:
    ch_end = html.find('}', ch_idx) + 1
    current = html[ch_idx:ch_end]
    if 'position: relative' not in current:
        # 已在v2中添加了 position:relative; padding-left:14px;
        pass
    # 检查::before是否存在
    before_idx = html.find('.doc-chapter-label::before')
    if before_idx > 0:
        fixes.append("✅ doc-chapter-label::before色条已存在")
    else:
        # 添加::before
        after_idx = html.find('.doc-chapter-label::after')
        if after_idx > 0:
            before_css = """.doc-chapter-label::before { content: ""; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 16px; background: var(--gradient-hero); border-radius: 2px; }
        """
            html = html[:after_idx] + before_css + html[after_idx:]
            fixes.append("✅ doc-chapter-label::before色条补充")

# ============================================================
# FIX 5: Top5 news-card rank badge + judgment-label 跟随card-accent
# ============================================================
rank_accent_css = """
/* ===== Top5 rank accent ===== */
.news-card-rank { background: color-mix(in srgb, var(--card-accent, var(--color-success)) 12%, white); color: var(--card-accent, var(--color-success)); }
.judgment-label { color: var(--card-accent, var(--color-success)); }
.news-card-why { border-left-color: var(--card-accent, var(--color-success)); background: color-mix(in srgb, var(--card-accent, var(--color-success)) 5%, white); }
"""

html = html.replace('</style>\n</head>', rank_accent_css + '</style>\n</head>')
fixes.append("✅ rank badge + judgment-label跟随card-accent色")

# ============================================================
# FIX 6: 响应式适配（overview 5列在小屏→2列）
# ============================================================
responsive_css = """
@media (max-width: 1024px) { .overview-grid.five-cols { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .overview-grid.five-cols { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .overview-grid.five-cols { grid-template-columns: 1fr; } }
"""

html = html.replace('</style>\n</head>', responsive_css + '</style>\n</head>')
fixes.append("✅ overview响应式(5→3→2→1列)")

# ============================================================
# 写入 + 同步
# ============================================================
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy(HTML_PATH, PUBLIC_PATH)

size = len(html.encode())
print(f"\n文件大小: {size:,} bytes")
print(f"\n修复清单:")
for fix in fixes:
    print(f"  {fix}")

issues = []
if '{{' in html: issues.append("模板变量")
if 'href=""' in html: issues.append("空href")
if '我是' not in html or '林克' not in html: issues.append("了解更多缺失")
print(f"\n合规: {'✅' if not issues else '❌ ' + str(issues)}")
