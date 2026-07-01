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
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent

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
    """更新首页最新日报卡片——滚动窗口，最近4期不同日报
    
    逻辑：
    1. 扫描 01-daily-reports/ 下所有 *-v3.html，按日期倒序取最近4个
    2. 用这4个日报重建"最近日报"区块的 list-item 列表
    3. 最新一条加"最新"标签，其余不加
    4. 每条的描述从对应 JSON 数据提取
    """
    month_str = date_str[:7]
    content = index_path.read_text(encoding="utf-8")

    # 收集所有日报日期（从 *-v3.html 文件名提取）
    reports_dir = PROJECT_ROOT / "01-daily-reports"
    all_dates = []
    for month_dir in sorted(reports_dir.iterdir()):
        if month_dir.is_dir() and re.match(r'\d{4}-\d{2}', month_dir.name):
            for html_file in month_dir.glob("*-v3.html"):
                m = re.match(r'(\d{4}-\d{2}-\d{2})-v3\.html', html_file.name)
                if m:
                    all_dates.append(m.group(1))
    all_dates.sort(reverse=True)
    recent_4 = all_dates[:4]

    if not recent_4:
        print(f"  ⚠️ 未找到任何日报HTML文件，跳过卡片更新")
        return True

    # 构建新的 list-item HTML
    items_html = ""
    for i, d in enumerate(recent_4):
        d_month = d[:7]
        dt = datetime.strptime(d, "%Y-%m-%d")
        date_cn = f'{dt.year}年{dt.month}月{dt.day}日'
        desc = _extract_daily_desc(d)
        latest_badge = ' <span style="background:#FEF2F2;color:#E11D48;font-size:11px;padding:2px 6px;border-radius:999px;margin-left:6px;">最新</span>' if i == 0 else ""
        items_html += f'''                    <a href="01-daily-reports/{d_month}/{d}.html" target="_blank" class="list-item">
                        <span class="list-item-icon">📅</span>
                        <div class="list-item-content">
                            <div class="list-item-title">{date_cn} AI日报{latest_badge}</div>
                            <div class="list-item-desc">{desc}</div>
                        </div>
                        <span class="list-item-arrow">→</span>
                    </a>
'''

    # 替换"最近日报"区块内的所有 list-item
    # 匹配: <!-- 最近日报 --> ... </div> (content-list 的结束标签)
    marker_start = '<!-- 最近日报（展示最近4期） -->'
    marker_pattern = re.compile(
        rf'({re.escape(marker_start)}\s*<div class="content-list">)(.*?)(\s*</div>\s*(?=\s*<!--|$))',
        re.DOTALL
    )
    m = marker_pattern.search(content)
    if not m:
        # fallback: 找 content-list 区块后替换所有 list-item
        print(f"  ⚠️ 未找到'最近日报'标记，尝试fallback替换")
        # fallback: 整体替换 content-list 内内容
        cl_pattern = re.compile(
            r'(<div class="content-list">\s*)(.*?)(\s*</div>\s*(?=\s*</div>))',
            re.DOTALL
        )
        m = cl_pattern.search(content)
        if not m:
            print(f"  ❌ 无法定位日报列表区块")
            return False

    new_content = content[:m.start()] + m.group(1) + '\n' + items_html + m.group(3) + content[m.end():]
    index_path.write_text(new_content, encoding="utf-8")
    print(f"  ✅ 日报卡片已更新（滚动窗口）: {', '.join(recent_4)}")
    return True


