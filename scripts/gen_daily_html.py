#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报 HTML 生成器 — 通用版
===========================
解决问题: 900行HTML不应在LLM context里手搓，应脚本化生成。
用法:
  1. LLM生成 data/daily-content-YYYY-MM-DD.json (纯内容，~200行)
  2. 本脚本读取JSON + CSS/JS模板 → 输出完整HTML (~900行)

这样LLM只需输出~200行JSON，而不是~900行HTML，节省75%的context。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_CSS_FILE = BASE_DIR / "templates" / "daily-report-v3.css"
TEMPLATE_JS_FILE = BASE_DIR / "templates" / "daily-report-v3.js"
REPORT_DIR = BASE_DIR / "01-daily-reports"

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ============ 模板提取（首次运行用） ============

def extract_templates_from_html(html_path: str):
    """从现有HTML中提取CSS和JS到模板文件。只需运行一次。"""
    content = Path(html_path).read_text(encoding="utf-8")

    css_start = content.find("<style>")
    css_end = content.find("</style>") + len("</style>")
    css = content[css_start:css_end]

    js_start = content.find("<script>")
    js_end = content.find("</script>") + len("</script>")
    js = content[js_start:js_end]

    templates_dir = BASE_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)

    (templates_dir / "daily-report-v3.css").write_text(css, encoding="utf-8")
    (templates_dir / "daily-report-v3.js").write_text(js, encoding="utf-8")
    print(f"✅ Extracted CSS ({len(css)} chars) and JS ({len(js)} chars) to templates/")


# ============ 新闻条目渲染 ============

def render_news_item(item: dict) -> str:
    """渲染单条新闻"""
    tag_map = {
        "hot": '<span class="news-tag tag-hot">HOT</span>',
        "new": '<span class="news-tag tag-new">NEW</span>',
        "cn": '<span class="news-tag tag-cn">🇨🇳</span>',
        "funding": '<span class="news-tag tag-funding">💰</span>',
        "policy": '<span class="news-tag tag-policy">📋</span>',
        "practice": '<span class="news-tag tag-practice">⚙️</span>',
    }
    tag = tag_map.get(item.get("tag", "new"), tag_map["new"])

    # 标题链接：url为空时显示纯文本
    url = item.get('url', '')
    if url:
        title_html = f'<a href="{url}" target="_blank">{item["title"]}</a>'
    else:
        title_html = item["title"]

    # 小红书原帖链接（可选）
    xhs_url = item.get('xhs_url', '')
    xhs_link_html = ''
    if xhs_url:
        xhs_link_html = f' · <a href="{xhs_url}" target="_blank" style="color:#ff2442;font-size:0.85em">📕小红书原帖</a>'

    # 简洁模式：只有标题和摘要
    if "details" not in item:
        return f'''
                <div class="news-item">
                    {tag}
                    <div class="news-title">{title_html}</div>
                    <div class="news-source">{item['source']}{xhs_link_html}</div>
                    <div class="news-summary-compact">{item.get('summary', '')}</div>
                </div>'''

    # 详细模式：有核心发现/关键数据/影响判断
    d = item["details"]
    label_class = "china" if item.get("tag") == "cn" else ""
    chip_class = " china" if item.get("tag") == "cn" else ""

    chips_html = ""
    # 兼容 chips(数组) 和 highlight(字符串) 两种格式
    # highlight 字符串用 | 分隔时拆为多个chip
    raw_chips = d.get("chips")
    if not raw_chips and d.get("highlight"):
        hl = d["highlight"]
        raw_chips = [c.strip() for c in hl.split("|") if c.strip()] if "|" in hl else [hl]
    chip_items = raw_chips or []
    if chip_items:
        chips = "".join(f'<span class="news-data-chip{chip_class}">{c}</span>' for c in chip_items)
        chips_html = f'''
                        <div class="news-detail-row">
                            <span class="news-detail-label {label_class}">关键数据</span>
                            <span class="news-detail-value"><div class="news-data-chips">{chips}</div></span>
                        </div>'''

    return f'''
                <div class="news-item">
                    {tag}
                    <div class="news-title">{title_html}</div>
                    <div class="news-source">{item['source']}{xhs_link_html}</div>
                    <div class="news-detail">
                        <div class="news-detail-row">
                            <span class="news-detail-label {label_class}">核心发现</span>
                            <span class="news-detail-value">{d['finding']}</span>
                        </div>{chips_html}
                        <div class="news-detail-row">
                            <span class="news-detail-label {label_class}">影响判断</span>
                            <span class="news-detail-value">{d.get('impact', '')}</span>
                        </div>
                    </div>
                </div>'''


