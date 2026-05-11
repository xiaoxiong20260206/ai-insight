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
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    PROJECT_ROOT,
    INTERNAL_PAGES_BASE,
    EXTERNAL_PAGES_BASE,
    INTERNAL_GITHUB_URL,
    EXTERNAL_GITHUB_URL,
    INTERNAL_GITHUB_USER,
    EXTERNAL_GITHUB_USER,
    EXTERNAL_REPO_NAME,
)
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
    "04-knowledge-base",      # 知识库（不对外公开，symlink → knowledge/packages/ai-insight/）
    "05-outputs",             # 产出物（不对外公开）
    "templates",              # 模板文件
    "scripts",                # 脚本文件
    "docs",                   # 内部文档
    "docs-publish",           # 发布用辅助文件
    ".cf",           # IDE配置
    ".git",                   # Git
    "data",                   # 数据文件
    "public",                 # 已是输出目录
}

# 任何路径中包含这些目录名的都要排除
EXCLUDE_PATH_PARTS = {"node_modules", ".git", "__pycache__", ".DS_Store"}

# 需要替换的敏感词映射（URL部分动态生成，根治硬编码根因 — 经验#73）
def _build_url_replacements():
    """URL 替换规则动态生成，仓库名/账号变更只改 config.py"""
    int_base = re.escape(INTERNAL_PAGES_BASE.rstrip('/'))
    ext_base = EXTERNAL_PAGES_BASE.rstrip('/')
    int_gh   = re.escape(INTERNAL_GITHUB_URL)
    ext_gh   = EXTERNAL_GITHUB_URL
    return [
        (rf'{int_base}/', f'{ext_base}/'),
        (rf'{int_gh}', f'{ext_gh}'),
    ]

_URL_REPLACEMENTS = _build_url_replacements()

