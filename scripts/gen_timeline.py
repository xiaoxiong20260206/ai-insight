#!/usr/bin/env python3
"""
gen_timeline.py — 从深度调研HTML文件自动生成时间轴卡片HTML

核心逻辑：
1. 扫描 02-deep-research/ 下所有主入口 HTML
2. 从每个 HTML 的 tc-meta 提取日期（📅 YYYY-MM-DD）
3. 按月分组，生成 timeline-month → timeline-cards 结构
4. 输出可直接粘贴到 index.html 的 HTML 片段
"""

import re
import os
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_DIR = PROJECT_ROOT / "02-deep-research"

# 目录级入口（子页不单独列出，由主入口代表）
INDEX_ENTRIES = {"index.html", "home.html"}
# 跳过的文件（子章节、附录、封面、发布版）
SKIP_PATTERNS = re.compile(
    r'chapter\d*|appendix|cover-hero|发布版|diagrams|panel-\d'
)

# 类别→CSS class + 图标 + 标签
CATEGORY_MAP = {
    "trends": ("cat-trend", "📈", "趋势"),
    "trend":  ("cat-trend", "📈", "趋势"),
    "companies": ("cat-company", "🏢", "公司"),
    "company": ("cat-company", "🏢", "公司"),
    "people": ("cat-people", "👤", "人物"),
    "topics": ("cat-topic", "🔬", "专题"),
    "topic":  ("cat-topic", "🔬", "专题"),
}

MONTH_NAMES = {
    1: "1月", 2: "2月", 3: "3月", 4: "4月",
    5: "5月", 6: "6月", 7: "7月", 8: "8月",
    9: "9月", 10: "10月", 11: "11月", 12: "12月",
}


