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

# 从 config.py SSoT 读取 URL
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from config import INTERNAL_PAGES_BASE as INTERNAL_BASE


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

    # 更新 href（仅替换周报入口卡片，不动往期pills — #124防复发）
    # 限定在包含 class="weekly-report-card" 的 <a> 标签内替换
    # 注意：HTML中href在class前面：href="..." class="weekly-report-card"
    def replace_card_href(match):
        return match.group(1) + f'01-daily-reports/{month}/weekly-{week_id}.html' + match.group(2)
    content = re.sub(
        r'(<a href=")01-daily-reports/\d{4}-\d{2}/weekly-\d{4}-W\d{2}\.html("[^>]*class="weekly-report-card"[^>]*>)',
        replace_card_href, content)

    # 更新标题
    content = re.sub(
        r'<div class="wrc-title">AI 周报 · 第\d+周（[\d./\-]+ - [\d./\-]+）',
        f'<div class="wrc-title">AI 周报 · {title}', content)
    
    # 更新描述
    if desc:
        content = re.sub(
            r'<div class="wrc-desc">.*?</div>',
            f'<div class="wrc-desc">{desc}</div>', content, count=1)
    
    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 周报卡片已更新: {title}")
    return True


def update_weekly_pill(index_path: Path, week_id: str, month: str, date_range: str) -> bool:
    """在首页往期周报pills区新增当前周报的pill链接"""
    content = index_path.read_text(encoding="utf-8")
    
    # pill HTML模板
    pill_html = f'''                        <a href="01-daily-reports/{month}/weekly-{week_id}.html" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; background: var(--color-bg-table-header); border: 1px solid var(--color-border-light); border-radius: var(--radius-full); font-size: 12px; color: var(--color-info); text-decoration: none; transition: all 0.15s;">{week_id}<span style="font-size: 10px; color: var(--color-text-muted);">{date_range}</span></a>'''
    
    # 检查是否已存在该pill
    if f'weekly-{week_id}.html' in content and '往期周报' in content:
        print(f"  ⏭️ 周报pill已包含 {week_id}")
        return True
    
    # 在往期周报区块开头插入新pill（最新的排在最前）
    pill_marker = '                        <a href="01-daily-reports/'
    # 找到往期周报区块的第一个pill
    pills_section = '<!-- 往期周报快速入口 -->'
    if pills_section not in content:
        print(f"  ⚠️ 未找到往期周报区块，跳过pill更新")
        return True  # 不是硬性失败
    
    # 在第一个pill之前插入新pill
    # 找往期周报区块后面的第一个pill链接
    pills_start = content.find(pills_section)
    if pills_start == -1:
        print(f"  ⚠️ 未找到往期周报区块标记")
        return True
    
    # 从pills_section往后找到第一个pill <a>标签
    first_pill_pos = content.find(pill_marker, pills_start)
    if first_pill_pos == -1:
        print(f"  ⚠️ 未找到往期周报pill链接")
        return True
    
    # 在第一个pill前插入新pill+换行
    insert_pos = first_pill_pos
    content = content[:insert_pos] + pill_html + '\n' + content[insert_pos:]
    
    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 周报pill已添加 {week_id} ({date_range})")
    return True


