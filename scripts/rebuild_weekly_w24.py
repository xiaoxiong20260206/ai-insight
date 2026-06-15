#!/usr/bin/env python3
"""
W24周报视觉重构脚本
- 复用日报的完整CSS（75KB）
- 五大板块：表格→news-item列表
- 周度洞察：insight-card→deep-focus-card
- 林克的洞察：callout→pi-card
- sidebar默认折叠
"""
import re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(BASE, '01-daily-reports/2026-06/2026-06-15-v3.html')
WEEKLY_IN = os.path.join(BASE, '01-daily-reports/2026-06/weekly-2026-W24.html')
WEEKLY_OUT = os.path.join(BASE, '01-daily-reports/2026-06/weekly-2026-W24.html')
PUBLIC_OUT = os.path.join(BASE, 'public/01-daily-reports/2026-06/weekly-2026-W24.html')

# SVG常用图标（从gen_weekly_html.py复用）
CAL_SVG = '<svg class="meta-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="4"/><line x1="8" y1="2" x2="8" y2="4"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
LINK_SVG = '<svg class="meta-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'

print("读取日报CSS...")
with open(DAILY, encoding='utf-8') as f:
    daily_html = f.read()
styles_daily = re.findall(r'<style[^>]*>(.*?)</style>', daily_html, re.DOTALL)
daily_css = styles_daily[1]  # 75KB主CSS

print("读取周报内容...")
with open(WEEKLY_IN, encoding='utf-8') as f:
    weekly_html = f.read()

# =========================================================================
# 提取周报各板块数据
# =========================================================================

def extract_section(html, section_id):
    """提取section内容"""
    start = html.find(f'<section id="{section_id}">')
    if start == -1:
        return ''
    end = html.find('</section>', start) + len('</section>')
    return html[start:end]

# 提取Top5内容（保持原样）
top5_section = extract_section(weekly_html, 'top5')

# 提取周度洞察内容（三条insight-card）
insight_section = extract_section(weekly_html, 'insight')

# 提取林克的洞察（callout段落）
linkinsight_section = extract_section(weekly_html, 'linkinsight')

# 提取日报索引
dailyindex_section = extract_section(weekly_html, 'dailyindex')

# 提取词汇表
vocab_section = extract_section(weekly_html, 'vocab')

# 提取宏观叙事
narrative_section = extract_section(weekly_html, 'narrative')

# 提取概览section
overview_section = extract_section(weekly_html, 'overview')

# 提取了解更多和footer
more_idx = weekly_html.find('<div style="max-width:var(--content-max)')
footer_end = weekly_html.find('</main>')
more_block = weekly_html[more_idx:footer_end] if more_idx > 0 else ''

# 提取五大板块表格数据 -> 转换为news-item列表
def table_to_news_items(section_html):
    """从table提取新闻条目，转为board-section news-item列表"""
    rows = re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td><td><a href="([^"]+)"[^>]*>链接</a></td></tr>', section_html)
    if not rows:
        # 尝试另一种格式
        rows = re.findall(r'<tr><td[^>]*>(.*?)</td><td[^>]*>(.*?)</td><td[^>]*>.*?href="([^"]+)".*?</td></tr>', section_html, re.DOTALL)
    items = []
    for event, source, url in rows:
        event = re.sub(r'<[^>]+>', '', event).strip()
        source = re.sub(r'<[^>]+>', '', source).strip()
        items.append((event, source, url))
    return items

