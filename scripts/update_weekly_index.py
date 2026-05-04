#!/usr/bin/env python3
"""
周报首页联动更新脚本 v1.1
============================
周报发布后自动更新两版首页（内部版 index.html + 外部版 public/index.html）的：
  1. weeklyReportsData JS 数据（日历上的"有周报"标识）
  2. 周报入口卡片（href + 标题 + 描述）
  3. [v1.1 新增] sync_to_public.py --all --force --with-index（同步周报 HTML 到 public/）

问题背景（经验#71 — 2026-04-07）:
  W14 周报已生成并部署，但两版首页均未更新，导致：
  - 日历上 4.5 没有"有周报"标识
  - 首页入口卡片仍指向 W13
  根因：旧版推送脚本已被废弃，改用 build_insight_mixcard.py + message 工具，靠人工记忆必然遗漏。

使用方式:
  python3 scripts/update_weekly_index.py               # 自动检测最新周报并更新
  python3 scripts/update_weekly_index.py 2026-W14      # 指定更新某周
  python3 scripts/update_weekly_index.py --dry-run     # 只检查，不修改

作者: AI洞察
版本: 1.0.0
"""
import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
INTERNAL_INDEX = PROJECT_ROOT / "index.html"
PUBLIC_INDEX = PROJECT_ROOT / "public" / "index.html"
DAILY_REPORTS = PROJECT_ROOT / "01-daily-reports"


# ── 工具函数 ─────────────────────────────────────────────────

def find_latest_weekly() -> Optional[Tuple[int, int, Path]]:
    """自动找到最新的周报文件，返回 (year, week_num, html_path)"""
    best = None
    for month_dir in sorted(DAILY_REPORTS.iterdir(), reverse=True):
        if not month_dir.is_dir():
            continue
        for f in sorted(month_dir.glob("weekly-*.html"), reverse=True):
            m = re.match(r"weekly-(\d{4})-W(\d{2})\.html", f.name)
            if m:
                year, week = int(m.group(1)), int(m.group(2))
                if best is None or (year, week) > (best[0], best[1]):
                    best = (year, week, f)
    return best


def get_week_end_date(year: int, week_num: int) -> datetime:
    """返回该 ISO 周的最后一天（周日）"""
    monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
    return monday + timedelta(days=6)


def get_week_date_range(year: int, week_num: int) -> Tuple[str, str]:
    """返回 (start_cn, end_cn) 如 ('3.30', '4.5')"""
    monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
    sunday = monday + timedelta(days=6)
    start_cn = f"{monday.month}.{monday.day}"
    end_cn = f"{sunday.month}.{sunday.day}"
    return start_cn, end_cn


def extract_weekly_desc(html_path: Path) -> str:
    """从周报 HTML 提取摘要描述（取 Top5 标题前60字）"""
    try:
        content = html_path.read_text(encoding="utf-8")
        # 尝试提取 <title> 里的描述
        title_m = re.search(r'<meta name="description" content="([^"]{10,100})"', content)
        if title_m:
            return title_m.group(1)[:80]
        # 从 h3/li 里拼接关键词
        items = re.findall(r'<h3[^>]*>([^<]{8,40})</h3>', content)
        if items:
            return " · ".join(i.strip() for i in items[:4])
    except Exception:
        pass
    return "本周AI行业重要动态汇总"


def count_news(html_path: Path) -> str:
    """从周报 HTML 里提取新闻总量标注"""
    try:
        content = html_path.read_text(encoding="utf-8")
        m = re.search(r'新闻总量[：:]\s*(?:约)?(\d+)', content)
        if m:
            return f"覆盖{m.group(1)}+条资讯"
        m = re.search(r'(\d{2,3})\s*条', content)
        if m:
            return f"覆盖{m.group(1)}+条资讯"
    except Exception:
        pass
    return "覆盖70+条资讯"


# ── 核心更新函数 ──────────────────────────────────────────────

