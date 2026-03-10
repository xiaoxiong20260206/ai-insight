#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报 KIM 卡片 v3.5 - 2026-03-10
热度趋势+动态+深度聚焦，从JSON读取内容
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    raise SystemExit(1)

sys.path.insert(0, str(Path(__file__).parent))
from kim_client import KimConfig

KimConfig.validate()
APP_KEY = KimConfig.APP_KEY
SECRET_KEY = KimConfig.SECRET_KEY
GATEWAY_URL = KimConfig.GATEWAY_URL

# 日期配置
DATE_STR = "2026-03-10"
WEEKDAY = "周二"
REPORT_URL = f"https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/2026-03/{DATE_STR}.html"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

# JSON数据路径
DATA_PATH = Path(__file__).parent.parent / "data" / f"daily-content-{DATE_STR}.json"

LQ = "\u201c"
RQ = "\u201d"


def load_daily_data():
    """加载每日内容JSON"""
    if not DATA_PATH.exists():
        print(f"Data file not found: {DATA_PATH}")
        return None
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_card(data):
    """构建v3.5格式卡片"""
    
    coverage = data.get("coverage", {})
    overseas = coverage.get("overseas", 0)
    china = coverage.get("china", 0)
    
    # ===== 热度趋势 =====
    heat_data = data.get("heat_trend", {})
    heat_title = heat_data.get("title", "近7期日报交叉分析")
    topics = heat_data.get("topics", [])
    
    # 趋势图标映射
    trend_icons = {
        "up": "📈",
        "down": "📉",
        "stable": "➡️",
        "new": "🆕",
        "burst": "⚡"
    }
    
    # 排名图标
    rank_icons = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]
    
    heat_lines = [f"🔥 **热度趋势**（{heat_title}）", ""]
    for i, topic in enumerate(topics[:6]):
        rank = rank_icons[i] if i < len(rank_icons) else f"{i+1}️⃣"
        name = topic.get("name", "")
        days = topic.get("days", 0)
        # 计算涉及板块数（简化）
        sectors = 2  # 默认
        trend_class = topic.get("trend_class", "stable")
        trend_icon = trend_icons.get(trend_class, "➡️")
        signal = topic.get("signal", "")
        
        heat_lines.append(f"- {rank} **{name}** — {days}天 · {sectors}板块 {trend_icon}")
        heat_lines.append(f"  → {signal}")
    
    heat_trend = "\n".join(heat_lines)
    
    # ===== 各板块内容 =====
    tabs = data.get("tabs", [])
    section_names = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业AI转型"]
    section_icons = ["🧠", "⌨️", "📱", "🏭", "🔄"]
    
    sections = []
    for i, tab in enumerate(tabs):
        if i >= 5:
            break
        
        name = section_names[i]
        icon = section_icons[i]
        
        news_data = tab.get("news", {})
        overseas_news = news_data.get("overseas", [])
        china_news = news_data.get("china", [])
        focus = tab.get("focus", {})
        
        lines = [f"## {icon} {name}", "", "📰 **动态**"]
        
        # 标签图标映射
        tag_icons = {
            "hot": "🔥 热门",
            "new": "🆕 新发布",
            "trend": "📈 趋势",
            "report": "📊 报告",
            "china": "🇨🇳 国内"
        }
        
        # 海外新闻
        for news in overseas_news[:3]:
            tag = news.get("tag", "")
            tag_display = tag_icons.get(tag, "📌") if tag else "📌"
            title = news.get("title", "")
            url = news.get("url", "")
            if url:
                lines.append(f"- {tag_display} | [{title}]({url})")
            else:
                lines.append(f"- {tag_display} | {title}")
        
        # 国内新闻
        for news in china_news[:2]:
            title = news.get("title", "")
            url = news.get("url", "")
            if url:
                lines.append(f"- 🇨🇳 国内 | [{title}]({url})")
            else:
                lines.append(f"- 🇨🇳 国内 | {title}")
        
        # 深度聚焦
        focus_title = focus.get("title", "")
        focus_summary = focus.get("summary", "")
        if focus_title or focus_summary:
            lines.append("")
            lines.append(f"💡 **深度聚焦** — {focus_title}")
            # 截取摘要前80字符
            if len(focus_summary) > 80:
                focus_summary = focus_summary[:80] + "..."
            lines.append(f"→ {focus_summary}")
        
        sections.append("\n".join(lines))
    
    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": f"# 📡 AI 日报（{DATE_STR}，{WEEKDAY}）"},
            },
            {
                "blockId": "subtitle",
                "type": "content",
                "text": {"type": "kimMd", "content": f"🌍 海外{overseas}条 · 🇨🇳 国内{china}条 | 五大板块 · 每板块含动态/深度聚焦"},
            },
            {"blockId": "div0", "type": "divider"},
            {"blockId": "heat", "type": "content", "text": {"type": "kimMd", "content": heat_trend}},
            {"blockId": "div1", "type": "divider"},
            {"blockId": "sec1", "type": "content", "text": {"type": "kimMd", "content": sections[0] if len(sections) > 0 else ""}},
            {"blockId": "div2", "type": "divider"},
            {"blockId": "sec2", "type": "content", "text": {"type": "kimMd", "content": sections[1] if len(sections) > 1 else ""}},
            {"blockId": "div3", "type": "divider"},
            {"blockId": "sec3", "type": "content", "text": {"type": "kimMd", "content": sections[2] if len(sections) > 2 else ""}},
            {"blockId": "div4", "type": "divider"},
            {"blockId": "sec4", "type": "content", "text": {"type": "kimMd", "content": sections[3] if len(sections) > 3 else ""}},
            {"blockId": "div5", "type": "divider"},
            {"blockId": "sec5", "type": "content", "text": {"type": "kimMd", "content": sections[4] if len(sections) > 4 else ""}},
            {"blockId": "div6", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察*"},
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {"type": "button", "text": {"type": "plainText", "content": "📄 查看完整日报 >>"}, "style": "green", "url": REPORT_URL},
                    {"type": "button", "text": {"type": "plainText", "content": "🏠 AI洞察首页"}, "style": "blue", "url": PROJECT_URL},
                ],
                "layout": "two",
            },
        ],
    }


