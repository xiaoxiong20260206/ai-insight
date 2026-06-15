#!/usr/bin/env python3
"""
W24周报视觉精修 v4
P1: overview等高 + NEWS tag跟板块色
P2: 词汇表卡片化
P3: 宏观叙事callout三色 + header摘要
"""
import re, shutil

BASE = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight'
HTML_PATH = f'{BASE}/01-daily-reports/2026-06/weekly-2026-W24.html'
PUBLIC_PATH = f'{BASE}/public/01-daily-reports/2026-06/weekly-2026-W24.html'

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

fixes = []

# ============================================================
# P1-A: Overview 5格等高 + 内容clamp防止溢出
# ============================================================
OVERVIEW_ITEM_CSS_OLD = """.overview-item {
            padding: 18px 16px; border-radius: var(--radius-md);
            border: 1px solid var(--color-border-light); background: var(--color-bg);
            transition: all var(--transition-normal); min-width: 0; overflow: hidden;
        }"""

OVERVIEW_ITEM_CSS_NEW = """.overview-item {
            padding: 18px 16px; border-radius: var(--radius-md);
            border: 1px solid var(--color-border-light); background: var(--color-bg);
            transition: all var(--transition-normal); min-width: 0; overflow: hidden;
            display: flex; flex-direction: column;
        }
        .overview-item-text { flex: 1; }"""

html = html.replace(OVERVIEW_ITEM_CSS_OLD, OVERVIEW_ITEM_CSS_NEW)
fixes.append("✅ overview-item flex column（等高布局）")

# overview-item-text 加 line-clamp（显示最多4行，不溢出）
CLAMP_CSS = """
.overview-item-text {
    display: -webkit-box;
    -webkit-line-clamp: 6;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
"""
html = html.replace('</style>\n</head>', CLAMP_CSS + '</style>\n</head>')
fixes.append("✅ overview-item-text 6行clamp防溢出")

# ============================================================
# P1-B: NEWS tag 跟随板块色（通过CSS变量继承）
# ============================================================
# 在board-accent的section里，.tag-new应该用board-accent色
NEWS_TAG_CSS = """
section[style*="--board-accent"] .tag-new {
    background: color-mix(in srgb, var(--board-accent) 12%, white);
    color: var(--board-accent);
    border: 1px solid color-mix(in srgb, var(--board-accent) 25%, white);
}
"""
html = html.replace('</style>\n</head>', NEWS_TAG_CSS + '</style>\n</head>')
fixes.append("✅ NEWS tag跟随board-accent色")

# ============================================================
# P2: 词汇表 table → 卡片grid
# ============================================================
# 找vocab section的table，改为卡片布局
vocab_sec = re.search(r'<section id="vocab">(.*?)</section>', html, re.DOTALL)
if vocab_sec:
    content = vocab_sec.group(1)
    # 提取table行
    rows = re.findall(
        r'<tr><td[^>]*><strong>(.*?)</strong></td><td[^>]*>(.*?)</td><td[^>]*><a href="([^"]+)"[^>]*>(.*?)</a></td></tr>',
        content, re.DOTALL
    )
    if not rows:
        # 尝试没有链接的格式
        rows_nlink = re.findall(
            r'<tr><td[^>]*><strong>(.*?)</strong></td><td[^>]*>(.*?)</td><td[^>]*>(.*?)</td></tr>',
            content, re.DOTALL
        )
        rows = [(term, definition, '', source) for term, definition, source in rows_nlink]

    if rows:
        VOCAB_COLORS = ['purple','info','success','warning','danger','purple','info','success']
        cards_html = '<div class="vocab-grid">'
        for i, row in enumerate(rows):
            term, definition = row[0], row[1]
            source_url = row[2] if len(row) > 2 else ''
            source_text = row[3] if len(row) > 3 else row[2] if len(row) > 2 else ''
            # 清理HTML标签
            term_clean = re.sub(r'<[^>]+>', '', term).strip()
            def_clean = re.sub(r'<[^>]+>', '', definition).strip()
            source_clean = re.sub(r'<[^>]+>', '', source_text).strip()
            color = VOCAB_COLORS[i % len(VOCAB_COLORS)]
            source_link = f'<a href="{source_url}" class="meta-link" target="_blank">{source_clean}</a>' if source_url and source_url != '#' else f'<span style="color:var(--color-text-muted)">{source_clean}</span>'
            
            cards_html += f'''
  <div class="vocab-card animate-on-scroll">
    <div class="vocab-term vocab-{color}">{term_clean}</div>
    <div class="vocab-def">{def_clean}</div>
    <div class="vocab-source">{source_link}</div>
  </div>'''
        cards_html += '\n</div>'

        # 找h2标题
        h2_m = re.search(r'(<h2[^>]*>.*?</h2>)', content, re.DOTALL)
        h2_html = h2_m.group(1) if h2_m else '<h2 class="animate-on-scroll">技术词汇表</h2>'
        chap_m = re.search(r'(<div class="doc-chapter-label[^"]*"[^>]*>.*?</div>)', content, re.DOTALL)
        chap_html = chap_m.group(1) if chap_m else ''

        new_vocab = f'''<section id="vocab">
{chap_html}
{h2_html}
{cards_html}
</section>'''
        html = html[:vocab_sec.start()] + new_vocab + html[vocab_sec.end():]
        fixes.append(f"✅ 词汇表 table → 卡片grid（{len(rows)}个词条）")
    else:
        fixes.append("⚠️ 词汇表行提取失败，保持原样")

