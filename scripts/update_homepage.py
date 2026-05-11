#!/usr/bin/env python3
"""
update_homepage.py — 首页+索引页自动更新脚本
=================================================
独立于 deploy_daily.sh，在 HTML 生成后立即调用。
解决根因：首页更新耦合在 deploy 里 → deploy 失败时首页不更新。

校验标准：
- 首页日历包含当天日期
- 首页最新日报链接指向当天
- 首页最新日报标题包含当天中文日期
- 索引页统计数字+最新日期已更新
- 内部版+外部版(public/)首页同步更新

用法:
  python3 scripts/update_homepage.py 2026-05-11
  python3 scripts/update_homepage.py 2026-05-11 --verify  # 验证模式
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"


def update_calendar(index_path: Path, date_str: str) -> bool:
    """更新首页 index.html 的日历数组，添加当天日期"""
    month_str = date_str[:7]  # YYYY-MM
    day_num = str(int(date_str.split("-")[2]))  # 去前导零

    content = index_path.read_text(encoding="utf-8")

    # 检查日历是否已包含当天
    if re.search(rf"'{month_str}':.*\b{day_num}\b", content):
        print(f"  ⏭️ 日历已包含 {month_str}/{day_num}")
        return True

    # 在当月数组末尾追加日期
    pattern = rf"('{re.escape(month_str)}': \[)([^\]]+)(\])"
    if re.search(pattern, content):
        def add_day(m):
            existing = m.group(2).strip().rstrip(',')
            return m.group(1) + existing + ', ' + day_num + m.group(3)
        new_content = re.sub(pattern, add_day, content)
    else:
        # 新月：在 reportsData 开头插入新月条目
        new_content = re.sub(
            r"(const reportsData = \{)\s*\n(\s*')",
            rf"\1\n            '{month_str}': [{day_num}],  // {month_str}日报日期 (最新: {date_str})\n\2",
            content
        )
        if new_content == content:
            print(f"  ❌ 无法自动插入新月日历数组")
            return False

    # 更新注释中的最新日期
    new_content = re.sub(r'最新: \d{4}-\d{2}-\d{2}', f'最新: {date_str}', new_content)

    # 防退化：检查 currentMonth 不被硬编码
    if re.search(r"let currentMonth\s*=\s*[0-9]", new_content):
        print(f"  ❌ currentMonth 被硬编码为数字，请改为 todayMonth")
        return False

    index_path.write_text(new_content, encoding="utf-8")
    print(f"  ✅ 日历已添加 {day_num}，注释更新为 {date_str}")
    return True


def update_latest_card(index_path: Path, date_str: str) -> bool:
    """更新首页最新日报卡片（链接+标题+描述）"""
    month_str = date_str[:7]
    content = index_path.read_text(encoding="utf-8")

    # 更新 href
    content = re.sub(
        r'href="01-daily-reports/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}\.html"(\s+target="_blank"\s+class="list-item")',
        f'href="01-daily-reports/{month_str}/{date_str}.html"\\1',
        content
    )

    # 更新标题
    d = datetime.strptime(date_str, "%Y-%m-%d")
    date_cn = f'{d.year}年{d.month}月{d.day}日'
    content = re.sub(
        r'\d{4}年\d{1,2}月\d{1,2}日( AI日报)',
        date_cn + r'\1',
        content
    )

    # 更新描述 — 从JSON提取
    desc = _extract_desc(date_str)
    content = re.sub(
        r'(<div class="list-item-desc">)[^<]*(</div>)',
        lambda m: m.group(1) + desc + m.group(2),
        content
    )

    # 更新 "最新" badge 日期
    content = re.sub(
        r'(\d{4}年\d{1,2}月\d{1,2}日 AI日报 <span[^>]*>最新</span>)',
        f'{date_cn} AI日报 <span style="background:#FEF2F2;color:#E11D48;font-size:11px;padding:2px 6px;border-radius:999px;margin-left:6px;">最新</span>',
        content
    )

    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 最新日报卡片已更新: {date_cn} → {month_str}/{date_str}.html")
    return True


def _extract_desc(date_str: str) -> str:
    """从 JSON 提取日报描述"""
    json_path = PROJECT_ROOT / "data" / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return "今日AI行业动态汇总"

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        overviews = data.get("overview", [])
        parts = []
        for ov in overviews[:4]:
            hl = ov.get("headline", "")
            if hl:
                clean = re.sub(r'<[^>]+>', '', hl)[:20]
                parts.append(clean)
        return ' · '.join(parts) if parts else "今日AI行业动态汇总"
    except Exception:
        return "今日AI行业动态汇总"


def update_report_index(date_str: str) -> bool:
    """更新 01-daily-reports/index.html（统计数字+最新日期）"""
    month_str = date_str[:7]
    index_path = PROJECT_ROOT / "01-daily-reports" / "index.html"

    if not index_path.exists():
        print(f"  ⚠️ 索引页不存在: {index_path}")
        return True  # 不阻断

    content = index_path.read_text(encoding="utf-8")
    report_count = len(list((PROJECT_ROOT / "01-daily-reports" / month_str).glob("*-v3.html")))

    content = re.sub(
        r'(<div class="stat-value">)\d+(</div><div class="stat-label">日报)',
        f'\\g<1>{report_count}\\g<2>',
        content
    )
    content = re.sub(
        r'(<div class="stat-value">)\d{4}-\d{2}-\d{2}(</div><div class="stat-label">最新)',
        f'\\g<1>{date_str}\\g<2>',
        content
    )

    index_path.write_text(content, encoding="utf-8")
    print(f"  ✅ 索引页已更新 (共{report_count}篇, 最新:{date_str})")
    return True


def sync_public_homepage(date_str: str) -> bool:
    """同步 public/index.html — 从内部版 copy 后更新"""
    src = PROJECT_ROOT / "index.html"
    dst = PROJECT_ROOT / "public" / "index.html"

    if not src.exists():
        print(f"  ❌ 内部版首页不存在")
        return False

    # 从内部版复制到 public/
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # 验证 public/index.html 包含当天日期
    pub_content = dst.read_text(encoding="utf-8")
    if date_str not in pub_content:
        print(f"  ❌ public/index.html 未包含 {date_str}")
        return False

    print(f"  ✅ public/index.html 已同步 (包含 {date_str})")
    return True


def verify_homepage(date_str: str) -> bool:
    """验证首页+索引页+public首页全部包含当天日期"""
    month_str = date_str[:7]
    errors = []

    # 内部版首页
    idx = PROJECT_ROOT / "index.html"
    if not idx.exists():
        errors.append("❌ 内部版 index.html 不存在")
    elif date_str not in idx.read_text(encoding="utf-8"):
        errors.append(f"❌ 内部版首页未包含 {date_str}")

    # public/首页
    pub = PROJECT_ROOT / "public" / "index.html"
    if not pub.exists():
        errors.append("❌ public/index.html 不存在")
    elif date_str not in pub.read_text(encoding="utf-8"):
        errors.append(f"❌ public首页未包含 {date_str}")

    # 索引页
    rep_idx = PROJECT_ROOT / "01-daily-reports" / "index.html"
    if rep_idx.exists() and date_str not in rep_idx.read_text(encoding="utf-8"):
        errors.append(f"❌ 索引页未包含 {date_str}")

    if errors:
        for e in errors:
            print(f"  {e}")
        return False
    print(f"  ✅ 首页验证通过: 内部版 + public + 索引页均包含 {date_str}")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/update_homepage.py YYYY-MM-DD [--verify]")
        sys.exit(1)

    date_str = sys.argv[1]
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        print(f"❌ 日期格式错误: {date_str}")
        sys.exit(1)

    verify_only = "--verify" in sys.argv

    print(f"\n🏠 首页更新: {date_str}")
    print("=" * 50)

    if verify_only:
        ok = verify_homepage(date_str)
        sys.exit(0 if ok else 1)

    # 1. 更新内部版首页日历
    print("\n📋 Step 1: 更新日历数组")
    update_calendar(PROJECT_ROOT / "index.html", date_str)

    # 2. 更新最新日报卡片
    print("\n📋 Step 2: 更新最新日报卡片")
    update_latest_card(PROJECT_ROOT / "index.html", date_str)

    # 3. 更新索引页
    print("\n📋 Step 3: 更新日报索引页")
    update_report_index(date_str)

    # 4. 同步到 public/
    print("\n📋 Step 4: 同步到 public/")
    sync_public_homepage(date_str)

    # 5. 验证
    print("\n📋 Step 5: 验证")
    ok = verify_homepage(date_str)

    if ok:
        print(f"\n✅ 首页更新完成！")
    else:
        print(f"\n⚠️ 首页更新完成但验证发现问题，请手动检查")
        sys.exit(1)


if __name__ == "__main__":
    main()