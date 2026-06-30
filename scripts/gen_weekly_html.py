#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI周报 HTML 生成器 — 从JSON动态生成
====================================
用法:
  1. LLM填写 data/weekly-content-YYYY-WXX.json
  2. uv run scripts/gen_weekly_html.py --date YYYY-WXX --input data/weekly-content-YYYY-WXX.json
  3. 自动输出到 01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html + cp到public/

自校验: ≥50KB + 5板块完整 + {{message}}扫描 + class名一致性
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_CSS_FILE = BASE_DIR / "templates" / "daily-report-v3.css"
TEMPLATE_JS_FILE = BASE_DIR / "templates" / "daily-report-v3.js"
REPORT_DIR = BASE_DIR / "01-daily-reports"
PUBLIC_DIR = BASE_DIR / "public"
DATA_DIR = BASE_DIR / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import INTERNAL_PAGES_BASE as INTERNAL_BASE
QINGSHUANG_SKILL_PATH = Path("/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/skills/qingshuang-research-style")
QINGSHUANG_BASE_CSS = QINGSHUANG_SKILL_PATH / "references" / "base-styles.css"
CUSTOM_CSS = BASE_DIR / "templates" / "ai-insight-custom.css"

ACCENT_MAP = {"purple":"var(--color-purple)","info":"var(--color-info)",
              "success":"var(--color-success)","warning":"var(--color-warning)","danger":"var(--color-danger)"}


# SVG icons for sidebar TOC — replaces emoji in structural elements (#124 format upgrade)
# Source: W22 manual upgrade (2026-06-01), now codified in script
SVG_ICONS = {
    "overview":    '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>',
    "top5":        '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.83-1 .83s-1-.28-1-.83v-2.34"/><path d="M14 14.66V17c0 .55.47.83 1 .83s1-.28 1-.83v-2.34"/><line x1="12" y1="3" x2="12" y2="14"/><path d="M6 4v5a6 6 0 0 0 12 0V4"/></svg>',
    "insight":     '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
    "linkinsight": '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8c0 3.4 2.1 6.3 5 7.5V22h6v-4.5c2.9-1.2 5-4.1 5-7.5a8 8 0 0 0-8-8z"/><line x1="12" y2="12" x2="12" y2="18"/></svg>',
    "llm":         '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8c0 3.4 2.1 6.3 5 7.5V22h6v-4.5c2.9-1.2 5-4.1 5-7.5a8 8 0 0 0-8-8z"/><line x1="12" y2="12" x2="12" y2="18"/></svg>',
    "coding":      '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "app":         '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>',
    "industry":    '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20h20V8l-6 4V4l-6 4V2L2 10v10z"/></svg>',
    "enterprise":   '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M20.49 15a9 9 0 0 1-14.85 3.36L1 14"/></svg>',
    "dailyindex":  '<svg class="meta-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y2="4" x2="16" y2="1"/><line x1="8" y2="4" x2="8" y2="1"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "vocab":       '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    "narrative":    '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.6 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2s2.6 2 5 2c2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2s2.6 2 5 2c2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>',
    "calendar":    '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="4"/><line x1="8" y1="2" x2="8" y2="4"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "newspaper":   '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/></svg>',
    "globe":       '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "home":        '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10l9-7 9 7v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/></svg>',
    "trophy":      '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.83-1 .83s-1-.28-1-.83v-2.34"/><path d="M14 14.66V17c0 .55.47.83 1 .83s1-.28 1-.83v-2.34"/><line x1="12" y1="3" x2="12" y2="14"/><path d="M6 4v5a6 6 0 0 0 12 0V4"/></svg>',
    "link":        '<svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
}

SECTION_META = {
    "llm":        {"icon": SVG_ICONS["llm"], "label": "大模型",    "h2_suffix": "大模型本周动态", "color": "#059669"},
    "coding":     {"icon": SVG_ICONS["coding"], "label": "AI Coding", "h2_suffix": "AI Coding本周动态", "color": "#2563EB"},
    "app":        {"icon": SVG_ICONS["app"], "label": "AI应用",    "h2_suffix": "AI应用本周动态", "color": "#7C3AED"},
    "industry":   {"icon": SVG_ICONS["industry"], "label": "AI行业",    "h2_suffix": "AI行业本周动态", "color": "#D97706"},
    "enterprise": {"icon": SVG_ICONS["enterprise"], "label": "企业转型",   "h2_suffix": "企业AI转型本周动态", "color": "#E11D48"},
}

