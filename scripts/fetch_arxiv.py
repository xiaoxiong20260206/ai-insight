#!/usr/bin/env python3
"""
ArXiv 学术论文监控工具

从 arXiv 获取 AI 相关论文，支持:
- 主题过滤 (cs.AI, cs.LG, cs.CL, cs.CV)
- 关键词过滤
- 每日/每周摘要
- 与 AI-Insight 日报系统集成

用法:
    python3 fetch_arxiv.py --days 1  # 获取过去1天的论文
    python3 fetch_arxiv.py --days 7 --summary  # 获取过去7天论文摘要
    python3 fetch_arxiv.py --keywords "agent" "LLM" "coding"  # 按关键词过滤
"""

import argparse
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re
import sys

# arXiv API 配置
ARXIV_API_BASE = "http://export.arxiv.org/api/query"

# AI 相关分类
AI_CATEGORIES = [
    "cs.AI",   # Artificial Intelligence
    "cs.LG",   # Machine Learning
    "cs.CL",   # Computation and Language (NLP)
    "cs.CV",   # Computer Vision
    "cs.NE",   # Neural and Evolutionary Computing
    "cs.IR",   # Information Retrieval
    "cs.RO",   # Robotics (for embodied AI)
    "stat.ML", # Machine Learning (Statistics)
]

# 关键词权重（用于排序）
KEYWORD_WEIGHTS = {
    # 高价值主题
    "agent": 3,
    "agents": 3,
    "reasoning": 3,
    "chain-of-thought": 3,
    "cot": 3,
    "coding": 3,
    "code generation": 3,
    "tool use": 3,
    "function calling": 3,
    
    # LLM 核心
    "large language model": 2,
    "llm": 2,
    "gpt": 2,
    "claude": 2,
    "gemini": 2,
    "transformer": 2,
    
    # 应用方向
    "retrieval": 2,
    "rag": 2,
    "fine-tuning": 2,
    "alignment": 2,
    "rlhf": 2,
    "dpo": 2,
    
    # 基础技术
    "benchmark": 1,
    "evaluation": 1,
    "dataset": 1,
    "scaling": 1,
}

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "04-knowledge-base" / "arxiv"


def fetch_arxiv_papers(
    categories: List[str] = None,
    keywords: List[str] = None,
    days: int = 1,
    max_results: int = 100
) -> List[Dict]:
    """
    从 arXiv 获取论文
    
    Args:
        categories: arXiv 分类列表
        keywords: 关键词过滤
        days: 获取过去多少天的论文
        max_results: 最大返回数量
    
    Returns:
        论文列表
    """
    if categories is None:
        categories = AI_CATEGORIES
    
    # 构建查询
    cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    # 添加关键词（如果有）
    if keywords:
        kw_query = " OR ".join([f"all:{kw}" for kw in keywords])
        search_query = f"({cat_query}) AND ({kw_query})"
    else:
        search_query = cat_query
    
    # 日期过滤（arXiv API 不直接支持日期过滤，需要后处理）
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    
    url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ 获取 arXiv 数据失败: {e}")
        return []
    
    # 解析 XML
    papers = parse_arxiv_response(xml_data, days)
    
    return papers


def parse_arxiv_response(xml_data: str, days: int) -> List[Dict]:
    """解析 arXiv API 响应"""
    
    # arXiv XML 命名空间
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
    }
    
    root = ET.fromstring(xml_data)
    papers = []
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    for entry in root.findall('atom:entry', ns):
        # 解析日期
        published_str = entry.find('atom:published', ns).text
        published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        
        # 日期过滤
        if published_date.replace(tzinfo=None) < cutoff_date:
            continue
        
        # 解析基本信息
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        
        # 解析作者
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns).text
            authors.append(name)
        
        # 解析分类
        categories = []
        for cat in entry.findall('atom:category', ns):
            categories.append(cat.get('term'))
        
        # 解析链接
        links = {}
        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'pdf':
                links['pdf'] = link.get('href')
            elif link.get('type') == 'text/html':
                links['abstract'] = link.get('href')
        
        paper = {
            'id': arxiv_id,
            'title': title,
            'summary': summary[:500] + '...' if len(summary) > 500 else summary,
            'authors': authors[:5],  # 只保留前5个作者
            'author_count': len(authors),
            'categories': categories,
            'published': published_date.strftime('%Y-%m-%d'),
            'links': links,
            'relevance_score': calculate_relevance(title, summary),
        }
        
        papers.append(paper)
    
    # 按相关性排序
    papers.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return papers


