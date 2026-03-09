#!/usr/bin/env python3
"""
AI洞察 内部版→公开版 同步脚本 v2.0
====================================
将内部版内容脱敏后同步到 public/ 目录，覆盖所有公开内容。

v2.0 变更 (2026-03-09):
- 从"日报专用同步"升级为"全内容同步"
- 新增 02-deep-research/ 同步
- 新增 01-daily-reports/index.html 同步
- 新增 --verify 敏感词零残留验证
- 新增 --deep-research 深度调研同步
- 新增 shared/ 公共资源同步

教训: v1.0只处理日报HTML，周报/深度调研/子目录index全部遗漏。
根因: 脚本设计为"文件名模式匹配"而非"目录遍历"，新内容类型无法自动纳入。

使用方式:
  python scripts/sync_to_public.py --all --force --with-index     # 日报+周报+首页
  python scripts/sync_to_public.py --full --force                  # 全量同步（推荐）
  python scripts/sync_to_public.py --full --force --verify         # 全量+验证
  python scripts/sync_to_public.py 2026-03-05                      # 同步指定日期
  python scripts/sync_to_public.py --deep-research --force         # 仅深度调研

作者: AI洞察
版本: 2.0.0
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
INTERNAL_REPORTS = PROJECT_ROOT / "01-daily-reports"
PUBLIC_DIR = PROJECT_ROOT / "public"
PUBLIC_REPORTS = PUBLIC_DIR / "01-daily-reports"

# 需要同步的目录（除日报外）
SYNC_DIRS = {
    "02-deep-research": {
        "description": "深度调研报告",
        "extensions": [".html", ".css", ".js", ".json"],
        "exclude_patterns": ["test", "draft", "tmp"],
    },
    "shared": {
        "description": "公共资源",
        "extensions": [".css", ".js"],
        "exclude_patterns": [],
    },
}

# 不需要同步的目录/文件（内部专用）
EXCLUDE_DIRS = {
    "03-tracking-registry",   # 追踪体系（首页已内嵌）
    "04-knowledge-base",      # 知识库（不对外公开）
    "05-outputs",             # 产出物（不对外公开）
    "templates",              # 模板文件
    "scripts",                # 脚本文件
    "docs",                   # 内部文档
    "docs-publish",           # 发布用辅助文件
    ".codeflicker",           # IDE配置
    ".git",                   # Git
    "data",                   # 数据文件
    "public",                 # 已是输出目录
}

# 任何路径中包含这些目录名的都要排除
EXCLUDE_PATH_PARTS = {"node_modules", ".git", "__pycache__", ".DS_Store"}

# 需要替换的敏感词映射
REPLACEMENTS = [
    # ===== URL替换（最高优先级，必须在文字替换之前执行） =====
    (r'xiaoxiong20260206\.github\.io/ai-insight/', 'xiaoxiong20260206.github.io/ai-insight-public/'),
    (r'github\.com/xiaoxiong20260206/ai-insight', 'github.com/xiaoxiong20260206/ai-insight-public'),
    
    # ===== 文件名重写（public版统一去掉-v3后缀） =====
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
    
    # ===== 简单替换（兜底） =====
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
    
    # ===== 公司相关 =====
    (r'快手', '某公司'),
    (r'Kuaishou', 'Company'),
]

# 敏感词验证列表（脱敏后不应出现的词）
SENSITIVE_WORDS = ['林克', '沈浪', '快手', 'Kuaishou']


def sanitize_html(content: str) -> str:
    """对HTML内容进行脱敏处理"""
    result = content
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def sync_report(date_str: str, force: bool = False) -> bool:
    """同步单个日报到公开版本"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    src_html_v3 = INTERNAL_REPORTS / month_str / f"{date_str}-v3.html"
    src_html_plain = INTERNAL_REPORTS / month_str / f"{date_str}.html"
    src_html = src_html_v3 if src_html_v3.exists() else src_html_plain
    
    dst_dir = PUBLIC_REPORTS / month_str
    dst_html = dst_dir / f"{date_str}.html"
    
    if not src_html.exists():
        print(f"❌ 源文件不存在: {src_html}")
        return False
    
    if dst_html.exists() and not force:
        print(f"⏭️ 跳过已存在: {dst_html.name}")
        return True
    
    dst_dir.mkdir(parents=True, exist_ok=True)
    content = src_html.read_text(encoding="utf-8")
    sanitized = sanitize_html(content)
    dst_html.write_text(sanitized, encoding="utf-8")
    print(f"✅ 已同步: {date_str}")
    return True