# 追加vocab卡片CSS
VOCAB_CSS = """
/* ===== 词汇表卡片 ===== */
.vocab-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 14px;
    margin-top: 12px;
}
.vocab-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border-light);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    box-shadow: var(--shadow-xs);
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: all var(--transition-fast);
}
.vocab-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-card); }
.vocab-term {
    font-size: 14px; font-weight: 700;
    display: inline-flex; padding: 4px 10px;
    border-radius: var(--radius-full);
    width: fit-content;
}
.vocab-purple { background: rgba(124,58,237,0.1); color: var(--color-purple); }
.vocab-info   { background: rgba(37,99,235,0.1);  color: var(--color-info); }
.vocab-success{ background: rgba(5,150,105,0.1);  color: var(--color-success); }
.vocab-warning{ background: rgba(217,119,6,0.1);  color: var(--color-warning); }
.vocab-danger { background: rgba(225,29,72,0.1);  color: var(--color-danger); }
.vocab-def {
    font-size: 13px; color: #44403C; line-height: 1.65;
    flex: 1;
}
.vocab-source {
    font-size: 12px; color: var(--color-text-muted);
    padding-top: 8px; border-top: 1px solid var(--color-border-light);
}
@media (max-width: 768px) { .vocab-grid { grid-template-columns: 1fr; } }
"""
html = html.replace('</style>\n</head>', VOCAB_CSS + '</style>\n</head>')

# ============================================================
# P3-A: 宏观叙事callout三色（第1个purple，第2个warning，第3个info）
# ============================================================
narrative_sec = re.search(r'<section id="narrative">(.*?)</section>', html, re.DOTALL)
if narrative_sec:
    content = narrative_sec.group(1)
    # 替换3个callout的颜色（当前都是callout-info/callout-success）
    callouts = list(re.finditer(r'class="callout (callout-\w+)', content))
    if len(callouts) >= 3:
        target_classes = ['callout-purple', 'callout-warning', 'callout-info']
        new_content = content
        for i, m in enumerate(callouts[:3]):
            old_cls = m.group(1)
            new_cls = target_classes[i]
            new_content = new_content.replace(f'class="callout {old_cls}', f'class="callout {new_cls}', 1)
        html = html[:narrative_sec.start()] + f'<section id="narrative">{new_content}</section>' + html[narrative_sec.end():]
        fixes.append("✅ 宏观叙事callout三色（purple/warning/info）")

# ============================================================
# P3-B: Header加摘要句
# ============================================================
old_header_meta = '<p class="header-meta">'
if old_header_meta in html:
    # 在header-meta后加摘要句
    pass  # header已经有meta，不重复添加

# 给header-title加副标题
OLD_TITLE_LINE = '<h1 class="header-title animate-on-scroll">AI 周报 2026年第24周</h1>'
NEW_TITLE_BLOCK = '''<h1 class="header-title animate-on-scroll">AI 周报 2026年第24周</h1>
<p class="header-subtitle animate-on-scroll" style="font-size:15px;color:var(--color-text-secondary);margin-top:4px;margin-bottom:0;line-height:1.6;max-width:600px;">基建竞赛全面启动：谷歌+DeepSeek千亿押注算力 · Fable/Mythos开启安全分层新纪元 · 豆包付费宣告免费时代终结</p>'''
html = html.replace(OLD_TITLE_LINE, NEW_TITLE_BLOCK)
fixes.append("✅ Header加副标题摘要句")

# ============================================================
# P3-C: board-section摘要callout背景跟accent色
# ============================================================
# 当前callout-info背景是蓝色，5个板块都一样
# 改为跟board-accent色联动
CALLOUT_ACCENT_CSS = """
section[style*="--board-accent"] .callout {
    background: color-mix(in srgb, var(--board-accent) 6%, white);
    border-color: var(--board-accent);
    color: #44403C;
}
"""
html = html.replace('</style>\n</head>', CALLOUT_ACCENT_CSS + '</style>\n</head>')
fixes.append("✅ 板块摘要callout跟随board-accent色")

# ============================================================
# 写入
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
