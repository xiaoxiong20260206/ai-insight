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
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"
QINGSHUANG_SKILL_PATH = Path("/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/skills/qingshuang-research-style")
QINGSHUANG_BASE_CSS = QINGSHUANG_SKILL_PATH / "references" / "base-styles.css"
CUSTOM_CSS = BASE_DIR / "templates" / "ai-insight-custom.css"

ACCENT_MAP = {"purple":"var(--color-purple)","info":"var(--color-info)",
              "success":"var(--color-success)","warning":"var(--color-warning)","danger":"var(--color-danger)"}
REQUIRED_CLASSES = ["news-card","stat-card","insight-card","callout",
                    "doc-header","daily-index","table-wrap","doc-chapter-label"]

def compute_week_dates(week_id):
    y, wn = int(week_id.split("-W")[0]), int(week_id.split("-W")[1])
    iso_mon = datetime.strptime(f"{y}-W{wn:02d}-1", "%G-W%V-%u")
    cov_mon = iso_mon - timedelta(days=7)
    cov_sun = iso_mon - timedelta(days=1)
    return {"cov_mon":cov_mon, "cov_sun":cov_sun, "month_str":cov_sun.strftime("%Y-%m"),
            "date_range":f"{cov_mon.strftime('%m/%d')}-{cov_sun.strftime('%m/%d')}"}

def esc(s):
    """Escape { } in strings for safe f-string embedding"""
    return s.replace("{", "&#123;").replace("}", "&#125;") if s else ""

def render_overview(d):
    ov = d.get("overview",{})
    rows = ov.get("table_rows",[])
    stats = ov.get("stats",[])
    tbl = ""
    if rows:
        tbl = '<div class="animate-on-scroll" style="overflow-x:auto;">\n<table style="width:100%;border-collapse:collapse;margin-top:16px;">\n<thead><tr style="background:var(--color-bg-table-header);"><th style="padding:10px 12px;text-align:left;border-bottom:2px solid var(--color-success);font-weight:700;">维度</th><th style="padding:10px 12px;text-align:left;border-bottom:2px solid var(--color-success);font-weight:700;">周度信号</th></tr></thead>\n<tbody>\n'
        for r in rows:
            tbl += f'<tr><td style="padding:8px 12px;border-bottom:1px solid var(--color-border);font-weight:600;">{r["dimension"]}</td><td style="padding:8px 12px;border-bottom:1px solid var(--color-border);">{r["signal"]}</td></tr>\n'
        tbl += '</tbody></table></div>'
    st = '<div class="stats-grid animate-on-scroll">\n'
    for s in stats:
        st += f'  <div class="stat-card {s.get("class","stat-info")}"><div class="stat-value">{s["value"]}</div><div class="stat-label">{s["label"]}</div></div>\n'
    st += '</div>'
    return f'<section id="overview">\n<div class="doc-chapter-label animate-on-scroll">概览</div>\n<h2 class="animate-on-scroll">📋 本周概览</h2>\n{tbl}\n{st}\n</section>'

def render_top5(d):
    cards = ""
    for item in d.get("top5",[]):
        ac = ACCENT_MAP.get(item.get("accent","info"),"var(--color-info)")
        cards += f'<div class="news-card animate-on-scroll" style="--card-accent: {ac};">\n  <div class="news-card-rank">TOP {item["rank"]} · {item.get("label","")}</div>\n  <div class="news-card-title">{item["title"]}</div>\n  <div class="news-card-source">📅 {d.get("date_range","")} · 📎 {item["source"]}</div>\n  <div class="news-card-desc">{item["desc"]}</div>\n  <div class="news-card-why"><strong>关键判断</strong>：{item["why"]}</div>\n</div>\n'
    return f'<section id="top5">\n<div class="doc-chapter-label animate-on-scroll">Top 5</div>\n<h2 class="animate-on-scroll">🏆 本周 Top 5 事件</h2>\n{cards}\n</section>'

