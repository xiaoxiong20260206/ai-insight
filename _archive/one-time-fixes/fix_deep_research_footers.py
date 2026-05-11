#!/usr/bin/env python3
"""
批量修改深度调研报告底部：
1. 删除冗余的返回链接、版本信息、关于林克卡片等
2. 统一添加"了解更多"模块（与AI日报格式完全一致）
"""

import os
import re

# ============================================================
# 标准"了解更多"模块 - 完全内联样式，兼容所有报告
# ============================================================
LEARN_MORE_MODULE = '''
    <!-- 了解更多 -->
    <div style="margin-top:24px;background:linear-gradient(135deg,#F6F8FA 0%,#EEF2F6 100%);border:1px solid #E8ECF0;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06),0 1px 2px rgba(31,35,40,.04)">
        <div style="font-size:16px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px">💡 了解更多</div>
        <p style="font-size:14px;color:#4D5561;line-height:1.7;margin:0 0 12px 0">
            我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。
        </p>
        <a href="https://xiaoxiong20260206.github.io/ai-insight/" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#1A7F37 0%,#2DA44E 100%);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
            🏠 访问AI洞察首页
        </a>
    </div>
'''

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DR = os.path.join(ROOT, '02-deep-research')

def get_learn_more(indent='    '):
    """返回指定缩进的了解更多模块"""
    lines = LEARN_MORE_MODULE.strip().split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            result.append(indent + stripped)
        else:
            result.append('')
    return '\n'.join(result)

def remove_block(content, start_marker, end_marker):
    """移除从 start_marker 到 end_marker（含）之间的内容"""
    start = content.find(start_marker)
    if start == -1:
        return content
    end = content.find(end_marker, start)
    if end == -1:
        return content
    end += len(end_marker)
    # 也删除前后的空白行
    while end < len(content) and content[end] in '\n\r':
        end += 1
    return content[:start] + content[end:]

def find_footer_range(content):
    """找到最后一个 <footer 到对应 </footer> 的范围"""
    # 找最后一个 <footer
    last_footer = content.rfind('<footer')
    if last_footer == -1:
        return None, None
    
    # 找对应的 </footer>
    close = content.find('</footer>', last_footer)
    if close == -1:
        return None, None
    close += len('</footer>')
    
    # 向前查找，看是否有注释标记（如 <!-- Footer --> 或 <!-- 页脚 -->）
    search_start = max(0, last_footer - 200)
    before = content[search_start:last_footer]
    comment_patterns = [
        '<!-- Footer -->',
        '<!-- 页脚 -->',
        '<!-- footer -->',
        '<!-- ==================== Footer ==================== -->',
    ]
    earliest = last_footer
    for pat in comment_patterns:
        idx = before.rfind(pat)
        if idx != -1:
            earliest = search_start + idx
            break
    
    # 向前找到行首
    while earliest > 0 and content[earliest-1] != '\n':
        earliest -= 1
    
    # 向后跳过空行
    while close < len(content) and content[close] in '\n\r':
        close += 1
    
    return earliest, close