def render_section(section: dict) -> str:
    """渲染一个板块的所有新闻"""
    parts = []
    if section.get("overseas"):
        parts.append('                <div class="sub-header">🌏 海外</div>')
        for item in section["overseas"]:
            parts.append(render_news_item(item))
    if section.get("china"):
        parts.append('                <div class="sub-header">🇨🇳 国内</div>')
        for item in section["china"]:
            parts.append(render_news_item(item))
    return "\n".join(parts)


# ============ 深度聚焦卡片 ============

def normalize_deep_focus(raw: dict) -> dict:
    """将 focus / deep_focus 的不同结构归一化为标准格式 {title, paragraphs[], takeaway}"""
    title = raw.get("title", "")
    # 已经是标准格式
    if "paragraphs" in raw:
        return {"title": title, "paragraphs": raw["paragraphs"], "takeaway": raw.get("takeaway", "")}
    # 旧格式：只有 summary 字符串 → 拆分
    summary = raw.get("summary", "")
    takeaway = ""
    # 尝试提取 Takeaway
    for sep in ["Takeaway：", "Takeaway:", "TAKEAWAY：", "TAKEAWAY:"]:
        if sep in summary:
            parts = summary.split(sep, 1)
            summary = parts[0].strip()
            takeaway = parts[1].strip()
            break
    # 按句号拆段（至少2段）
    sentences = [s.strip() for s in summary.replace("。", "。\n").split("\n") if s.strip()]
    if len(sentences) <= 1:
        paragraphs = [summary] if summary else []
    else:
        # 合并短句为2-4段
        paragraphs = []
        buf = ""
        for s in sentences:
            buf += s
            if len(buf) >= 60:
                paragraphs.append(buf)
                buf = ""
        if buf:
            paragraphs.append(buf)
    return {"title": title, "paragraphs": paragraphs, "takeaway": takeaway}


def render_deep_focus(df: dict, theme: str = "") -> str:
    """渲染深度聚焦卡片（兼容 focus 和 deep_focus 两种字段结构）"""
    ndf = normalize_deep_focus(df)
    theme_class = f" {theme}" if theme else ""
    takeaway_theme = f' {theme}' if theme else ""
    label_color = ""
    if theme == "orange-theme":
        label_color = " orange"
    elif theme == "china-theme":
        label_color = " china"

    takeaway_html = ""
    if ndf['takeaway']:
        takeaway_html = f'''\n                    <div class="deep-focus-takeaway{takeaway_theme}">
                        <div class="deep-focus-takeaway-label{label_color}">💡 TAKEAWAY</div>
                        <div class="deep-focus-takeaway-text">{ndf['takeaway']}</div>
                    </div>'''

    return f'''
            <div class="deep-focus-card">
                <div class="deep-focus-header{theme_class}">
                    <div>
                        <div class="deep-focus-label">💡 深度聚焦</div>
                        <div class="deep-focus-title">{ndf['title']}</div>
                    </div>
                </div>
                <div class="deep-focus-body">
                    {''.join(f"<p>{p}</p>" for p in ndf['paragraphs'])}{takeaway_html}
                </div>
            </div>'''


# ============ 热度趋势 ============

def render_heat_trend(heat: dict) -> str:
    """渲染热度趋势卡片"""
    rows = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
    for i, t in enumerate(heat["topics"]):
        fills = int(t.get("score", 7))
        empties = 10 - fills
        bar = '<span class="heat-bar-fill"></span>' * fills + '<span class="heat-bar-empty"></span>' * empties
        trend_class = t.get("trend_class", "up")
        trend_label = t.get("trend_label", "📈 攀升")
        rows.append(f'''                        <tr>
                            <td>{medals[i]}</td>
                            <td><strong>{t['name']}</strong></td>
                            <td><div class="heat-bar">{bar}</div></td>
                            <td>{t['days']}天</td>
                            <td><span class="heat-trend-tag {trend_class}">{trend_label}</span></td>
                            <td>{t['signal']}</td>
                        </tr>''')

    return f'''
        <div class="heat-card">
            <div class="heat-header">
                <div class="heat-header-label">🔥 热度趋势</div>
                <div class="heat-header-title">{heat['title']}</div>
            </div>
            <div class="heat-body">
                <table class="heat-table">
                    <thead><tr><th>排名</th><th>话题</th><th>热度</th><th>天数</th><th>趋势</th><th>核心信号</th></tr></thead>
                    <tbody>
{chr(10).join(rows)}
                    </tbody>
                </table>
                <p>{heat['summary']}</p>
            </div>
        </div>'''


# ============ 数据速览表格 ============

