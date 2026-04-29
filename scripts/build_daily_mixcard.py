#!/usr/bin/env python3
"""
AI日报 MixCard JSON 生成器
=========================
从 daily-content-YYYY-MM-DD.json 生成用于 message 工具 kimMixCard 参数的卡片 JSON。

用途:
- 旧方式: send_ai_daily.py 直接调用 KIM API (需要 KIM_APP_KEY + KIM_SECRET_KEY)
- 新方式: 本脚本输出卡片 JSON → 通过 MyFlicker message 工具 + kimMixCard 参数发送

使用:
    python3 scripts/build_daily_mixcard.py YYYY-MM-DD [--output card.json]
    
或在 Agent 中:
    1. python3 scripts/build_daily_mixcard.py 2026-04-29 --output /tmp/card.json
    2. 读取 /tmp/card.json 内容
    3. 调用 message(channel=kim, target=username:shenlang, kimMixCard=<json>, message=<summary>)

保持与 send_ai_daily.py 中 build_card_v35 完全一致的结构（热度趋势+5板块+深度聚焦+林克自述+双按钮）。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 项目根: 脚本父目录的父目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 派生 URL
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"
REPORT_BASE_URL = f"{INTERNAL_BASE}/01-daily-reports"
PROJECT_URL = f"{INTERNAL_BASE}/"


def build_card(date_str: str, data: dict) -> dict:
    """构建完整 mixCard JSON（与 send_ai_daily.py build_card_v35 保持一致）"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[date_obj.weekday()]
    month_str = date_obj.strftime("%Y-%m")
    report_url = f"{REPORT_BASE_URL}/{month_str}/{date_str}.html"

    coverage = data.get("coverage", {}) or {}
    overseas = coverage.get("overseas", 0)
    china = coverage.get("china", 0)

    # ---------- 热度趋势 ----------
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
    heat_trend = "\n".join(heat_lines)

    # ---------- 板块 ----------
    tabs = data.get("tabs", []) or []
    section_names = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业转型"]
    section_icons = ["🧠", "⌨️", "📱", "🏭", "🔄"]

    sections = []
    for i, tab in enumerate(tabs[:5]):
        name = section_names[i]
        icon = section_icons[i]
        news_data = tab.get("news", {}) or {}
        overseas_news = news_data.get("overseas", []) or []
        china_news = news_data.get("china", []) or []

        focus = tab.get("deep_focus") or tab.get("focus") or {}
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
        takeaway = focus.get("takeaway", "")

        if focus_title or focus_summary:
            lines.append("")
            if focus_title:
                lines.append(f"💡 **深度聚焦** — {focus_title}")
            if focus_summary:
                if len(focus_summary) > 100:
                    focus_summary = focus_summary[:100] + "..."
                lines.append(f"→ {focus_summary}")
            if takeaway:
                lines.append(f"**关键判断**：{takeaway}")

        sections.append("\n".join(lines))

    # ---------- 组装 blocks ----------
    blocks = [
        {"blockId": "header", "type": "content",
         "text": {"type": "kimMd", "content": f"# 📡 AI 日报（{date_str}，{weekday}）"}},
        {"blockId": "subtitle", "type": "content",
         "text": {"type": "kimMd",
                  "content": f"🌍 海外{overseas}条 · 🇨🇳 国内{china}条 | 五大板块 · 每板块含动态/深度聚焦"}},
        {"blockId": "div0", "type": "divider"},
    ]

    if heat_trend:
        blocks.append({"blockId": "heat", "type": "content",
                       "text": {"type": "kimMd", "content": heat_trend}})
        blocks.append({"blockId": "div_heat", "type": "divider"})

    for i, sec in enumerate(sections):
        blocks.append({"blockId": f"sec{i+1}", "type": "content",
                       "text": {"type": "kimMd", "content": sec}})
        blocks.append({"blockId": f"div{i+1}", "type": "divider"})

    cap = data.get("capability_update", "") or ""
    if cap:
        blocks.append({"blockId": "capability", "type": "content",
                       "text": {"type": "kimMd", "content": cap}})
        blocks.append({"blockId": "div_cap", "type": "divider"})

    blocks.append({"blockId": "footer", "type": "content",
                   "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察*"}})

    blocks.append({
        "blockId": "buttons",
        "type": "action",
        "layout": "two",
        "actions": [
            {"type": "button",
             "text": {"type": "plainText", "content": "📄 查看完整日报 >>"},
             "style": "green", "url": report_url},
            {"type": "button",
             "text": {"type": "plainText", "content": "💡 了解AI洞察项目"},
             "style": "blue", "url": PROJECT_URL},
        ],
    })

    card = {
        "config": {"forward": True, "forwardType": 3, "wideSelfAdaptive": True},
        "updateMulti": 1,
        "blocks": blocks,
    }
    return card


def build_summary(date_str: str, data: dict) -> str:
    """构建 message 正文 (当 mixCard 不可用时的降级 + 作为卡片描述)"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[date_obj.weekday()]
    coverage = data.get("coverage", {}) or {}
    overseas = coverage.get("overseas", 0)
    china = coverage.get("china", 0)
    return f"📡 AI 日报 {date_str}（{weekday}）| 海外{overseas}条 · 国内{china}条 · 5板块全覆盖"


def main():
    parser = argparse.ArgumentParser(description="生成 AI日报 mixCard JSON")
    parser.add_argument("date", help="日报日期 YYYY-MM-DD")
    parser.add_argument("--output", "-o", help="输出文件路径 (默认 stdout)")
    parser.add_argument("--with-summary", action="store_true",
                        help="输出带 summary 的完整结构 {card, summary}")
    args = parser.parse_args()

    json_path = PROJECT_ROOT / "data" / f"daily-content-{args.date}.json"
    if not json_path.exists():
        print(f"❌ 找不到日报数据文件: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    card = build_card(args.date, data)
    summary = build_summary(args.date, data)

    if args.with_summary:
        out = {"card": card, "summary": summary}
    else:
        out = card

    out_str = json.dumps(out, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        size = len(out_str)
        print(f"✅ 卡片已生成: {args.output}")
        print(f"   大小: {size} chars ({size/1024:.1f}KB)")
        print(f"   Blocks: {len(card['blocks'])}")
        print(f"   Summary: {summary}")
    else:
        print(out_str)


if __name__ == "__main__":
    main()
