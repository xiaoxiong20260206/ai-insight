#!/usr/bin/env python3
"""
AI日报外部版本同步脚本
======================
将脱敏后的日报同步到外部公开仓库 (ai-daily-report)

功能:
1. 从 public/ 目录复制脱敏后的日报HTML
2. 更新外部仓库的 index.html (日报数量和最新日期)
3. 提交并推送到 my-ai-research-lab/ai-daily-report

使用方式:
  python scripts/sync_to_external.py                    # 同步今天的日报
  python scripts/sync_to_external.py 2026-03-06         # 同步指定日期
  python scripts/sync_to_external.py --all              # 同步所有日报

前置条件:
  1. 已运行 sync_to_public.py 生成脱敏版本
  2. ../ai-daily-report/ 仓库存在且有 org remote 配置

作者: 林克 (沈浪的AI分身)
版本: 1.0.0
"""

import argparse
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
PUBLIC_REPORTS = PROJECT_ROOT / "public" / "01-daily-reports"
EXTERNAL_REPO = PROJECT_ROOT.parent / "ai-daily-report"


def get_all_report_dates() -> list:
    """获取 public 目录下所有日报的日期列表"""
    dates = []
    for month_dir in sorted(PUBLIC_REPORTS.iterdir()):
        if not month_dir.is_dir() or month_dir.name.startswith('.'):
            continue
        for html_file in sorted(month_dir.glob("*.html")):
            if html_file.name != "index.html":
                dates.append(html_file.stem)  # e.g., "2026-03-06"
    return dates


def sync_report(date_str: str) -> bool:
    """
    同步单个日报到外部仓库
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
    
    Returns:
        是否成功同步
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    # 源文件路径
    src_html = PUBLIC_REPORTS / month_str / f"{date_str}.html"
    
    # 目标路径 (外部仓库根目录，不按月份分子目录)
    dst_html = EXTERNAL_REPO / f"{date_str}.html"
    
    if not src_html.exists():
        print(f"❌ 源文件不存在: {src_html}")
        print(f"   请先运行: python3 scripts/sync_to_public.py {date_str}")
        return False
    
    if not EXTERNAL_REPO.exists():
        print(f"❌ 外部仓库不存在: {EXTERNAL_REPO}")
        return False
    
    # 复制文件
    shutil.copy2(src_html, dst_html)
    print(f"✅ 已复制: {date_str}.html")
    
    return True


def update_external_index(dates: list) -> bool:
    """
    更新外部仓库的 index.html
    
    Args:
        dates: 所有日报日期列表 (已排序)
    """
    index_path = EXTERNAL_REPO / "index.html"
    
    if not index_path.exists():
        print("❌ 外部仓库 index.html 不存在")
        return False
    
    # 读取当前 index.html
    content = index_path.read_text(encoding="utf-8")
    
    # 获取最新日期和日报数量
    latest_date = max(dates)
    report_count = len(dates)
    
    # 更新统计数字
    content = re.sub(
        r'(<div class="stat-value">)\d+(</div><div class="stat-label">日报</div>)',
        rf'\g<1>{report_count}\g<2>',
        content
    )
    content = re.sub(
        r'(<div class="stat-value">)\d{4}-\d{2}-\d{2}(</div><div class="stat-label">最新</div>)',
        rf'\g<1>{latest_date}\g<2>',
        content
    )
    
    # 生成日报列表 HTML
    report_items = []
    for i, date in enumerate(sorted(dates, reverse=True)):
        if i == 0:
            # 最新的带标签
            report_items.append(
                f'<div class="report-item"><a href="{date}.html">{date}</a>'
                f'<span class="report-badge badge-latest">最新</span></div>'
            )
        else:
            report_items.append(
                f'<div class="report-item"><a href="{date}.html">{date}</a></div>'
            )
    
    # 替换日报列表
    report_list_html = "\n            ".join(report_items)
    content = re.sub(
        r'(<div class="section-title">📰 日报</div>\n)\s*<div class="report-item">.*?(?=\n\s*</div>\s*<div class="footer">)',
        rf'\g<1>            {report_list_html}\n        ',
        content,
        flags=re.DOTALL
    )
    
    # 写入更新后的 index.html
    index_path.write_text(content, encoding="utf-8")
    print(f"✅ 已更新 index.html: {report_count} 篇日报, 最新 {latest_date}")
    
    return True


def git_push() -> bool:
    """提交并推送到外部仓库"""
    try:
        os.chdir(EXTERNAL_REPO)
        
        # git add
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # 检查是否有变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            print("ℹ️  无变更需要提交")
            return True
        
        # git commit
        commit_msg = f"更新至 {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
            capture_output=True
        )
        print(f"✅ 已提交: {commit_msg}")
        
        # git push org main
        subprocess.run(
            ["git", "push", "org", "main"],
            check=True,
            capture_output=True
        )
        print("✅ 已推送到 my-ai-research-lab/ai-daily-report")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False
    finally:
        os.chdir(PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="AI日报外部版本同步脚本")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--all", action="store_true", help="同步所有日报")
    parser.add_argument("--no-push", action="store_true", help="不自动推送到远程")
    args = parser.parse_args()
    
    print("🔄 AI日报外部版本同步")
    print("=" * 50)
    
    # 确定要同步的日期
    if args.all:
        dates_to_sync = get_all_report_dates()
        print(f"📋 同步所有日报 ({len(dates_to_sync)} 篇)...")
    else:
        date_str = args.date or datetime.now().strftime("%Y-%m-%d")
        dates_to_sync = [date_str]
    
    # 同步文件
    synced_dates = []
    for date in dates_to_sync:
        if sync_report(date):
            synced_dates.append(date)
    
    if not synced_dates:
        print("❌ 没有成功同步任何日报")
        return
    
    # 更新 index.html
    all_dates = get_all_report_dates()
    # 合并已同步的日期（可能有新的）
    all_external_dates = []
    for f in EXTERNAL_REPO.glob("*.html"):
        if f.name != "index.html" and re.match(r"\d{4}-\d{2}-\d{2}\.html", f.name):
            all_external_dates.append(f.stem)
    
    update_external_index(all_external_dates)
    
    # Git 推送
    if not args.no_push:
        git_push()
    
    print("=" * 50)
    print(f"📊 同步完成: {len(synced_dates)} 篇日报")
    print(f"🔗 外部版本: https://my-ai-research-lab.github.io/ai-daily-report/")


if __name__ == "__main__":
    main()