def render_data_table(data: list) -> str:
    rows = "\n".join(
        f'                    <tr><td>{d["metric"]}</td><td><strong>{d["value"]}</strong></td><td>{d["note"]}</td></tr>'
        for d in data
    )
    return f'''
        <div class="section-card" style="margin-top:20px">
            <div class="section-header"><span class="num">📊</span> 数据速览</div>
            <table class="data-table">
                <thead><tr><th>指标</th><th>数值</th><th>变化/说明</th></tr></thead>
                <tbody>
{rows}
                </tbody>
            </table>
        </div>'''


# ============ 明日/下周预览 ============

def render_preview(events: list) -> str:
    if not events:
        return ""
    items = []
    for e in events:
        # 兼容两种格式: preview_events {name,desc,color} 和 watch_list [string]
        if isinstance(e, str):
            # 从字符串中提取名称和描述
            if " - " in e:
                parts = e.split(" - ", 1)
                name = parts[0].strip()
                desc = parts[1].strip()
            elif "（" in e:
                parts = e.split("（", 1)
                name = parts[0].strip()
                desc = "（" + parts[1]
            else:
                name = e[:30]
                desc = e
            # 智能检测紧迫度: 今天/明天的事件用强调色
            lower = e.lower()
            if any(k in lower for k in ["今天", "今日", "3月13"]):
                color = "var(--color-danger)"
                border_color = "var(--color-danger)"
                icon = "🔴"
            elif any(k in lower for k in ["明天", "明日", "3月14"]):
                color = "var(--color-warning)"
                border_color = "var(--color-warning)"
                icon = "🟡"
            elif any(k in lower for k in ["持续", "监测", "后续"]):
                color = "var(--color-info)"
                border_color = "var(--color-info)"
                icon = "🔵"
            else:
                color = "var(--color-success)"
                border_color = "var(--color-success)"
                icon = "🟢"
        else:
            color_key = e.get("color", "success")
            color = f'var(--color-{color_key})'
            border_color = color
            name = e.get("name", "")
            desc = e.get("desc", "")
            icon = {"danger": "🔴", "warning": "🟡", "info": "🔵"}.get(color_key, "🟢")
        items.append(f'''                <div style="padding:12px 16px;background:var(--color-bg);border-radius:var(--radius-md);border:1px solid var(--color-border-light);border-left:3px solid {border_color};transition:all .2s">
                    <div style="font-size:13px;font-weight:700;color:{color};display:flex;align-items:center;gap:6px">{icon} {name}</div>
                    <div style="font-size:12px;color:var(--color-text-muted);margin-top:4px;line-height:1.5">{desc}</div>
                </div>''')
    return f'''
        <div class="section-card">
            <div class="section-header"><span class="num">📌</span> 明日/下周值得关注</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
{chr(10).join(items)}
            </div>
        </div>'''


# ============ 主生成函数 ============

