#!/usr/bin/env python3
"""从 daily-content-{date}.json 生成 {date}.md 日报 Markdown 文件"""
import json, sys
from pathlib import Path
from datetime import datetime

def gen_md(date_str: str):
    base = Path(__file__).parent.parent
    json_path = base / "data" / f"daily-content-{date_str}.json"
    if not json_path.exists():
        print(f"❌ 找不到: {json_path}")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    prev_dt = datetime.fromordinal(dt.toordinal() - 1)
    prev_date = prev_dt.strftime("%Y-%m-%d")
    time_window = f"{prev_date} 08:00 ~ {date_str} 08:00"

    TAB_ICON = {
        "models": "🧠 大模型",
        "coding": "💻 AI编程",
        "apps": "📱 AI应用",
        "industry": "🏭 AI行业",
        "enterprise": "🏢 企业转型",
    }

    lines = []
    lines.append(f"# AI 洞察日报 · {dt.strftime('%Y年%-m月%-d日')}")
    lines.append(f"> 时间窗口：{time_window}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📌 今日概览")
    lines.append("| 维度 | 信号 |")
    lines.append("|------|------|")

    overview = data.get("overview", [])
    for item in overview:
        if isinstance(item, dict):
            icon = item.get("icon", "")
            label = item.get("label", "")
            headline = item.get("headline", "")
            lines.append(f"| {icon} {label} | {headline} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    tabs = data.get("tabs", [])
    for tab in tabs:
        if not isinstance(tab, dict):
            continue
        tab_id = tab.get("id", "")
        tab_title = TAB_ICON.get(tab_id, tab.get("title", tab_id))
        lines.append(f"## {tab_title} 板块")

        news_list = tab.get("news", [])
        for item in news_list:
            if not isinstance(item, dict):
                continue
            title = item.get("title", "")
            source = item.get("source", "")
            url = item.get("url", "")
            date = item.get("date", "")
            details = item.get("details", {})
            if isinstance(details, dict):
                summary = details.get("summary", details.get("text", ""))
                insight = details.get("insight", details.get("significance", ""))
            else:
                summary = str(details)
                insight = ""

            lines.append(f"### {title}")
            if url and url.strip():
                lines.append(f"**来源**: [{source}]({url}) | {date}")
            else:
                lines.append(f"**来源**: {source} | {date}")
            if summary:
                lines.append(summary)
            if insight:
                lines.append(f"*{insight}*")
            lines.append("")
            lines.append("---")
            lines.append("")

        # 深度聚焦
        deep_focus = tab.get("deep_focus", {})
        if isinstance(deep_focus, dict) and deep_focus:
            df_title = deep_focus.get("title", "")
            paragraphs = deep_focus.get("paragraphs", [])
            takeaway = deep_focus.get("takeaway", "")
            lines.append(f"### 🔍 深度聚焦：{df_title}")
            for p in paragraphs:
                lines.append(p)
                lines.append("")
            if takeaway:
                lines.append(f"> **核心洞察**: {takeaway}")
                lines.append("")
            lines.append("---")
            lines.append("")

    month_str = dt.strftime("%Y-%m")
    out_dir = base / "01-daily-reports" / month_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ MD文件已生成: {out_path}")
    print(f"   行数: {len(lines)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python gen_md_from_json.py <date>")
        sys.exit(1)
    gen_md(sys.argv[1])