def extract_info(html_path: Path):
    """从 HTML 提取日期、标题、描述、类别等"""
    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
    except:
        return None

    # 提取日期（多策略）
    date_str = None
    # 策略1：📅 YYYY-MM-DD（首页/日报风格）
    date_match = re.search(r'📅\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        date_str = date_match.group(1)
    # 策略2：editorial-hero-badge 中的日期
    if not date_str:
        date_match = re.search(r'editorial-hero-badge[^>]*>.*?(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            date_str = date_match.group(1)
    # 策略3：meta date 标签
    if not date_str:
        date_match = re.search(r'<meta[^>]*date[^>]*content="(\d{4}-\d{2}-\d{2})"', content)
        if date_match:
            date_str = date_match.group(1)
    # 策略4：文件名中的日期（如 xxx-2026-05-14.html）
    if not date_str:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html_path.stem)
        if date_match:
            date_str = date_match.group(1)
    # 策略5：文件修改时间（git log）
    if not date_str:
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%as", "--", str(html_path)],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0 and result.stdout.strip():
                date_str = result.stdout.strip()
        except:
            pass

    if not date_str:
        return None

    # 提取标题（多策略）
    title = html_path.stem.replace("-", " ").replace("_", " ")
    # 策略1：tc-title（首页卡片风格）
    title_match = re.search(r'tc-title[^>]*>([^<]+)<', content)
    if title_match:
        title = title_match.group(1).strip()
    # 策略2：editorial-hero h1（深度调研风格）
    if not title_match:
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        if h1_match:
            h1_raw = h1_match.group(1)
            # 清理 HTML 标签
            title = re.sub(r'<[^>]+>', '', h1_raw).strip()
            # 截断过长标题
            if len(title) > 60:
                title = title[:57] + "..."
    # 策略3：<title> 标签
    if not title_match and not h1_match:
        title_match2 = re.search(r'<title>([^<]+)</title>', content)
        if title_match2:
            title = title_match2.group(1).split("|")[0].strip()

    # 提取描述（多策略）
    desc = ""
    # 策略1：tc-desc
    desc_match = re.search(r'tc-desc[^>]*>([^<]+)<', content)
    if desc_match:
        desc = desc_match.group(1).strip()
    # 策略2：meta description
    if not desc:
        desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', content)
        if desc_match:
            desc = desc_match.group(1).strip()
    # 截断
    if len(desc) > 120:
        desc = desc[:117] + "..."

    # 提取 meta 信息（从 tc-meta）
    meta_match = re.search(r'tc-meta[^>]*>([^<]+)<', content)
    meta = meta_match.group(1).strip() if meta_match else f"📅 {date_str}"

    # 推断类别（从文件路径）
    rel_path = html_path.relative_to(RESEARCH_DIR)
    parts = rel_path.parts
    category = "topic"  # 默认
    for part in parts:
        if part in CATEGORY_MAP:
            category = part.rstrip("s")  # trends→trend, companies→company
            break

    # 推断类别标签（从 tc-tag）
    tag_match = re.search(r'tc-tag (trend|company|topic|people)', content)
    if tag_match:
        category = tag_match.group(1)

    # 图标
    icon_match = re.search(r'tc-icon[^>]*>([^<]+)<', content)
    icon = icon_match.group(1).strip() if icon_match else CATEGORY_MAP.get(category, ("", "🔬", "专题"))[1]

    return {
        "date": date_str,
        "title": title,
        "desc": desc,
        "meta": meta,
        "icon": icon,
        "category": category,
        "rel_path": f"02-deep-research/{rel_path}",
        "filename": html_path.stem,
    }


def find_main_entries(directory: Path):
    """找到每个调研主题的主入口 HTML"""
    entries = []

    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        rel = root_path.relative_to(directory)
        parts = rel.parts

        # 跳过 images 目录
        if "images" in parts:
            continue

        for f in files:
            if not f.endswith(".html"):
                continue
            if SKIP_PATTERNS.search(f):
                continue

            filepath = root_path / f

            # 目录级入口：index.html 或 home.html 只取一个
            if f in INDEX_ENTRIES:
                # 确保不是子章节的 index（如 chapter1/index.html）
                parent = filepath.parent.name
                if SKIP_PATTERNS.search(parent):
                    continue
                entries.append(filepath)
            else:
                # 独立 HTML 文件（如 anthropic-financial-agents-new-org-model.html）
                # 排除和目录同名的 index 重复
                entries.append(filepath)

    return entries


def gen_card_html(info: dict) -> str:
    """生成单个 timeline-card HTML"""
    cat_info = CATEGORY_MAP.get(info["category"], ("cat-topic", "🔬", "专题"))
    css_class = cat_info[0]
    icon = info["icon"] or cat_info[1]
    tag_name = cat_info[2]

    return f'''                            <a href="{info['rel_path']}" target="_blank" class="timeline-card {css_class}">
                                <div class="tc-header">
                                    <span class="tc-icon">{icon}</span>
                                    <span class="tc-title">{info['title']}</span>
                                    <span class="tc-tag {info['category']}">{tag_name}</span>
                                </div>
                                <div class="tc-desc">{info['desc']}</div>
                                <div class="tc-meta">{info['meta']}</div>
                            </a>'''


def gen_month_html(month_key: str, reports: list) -> str:
    """生成单个 timeline-month HTML"""
    if month_key == "earlier":
        label = "更早"
        title = "早期积累"
        label_style = ' style="font-size:10px;"'
        title_style = ' style="color:var(--color-text-secondary)"'
    else:
        year, month = month_key.split("-")
        label = f"{MONTH_NAMES[int(month)]}<br>{year}"
        title = f"{year}年{int(month)}月"
        label_style = ""
        title_style = ""

    cards = "\n".join(gen_card_html(r) for r in reports)

    return f'''                    <div class="timeline-month" data-month="{month_key}">
                        <div class="timeline-month-header">
                            <div class="timeline-month-label"{label_style}>{label}</div>
                            <div class="timeline-month-dot">
                                <div class="timeline-dot-outer"><div class="timeline-dot-inner"></div></div>
                            </div>
                            <div class="timeline-month-info">
                                <span class="timeline-month-title"{title_style}>{title}</span>
                                <span class="timeline-month-count">{len(reports)}篇</span>
                            </div>
                        </div>
                        <div class="timeline-cards">
{cards}
                        </div>
                    </div>'''


def main():
    print("🔍 扫描深度调研目录...")
    entries = find_main_entries(RESEARCH_DIR)
    print(f"   找到 {len(entries)} 个 HTML 入口")

    # 提取信息
    reports = []
    seen = set()  # 去重：同一目录的 index.html 和其他文件
    for entry in entries:
        info = extract_info(entry)
        if info is None:
            continue
        # 用目录路径去重（一个调研主题只出现一次）
        dedup_key = str(Path(info["rel_path"]).parent)
        if dedup_key in seen and Path(info["rel_path"]).name != "index.html":
            continue
        # 特殊：独立 HTML 文件（不与 index 重复）
        if Path(info["rel_path"]).name == "index.html":
            seen.add(dedup_key)
        reports.append(info)

    print(f"   有效调研: {len(reports)} 篇")

    # 按月分组
    by_month = defaultdict(list)
    for r in reports:
        ym = r["date"][:7]  # YYYY-MM
        by_month[ym].append(r)

    # 排序：月份倒序
    sorted_months = sorted(by_month.keys(), reverse=True)

    # 将3月以前归入 "earlier"
    earlier_reports = []
    main_months = []
    for m in sorted_months:
        if m < "2026-03":
            earlier_reports.extend(by_month[m])
        else:
            main_months.append(m)

    # 每月内按日期倒序
    for m in main_months:
        by_month[m].sort(key=lambda r: r["date"], reverse=True)
    earlier_reports.sort(key=lambda r: r["date"], reverse=True)

    # 生成 HTML
    html_parts = []
    for m in main_months:
        html_parts.append(gen_month_html(m, by_month[m]))
    if earlier_reports:
        html_parts.append(gen_month_html("earlier", earlier_reports))

    output = "\n\n".join(html_parts)

    # 输出
    print(f"\n📋 生成 {len(main_months)} 个月份分组 + {len(earlier_reports)} 早期报告")
    for m in main_months:
        print(f"   {m}: {len(by_month[m])} 篇")
    if earlier_reports:
        print(f"   earlier: {len(earlier_reports)} 篇")

    # 保存到文件
    output_path = PROJECT_ROOT / "scripts" / "_timeline_output.html"
    output_path.write_text(output, encoding="utf-8")
    print(f"\n✅ 输出到: {output_path}")
    print("   使用方法: 将此内容替换 index.html 中 <!-- TIMELINE_START --> 和 <!-- TIMELINE_END --> 之间的内容")


if __name__ == "__main__":
    main()