REPLACEMENTS = _URL_REPLACEMENTS + [
    # ===== (下方规则由 _build_url_replacements 生成，此处为其余脱敏规则) =====
    
    # ===== 文件名重写（public版统一去掉-v3后缀） =====
    (r'(\d{4}-\d{2}-\d{2})-v3\.html', r'\1.html'),
    
    # ===== 标题和描述 =====
    (r'林克的AI洞察', 'AI行业洞察'),
    (r'我是林克，这是沈浪让我负责的AI洞察项目', 'AI洞察 · 持续追踪AI行业动态'),
    (r'林克负责的AI行业洞察项目', '持续追踪AI行业动态'),
    
    # ===== 页脚和署名 =====
    (r'由 <strong>林克</strong>（沈浪的AI分身）完成洞察', 'AI洞察'),
    (r'林克（沈浪的AI分身）· AI洞察', 'AI洞察'),
    (r'由 <a href="https://github.com/xiaoxiong20260206" target="_blank">[^<]*</a>（[^）]*）负责维护', 'AI洞察 · 持续追踪AI行业动态'),
    (r'由 <a href="https://github.com/xiaoxiong20260206" target="_blank">林克</a>（沈浪的AI分身）负责维护', 'AI洞察 · 持续追踪AI行业动态'),
    (r'由林克（沈浪的AI分身）每日更新', '每日更新'),
    (r'由林克 AI 洞察系统生成', '由 AI 洞察系统生成'),  # #114: 防止"由AI洞察 AI洞察系统"重复
    (r'AI分身', 'AI洞察'),  # #115: "AI分身"也是身份暴露
    (r'让我负责', ''),  # #115: "让我负责"暗示个人身份
    (r'Powered by MyFlicker ❤️🔥（沈浪的AI工作伙伴）', 'Powered by ❤️🔥'),
    (r'Powered by MyFlicker ❤️🔥', 'Powered by ❤️🔥'),
    (r'MyFlicker', 'AI洞察'),  # #115: 平台名也暴露内部信息
    (r'myflicker', 'ai-insight'),
    (r'my-ai-research-lab', 'ai-insight-lab'),
    # link-avatar-small.webp 在外部版直接去除（下方有整块div删除规则，此行兜底）
    (r'src="link-avatar-small\.webp"[^>]*>', 'style="display:none">'),
    (r'link-avatar', 'ai-insight-logo'),  # #115: 头像文件名含内部身份
    
    # ===== 页头Badge =====
    (r'📡 林克的AI洞察项目 - AI日报', '📡 AI行业洞察 - AI日报'),
    
    # ===== 介绍文本 =====
    (r'我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。',
     'AI洞察是一个系统化追踪AI行业动态的项目，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。'),
    
    # ===== 林克头像图片（外部版去掉头像，保留文字） =====
    (r'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">\s*<img src="[^"]*link-avatar-small\.webp"[^>]*>\s*<span>', '<span>'),
    (r'<div style="text-align:center; margin-bottom:16px;">\s*<img src="link-avatar-small\.webp"[^>]*>\s*</div>', ''),
    (r'<div style="margin-bottom:12px;">\s*<img src="link-avatar-small\.webp"[^>]*>\s*<strong>林克</strong> · 沈浪的AI分身', '<strong>AI洞察</strong>'),
    # footer 中的头像图片 div（· 的AI洞察 是脱敏后的残留）
    (r'<div style="margin-bottom:12px;">\s*<img src="ai-insight-logo\.webp"[^>]*>\s*<strong>AI洞察</strong> · 的AI洞察\s*</div>', ''),
    (r'<div style="margin-bottom:12px;">\s*<img[^>]*ai-insight-logo[^>]*>[^<]*</div>', ''),
    
    # ===== 简单替换（兜底） =====
    (r'林克', 'AI洞察'),
    (r'沈浪', ''),
    # CF品牌词替换（v9.6新增：防止品牌词泄露到公开版）
    # ⚠️ v9.7修复：禁止替换CSS颜色值中的CF（如 #ECFDF5、#8B5CF6）
    # 使用负向lookbehind：CF前面不能是十六进制字符(0-9A-Fa-f)或#
    (r'(?<![0-9A-Fa-f#])CF(?![0-9A-Fa-f])', 'AI助手平台'),
    (r'基于CF打造的', ''),
    (r'AI数字分身', 'AI洞察'),
    (r'沈浪让我负责的', ''),
    
    # ===== 时间戳格式调整 =====
    (r'⏰ 每日8点更新', '⏰ 每日更新'),
    
    # ===== 知识库中的个人感悟 =====
    (r'🌱</span> 每日学习，每日精进中！我是AI，同时也能越来越理解AI本身。',
     '🌱</span> 每日更新，持续追踪AI行业动态。'),
    
    # ===== 公司相关（v2.2恢复全局替换 — 保持替换规则和检查规则一致性）=====
    # ⚠️ 注意: SENSITIVE_WORDS 和 deploy_daily.sh 的 grep 都检查「快手」
    # 必须保持一致：替换了才能通过验证；只要这里不替换，公开版敏感词检查就会 abort
    # v2.1曾尝试「只替换机构名」，但与 SENSITIVE_WORDS 检查不一致，会导致部署 abort
    (r'快手', '某公司'),
    (r'Kuaishou', 'Company'),
    
    # ===== #115: 全量脱敏新增规则（深度调研/周报中的内部工具/平台名） =====
    (r'KATE平台', 'Agent平台'),
    (r'KATE', 'Agent平台'),
    (r'天策平台', '数据平台'),
    (r'天策', '数据平台'),
    (r'天玑平台', '数据分析平台'),
    (r'天玑', '数据分析平台'),
    (r'KwaiBI', 'BI平台'),
    (r'CodeFlicker', 'AI IDE'),
    (r'Titi', '数据Agent'),
    (r'SKILL\.md体系', '技能体系'),
    (r'SKILL\.md', '技能定义文件'),
    (r'小无相功', '自进化体系'),
    (r'KIM Doc', '内部文档'),
    (r'docs\.corp\.kuaishou\.com[^"]*', '#internal-link'),
    (r'shenlang03', ''),
    (r'shenlang', ''),
    
    # ===== 外部版首页订阅按钮自动剥离（v10.4 经验62）=====
    # 外部版是公开页面，订阅功能需要内部认证，不提供此能力
    # 匹配 header 区域内订阅按钮 div（含 <a href="./subscribe/">）
    (r'<div style="margin-top: 24px; text-align: center;">[\s\S]*?订阅AI日报[\s\S]*?</div>', ''),
]

# 敏感词验证列表（脱敏后不应出现的词）
# v12.0: public/ 是内部版Pages部署源（经验#114），"林克"等品牌内容是合法的
# 只检查不应该出现的真正敏感词（公司内部代号、内网地址、沈浪个人信息）
# "林克"、"AI分身"、"让我负责" 等是内部版品牌标识，不检测
PUBLIC_SENSITIVE_WORDS = ['沈浪', '快手', 'Kuaishou', 'CodeFlicker', 'KATE', '天策', '天玑', 'KwaiBI', '小无相功', 'docs.corp.kuaishou', 'shenlang', 'KIM Doc', 'MyFlicker', 'myflicker']  # v12.0: 不含"林克/AI分身/让我负责/link-avatar/CF/SKILL.md"


