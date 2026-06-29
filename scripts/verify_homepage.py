#!/usr/bin/env python3
"""AI洞察首页完整性验证脚本（v1.0 — 2026-06-29）

每次日报/周报部署后自动执行，检查内部版+外部版首页的所有已知问题模式。
全部通过 = 准出；任何一项失败 = 阻断，必须修复后重跑。

用法：
  uv run scripts/verify_homepage.py --date 2026-06-29          # 日报模式
  uv run scripts/verify_homepage.py --week 2026-W26            # 周报模式
  uv run scripts/verify_homepage.py --date 2026-06-29 --week 2026-W26  # 同时验证
  uv run scripts/verify_homepage.py --full                    # 全量检查（不限定日期）
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from calendar import monthrange

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
EXTERNAL_DIR = PROJECT_ROOT.parent / "ai-insight-public"
INTERNAL_INDEX = PROJECT_ROOT / "index.html"
PUBLIC_INDEX = PUBLIC_DIR / "index.html"
EXTERNAL_INDEX = EXTERNAL_DIR / "index.html"

# ========== 敏感词列表（外部版零容忍）==========
EXTERNAL_SENSITIVE = [
    "林克", "沈浪", "link-avatar-small", "corp.kuaishou.com",
    "MyFlicker", "快手", "kuaishou",
]

# ========== 检查项 ==========

class Check:
    def __init__(self, name: str, severity: str, passed: bool, detail: str):
        self.name = name
        self.severity = severity  # "HARD" | "SOFT"
        self.passed = passed
        self.detail = detail

    def __repr__(self):
        icon = "✅" if self.passed else ("🚫" if self.severity == "HARD" else "⚠️")
        return f"{icon} [{self.severity}] {self.name}: {self.detail}"


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def check_files_exist() -> list[Check]:
    """1. 三个版本首页文件存在性"""
    results = []
    for label, path in [("内部版", INTERNAL_INDEX), ("public/", PUBLIC_INDEX), ("外部版", EXTERNAL_INDEX)]:
        if path.exists():
            results.append(Check("文件存在", "HARD", True, f"{label} 存在 ({path.stat().st_size/1024:.0f}KB)"))
        else:
            results.append(Check("文件存在", "HARD", False, f"{label} 不存在: {path}"))
    return results


def check_internal_identity() -> list[Check]:
    """2. 内部版必须保留林克身份"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        results.append(Check("内部版身份", "HARD", False, "index.html 不存在"))
        return results
    
    checks = [
        ("林克文字", "林克" in content),
        ("link-avatar-small.webp", "link-avatar-small.webp" in content),
        ("CSS class link-avatar", "link-avatar" in content),
    ]
    for label, ok in checks:
        results.append(Check(f"内部版·{label}", "HARD", ok, 
            "保留" if ok else "❌ 缺失（可能被脱敏版覆盖）"))
    return results


def check_external_sanitized() -> list[Check]:
    """3. 外部版零敏感词"""
    results = []
    content = read_file(EXTERNAL_INDEX)
    if not content:
        results.append(Check("外部版脱敏", "HARD", True, "外部版不存在（跳过）"))
        return results
    
    found = []
    for word in EXTERNAL_SENSITIVE:
        if word in content:
            # 统计出现次数
            count = content.count(word)
            found.append(f"{word}×{count}")
    
    if found:
        results.append(Check("外部版敏感词", "HARD", False, f"发现: {', '.join(found)}"))
    else:
        results.append(Check("外部版敏感词", "HARD", True, "零敏感词 ✅"))
    return results


def check_external_daily_html_sensitive(date_str: str) -> list[Check]:
    """3.5 外部版日报HTML零敏感词"""
    results = []
    if not date_str:
        return results
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    external_html = EXTERNAL_DIR / "01-daily-reports" / month_str / f"{date_str}.html"
    if not external_html.exists():
        return results
    
    content = read_file(external_html)
    found = []
    for word in EXTERNAL_SENSITIVE:
        if word in content:
            count = content.count(word)
            found.append(f"{word}×{count}")
    
    if found:
        results.append(Check("外部版日报HTML敏感词", "HARD", False, f"外部版日报{date_str}含: {', '.join(found)}"))
    else:
        results.append(Check("外部版日报HTML敏感词", "HARD", True, f"外部版日报{date_str}零敏感词 ✅"))
    return results


