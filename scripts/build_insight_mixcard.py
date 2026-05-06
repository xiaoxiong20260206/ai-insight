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
版本: 1.0.0 (2026-04-29: 统一日报/周报/深度调研/产品本质)
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
WEEKDAY_CN = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"
REPORT_BASE_URL = f"{INTERNAL_BASE}/01-daily-reports"
PROJECT_URL = f"{INTERNAL_BASE}/"

# 统一卡片骨架配置
CARD_CONFIG = {"forward": True, "forwardType": 3, "wideSelfAdaptive": True}


def _divider(block_id: str) -> dict:
    return {"blockId": block_id, "type": "divider"}


def _content(block_id: str, text: str) -> dict:
    return {"blockId": block_id, "type": "content",
            "text": {"type": "kimMd", "content": text}}


def _footer(tag: str = "") -> dict:
    suffix = f" · {tag}" if tag else ""
    return _content("footer", f"*林克（沈浪的AI分身）· AI洞察{suffix}*")


def _buttons(btn1_text: str, btn1_url: str, btn2_text: str = "💡 了解AI洞察项目",
             btn2_url: str = PROJECT_URL) -> dict:
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

    # 热度趋势
    heat_data = data.get("heat_trend", {}) or {}
    heat_title = heat_data.get("title", "近7期日报交叉分析")
    topics = heat_data.get("topics", []) or []
    trend_icons = {"up": "📈", "down": "📉", "stable": "➡️", "new": "🆕", "burst": "⚡"}
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]

    heat_lines = []
    if topics:
        heat_lines = [f"🔥 **热度趋势**（{heat_title}）", ""]
        for i, t in enumerate(topics[:6]):
            rank = rank_icons[i] if i < len(rank_icons) else f"{i+1}️⃣"
            name = t.get("name", "")
            days = t.get("days", 0)
            trend_icon = trend_icons.get(t.get("trend_class", "stable"), "➡️")
            signal = t.get("signal", "")
            heat_lines.append(f"- {rank} **{name}** — {days}天 {trend_icon}")
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

    # 计算周日期范围
    from datetime import timedelta
    monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    date_range = f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d')}"

    # 查找周报文件（动态搜索月目录，不硬编码月份）
    weekly_patterns = [
        PROJECT_ROOT / "01-daily-reports" / monday.strftime("%Y-%m") / f"weekly-{year}-W{week_num:02d}.md",
        PROJECT_ROOT / "01-daily-reports" / sunday.strftime("%Y-%m") / f"weekly-{year}-W{week_num:02d}.md",
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

    # 周报 URL：使用周日的月份目录（周报通常存在周日所在月份）
    month_str = sunday.strftime("%Y-%m")
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

def build_research(slug: str = "", title: str = "", core_insight: str = "",
                   trends: str = "", principles: str = "", sources: str = "",
                   report_url: str = "") -> dict:
    """构建深度调研 mixCard（参数化，可传入任意专题内容）"""
    if not title:
        title = f"📚 深度调研 · {slug or 'AI专题'}"
    if not report_url:
        if slug:
            report_url = f"{INTERNAL_BASE}/02-deep-research/{slug}.html"
        else:
            report_url = PROJECT_URL

    today = datetime.now().strftime("%Y-%m-%d")
    weekday = WEEKDAY_CN[datetime.now().weekday()]

    blocks = [
        _content("header", f"# {title}"),
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

    research_url = f"{INTERNAL_BASE}/02-deep-research/ai-product-essence.html"

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
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--with-summary", action="store_true", help="输出 {card, summary}")
    args = parser.parse_args()

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
            card = build_research(slug=args.slug or "")
            summary = build_summary("research")
        elif args.scenario == "product":
            card = build_product_essence()
            summary = build_summary("product")
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    out = {"card": card, "summary": summary} if args.with_summary else card
    out_str = json.dumps(out, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"✅ mixCard已生成: {args.output}")
        print(f"   大小: {len(out_str)} chars ({len(out_str)/1024:.1f}KB)")
        print(f"   Blocks: {len(card['blocks'])}")
        print(f"   Summary: {summary}")
    else:
        print(out_str)


if __name__ == "__main__":
    main()