# Emoji-to-section key mapping for overview table dimension cleanup (#124)
_DIMENSION_EMOJI_MAP = {
    "🧠": "llm", "⌨️": "coding", "📱": "app", "🏭": "industry", "🔄": "enterprise",
}

def _clean_dimension_emoji(text):
    """Replace leading emoji in overview table dimension with SVG icon (#124 format upgrade)"""
    for emj, key in _DIMENSION_EMOJI_MAP.items():
        if text.startswith(emj):
            label = text[len(emj):].strip()
            return f'{SVG_ICONS.get(key, "")} {label}'
    return text

# 68ch line width CSS for body text paragraphs (#124 format upgrade)
LINE_WIDTH_CSS = """
/* ===== 68ch行宽限制（容器100%，文字68ch）===== */
.news-card-desc, .news-card-why, .insight-card p,
.content-paragraph, .callout > p,
.daily-item-kw, .doc-footer p {
  max-width: 68ch;
}

/* ===== stats-grid自适应列数（支持4/5卡）===== */
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
"""

REQUIRED_CLASSES = ["news-card","stat-card","insight-card","callout",
                    "doc-header","daily-index","table-wrap","doc-chapter-label"]

def compute_week_dates(week_id):
    y, wn = int(week_id.split("-W")[0]), int(week_id.split("-W")[1])
    iso_mon = datetime.strptime(f"{y}-W{wn:02d}-1", "%G-W%V-%u")
    cov_mon = iso_mon - timedelta(days=7)
    cov_sun = iso_mon - timedelta(days=1)
    # Month for file path = ISO Monday month (where cron runs & daily reports live),
    # NOT coverage_sunday month (which can be previous month for W23 etc.)
    month_str = iso_mon.strftime("%Y-%m")
    return {"cov_mon":cov_mon, "cov_sun":cov_sun, "month_str":month_str,
            "date_range":f"{cov_mon.strftime('%m/%d')}-{cov_sun.strftime('%m/%d')}"}

def esc(s):
    """Escape { } in strings for safe f-string embedding"""
    return s.replace("{", "&#123;").replace("}", "&#125;") if s else ""

def render_overview(d):
    ov = d.get("overview",{})
    rows = ov.get("table_rows",[])
    stats = ov.get("stats",[])
    # 概览表格：升级为 board-table 样式
    tbl = ""
    if rows:
        tbl_rows = ""
        for r in rows:
            dim = _clean_dimension_emoji(r["dimension"])
            sig = r["signal"]
            tbl_rows += f'<tr><td style="font-weight:600;min-width:80px;">{dim}</td><td>{sig}</td></tr>\n'
        tbl = f'''<div class="table-wrap animate-on-scroll">
<table class="board-table" style="--board-color:#059669;">
<thead><tr><th>维度</th><th>周度信号</th></tr></thead>
<tbody>{tbl_rows}</tbody>
</table></div>'''
    # stat-card 网格
    st = '<div class="stats-grid animate-on-scroll">\n'
    for s in stats:
        st += f'  <div class="stat-card {s.get("class","stat-info")}"><div class="stat-value">{s["value"]}</div><div class="stat-label">{s["label"]}</div></div>\n'
    st += '</div>'
    return f'<section id="overview">\n<div class="doc-chapter-label animate-on-scroll">概览</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["overview"]} 本周概览</h2>\n{tbl}\n{st}\n</section>'

