#!/usr/bin/env python3
"""
Fix JSON format: convert new flat format back to old nested format for script compatibility.
Usage: uv run scripts/fix_json_format.py YYYY-MM-DD
"""
import json
import sys
from pathlib import Path

def fix_json(date_str):
    json_path = Path(f"data/daily-content-{date_str}.json")
    if not json_path.exists():
        print(f"❌ JSON not found: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if already in old format
    tabs = data.get("tabs", [])
    if not tabs:
        print("❌ No tabs found")
        return False
    
    first_tab = tabs[0]
    news = first_tab.get("news", {})
    if isinstance(news, dict) and ("overseas" in news or "china" in news):
        print("✅ Already in old format, no fix needed")
        return True
    
    # Convert new format to old format
    for tab in tabs:
        news_list = tab.get("news", [])
        if isinstance(news_list, list):
            # Classify by source
            overseas = []
            china = []
            for item in news_list:
                source = item.get("source", "")
                url = item.get("url", "")
                # Heuristic: if URL contains non-Chinese domain or source mentions foreign
                if any(kw in source.lower() for kw in ["techcrunch", "the information", "anthropic", "openai", "reuters", "politico", "business insider", "arXiv", "github"]):
                    overseas.append(item)
                elif any(kw in url for kw in [".com", ".io", ".org", ".net"]):
                    if any(cn in url for cn in [".cn", "sina", "163", "toutiao", "baidu", "csdn", "36kr", "smzdm"]):
                        china.append(item)
                    else:
                        overseas.append(item)
                else:
                    china.append(item)
            tab["news"] = {"overseas": overseas, "china": china}
    
    # Write back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fixed JSON format: {json_path}")
    print(f"   Converted {len(tabs)} tabs to old nested format")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/fix_json_format.py YYYY-MM-DD")
        sys.exit(1)
    date_str = sys.argv[1]
    success = fix_json(date_str)
    sys.exit(0 if success else 1)
