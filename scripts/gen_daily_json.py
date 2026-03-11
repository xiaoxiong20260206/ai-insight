#!/usr/bin/env python3
"""
AI日报JSON数据生成器
====================
根据模板快速生成日报JSON数据文件

使用方式:
  # 1. 生成空白模板
  python scripts/gen_daily_json.py 2026-03-12 --template
  
  # 2. 从现有日报JSON复制并更新日期
  python scripts/gen_daily_json.py 2026-03-12 --from 2026-03-11
  
  # 3. 验证JSON格式正确性
  python scripts/gen_daily_json.py 2026-03-12 --validate

作者: 林克 (沈浪的AI分身)
版本: v1.0.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data"

# JSON模板结构
TEMPLATE = {
    "coverage": {"overseas": 0, "china": 0},
    "overview": [
        {"icon": "🧠", "label": "大模型", "headline": "", "text": ""},
        {"icon": "⌨️", "label": "AI Coding", "headline": "", "text": ""},
        {"icon": "📱", "label": "AI 应用", "headline": "", "text": ""},
        {"icon": "🏭", "label": "AI 行业", "headline": "", "text": ""},
        {"icon": "🔄", "label": "企业转型", "label_class": "orange", "headline": "", "text": ""}
    ],
    "heat_trend": {
        "title": "近7期日报交叉分析",
        "topics": [],
        "summary": ""
    },
    "tabs": [
        {
            "news": {
                "overseas": [
                    {"tag": "hot", "title": "", "url": "", "source": ""}
                ],
                "china": [
                    {"tag": "new", "title": "", "url": "", "source": ""}
                ]
            },
            "focus": {"title": "", "summary": ""}
        },
        {
            "news": {
                "overseas": [
                    {"tag": "hot", "title": "", "url": "", "source": ""}
                ],
                "china": [
                    {"tag": "new", "title": "", "url": "", "source": ""}
                ]
            },
            "focus": {"title": "", "summary": ""}
        },
        {
            "news": {
                "overseas": [
                    {"tag": "hot", "title": "", "url": "", "source": ""}
                ],
                "china": [
                    {"tag": "new", "title": "", "url": "", "source": ""}
                ]
            },
            "focus": {"title": "", "summary": ""}
        },
        {
            "news": {
                "overseas": [
                    {"tag": "hot", "title": "", "url": "", "source": ""}
                ],
                "china": [
                    {"tag": "new", "title": "", "url": "", "source": ""}
                ]
            },
            "focus": {"title": "", "summary": ""}
        },
        {
            "news": {
                "overseas": [],
                "china": [
                    {"tag": "new", "title": "", "url": "", "source": ""}
                ]
            },
            "focus": {"title": "", "summary": ""}
        }
    ]
}


def validate_json(date_str: str) -> bool:
    """验证JSON文件格式正确性"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        return False
    
    try:
        content = json_path.read_text(encoding="utf-8")
        
        # 尝试解析JSON（中文引号在内容中是允许的，只要JSON语法正确）
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return False
        
        # 检查必要字段
        if "tabs" not in data:
            print("❌ 缺少 tabs 字段")
            return False
        
        # 检查URL有效性
        invalid_urls = []
        for i, tab in enumerate(data.get("tabs", [])):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    url = item.get('url', '')
                    if url == '#' or (url and not url.startswith('http')):
                        invalid_urls.append(f"板块{i+1}: {item.get('title', '')[:20]} → {url}")
        
        if invalid_urls:
            print(f"❌ 发现{len(invalid_urls)}个无效链接:")
            for u in invalid_urls[:5]:
                print(f"   {u}")
            return False
        
        # 统计
        total_news = sum(
            len(tab.get("news", {}).get("overseas", [])) + 
            len(tab.get("news", {}).get("china", []))
            for tab in data.get("tabs", [])
        )
        heat_topics = len(data.get("heat_trend", {}).get("topics", []))
        
        print(f"✅ JSON格式正确")
        print(f"   📊 {len(data.get('tabs', []))}个板块, {total_news}条新闻, {heat_topics}个热度话题")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def generate_template(date_str: str) -> bool:
    """生成空白模板"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    
    if json_path.exists():
        print(f"⚠️ 文件已存在: {json_path}")
        response = input("是否覆盖? (y/N): ").strip().lower()
        if response != 'y':
            print("已取消")
            return False
    
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成模板: {json_path}")
    print("💡 请编辑填充内容后运行: python scripts/gen_daily_json.py --validate")
    return True


def copy_from(date_str: str, from_date: str) -> bool:
    """从现有JSON复制并更新"""
    source_path = DATA_PATH / f"daily-content-{from_date}.json"
    target_path = DATA_PATH / f"daily-content-{date_str}.json"
    
    if not source_path.exists():
        print(f"❌ 源文件不存在: {source_path}")
        return False
    
    if target_path.exists():
        print(f"⚠️ 目标文件已存在: {target_path}")
        response = input("是否覆盖? (y/N): ").strip().lower()
        if response != 'y':
            print("已取消")
            return False
    
    try:
        data = json.loads(source_path.read_text(encoding="utf-8"))
        
        # 更新热度趋势标题中的日期
        if "heat_trend" in data:
            old_title = data["heat_trend"].get("title", "")
            # 简单替换日期范围
            data["heat_trend"]["title"] = f"近7期日报交叉分析"
        
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已复制: {source_path} → {target_path}")
        print("💡 请更新内容后运行: python scripts/gen_daily_json.py --validate")
        return True
        
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="AI日报JSON数据生成器")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--template", "-t", action="store_true", help="生成空白模板")
    parser.add_argument("--from", dest="from_date", help="从指定日期的JSON复制")
    parser.add_argument("--validate", "-v", action="store_true", help="验证JSON格式")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📅 日期: {date_str}")
    
    if args.validate:
        success = validate_json(date_str)
        return 0 if success else 1
    elif args.from_date:
        success = copy_from(date_str, args.from_date)
        return 0 if success else 1
    elif args.template:
        success = generate_template(date_str)
        return 0 if success else 1
    else:
        # 默认: 验证或生成模板
        json_path = DATA_PATH / f"daily-content-{date_str}.json"
        if json_path.exists():
            print("📋 文件已存在，执行验证...")
            success = validate_json(date_str)
        else:
            print("📋 文件不存在，生成模板...")
            success = generate_template(date_str)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