def check_calendar_daily(date_str: str) -> list[Check]:
    """4. 日历日报数据"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content or not date_str:
        return results
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    day = date_obj.day
    
    cal_match = re.search(rf"'{re.escape(month_str)}':\s*\[([^\]]+)\]", content)
    if cal_match:
        days = [int(x.strip()) for x in cal_match.group(1).split(",") if x.strip().isdigit()]
        if day in days:
            results.append(Check("日历·日报", "HARD", True, f"{month_str} 包含 {day}日"))
        else:
            results.append(Check("日历·日报", "HARD", False, f"{month_str} 缺少 {day}日，当前: {days}"))
    else:
        results.append(Check("日历·日报", "HARD", False, f"未找到 {month_str} 月日历数据"))
    
    return results


def check_calendar_weekly(week_id: str) -> list[Check]:
    """5. 日历周报数据"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content or not week_id:
        return results
    
    # 从周号推算周一日期：W26 → 2026-06-22
    match = re.match(r"(\d{4})-W(\d+)", week_id)
    if not match:
        results.append(Check("日历·周报", "HARD", False, f"无效周号格式: {week_id}"))
        return results
    
    year = int(match.group(1))
    week = int(match.group(2))
    # ISO week: 周一日期
    monday = datetime.fromisocalendar(year, week, 1)
    next_monday = monday + timedelta(days=7)
    
    month_str = monday.strftime("%Y-%m")
    day = monday.day
    next_month_str = next_monday.strftime("%Y-%m")
    next_day = next_monday.day
    
    # 检查本周周一
    month_data = re.search(rf"'{re.escape(month_str)}':\s*\{{([^}}]+)\}}", content)
    if month_data:
        entries = month_data.group(1)
        if f"{day}: 'weekly-{week_id}'" in entries:
            results.append(Check("日历·周报·本周一", "HARD", True, f"{month_str}/{day} → {week_id}"))
        else:
            results.append(Check("日历·周报·本周一", "HARD", False, f"{month_str}/{day} 未关联 {week_id}，当前: {entries.strip()}"))
    else:
        results.append(Check("日历·周报·本周一", "HARD", False, f"未找到 {month_str} 月周报日历数据"))
    
    # 检查下周周一
    next_data = re.search(rf"'{re.escape(next_month_str)}':\s*\{{([^}}]+)\}}", content)
    if next_data:
        entries = next_data.group(1)
        if f"{next_day}: 'weekly-{week_id}'" in entries:
            results.append(Check("日历·周报·下周一", "HARD", True, f"{next_month_str}/{next_day} → {week_id}"))
        else:
            results.append(Check("日历·周报·下周一", "HARD", False, f"{next_month_str}/{next_day} 未关联 {week_id}（W+1未出时也应关联上周）"))
    else:
        # 下月尚无数据=可能正常
        results.append(Check("日历·周报·下周一", "SOFT", False, f"{next_month_str} 月无周报日历数据"))
    
    return results