# 提取各板块callout摘要（用于board-header下方的摘要）
def extract_callout_text(section_html):
    m = re.search(r'class="callout callout-\w+ animate-on-scroll">(.*?)</div>', section_html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ''

SECTIONS_INFO = [
    ('llm',       '大模型',     'color-purple',  '🧠', 'llm'),
    ('coding',    'AI Coding',  'color-info',    '💻', 'coding'),
    ('app',       'AI应用',     'color-warning', '📱', 'app'),
    ('industry',  'AI行业',     'color-success', '🏭', 'industry'),
    ('enterprise','企业AI转型', 'color-danger',  '🔄', 'enterprise'),
]

board_sections_html = ''
for sec_id, sec_name, color_var, icon, anchor in SECTIONS_INFO:
    sec_html = extract_section(weekly_html, sec_id)
    summary = extract_callout_text(sec_html)
    items = table_to_news_items(sec_html)
    
    # 提取stats-grid（如果有）
    stats_m = re.search(r'<div class="stats-grid[^"]*">(.*?)</div>\s*</section>', sec_html, re.DOTALL)
    stats_html = f'<div class="stats-grid animate-on-scroll">{stats_m.group(1)}</div>' if stats_m else ''
    
    # 构建board-section
    items_html = ''
    for event, source, url in items:
        items_html += f'''
        <div class="news-item animate-on-scroll">
          <div class="news-title-row">
            <span class="news-tag tag-new">NEW</span>
            <a href="{url}" target="_blank">{event}</a>
            <span class="news-source-inline">{source}</span>
          </div>
        </div>'''
    
    board_sections_html += f'''
<section id="{anchor}">
<div class="doc-chapter-label animate-on-scroll">{sec_name}</div>
<h2 class="animate-on-scroll" style="font-size:var(--heading-2);font-weight:700;color:var(--color-text-primary);margin-bottom:12px;display:flex;align-items:center;gap:8px;">
  <span style="font-size:18px;">{icon}</span> {sec_name}本周动态
</h2>
{f'<div class="callout callout-info animate-on-scroll" style="margin-bottom:16px;">{summary}</div>' if summary else ''}
<div class="board-section animate-on-scroll">
  <div class="board-header">
    <span class="board-badge">{len(items)}</span> 本周重要动态
  </div>
  {items_html}
</div>
{stats_html}
</section>'''

print(f"五大板块 board-section 构建完成")

# =========================================================================
# 重构周度洞察为deep-focus-card
# =========================================================================

# 提取三条洞察的title+正文+来源
insight_cards = re.findall(
    r'<div class="insight-card animate-on-scroll">.*?'
    r'<div class="insight-tag">(.*?)</div>.*?'
    r'<div class="insight-title">(.*?)</div>.*?'
    r'<p style="[^"]*">(.*?)</p>.*?'
    r'<div class="insight-trend">(.*?)</div>.*?'
    r'</div>',
    insight_section, re.DOTALL
)

INSIGHT_COLORS = [
    ('color-purple', 'var(--color-purple)', 'var(--color-purple-50, #F5F3FF)'),
    ('color-info',   'var(--color-info)',   'var(--color-info-50, #EFF6FF)'),
    ('color-success','var(--color-success)','var(--color-success-50, #ECFDF5)'),
]

insight_rebuilt = ''
for i, card in enumerate(insight_cards):
    tag, title, body, trend = card
    color_name, color_val, bg_color = INSIGHT_COLORS[i % len(INSIGHT_COLORS)]
    # 清理trend的SVG，保留链接
    trend_clean = re.sub(r'<svg[^>]*>.*?</svg>', LINK_SVG, trend, flags=re.DOTALL)
    
    insight_rebuilt += f'''
<div class="deep-focus-card animate-on-scroll" style="margin-bottom:20px;">
  <div class="deep-focus-header" style="background:linear-gradient(135deg,{color_val} 0%,{color_val}CC 100%);color:#fff;padding:18px 24px;border-radius:var(--radius-lg) var(--radius-lg) 0 0;display:flex;align-items:flex-start;gap:12px;">
    <div>
      <div class="deep-focus-label" style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;opacity:0.85;margin-bottom:6px;">{tag}</div>
      <div class="deep-focus-title" style="font-size:17px;font-weight:700;line-height:1.35;">{title}</div>
    </div>
  </div>
  <div class="deep-focus-body" style="padding:20px 24px;background:var(--color-bg-card);border:1px solid var(--color-border-light);border-top:none;border-radius:0 0 var(--radius-lg) var(--radius-lg);">
    <p style="font-size:14px;line-height:1.75;color:var(--color-text-secondary);margin-bottom:12px;">{body}</p>
    <div class="deep-focus-takeaway" style="margin-top:16px;padding:14px 16px;background:{bg_color};border-radius:var(--radius-md);border-left:3px solid {color_val};">
      <div class="deep-focus-takeaway-label" style="font-size:11px;font-weight:700;letter-spacing:0.08em;color:{color_val};text-transform:uppercase;margin-bottom:6px;">📎 来源参考</div>
      <div class="deep-focus-takeaway-text" style="font-size:13px;color:var(--color-text-secondary);">{trend_clean}</div>
    </div>
  </div>
</div>'''

print(f"周度洞察 deep-focus-card 构建完成，共{len(insight_cards)}条")

# =========================================================================
# 重构林克的洞察为pi-card
# =========================================================================

# 提取callout内容（三段）
callouts = re.findall(r'class="callout callout-\w+ animate-on-scroll"[^>]*>(.*?)</div>', linkinsight_section, re.DOTALL)

PI_TITLES = [
    '本周三条线索的交叉信号',
    'AI监管：刹车油门悖论',
    '对从业者的三条启示',
]

linkinsight_rebuilt = ''
for i, content in enumerate(callouts):
    # 将callout内的h3或strong转为正文强调
    content_clean = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<strong style="color:var(--color-text-primary);">\1</strong><br>', content, flags=re.DOTALL)
    title = PI_TITLES[i] if i < len(PI_TITLES) else f'洞察{i+1}'
    linkinsight_rebuilt += f'''
<div class="pi-card animate-on-scroll" style="margin-bottom:16px;">
  <div class="pi-card-label">{title}</div>
  <div class="pi-card-content" style="font-size:14px;line-height:1.75;">{content_clean}</div>
</div>'''

print(f"林克的洞察 pi-card 构建完成，共{len(callouts)}段")

# =========================================================================
# 重构概览区为overview-grid风格
# =========================================================================

# 提取表格行（5个板块概览）
overview_rows = re.findall(
    r'<tr><td[^>]*>.*?</td><td[^>]*>(.*?)</td></tr>',
    overview_section, re.DOTALL
)
OVERVIEW_ICONS = ['🧠', '💻', '📱', '🏭', '🔄']
OVERVIEW_LABELS = ['大模型', 'AI Coding', 'AI应用', 'AI行业', '企业AI转型']

overview_items = ''
for i, (label, icon) in enumerate(zip(OVERVIEW_LABELS, OVERVIEW_ICONS)):
    if i < len(overview_rows):
        text = re.sub(r'<[^>]+>', '', overview_rows[i]).strip()
        overview_items += f'''
      <div class="overview-item animate-on-scroll">
        <div class="overview-item-header">
          <span class="overview-item-icon">{icon}</span>
          <span class="overview-item-label">{label}</span>
        </div>
        <div class="overview-item-text" style="font-size:13px;color:var(--color-text-secondary);line-height:1.65;">{text}</div>
      </div>'''

# 提取stats-grid（从overview原始section）
stats_m = re.search(r'(<div class="stats-grid.*?</div>)\s*</section>', overview_section, re.DOTALL)
overview_stats = stats_m.group(1) if stats_m else ''

overview_rebuilt = f'''
<section id="overview">
<div class="doc-chapter-label animate-on-scroll">概览</div>
<h2 class="animate-on-scroll" style="font-size:var(--heading-2);font-weight:700;color:var(--color-text-primary);margin-bottom:16px;display:flex;align-items:center;gap:8px;">
  <svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
  本周概览
</h2>
<div class="overview animate-on-scroll">
  <div class="overview-title">
    <svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
    五大板块 · 本周信号
  </div>
  <div class="overview-grid five-cols">
    {overview_items}
  </div>
</div>
{overview_stats}
</section>'''

print("概览区 overview-grid 构建完成")

# =========================================================================
# 重构Top5（保持news-card，只升级header）
# =========================================================================
top5_rebuilt = top5_section  # 保持原样，Top5已经很好了

# =========================================================================
# 重构周度洞察section（加上deep-focus-card重构内容）
# =========================================================================
insight_rebuilt_section = f'''
<section id="insight">
<div class="doc-chapter-label animate-on-scroll">洞察</div>
<h2 class="animate-on-scroll" style="font-size:var(--heading-2);font-weight:700;color:var(--color-text-primary);margin-bottom:16px;display:flex;align-items:center;gap:8px;">
  <svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>
  周度洞察
</h2>
{insight_rebuilt}
</section>'''

# =========================================================================
# 重构林克的洞察section
# =========================================================================
linkinsight_rebuilt_section = f'''
<section id="linkinsight">
<div class="doc-chapter-label animate-on-scroll">林克的洞察</div>
<h2 class="animate-on-scroll" style="font-size:var(--heading-2);font-weight:700;color:var(--color-text-primary);margin-bottom:16px;display:flex;align-items:center;gap:8px;">
  <svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8c0 3.4 2.1 6.3 5 7.5V22h6v-4.5c2.9-1.2 5-4.1 5-7.5a8 8 0 0 0-8-8z"/><line x1="12" y1="12" x2="12" y2="18"/></svg>
  林克的洞察
</h2>
{linkinsight_rebuilt}
</section>'''

# =========================================================================
# 额外周报专用CSS
# =========================================================================
WEEKLY_EXTRA_CSS = '''
/* ===== 周报专用组件 ===== */
.news-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-normal), transform var(--transition-normal);
  position: relative;
  border-left: 4px solid var(--card-accent, var(--color-success));
}
.news-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
.news-card-rank {
  display: inline-flex; align-items: center;
  font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  background: color-mix(in srgb, var(--card-accent, var(--color-success)) 12%, white);
  color: var(--card-accent, var(--color-success));
  padding: 4px 10px; border-radius: var(--radius-full);
  margin-bottom: 10px;
}
.news-card-title {
  font-size: 18px; font-weight: 700; color: var(--color-text-primary);
  line-height: 1.4; margin-bottom: 10px;
}
.news-card-meta {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  font-size: 13px; color: var(--color-text-muted); margin-bottom: 12px;
}
.meta-item { display: flex; align-items: center; gap: 4px; }
.meta-divider { color: var(--color-border); }
.meta-link { color: var(--color-info); text-decoration: none; font-weight: 500; }
.meta-link:hover { text-decoration: underline; }
.news-card-desc {
  font-size: 14px; color: var(--color-text-secondary);
  line-height: 1.7; max-width: 68ch; margin-bottom: 16px;
}
.news-card-why {
  border-left: 3px solid var(--card-accent, var(--color-success));
  background: color-mix(in srgb, var(--card-accent, var(--color-success)) 5%, white);
  padding: 12px 16px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.judgment-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--card-accent, var(--color-success)); margin-bottom: 6px;
}
/* 洞察卡片（向后兼容） */
.insight-card {
  background: var(--color-bg-card); border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg); padding: 20px 24px; margin-bottom: 16px;
  box-shadow: var(--shadow-card);
}
.insight-tag {
  display: inline-block; font-size: 12px; font-weight: 600;
  color: var(--color-purple);
  background: color-mix(in srgb, var(--color-purple) 10%, white);
  padding: 3px 10px; border-radius: var(--radius-full); margin-bottom: 8px;
}
.insight-title {
  font-size: 16px; font-weight: 600; color: var(--color-text-primary);
  line-height: 1.4; margin-bottom: 12px;
}
.insight-trend {
  font-size: 13px; color: var(--color-text-muted);
  padding-top: 8px; border-top: 1px solid var(--color-border-light);
  display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
}
/* 日报索引 */
.daily-index { display: flex; flex-direction: column; gap: 8px; }
.daily-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px; background: var(--color-bg-card);
  border: 1px solid var(--color-border-light); border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.daily-item:hover { border-color: var(--color-success); background: rgba(5,150,105,0.02); }
.daily-item-date { font-size: 13px; font-weight: 600; color: var(--color-text-muted); min-width: 88px; }
.daily-item-link { font-size: 13px; color: var(--color-info); font-weight: 500; text-decoration: none; }
.daily-item-link:hover { text-decoration: underline; }
.daily-item-kw { font-size: 12px; color: var(--color-text-muted); flex: 1; max-width: 68ch; }
/* 表格 */
.table-wrap { overflow-x: auto; margin: 12px 0; }
.table-wrap table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table-wrap th { background: var(--color-bg-table-header); color: var(--color-text-secondary); padding: 10px 14px; font-weight: 600; font-size: 12px; text-align: left; border-bottom: 1px solid var(--color-border); }
.table-wrap td { padding: 10px 14px; border-bottom: 1px solid var(--color-border-light); vertical-align: middle; }
.table-wrap tbody tr:hover td { background: rgba(0,0,0,0.015); }
.table-wrap tr:last-child td { border-bottom: none; }
/* 行宽限制 */
.news-card-desc, .news-card-why, .insight-card p,
.content-paragraph, .callout > p, .daily-item-kw, .doc-footer p {
  max-width: 68ch;
}
/* callout */
.callout {
  padding: 14px 18px; border-radius: var(--radius-md);
  margin-bottom: 12px; font-size: 14px; line-height: 1.75;
  border-left: 3px solid;
}
.callout-purple { background: var(--color-purple-50,#F5F3FF); border-color: var(--color-purple); color: var(--color-text-secondary); }
.callout-info { background: var(--color-info-50,#EFF6FF); border-color: var(--color-info); color: var(--color-text-secondary); }
.callout-success { background: var(--color-success-50,#ECFDF5); border-color: var(--color-success); color: var(--color-text-secondary); }
.callout-warning { background: var(--color-warning-50,#FFFBEB); border-color: var(--color-warning); color: var(--color-text-secondary); }
.callout-danger { background: #FFF1F2; border-color: var(--color-danger); color: var(--color-text-secondary); }
/* doc-footer */
.doc-footer {
  margin-top: 32px; padding: 20px 0; border-top: 1px solid var(--color-border-light);
  font-size: 13px; color: var(--color-text-muted); display: flex; flex-direction: column; gap: 4px;
}
/* animate-on-scroll */
.animate-on-scroll { opacity: 0; transform: translateY(14px); transition: opacity 0.4s ease, transform 0.4s ease; }
.animate-on-scroll.visible { opacity: 1; transform: none; }
'''

# =========================================================================
# 提取原周报的JS
# =========================================================================
js_m = re.search(r'<script>(.*?)</script>', weekly_html, re.DOTALL)
weekly_js = js_m.group(1) if js_m else ''

# 保留完整的header区（h1+meta行）
header_m = re.search(r'(<header class="doc-header">.*?</header>)', weekly_html, re.DOTALL)
header_block = header_m.group(1) if header_m else '<header class="doc-header"><div class="header-badge">AI INSIGHT · WEEKLY REPORT · 24</div><h1 class="header-title">AI 周报 2026年第24周</h1><p class="header-meta"><span>06/09-06/14</span></p></header>'

# 提取sidebar
sidebar_m = re.search(r'(<nav class="sidebar-nav[^"]*"[^>]*>.*?</nav>)', weekly_html, re.DOTALL)
sidebar_block = sidebar_m.group(1) if sidebar_m else ''
# 确保sidebar默认折叠
if sidebar_block:
    sidebar_block = sidebar_block.replace('class="sidebar-nav"', 'class="sidebar-nav sidebar-collapsed"')
    sidebar_block = sidebar_block.replace('class="sidebar-nav animate-on-scroll"', 'class="sidebar-nav sidebar-collapsed"')

collapse_btn_m = re.search(r'(<button class="sidebar-collapse-btn"[^>]*>.*?</button>)', weekly_html, re.DOTALL)
collapse_btn = collapse_btn_m.group(1) if collapse_btn_m else ''
if collapse_btn and 'collapsed-pos' not in collapse_btn:
    collapse_btn = collapse_btn.replace('class="sidebar-collapse-btn"', 'class="sidebar-collapse-btn collapsed-pos"')
    collapse_btn = collapse_btn.replace('折叠导航', '展开导航').replace('«', '»')

# =========================================================================
# 组装最终HTML
# =========================================================================

final_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 周报 2026-W24 (06/09-06/14) | AI洞察</title>
<meta name="description" content="基建竞赛全面启动——谷歌800亿+DeepSeek 500亿融资指向算力基础设施；Fable/Mythos双轨发布开启安全分层新模式；豆包付费宣告AI免费获客时代终结；AI编程信任悖论浮出水面">
<meta property="og:title" content="AI 周报 2026-W24 | AI洞察">
<meta property="og:type" content="article">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%232563EB'/%3E%3Ctext x='6' y='23' font-size='18' fill='white'%3E📊%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<noscript><style>.animate-on-scroll{{opacity:1!important;transform:none!important;}}</style></noscript>
<style>
{daily_css}

{WEEKLY_EXTRA_CSS}
</style>
</head>
<body>
<a class="skip-to-content" href="#main-content">跳到主内容</a>
<div class="layout-wrapper">
{sidebar_block}
{collapse_btn}
<main class="content-area" id="main-content">
<div class="content-inner">

{header_block}

{overview_rebuilt}

{top5_rebuilt}

{insight_rebuilt_section}

{linkinsight_rebuilt_section}

{board_sections_html}

{dailyindex_section}

{vocab_section}

{narrative_section}

{more_block}
</div>
</main>
</div>
<div class="scroll-to-top" id="scrollToTop">↑</div>
<script>
{weekly_js}
</script>
</body>
</html>'''

print(f"最终HTML组装完成，大小: {len(final_html.encode())} bytes")

# 验证合规
issues = []
if len(final_html.encode()) < 50000:
    issues.append(f"文件太小: {len(final_html.encode())} < 50000")
if '{{' in final_html:
    issues.append("发现{{模板变量}}")
if re.search(r'\*\*[^\n]*\*\*', final_html):
    issues.append("发现**Markdown**语法")
if 'href=""' in final_html:
    issues.append("发现空href")
if '我是' not in final_html or '林克' not in final_html:
    issues.append("了解更多林克介绍缺失")

if issues:
    print("⚠️ 合规问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ 合规检查通过")

# 写入
with open(WEEKLY_OUT, 'w', encoding='utf-8') as f:
    f.write(final_html)
print(f"✅ 写入: {WEEKLY_OUT}")

import shutil
shutil.copy(WEEKLY_OUT, PUBLIC_OUT)
print(f"✅ 同步: {PUBLIC_OUT}")

print(f"\n最终文件大小: {os.path.getsize(WEEKLY_OUT):,} bytes")
PYEOF
