#!/usr/bin/env python3
"""AI周报 HTML 展示完整性验证器 (2026-06-30)"""

import sys, re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = ["overview", "top5", "insight", "llm", "coding", "app", "industry", "enterprise", "dailyindex"]
REQUIRED_CLASSES = ["news-card", "board-table", "callout", "doc-header", "table-wrap", "doc-chapter-label"]
FORBIDDEN_WORDS_INTERNAL = []  # 内部版无限制
FORBIDDEN_WORDS_EXTERNAL = ["林克", "沈浪", "AI分身", "MyFlicker", "corp.kuaishou"]

def validate(week_id: str, external: bool = False) -> list:
    # 找 HTML 文件
    for month in ["2026-06", "2026-07"]:
        html_file = PROJECT / "01-daily-reports" / month / f"weekly-{week_id}.html"
        if html_file.exists():
            break
    else:
        return [f"❌ HTML文件不存在: weekly-{week_id}.html"]
    
    with open(html_file, encoding="utf-8") as f:
        html = f.read()
    
    errors = []
    warnings = []
    
    # 1. 文件大小
    if len(html) < 50000:
        errors.append(f"❌ HTML太小: {len(html)} bytes（最小50KB）")
    
    # 2. Section ID 存在
    for sid in REQUIRED_SECTIONS:
        if f'id="{sid}"' not in html:
            errors.append(f"❌ 缺少section: #{sid}")
    
    # 3. Required classes
    for cls in REQUIRED_CLASSES:
        if cls not in html:
            errors.append(f"❌ 缺少class: {cls}")
    
    # 4. 模板变量残留
    leaks = re.findall(r'\{[A-Z_][A-Z_0-9]*(?:\[.*?\])?\}', html)
    if leaks:
        errors.append(f"❌ 模板变量残留: {leaks[:5]}")
    
    # 5. 空href检查
    empty_hrefs = re.findall(r'href=""', html)
    if empty_hrefs:
        warnings.append(f"⚠️ 空href: {len(empty_hrefs)}处")
    
    # 6. 锚点占位URL
    # 页面内导航锚点（#section-id）是正常的，只检测非导航锚点占位
    valid_anchors = {'llm','coding','app','industry','enterprise','overview','top5','insight','linkinsight','dailyindex','vocab','narrative','main-content','sidebar','scrollToTop','readingProgress'}
    anchor_urls = [m for m in re.findall(r'href="#([^"]+)"', html) if m not in valid_anchors and not m.startswith('http')]
    if anchor_urls:
        errors.append(f"❌ 锚点占位URL: {len(anchor_urls)}处: {anchor_urls[:3]}")
    
    # 7. 敏感词（外部版）
    if external:
        for word in FORBIDDEN_WORDS_EXTERNAL:
            cnt = html.count(word)
            if cnt > 0:
                errors.append(f"❌ 外部版敏感词: {word} × {cnt}")
    
    # 8. 深色Header检查
    if "0f172a" not in html:
        warnings.append("⚠️ Header缺少深色渐变背景")
    
    # 9. board-table 用 table-layout: auto
    if "table-layout: auto" not in html and "table-layout:auto" not in html:
        warnings.append("⚠️ board-table 缺少 table-layout:auto")
    
    # 10. overflow-x: auto
    if "overflow-x: auto" not in html and "overflow-x:auto" not in html:
        warnings.append("⚠️ .table-wrap 缺少 overflow-x:auto")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("用法: uv run scripts/validate_weekly_html.py <YYYY-WXX> [--external]")
        sys.exit(1)
    week_id = sys.argv[1]
    external = "--external" in sys.argv
    errors, warnings = validate(week_id, external)
    for e in errors: print(e)
    for w in warnings: print(w)
    if errors:
        print(f"\n❌ 验证失败: {len(errors)} 错误")
        sys.exit(1)
    else:
        print(f"\n✅ 验证通过" + (f" ({len(warnings)} 警告)" if warnings else ""))
        sys.exit(0)

if __name__ == "__main__":
    main()