def render_top5(d):
    svg_calendar = '<svg class="meta-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y2="4" x2="16" y2="1"/><line x1="8" y2="4" x2="8" y2="1"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
    svg_link = '<svg class="meta-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'
    cards = ""
    for item in d.get("top5",[]):
        ac = ACCENT_MAP.get(item.get("accent","info"),"var(--color-info)")
        rank = item.get("rank", "")
        label = item.get("label", "")
        sources = item.get("sources", [])
        meta_date = f'<span class="meta-item">{svg_calendar} {d.get("date_range","")}</span>'
        meta_sources = ""
        if sources:
            source_parts = []
            for s in sources:
                surl = s.get("url","")
                sname = s.get("name","")
                if surl:
                    source_parts.append(f'<a href="{surl}" target="_blank" class="meta-link">{svg_link} {sname}</a>')
                else:
                    source_parts.append(f'<span class="meta-item">{sname}</span>')
            meta_sources = '<span class="meta-divider">·</span>' + '<span class="meta-divider">·</span>'.join(source_parts)
        else:
            source_url = item.get("source_url", item.get("url",""))
            source_name = item.get("source","")
            meta_sources = f'<span class="meta-divider">·</span><a href="{source_url}" target="_blank" class="meta-link">{svg_link} {source_name}</a>' if source_url else f'<span class="meta-divider">·</span><span class="meta-item">{source_name}</span>'
        # 升级：卡片化结构 + 左边框 + why区域高亮背景
        cards += f'''<div class="weekly-news-card animate-on-scroll" style="border-left:4px solid {ac};background:var(--color-bg-card);border-radius:var(--radius-md);padding:18px 20px;margin-bottom:14px;box-shadow:var(--shadow-card);transition:box-shadow .2s,transform .2s;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <span style="background:{ac};color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:var(--radius-full);letter-spacing:.05em;">TOP {rank}</span>
    <span style="font-size:12px;color:var(--color-text-muted);font-weight:500;">{label}</span>
  </div>
  <div class="news-card-title" style="font-size:17px;font-weight:700;color:var(--color-text-primary);line-height:1.4;margin-bottom:8px;">{item["title"]}</div>
  <div class="news-card-meta" style="margin-bottom:10px;">{meta_date}{meta_sources}</div>
  <div class="news-card-desc" style="font-size:14px;color:var(--color-text-secondary);line-height:1.7;margin-bottom:12px;">{item["desc"]}</div>
  <div style="background:color-mix(in srgb,{ac} 6%,white);border-radius:var(--radius-sm);padding:10px 14px;border-left:3px solid {ac};">
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:{ac};margin-bottom:4px;">关键判断</div>
    <div class="news-card-why" style="font-size:13px;line-height:1.7;color:var(--color-text-primary);">{item["why"]}</div>
  </div>
</div>
'''
    return f'<section id="top5">\n<div class="doc-chapter-label animate-on-scroll">Top 5</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["trophy"]} 本周 Top 5 事件</h2>\n{cards}\n</section>'

def _clean_daily_url(url):
    """Remove -v3.html suffix from daily report URLs — internal and external use plain .html"""
    if url and "-v3.html" in url:
        return url.replace("-v3.html", ".html")
    return url

def render_insights(d):
    INSIGHT_COLORS = ["#7C3AED","#2563EB","#059669","#D97706","#E11D48"]
    cards = ""
    for i, item in enumerate(d.get("insights",[])):
        color = INSIGHT_COLORS[i % len(INSIGHT_COLORS)]
        links = item.get("trend_links",[])
        tl = " · ".join(f'<a href="{_clean_daily_url(l["url"])}" target="_blank" style="color:{color};">{l["text"]}</a>' for l in links) if links else ""
        trend_html = f'<div class="insight-trend" style="margin-top:10px;font-size:12px;color:var(--color-text-muted);">{SVG_ICONS["link"]} {tl}</div>' if tl else ""
        cards += f'''<div class="animate-on-scroll" style="background:var(--color-bg-card);border-radius:var(--radius-md);padding:20px 22px;margin-bottom:16px;box-shadow:var(--shadow-card);border-left:4px solid {color};">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
    <span style="background:{color};color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:var(--radius-full);">{item["tag_label"]}</span>
  </div>
  <div style="font-size:16px;font-weight:700;color:{color};line-height:1.4;margin-bottom:10px;">{item["title"]}</div>
  <p style="font-size:14px;color:var(--color-text-secondary);line-height:1.8;margin:0;">{item["content"]}</p>
  {trend_html}
</div>
'''
    return f'<section id="insight">\n<div class="doc-chapter-label animate-on-scroll">洞察</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["insight"]} 周度洞察</h2>\n{cards}\n</section>'

def _strip_double_strong(text):
    """Remove double <strong><strong>...</strong></strong> nesting — only one level needed"""
    # Also strip single <strong> if the whole content is wrapped (callout adds its own <strong> wrapper)
    text = text.replace("<strong><strong>", "<strong>").replace("</strong></strong>", "</strong>")
    return text