def sanitize_html(content: str) -> str:
    """对HTML内容进行脱敏处理"""
    result = content
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def preserve_block(generated_content: str, existing_content: str, start_marker: str, end_marker: str):
    """保留目标文件中的手工维护区块，避免同步覆盖。"""
    generated_start = generated_content.find(start_marker)
    generated_end = generated_content.find(end_marker)
    existing_start = existing_content.find(start_marker)
    existing_end = existing_content.find(end_marker)

    if min(generated_start, generated_end, existing_start, existing_end) == -1:
        return generated_content, False
    if generated_start >= generated_end or existing_start >= existing_end:
        return generated_content, False

    preserved_block = existing_content[existing_start:existing_end]
    merged_content = (
        generated_content[:generated_start]
        + preserved_block
        + generated_content[generated_end:]
    )
    return merged_content, True


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
        
        # 同步 .md 文件（v2.3新增：.md含「林克自述」章节，必须脱敏）
        for md_file in sorted(month_dir.glob("*.md")):
            if md_file.stem.endswith('-v3'):  # 内部版专有文件，跳过
                continue
            dst_md = PUBLIC_REPORTS / month_dir.name / md_file.name
            if dst_md.exists() and not force:
                continue
            dst_md.parent.mkdir(parents=True, exist_ok=True)
            content = md_file.read_text(encoding="utf-8")
            sanitized = sanitize_html(content)
            dst_md.write_text(sanitized, encoding="utf-8")
        
        for html_file in sorted(month_dir.glob("*.html")):
            if html_file.name == "index.html":
                continue
            if "test" in html_file.name:
                continue
            # ⭐ v2.3修复：明确跳过 -v3.html（内部版文件，由 sync_report 读取后脱敏输出为不带v3的文件）
            # 无需直接复制 -v3.html 进 public/，sync_report(date_str) 会主动读取并脱敏
            if html_file.stem.endswith('-v3'):
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
    """同步根首页（v3.0：内部版Pages保留林克身份，脱敏版单独推ai-insight-public）"""
    src = PROJECT_ROOT / "index.html"
    dst = PUBLIC_DIR / "index.html"
    
    if not src.exists():
        print("❌ 内部版首页不存在")
        return False
    
    # ⭐ v2.1: 内部版首页被污染检测（经验#55防护）
    content = src.read_text(encoding="utf-8")
    link_count = content.count('林克')
    if link_count == 0:
        print("⚠️ [WARNING] 内部版首页中未找到'林克'字样，疑似被脱敏版覆盖！")
        print("   请检查: grep -c '林克' index.html")
        print("   如果确认是污染，从最近正确commit恢复: git checkout bcb0937 -- index.html")
        print("   继续同步（将复制当前内容）...")
    else:
        print(f"✅ 内部版首页内容正常（林克: {link_count}处），开始同步...")
    
    # ⭐ v3.0: public/ 保留原始内容（含林克），用于内部版 Pages 部署
    # 脱敏版由 ai-insight-public 仓库单独管理
    dst.write_text(content, encoding="utf-8")
    print("✅ 已同步首页到 public/（内部版，保留林克身份）")
    
    # 同时生成脱敏版到 ai-insight-public 仓库
    external_repo = PROJECT_ROOT.parent / "ai-insight-public"
    if external_repo.exists() and external_repo.is_dir():
        sanitized = sanitize_html(content)
        ext_dst = external_repo / "index.html"
        if ext_dst.exists():
            existing_public = ext_dst.read_text(encoding="utf-8")
            sanitized, preserved = preserve_block(
                sanitized,
                existing_public,
                "<!-- 2. 深度调研 -->",
                "<!-- 3. 追踪体系 -->",
            )
            if preserved:
                print("🛡️ 已保留外部版手工维护的深度调研区块")
        ext_dst.write_text(sanitized, encoding="utf-8")
        print("✅ 已同步脱敏首页到 ai-insight-public/")
    else:
        print("⚠️ ai-insight-public 仓库不存在，跳过脱敏版同步")
    
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
    验证外部版(ai-insight-public/)目录中是否有敏感词残留和 -v3 链接残留（v12.0修复）
    
    v12.0: 验证目标从 public/（内部版）改为 ai-insight-public/（外部版）
    因为 public/ 是内部版Pages部署源，包含"林克"是正确行为
    
    检查项:
    1. 敏感词残留（沈浪/快手/Kuaishou等在外部版中不应出现）
    2. -v3.html 链接残留
    
    Returns:
        (is_clean, violations) - 是否干净, 违规列表
    """
    violations = []
    
    # v12.0: 验证外部版而非内部版
    external_repo = PROJECT_ROOT.parent / "ai-insight-public"
    if not external_repo.exists():
        print("⚠️ 外部版仓库不存在，跳过验证")
        return True, []
    
    verify_dir = external_repo
    text_extensions = {'.html', '.css', '.js', '.json', '.md', '.txt'}
    
    # v2.2: -v3.html 链接残留检测模式
    v3_link_pattern = re.compile(r'\d{4}-\d{2}-\d{2}-v3\.html')
    
    for f in verify_dir.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in text_extensions:
            continue
        # 排除隐藏文件
        rel_parts = f.relative_to(verify_dir).parts
        if any(p.startswith('.') for p in rel_parts):
            continue
        
        try:
            content = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        
        rel_path = f.relative_to(verify_dir)
        
        # 检查1: 敏感词残留
        for word in PUBLIC_SENSITIVE_WORDS:
            occurrences = [(m.start(), m.group()) for m in re.finditer(re.escape(word), content)]
            if occurrences:
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
        
        # 检查2: -v3.html 链接残留（v2.2新增）
        # public版的文件名已统一去掉-v3后缀，但引用链接可能遗漏替换
        v3_matches = list(v3_link_pattern.finditer(content))
        if v3_matches:
            for m in v3_matches:
                pos = m.start()
                start = max(0, pos - 30)
                end = min(len(content), m.end() + 30)
                context = content[start:end].replace('\n', ' ').strip()
                violations.append({
                    "file": str(rel_path),
                    "word": f"-v3.html残留({m.group()})",
                    "context": f"...{context}...",
                })
    
    is_clean = len(violations) == 0
    return is_clean, violations


def verify_consistency():
    """v2.6新增: 验证内部版和public版的深度调研文件一致性
    
    教训: 2026-04-06 meta-skill-system-2026.html 被直接推送到外部仓库，
    绕过脱敏管道，导致外部版有内部版没有的文件。
    
    检查规则:
    1. public/ 中不应存在内部版没有的文件（反向泄漏检测）
    2. 内部版的HTML文件应在public/中都有对应（正向完整性检测）
    """
    internal_dr = PROJECT_ROOT / "02-deep-research"
    public_dr = PUBLIC_DIR / "02-deep-research"
    
    if not internal_dr.exists() or not public_dr.exists():
        return True, []
    
    issues = []
    
    # 收集内部版和public版的HTML文件（相对路径）
    internal_htmls = set()
    for f in internal_dr.rglob("*.html"):
        if any(part in f.parts for part in EXCLUDE_PATH_PARTS):
            continue
        internal_htmls.add(str(f.relative_to(internal_dr)))
    
    public_htmls = set()
    for f in public_dr.rglob("*.html"):
        if any(part in f.parts for part in EXCLUDE_PATH_PARTS):
            continue
        public_htmls.add(str(f.relative_to(public_dr)))
    
    # 检查1: public有但内部版没有的文件（反向泄漏）
    orphan_in_public = public_htmls - internal_htmls
    for f in sorted(orphan_in_public):
        issues.append({
            "type": "orphan_public",
            "file": f,
            "message": f"⚠️ public/ 中存在但内部版没有的文件: {f} (可能是绕过管道直接推送的)"
        })
    
    # 检查2: 内部版有但public没有的文件（遗漏同步）
    missing_in_public = internal_htmls - public_htmls
    for f in sorted(missing_in_public):
        issues.append({
            "type": "missing_public",
            "file": f,
            "message": f"ℹ️ 内部版有但 public/ 没有的文件: {f}"
        })
    
    return len(issues) == 0, issues


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
        
        # v2.6新增: 一致性验证
        print()
        print("🔍 一致性验证（内部版 vs public/）...")
        print("-" * 50)
        is_consistent, consistency_issues = verify_consistency()
        
        if is_consistent:
            print("✅ 内部版与 public/ 深度调研文件完全一致。")
        else:
            orphan_count = sum(1 for i in consistency_issues if i["type"] == "orphan_public")
            missing_count = sum(1 for i in consistency_issues if i["type"] == "missing_public")
            
            if orphan_count > 0:
                print(f"⚠️ 发现 {orphan_count} 个反向泄漏文件（public/有但内部版没有）:")
                for i in consistency_issues:
                    if i["type"] == "orphan_public":
                        print(f"   {i['message']}")
            
            if missing_count > 0:
                print(f"ℹ️ 发现 {missing_count} 个未同步文件（内部版有但public/没有）:")
                for i in consistency_issues:
                    if i["type"] == "missing_public":
                        print(f"   {i['message']}")
            
            if orphan_count > 0:
                print("\n⛔ 一致性验证失败！请检查是否有文件绕过脱敏管道。")
                sys.exit(1)


if __name__ == "__main__":
    main()
