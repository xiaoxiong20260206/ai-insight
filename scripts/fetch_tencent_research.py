#!/usr/bin/env python3
"""
Fetch Tencent Research Institute AI Daily Digest (腾讯研究院AI速递) from Sohu mirror.

This script serves as a supplementary data source for the AI Insight daily report.
It uses the IMA API to check for the latest entries, then fetches full content from
the Sohu mirror of the WeChat public account articles.

Usage:
    uv run scripts/fetch_tencent_research.py --date YYYY-MM-DD
    uv run scripts/fetch_tencent_research.py --date YYYY-MM-DD --raw  # output raw text
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# IMA API credentials
CONFIG_DIR = Path.home() / ".config" / "ima"
CLIENT_ID = os.environ.get("IMA_OPENAPI_CLIENTID", "")
API_KEY = os.environ.get("IMA_OPENAPI_APIKEY", "")

if not CLIENT_ID and CONFIG_DIR.exists():
    cid_file = CONFIG_DIR / "client_id"
    ak_file = CONFIG_DIR / "api_key"
    if cid_file.exists():
        CLIENT_ID = cid_file.read_text().strip()
    if ak_file.exists():
        API_KEY = ak_file.read_text().strip()

# IMA Knowledge Base ID for "AGI数据库.腾讯研究院"
IMA_KB_ID = "oalGkoohPXOk8tv7vD1O0c-ughzb3qF2Nz1TYCWEv-Q="

# IMA API script path
SKILL_DIR = Path(__file__).parent.parent.parent.parent / "user-skills" / "ima-skill"
IMA_API_CJS = SKILL_DIR / "ima_api.cjs"

# Tavily search script
TAVILY_SCRIPT = Path(__file__).parent.parent.parent.parent / "skills" / "tavily-search" / "scripts" / "tavily_search.py"


def call_ima_api(endpoint: str, body: dict) -> dict:
    """Call IMA OpenAPI via ima_api.cjs"""
    if not CLIENT_ID or not API_KEY:
        return {"error": "IMA credentials not configured"}
    
    opts = json.dumps({"clientId": CLIENT_ID, "apiKey": API_KEY})
    body_str = json.dumps(body, ensure_ascii=False)
    
    result = subprocess.run(
        ["node", str(IMA_API_CJS), endpoint, body_str, opts],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode != 0:
        return {"error": f"IMA API call failed: {result.stderr[:200]}"}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"IMA API returned non-JSON: {result.stdout[:200]}"}


def check_latest_entry(target_date: str) -> dict:
    """Check if a Tencent Research AI digest exists for the target date via IMA API."""
    date_str = target_date.replace("-", "")  # 2026-06-29 → 20260629
    title = f"腾讯研究院AI速递 {date_str}"
    
    resp = call_ima_api("openapi/wiki/v1/search_knowledge", {
        "query": title,
        "knowledge_base_id": IMA_KB_ID,
        "cursor": ""
    })
    
    if "error" in resp:
        return {"exists": False, "error": resp["error"]}
    
    items = resp.get("data", {}).get("info_list", [])
    for item in items:
        if date_str in item.get("title", ""):
            return {"exists": True, "title": item["title"], "media_id": item["media_id"]}
    
    return {"exists": False, "note": f"No entry found for {title}"}


def fetch_from_sohu(target_date: str) -> dict:
    """Fetch article content from Sohu mirror via Tavily search."""
    date_str = target_date.replace("-", "")
    query = f"腾讯研究院AI速递 {date_str} site:sohu.com"
    
    # Search via Tavily
    result = subprocess.run(
        ["uv", "run", "--refresh-package", "ks_aimate", str(TAVILY_SCRIPT),
         "--query", query, "--max-results", "3", "--format", "brave"],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode != 0:
        return {"error": f"Tavily search failed: {result.stderr[:200]}"}
    
    try:
        search_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"Tavily returned non-JSON: {result.stdout[:200]}"}
    
    # Find sohu.com article URL
    sohu_url = None
    for r in search_data.get("results", []):
        url = r.get("url", "")
        if "sohu.com/a/" in url:
            sohu_url = url
            break
    
    if not sohu_url:
        # Try broader search without site filter
        query2 = f"腾讯研究院AI速递 {date_str}"
        result2 = subprocess.run(
            ["uv", "run", "--refresh-package", "ks_aimate", str(TAVILY_SCRIPT),
             "--query", query2, "--max-results", "5", "--format", "brave"],
            capture_output=True, text=True, timeout=30
        )
        try:
            search_data2 = json.loads(result2.stdout)
            for r in search_data2.get("results", []):
                url = r.get("url", "")
                if "sohu.com/a/" in url:
                    sohu_url = url
                    break
        except json.JSONDecodeError:
            pass
    
    if not sohu_url:
        return {"error": "No Sohu mirror URL found", "date": target_date}
    
    # Fetch content from Sohu
    # Convert mobile URL to desktop if needed
    sohu_url = re.sub(r'^https?://m\.sohu\.com/', 'https://www.sohu.com/', sohu_url)
    # Remove query params
    sohu_url = sohu_url.split("?")[0]
    
    result = subprocess.run(
        ["curl", "-sL", sohu_url,
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"],
        capture_output=True, text=True, timeout=20
    )
    
    if result.returncode != 0:
        return {"error": f"Failed to fetch Sohu article: {result.stderr[:200]}"}
    
    html = result.stdout
    # Extract text content
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Find the article body
    idx = text.find('AI速递')
    if idx < 0:
        return {"error": "Article content not found in page", "url": sohu_url}
    
    article_text = text[idx:idx+8000]
    
    # Truncate at footer markers before parsing
    for marker in ['👇加入AGI数据库', '返回搜狐', '平台声明', 'window.deployEnv', '阅读 ( )']:
        if marker in article_text:
            article_text = article_text[:article_text.index(marker)]
    
    # Parse into structured news items
    return parse_article(article_text, target_date, sohu_url)


def parse_article(text: str, date: str, source_url: str) -> dict:
    """Parse the Tencent Research AI digest into structured news items."""
    # The format is: "一、Title 1. point1 2. point2 3. point3 二、Title ..."
    # Split by Chinese numerals (一二三四五六七八九十)
    sections = re.split(r'(?=[一二三四五六七八九十]、)', text)
    
    news_items = []
    for section in sections:
        # Match pattern like "一、OpenAI发布GPT-5.6"
        match = re.match(r'([一二三四五六七八九十]+)、(.+)', section, re.DOTALL)
        if match:
            title_part = match.group(2).strip()
            # Extract title (before the first numbered point)
            title = re.split(r'\s+1\.', title_part, maxsplit=1)[0].strip()
            if len(title) > 200:
                title = title[:120]
            
            # Extract numbered points from the section
            point_matches = re.findall(r'(?:^|\s)(\d+)\.\s*(.+?)(?=\s+\d+\.|$)', section)
            points = []
            for num, pt in point_matches:
                if pt.strip() and len(pt.strip()) > 10:
                    points.append(pt.strip())
            
            # Also try "报告观点" section marker
            if not points:
                # Extract text after title
                body = section[len(title)+5:]
                body_points = re.findall(r'\d+\.\s*(.+?)(?=\s+\d+\.|$)', body)
                points = [p.strip() for p in body_points if p.strip() and len(p.strip()) > 10]
            
            if title and len(title) > 5:
                news_items.append({
                    "title": title,
                    "points": points[:3],
                    "source": "tencent_research",
                    "source_url": source_url,
                    "date": date
                })
    
    return {
        "date": date,
        "source": "腾讯研究院AI速递",
        "source_url": source_url,
        "items_count": len(news_items),
        "items": news_items
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Tencent Research AI Daily Digest")
    parser.add_argument("--date", required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--raw", action="store_true", help="Output raw text instead of structured JSON")
    parser.add_argument("--skip-ima", action="store_true", help="Skip IMA existence check")
    args = parser.parse_args()
    
    target_date = args.date
    
    # Step 1: Check IMA for existence (optional but useful for validation)
    if not args.skip_ima:
        check = check_latest_entry(target_date)
        print(f"IMA check: {'✅ Found' if check.get('exists') else '⚠️ Not found'} - {check.get('title', check.get('note', check.get('error', '')))}", file=sys.stderr)
    
    # Step 2: Fetch from Sohu mirror
    result = fetch_from_sohu(target_date)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    if args.raw:
        # Output raw article text
        for item in result.get("items", []):
            print(f"{'='*60}")
            print(f"【{item['title']}】")
            for i, pt in enumerate(item.get("points", []), 1):
                print(f"  {i}. {pt}")
            print()
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