def render_link_insight(d):
    li = d.get("link_insight",{})
    intro_raw = li.get("intro_callout","")
    intro_inner = _strip_double_strong(intro_raw)
    if intro_inner.startswith("<strong>") and intro_inner.endswith("</strong>"):
        intro_inner = intro_inner[len("<strong>"):-len("</strong>")]
    intro = f'<div class="callout callout-purple animate-on-scroll"><strong>{intro_inner}</strong></div>' if intro_raw else ""
    blocks = ""
    for k in ["turning_point","paradox","takeaway"]:
        b = li.get(k,{})
        if b: blocks += f'<div class="callout {b.get("class","callout-info")} animate-on-scroll" style="margin-top:16px;">{_strip_double_strong(b.get("content",""))}</div>\n'
    return f'<section id="linkinsight">\n<div class="doc-chapter-label animate-on-scroll">深度洞察</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["linkinsight"]} 深度洞察</h2>\n{intro}\n{blocks}\n</section>'

def md_link_to_html(text):
    """Convert markdown links [text](url) to HTML <a> tags. Defensive cleaner.
    Returns (converted_html, list_of_extracted_urls)."""
    import re as _re
    urls = []
    def _replace(m):
        link_text = m.group(1)
        url = m.group(2)
        urls.append(url)
        return f'<a href="{url}" target="_blank">{link_text}</a>'
    result = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _replace, text)
    return result, urls

def render_section(key, sec):
    """渲染五大板块，key是llm/coding/app/industry/enterprise"""
    meta = SECTION_META.get(key, {"icon": "📌", "label": key, "h2_suffix": key, "color": "#2563EB"})
    id_ = key
    icon = meta["icon"]
    title = meta["h2_suffix"]
    board_color = meta.get("color", "#2563EB")
    co = sec.get("callout","")
    cocl = sec.get("callout_class","callout-info")
    co_html = f'<div class="callout {cocl} animate-on-scroll" style="border-left-color:{board_color};">{co}</div>' if co else ""
    tbl = sec.get("table",[])
    tbl_html = ""
    if tbl:
        rows = ""
        for r in tbl:
            event_raw = r.get("event","")
            source_raw = r.get("source","")
            extracted_url = r.get("url","")
            event_html, event_urls = md_link_to_html(event_raw)
            source_html, source_urls = md_link_to_html(source_raw)
            if not extracted_url and event_urls:
                extracted_url = event_urls[0]
            link_cell = f'<a href="{extracted_url}" target="_blank" style="color:{board_color};">链接</a>' if extracted_url else ""
            rows += f'<tr><td>{event_html}</td><td>{source_html}</td>{f"<td>{link_cell}</td>" if link_cell else ""}</tr>\n'
        has_any_link = any(r.get("url","") or md_link_to_html(r.get("event",""))[1] for r in tbl)
        header_extra = "<th>链接</th>" if has_any_link else ""
        col_extra = "<col>" if has_any_link else ""
        tbl_html = f'<div class="table-wrap animate-on-scroll">\n<table class="board-table" style="--board-color:{board_color};"><colgroup><col style="width:55%;"><col style="width:30%;">{col_extra}</colgroup><thead><tr><th>事件</th><th>来源</th>{header_extra}</tr></thead>\n<tbody>{rows}</tbody></table></div>'
    stats = sec.get("stats",[])
    stats_html = ""
    if stats:
        stats_html = '<div class="stats-grid animate-on-scroll">\n' + "".join(f'  <div class="stat-card {s.get("class","stat-info")}"><div class="stat-value">{s["value"]}</div><div class="stat-label">{s["label"]}</div></div>\n' for s in stats) + '</div>'
    return f'''<section id="{id_}" style="--section-color:{board_color};margin-top:40px;padding-top:32px;border-top:2px solid color-mix(in srgb,{board_color} 15%,var(--color-border-light));">
<div class="doc-chapter-label animate-on-scroll" style="color:{board_color};background:color-mix(in srgb,{board_color} 8%,white);display:inline-block;padding:2px 10px;border-radius:var(--radius-full);font-size:11px;">{meta["label"]}</div>
<h2 class="animate-on-scroll" style="color:{board_color};margin-top:10px;">{icon} {title}</h2>
{co_html}
{tbl_html}
{stats_html}
</section>'''

def render_daily_index(d):
    items = d.get("daily_index",[])
    cards = "".join(f'''<div class="daily-item">
  <div class="daily-item-date">{i["date"]}<br/><span style="font-weight:400;font-size:10px;opacity:.8;">{i["weekday"]}</span></div>
  <div style="flex:1;min-width:0;">
    <a href="{i["url"]}" target="_blank" class="daily-item-link">{i["title"]}</a>
    <div class="daily-item-kw">{i.get("keywords","")}</div>
  </div>
</div>
''' for i in items)
    return f'<section id="dailyindex">\n<div class="doc-chapter-label animate-on-scroll">日报索引</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["dailyindex"]} 本周日报索引</h2>\n<div class="daily-index animate-on-scroll">\n{cards}\n</div>\n</section>'

