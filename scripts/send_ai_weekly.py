#!/usr/bin/env python3
"""
AI周报 KIM 推送脚本 v1.0
========================
将 AI 周报推送到 KIM（支持个人/群推送）

功能特性:
- 从周报 Markdown 提取 Top 5 + 周度洞察
- 双按钮：查看完整周报 + 了解AI洞察项目
- 支持发送到个人或群
- 重试机制：遇到频率限制自动重试

使用方式:
  python scripts/send_ai_weekly.py --to-user shenlang    # 发给个人（预览）
  python scripts/send_ai_weekly.py --to-groups            # 发送到所有群
  python scripts/send_ai_weekly.py 2026-W10               # 推送指定周
  python scripts/send_ai_weekly.py --dry-run              # 试运行

作者: 林克 (沈浪的AI分身)
版本: 1.0.0
"""

import asyncio
import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from kim_client import (
    KimConfig, get_access_token, get_bot_groups,
    send_to_user, send_to_group_with_retry, send_to_all_groups
)


# 路径配置
DAILY_REPORTS_PATH = Path(__file__).parent.parent / "01-daily-reports"
REPORT_BASE_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"


def get_week_dates(week_str: str = None):
    """
    获取周的日期范围

    Args:
        week_str: 周标识，如 "2026-W10"，默认本周

    Returns:
        (year, week_num, start_date, end_date)
    """
    if week_str:
        match = re.match(r"(\d{4})-W(\d{1,2})", week_str)
        if not match:
            raise ValueError(f"Invalid week format: {week_str}, expected YYYY-WNN")
        year, week_num = int(match.group(1)), int(match.group(2))
        # ISO周一为周起始（使用%G-%V-%u格式正确处理ISO周数）
        start_date = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u").date()
    else:
        today = datetime.now().date()
        # 上一周
        start_date = today - timedelta(days=today.weekday() + 7)
        year, week_num = start_date.isocalendar()[:2]

    end_date = start_date + timedelta(days=6)
    return year, week_num, start_date, end_date


def read_weekly_report(year: int, week_num: int) -> dict:
    """
    尝试读取已生成的周报文件

    Returns:
        {"found": bool, "content": str, "url": str}
    """
    # 查找周报文件
    for month_dir in sorted(DAILY_REPORTS_PATH.iterdir()):
        if not month_dir.is_dir():
            continue
        weekly_md = month_dir / f"weekly-{year}-W{week_num:02d}.md"
        weekly_html = month_dir / f"weekly-{year}-W{week_num:02d}.html"
        if weekly_md.exists():
            content = weekly_md.read_text(encoding="utf-8")
            month_str = month_dir.name
            url = f"{REPORT_BASE_URL}/{month_str}/weekly-{year}-W{week_num:02d}.html"
            return {"found": True, "content": content, "url": url, "has_html": weekly_html.exists()}

    return {"found": False, "content": "", "url": "", "has_html": False}


