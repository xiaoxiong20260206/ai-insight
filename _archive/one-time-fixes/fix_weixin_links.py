#!/usr/bin/env python3
"""
批量修复AI日报中失效的微信公众号链接
方案：将失效的 mp.weixin.qq.com 链接替换为搜狗微信搜索链接
搜索链接格式: https://weixin.sogou.com/weixin?type=2&query=TITLE
读者点击后可在搜狗微信搜索中找到相关文章
"""

import os
import re
import sys
from urllib.parse import quote

# 配置
DAILY_DIR = "01-daily-reports/2026-03"
DRY_RUN = "--dry-run" in sys.argv

# 匹配 Markdown 链接中包含微信域名的模式
# 模式A: [标题](https://mp.weixin.qq.com/) - 裸域名占位符
# 模式B: [标题](https://mp.weixin.qq.com/s?src=11&timestamp=...&signature=...&new=1) - 已过期的搜狗代理URL
WEIXIN_LINK_PATTERN = re.compile(
    r'\[([^\]]+)\]\((https://mp\.weixin\.qq\.com[^)]*)\)'
)

def generate_sogou_search_url(title):
    """从文章标题生成搜狗微信搜索URL"""
    # 清理标题中的特殊字符（保留中文和英文）
    clean_title = title.strip()
    # 去掉标题中可能的markdown加粗标记
    clean_title = clean_title.replace("**", "")
    # 提取标题的核心关键词（取冒号前后最关键的部分）
    # 如果标题太长（超过30字），截取到冒号前的部分作为搜索词
    if len(clean_title) > 40 and "：" in clean_title:
        clean_title = clean_title.split("：")[0]
    elif len(clean_title) > 40 and ":" in clean_title:
        clean_title = clean_title.split(":")[0]
    
    encoded = quote(clean_title)
    return f"https://weixin.sogou.com/weixin?type=2&query={encoded}"

def is_broken_weixin_link(url):
    """判断是否是失效的微信链接"""
    # 模式A: 裸域名
    if url in ("https://mp.weixin.qq.com/", "https://mp.weixin.qq.com"):
        return True
    # 模式B: 搜狗代理临时链接（含 src=11 和 timestamp）
    if "mp.weixin.qq.com/s?" in url and ("timestamp=" in url or "signature=" in url):
        return True
    # 模式C: 带src=11的搜狗代理链接
    if "mp.weixin.qq.com/s?" in url and "src=11" in url:
        return True
    return False

def fix_file(filepath):
    """修复单个文件中的微信链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    replacements = []
    
    def replace_link(match):
        title = match.group(1)
        url = match.group(2)
        
        if is_broken_weixin_link(url):
            new_url = generate_sogou_search_url(title)
            replacements.append({
                'title': title,
                'old_url': url[:80] + ('...' if len(url) > 80 else ''),
                'new_url': new_url
            })
            return f'[{title}]({new_url})'
        return match.group(0)
    
    new_content = WEIXIN_LINK_PATTERN.sub(replace_link, content)
    
    if replacements:
        filename = os.path.basename(filepath)
        print(f"\n{'='*60}")
        print(f"文件: {filename} ({len(replacements)} 处替换)")
        print(f"{'='*60}")
        for i, r in enumerate(replacements, 1):
            print(f"  {i}. {r['title'][:50]}...")
            print(f"     旧: {r['old_url']}")
            print(f"     新: {r['new_url'][:80]}...")
        
        if not DRY_RUN:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  >>> 已保存")
        else:
            print(f"  >>> [DRY RUN] 未保存")
    
    return len(replacements)

def main():
    if DRY_RUN:
        print("=" * 60)
        print("DRY RUN 模式 - 不会修改文件")
        print("=" * 60)
    
    total = 0
    files_fixed = 0
    
    for filename in sorted(os.listdir(DAILY_DIR)):
        if filename.endswith('.md'):
            filepath = os.path.join(DAILY_DIR, filename)
            count = fix_file(filepath)
            if count > 0:
                total += count
                files_fixed += 1
    
    print(f"\n{'='*60}")
    print(f"总结: {files_fixed} 个文件, {total} 处链接已{'替换' if not DRY_RUN else '发现(未修改)'}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