def render_vocab(d):
    items = d.get("vocab",[])
    if not items: return ""
    rows = "".join(f'<tr><td style="font-weight:600;min-width:80px;">{i["term"]}</td><td style="color:var(--color-text-secondary);">{i["definition"]}</td><td style="color:var(--color-text-muted);font-size:12px;">{i.get("source","")}</td></tr>\n' for i in items)
    return f'<section id="vocab">\n<div class="doc-chapter-label animate-on-scroll">技术词汇</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["vocab"]} 技术词汇表</h2>\n<div class="table-wrap animate-on-scroll">\n<table class="board-table" style="--board-color:#7C3AED;"><thead><tr><th>术语</th><th>定义</th><th>出处</th></tr></thead>\n<tbody>{rows}</tbody></table></div>\n</section>'

def render_narrative(d):
    n = d.get("narrative",{})
    if not n: return ""
    intro_inner = _strip_double_strong(n.get("intro_callout",""))
    # If entire intro is wrapped in <strong>, unwrap it (we add our own wrapper)
    if intro_inner.startswith("<strong>") and intro_inner.endswith("</strong>"):
        intro_inner = intro_inner[len("<strong>"):-len("</strong>")]
    intro = f'<div class="callout callout-purple animate-on-scroll"><strong>{intro_inner}</strong></div>'
    blocks = "".join(f'<div class="callout {b.get("class","callout-info")} animate-on-scroll" style="margin-top:16px;">{_strip_double_strong(b.get("content",""))}</div>\n' for b in n.get("main_blocks",[]))
    conc = ""
    if n.get("conclusion_callout"):
        conc = f'<hr style="border:none;border-top:2px solid var(--color-success);margin:32px 0;">\n<div class="callout callout-success animate-on-scroll">{_strip_double_strong(n["conclusion_callout"])}</div>'
    return f'<section id="narrative">\n<div class="doc-chapter-label animate-on-scroll">宏观叙事</div>\n<h2 class="animate-on-scroll">{SVG_ICONS["narrative"]} 宏观叙事：{n.get("title","")}</h2>\n{intro}\n{blocks}\n{conc}\n</section>'

LEARN_MORE_TEMPLATE = '''<div style="max-width:100%;margin:0 auto;padding:0 0 48px;">
<div style="background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #E7E5E4;border-radius:14px;padding:24px 28px;box-shadow:0 2px 8px rgba(31,35,40,.06)">
  <div style="font-size:16px;font-weight:700;margin-bottom:8px">__SVG_INSIGHT__ 了解更多</div>
  <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">AI洞察是系统化追踪AI行业动态的项目，覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。</p>
  <a href="__HOMEPAGE_URL__/" target="_blank" style="display:inline-flex;padding:8px 16px;background:linear-gradient(135deg,#059669,#10B981);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">__SVG_HOME__ 访问AI洞察首页</a>
</div></div>'''

def render_sidebar(d):
    secs = d.get("sections",{})
    links = [f'<a href="#overview" class="toc-link">{SVG_ICONS.get("overview","")} 本周概览</a>',
             f'<a href="#top5" class="toc-link">{SVG_ICONS.get("top5","")} Top 5 事件</a>',
             f'<a href="#insight" class="toc-link">{SVG_ICONS.get("insight","")} 周度洞察</a>',
             f'<a href="#linkinsight" class="toc-link">{SVG_ICONS.get("linkinsight","")} 深度洞察</a>']
    for k,s in secs.items():
        icon_svg = SVG_ICONS.get(k, s.get("icon",""))
        links.append(f'<a href="#{k}" class="toc-link">{icon_svg} {s.get("title",k)}</a>')
    links.extend([f'<a href="#dailyindex" class="toc-link">{SVG_ICONS.get("dailyindex","")} 日报索引</a>',
                  f'<a href="#vocab" class="toc-link">{SVG_ICONS.get("vocab","")} 技术词汇</a>',
                  f'<a href="#narrative" class="toc-link">{SVG_ICONS.get("narrative","")} 宏观叙事</a>'])
    return f'<nav class="sidebar-nav" id="sidebar" aria-label="目录导航">\n<div class="sidebar-doc-title">AI 周报 {d.get("week_id","")}</div>\n<div class="toc-section"><div class="toc-group-label">目录</div>\n{chr(10).join(links)}\n</div>\n<div class="reading-progress-wrap"><div class="reading-progress-label">阅读进度</div><div class="reading-progress-track"><div class="reading-progress-fill" id="readingProgress"></div></div></div>\n</nav>'