def update_weekly_reports_data(html_content: str, year: int, week_num: int,
                               end_day: int, month_str: str) -> Tuple[str, bool]:
    """
    更新 JS 里的 weeklyReportsData 字典
    
    两种情况：
    A. 当月已有条目 → 追加日期
    B. 当月无条目   → 插入新月条目
    
    Returns: (new_content, was_changed)
    """
    weekly_key = f"weekly-{year}-W{week_num:02d}"
    
    # 检查是否已存在
    if weekly_key in html_content:
        return html_content, False  # 已存在，无需更新
    
    # 情况A: 当月已有条目
    month_pattern = re.compile(
        rf"('{re.escape(month_str)}':\s*\{{)([^}}]+)(\}})"
    )
    m = month_pattern.search(html_content)
    if m:
        existing = m.group(2).rstrip()
        new_entry = f"{end_day}: '{weekly_key}'"
        new_content = html_content[:m.start()] + \
                      m.group(1) + existing + f", {new_entry}" + m.group(3) + \
                      html_content[m.end():]
        return new_content, True
    
    # 情况B: 当月无条目，在 weeklyReportsData 第一个月前插入
    insert_pattern = re.compile(
        r"(const weeklyReportsData\s*=\s*\{\s*\n\s*)'(\d{4}-\d{2})':"
    )
    mi = insert_pattern.search(html_content)
    if mi:
        new_line = f"'{month_str}': {{{end_day}: '{weekly_key}'}},  // {month_str}第{week_num:02d}周\n            "
        new_content = html_content[:mi.start(1)] + mi.group(1) + new_line + html_content[mi.start(2):]
        return new_content, True
    
    print(f"  ⚠️  无法定位 weeklyReportsData，请手动更新")
    return html_content, False


def update_weekly_card(html_content: str, year: int, week_num: int,
                       month_str: str, start_cn: str, end_cn: str,
                       desc: str, news_count: str) -> Tuple[str, bool]:
    """
    更新周报入口卡片的 href + 标题 + 描述
    
    Returns: (new_content, was_changed)
    """
    weekly_key = f"weekly-{year}-W{week_num:02d}"
    new_href = f"01-daily-reports/{month_str}/{weekly_key}.html"
    new_title = f"AI 周报 · 第{week_num}周（{start_cn} - {end_cn}）"
    new_desc_text = f"{news_count} · {desc}"[:120]
    
    # 检查是否已是最新
    if new_href in html_content and f"第{week_num}周" in html_content:
        return html_content, False
    
    # 替换 weekly-report-card 的 href
    card_pattern = re.compile(
        r'(<a\s+href=")01-daily-reports/\d{4}-\d{2}/weekly-[^"]+(".*?class="weekly-report-card">)',
        re.DOTALL
    )
    if card_pattern.search(html_content):
        html_content = card_pattern.sub(rf'\g<1>{new_href}\g<2>', html_content)
    
    # 替换 wrc-title
    title_pattern = re.compile(
        r'(<div class="wrc-title">)[^<]*(<span class="wrc-badge">最新</span></div>)'
    )
    if title_pattern.search(html_content):
        html_content = title_pattern.sub(
            rf'\g<1>{new_title}\g<2>', html_content
        )
    
    # 替换 wrc-desc
    desc_pattern = re.compile(
        r'(<div class="wrc-desc">)[^<]*(</div>)'
    )
    if desc_pattern.search(html_content):
        html_content = desc_pattern.sub(
            rf'\g<1>{new_desc_text}\g<2>', html_content
        )
    
    return html_content, True


def update_index_file(index_path: Path, year: int, week_num: int,
                      end_date: datetime, dry_run: bool = False) -> bool:
    """更新单个 index.html 文件"""
    if not index_path.exists():
        print(f"  ⚠️  文件不存在: {index_path}")
        return False
    
    month_str = end_date.strftime("%Y-%m")
    end_day = end_date.day
    start_cn, end_cn = get_week_date_range(year, week_num)
    
    # 找周报 HTML 提取描述
    weekly_html = DAILY_REPORTS / month_str / f"weekly-{year}-W{week_num:02d}.html"
    if not weekly_html.exists():
        # 尝试 public/ 版
        weekly_html = PROJECT_ROOT / "public" / "01-daily-reports" / month_str / f"weekly-{year}-W{week_num:02d}.html"
    
    news_count = count_news(weekly_html) if weekly_html.exists() else "覆盖70+条资讯"
    desc = extract_weekly_desc(weekly_html) if weekly_html.exists() else ""
    
    content = index_path.read_text(encoding="utf-8")
    original = content
    
    # Step 1: 更新 weeklyReportsData
    content, changed1 = update_weekly_reports_data(content, year, week_num, end_day, month_str)
    
    # Step 2: 更新入口卡片
    content, changed2 = update_weekly_card(content, year, week_num, month_str, start_cn, end_cn, desc, news_count)
    
    changed = changed1 or changed2
    
    rel_path = index_path.relative_to(PROJECT_ROOT) if index_path.is_relative_to(PROJECT_ROOT) else index_path
    
    if not changed:
        print(f"  ⏭️  {rel_path}: 已是最新（W{week_num:02d} 已存在），无需更新")
        return False
    
    if dry_run:
        print(f"  [DRY-RUN] {rel_path}: 会更新 weeklyReportsData={changed1}, 入口卡片={changed2}")
        return True
    
    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ {rel_path}: 已更新（weeklyReportsData={changed1}, 入口卡片={changed2}）")
    return True