def check_calendar_no_ghost() -> list[Check]:
    """6. 日历无幽灵条目（不存在的周报文件引用）"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        return results
    
    # 提取所有周报日历引用
    weekly_block = re.search(r"weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;", content)
    if not weekly_block:
        return results
    
    entries = re.findall(r"(\d+):\s*'weekly-([^']+)'", weekly_block.group(1))
    for day_str, week_id in entries:
        # 检查对应HTML文件是否存在
        # 周一可能在月底，文件可能在下月目录，搜索两个位置
        m = re.match(r"(\d{4})-W(\d+)", week_id)
        if m:
            year, week = int(m.group(1)), int(m.group(2))
            monday = datetime.fromisocalendar(year, week, 1)
            month_str = monday.strftime("%Y-%m")
            # 周一可能在月底，HTML可能在下月目录
            next_month = (monday.replace(day=28) + timedelta(days=4)).strftime("%Y-%m")
            html_paths = [
                PROJECT_ROOT / "01-daily-reports" / month_str / f"weekly-{week_id}.html",
                PROJECT_ROOT / "01-daily-reports" / next_month / f"weekly-{week_id}.html",
            ]
            found = any(p.exists() for p in html_paths)
            if not found:
                tried = ", ".join(str(p.relative_to(PROJECT_ROOT)) for p in html_paths)
                results.append(Check("日历·幽灵条目", "HARD", False, 
                    f"日历引用 {day_str}:'weekly-{week_id}' 但文件不存在 (搜索: {tried})"))
    
    if not any(c.name == "日历·幽灵条目" and not c.passed for c in results):
        results.append(Check("日历·幽灵条目", "HARD", True, "所有日历引用的周报文件均存在"))
    
    return results


def check_weekly_card_link() -> list[Check]:
    """7. 周报大卡片链接指向存在的文件"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        return results
    
    # 匹配周报卡片链接
    href_match = re.search(r'<a\s+[^>]*href="([^"]+)"[^>]*class="weekly-report-card"', content)
    if not href_match:
        href_match = re.search(r'class="weekly-report-card"[^>]*href="([^"]+)"', content)
    if href_match:
        href = href_match.group(1)
        target = PROJECT_ROOT / href.lstrip("./")
        if target.exists():
            results.append(Check("周报卡片链接", "HARD", True, f"→ {href} ({target.stat().st_size/1024:.0f}KB)"))
        else:
            results.append(Check("周报卡片链接", "HARD", False, f"→ {href} 文件不存在！"))
    else:
        results.append(Check("周报卡片链接", "SOFT", False, "未找到weekly-report-card"))
    
    # 外部版也检查
    ext_content = read_file(EXTERNAL_INDEX)
    if ext_content:
        ext_href = re.search(r'<a\s+[^>]*href="([^"]+)"[^>]*class="weekly-report-card"', ext_content)
        if not ext_href:
            ext_href = re.search(r'class="weekly-report-card"[^>]*href="([^"]+)"', ext_content)
        if ext_href:
            href = ext_href.group(1)
            ext_target = EXTERNAL_DIR / href.lstrip("./")
            if ext_target.exists():
                results.append(Check("周报卡片链接·外部", "HARD", True, f"→ {href}"))
            else:
                results.append(Check("周报卡片链接·外部", "HARD", False, f"→ {href} 外部仓库文件不存在！"))
    
    return results


def check_subscribe_button() -> list[Check]:
    """8. 订阅按钮URL"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        return results
    
    CORRECT_URL = "https://aidailyinsight-subscribe.frontend-cloud.corp.kuaishou.com"
    
    if CORRECT_URL in content:
        results.append(Check("订阅按钮·内部", "HARD", True, f"指向正确内网URL"))
    elif "./subscribe/" in content or "subscribe/" in content:
        results.append(Check("订阅按钮·内部", "HARD", False, f"使用了相对路径（SSO 302会失败），应改为 {CORRECT_URL}"))
    else:
        results.append(Check("订阅按钮·内部", "SOFT", False, "未找到订阅按钮"))
    
    return results


def check_internal_external_consistency() -> list[Check]:
    """9. 内部版和public/一致性"""
    results = []
    internal = read_file(INTERNAL_INDEX)
    public = read_file(PUBLIC_INDEX)
    
    if internal and public:
        if internal == public:
            results.append(Check("内部版=public/", "HARD", True, "内容完全一致"))
        else:
            # 允许微小差异（校准后数字可能不同），但关键结构必须一致
            # 检查关键标记
            internal_weekly = re.findall(r"weekly-\d{4}-W\d+", internal)
            public_weekly = re.findall(r"weekly-\d{4}-W\d+", public)
            if set(internal_weekly) == set(public_weekly):
                results.append(Check("内部版≈public/", "HARD", True, "周报引用一致（微差异可能是统计校准）"))
            else:
                results.append(Check("内部版vs public/", "HARD", False, 
                    f"周报引用不一致！内部={set(internal_weekly)} public={set(public_weekly)}"))
    
    return results


def check_no_duplicate_weekly_calendar() -> list[Check]:
    """10. 日历同一周号不重复"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        return results
    
    weekly_block = re.search(r"weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;", content)
    if not weekly_block:
        return results
    
    # 检查同一week_id出现在多个day key
    entries = re.findall(r"(\d+):\s*'weekly-([^']+)'", weekly_block.group(1))
    week_id_days = {}
    for day_str, week_id in entries:
        week_id_days.setdefault(week_id, []).append(day_str)
    
    # 允许：本周一+下周一 关联同一个week_id（这是正常的）
    # 不允许：同一个月内两个不同day关联同一week_id（除非差=7）
    for week_id, days in week_id_days.items():
        if len(days) > 2:
            results.append(Check("日历·重复周号", "HARD", False, 
                f"{week_id} 出现在 {len(days)} 个日: {days}（最多2个：本周一+下周一）"))
        elif len(days) == 2:
            d1, d2 = int(days[0]), int(days[1])
            if abs(d2 - d1) != 7:
                results.append(Check("日历·重复周号", "HARD", False,
                    f"{week_id} 在 {days}，间隔{abs(d2-d1)}天（应为7天）"))
    
    if not any(c.name == "日历·重复周号" and not c.passed for c in results):
        results.append(Check("日历·重复周号", "HARD", True, "无异常重复"))
    
    return results


