#!/usr/bin/env python3
"""
AI洞察首页周报入口更新脚本 v1.0
=================================
每次生成新周报后，自动更新内外版首页的：
1. 周报入口卡片（wrc-title + href + wrc-desc）
2. 日历JS周报数据（weeklyReportsData）

使用方式:
  python scripts/update_homepage_weekly.py --week W19 --title "第19周（5.5 - 5.11）" --desc "覆盖90+条资讯+深度调研 · ..." --month 2026-05 --day 11

作者: 林克
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "index.html"
PUBLIC_INDEX = PROJECT_ROOT / "public" / "index.html"
EXTERNAL_INDEX = PROJECT_ROOT.parent / "ai-insight-public" / "index.html"


def update_weekly_card(html: str, week_id: str, month: str, title: str, desc: str) -> str:
    """更新周报入口卡片"""
    # 更新 href
    old_href_pattern = r'href="01-daily-reports/\d{4}-\d{2}/weekly-\d{4}-W\d{2}.html"'
    new_href = f'href="01-daily-reports/{month}/weekly-{week_id}.html"'
    html = re.sub(old_href_pattern, new_href, html)

    # 更新标题
    old_title_pattern = r'<div class="wrc-title">AI 周报 · 第\d+周（[\d.]+ - [\d.]+）'
    new_title = f'<div class="wrc-title">AI 周报 · {title}'
    html = re.sub(old_title_pattern, new_title, html)

    # 更新描述
    old_desc_pattern = r'<div class="wrc-desc">[^<]+</div>'
    new_desc = f'<div class="wrc-desc">{desc}</div>'
    # 只替换第一个匹配（周报卡片描述）
    html = html.replace(html[html.find('<div class="wrc-desc">'):html.find('</div>', html.find('<div class="wrc-desc">'))+len('</div>')], new_desc)

    return html


def update_calendar_js(html: str, month: str, day: int, week_id: str) -> str:
    """更新日历JS周报数据"""
    # 检查是否已有该月数据
    month_pattern = f"'{month}':"
    if month_pattern in html:
        # 已有该月，追加日期
        month_line_pattern = rf"'{month}':\s*\{{[^}}]+\}}"
        month_line_match = re.search(month_line_pattern, html)
        if month_line_match:
            old_line = month_line_match.group()
            # 检查是否已有该日期
            day_pattern = rf"{day}:\s*'weekly-\d{4}-W\d{{2}}'"
            if not re.search(day_pattern, old_line):
                # 插入新日期
                new_line = old_line.rstrip()  # Remove trailing }
                new_line = new_line[:-1] + f", {day}: 'weekly-{week_id}'}}"
                html = html.replace(old_line, new_line)
    else:
        # 新月份，添加整行
        # 找到合适位置（按月份排序）
        year = month.split('-')[0]
        prev_month_num = int(month.split('-')[1]) - 1
        prev_month = f"{year}-{prev_month_num:02d}"
        
        new_line = f"            '{month}': {{4: 'weekly-{week_id[:-3]}-W{int(week_id.split(\"W\")[1])-1:02d}', {day}: 'weekly-{week_id}'}},  // {week_id}"
        
        # 在前一个月的数据行后面插入
        prev_pattern = rf"'{prev_month}':\s*\{{[^}}]+\}},\s*//[^\n]+"
        prev_match = re.search(prev_pattern, html)
        if prev_match:
            html = html.replace(prev_match.group(), prev_match.group() + '\n' + new_line)
        else:
            # fallback: 在最后一个月数据行后面插入
            last_month_pattern = r"'\d{4}-\d{2}':\s*\{[^}]+\},\s*//[^\n]+"
            last_match = re.findall(last_month_pattern, html)
            if last_match:
                html = html.replace(last_match[-1], last_match[-1] + '\n' + new_line)

    return html


def main():
    parser = argparse.ArgumentParser(description='更新首页周报入口')
    parser.add_argument('--week', required=True, help='周ID，如 2026-W19')
    parser.add_argument('--title', required=True, help='标题，如 "第19周（5.5 - 5.11）"')
    parser.add_argument('--desc', required=True, help='描述文字')
    parser.add_argument('--month', required=True, help='月份，如 2026-05')
    parser.add_argument('--day', required=True, type=int, help='周报所在日（周日日期），如 11')
    args = parser.parse_args()

    results = []
    
    # 更新内部版首页
    if INDEX_HTML.exists():
        with open(INDEX_HTML) as f:
            html = f.read()
        html = update_weekly_card(html, args.week, args.month, args.title, args.desc)
        html = update_calendar_js(html, args.month, args.day, args.week)
        with open(INDEX_HTML, 'w') as f:
            f.write(html)
        results.append(f"✅ 内部版首页已更新 ({INDEX_HTML})")
    
    # 更新 public/首页
    if PUBLIC_INDEX.exists():
        with open(PUBLIC_INDEX) as f:
            html = f.read()
        html = update_weekly_card(html, args.week, args.month, args.title, args.desc)
        html = update_calendar_js(html, args.month, args.day, args.week)
        with open(PUBLIC_INDEX, 'w') as f:
            f.write(html)
        results.append(f"✅ public/首页已更新 ({PUBLIC_INDEX})")
    
    # 更新外部版首页
    if EXTERNAL_INDEX.exists():
        with open(EXTERNAL_INDEX) as f:
            html = f.read()
        html = update_weekly_card(html, args.week, args.month, args.title, args.desc)
        html = update_calendar_js(html, args.month, args.day, args.week)
        with open(EXTERNAL_INDEX, 'w') as f:
            f.write(html)
        results.append(f"✅ 外部版首页已更新 ({EXTERNAL_INDEX})")
    
    for r in results:
        print(r)
    
    # 验证
    for path in [INDEX_HTML, PUBLIC_INDEX, EXTERNAL_INDEX]:
        if path.exists():
            with open(path) as f:
                content = f.read()
            wrc_count = len(re.findall(rf"weekly-{args.week}", content))
            print(f"  📍 {path.name}: {wrc_count} 处引用 weekly-{args.week}")

    print("\n⚠️ 下一步：git push 内部版 + 外部版仓库")


if __name__ == "__main__":
    main()