def sync_generic_file(src_file: Path, src_base: Path, dst_base: Path, force: bool = False) -> bool:
    """
    通用文件同步：读取→脱敏→写入
    
    Args:
        src_file: 源文件绝对路径
        src_base: 源基准目录（用于计算相对路径）
        dst_base: 目标基准目录
        force: 是否强制覆盖
    """
    rel_path = src_file.relative_to(src_base)
    dst_file = dst_base / rel_path
    
    if dst_file.exists() and not force:
        return True  # 静默跳过
    
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 只对文本文件脱敏
    text_extensions = {'.html', '.css', '.js', '.json', '.md', '.txt', '.xml', '.svg'}
    if src_file.suffix.lower() in text_extensions:
        content = src_file.read_text(encoding="utf-8")
        sanitized = sanitize_html(content)
        dst_file.write_text(sanitized, encoding="utf-8")
    else:
        # 二进制文件直接复制
        import shutil
        shutil.copy2(src_file, dst_file)
    
    return True


def sync_all_reports(force: bool = False):
    """同步所有日报和周报"""
    count = 0
    weekly_count = 0
    synced_dates = set()
    
    for month_dir in sorted(INTERNAL_REPORTS.iterdir()):
        if not month_dir.is_dir() or month_dir.name.startswith('.'):
            continue
        
        for html_file in sorted(month_dir.glob("*.html")):
            if html_file.name == "index.html":
                continue
            if "test" in html_file.name:
                continue
            
            # 周报文件
            if html_file.name.startswith("weekly-"):
                month_str = month_dir.name
                dst_dir = PUBLIC_REPORTS / month_str
                dst_html = dst_dir / html_file.name
                
                if dst_html.exists() and not force:
                    continue
                
                dst_dir.mkdir(parents=True, exist_ok=True)
                content = html_file.read_text(encoding="utf-8")
                sanitized = sanitize_html(content)
                dst_html.write_text(sanitized, encoding="utf-8")
                print(f"✅ 已同步周报: {html_file.name}")
                weekly_count += 1
                continue
            
            # 日报文件
            stem = html_file.stem
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', stem)
            if not date_match:
                continue
            date_str = date_match.group(1)
            
            if date_str in synced_dates:
                continue
            synced_dates.add(date_str)
            
            if sync_report(date_str, force):
                count += 1
    
    if weekly_count > 0:
        print(f"✅ 共同步 {weekly_count} 篇周报")
    return count


def sync_reports_index(force: bool = False):
    """同步 01-daily-reports/index.html（v2.0新增）"""
    src = INTERNAL_REPORTS / "index.html"
    dst = PUBLIC_REPORTS / "index.html"
    
    if not src.exists():
        print("⏭️ 日报索引不存在，跳过")
        return False
    
    if dst.exists() and not force:
        print("⏭️ 跳过已存在: 01-daily-reports/index.html")
        return True
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    content = src.read_text(encoding="utf-8")
    sanitized = sanitize_html(content)
    dst.write_text(sanitized, encoding="utf-8")
    print("✅ 已同步日报索引: 01-daily-reports/index.html")
    return True


def sync_index(force: bool = False):
    """同步根首页"""
    src = PROJECT_ROOT / "index.html"
    dst = PUBLIC_DIR / "index.html"
    
    if not src.exists():
        print("❌ 内部版首页不存在")
        return False
    
    content = src.read_text(encoding="utf-8")
    sanitized = sanitize_html(content)
    dst.write_text(sanitized, encoding="utf-8")
    print("✅ 已同步首页: index.html")
    return True


def sync_directory(dir_name: str, force: bool = False) -> int:
    """
    同步指定目录到 public/（v2.0新增）
    
    Args:
        dir_name: 目录名（如 "02-deep-research"）
        force: 是否强制覆盖
    
    Returns:
        同步文件数
    """
    config = SYNC_DIRS.get(dir_name)
    if not config:
        print(f"❌ 未知目录: {dir_name}")
        return 0
    
    src_dir = PROJECT_ROOT / dir_name
    dst_dir = PUBLIC_DIR / dir_name
    
    if not src_dir.exists():
        print(f"⏭️ 目录不存在: {dir_name}")
        return 0
    
    count = 0
    for src_file in sorted(src_dir.rglob("*")):
        if not src_file.is_file():
            continue
        
        # 排除隐藏文件和 node_modules 等
        rel_parts = src_file.relative_to(src_dir).parts
        if any(p.startswith('.') for p in rel_parts):
            continue
        if any(p in EXCLUDE_PATH_PARTS for p in rel_parts):
            continue
        
        # 文件扩展名过滤
        if src_file.suffix.lower() not in config["extensions"]:
            continue
        
        # 排除模式
        if any(pat in src_file.name.lower() for pat in config["exclude_patterns"]):
            continue
        
        if sync_generic_file(src_file, PROJECT_ROOT, PUBLIC_DIR, force):
            count += 1
    
    print(f"✅ 已同步 {config['description']}: {count} 个文件")
    return count


