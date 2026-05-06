#!/usr/bin/env python3
"""
周报HTML超链接注入脚本 v1.0
=============================
从日报JSON提取URL，自动注入到周报HTML的事件表格和Top 5卡片中。

用法：
  python3 scripts/inject_weekly_links.py weekly-2026-W18
  python3 scripts/inject_weekly_links.py weekly-2026-W18 --dry-run
"""
import argparse
import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DAILY_DIR = PROJECT_ROOT / "01-daily-reports"
DATA_DIR = PROJECT_ROOT / "data"


def find_weekly_html(week_str: str) -> Path:
    """定位周报HTML文件"""
    m = re.match(r"weekly-(\d{4})-W(\d{2})", week_str)
    if not m:
        raise ValueError(f"Invalid format: {week_str}")
    year, week = int(m.group(1)), int(m.group(2))
    
    # Calculate month directory from week dates
    from datetime import datetime, timedelta
    monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    
    # Try both months (week might span two months)
    for month_str in [monday.strftime("%Y-%m"), sunday.strftime("%Y-%m")]:
        html_path = DAILY_DIR / month_str / f"{week_str}.html"
        if html_path.exists():
            return html_path
    
    raise FileNotFoundError(f"Cannot find {week_str}.html")


def extract_urls_from_daily_jsons(week_str: str) -> dict:
    """从7天的日报JSON提取所有新闻URL"""
    m = re.match(r"weekly-(\d{4})-W(\d{2})", week_str)
    year, week = int(m.group(1)), int(m.group(2))
    
    from datetime import datetime, timedelta
    monday = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    
    url_map = {}  # short_title -> (url, source, date)
    
    for i in range(7):
        date = monday + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        json_path = DATA_DIR / f"daily-content-{date_str}.json"
        
        if not json_path.exists():
            print(f"  ⚠️ Missing: {json_path}")
            continue
        
        with open(json_path, encoding="utf-8") as f:
            d = json.load(f)
        
        tabs = d.get("tabs", [])
        for tab in tabs:
            news_dict = tab.get("news", {})
            for region in ["overseas", "china"]:
                items = news_dict.get(region, [])
                for item in items:
                    title = item.get("title", "")
                    url = item.get("url", "")
                    source = item.get("source", "")
                    if url and title:
                        # Use shortened title as key
                        url_map[title[:80]] = {
                            "url": url,
                            "source": source,
                            "date": date_str,
                            "full_title": title,
                        }
    
    return url_map


def fuzzy_match(text: str, url_map: dict, threshold: float = 0.35) -> dict:
    """模糊匹配HTML中的事件描述到日报JSON中的URL"""
    best_match = None
    best_score = 0
    
    # Clean text for matching
    clean_text = re.sub(r'[⭐🌟🔥💎🧠⌨️📱🏭🔄📋📊👀📅📖🌐💡🏆📌🏗️💰🎯🤖✅❌⚠️🔴🟡🟢]', '', text)
    clean_text = clean_text.strip()
    
    for key, info in url_map.items():
        # Compare key phrases
        score = SequenceMatcher(None, clean_text[:60], key[:60]).ratio()
        if score > best_score:
            best_score = score
            best_match = info
    
    if best_score >= threshold and best_match:
        return best_match
    return None


def inject_links_into_html(html_path: Path, url_map: dict, dry_run: bool = False) -> bool:
    """将超链接注入周报HTML"""
    content = html_path.read_text(encoding="utf-8")
    original = content
    changes = 0
    
    # 1. Inject links into Top 5 card source lines
    # Pattern: <div class="news-card-source">📎 SourceName · Date</div>
    # → <div class="news-card-source">📎 <a href="URL" target="_blank">SourceName</a> · Date</div>
    
    # Extract Top 5 card titles for URL lookup
    top5_pattern = re.compile(
        r'<div class="news-card-title">([^<]+)</div>\s*<div class="news-card-source">📎 ([^·]+)· ([^<]+)</div>',
        re.DOTALL
    )
    
    for match in top5_pattern.finditer(content):
        title = match.group(1).strip()
        source = match.group(2).strip()
        date_str = match.group(3).strip()
        
        match_info = fuzzy_match(title, url_map)
        if match_info:
            url = match_info["url"]
            # Replace source line
            old_source_line = f'<div class="news-card-source">📎 {source}· {date_str}</div>'
            new_source_line = f'<div class="news-card-source">📎 <a href="{url}" target="_blank">{source}</a> · {date_str}</div>'
            
            if old_source_line in content:
                content = content.replace(old_source_line, new_source_line)
                changes += 1
                print(f"  ✅ Top5 source: {source} → {url[:60]}...")
    
    # 2. Inject links into event table rows
    # Pattern: <td>Event description text</td><td>SourceName</td>
    # → <td><a href="URL" target="_blank">Event description text</a></td><td><a href="URL" target="_blank">SourceName</a></td>
    
    table_row_pattern = re.compile(
        r'<tr><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td></tr>'
    )
    
    for match in table_row_pattern.finditer(content):
        date_cell = match.group(1).strip()
        event_text = match.group(2).strip()
        source_cell = match.group(3).strip()
        star_cell = match.group(4).strip()
        
        match_info = fuzzy_match(event_text, url_map)
        if match_info:
            url = match_info["url"]
            actual_source = match_info["source"] or source_cell
            
            old_row = f'<tr><td>{date_cell}</td><td>{event_text}</td><td>{source_cell}</td><td>{star_cell}</td></tr>'
            new_row = f'<tr><td>{date_cell}</td><td><a href="{url}" target="_blank">{event_text}</a></td><td><a href="{url}" target="_blank">{source_cell}</a></td><td>{star_cell}</td></tr>'
            
            if old_row in content:
                content = content.replace(old_row, new_row, 1)  # Replace only first occurrence
                changes += 1
                print(f"  ✅ Table event: {event_text[:40]}... → {url[:60]}...")
    
    if changes == 0:
        print("  ⚠️ No links injected - check URL map and HTML content")
        return False
    
    if dry_run:
        print(f"\n  [DRY-RUN] {changes} links would be injected")
        return True
    
    html_path.write_text(content, encoding="utf-8")
    print(f"\n  ✅ {changes} links injected into {html_path.name}")
    
    # Verify file size still > 50KB
    size = html_path.stat().st_size
    print(f"  File size: {size} bytes ({'✅ > 50KB' if size > 50000 else '⚠️ < 50KB'})")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="周报HTML超链接注入脚本 v1.0")
    parser.add_argument("week", help="周标识，如 weekly-2026-W18")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不修改文件")
    args = parser.parse_args()
    
    print("🔗 周报HTML超链接注入 v1.0")
    print("=" * 45)
    
    # Find HTML file
    print(f"📅 定位周报: {args.week}")
    try:
        html_path = find_weekly_html(args.week)
        print(f"   文件: {html_path}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Extract URLs from daily JSONs
    print(f"\n📝 从日报JSON提取URL...")
    url_map = extract_urls_from_daily_jsons(args.week)
    print(f"   提取到 {len(url_map)} 条新闻URL")
    
    # Inject links
    print(f"\n🔗 注入超链接到 {html_path.name}...")
    success = inject_links_into_html(html_path, url_map, args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()