def process_standard_report(filepath):
    """处理标准报告：替换整个footer为了解更多模块"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. 先移除 footer 之前的冗余块
    # 移除"关于林克"卡片
    if 'about-card' in content:
        pattern = r'<!-- 关于林克 -->.*?</div>\s*</div>\s*\n'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        # 也尝试直接匹配 about-card div
        if 'about-card' in content:
            # 找 about-card 的开始
            idx = content.find('class="about-card"')
            if idx != -1:
                # 向前找到 <div
                div_start = content.rfind('<div', max(0, idx-100), idx)
                if div_start != -1:
                    # 找到对应的闭合（计数嵌套div）
                    pos = idx
                    depth = 1
                    while pos < len(content) and depth > 0:
                        next_open = content.find('<div', pos + 1)
                        next_close = content.find('</div>', pos + 1)
                        if next_close == -1:
                            break
                        if next_open != -1 and next_open < next_close:
                            depth += 1
                            pos = next_open
                        else:
                            depth -= 1
                            pos = next_close
                    if depth == 0:
                        end = pos + len('</div>')
                        # 检查前面是否有注释
                        check_start = max(0, div_start - 50)
                        before = content[check_start:div_start]
                        comment_match = re.search(r'<!--.*?-->\s*$', before)
                        if comment_match:
                            div_start = check_start + comment_match.start()
                        while end < len(content) and content[end] in '\n\r':
                            end += 1
                        content = content[:div_start] + content[end:]
    
    # 移除导航链接卡片（openclaw特有）
    nav_card_pattern = r'<div class="card" style="text-align: center;">\s*<a href="[^"]*">🏠 AI洞察首页</a>.*?</div>\s*\n'
    content = re.sub(nav_card_pattern, '', content, flags=re.DOTALL)
    
    # 移除已有的"了解更多"区块（ai-product-transformation特有）
    learn_more_pattern = r'<!-- 了解更多 -->\s*<div class="section"[^>]*>.*?</div>\s*\n'
    content = re.sub(learn_more_pattern, '', content, flags=re.DOTALL)
    # 也匹配 style 内联的了解更多
    learn_more_pattern2 = r'<div[^>]*style="[^"]*linear-gradient[^"]*"[^>]*>\s*<h3[^>]*>💡 了解更多</h3>.*?</div>\s*\n'
    content = re.sub(learn_more_pattern2, '', content, flags=re.DOTALL)
    
    # 2. 找到并替换 footer
    start, end = find_footer_range(content)
    if start is None:
        print(f"  ⚠️  未找到 footer: {filepath}")
        return False
    
    # 检测缩进级别
    indent = '    '
    line_start = content.rfind('\n', 0, start)
    if line_start != -1:
        line = content[line_start+1:start+20]
        spaces = len(line) - len(line.lstrip())
        if spaces > 0:
            indent = ' ' * spaces
    
    # 替换为了解更多模块
    replacement = get_learn_more(indent) + '\n'
    content = content[:start] + replacement + content[end:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def process_multichapter_report(filepath):
    """处理多章节报告：保留章节导航，在footer后添加了解更多模块"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 找到 footer
    start, end = find_footer_range(content)
    if start is None:
        print(f"  ⚠️  未找到 footer: {filepath}")
        return False
    
    footer_content = content[start:end]
    
    # 提取章节导航链接
    nav_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', footer_content)
    
    # 过滤：保留章节导航（chapter, index, 上一章, 下一章, 开始阅读, 返回目录, 首页）
    # 但移除"返回首页"和"AI-Insight首页"类的外部链接
    chapter_links = []
    for href, text in nav_links:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        # 跳过外部首页链接
        if '../../index.html' in href or '../../../index.html' in href:
            continue
        if 'xiaoxiong20260206.github.io' in href:
            continue
        if 'AIFinLearn' in href:
            continue
        # 保留章节导航
        chapter_links.append((href, clean_text))
    
    # 检测缩进
    indent = '        '
    line_start = content.rfind('\n', 0, start)
    if line_start != -1:
        line = content[line_start+1:start+20]
        spaces = len(line) - len(line.lstrip())
        if spaces > 0:
            indent = ' ' * spaces
    
    # 构建新的底部区域
    parts = []
    
    # 如果有章节导航链接，保留为简洁导航
    if chapter_links:
        nav_html = f'{indent}<!-- 章节导航 -->\n'
        nav_html += f'{indent}<div style="margin-top:24px;padding-top:16px;border-top:1px solid #E8ECF0;display:flex;justify-content:{"space-between" if len(chapter_links) > 1 else "flex-end"};align-items:center;gap:12px;flex-wrap:wrap">\n'
        for href, text in chapter_links:
            nav_html += f'{indent}    <a href="{href}" style="color:#1A7F37;text-decoration:none;font-size:14px;font-weight:500">{text}</a>\n'
        nav_html += f'{indent}</div>\n'
        parts.append(nav_html)
    
    # 添加了解更多模块
    parts.append(get_learn_more(indent))
    
    replacement = '\n'.join(parts) + '\n'
    content = content[:start] + replacement + content[end:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def process_bytedance_report(filepath):
    """处理字节跳动指南：保留页面导航，替换footer"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 找到 footer
    start, end = find_footer_range(content)
    if start is None:
        print(f"  ⚠️  未找到 footer: {filepath}")
        return False
    
    footer_content = content[start:end]
    
    # 字节指南的footer有 container > h3 + footer-links + footer-bottom
    # 保留 footer-links 中的章节导航链接
    nav_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', footer_content)
    
    chapter_links = []
    for href, text in nav_links:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        # 保留所有章节页面链接
        if href.endswith('.html') and 'index.html' not in href:
            chapter_links.append((href, clean_text))
        elif href == '../home.html' or href == 'home.html':
            chapter_links.insert(0, (href, '首页'))
    
    # 检测缩进
    indent = '    '
    
    # 构建替换内容
    parts = []
    
    if chapter_links:
        nav_html = f'{indent}<!-- 章节导航 -->\n'
        nav_html += f'{indent}<div style="margin-top:24px;padding:16px 0;border-top:1px solid #E8ECF0;display:flex;justify-content:center;align-items:center;gap:16px;flex-wrap:wrap">\n'
        for href, text in chapter_links:
            nav_html += f'{indent}    <a href="{href}" style="color:#1A7F37;text-decoration:none;font-size:13px;font-weight:500">{text}</a>\n'
        nav_html += f'{indent}</div>\n'
        parts.append(nav_html)
    
    parts.append(get_learn_more(indent))
    
    replacement = '\n'.join(parts) + '\n'
    content = content[:start] + replacement + content[end:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# ============================================================
# 文件清单
# ============================================================

# Group 1: 标准独立报告 - 直接替换footer
STANDARD_REPORTS = [
    'trends/ai-leaders-2026.html',
    'trends/barry-zhang-anthropic.html',
    'topics/ai-product-transformation-2026.html',
    'topics/openclaw-deep-research-2026.html',
    'topics/ai-essence-insight/index.html',
    'topics/ai-tools-analysis/index.html',
    'topics/ai-studio/index.html',
    'topics/ai-studio/2-ai-workbench/index.html',
    'topics/ai-studio/3-agent-infra/index.html',
    'topics/ai-studio/docs/CF-不只是编码-发布版.html',
    'topics/ai-studio/docs/diagrams.html',
]

# Group 2: 多章节报告 - 保留章节导航
MULTICHAPTER_REPORTS = [
    'topics/ai-agent-guide/index.html',
    'topics/ai-agent-guide/chapter1-scenarios.html',
    'topics/ai-agent-guide/chapter2-architecture.html',
    'topics/ai-agent-guide/chapter3-implementation.html',
    'topics/ai-agent-guide/chapter4-future.html',
    'topics/ai-agent-guide/appendix-industry-research.html',
    'topics/ai-financial/index.html',
    'topics/ai-financial/产品架构.html',
    'topics/ai-financial/幻方量化调研报告.html',
    'topics/ai-studio/1-ai-engineer-analysis/index.html',
    'topics/ai-studio/1-ai-engineer-analysis/agent-details.html',
    'topics/ai-studio/3-agent-infra/application-layer.html',
    'topics/ai-studio/3-agent-infra/capability-layer.html',
    'topics/ai-studio/3-agent-infra/implementation-layer.html',
    'topics/ai-studio/3-agent-infra/infrastructure-layer.html',
    'topics/ai-studio/3-agent-infra/orchestration-layer.html',
    'topics/ai-studio/3-agent-infra/product-layer.html',
]

# Group 3: 字节跳动指南 - 保留品牌导航
BYTEDANCE_REPORTS = [
    'companies/bytedance-ai-guide/home.html',
    'companies/bytedance-ai-guide/pages/ai-history.html',
    'companies/bytedance-ai-guide/pages/bytedance-ai.html',
    'companies/bytedance-ai-guide/pages/agent-infra.html',
    'companies/bytedance-ai-guide/pages/security-practice.html',
    'companies/bytedance-ai-guide/pages/finance-insights.html',
]

def main():
    updated = 0
    failed = 0
    skipped = 0
    
    print("=" * 60)
    print("深度调研报告底部统一修改工具")
    print("=" * 60)
    
    # Group 1
    print("\n📄 Group 1: 标准独立报告")
    for rel in STANDARD_REPORTS:
        fp = os.path.join(DR, rel)
        if not os.path.exists(fp):
            print(f"  ❌ 文件不存在: {rel}")
            skipped += 1
            continue
        try:
            if process_standard_report(fp):
                print(f"  ✅ {rel}")
                updated += 1
            else:
                print(f"  ⏭️  无变化: {rel}")
                skipped += 1
        except Exception as e:
            print(f"  ❌ 失败: {rel} - {e}")
            failed += 1
    
    # Group 2
    print("\n📑 Group 2: 多章节报告")
    for rel in MULTICHAPTER_REPORTS:
        fp = os.path.join(DR, rel)
        if not os.path.exists(fp):
            print(f"  ❌ 文件不存在: {rel}")
            skipped += 1
            continue
        try:
            if process_multichapter_report(fp):
                print(f"  ✅ {rel}")
                updated += 1
            else:
                print(f"  ⏭️  无变化: {rel}")
                skipped += 1
        except Exception as e:
            print(f"  ❌ 失败: {rel} - {e}")
            failed += 1
    
    # Group 3
    print("\n🏢 Group 3: 字节跳动指南")
    for rel in BYTEDANCE_REPORTS:
        fp = os.path.join(DR, rel)
        if not os.path.exists(fp):
            print(f"  ❌ 文件不存在: {rel}")
            skipped += 1
            continue
        try:
            if process_bytedance_report(fp):
                print(f"  ✅ {rel}")
                updated += 1
            else:
                print(f"  ⏭️  无变化: {rel}")
                skipped += 1
        except Exception as e:
            print(f"  ❌ 失败: {rel} - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 已更新: {updated}  ⏭️ 跳过: {skipped}  ❌ 失败: {failed}")
    print(f"📊 总计处理: {updated + skipped + failed} 个文件")
    print("=" * 60)

if __name__ == '__main__':
    main()
