#!/usr/bin/env python3
"""
AI日报双版本同步脚本
===================
将内部版日报同步生成到公开版本(public目录)

功能:
1. 读取内部版日报HTML
2. 移除敏感信息(林克、沈浪、快手等)
3. 输出到 public/01-daily-reports/ 目录

使用方式:
  python scripts/sync_to_public.py                    # 同步今天的日报
  python scripts/sync_to_public.py 2026-03-05         # 同步指定日期
  python scripts/sync_to_public.py --all              # 同步所有日报

作者: AI洞察
版本: 1.0.0
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
INTERNAL_REPORTS = PROJECT_ROOT / "01-daily-reports"
PUBLIC_REPORTS = PROJECT_ROOT / "public" / "01-daily-reports"

# 需要替换的敏感词映射
REPLACEMENTS = [
    # ===== URL替换（最高优先级，必须在文字替换之前执行） =====
    # 将所有指向内部版仓库的链接改为指向公开版
    (r'xiaoxiong20260206\.github\.io/ai-insight/', 'xiaoxiong20260206.github.io/ai-insight-public/'),
    (r'github\.com/xiaoxiong20260206/ai-insight', 'github.com/xiaoxiong20260206/ai-insight-public'),
    
    # ===== 文件名重写（public版统一去掉-v3后缀） =====
    # sync_report()会把-v3.html重命名为.html，index.html中的链接也必须同步
    (r'(\d{4}-\d{2}-\d{2})-v3\.html', r'\1.html'),
    
    # ===== 标题和描述 =====
    (r'林克的AI洞察', 'AI行业洞察'),
    (r'我是林克，这是沈浪让我负责的AI洞察项目', 'AI洞察 · 持续追踪AI行业动态'),
    (r'林克负责的AI行业洞察项目', '持续追踪AI行业动态'),
    
    # ===== 页脚和署名 =====
    (r'由 <strong>林克</strong>（沈浪的AI分身）完成洞察', 'AI洞察'),
    (r'林克（沈浪的AI分身）· AI洞察', 'AI洞察'),
    (r'由 <a href="https://github.com/xiaoxiong20260206" target="_blank">林克</a>（沈浪的AI分身）负责维护', 'AI洞察 · 持续追踪AI行业动态'),
    (r'由林克（沈浪的AI分身）每日更新', '每日更新'),
    
    # ===== 页头Badge =====
    (r'📡 林克的AI洞察项目 - AI日报', '📡 AI行业洞察 - AI日报'),
    
    # ===== 介绍文本 =====
    (r'我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。',
     'AI洞察是一个系统化追踪AI行业动态的项目，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。'),
    
    # ===== 简单替换 =====
    (r'林克', 'AI洞察'),
    (r'沈浪', ''),
    (r'（的AI分身）', ''),
    (r'的AI分身', ''),
    (r'沈浪让我负责的', ''),
    
    # ===== 时间戳格式调整 =====
    (r'⏰ 每日8点更新', '⏰ 每日更新'),
    
    # ===== 知识库中的个人感悟 =====
    (r'🌱</span> 每日学习，每日精进中！我是AI，同时也能越来越理解AI本身。',
     '🌱</span> 每日更新，持续追踪AI行业动态。'),
    
    # ===== 快手相关 =====
    (r'快手', '某公司'),
    (r'Kuaishou', 'Company'),
]


def sanitize_html(content: str) -> str:
    """对HTML内容进行脱敏处理"""
    result = content
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def sync_report(date_str: str, force: bool = False) -> bool:
    """
    同步单个日报到公开版本
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        force: 是否强制覆盖已存在的文件
    
    Returns:
        是否成功同步
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    # 源文件路径（优先使用v3版本）
    src_html_v3 = INTERNAL_REPORTS / month_str / f"{date_str}-v3.html"
    src_html_plain = INTERNAL_REPORTS / month_str / f"{date_str}.html"
    src_html = src_html_v3 if src_html_v3.exists() else src_html_plain
    src_md = INTERNAL_REPORTS / month_str / f"{date_str}.md"
    
    # 目标路径
    dst_dir = PUBLIC_REPORTS / month_str
    dst_html = dst_dir / f"{date_str}.html"
    
    if not src_html.exists():
        print(f"❌ 源文件不存在: {src_html}")
        return False
    
    if dst_html.exists() and not force:
        print(f"⏭️ 跳过已存在: {dst_html.name}")
        return True
    
    # 确保目标目录存在
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取并脱敏
    content = src_html.read_text(encoding="utf-8")
    sanitized = sanitize_html(content)
    
    # 写入公开版本
    dst_html.write_text(sanitized, encoding="utf-8")
    print(f"✅ 已同步: {date_str}")
    
    return True


def sync_all_reports(force: bool = False):
    """同步所有日报"""
    count = 0
    synced_dates = set()  # 防止重复同步同一天
    for month_dir in sorted(INTERNAL_REPORTS.iterdir()):
        if not month_dir.is_dir() or month_dir.name.startswith('.'):
            continue
        
        for html_file in sorted(month_dir.glob("*.html")):
            if html_file.name == "index.html":
                continue
            
            # 跳过测试文件
            if "test" in html_file.name:
                continue
            
            # 从文件名提取日期（支持 2026-03-05.html 和 2026-03-05-v3.html 格式）
            stem = html_file.stem  # 例如 "2026-03-05" 或 "2026-03-05-v3"
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', stem)
            if not date_match:
                continue
            date_str = date_match.group(1)
            
            # 跳过已同步的日期
            if date_str in synced_dates:
                continue
            synced_dates.add(date_str)
            
            if sync_report(date_str, force):
                count += 1
    
    return count


def sync_index():
    """同步首页"""
    src = PROJECT_ROOT / "index.html"
    dst = PROJECT_ROOT / "public" / "index.html"
    
    if not src.exists():
        print("❌ 内部版首页不存在")
        return False
    
    content = src.read_text(encoding="utf-8")
    sanitized = sanitize_html(content)
    
    dst.write_text(sanitized, encoding="utf-8")
    print("✅ 已同步首页")
    return True


def main():
    parser = argparse.ArgumentParser(description="AI日报双版本同步脚本")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--all", action="store_true", help="同步所有日报")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")
    parser.add_argument("--with-index", action="store_true", help="同时同步首页")
    args = parser.parse_args()
    
    print("🔄 AI日报双版本同步")
    print("=" * 50)
    
    if args.all:
        print("📋 同步所有日报...")
        count = sync_all_reports(args.force)
        print(f"✅ 共同步 {count} 篇日报")
    else:
        date_str = args.date or datetime.now().strftime("%Y-%m-%d")
        sync_report(date_str, args.force)
    
    if args.with_index:
        sync_index()
    
    print("=" * 50)
    print(f"📁 公开版本位置: {PUBLIC_REPORTS}")


if __name__ == "__main__":
    main()