async def get_bot_groups(client, token):
    resp = await client.post(
        f"{GATEWAY_URL}/openapi/v2/group/bot/list",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json={"pageSize": 50},
    )
    result = resp.json()
    if result.get("code") == 0:
        return result.get("data", {}).get("groups", [])
    print(f"Get groups failed: {result}")
    return []


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"  # 默认预览模式
    
    # 加载数据
    data = load_daily_data()
    if not data:
        print("Failed to load data")
        return
    
    card = build_card(data)
    print(f"Card v3.5 ({DATE_STR}) built OK")
    
    # 获取token
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={"appKey": APP_KEY, "secretKey": SECRET_KEY, "grantType": "client_credentials"},
        )
        result = resp.json()
        if result.get("code") != 0:
            print(f"Token failed: {result}")
            return
        token = result["result"]["accessToken"]
        print("Token OK")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if mode == "preview":
            # 发送给shenlang预览
            resp = await client.post(
                f"{GATEWAY_URL}/openapi/v2/message/send",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                json={"username": "shenlang", "msgType": "mixCard", "mixCard": card},
            )
            result = resp.json()
            print(f"Preview result: {result}")
            if result.get("code") == 0:
                print("✅ SUCCESS - 已发送给你预览")
            else:
                print(f"❌ FAILED: {result}")
        elif mode == "groups":
            # 发送到所有群
            groups = await get_bot_groups(client, token)
            print(f"Found {len(groups)} groups")
            for g in groups:
                gid = str(g.get("groupId", ""))
                gname = g.get("groupName", "unknown")
                resp = await client.post(
                    f"{GATEWAY_URL}/openapi/v2/message/send",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                    json={"groupId": gid, "msgType": "mixCard", "mixCard": card},
                )
                result = resp.json()
                status = "OK" if result.get("code") == 0 else "FAIL"
                print(f"  [{status}] {gname} ({gid}): {result.get('message', '')}")
                await asyncio.sleep(2)
            print(f"Done - sent to {len(groups)} groups")


if __name__ == "__main__":
    asyncio.run(main())