def build_weekly_card(year: int, week_num: int, start_date, end_date, report_data: dict) -> dict:
    """构建周报 MixCard 卡片"""
    date_range = f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"

    # 如果有周报内容，从中提取 Top 5
    top5_text = ""
    insight_text = ""

    if report_data["found"]:
        content = report_data["content"]
        # 尝试提取 Top 5
        top5_match = re.search(r"## .*Top 5.*?\n((?:[\s\S]*?))\n## ", content)
        if top5_match:
            top5_text = top5_match.group(1).strip()
        # 尝试提取周度洞察
        insight_match = re.search(r"## .*洞察.*?\n((?:[\s\S]*?))\n## ", content)
        if insight_match:
            insight_text = insight_match.group(1).strip()

    # 构建卡片内容
    header_content = f"# 📊 AI 周报（{year}年第{week_num}周，{date_range}）"

    if not top5_text:
        top5_text = "(周报尚未生成，请先生成周报后再推送)"

    blocks = [
        {
            "blockId": "header",
            "type": "content",
            "text": {"type": "kimMd", "content": header_content}
        },
        {"blockId": "div0", "type": "divider"},
        {
            "blockId": "top5",
            "type": "content",
            "text": {"type": "kimMd", "content": f"🏆 **Top 5 本周最重要**\n\n{top5_text}"}
        },
    ]

    if insight_text:
        blocks.extend([
            {"blockId": "div1", "type": "divider"},
            {
                "blockId": "insight",
                "type": "content",
                "text": {"type": "kimMd", "content": f"🔥 **周度洞察**\n\n{insight_text}"}
            },
        ])

    blocks.extend([
        {"blockId": "div_footer", "type": "divider"},
        {
            "blockId": "footer",
            "type": "content",
            "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察 · 周报*"}
        },
        {
            "blockId": "buttons",
            "type": "action",
            "actions": [
                {
                    "type": "button",
                    "text": {"type": "plainText", "content": "📄 查看完整周报 >>"},
                    "style": "green",
                    "url": report_data.get("url", PROJECT_URL)
                },
                {
                    "type": "button",
                    "text": {"type": "plainText", "content": "了解AI洞察项目"},
                    "style": "blue",
                    "url": PROJECT_URL
                }
            ],
            "layout": "two"
        }
    ])

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": KimConfig.APP_KEY,
        "updateMulti": 1,
        "blocks": blocks
    }


async def main():
    parser = argparse.ArgumentParser(description="AI周报 KIM 推送脚本 v1.0")
    parser.add_argument("week", nargs="?", help="周标识 (YYYY-WNN)，默认上一周")
    parser.add_argument("--to-user", type=str, help="发送到指定用户（用户名）")
    parser.add_argument("--to-groups", action="store_true", help="发送到所有群")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()

    if not args.to_user and not args.to_groups:
        print("Please specify: --to-user <username> or --to-groups")
        print("  Example: python scripts/send_ai_weekly.py --to-user shenlang")
        return

    # 确定周
    try:
        year, week_num, start_date, end_date = get_week_dates(args.week)
    except ValueError as e:
        print(f"Error: {e}")
        return

    date_range = f"{start_date.strftime('%m/%d')}-{end_date.strftime('%m/%d')}"
    print(f"📊 AI 周报推送 v1.0 - {year}-W{week_num:02d} ({date_range})")
    if args.dry_run:
        print("   [DRY-RUN mode]")
    print("=" * 50)

    # 1. 读取周报
    print("📖 读取周报内容...")
    report_data = read_weekly_report(year, week_num)
    if report_data["found"]:
        print(f"   Found: weekly-{year}-W{week_num:02d}.md")
    else:
        print(f"   Warning: weekly-{year}-W{week_num:02d}.md not found")
        print(f"   Will send placeholder card")

    # 2. 构建卡片
    print("🎨 构建周报卡片...")
    card = build_weekly_card(year, week_num, start_date, end_date, report_data)
    print("   Card built OK")

    # 3. 获取 Token
    print("🔑 获取 Access Token...")
    try:
        token = await get_access_token()
        print("   Token OK")
    except Exception as e:
        print(f"   Token FAIL: {e}")
        return

    # 4. 发送
    if args.to_user:
        print(f"\n📤 发送给用户: {args.to_user}")
        success = await send_to_user(token, args.to_user, card, args.dry_run)
        if success:
            print("   Send OK! Check KIM.")
        else:
            print("   Send FAIL")

    if args.to_groups:
        print("\n📤 发送到所有群...")
        success_count, fail_count = await send_to_all_groups(token, card, args.dry_run)
        print(f"\n📊 Done! Success: {success_count}, Fail: {fail_count}")

    if report_data.get("url"):
        print(f"\n📄 周报链接: {report_data['url']}")


if __name__ == "__main__":
    asyncio.run(main())