def _extract_daily_desc(date_str: str) -> str:
    """从JSON数据提取日报描述，支持flat和subdir两种路径"""
    # 路径1: data/daily-content-YYYY-MM-DD.json (flat, 旧格式)
    json_path = PROJECT_ROOT / "data" / f"daily-content-{date_str}.json"
    # 路径2: data/daily/YYYY-MM/daily-content-YYYY-MM-DD.json (subdir, 新格式)
    if not json_path.exists():
        month_str = date_str[:7]
        json_path = PROJECT_ROOT / "data" / "daily" / month_str / f"daily-content-{date_str}.json"
    # 路径3: data/daily-reports/YYYY-MM/daily-content-YYYY-MM-DD.json (cron产出)
    if not json_path.exists():
        month_str = date_str[:7]
        json_path = PROJECT_ROOT / "data" / "daily-reports" / month_str / f"daily-content-{date_str}.json"
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
    
    # pill HTML模板（#124防复发：标签用W+数字，不用完整week_id）
    pill_label = "W" + (week_id.split("-W")[1] if "-W" in week_id else week_id)  # "2026-W23" → "W23"
    pill_html = f'''                        <a href="01-daily-reports/{month}/weekly-{week_id}.html" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; background: var(--color-bg-table-header); border: 1px solid var(--color-border-light); border-radius: var(--radius-full); font-size: 12px; color: var(--color-info); text-decoration: none; transition: all 0.15s;">{pill_label}<span style="font-size: 10px; color: var(--color-text-muted);">{date_range}</span></a>'''
    
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
    """更新日历JS周报数据
    
    day = 本周周一的日期（周报所在周的起始日）
    同时自动将下周周一（day+7）也关联到本周周报，
    确保下周一在周报未出前能看到最新周报。
    如果 day+7 超出本月，则跨月写入（由脚本自动处理）。
    """
    content = index_path.read_text(encoding="utf-8")
    day_str = f"{day}: 'weekly-{week_id}'"
    
    # 计算下周周一：如果同月则追加，如果跨月则独立写入下月
    from calendar import monthrange
    import datetime as _dt
    year_int = int(month.split('-')[0])
    month_int = int(month.split('-')[1])
    next_monday_day = day + 7
    next_monday_month = month
    if next_monday_day > monthrange(year_int, month_int)[1]:
        next_monday_day -= monthrange(year_int, month_int)[1]
        next_month = month_int + 1 if month_int < 12 else 1
        next_year = year_int if month_int < 12 else year_int + 1
        next_monday_month = f"{next_year}-{next_month:02d}"
    next_monday_str = f"{next_monday_day}: 'weekly-{week_id}'"

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
            _write_next_monday_to_calendar(index_path, next_monday_month, next_monday_day, week_id)
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
                _write_next_monday_to_calendar(index_path, next_monday_month, next_monday_day, week_id)
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
        _write_next_monday_to_calendar(index_path, next_monday_month, next_monday_day, week_id)
        return True

    # 最终 fallback: 没找到任何周报日历数据 — hard fail
    print(f"  ❌ 未找到周报日历数据，无法更新日历（期望包含 weeklyReportsData 或月份行）")
    return False