def render_insights(d):
    cards = ""
    for item in d.get("insights",[]):
        links = item.get("trend_links",[])
        tl = " · ".join(f'<a href="{l["url"]}" target="_blank">{l["text"]}</a>' for l in links) if links else ""
        cards += f'<div class="insight-card animate-on-scroll">\n  <div class="insight-tag">{item["tag_label"]}</div>\n  <div class="insight-title">{item["title"]}</div>\n  <p style="font-family:var(--font-family-cn);line-height:1.75;font-size:13px;">{item["content"]}</p>\n  <div class="insight-trend">🔗 {tl}</div>\n</div>\n'
    return f'<section id="insight">\n<div class="doc-chapter-label animate-on-scroll">洞察</div>\n<h2 class="animate-on-scroll">💡 周度洞察</h2>\n{cards}\n</section>'

def render_link_insight(d):
    li = d.get("link_insight",{})
    intro = f'<div class="callout callout-purple animate-on-scroll"><strong>{li.get("intro_callout","")}</strong></div>'
    blocks = ""
    for k in ["turning_point","paradox","takeaway"]:
        b = li.get(k,{})
        if b: blocks += f'<div class="callout {b.get("class","callout-info")} animate-on-scroll" style="margin-top:16px;">{b.get("content","")}</div>\n'
    return f'<section id="linkinsight">\n<div class="doc-chapter-label animate-on-scroll">林克的洞察</div>\n<h2 class="animate-on-scroll">🧠 林克的洞察</h2>\n{intro}\n{blocks}\n</section>'

def render_section(sec):
    id_ = sec.get("id","")
    icon = sec.get("icon","")
    title = sec.get("title","")
    co = sec.get("callout","")
    cocl = sec.get("callout_class","callout-info")
    co_html = f'<div class="callout {cocl} animate-on-scroll">{co}</div>' if co else ""
    tbl = sec.get("table",[])
    tbl_html = ""
    if tbl:
        rows = "".join(f'<tr><td>{r.get("date","")}</td><td>{r.get("event","")}</td><td>{r.get("source","")}</td><td>{r.get("importance","")}</td></tr>\n' for r in tbl)
        tbl_html = f'<div class="table-wrap animate-on-scroll">\n<table><thead><tr><th>日期</th><th>事件</th><th>来源</th><th>重要度</th></tr></thead>\n<tbody>{rows}</tbody></table></div>'
    stats = sec.get("stats",[])
    stats_html = ""
    if stats:
        stats_html = '<div class="stats-grid animate-on-scroll">\n' + "".join(f'  <div class="stat-card {s.get("class","stat-info")}"><div class="stat-value">{s["value"]}</div><div class="stat-label">{s["label"]}</div></div>\n' for s in stats) + '</div>'
    return f'<section id="{id_}">\n<div class="doc-chapter-label animate-on-scroll">{icon}</div>\n<h2 class="animate-on-scroll">{icon} {title}</h2>\n{co_html}\n{tbl_html}\n{stats_html}\n</section>'

def render_daily_index(d):
    items = d.get("daily_index",[])
    cards = "".join(f'<div class="daily-item">\n  <div class="daily-item-date">{i["date"]} {i["weekday"]}</div>\n  <a href="{i["url"]}" target="_blank" class="daily-item-link">{i["title"]}</a>\n  <div class="daily-item-kw">{i.get("keywords","")}</div>\n</div>\n' for i in items)
    return f'<section id="dailyindex">\n<div class="doc-chapter-label animate-on-scroll">日报索引</div>\n<h2 class="animate-on-scroll">📅 本周日报索引</h2>\n<div class="daily-index animate-on-scroll">\n{cards}\n</div>\n</section>'

def render_vocab(d):
    items = d.get("vocab",[])
    if not items: return ""
    rows = "".join(f'<tr><td style="font-weight:600;">{i["term"]}</td><td>{i["definition"]}</td><td>{i.get("source","")}</td></tr>\n' for i in items)
    return f'<section id="vocab">\n<div class="doc-chapter-label animate-on-scroll">技术词汇</div>\n<h2 class="animate-on-scroll">📖 技术词汇表</h2>\n<div class="table-wrap animate-on-scroll">\n<table><thead><tr><th>术语</th><th>定义</th><th>出处</th></tr></thead>\n<tbody>{rows}</tbody></table></div>\n</section>'