# ── 主流程 ────────────────────────────────────────────────────

def run(week_str: str = None, dry_run: bool = False) -> bool:
    """
    主入口。
    
    Args:
        week_str: "2026-W14" 格式，None 表示自动检测最新周报
        dry_run: 只检查不修改
    
    Returns: True = 有更新发生，False = 无需更新或失败
    """
    print("🔄 周报首页联动更新 v1.0")
    print("=" * 45)
    
    # 确定要更新的周
    if week_str:
        m = re.match(r"(\d{4})-W(\d{1,2})", week_str)
        if not m:
            print(f"❌ 无效格式: {week_str}，期望 YYYY-WNN")
            return False
        year, week_num = int(m.group(1)), int(m.group(2))
        print(f"📅 指定周: {year}-W{week_num:02d}")
    else:
        result = find_latest_weekly()
        if not result:
            print("❌ 未找到任何周报文件")
            return False
        year, week_num, latest_html = result
        print(f"📅 自动检测最新周报: {year}-W{week_num:02d}  ({latest_html.parent.name}/{latest_html.name})")
    
    end_date = get_week_end_date(year, week_num)
    start_cn, end_cn = get_week_date_range(year, week_num)
    print(f"   覆盖日期: {start_cn} ~ {end_cn}，周末日期: {end_date.strftime('%Y-%m-%d')}（日历标注在{end_date.day}号）")
    print()
    
    any_changed = False
    
    # 更新内部版
    print("📝 更新内部版首页（index.html）:")
    changed = update_index_file(INTERNAL_INDEX, year, week_num, end_date, dry_run)
    any_changed = any_changed or changed
    
    # 更新 public 版
    print("📝 更新外部版首页（public/index.html）:")
    changed = update_index_file(PUBLIC_INDEX, year, week_num, end_date, dry_run)
    any_changed = any_changed or changed
    
    print()
    if any_changed and not dry_run:
        print("✅ 首页联动更新完成！")
        
        # ⭐ 新增：同步周报 HTML 到 public/ 目录（经验#71加固）
        # 确保 public/ 里有周报 HTML，供 sync_to_external.py 推送到外部仓库
        print()
        print("📝 同步周报 HTML 到 public/ 目录...")
        import subprocess, sys
        sync_pub_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "sync_to_public.py"),
             "--all", "--force", "--with-index"],
            cwd=str(PROJECT_ROOT)
        )
        if sync_pub_result.returncode == 0:
            print("  ✅ public/ 同步完成（周报 HTML + 首页均已写入 public/）")
        else:
            print("  ⚠️  public/ 同步失败，请手动执行：")
            print("      python3 scripts/sync_to_public.py --all --force --with-index")
        
        print()
        print("   后续步骤（由调用方（Agent message 工具发送后手动同步）执行）:")
        print(f"     git add . && git commit -m '📊 周报首页联动 {year}-W{week_num:02d}'")
        print(f"     python3 scripts/sync_to_external.py --full --verify")
    elif not any_changed:
        print("✅ 两版首页均已是最新，无需更新")
    
    return any_changed


def main():
    parser = argparse.ArgumentParser(
        description="周报首页联动更新工具 v1.0",
        epilog="""
示例:
  %(prog)s                    # 自动检测最新周报并更新
  %(prog)s 2026-W14           # 指定更新 W14
  %(prog)s --dry-run          # 预览模式（不修改文件）
        """
    )
    parser.add_argument("week", nargs="?", help="周标识 YYYY-WNN，不填则自动检测")
    parser.add_argument("--dry-run", action="store_true", help="只检查，不实际修改")
    args = parser.parse_args()
    
    success = run(args.week, args.dry_run)
    sys.exit(0 if success is not False else 1)


if __name__ == "__main__":
    main()