def verify_sanitization() -> tuple:
    """
    验证 public/ 目录中是否有敏感词残留（v2.0新增）
    
    Returns:
        (is_clean, violations) - 是否干净, 违规列表
    """
    violations = []
    
    text_extensions = {'.html', '.css', '.js', '.json', '.md', '.txt'}
    
    for f in PUBLIC_DIR.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in text_extensions:
            continue
        # 排除隐藏文件
        rel_parts = f.relative_to(PUBLIC_DIR).parts
        if any(p.startswith('.') for p in rel_parts):
            continue
        
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        
        for word in SENSITIVE_WORDS:
            occurrences = [(m.start(), m.group()) for m in re.finditer(re.escape(word), content)]
            if occurrences:
                rel_path = f.relative_to(PUBLIC_DIR)
                for pos, match in occurrences:
                    # 提取上下文（前后30字符）
                    start = max(0, pos - 30)
                    end = min(len(content), pos + len(match) + 30)
                    context = content[start:end].replace('\n', ' ').strip()
                    violations.append({
                        "file": str(rel_path),
                        "word": word,
                        "context": f"...{context}...",
                    })
    
    is_clean = len(violations) == 0
    return is_clean, violations


def print_sync_summary(counts: dict):
    """打印同步汇总"""
    print()
    print("=" * 50)
    print("📊 同步汇总")
    print("-" * 50)
    for label, count in counts.items():
        status = "✅" if count > 0 else "⏭️"
        print(f"  {status} {label}: {count}")
    total = sum(counts.values())
    print(f"  📁 总计: {total} 个文件")
    print(f"  📂 公开版位置: {PUBLIC_DIR}")


def main():
    parser = argparse.ArgumentParser(
        description="AI洞察 内部版→公开版 同步脚本 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --full --force           # 全量同步（推荐）
  %(prog)s --full --force --verify  # 全量+敏感词验证
  %(prog)s --all --force --with-index  # 日报+周报+首页（兼容v1.0）
  %(prog)s 2026-03-05               # 同步指定日期日报
  %(prog)s --deep-research --force  # 仅同步深度调研
        """
    )
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--all", action="store_true", help="同步所有日报和周报")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")
    parser.add_argument("--with-index", action="store_true", help="同时同步首页")
    parser.add_argument("--deep-research", action="store_true", help="同步深度调研 (v2.0)")
    parser.add_argument("--full", action="store_true", help="全量同步所有公开内容 (v2.0)")
    parser.add_argument("--verify", action="store_true", help="验证脱敏完整性 (v2.0)")
    args = parser.parse_args()
    
    print("🔄 AI洞察 内部版→公开版 同步 v2.0")
    print("=" * 50)
    
    counts = {}
    
    # --full 模式: 全量同步
    if args.full:
        print("📋 [全量模式] 同步所有公开内容...")
        print()
        
        # 1. 日报+周报
        print("── 01-daily-reports/ ──")
        counts["日报"] = sync_all_reports(args.force)
        sync_reports_index(args.force)
        counts["日报索引"] = 1
        
        # 2. 首页
        print()
        print("── index.html ──")
        sync_index(args.force)
        counts["首页"] = 1
        
        # 3. 深度调研
        print()
        print("── 02-deep-research/ ──")
        counts["深度调研"] = sync_directory("02-deep-research", args.force)
        
        # 4. 公共资源
        print()
        print("── shared/ ──")
        counts["公共资源"] = sync_directory("shared", args.force)
        
        print_sync_summary(counts)
    
    else:
        # 兼容 v1.0 模式
        if args.all:
            print("📋 同步所有日报和周报...")
            count = sync_all_reports(args.force)
            print(f"✅ 共同步 {count} 篇日报")
            # v2.0: --all 时也同步日报索引
            sync_reports_index(args.force)
        elif args.date or (not args.deep_research and not args.full):
            date_str = args.date or datetime.now().strftime("%Y-%m-%d")
            sync_report(date_str, args.force)
        
        if args.with_index:
            sync_index(args.force)
        
        if args.deep_research:
            print("📋 同步深度调研...")
            sync_directory("02-deep-research", args.force)
        
        print("=" * 50)
        print(f"📁 公开版本位置: {PUBLIC_DIR}")
    
    # --verify 模式: 敏感词验证
    if args.verify:
        print()
        print("🔍 敏感词验证...")
        print("-" * 50)
        is_clean, violations = verify_sanitization()
        
        if is_clean:
            print("✅ 敏感词零残留！所有文件已通过验证。")
        else:
            print(f"❌ 发现 {len(violations)} 处敏感词残留:")
            for v in violations[:20]:  # 最多显示20条
                print(f"   📄 {v['file']}")
                print(f"      敏感词: {v['word']}")
                print(f"      上下文: {v['context']}")
            if len(violations) > 20:
                print(f"   ... 还有 {len(violations) - 20} 处")
            sys.exit(1)


if __name__ == "__main__":
    main()
