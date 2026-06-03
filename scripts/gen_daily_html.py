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

# 从 config.py SSoT 读取 URL
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import INTERNAL_PAGES_BASE

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_CSS_FILE = BASE_DIR / "templates" / "daily-report-v3.css"
TEMPLATE_JS_FILE = BASE_DIR / "templates" / "daily-report-v3.js"
REPORT_DIR = BASE_DIR / "01-daily-reports"

# ===== 清爽调研风格引用（动态读取，保持同步）=====
# 公共CSS变量+基础样式从 qingshuang-research-style skill 引用
# 项目定制样式从本地 templates/ 读取
QINGSHUANG_SKILL_PATH = Path("/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/skills/qingshuang-research-style")
QINGSHUANG_BASE_CSS = QINGSHUANG_SKILL_PATH / "references" / "base-styles.css"
AI_INSIGHT_CUSTOM_CSS = BASE_DIR / "templates" / "ai-insight-custom.css"

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
    """渲染单条新闻（v5.1 — 紧凑排版：标题+来源合并一行，NEW标签inline化）"""
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
        xhs_link_html = f' · <a href="{xhs_url}" target="_blank" style="color:#ff2442;font-size:0.85em">📕小红书</a>'

    # 微信公众号原文链接（可选）
    wx_url = item.get('wx_url', '')
    wx_link_html = ''
    if wx_url:
        wx_link_html = f' · <a href="{wx_url}" target="_blank" style="color:#07C160;font-size:0.85em">💬微信</a>'

    # 来源（inline 跟在标题后）
    source_inline = f'<span class="news-source-inline">{item["source"]}{xhs_link_html}{wx_link_html}</span>'

    # 简洁模式：只有标题和摘要
    if "details" not in item:
        return f'''
                <div class="news-item">
                    <div class="news-title-row">{tag} {title_html} {source_inline}</div>
                    <div class="news-summary-compact">{item.get('summary', '')}</div>
                </div>'''

    # 详细模式：有核心发现/关键数据/影响判断
    d = item.get("details") or {}
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
                    <div class="news-title-row">{tag} {title_html} {source_inline}</div>
                    <div class="news-detail">
                        <div class="news-detail-row">
                            <span class="news-detail-label {label_class}">核心发现</span>
                            <span class="news-detail-value">{d.get('finding', '')}</span>
                        </div>{chips_html}
                        <div class="news-detail-row">
                            <span class="news-detail-label {label_class}">影响判断</span>
                            <span class="news-detail-value">{d.get('impact', '')}</span>
                        </div>
                    </div>
                </div>'''


def render_section(section) -> str:
    """渲染一个板块的所有新闻（兼容 {overseas:[], china:[]} 和 flat list 两种格式）"""
    parts = []
    if isinstance(section, list):
        # 扁平列表格式，按 region 分组
        overseas = [item for item in section if item.get("region") != "china"]
        china = [item for item in section if item.get("region") == "china"]
        if overseas:
            parts.append('                <div class="sub-header">🌏 海外</div>')
            for item in overseas:
                parts.append(render_news_item(item))
        if china:
            parts.append('                <div class="sub-header">🇨🇳 国内</div>')
            for item in china:
                parts.append(render_news_item(item))
    elif isinstance(section, dict):
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
    """渲染热度趋势卡片（v9.13: 兼容 topics[] 和 rising/stable/cooling 两种格式）"""
    # v9.13: 兼容 rising/stable/cooling 字典格式，自动转换为 topics 数组
    topics = heat.get("topics", [])
    if not topics and any(k in heat for k in ("rising", "stable", "cooling")):
        for name in heat.get("rising", []):
            topics.append({"name": name, "score": 8, "days": 1, "trend_class": "up", "trend_label": "📈 攀升", "signal": "今日新热点"})
        for name in heat.get("stable", []):
            topics.append({"name": name, "score": 6, "days": 3, "trend_class": "stable", "trend_label": "➡️ 持平", "signal": "持续关注中"})
        for name in heat.get("cooling", []):
            topics.append({"name": name, "score": 4, "days": 5, "trend_class": "down", "trend_label": "📉 降温", "signal": "热度回落"})

    rows = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
    # v9.8修复: 超出 medals 列表长度时用数字代替，防止 IndexError
    for i, t in enumerate(topics):
        fills = int(t.get("score", 7))
        empties = 10 - fills
        bar = '<span class="heat-bar-fill"></span>' * fills + '<span class="heat-bar-empty"></span>' * empties
        trend_class = t.get("trend_class", "up")
        trend_label = t.get("trend_label", "📈 攀升")
        rows.append(f'''                        <tr>
                            <td>{medals[i] if i < len(medals) else str(i + 1)}</td>
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
                <div class="heat-header-title">{heat.get('title', '')}</div>
            </div>
            <div class="heat-body">
                <table class="heat-table">
                    <thead><tr><th>排名</th><th>话题</th><th>热度</th><th>天数</th><th>趋势</th><th>核心信号</th></tr></thead>
                    <tbody>
{chr(10).join(rows)}
                    </tbody>
                </table>
                <p>{heat.get('summary', '')}</p>
            </div>
        </div>'''


# ============ 深度洞察 / 林克自述 ============

def render_capability_update(text: str) -> str:
    """渲染 capability_update（林克自述 / 深度洞察）卡片（v9.13新增）"""
    if not text:
        return ""
    # 将换行符转为 <br>，处理 **粗体** Markdown
    import re
    html_text = text.replace("\n\n", "</p><p style='margin:8px 0 0 0'>")
    html_text = html_text.replace("\n", "<br>")
    html_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_text)
    return f'''
        <div class="insight-block animate-on-scroll">
            <div class="insight-block-title">🤖 深度洞察</div>
            <div class="insight-block-body">
                <p style="margin:0">{html_text}</p>
            </div>
        </div>'''


# ============ 数据速览表格 ============

def render_data_table(data: list) -> str:
    rows = "\n".join(
        f'                    <tr><td>{d["metric"]}</td><td><strong>{d["value"]}</strong></td><td>{d.get("note", d.get("context", ""))}</td></tr>'
        for d in data
    )
    return f'''
        <div class="section-card">
            <div class="section-header"><span class="num">📊</span> 数据速览</div>
            <div class="data-table-wrap">
                <table class="data-table">
                    <thead><tr><th>指标</th><th>数值</th><th>变化/说明</th></tr></thead>
                    <tbody>
{rows}
                    </tbody>
                </table>
            </div>
        </div>'''


# ============ 明日/下周预览 ============

def render_preview(events: list) -> str:
    if not events:
        return ""
    items = []
    for e in events:
        # 格式1: {category, items: [...]} — 按分类展示
        if isinstance(e, dict) and "category" in e and "items" in e:
            cat = e.get("category", "")
            sub_items = e.get("items", [])
            if not sub_items:
                continue
            # 按category选颜色
            if "日期" in cat or "📅" in cat:
                color = "var(--color-warning)"
                border_color = "var(--color-warning)"
                icon = "📅"
            elif "指标" in cat or "📊" in cat:
                color = "var(--color-info)"
                border_color = "var(--color-info)"
                icon = "📊"
            elif "信号" in cat or "🔍" in cat:
                color = "var(--color-success)"
                border_color = "var(--color-success)"
                icon = "🔍"
            else:
                color = "var(--color-success)"
                border_color = "var(--color-success)"
                icon = "📌"
            desc_html = "".join(f'<div style="margin-top:3px">• {item}</div>' for item in sub_items)
            # 如果category本身已含emoji，则不再重复加icon
            cat_display = cat if any(ord(c) > 127 for c in cat[:2]) else f"{icon} {cat}"
            items.append(f'''                <div style="padding:12px 16px;background:var(--color-bg);border-radius:var(--radius-md);border:1px solid var(--color-border-light);border-left:3px solid {border_color};transition:all .2s">
                    <div style="font-size:13px;font-weight:700;color:{color};display:flex;align-items:center;gap:6px">{cat_display}</div>
                    <div style="font-size:12px;color:var(--color-text-muted);margin-top:4px;line-height:1.5">{desc_html}</div>
                </div>''')
        # 格式2: str — 单条文本
        elif isinstance(e, str):
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
            lower = e.lower()
            if any(k in lower for k in ["今天", "今日"]):
                color = "var(--color-danger)"; border_color = color; icon = "🔴"
            elif any(k in lower for k in ["明天", "明日"]):
                color = "var(--color-warning)"; border_color = color; icon = "🟡"
            elif any(k in lower for k in ["持续", "监测", "后续"]):
                color = "var(--color-info)"; border_color = color; icon = "🔵"
            else:
                color = "var(--color-success)"; border_color = color; icon = "🟢"
            items.append(f'''                <div style="padding:12px 16px;background:var(--color-bg);border-radius:var(--radius-md);border:1px solid var(--color-border-light);border-left:3px solid {border_color};transition:all .2s">
                    <div style="font-size:13px;font-weight:700;color:{color};display:flex;align-items:center;gap:6px">{icon} {name}</div>
                    <div style="font-size:12px;color:var(--color-text-muted);margin-top:4px;line-height:1.5">{desc}</div>
                </div>''')
        # 格式3: {name, desc, color} — 旧格式兼容
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
    if not items:
        return ""
    return f'''
        <div class="section-card">
            <div class="section-header"><span class="num">📌</span> 明日/下周值得关注</div>
            <div class="watch-grid">
{chr(10).join(items)}
            </div>
        </div>'''


# ============ 主生成函数 (v4.0 — 清爽调研风格，长页面+左侧TOC) ============

def generate_html(data: dict) -> str:
    """从JSON数据生成完整HTML（清爽调研风格 v5.0 × 日报）"""
    date_str = data.get("date") or data.get("date_str") or ""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[date_obj.weekday()]

    # 读CSS模板：公共层(qingshuang skill) + 定制层(本地)
    # v5.0: 改为引用关系，清爽调研风格更新时自动同步
    base_css = ""
    if QINGSHUANG_BASE_CSS.exists():
        base_css = QINGSHUANG_BASE_CSS.read_text(encoding="utf-8")
        print(f"  ✅ CSS公共层: 从 qingshuang-research-style 引用 ({len(base_css)} chars)")
    else:
        # 回退：如果 qingshuang skill 不存在，使用本地备份
        if TEMPLATE_CSS_FILE.exists():
            base_css = TEMPLATE_CSS_FILE.read_text(encoding="utf-8")
            print(f"  ⚠️ CSS回退: 使用本地备份 (qingshuang skill不存在)")
        else:
            base_css = "<style></style>"
    
    custom_css = ""
    if AI_INSIGHT_CUSTOM_CSS.exists():
        custom_css = AI_INSIGHT_CUSTOM_CSS.read_text(encoding="utf-8")
    
    # 日报组件样式（中间层：布局、sidebar、news-item、deep-focus 等日报专用选择器）
    # 注意：daily-report-v3.css 本身包裹了 <style>...</style>，需剥掉再嵌入，避免双重嵌套
    report_css = ""
    if TEMPLATE_CSS_FILE.exists():
        raw = TEMPLATE_CSS_FILE.read_text(encoding="utf-8")
        # 剥掉首尾的 <style> / </style> 包装标签
        import re as _re
        raw = _re.sub(r'^\s*<style[^>]*>\s*', '', raw)
        raw = _re.sub(r'\s*</style>\s*$', '', raw)
        report_css = raw
    
    # 合并：公共层变量+基础样式 + 日报组件样式 + 定制层组件样式
    css_combined = f"<style>\n{base_css}\n\n/* ===== 日报组件层 ===== */\n{report_css}\n\n/* ===== AI洞察定制层 ===== */\n{custom_css}\n</style>"
    css_block = css_combined
    
    js_block = TEMPLATE_JS_FILE.read_text(encoding="utf-8") if TEMPLATE_JS_FILE.exists() else "<script></script>"

    # 覆盖率（兼容 dict 和字符串两种格式）
    cov = data.get("coverage", {})
    if isinstance(cov, dict):
        overseas_count = cov.get("overseas", cov.get("overseas_count", 10))
        china_count = cov.get("china", cov.get("china_count", cov.get("domestic", 8)))
    else:
        # coverage 是时间窗口字符串时，从 meta.data_sources 推断
        meta_ds = data.get("meta", {}).get("data_sources", {})
        overseas_count = meta_ds.get("overseas_search", 10)
        china_count = meta_ds.get("weixin_search", 0) + meta_ds.get("weixin_direct_cite", 0)
        if china_count == 0:
            china_count = 8
    total = overseas_count + china_count
    overseas_pct = round(overseas_count / total * 100) if total else 50
    china_pct = 100 - overseas_pct

    # 概览卡片
    overview_items = []
    for ov in data.get("overview", []):
        # 兼容两种schema: {icon,label,headline,text} 和 {tab,emoji,summary}
        icon = ov.get('icon', ov.get('emoji', '📌'))
        label = ov.get('label', ov.get('tab', ''))
        text = ov.get('text', ov.get('summary', ''))
        span = ' style="grid-column: span 2;"' if ov.get("span2") else ""
        label_class = f' class="{ov["label_class"]}"' if ov.get("label_class") else ""
        # v5.1: 去掉 overview-headline（截断显示不好看），summary 已完整展示
        overview_items.append(f'''                <div class="overview-item animate-on-scroll"{span}>
                    <div class="overview-item-header"><span class="overview-item-icon">{icon}</span><span class="overview-item-label"{label_class}>{label}</span></div>
                    <div class="overview-item-text">{text}</div>
                </div>''')

    # 五大板块 Sections — 从 Tab 改为锚点 Section
    tabs = data.get("tabs", [])
    tab_defs = [
        ("🧠", "大模型", "llm"),
        ("⌨️", "AI Coding", "coding"),
        ("📱", "AI 应用", "app"),
        ("🏭", "AI 行业", "industry"),
        ("🔄", "企业AI转型", "enterprise"),
    ]

    # === 验证 ===
    if len(tabs) != 5:
        print(f"  ⚠️ 警告: JSON包含{len(tabs)}个tab，期望5个。缺失板块将渲染为空。")
        print(f"     期望: {[n for _, n, _ in tab_defs]}")

    empty_tabs = []
    for i, (icon, name, tid) in enumerate(tab_defs):
        if i < len(tabs):
            news = tabs[i].get("news", {})
            # 兼容两种schema: {overseas:[], china:[]} 或 flat list
            if isinstance(news, list):
                count = len(news)
            else:
                count = len(news.get("overseas", [])) + len(news.get("china", []))
            if count == 0:
                empty_tabs.append(name)
        else:
            empty_tabs.append(name)
    if empty_tabs:
        print(f"  ⚠️ 警告: 以下板块无新闻条目: {', '.join(empty_tabs)}")

    # 生成 Section HTML
    section_blocks = []
    for i, (icon, name, tid) in enumerate(tab_defs):
        tab_data = tabs[i] if i < len(tabs) else {}
        section_html = render_section(tab_data.get("news", {}))
        df_data = tab_data.get("deep_focus") or tab_data.get("focus")
        deep_focus_html = render_deep_focus(df_data, tab_data.get("theme", "")) if df_data else ""
        pi_html = tab_data.get("pattern_insight_html", "") or tab_data.get("pattern_insight", "")
        # v11.0: pi-card兜底 — 内容缺失或结构不完整时用默认模板
        if not pi_html or len(pi_html) < 50 or "pi-card" not in pi_html:
            pi_html = f'<div class="pi-card"><div class="pi-title">规律洞察</div><div class="pi-content">本板块暂无规律洞察，关注后续更新。</div></div>'

        section_blocks.append(f'''
            <!-- ===== {name} ===== -->
            <section id="{tid}" class="report-section animate-on-scroll">
                <div class="doc-chapter-label">{icon} {name}</div>
                <div class="board-section">
                    <div class="board-header">
                        <span class="board-badge">1</span> 最近动态
                    </div>
{section_html}
                </div>
{deep_focus_html}
{pi_html}
            </section>''')

    # 数据速览 & 预览 & 深度洞察
    data_table_html = render_data_table(data.get("data_snapshot", []))
    preview_html = render_preview(data.get('preview_events') or data.get('watch_list', []))
    capability_html = render_capability_update(data.get("capability_update", ""))

    date_display = date_obj.strftime("%Y年%-m月%-d日")

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 日报 · {date_str} | AI洞察</title>
    <meta name="description" content="AI洞察日报 {date_str}：大模型、AI Coding、AI应用、AI行业、企业AI转型五大板块动态">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23059669'/><text x='6' y='23' font-size='18' fill='white'>📡</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <noscript><style>.animate-on-scroll{{opacity:1!important;transform:none!important;}}</style></noscript>
    {css_block}
</head>
<body>
<a class="skip-to-content" href="#main-content">跳到主内容</a>

<div class="layout-wrapper">
    <!-- SIDEBAR TOC -->
    <nav class="sidebar-nav sidebar-collapsed" id="sidebar" aria-label="目录导航">
        <div class="sidebar-doc-title">AI 日报 · {date_str}</div>
        <div class="toc-section">
            <div class="toc-group-label">目录</div>
            <a href="#overview"   class="toc-link">📋 全文概览</a>
            <a href="#heat"       class="toc-link">🔥 热度趋势</a>
            <a href="#llm"        class="toc-link">🧠 大模型</a>
            <a href="#coding"     class="toc-link">⌨️ AI Coding</a>
            <a href="#app"        class="toc-link">📱 AI 应用</a>
            <a href="#industry"   class="toc-link">🏭 AI 行业</a>
            <a href="#enterprise" class="toc-link">🔄 企业AI转型</a>
            <a href="#data"       class="toc-link">📊 数据速览</a>
            <a href="#watch"      class="toc-link">📌 明日关注</a>
        </div>
        <div class="reading-progress-wrap">
            <div class="reading-progress-label">阅读进度</div>
            <div class="reading-progress-track">
                <div class="reading-progress-fill" id="readingProgress"></div>
            </div>
        </div>
    </nav>
    <button class="sidebar-collapse-btn collapsed-pos" id="collapseBtn" title="展开导航" aria-label="展开导航">»</button>

    <!-- MAIN CONTENT -->
    <main class="content-area" id="main-content">
        <div class="content-inner">

            <!-- HEADER -->
            <header class="doc-header">
                <div class="header-badge">AI INSIGHT · DAILY REPORT</div>
                <h1 class="header-title">AI 日报 <span class="version-badge">v4.0</span></h1>
                <div class="header-meta">
                    <span>📅 {date_display} {weekday}</span>
                    <span>🌐 海外 {overseas_count}条 · 国内 {china_count}条</span>
                    <span>📊 五大板块：大模型 · AI Coding · AI应用 · AI行业 · 企业转型</span>
                </div>
            </header>

            <!-- COVERAGE BAR -->
            <div class="coverage-bar animate-on-scroll">
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

            <!-- OVERVIEW -->
            <section id="overview" class="report-section">
                <div class="overview animate-on-scroll">
                    <div class="overview-title">📋 全文概览</div>
                    <div class="overview-grid five-cols">
{chr(10).join(overview_items)}
                    </div>
                </div>
            </section>

            <!-- HEAT TREND -->
            <section id="heat" class="report-section animate-on-scroll">
{render_heat_trend(data.get("heat_trend", {}))}
            </section>

            <!-- FIVE BOARDS -->
{chr(10).join(section_blocks)}

            <!-- DATA SNAPSHOT -->
            <section id="data" class="report-section animate-on-scroll">
{data_table_html}
            </section>

            <!-- WATCH LIST -->
            <section id="watch" class="report-section animate-on-scroll">
{preview_html}
            </section>

            <!-- CAPABILITY UPDATE / DEEP INSIGHT -->
{capability_html}

            <!-- FOOTER -->
            <footer class="doc-footer animate-on-scroll">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <img src="link-avatar-small.webp" alt="林克" style="width:36px;height:36px;border-radius:50%;border:1.5px solid rgba(5,150,105,0.3);object-fit:cover">
                    <span>我是 <strong>林克</strong>，沈浪的AI分身。
                    <a href="{INTERNAL_PAGES_BASE}/" target="_blank">🏠 访问AI洞察首页</a></span>
                </div>
                <p style="margin-top:6px">AI洞察 · 系统化追踪AI行业动态 · 五大板块每日更新</p>
            </footer>

        </div>
    </main>
</div>

<button class="scroll-to-top" id="scrollToTop" aria-label="回到顶部">↑</button>

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
    <p>正在跳转至 <a href="{date_str}-v3.html">AI 日报 {date_str} (v3.2)</a>...</p>
</body>
</html>
''', encoding="utf-8")
        print(f"  + Redirect: {redirect_path.name}")

    print(f"✅ Generated: {out_path}")
    print(f"   {len(html):,} chars, {html.count(chr(10)):,} lines")

    # ============ 关键板块渲染完整性验证 ============
    warnings = []
    hard_errors = []

    import re as _re

    # 0. HTML文件大小底线 — <50KB = 空壳/严重缺失
    if len(html) < 50000:
        hard_errors.append(f"❌ [致命] HTML仅 {len(html):,} chars (<50KB底线)，内容严重缺失")
    
    # 0.1 {{message}}占位符扫描 — 禁止泄露到HTML
    if "{{message}}" in html or "{{" in html and _re.search(r'\{\{[^}]+\}\}', html):
        placeholders = _re.findall(r'\{\{[^}]+\}\}', html)
        for p in placeholders:
            hard_errors.append(f"❌ [致命] HTML中发现模板占位符 '{p}'，禁止在渲染输出中使用")

    # 1. 验证"明日/下周值得关注"板块是否渲染（有内容）
    if "明日/下周值得关注" not in html:
        warnings.append("⚠️ [警告] '明日/下周值得关注'板块未渲染 — 检查watch_list/preview_events字段")
    else:
        section_match = _re.search(r"明日/下周值得关注(.*?)(?:了解更多|</div>\s*</div>\s*<div style=\"margin-top:24px)", html, _re.DOTALL)
        if section_match and len(section_match.group(1)) < 100:
            warnings.append("⚠️ [警告] '明日/下周值得关注'板块内容疑似为空")

    # 2. 验证5个Tab板块都有内容
    tab_checks = [("大模型", "llm"), ("AI Coding", "coding"),
                  ("AI 应用", "app"), ("AI 行业", "industry"), ("企业转型", "enterprise")]
    tab_present = 0
    for tab_name, tab_id in tab_checks:
        if f'id="{tab_id}"' in html:
            tab_present += 1
            m = _re.search(f'id="{tab_id}"(.*?)id="[a-z]', html, _re.DOTALL)
            if m and len(m.group(1)) < 500:
                warnings.append(f"⚠️ [警告] Tab '{tab_name}' 内容疑似为空")
        else:
            hard_errors.append(f"❌ [关键] Tab '{tab_name}' 完全缺失(id={tab_id})")
    if tab_present < 3:
        hard_errors.append(f"❌ [致命] 仅 {tab_present}/5 个板块渲染，内容严重不足")

    # 3. 验证overview板块
    if "overview-item" not in html:
        hard_errors.append("❌ [关键] '全文概览'板块未渲染")

    # 4. 验证热度趋势
    if "heat-trend" not in html and "热度趋势" not in html:
        warnings.append("⚠️ [警告] 烦度趋势板块未渲染")

    # 5. 验证深度聚焦
    if "deep-focus-card" not in html and "deep-focus-header" not in html:
        hard_errors.append("❌ [关键] 深度聚焦(deep_focus)未渲染")

    # 6. 验证规律洞察
    if "pi-card" not in html:
        warnings.append("⚠️ [警告] 规律洞察未渲染")

    # ══ 结果输出 ══
    if hard_errors:
        print()
        print("🚫 HTML校验硬性失败（不可推送）：")
        for e in hard_errors:
            print(f"   {e}")
        print("   → 请检查JSON数据，修复后重新生成")
        sys.exit(1)
    if warnings:
        print()
        print("⚠️  HTML渲染完整性检查发现软性警告：")
        for w in warnings:
            print(f"   {w}")
    else:
        print("   ✅ HTML校验通过: ≥50KB + 5板块完整 + 无{{message}}占位符 + overview/深度聚焦正常")


if __name__ == "__main__":
    main()