def check_no_wrong_format_weekly_keys() -> list[Check]:
    """11. 日历周报key不能是日期格式（必须是WXX格式）"""
    results = []
    content = read_file(INTERNAL_INDEX)
    if not content:
        return results
    
    weekly_block = re.search(r"weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;", content)
    if not weekly_block:
        return results
    
    # 检测 weekly-YYYY-MM-DD 格式的错误key
    wrong_format = re.findall(r"'weekly-\d{4}-\d{2}-\d{2}'", weekly_block.group(1))
    if wrong_format:
        results.append(Check("日历·错误key格式", "HARD", False, 
            f"发现日期格式key: {wrong_format}（应为 weekly-YYYY-WXX 格式）"))
    else:
        results.append(Check("日历·key格式", "HARD", True, "所有周报key为WXX格式"))
    
    return results


# ========== 主流程 ==========

def run_checks(date_str: str = "", week_id: str = "", full: bool = False) -> list[Check]:
    checks = []
    
    # 1. 文件存在
    checks.extend(check_files_exist())
    
    # 2-3. 身份+脱敏
    checks.extend(check_internal_identity())
    checks.extend(check_external_sanitized())
    
    # 4. 日历日报
    if date_str or full:
        checks.extend(check_calendar_daily(date_str or datetime.now().strftime("%Y-%m-%d")))
        checks.extend(check_external_daily_html_sensitive(date_str or datetime.now().strftime("%Y-%m-%d")))
    
    # 5. 日历周报
    if week_id or full:
        checks.extend(check_calendar_weekly(week_id))
    
    # 6-11. 通用检查（始终执行）
    checks.extend(check_calendar_no_ghost())
    checks.extend(check_weekly_card_link())
    checks.extend(check_subscribe_button())
    checks.extend(check_internal_external_consistency())
    checks.extend(check_no_duplicate_weekly_calendar())
    checks.extend(check_no_wrong_format_weekly_keys())
    
    return checks


def main():
    parser = argparse.ArgumentParser(description="AI洞察首页完整性验证")
    parser.add_argument("--date", help="日报日期 (YYYY-MM-DD)")
    parser.add_argument("--week", help="周号 (YYYY-WXX)")
    parser.add_argument("--full", action="store_true", help="全量检查")
    args = parser.parse_args()
    
    print("\n🔍 AI洞察首页完整性验证")
    print("=" * 60)
    
    checks = run_checks(date_str=args.date, week_id=args.week, full=args.full)
    
    hard_pass = [c for c in checks if c.severity == "HARD" and c.passed]
    hard_fail = [c for c in checks if c.severity == "HARD" and not c.passed]
    soft_fail = [c for c in checks if c.severity == "SOFT" and not c.passed]
    
    for c in checks:
        print(f"  {c}")
    
    print(f"\n{'=' * 60}")
    print(f"  硬性通过: {len(hard_pass)} | 硬性失败: {len(hard_fail)} | 软性警告: {len(soft_fail)}")
    
    if hard_fail:
        print(f"\n🚫 准出失败！{len(hard_fail)} 项硬性检查未通过：")
        for c in hard_fail:
            print(f"   • {c.name}: {c.detail}")
        print(f"\n   修复后重新运行: uv run scripts/verify_homepage.py --date {args.date or ''} --week {args.week or ''}")
        sys.exit(1)
    else:
        print(f"\n✅ 准出通过！所有硬性检查均通过。")
        if soft_fail:
            print(f"   ⚠️ {len(soft_fail)} 项软性警告，不阻断。")
        sys.exit(0)


if __name__ == "__main__":
    main()