def render_narrative(d):
    n = d.get("narrative",{})
    if not n: return ""
    intro = f'<div class="callout callout-purple animate-on-scroll"><strong>{n.get("intro_callout","")}</strong></div>'
    blocks = "".join(f'<div class="callout {b.get("class","callout-info")} animate-on-scroll" style="margin-top:16px;">{b.get("content","")}</div>\n' for b in n.get("main_blocks",[]))
    conc = ""
    if n.get("conclusion_callout"):
        conc = f'<hr style="border:none;border-top:2px solid var(--color-success);margin:32px 0;">\n<div class="callout callout-success animate-on-scroll">{n["conclusion_callout"]}</div>'
    return f'<section id="narrative">\n<div class="doc-chapter-label animate-on-scroll">宏观叙事</div>\n<h2 class="animate-on-scroll">🌊 宏观叙事：{n.get("title","")}</h2>\n{intro}\n{blocks}\n{conc}\n</section>'

LEARN_MORE = '''<div style="max-width:var(--content-max);margin:0 auto;padding:16px 20px 48px;">
<div style="background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #E7E5E4;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06)">
  <div style="font-size:16px;font-weight:700;margin-bottom:8px">💡 了解更多</div>
  <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是系统化追踪AI行业动态的项目，覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。</p>
  <a href="https://xiaoxiong20260206.github.io/ai-insight/" target="_blank" style="display:inline-flex;padding:8px 16px;background:linear-gradient(135deg,#059669,#10B981);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">🏠 访问AI洞察首页</a>
</div></div>'''

def render_sidebar(d):
    secs = d.get("sections",{})
    links = ['<a href="#overview" class="toc-link">📋 本周概览</a>',
             '<a href="#top5" class="toc-link">🏆 Top 5 事件</a>',
             '<a href="#insight" class="toc-link">💡 周度洞察</a>',
             '<a href="#linkinsight" class="toc-link">🧠 林克的洞察</a>']
    for k,s in secs.items():
        links.append(f'<a href="#{k}" class="toc-link">{s.get("icon","")} {s.get("title",k)}</a>')
    links.extend(['<a href="#dailyindex" class="toc-link">📅 日报索引</a>',
                  '<a href="#vocab" class="toc-link">📖 技术词汇</a>',
                  '<a href="#narrative" class="toc-link">🌊 宏观叙事</a>'])
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
    css_block = f"<style>\n{base_css}\n\n/* ===== 日报组件层 ===== */\n{rep_css}\n\n/* ===== AI洞察定制层 ===== */\n{cust_css}\n</style>"
    js_block = TEMPLATE_JS_FILE.read_text(encoding="utf-8") if TEMPLATE_JS_FILE.exists() else "<script></script>"
    
    header = f'<header class="doc-header">\n  <div class="header-badge">AI INSIGHT · WEEKLY REPORT · {d["week_num"]}</div>\n  <h1 class="header-title">AI 周报 {d["year"]}年第{d["week_num"]}周</h1>\n  <p class="header-meta"><span>📅 {d["date_range"]}</span><span>📰 覆盖7天日报 · 5板块</span><span>🌐 海外+国内</span></p>\n</header>'
    
    body_secs = [header, render_overview(d), render_top5(d), render_insights(d), render_link_insight(d)]
    for k in ["llm","coding","app","industry","enterprise"]:
        s = d.get("sections",{}).get(k,{})
        if s: body_secs.append(render_section(s))
    body_secs.append(render_daily_index(d))
    v = render_vocab(d)
    if v: body_secs.append(v)
    n = render_narrative(d)
    if n: body_secs.append(n)
    body_secs.append(LEARN_MORE)
    
    footer = f'<div class="doc-footer"><p>🧠 林克（沈浪的AI分身） · AI洞察 · 周报 · {wid}</p><p style="margin-top:4px;">数据来源：AI洞察日报 {d.get("date_range","")} · 5板块</p></div>'
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
    if errs:
        print(f"\n❌ HTML自校验失败 ({len(errs)}):")
        for e in errs: print(f"  • {e}")
        return False
    print(f"\n✅ HTML自校验通过: {sz/1024:.1f}KB + 5板块 + {len(REQUIRED_CLASSES)}个class名 + 了解更多模块")
    return True

def main():
    parser = argparse.ArgumentParser(description="AI周报HTML生成器（从JSON动态生成）")
    parser.add_argument("--date", required=True, help="周号 YYYY-WXX")
    parser.add_argument("--input", required=True, help="JSON文件路径")
    parser.add_argument("--skip-validate", action="store_true", help="跳过HTML自校验")
    args = parser.parse_args()
    wid = args.date
    jp = Path(args.input)
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