def update_calendar_weekly(index_path: Path, month: str, day: int, week_id: str) -> bool:
    """更新日历JS周报数据"""
    content = index_path.read_text(encoding="utf-8")
    day_str = f"{day}: 'weekly-{week_id}'"

    # 快速检查：如果日历区域已包含该条目，直接返回成功
    # 只在 weeklyReportsData 变量块内搜索，避免误匹配卡片链接等区域
    weekly_block_pattern_quick = r'weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;'
    m_quick = re.search(weekly_block_pattern_quick, content)
    if m_quick and day_str in m_quick.group(1):
        print(f"  ⏭️ 周报日历已包含 {month}/{day} ({week_id})，无需更新")
        return True
    # fallback: 也在月份行模式中检查
    month_line_pattern_quick = rf"'{month}':\s*\{{([^}}]*)\}}"
    m2_quick = re.search(month_line_pattern_quick, content)
    if m2_quick and day_str in m2_quick.group(1):
        print(f"  ⏭️ 周报日历已包含 {month}/{day} ({week_id})，无需更新")
        return True

    # Strategy 1: 匹配 weeklyReportsData 变量（值含嵌套{}，需要非贪婪多层匹配）
    weekly_block_pattern = r'weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;'
    m = re.search(weekly_block_pattern, content)
    if m:
        existing = m.group(1)
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
        else:
            # 月份不存在，追加新月份行
            last_month_pattern = r"'(\d{4}-\d{2})':\s*\{[^}]+\}\s*(?:,\s*)?(//[^\n]*)?"
            all_months = list(re.finditer(last_month_pattern, existing))
            if all_months:
                last_m = all_months[-1]
                new_month_line = f"    '{month}': {{{day_str}}},  // {week_id}"
                insert_pos = last_m.end()
                new_existing = existing[:insert_pos] + "\n            " + new_month_line + existing[insert_pos:]
                new_content = content.replace(existing, new_existing)
                index_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ 周报日历追加新月: {month}/{day}")
                return True

    # Strategy 2: 直接搜索月份行模式（无 weeklyReportsData 变量名）
    month_line_pattern = rf"'{month}':\s*\{{([^}}]*)\}}"
    m2 = re.search(month_line_pattern, content)
    if m2:
        old_line = m2.group(0)
        new_line = old_line.rstrip("}") + ", " + day_str + "}"
        new_content = content[:m2.start()] + new_line + content[m2.end():]
        index_path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ 周报日历已更新(直接匹配): {month}/{day}")
        return True

    # 最终 fallback: 没找到任何周报日历数据 — hard fail
    print(f"  ❌ 未找到周报日历数据，无法更新日历（期望包含 weeklyReportsData 或月份行）")
    return False


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
    
    # ⚡ 统计卡片自动校准（P1 — 每次同步首页时自动校准）
    try:
        from calibrate_stats import calibrate
        calibrate(pub, dry_run=False)
    except Exception as e:
        print(f"  ⚠️ 统计校准跳过: {e}")

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
    """验证所有版本首页（含日历数据检查和外部版文件检查）"""
    errors = []
    check_str = date_str or week_id

    # 1. 首页 HTML 包含当前日期/周号
    for label, path in [
        ("内部版", PROJECT_ROOT / "index.html"),
        ("public/", PROJECT_ROOT / "public" / "index.html"),
    ]:
        if not path.exists():
            errors.append(f"❌ {label}不存在")
        elif check_str not in path.read_text(encoding="utf-8"):
            errors.append(f"❌ {label}未包含 {check_str}")

    # 2. 周报模式：日历数据中必须包含本周周号
    if week_id:
        for label, path in [
            ("内部版日历", PROJECT_ROOT / "index.html"),
            ("public/日历", PROJECT_ROOT / "public" / "index.html"),
        ]:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                # 检查日历中 weeklyReportsData 是否包含 week_id
                if f"weekly-{week_id}" not in content:
                    errors.append(f"❌ {label}日历数据未包含 weekly-{week_id}")

    # 3. 外部版：HTML 文件必须存在
    if week_id:
        # 从 week_id 计算月份目录 — 必须和 gen_weekly_html.py 一致
        # gen_weekly_html.py 用 ISO Monday 的月份（日报存放月份）
        # W23的日报在2026-06/，周报文件也应在2026-06/
        week_num = int(week_id.split("-W")[1])
        year = int(week_id.split("-")[0])
        from datetime import timedelta
        iso_monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
        month_str = iso_monday.strftime("%Y-%m")  # 和gen_weekly_html.py一致
        
        ext_repo = PROJECT_ROOT.parent / "ai-insight-public"
        if ext_repo.exists():
            ext_html = ext_repo / "01-daily-reports" / month_str / f"weekly-{week_id}.html"
            if not ext_html.exists():
                # 外部版HTML在Step 5(sync_to_external)后才同步，Step 4时可能不存在
                # 改为WARNING而非硬性ERROR，避免首页更新阶段误判
                print(f"  ⚠️ 外部版周报HTML尚未同步（将在Step 5 sync_to_external后到位）: {ext_html}")
            ext_index = ext_repo / "index.html"
            if ext_index.exists() and week_id not in ext_index.read_text(encoding="utf-8"):
                errors.append(f"❌ 外部版首页未包含 {week_id}")

    # 4. #124防复发：pills href与显示文本匹配校验
    # 检测往期周报pills是否全部指向同一URL（#120/#124同类复发）
    for label, path in [
        ("内部版", PROJECT_ROOT / "index.html"),
        ("public/", PROJECT_ROOT / "public" / "index.html"),
    ]:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # Find all pill badges like >W21< and their hrefs
            pill_pattern = re.compile(r'>W(\d+)<.*?href="([^"]*weekly-[^"]+)"', re.DOTALL)
            pills = pill_pattern.findall(content)
            if pills:
                mismatched = [(f"W{w}", href) for w, href in pills if f"W{w}" not in href]
                if len(mismatched) > len(pills) // 2:
                    # More than half of pills don't match = likely all pointing to same URL
                    errors.append(f"❌ {label}往期周报pills链接与文本不匹配（{len(mismatched)}/{len(pills)}个），疑似全指向同一URL（#124防复发）")

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

        print("\n📋 Step 1.5: 更新周报pill")
        update_weekly_pill(PROJECT_ROOT / "index.html", week_id,
                          args.week_month, args.week_title.replace("第", "").replace("周（", "").replace("）", "").strip())

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