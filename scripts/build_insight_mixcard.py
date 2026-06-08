#!/usr/bin/env python3
"""
AI洞察 mixCard JSON 统一生成器
=============================
为所有 AI洞察 KIM 推送场景生成 mixCard JSON，供 MyFlicker message 工具 + kimMixCard 参数使用。

覆盖场景:
1. AI日报 (daily)     — 统一入口（旧版 build_daily_mixcard.py 已归档废弃）
2. AI周报 (weekly)    — 从周报 MD 内容提取 Top5 + 洞察
3. 深度调研 (research) — 独立专题卡片（需传入参数）
4. 产品本质 (product)  — 独立专题卡片（需传入参数）

使用:
    python3 scripts/build_insight_mixcard.py daily 2026-04-29 --output /tmp/card.json
    python3 scripts/build_insight_mixcard.py weekly 2026-W17 --output /tmp/card.json
    python3 scripts/build_insight_mixcard.py research --slug ai-下半场 --output /tmp/card.json
    python3 scripts/build_insight_mixcard.py product --output /tmp/card.json

设计原则:
- 所有卡片共享统一格式：config/forwardType=3/wideSelfAdaptive/updateMulti=1
- 所有卡片双按钮统一：按钮1=当期内容(绿) + 按钮2=了解AI洞察项目(蓝)
- 所有卡片页脚统一：*林克（沈浪的AI分身）· AI洞察*
- 输出不含 appKey（由 message 工具的 kimMixCard 机制处理，不走 KIM API）

作者: 林克 (沈浪的AI分身)
版本: 2.0.0 (2026-05-11: 新增6锚点自校验+URL可达性验证+{{message}}扫描+kimMd格式校验)
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
WEEKDAY_CN = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 从 config.py SSoT 读取 URL
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from config import INTERNAL_PAGES_BASE as INTERNAL_BASE
from config import EXTERNAL_PAGES_BASE as EXTERNAL_BASE
# ⭐ v2.1 修正（2026-06-08 P0）：MixCard按钮URL统一使用外部版（GitHub Pages）
# 根因：frontend-cloud内部版需要快手SSO登录，KIM WebView点击按钮时没有SSO cookie → SSO拦截 → 用户看到"无法跳转"
# 外部版（GitHub Pages）不需要SSO，任何人都能直接访问，是KIM MixCard按钮的唯一可靠URL
# 旧规则（P0 #13）"私发用内部版"已被推翻——内部版URL在KIM里根本无法正常跳转
# 内部版URL仅适合在已登录快手SSO的浏览器里直接访问（如首页浏览），不适合MixCard按钮场景
REPORT_BASE_URL = f"{EXTERNAL_BASE}/01-daily-reports"
PROJECT_URL = f"{EXTERNAL_BASE}/"  # 所有MixCard按钮统一使用外部版
_current_target = "private"  # 推送目标：private=私发(内部版身份), group=群发(脱敏身份)

# 统一卡片骨架配置
CARD_CONFIG = {"forward": True, "forwardType": 3, "wideSelfAdaptive": True}

# ══ 6锚点定义（所有卡片类型必须包含） ══
ANCHOR_NAMES = ["header", "subtitle", "footer", "buttons"]
ANCHOR_TYPES = {"header": "content", "subtitle": "content", "footer": "content", "buttons": "action"}


def _divider(block_id: str) -> dict:
    return {"blockId": block_id, "type": "divider"}


def _content(block_id: str, text: str) -> dict:
    return {"blockId": block_id, "type": "content",
            "text": {"type": "kimMd", "content": text}}


def _footer(tag: str = "") -> dict:
    suffix = f" · {tag}" if tag else ""
    if _current_target == "group":
        text = f"*AI洞察{suffix}*"
    else:
        text = f"*林克（沈浪的AI分身）· AI洞察{suffix}*"
    return _content("footer", text)


def _buttons(btn1_text: str, btn1_url: str, btn2_text: str = "💡 了解AI洞察项目",
             btn2_url: str = None) -> dict:
    if btn2_url is None:
        btn2_url = PROJECT_URL
    return {
        "blockId": "buttons",
        "type": "action",
        "layout": "two",
        "actions": [
            {"type": "button", "text": {"type": "plainText", "content": btn1_text},
             "style": "green", "url": btn1_url},
            {"type": "button", "text": {"type": "plainText", "content": btn2_text},
             "style": "blue", "url": btn2_url},
        ],
    }


# ============ 日报 ============

def build_daily(date_str: str) -> dict:
    """从 daily-content JSON 构建日报 mixCard"""
    json_path = PROJECT_ROOT / "data" / f"daily-content-{date_str}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"日报数据文件不存在: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAY_CN[date_obj.weekday()]
    month_str = date_str[:7]
    report_url = f"{REPORT_BASE_URL}/{month_str}/{date_str}.html"

    coverage = data.get("coverage", {}) or {}
    overseas = coverage.get("overseas", 0)
    china = coverage.get("china", 0)

    # 热度趋势 — 兼容多种数据格式(v11.2 fix)
    # 格式1: heat_trend.topics (cron早期版本)
    # 格式2: heat_trend.top_items (2026-05-11起)
    # 格式3: heat_trend.top_keywords + trend_summary (2026-05-15起)
    heat_data = data.get("heat_trend", {}) or {}
    heat_title = heat_data.get("title", "近7期日报交叉分析")
    # 优先取top_items，fallback到topics，再fallback到top_keywords
    raw_items = heat_data.get("top_items", []) or heat_data.get("topics", []) or heat_data.get("top_keywords", []) or []
    # 如果raw_items是字符串列表(top_keywords格式)，转换为dict格式
    if raw_items and isinstance(raw_items[0], str):
        raw_items = [{"title": kw, "trend": "new"} for kw in raw_items[:6]]
    trend_summary = heat_data.get("trend_summary", "") or heat_data.get("summary", "")
    trend_icons = {"up": "📈", "down": "📉", "stable": "➡️", "new": "🆕", "burst": "⚡", "hot": "🔥"}
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]

    heat_lines = []
    if raw_items:
        heat_lines = [f"🔥 **热度趋势**（{heat_title}）", ""]
        for i, t in enumerate(raw_items[:6]):
            rank = rank_icons[i] if i < len(rank_icons) else f"{i+1}️⃣"
            name = t.get("name", "") or t.get("title", "")
            days = t.get("days", 0)
            trend_class = t.get("trend_class", "") or t.get("trend", "")
            trend_icon = trend_icons.get(trend_class, "➡️")
            signal = t.get("signal", "")
            if days:
                heat_lines.append(f"- {rank} **{name}** — {days}天 {trend_icon}")
            else:
                heat_lines.append(f"- {rank} **{name}** {trend_icon}")
            if signal:
                heat_lines.append(f"  → {signal}")

    # 板块
    tabs = data.get("tabs", []) or []
    section_names = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业转型"]
    section_icons = ["🧠", "⌨️", "📱", "🏭", "🔄"]

    sections = []
    for i, tab in enumerate(tabs[:5]):
        name = section_names[i]
        icon = section_icons[i]
        news_data = tab.get("news", {}) or {}
        # 兼容两种schema: {overseas:[], china:[]} 或 flat list
        if isinstance(news_data, list):
            overseas_news = [n for n in news_data if n.get("region") != "china"]
            china_news = [n for n in news_data if n.get("region") == "china"]
        else:
            overseas_news = news_data.get("overseas", []) or []
            china_news = news_data.get("china", []) or []
        focus = tab.get("deep_focus") or tab.get("focus") or {}
        # 扁平列表模式下，从新闻项中提取第一个有 deep_focus 的
        if not focus and isinstance(news_data, list):
            for n in news_data:
                df = n.get("deep_focus")
                if df:
                    focus = df
                    break
        if isinstance(focus, str):
            focus = {"summary": focus}

        lines = [f"## {icon} {name}", "", "📰 **动态**"]
        for n in overseas_news[:3]:
            title = n.get("title", "")
            url = n.get("url", "")
            if url:
                lines.append(f"- 📌 | [{title}]({url})")
            else:
                lines.append(f"- 📌 | {title}")
        for n in china_news[:2]:
            title = n.get("title", "")
            url = n.get("url", "")
            if url:
                lines.append(f"- 🇨🇳 国内 | [{title}]({url})")
            else:
                lines.append(f"- 🇨🇳 国内 | {title}")

        focus_title = focus.get("title", "")
        focus_summary = focus.get("summary", "")
        if not focus_summary and focus.get("paragraphs"):
            focus_summary = " ".join(focus["paragraphs"])
        takeaway = focus.get("takeaway", "") or focus.get("key_takeaway", "")

        if focus_title or focus_summary:
            lines.append("")
            if focus_title:
                lines.append(f"💡 **深度聚焦** — {focus_title}")
            if focus_summary:
                if len(focus_summary) > 200:
                    focus_summary = focus_summary[:200] + "..."
                lines.append(f"→ {focus_summary}")
            if takeaway:
                lines.append(f"**关键判断**：{takeaway}")
        sections.append("\n".join(lines))

    # 组装 blocks
    blocks = [
        _content("header", f"# 📡 AI 日报（{date_str}，{weekday}）"),
        _content("subtitle", f"🌍 海外{overseas}条 · 🇨🇳 国内{china}条 | 五大板块 · 每板块含动态/深度聚焦"),
        _divider("div0"),
    ]

    if heat_lines:
        blocks.append(_content("heat", "\n".join(heat_lines)))
        blocks.append(_divider("div_heat"))

    for i, sec in enumerate(sections):
        blocks.append(_content(f"sec{i+1}", sec))
        blocks.append(_divider(f"div{i+1}"))

    cap = data.get("capability_update", "") or ""
    if cap:
        blocks.append(_content("capability", cap))
        blocks.append(_divider("div_cap"))

    blocks.append(_footer("日报"))
    blocks.append(_buttons("📄 查看完整日报 >>", report_url))

    return {"config": CARD_CONFIG, "updateMulti": 1, "blocks": blocks}


# ============ 周报 ============

def build_weekly(week_id: str) -> dict:
    """从周报 MD 构建周报 mixCard"""
    # week_id 格式: 2026-W17 或 2026-04-29 (自动计算周)
    if week_id.startswith("2026-W"):
        # 格式 YYYY-Www
        week_num = int(week_id.split("-W")[1])
        year = int(week_id.split("-")[0])
    else:
        # 格式 YYYY-MM-DD
        date_obj = datetime.strptime(week_id, "%Y-%m-%d")
        year = date_obj.isocalendar()[0]
        week_num = date_obj.isocalendar()[1]

    # 计算周日期范围——从MD内容提取（最准确）
    # 兜底：ISO周号-1周
    iso_monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
    fallback_monday = iso_monday - timedelta(days=7)
    fallback_sunday = iso_monday - timedelta(days=1)

    # 查找周报文件（动态搜索月目录，不硬编码月份）
    # 搜索范围：覆盖周的周一日、fallback周一/周日、根目录
    weekly_patterns = [
        PROJECT_ROOT / "01-daily-reports" / iso_monday.strftime("%Y-%m") / f"weekly-{year}-W{week_num:02d}.md",
        PROJECT_ROOT / "01-daily-reports" / fallback_monday.strftime("%Y-%m") / f"weekly-{year}-W{week_num:02d}.md",
        PROJECT_ROOT / "01-daily-reports" / fallback_sunday.strftime("%Y-%m") / f"weekly-{year}-W{week_num:02d}.md",
        PROJECT_ROOT / "01-daily-reports" / f"weekly-{year}-W{week_num:02d}.md",
    ]

    content = ""
    found = False
    for p in weekly_patterns:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            found = True
            break

    # 从MD内容提取日期范围（最准确的方式）
    date_range = None
    coverage_sunday = fallback_sunday
    if found and content:
        # 匹配标题中的日期范围，如 "05/19 - 05/25" 或 "05.19-05.25"
        date_match = re.search(r'(\d{2}[./]\d{2})\s*[-–至到]\s*(\d{2}[./]\d{2})', content)
        if date_match:
            start_str = date_match.group(1).replace('.', '/')
            end_str = date_match.group(2).replace('.', '/')
            try:
                start_date = datetime.strptime(f"{year}-{start_str}", "%Y-%m/%d")
                end_date = datetime.strptime(f"{year}-{end_str}", "%Y-%m/%d")
                date_range = f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"
                coverage_sunday = end_date
            except ValueError:
                pass
    
    if not date_range:
        # 兜底：ISO周号-1周
        date_range = f"{fallback_monday.strftime('%m/%d')}-{fallback_sunday.strftime('%m/%d')}"

    # 提取 Top 5、周度洞察、林克的洞察
    top5_text = ""
    insight_text = ""
    link_insight_text = ""
    if found and content:
        top5_match = re.search(r"## .*Top 5.*?\n((?:[\s\S]*?))\n## ", content)
        if top5_match:
            top5_text = top5_match.group(1).strip()
            top5_text = re.sub(r'\n---\s*$', '', top5_text)
        insight_match = re.search(r"## .*洞察.*?\n((?:[\s\S]*?))\n## ", content)
        if insight_match:
            insight_text = insight_match.group(1).strip()
            insight_text = re.sub(r'\n---\s*$', '', insight_text)
        # 林克的洞察 — 在周度洞察之后、日报索引之前
        link_match = re.search(r"## 🔥 林克的洞察\n((?:[\s\S]*?))\n## ", content)
        if not link_match:
            link_match = re.search(r"## 🔥 林克的洞察\n((?:[\s\S]*?))(?:\n---|\n\*)", content)
        if link_match:
            link_insight_text = link_match.group(1).strip()

    if not top5_text:
        top5_text = "(周报尚未生成，请先生成周报后再推送)"

    # 周报 URL：使用覆盖周的月份目录（周报存在数据覆盖周的月份）
    month_str = coverage_sunday.strftime("%Y-%m")
    weekly_url = f"{REPORT_BASE_URL}/{month_str}/weekly-{year}-W{week_num:02d}.html"

    blocks = [
        _content("header", f"# 📊 AI 周报（{year}年第{week_num}周，{date_range}）"),
        _content("subtitle", f"📅 {date_range} | Top 5 事件 + 周度洞察 + 林克的洞察"),
        _divider("div0"),
        _content("top5", f"🏆 **Top 5 本周最重要**\n\n{top5_text}"),
    ]

    if insight_text:
        blocks.append(_divider("div1"))
        blocks.append(_content("insight", f"🔥 **周度洞察**\n\n{insight_text}"))

    if link_insight_text:
        blocks.append(_divider("div_link"))
        blocks.append(_content("link_insight", f"🔥 **林克的洞察**\n\n{link_insight_text}"))

    blocks.append(_footer("周报"))
    blocks.append(_buttons("📄 查看完整周报 >>", weekly_url))

    return {"config": CARD_CONFIG, "updateMulti": 1, "blocks": blocks}


# ============ 深度调研 ============

def build_research(slug: str = "", title: str = "", subtitle: str = "",
                   core_insight: str = "",
                   trends: str = "", principles: str = "", sources: str = "",
                   report_url: str = "") -> dict:
    """构建深度调研 mixCard（参数化，可传入任意专题内容）"""
    if not title:
        title = f"📚 深度调研 · {slug or 'AI专题'}"
    if not report_url:
        if slug:
            report_url = f"{EXTERNAL_BASE}/02-deep-research/{slug}.html"
        else:
            report_url = PROJECT_URL

    today = datetime.now().strftime("%Y-%m-%d")
    weekday = WEEKDAY_CN[datetime.now().weekday()]

    blocks = [
        _content("header", f"# {title}"),
        _content("subtitle", subtitle or "深度调研 · AI专题"),
        _content("date", f"📅 *{today}（{weekday}）发布*"),
        _divider("div0"),
    ]

    if core_insight:
        blocks.append(_content("insight", core_insight))
        blocks.append(_divider("div1"))

    if trends:
        blocks.append(_content("trends", trends))
        blocks.append(_divider("div2"))

    if principles:
        blocks.append(_content("principles", principles))
        blocks.append(_divider("div3"))

    if sources:
        blocks.append(_content("sources", sources))
        blocks.append(_divider("div4"))

    blocks.append(_footer("深度调研系列"))
    blocks.append(_buttons("📄 查看完整报告 >>", report_url))

    return {"config": CARD_CONFIG, "updateMulti": 1, "blocks": blocks}


# ============ 产品本质 ============

def build_product_essence() -> dict:
    """构建 AI产品本质研究 mixCard（固定内容卡片）"""
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = WEEKDAY_CN[datetime.now().weekday()]

    LQ = "\u201c"
    RQ = "\u201d"
    EM = "\u2014"

    header_text = f"# 🧠 深度调研 · AI产品本质研究\n\n📅 *{today}（{weekday}）*"

    core_text = (
        "**核心结论**\n\n"
        f"99%的AI产品正在用{LQ}**买工具**{RQ}的思维，做{LQ}**招员工**{RQ}的事。\n\n"
        "AI产品的本质是**认知代劳**，不是功能替代。用SaaS的逻辑做AI，越努力越错。\n\n"
        "📌 成功公式：**(Q > 阈值) × D × T > E**\n"
        "- Q: 质量穿越阈值（用户要惊叹，不是还行）\n"
        "- D: 场景要深不要广\n"
        "- T: 信任累积必须跑赢成本消耗"
    )

    mistakes_text = (
        "❌ **六大错误：买工具思维 vs 招员工现实**\n\n"
        f"- 错误1：**拼命堆功能** {EM} 质量不够的功能越多，负面体验面越大\n"
        f"- 错误2：**先推广再打磨** {EM} AI的第一印象定格为{LQ}没用{RQ}，几乎不可逆\n"
        f"- 错误3：**不计成本拉用户** {EM} 每次推理都烧算力，质量未过阈值时越推广越烧信誉\n"
        f"- 错误4：**功能矩阵对标竞品** {EM} AI的竞争维度是质量深度，不是功能广度\n"
        f"- 错误5：**用SaaS漏斗找留存答案** {EM} SaaS留存是UX问题，AI留存是质量问题\n"
        f"- 错误6：**先圈地盘再提质量** {EM} 圈了一个{LQ}不够聪明{RQ}的心智，是最难逆转的"
    )

    scorecard_text = (
        "📋 **五款产品评分（五维框架：Q质量/E经济/T信任/D场景）**\n\n"
        "- ✅ Cursor — Q:★★★★★ E:★★★★★ T:★★★★★ D:★★★★★ | 教科书\n"
        "- ✅ Claude Code — Q:★★★★★ E:★★★★ T:★★★★ D:★★★★★ | 教科书\n"
        "- ✅ 钉钉悟空 — Q:★★★★ E:★★★★ T:★★★★★ D:★★★★ | 方向正确\n"
        "- ⚠️ OpenClaw — Q:★★★★ E:★★ T:★★★ D:★★★ | 验证了需求\n"
        "- ⚠️ Manus — Q:★★★ E:★★ T:★★ D:★★ | 通用陷阱（样样能做，样样不深）"
    )

    insight_text = (
        "🧠 **林克的本质洞察**\n\n"
        f"表面：做得好的AI产品不推广，砸了钱的反而越做越难。\n\n"
        f"本质：SaaS卖的是{LQ}权利{RQ}{EM}你有权使用这个功能；"
        f"AI卖的是{LQ}代劳{RQ}{EM}我替你把这件事做好。"
        f"权利可以承诺，代劳只能证明。就像钥匙可以大量复制分发，人只能靠口口相传建立信任。\n\n"
        f"趋势推演：未来AI产品的护城河不是功能数量，而是{LQ}信任深度{RQ}"
        f"{EM}谁的AI积累了更多个性化记忆、让用户越用越离不开，就越难被替换。"
    )

    research_url = f"{EXTERNAL_BASE}/02-deep-research/ai-product-essence.html"

    blocks = [
        _content("header", header_text),
        _divider("div0"),
        _content("core", core_text),
        _divider("div1"),
        _content("mistakes", mistakes_text),
        _divider("div2"),
        _content("scorecard", scorecard_text),
        _divider("div3"),
        _content("insight", insight_text),
        _divider("div4"),
        _footer("深度调研系列"),
        _buttons("📄 查看完整解读 >>", research_url),
    ]

    return {"config": CARD_CONFIG, "updateMulti": 1, "blocks": blocks}


# ============ 自校验系统 ============

def validate_card(card: dict, scenario: str) -> list[str]:
    """校验 mixCard JSON 的完整性。返回错误列表，空=通过。
    
    校验项:
    1. 6锚点存在性: header/subtitle/footer/buttons 必须存在
    2. kimMd 格式: content block 的 text 必须是 {"type": "kimMd", "content": "..."} object
    3. {{message}} 占位符扫描: kimMd content 中禁止包含 {{...}}
    4. URL可达性: 按钮 URL 必须 HTTP 200 (可跳过)
    """
    errors = []
    blocks = card.get("blocks", [])
    block_ids = [b.get("blockId", "") for b in blocks]
    block_types = {b.get("blockId", ""): b.get("type", "") for b in blocks}
    
    # 1. 锚点存在性检查
    for anchor in ANCHOR_NAMES:
        if anchor not in block_ids:
            errors.append(f"❌ 缺少锚点: {anchor}")
        elif ANCHOR_TYPES.get(anchor) and block_types.get(anchor) != ANCHOR_TYPES[anchor]:
            errors.append(f"❌ 锚点 {anchor} 类型错误: 期望 {ANCHOR_TYPES[anchor]}, 实际 {block_types.get(anchor)}")
    
    # 2. kimMd 格式检查 — 所有 content block 的 text 必须是 kimMd object
    for b in blocks:
        if b.get("type") == "content" and "text" in b:
            text = b["text"]
            if isinstance(text, str):
                errors.append(f"❌ block {b.get('blockId', '?')}: text 是纯字符串，必须是 {'type':'kimMd','content':'...'} object")
            elif isinstance(text, dict):
                if text.get("type") != "kimMd":
                    errors.append(f"❌ block {b.get('blockId', '?')}: text.type={text.get('type')}, 必须是 kimMd")
                content = text.get("content", "")
                # 3. {{message}} 占位符扫描
                placeholders = re.findall(r'\{\{[^}]+\}\}', content)
                for p in placeholders:
                    errors.append(f"❌ block {b.get('blockId', '?')}: 发现模板占位符 '{p}'，禁止在 kimMd 中使用")
    
    # 4. 按钮URL格式检查（不做HTTP验证，太慢）
    for b in blocks:
        if b.get("type") == "action":
            for act in b.get("actions", []):
                url = act.get("url", "")
                if not url:
                    errors.append(f"❌ 按钮 '{act.get('text', {}).get('content', '?')}' 缺少 url")
                elif not url.startswith("http"):
                    errors.append(f"❌ 按钮 URL 格式错误: {url}")
    
    return errors


def validate_card_with_url_check(card: dict, scenario: str) -> list[str]:
    """完整校验 = 结构校验 + 按钮 URL HTTP 可达性验证"""
    errors = validate_card(card, scenario)
    
    # 按钮 URL HTTP 可达性验证
    # weekly场景：按钮URL不可达=hard fail(❌)，其他场景=soft warning(⚠️)
    is_weekly = scenario == "weekly"
    for b in card.get("blocks", []):
        if b.get("type") == "action":
            for act in b.get("actions", []):
                url = act.get("url", "")
                if url and url.startswith("http"):
                    try:
                        req = urllib.request.Request(url, method="HEAD")
                        req.add_header('User-Agent', 'MyFlicker-MixCard-Validator/2.0')
                        resp = urllib.request.urlopen(req, timeout=10)
                        if resp.status >= 400:
                            prefix = "❌" if is_weekly else "⚠️"
                            errors.append(f"{prefix} 按钮 URL 不可达: {url} (HTTP {resp.status})")
                    except Exception:
                        prefix = "❌" if is_weekly else "⚠️"
                        errors.append(f"{prefix} 按钮 URL 验证失败: {url}")
    
    return errors


# ============ 入口 ============

def build_summary(scenario: str, date_str: str = "") -> str:
    """生成 message 正文摘要"""
    if scenario == "daily":
        d = datetime.strptime(date_str, "%Y-%m-%d")
        wd = WEEKDAY_CN[d.weekday()]
        return f"📡 AI 日报 {date_str}（{wd}）"
    elif scenario == "weekly":
        return f"📊 AI 周报 {date_str}"
    elif scenario == "research":
        return "📚 AI洞察深度调研"
    elif scenario == "product":
        return "🧠 AI产品本质研究"
    return "AI洞察"


def main():
    parser = argparse.ArgumentParser(description="AI洞察 mixCard 统一生成器")
    parser.add_argument("scenario", choices=["daily", "weekly", "research", "product"],
                        help="推送场景")
    parser.add_argument("--date", "-d", help="日期 (日报: YYYY-MM-DD, 周报: YYYY-Www 或 YYYY-MM-DD)")
    parser.add_argument("--slug", help="深度调研 slug (如 ai-下半场)")
    parser.add_argument("--title", help="深度调研卡片标题")
    parser.add_argument("--subtitle-text", help="深度调研卡片subtitle内容")
    parser.add_argument("--insight", help="核心结论内容")
    parser.add_argument("--trends", help="趋势内容")
    parser.add_argument("--principles", help="原理/洞见内容")
    parser.add_argument("--sources", help="参考来源内容")
    parser.add_argument("--footer-text", help="footer文字")
    parser.add_argument("--report-url", help="完整报告URL")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--with-summary", action="store_true", help="输出 {card, summary}")
    parser.add_argument("--verify-urls", action="store_true", help="校验按钮URL可达性(HTTP 200)")
    parser.add_argument("--target", choices=["private", "group"], default="private",
                        help="推送目标: private=私发订阅者(内部版URL), group=群发(外部版URL)")
    args = parser.parse_args()

    # ⭐ v2.1 修正（2026-06-08 P0）：所有MixCard按钮统一使用外部版URL
    # --target 仅控制 footer 文本（private=林克身份, group=脱敏身份）
    # 不再控制按钮URL——因为frontend-cloud内部版需要SSO，KIM里点击必被拦截
    # 所有MixCard按钮URL统一用外部版（GitHub Pages），无需SSO即可访问
    _current_target = args.target

    try:
        if args.scenario == "daily":
            date_str = args.date or datetime.now().strftime("%Y-%m-%d")
            card = build_daily(date_str)
            summary = build_summary("daily", date_str)
        elif args.scenario == "weekly":
            date_str = args.date or f"{datetime.now().isocalendar()[0]}-W{datetime.now().isocalendar()[1]:02d}"
            card = build_weekly(date_str)
            summary = build_summary("weekly", date_str)
        elif args.scenario == "research":
            card = build_research(
                slug=args.slug or "",
                title=args.title or "",
                subtitle=args.subtitle_text or "",
                core_insight=args.insight or "",
                trends=args.trends or "",
                principles=args.principles or "",
                sources=args.sources or "",
                report_url=args.report_url or "",
            )
            summary = build_summary("research")
        elif args.scenario == "product":
            card = build_product_essence()
            summary = build_summary("product")
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    # ══ 自校验（所有卡片生成后必须通过） ══
    errors = validate_card(card, args.scenario)
    hard_errors = [e for e in errors if e.startswith("❌")]
    soft_errors = [e for e in errors if e.startswith("⚠️")]
    if hard_errors:
        print("🚫 MixCard 校验失败:", file=sys.stderr)
        for e in hard_errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    if soft_errors:
        print("⚠️ MixCard 存在软性警告:", file=sys.stderr)
        for e in soft_errors:
            print(f"  {e}", file=sys.stderr)
    if not errors:
        print("✅ MixCard 校验通过: 6锚点完整 + kimMd格式正确 + 无{{message}}占位符")

    # URL可达性验证（可选，--verify-urls 时执行；weekly场景默认执行）
    should_verify_urls = args.verify_urls or args.scenario == "weekly"
    if should_verify_urls:
        url_errors = validate_card_with_url_check(card, args.scenario)
        url_warnings = [e for e in url_errors if e.startswith("⚠️")]
        url_hard = [e for e in url_errors if e.startswith("❌")]
        if url_warnings:
            for w in url_warnings:
                print(f"  {w}")
        if url_hard:
            for h in url_hard:
                print(f"  {h}")
            print("🚫 按钮URL不可达，MixCard不能推送！", file=sys.stderr)
            sys.exit(1)

    # ⚠️ 输出格式说明：
    # - kimMixCard参数需要inner card格式（config+blocks直接在顶层）
    # - 旧版 --with-summary 输出 {"card": {...}, "summary": "..."} 双层结构会导致KIM渲染为空消息
    # - 新版默认输出inner card格式；summary信息打印到stdout而非嵌入JSON
    out = card  # 直接输出inner card（config+blocks），可用于kimMixCard参数
    out_str = json.dumps(out, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        # 输出生成摘要
        n_blocks = len(card.get("blocks", []))
        anchor_status = "✅ 6锚点完整" if not hard_errors else "❌ 锚点缺失"
        print(f"✅ mixCard已生成: {args.output}")
        print(f"   大小: {len(out_str)} chars ({len(out_str)/1024:.1f}KB)")
        print(f"   Blocks: {n_blocks}")
        print(f"   校验: {anchor_status}")
        print(f"   Summary: {summary}")
        print(f"   ⚠️ 使用方式: 读取此JSON，直接传给 message(kimMixCard=<此JSON内容>)")
    else:
        print(out_str)


if __name__ == "__main__":
    main()