def generate_html(data: dict) -> str:
    """从JSON数据生成完整HTML"""
    date_str = data["date"]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[date_obj.weekday()]
    month_str = date_obj.strftime("%Y-%m")

    # 读CSS/JS模板
    css_block = TEMPLATE_CSS_FILE.read_text(encoding="utf-8") if TEMPLATE_CSS_FILE.exists() else "<style></style>"
    js_block = TEMPLATE_JS_FILE.read_text(encoding="utf-8") if TEMPLATE_JS_FILE.exists() else "<script></script>"

    # 覆盖率
    cov = data.get("coverage", {})
    overseas_count = cov.get("overseas", 10)
    china_count = cov.get("china", 8)
    total = overseas_count + china_count
    overseas_pct = round(overseas_count / total * 100) if total else 50
    china_pct = 100 - overseas_pct

    # 概览
    overview_items = []
    for ov in data.get("overview", []):
        span = f' style="grid-column: span 2;"' if ov.get("span2") else ""
        label_class = f' class="{ov["label_class"]}"' if ov.get("label_class") else ""
        overview_items.append(f'''                <div class="overview-item"{span}>
                    <div class="overview-item-header"><span class="overview-item-icon">{ov['icon']}</span><span class="overview-item-label"{label_class}>{ov['label']}</span></div>
                    <div class="overview-headline">{ov['headline']}</div>
                    <div class="overview-item-text">{ov['text']}</div>
                </div>''')

    # Tab面板
    tabs = data.get("tabs", [])
    tab_names = [("🧠", "大模型", "foundation"), ("⌨️", "AI Coding", "coding"),
                 ("📱", "AI 应用", "application"), ("🏭", "AI 行业", "industry"),
                 ("🔄", "企业转型", "enterprise")]
    tab_buttons = []
    tab_panels = []
    for i, (icon, name, tid) in enumerate(tab_names):
        active = " active" if i == 0 else ""
        selected = "true" if i == 0 else "false"
        orange = " orange" if tid == "enterprise" else ""
        tab_buttons.append(f'            <button class="tab-btn{orange}" role="tab" aria-selected="{selected}" data-tab="{tid}">{icon} {name}</button>')

        tab_data = tabs[i] if i < len(tabs) else {}
        section_html = render_section(tab_data.get("news", {}))
        # 兼容 deep_focus 和 focus 两种字段名
        df_data = tab_data.get("deep_focus") or tab_data.get("focus")
        deep_focus_html = render_deep_focus(df_data, tab_data.get("theme", "")) if df_data else ""
        # pattern insight is optional
        pi_html = tab_data.get("pattern_insight_html", "")

        tab_panels.append(f'''
        <article id="{tid}" class="tab-panel{active}">
            <div class="section-card">
                <div class="section-header"><span class="num">1</span> 最近动态</div>
{section_html}
            </div>
{deep_focus_html}
{pi_html}
        </article>''')

    # 组装
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 日报 - {date_str} (v3.2)</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%231A7F37'/><circle cx='16' cy='14' r='6' fill='none' stroke='white' stroke-width='2'/><path d='M12 12h8M16 10v4M10 22c0-3.3 2.7-6 6-6s6 2.7 6 6' fill='none' stroke='white' stroke-width='2' stroke-linecap='round'/></svg>">
    {css_block}
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-badge">📡 林克的AI洞察项目 - AI日报</div>
            <div class="header-title">AI 日报 <span class="version-badge">v3.2</span></div>
            <div class="header-date">{date_obj.strftime("%Y年%-m月%-d日")} {weekday} | 五大板块：大模型 · AI Coding · AI应用 · AI行业 · 企业转型</div>
        </div>

        <div class="coverage-bar">
            <span class="label">📊 覆盖均衡</span>
            <div class="bar">
                <div class="bar-overseas" style="width:{overseas_pct}%"></div>
                <div class="bar-china" style="width:{china_pct}%"></div>
            </div>
            <div class="stats">
                <span class="stat-overseas">🌏 海外 {overseas_count}条</span>
                <span class="stat-china">🇨🇳 国内 {china_count}条</span>
            </div>
        </div>

        <div class="overview">
            <div class="overview-title">📋 全文概览</div>
            <div class="overview-grid five-cols">
{chr(10).join(overview_items)}
            </div>
        </div>

{render_heat_trend(data.get("heat_trend", {}))}

        <nav class="tab-nav" role="tablist">
{chr(10).join(tab_buttons)}
        </nav>

{chr(10).join(tab_panels)}

{render_data_table(data.get("data_snapshot", []))}

{render_preview(data.get('preview_events') or data.get('watch_list', []))}

        <div style="margin-top:24px;background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #F5F5F4;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06),0 1px 2px rgba(31,35,40,.04)">
            <div style="font-size:16px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px">💡 了解更多</div>
            <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">
                我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。
            </p>
            <a href="https://xiaoxiong20260206.github.io/ai-insight/" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#059669 0%,#10B981 100%);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
                🏠 访问AI洞察首页
            </a>
        </div>
    </div>

    {js_block}
</body>
</html>
'''


# ============ CLI入口 ============

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python gen_daily_html.py <date>          # 从 data/daily-content-<date>.json 生成HTML")
        print("  python gen_daily_html.py --extract <html> # 从现有HTML提取CSS/JS模板")
        sys.exit(1)

    if sys.argv[1] == "--extract":
        extract_templates_from_html(sys.argv[2])
        return

    date_str = sys.argv[1]
    json_path = BASE_DIR / "data" / f"daily-content-{date_str}.json"

    if not json_path.exists():
        print(f"❌ 找不到内容JSON: {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["date"] = date_str

    html = generate_html(data)

    month_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
    out_dir = REPORT_DIR / month_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}-v3.html"
    out_path.write_text(html, encoding="utf-8")

    # 同时生成redirect文件
    redirect_path = out_dir / f"{date_str}.html"
    if not redirect_path.exists():
        redirect_path.write_text(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AI 日报 - {date_str}</title>
    <meta http-equiv="refresh" content="0;url={date_str}-v3.html">
    <style>body{{font-family:-apple-system,system-ui,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#F8FAFB;color:#57534E}}a{{color:#059669}}</style>
</head>
<body>
    <p>正在跳转至 <a href="{date_str}-v3.html">AI 日报 {date_str} (v3.1)</a>...</p>
</body>
</html>
''', encoding="utf-8")
        print(f"  + Redirect: {redirect_path.name}")

    print(f"✅ Generated: {out_path}")
    print(f"   {len(html):,} chars, {html.count(chr(10)):,} lines")


if __name__ == "__main__":
    main()