def _write_next_monday_to_calendar(index_path: Path, next_monday_month: str, next_monday_day: int, week_id: str) -> None:
    """将下周周一也关联到本周周报（供update_calendar_weekly调用）"""
    content = index_path.read_text(encoding="utf-8")
    next_day_str = f"{next_monday_day}: 'weekly-{week_id}'"
    
    # 如果已存在，跳过
    if next_day_str in content:
        print(f"  ⏭️ 下周周一 {next_monday_month}/{next_monday_day} 已关联 {week_id}")
        return
    
    month_line_pattern = rf"'{next_monday_month}':\s*\{{([^}}]*)\}}"
    m = re.search(month_line_pattern, content)
    if m:
        old_line = m.group(0)
        new_line = old_line.rstrip("}") + ", " + next_day_str + "}"
        new_content = content[:m.start()] + new_line + content[m.end():]
        index_path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ 下周周一 {next_monday_month}/{next_monday_day} 已关联 {week_id}")
    else:
        # 下月尚无数据，追加新月份行
        weekly_block_pattern = r'weeklyReportsData\s*=\s*\{([\s\S]+?)\}\s*;'
        bm = re.search(weekly_block_pattern, content)
        if bm:
            existing = bm.group(1)
            last_month_pattern = r"'(\d{4}-\d{2})':\s*\{[^}]+\}\s*(?:,\s*)?"
            all_months = list(re.finditer(last_month_pattern, existing))
            if all_months:
                last_m = all_months[-1]
                new_month_line = f"    '{next_monday_month}': {{{next_day_str}}},  // {week_id}"
                insert_pos = last_m.end()
                new_existing = existing[:insert_pos] + "\n            " + new_month_line + existing[insert_pos:]
                new_content = content.replace(existing, new_existing)
                index_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ 下周周一 {next_monday_month}/{next_monday_day} 追加新月 {week_id}")


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
            # 先校准public/的统计数字，再用校准后的版本脱敏
            calibrate_result = None
            try:
                from calibrate_stats import calibrate as _calibrate
                calibrate_result = _calibrate(pub, dry_run=True)  # 先dry_run获取数值
            except Exception:
                pass
            
            sanitized = sanitize_html(src.read_text(encoding="utf-8"))
            
            # 如果校准成功，把统计数字也应用到外部版
            if calibrate_result:
                for label, value in calibrate_result.items():
                    pattern = rf'(<div class="stat-value [^"]*">)[^<]*(</div>\s*<div class="stat-label">\s*{re.escape(label)})'
                    sanitized = re.sub(pattern, rf'\g<1>{value}\g<2>', sanitized)
            
            (external_repo / "index.html").write_text(sanitized, encoding="utf-8")
            print(f"  ✅ ai-insight-public/index.html 已脱敏同步（含统计校准）")
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
            # Find all pill badges: href在前, >W21<在后（#124修复：正则顺序匹配HTML结构）
            pill_pattern = re.compile(r'href="([^"]*weekly-2026-W(\d+)\.html)"[^>]*>[^<]*>W(\d+)<', re.DOTALL)
            pills = pill_pattern.findall(content)
            if pills:
                # href中的W编号(组2) vs 标签文本中的W编号(组3) 必须匹配
                mismatched = [(f"W{text_w}", href) for href, href_w, text_w in pills if href_w != text_w]
                if len(mismatched) > len(pills) // 2:
                    # More than half of pills don't match = likely all pointing to same URL
                    errors.append(f"❌ {label}往期周报pills链接与文本不匹配（{len(mismatched)}/{len(pills)}个），疑似全指向同一URL（#124防复发）")

    if errors:
        for e in errors:
            print(f"  {e}")
        return False
    print(f"  ✅ 首页快速验证通过: {check_str}")
    
    # v2.0 (#129): 调用独立验证脚本做完整17项检查
    try:
        cmd = [sys.executable, str(SCRIPT_DIR / "verify_homepage.py")]
        if date_str:
            cmd.extend(["--date", date_str])
        if week_id:
            cmd.extend(["--week", week_id])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT))
        if result.returncode != 0:
            print(f"  ❌ 完整验证失败:")
            print(result.stdout[-500:] if result.stdout else "")
            return False
        print(f"  ✅ 完整验证通过（17项）")
    except Exception as e:
        print(f"  ⚠️ 完整验证脚本不可用: {e}（快速验证已通过）")
    
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

        # #129: 自动计算周一日期（如果未传--week-day）
        if args.week_day == 0:
            m = re.match(r"(\d{4})-W(\d+)", week_id)
            if m:
                year, week = int(m.group(1)), int(m.group(2))
                monday = datetime.fromisocalendar(year, week, 1)
                args.week_day = monday.day
                print(f"  📅 自动计算周一日: {monday.strftime('%Y-%m-%d')} (day={args.week_day})")
            else:
                print("❌ 无法从周号自动计算周一日期，请传 --week-day")
                sys.exit(1)

        if args.verify:
            ok = verify_homepage(week_id=week_id)
            sys.exit(0 if ok else 1)

        print("\n📋 Step 1: 更新周报入口卡片")
        update_weekly_card(PROJECT_ROOT / "index.html", week_id,
                           args.week_month, args.week_title, args.week_desc)

        print("\n📋 Step 1.5: 更新周报pill")
        # 从title提取日期范围：第24周（06/08 - 06/14）→ 06/08-06/14
        import re as _re
        _m = _re.search(r"（([^）]+)）", args.week_title)
        _date_range = _m.group(1).replace(" - ", "-") if _m else args.week_title.replace("第", "").replace("周", "")
        update_weekly_pill(PROJECT_ROOT / "index.html", week_id,
                          args.week_month, _date_range)

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