def calculate_relevance(title: str, summary: str) -> int:
    """计算论文相关性分数"""
    text = (title + " " + summary).lower()
    score = 0
    
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in text:
            score += weight
    
    return score


def format_paper_markdown(paper: Dict) -> str:
    """格式化单篇论文为 Markdown"""
    authors_str = ", ".join(paper['authors'])
    if paper['author_count'] > 5:
        authors_str += f" 等 ({paper['author_count']} 人)"
    
    cats_str = ", ".join(paper['categories'][:3])
    
    md = f"""### [{paper['title']}]({paper['links'].get('abstract', '')})

- **arXiv ID**: {paper['id']}
- **作者**: {authors_str}
- **分类**: {cats_str}
- **发布日期**: {paper['published']}
- **相关度**: {'⭐' * min(paper['relevance_score'], 5)}

**摘要**: {paper['summary']}

[📄 PDF]({paper['links'].get('pdf', '')}) | [📝 Abstract]({paper['links'].get('abstract', '')})

---
"""
    return md


def generate_daily_digest(papers: List[Dict], date: str) -> str:
    """生成每日论文摘要"""
    
    if not papers:
        return f"# arXiv AI 论文摘要 ({date})\n\n暂无符合条件的新论文。"
    
    # 按分类分组
    by_category = {}
    for paper in papers:
        primary_cat = paper['categories'][0] if paper['categories'] else 'other'
        if primary_cat not in by_category:
            by_category[primary_cat] = []
        by_category[primary_cat].append(paper)
    
    # 生成 Markdown
    md = f"""# arXiv AI 论文摘要 ({date})

> 自动生成 | 共 {len(papers)} 篇新论文 | 按相关度排序

## 📊 统计

| 分类 | 数量 |
|------|------|
"""
    for cat, cat_papers in sorted(by_category.items(), key=lambda x: -len(x[1])):
        md += f"| {cat} | {len(cat_papers)} |\n"
    
    md += "\n---\n\n"
    
    # Top 论文
    md += "## 🔥 高相关度论文\n\n"
    top_papers = [p for p in papers if p['relevance_score'] >= 3][:10]
    if top_papers:
        for paper in top_papers:
            md += format_paper_markdown(paper)
    else:
        md += "_今日无高相关度论文_\n\n"
    
    # 分类论文
    md += "## 📚 按分类浏览\n\n"
    for cat, cat_papers in sorted(by_category.items()):
        md += f"### {cat}\n\n"
        for paper in cat_papers[:5]:  # 每个分类最多5篇
            md += f"- [{paper['title']}]({paper['links'].get('abstract', '')}) ({paper['published']})\n"
        if len(cat_papers) > 5:
            md += f"- _...还有 {len(cat_papers) - 5} 篇_\n"
        md += "\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description='arXiv AI 论文监控')
    parser.add_argument('--days', type=int, default=1, help='获取过去多少天的论文')
    parser.add_argument('--keywords', nargs='+', help='关键词过滤')
    parser.add_argument('--max', type=int, default=100, help='最大返回数量')
    parser.add_argument('--summary', action='store_true', help='生成摘要报告')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    print(f"📡 正在获取 arXiv 论文 (过去 {args.days} 天)...")
    
    papers = fetch_arxiv_papers(
        keywords=args.keywords,
        days=args.days,
        max_results=args.max
    )
    
    print(f"✅ 获取到 {len(papers)} 篇论文")
    
    if args.json:
        output = json.dumps(papers, ensure_ascii=False, indent=2)
    elif args.summary:
        date = datetime.now().strftime('%Y-%m-%d')
        output = generate_daily_digest(papers, date)
    else:
        # 简单列表输出
        output = ""
        for paper in papers[:20]:
            output += f"\n{'='*60}\n"
            output += f"📄 {paper['title']}\n"
            output += f"   ID: {paper['id']} | 日期: {paper['published']}\n"
            output += f"   作者: {', '.join(paper['authors'][:3])}\n"
            output += f"   分类: {', '.join(paper['categories'][:3])}\n"
            output += f"   相关度: {'⭐' * min(paper['relevance_score'], 5)}\n"
    
    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')
        print(f"📝 已保存到: {output_path}")
    else:
        print(output)
    
    # 为日报系统提供简洁输出
    if papers and not args.output:
        print("\n" + "="*60)
        print("📰 日报推荐 (Top 5):")
        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper['title'][:60]}...")
            print(f"   {paper['links'].get('abstract', '')}")


if __name__ == "__main__":
    main()
