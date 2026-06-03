#!/usr/bin/env python3
"""统计卡片自动校准：从实际文件计算首页 stat-value 数字。

用法: uv run scripts/calibrate_stats.py [--print] [--write]
  --print: 只打印实际数值，不写入文件
  --write: 写入首页 HTML
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def count_tracking_entries(index_html: str) -> dict:
    """从首页HTML统计追踪体系条目数"""
    # 统计表格行（排除表头行 <thead>）
    people_match = re.search(
        r'(?<=人物追踪).*?(?=公司追踪)',
        index_html, re.DOTALL
    )
    companies_match = re.search(
        r'(?<=公司追踪).*?$',
        index_html, re.DOTALL
    )
    
    people_count = 0
    companies_count = 0
    
    if people_match:
        # 统计 <tr> 行，排除 <thead> 和 <th> 行
        trs = re.findall(r'<tr>.*?</tr>', people_match.group(), re.DOTALL)
        people_count = sum(1 for tr in trs if '<th>' not in tr)
    
    if companies_match:
        trs = re.findall(r'<tr>.*?</tr>', companies_match.group(), re.DOTALL)
        companies_count = sum(1 for tr in trs if '<th>' not in tr)
    
    return {"people": people_count, "companies": companies_count}


def count_deep_research() -> int:
    """统计首页时间轴上的深度调研专题数"""
    index_path = PROJECT_ROOT / "index.html"
    if not index_path.exists():
        return 0
    content = index_path.read_text(encoding="utf-8")
    # 时间轴中每个调研卡片有一个唯一链接
    links = set(re.findall(r'href="02-deep-research/[^"]*"', content))
    return len(links)


def count_daily_weekly() -> dict:
    """统计日报+周报数"""
    reports_dir = PROJECT_ROOT / "public" / "01-daily-reports"
    if not reports_dir.exists():
        return {"daily": 0, "weekly": 0}
    
    dailies = len([f for f in reports_dir.rglob("*.html") 
                   if not f.name.startswith("weekly-") and not f.name == "index.html"])
    weeklies = len(list(reports_dir.rglob("weekly-*.html")))
    
    return {"daily": dailies, "weekly": weeklies}


def calibrate(index_path: Path, dry_run: bool = False) -> dict:
    """校准首页统计卡片"""
    content = index_path.read_text(encoding="utf-8")
    
    tracking = count_tracking_entries(content)
    dr_count = count_deep_research()
    dw = count_daily_weekly()
    total_reports = dw["daily"] + dw["weekly"]
    
    stats = {
        "追踪人物": f"{tracking['people']}+",
        "追踪公司": f"{tracking['companies']}+",
        "信息源": "280+",  # 无法自动统计，保持现状
        "深度调研": str(dr_count),
        "日报 / 周报": f"{total_reports}+",
    }
    
    if dry_run:
        print("=== 统计卡片实际数值 ===")
        for label, value in stats.items():
            print(f"  {label}: {value}")
        print(f"  (追踪表格: {tracking['people']}人 + {tracking['companies']}公司)")
        print(f"  (深度调研: {dr_count}篇)")
        print(f"  (日报: {dw['daily']}篇 + 周报: {dw['weekly']}期 = {total_reports})")
        return stats
    
    # 写入首页
    updated = content
    for label, value in stats.items():
        # 匹配模式: <div class="stat-value {color}">NUMBER</div>\n<div class="stat-label">LABEL</div>
        pattern = rf'(<div class="stat-value [^"]*">)[^<]*(</div>\s*<div class="stat-label">\s*{re.escape(label)})'
        updated = re.sub(pattern, rf'\g<1>{value}\g<2>', updated)
    
    index_path.write_text(updated, encoding="utf-8")
    print("✅ 统计卡片已校准")
    return stats


if __name__ == "__main__":
    index_path = PROJECT_ROOT / "index.html"
    if not index_path.exists():
        print("❌ index.html 不存在", file=sys.stderr)
        sys.exit(1)
    
    if "--print" in sys.argv:
        calibrate(index_path, dry_run=True)
    elif "--write" in sys.argv:
        calibrate(index_path, dry_run=False)
    else:
        print("用法: uv run scripts/calibrate_stats.py [--print | --write]")
        sys.exit(1)