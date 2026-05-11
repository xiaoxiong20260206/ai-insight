#!/usr/bin/env python3
"""
update_homepage.py — 首页自动更新统一脚本（v2.0 合并版）
=================================================
合并了日报和周报的首页更新逻辑，一个脚本处理所有场景。

用法:
  # 日报模式
  python3 scripts/update_homepage.py 2026-05-11 --type daily
  
  # 周报模式
  python3 scripts/update_homepage.py 2026-W19 --type weekly --week-title "第19周（5.5 - 5.11）" --week-desc "覆盖90+条资讯 · ..."

  # 验证模式
  python3 scripts/update_homepage.py 2026-05-11 --type daily --verify
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"


# ============ 日报更新逻辑 ============

def update_calendar_daily(index_path: Path, date_str: str) -> bool:
    """更新首页日历数组，添加当天日期"""
    month_str = date_str[:7]
    day_num = str(int(date_str.split("-")[2]))

    content = index_path.read_text(encoding="utf-8")

    if re.search(rf"'{month_str}':.*\b{day_num}\b", content):
        print(f"  ⏭️ 日历已包含 {month_str}/{day_num}")
        return True

    pattern = rf"('{re.escape(month_str)}': \[)([^\]]+)(\])"
    if re.search(pattern, content):
        def add_day(m):
            existing = m.group(2).strip().rstrip(',')
            return m.group(1) + existing + ', ' + day_num + m.group(3)
        new_content = re.sub(pattern, add_day, content)
    else:
        new_content = re.sub(
            r"(const reportsData = \{)\s*\n(\s*')",
            rf"\1\n            '{month_str}': [{day_num}],  // {month_str}日报日期 (最新: {date_str})\n\2",
            content
        )
        if new_content == content:
            print(f"  ❌ 无法自动插入新月日历数组")
            return False

    new_content = re.sub(r'最新: \d{4}-\d{2}-\d{2}', f'最新: {date_str}', new_content)

    if re.search(r"let currentMonth\s*=\s*[0-9]", new_content):
        print(f"  ❌ currentMonth 被硬编码")
        return False

    index_path.write_text(new_content, encoding="utf-8")
    print(f"  ✅ 日历已添加 {day_num}")
    return True


def update_daily_card(index_path: Path, date_str: str) -> bool:
    """更新首页最新日报卡片"""
    month_str = date_str[:7]
    content = index_path.read_text(encoding="utf-8")

    content = re.sub(
        r'href="01-daily-reports/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}\.html"(\s+target="_blank"\s+class="list-item")',
        f'href="01-daily-reports/{month_str}/{date_str}.html"\\1', content)

    d = datetime.strptime(date_str, "%Y-%m-%d")
    date_cn = f'{d.year}年{d.month}月{d.day}日'
    content = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日( AI日报)', date_cn + r'\1', content)

    desc = _extract_daily_desc(date_str)
    content = re.sub(r'(<div class="list-item-desc">)[^<]*(</div>)',
                     lambda m: m.group(1) + desc + m.group(2), content)

    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 日报卡片已更新: {date_cn}")
    return True


def _extract_daily_desc(date_str: str) -> str:
    json_path = PROJECT_ROOT / "data" / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return "今日AI行业动态汇总"
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        parts = [re.sub(r'<[^>]+>', '', ov.get("headline", ""))[:20]
                 for ov in data.get("overview", [])[:4] if ov.get("headline")]
        return ' · '.join(parts) if parts else "今日AI行业动态汇总"
    except Exception:
        return "今日AI行业动态汇总"


def update_report_index(date_str: str) -> bool:
    """更新 01-daily-reports/index.html"""
    month_str = date_str[:7]
    index_path = PROJECT_ROOT / "01-daily-reports" / "index.html"
    if not index_path.exists():
        return True
    content = index_path.read_text(encoding="utf-8")
    report_count = len(list((PROJECT_ROOT / "01-daily-reports" / month_str).glob("*-v3.html")))
    content = re.sub(r'(<div class="stat-value">)\d+(</div><div class="stat-label">日报)',
                     f'\\g<1>{report_count}\\g<2>', content)
    content = re.sub(r'(<div class="stat-value">)\d{4}-\d{2}-\d{2}(</div><div class="stat-label">最新)',
                     f'\\g<1>{date_str}\\g<2>', content)
    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 索引页已更新 (共{report_count}篇)")
    return True


# ============ 周报更新逻辑 ============

def update_weekly_card(index_path: Path, week_id: str, month: str, title: str, desc: str) -> bool:
    """更新首页周报入口卡片"""
    content = index_path.read_text(encoding="utf-8")

    # 更新 href
    content = re.sub(
        r'href="01-daily-reports/\d{4}-\d{2}/weekly-\d{4}-W\d{2}.html"',
        f'href="01-daily-reports/{month}/weekly-{week_id}.html"', content)

    # 更新标题
    content = re.sub(
        r'<div class="wrc-title">AI 周报 · 第\d+周（[\d.]+ - [\d.]+）',
        f'<div class="wrc-title">AI 周报 · {title}', content)

    # 更新描述
    desc_idx = content.find('<div class="wrc-desc">')
    if desc_idx >= 0:
        end_idx = content.find('</div>', desc_idx) + len('</div>')
        content = content[:desc_idx] + f'<div class="wrc-desc">{desc}</div>' + content[end_idx:]

    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 周报卡片已更新: {title}")
    return True


def update_calendar_weekly(index_path: Path, month: str, day: int, week_id: str) -> bool:
    """更新日历JS周报数据"""
    content = index_path.read_text(encoding="utf-8")
    day_str = f"{day}: 'weekly-{week_id}'"

    # 查找周报数据位置
    weekly_pattern = r'weeklyReportsData\s*=\s*\{([^}]+)\}'
    m = re.search(weekly_pattern, content)
    if m:
        existing = m.group(1)
        if day_str not in existing:
            # 在对应月份后面追加
            month_pattern = rf"'{month}':\s*\{{[^}}]+\}}"
            month_match = re.search(month_pattern, existing)
            if month_match:
                old = month_match.group()
                new = old.rstrip("}") + ", " + day_str + "}"
                new_content = content.replace(existing, existing.replace(old, new))
                index_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ 周报日历已更新: {month}/{day}")
                return True

    # fallback: 没找到weeklyReportsData，跳过
    print(f"  ⚠️ 未找到weeklyReportsData，跳过周报日历更新")
    return True


# ============ 公共逻辑 ============

def sync_all_homepages(date_str: str, update_type: str, 
                       week_id: str = "", week_title: str = "", week_desc: str = "",
                       week_month: str = "", week_day: int = 0) -> bool:
    """同步所有版本首页"""
    src = PROJECT_ROOT / "index.html"
    if not src.exists():
        print(f"  ❌ 内部版首页不存在")
        return False

    # 内部版 → public/
    pub = PROJECT_ROOT / "public" / "index.html"
    pub.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # 调用 sync_to_public.py 脱敏 → ai-insight-public/
    external_repo = PROJECT_ROOT.parent / "ai-insight-public"
    if external_repo.exists():
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from sync_to_public import sanitize_html
            sanitized = sanitize_html(src.read_text(encoding="utf-8"))
            (external_repo / "index.html").write_text(sanitized, encoding="utf-8")
            print(f"  ✅ ai-insight-public/index.html 已脱敏同步")
        except Exception as e:
            print(f"  ⚠️ 脱敏同步失败: {e}")

    print(f"  ✅ public/index.html 已同步")
    return True


def verify_homepage(date_str: str = "", week_id: str = "") -> bool:
    """验证所有版本首页"""
    errors = []
    check_str = date_str or week_id

    for label, path in [
        ("内部版", PROJECT_ROOT / "index.html"),
        ("public/", PROJECT_ROOT / "public" / "index.html"),
    ]:
        if not path.exists():
            errors.append(f"❌ {label}不存在")
        elif check_str not in path.read_text(encoding="utf-8"):
            errors.append(f"❌ {label}未包含 {check_str}")

    if errors:
        for e in errors:
            print(f"  {e}")
        return False
    print(f"  ✅ 首页验证通过: {check_str}")
    return True


def main():
    parser = argparse.ArgumentParser(description='首页自动更新统一脚本 v2.0')
    parser.add_argument("date", help="日期 (日报: YYYY-MM-DD, 周报: YYYY-Www 或 YYYY-MM-DD)")
    parser.add_argument("--type", choices=["daily", "weekly"], default="daily", help="更新类型")
    parser.add_argument("--verify", action="store_true", help="只验证不修改")
    parser.add_argument("--week-title", help="周报标题 (周报模式)")
    parser.add_argument("--week-desc", help="周报描述 (周报模式)")
    parser.add_argument("--week-month", help="周报月份 (周报模式, YYYY-MM)")
    parser.add_argument("--week-day", type=int, default=0, help="周报所在日 (周报模式)")
    args = parser.parse_args()

    print(f"\n🏠 首页更新: {args.date} ({args.type})")
    print("=" * 50)

    if args.type == "daily":
        date_str = args.date
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            print(f"❌ 日报日期格式错误: {date_str}")
            sys.exit(1)

        if args.verify:
            ok = verify_homepage(date_str=date_str)
            sys.exit(0 if ok else 1)

        print("\n📋 Step 1: 更新日历数组")
        update_calendar_daily(PROJECT_ROOT / "index.html", date_str)

        print("\n📋 Step 2: 更新日报卡片")
        update_daily_card(PROJECT_ROOT / "index.html", date_str)

        print("\n📋 Step 3: 更新索引页")
        update_report_index(date_str)

        print("\n📋 Step 4: 同步所有版本")
        sync_all_homepages(date_str, "daily")

        print("\n📋 Step 5: 验证")
        ok = verify_homepage(date_str=date_str)

    elif args.type == "weekly":
        week_id = args.date
        if not args.week_title or not args.week_desc or not args.week_month:
            print("❌ 周报模式需要 --week-title, --week-desc, --week-month")
            sys.exit(1)

        if args.verify:
            ok = verify_homepage(week_id=week_id)
            sys.exit(0 if ok else 1)

        print("\n📋 Step 1: 更新周报入口卡片")
        update_weekly_card(PROJECT_ROOT / "index.html", week_id,
                           args.week_month, args.week_title, args.week_desc)

        print("\n📋 Step 2: 更新周报日历数据")
        update_calendar_weekly(PROJECT_ROOT / "index.html", args.week_month, args.week_day, week_id)

        print("\n📋 Step 3: 同步所有版本")
        sync_all_homepages(args.date, "weekly", week_id=week_id,
                           week_title=args.week_title, week_desc=args.week_desc,
                           week_month=args.week_month, week_day=args.week_day)

        print("\n📋 Step 4: 验证")
        ok = verify_homepage(week_id=week_id)

    if ok:
        print(f"\n✅ 首页更新完成！")
    else:
        print(f"\n⚠️ 验证发现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()