def generate_html(d):
    wid = d.get("week_id","2026-W22")
    dt = compute_week_dates(wid)
    # CSS
    base_css = QINGSHUANG_BASE_CSS.read_text(encoding="utf-8") if QINGSHUANG_BASE_CSS.exists() else ""
    rep_css = ""
    if TEMPLATE_CSS_FILE.exists():
        raw = TEMPLATE_CSS_FILE.read_text(encoding="utf-8")
        raw = re.sub(r'^\s*<style[^>]*>\s*','',raw); raw = re.sub(r'\s*</style>\s*$','',raw)
        rep_css = raw
    cust_css = CUSTOM_CSS.read_text(encoding="utf-8") if CUSTOM_CSS.exists() else ""
    css_block = f"<style>\n{base_css}\n\n/* ===== 日报组件层 ===== */\n{rep_css}\n\n/* ===== AI洞察定制层 ===== */\n{cust_css}\n\n{LINE_WIDTH_CSS}\n</style>"
    js_block = TEMPLATE_JS_FILE.read_text(encoding="utf-8") if TEMPLATE_JS_FILE.exists() else "<script></script>"
    
    subtitle = d.get("subtitle","")
    subtitle_html = f'\n  <div style="clear:both;display:block;width:100%;font-size:13px;color:var(--color-text-muted);margin-top:14px;margin-bottom:16px;line-height:1.8;max-width:100%;letter-spacing:0.01em;">{subtitle}</div>' if subtitle else ""
    header = f'<header class="doc-header">\n  <div class="header-badge">AI INSIGHT · WEEKLY REPORT · {d["week_num"]}</div>\n  <h1 class="header-title">AI 周报 {d["year"]}年第{d["week_num"]}周</h1>{subtitle_html}\n  <p class="header-meta"><span>{SVG_ICONS["calendar"]} {d["date_range"]}</span><span>{SVG_ICONS["newspaper"]} 覆盖7天日报 · 5板块</span><span>{SVG_ICONS["globe"]} 海外+国内</span></p>\n</header>'
    
    body_secs = [header, render_overview(d), render_top5(d), render_insights(d), render_link_insight(d)]
    for k in ["llm","coding","app","industry","enterprise"]:
        s = d.get("sections",{}).get(k,{})
        if s: body_secs.append(render_section(k, s))
    body_secs.append(render_daily_index(d))
    v = render_vocab(d)
    if v: body_secs.append(v)
    n = render_narrative(d)
    if n: body_secs.append(n)
    learn_more = LEARN_MORE_TEMPLATE.replace("__SVG_INSIGHT__", SVG_ICONS["insight"]).replace("__HOMEPAGE_URL__", INTERNAL_BASE).replace("__SVG_HOME__", SVG_ICONS["home"])
    body_secs.append(learn_more)
    
    footer = f'<div class="doc-footer"><p>{SVG_ICONS["newspaper"]} AI洞察 · 周报 · {wid}</p><p style="margin-top:4px;">数据来源：AI洞察日报 {d.get("date_range","")} · 5板块</p><p style="margin-top:8px;"><a href="{INTERNAL_BASE}/" target="_blank">{SVG_ICONS["home"]} 访问AI洞察首页，获取更多深度分析</a></p></div>'
    sidebar = render_sidebar(d)
    
    fav = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%232563EB'/%3E%3Ctext x='6' y='23' font-size='18' fill='white'%3E⚡%3C/text%3E%3C/svg%3E"
    
    html_head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 周报 {wid} ({d["date_range"]}) | AI洞察</title>
<meta name="description" content="{d.get('description','AI行业动态周报')}">
<meta property="og:title" content="AI 周报 {wid} | AI洞察">
<meta property="og:description" content="{d.get('description','')}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="{fav}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<noscript></noscript>
{css_block}
</head>"""
    
    html_body = f"""<body>
<a class="skip-to-content" href="#main-content">跳到主内容</a>
<div class="layout-wrapper">
{sidebar}
<button class="sidebar-collapse-btn" id="collapseBtn" title="折叠导航" aria-label="折叠导航">«</button>
<main class="content-area" id="main-content">
<div class="content-inner">
{chr(10).join(body_secs)}
{footer}
</div>
</main>
</div>
<div class="scroll-to-top" id="scrollToTop">↑</div>
{js_block}
</body>
</html>"""
    
    return html_head + "\n" + html_body

def validate_html(html, wid):
    errs = []
    sz = len(html.encode("utf-8"))
    if sz < 50000: errs.append(f"HTML大小={sz}字节，低于50KB阈值")
    if "{{message}}" in html or "{{" in html: errs.append("HTML包含{{...}}占位符（P0红线）")
    for sid in ["llm","coding","app","industry","enterprise"]:
        if f'id="{sid}"' not in html: errs.append(f"缺失板块: {sid}")
    for cls in REQUIRED_CLASSES:
        if cls not in html: errs.append(f"缺失class名: {cls}")
    if "了解更多" not in html: errs.append("缺失底部了解更多模块（P0强制）")
    # #124: Markdown syntax leaked into HTML
    import re as _re
    md_links = _re.findall(r'\[([^\]]+)\]\(([^)]+)\)', html)
    if md_links: errs.append(f"HTML包含{len(md_links)}处未渲染Markdown链接[text](url)（#124防复发）")
    empty_hrefs = html.count('href=""')
    if empty_hrefs: errs.append(f"HTML包含{empty_hrefs}处空href链接（#124防复发）")
    # #W24-0615: Header副标题间距检查
    if 'margin-top:2px' in html and 'clear:both' in html: errs.append("副标题margin-top=2px太挤，需≥14px（#W24-0615）")
    if 'max-width:640px' in html and 'clear:both' in html: errs.append("副标题max-width=640px在content-inner内双约束，需100%（#W24-0615）")
    # #W24-0615: 了解更多模块双约束检查
    if 'max-width:var(--content-max)' in html and 'padding:16px 20px 48px' in html: errs.append("了解更多外层div有独立max-width约束，需改为100%（#W24-0615）")
    if errs:
        print(f"\n❌ HTML自校验失败 ({len(errs)}):")
        for e in errs: print(f"  • {e}")
        return False
    print(f"\n✅ HTML自校验通过: {sz/1024:.1f}KB + 5板块 + {len(REQUIRED_CLASSES)}个class名 + 了解更多模块 + 无Markdown泄漏 + 无空href")
    return True

def main():
    parser = argparse.ArgumentParser(description="AI周报HTML生成器（从JSON动态生成）")
    parser.add_argument("--date", required=True, help="周号 YYYY-WXX")
    parser.add_argument("--input", default=None, help="JSON文件路径（默认 data/weekly-content-YYYY-WXX.json）")
    parser.add_argument("--skip-validate", action="store_true", help="跳过HTML自校验")
    args = parser.parse_args()
    wid = args.date
    json_path = args.input if args.input else str(BASE_DIR / "data" / f"weekly-content-{wid}.json")
    jp = Path(json_path)
    if not jp.exists(): print(f"❌ JSON文件不存在: {jp}"); sys.exit(1)
    try: d = json.loads(jp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e: print(f"❌ JSON格式错误: {e}"); sys.exit(1)
    print(f"📊 生成周报HTML: {wid}")
    html = generate_html(d)
    if not args.skip_validate and not validate_html(html, wid): sys.exit(1)
    dt = compute_week_dates(wid)
    ms = dt["month_str"]
    op = REPORT_DIR / ms / f"weekly-{wid}.html"
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(html, encoding="utf-8")
    sz = op.stat().st_size
    print(f"✅ HTML已写入: {op} ({sz/1024:.1f}KB)")
    pp = PUBLIC_DIR / "01-daily-reports" / ms / f"weekly-{wid}.html"
    pp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(op, pp)
    ps = pp.stat().st_size
    print(f"✅ 已同步到public/: {pp} ({ps/1024:.1f}KB)")
    if abs(sz-ps)>100: print(f"⚠️ 源文件({sz})和public({ps})大小不一致！")
    print(f"\n🔗 内部版URL: {INTERNAL_BASE}/01-daily-reports/{ms}/weekly-{wid}.html")

if __name__ == "__main__":
    main()