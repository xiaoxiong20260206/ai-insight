#!/usr/bin/env python3
"""
AI日报 KIM 推送脚本 (通用版，持续迭代)
=====================================
将 AI 日报推送到指定的2个目标群（CodeFlicker项目群 + 研发效能中心全员群）

功能特性:
- 卡片格式持续迭代（热度趋势 + 五大板块 × 动态/深度聚焦）
- 每条动态带链接，点击可跳转原文
- 双按钮：查看完整日报 + 了解AI洞察项目
- 支持从JSON文件读取数据（优先）或从MD文件解析（兜底）
- P0安全规则：42900限流不自动重试（可能已投递，重试会导致重复消息）
- 间隔控制：群间2.5秒间隔
- 推送范围：仅发2个目标群（DAILY_TARGET_GROUPS），周报发所有群

使用方式:
  python scripts/send_ai_daily.py                    # 推送今天的日报到目标群
  python scripts/send_ai_daily.py 2026-03-10         # 推送指定日期的日报
  python scripts/send_ai_daily.py --preview          # 先发给自己预览
  python scripts/send_ai_daily.py --dry-run          # 试运行，不实际发送

作者: 林克 (沈浪的AI分身)
"""

import asyncio
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

try:
    import httpx
except ImportError:
    print("❌ 请先安装 httpx: pip install httpx")
    raise SystemExit(1)

# 使用公共模块加载凭证
sys.path.insert(0, str(Path(__file__).parent))
from kim_client import KimConfig

KimConfig.validate()

# ============ 配置 ============
APP_KEY = KimConfig.APP_KEY
SECRET_KEY = KimConfig.SECRET_KEY
GATEWAY_URL = KimConfig.GATEWAY_URL

# 日报路径 (相对于项目根目录)
PROJECT_ROOT = Path(__file__).parent.parent
DAILY_REPORTS_PATH = PROJECT_ROOT / "01-daily-reports"
DATA_PATH = PROJECT_ROOT / "data"
REPORT_BASE_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

# 推送配置
SEND_INTERVAL = 2.5  # 群间发送间隔(秒)，避免频率限制
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 5

# 日报推送目标群（仅推送到这2个群，周报才推所有群）
DAILY_TARGET_GROUPS = {
    "6501852196213070",  # 【项目】CodeFlicker（2026年）
    "3705455482343722",  # 研发效能中心全员群
}  # set 类型，O(1) 查找

# 常量
LQ = "\u201c"  # 中文左引号
RQ = "\u201d"  # 中文右引号
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# ============ API 调用 ============
async def get_access_token() -> str:
    """获取林克应用的 Access Token"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={
                "appKey": APP_KEY,
                "secretKey": SECRET_KEY,
                "grantType": "client_credentials"
            }
        )
        result = resp.json()
        if result.get("code") == 0:
            return result["result"]["accessToken"]
        raise Exception(f"Token获取失败: {result}")


async def get_bot_groups(token: str) -> list:
    """获取林克机器人所在的所有群（包含群名）"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/group/bot/list",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={"pageSize": 50}
        )
        result = resp.json()
        if result.get("code") == 0:
            groups = result.get("data", {}).get("groups", [])
            enriched_groups = []
            for group in groups:
                enriched_groups.append({
                    "groupId": group.get("groupId", ""),
                    "groupName": group.get("name", "未知群"),
                    "memberCount": group.get("userCount", 0)
                })
            return enriched_groups
        return []


async def send_to_target(
    token: str,
    card: dict,
    target_type: str,  # "group" | "user"
    target_id: str,
    target_name: str,
    dry_run: bool = False
) -> bool:
    """发送消息到目标（群或个人）。
    
    P0安全规则: 42900 频率限制**不自动重试**，因为42900不保证消息未投递，
    重试可能导致消息重复发送。仅对网络异常做有限重试。
    """
    if dry_run:
        print(f"   🔍 [DRY-RUN] 将发送到: {target_name} ({target_id})")
        return True
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {"msgType": "mixCard", "mixCard": card}
                if target_type == "group":
                    payload["groupId"] = target_id
                else:
                    payload["username"] = target_id
                
                resp = await client.post(
                    f"{GATEWAY_URL}/openapi/v2/message/send",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    },
                    json=payload
                )
                result = resp.json()
                
                if result.get("code") == 0:
                    return True
                
                if result.get("code") == 42900:
                    # P0: 42900 不保证消息未投递，禁止自动重试，避免重复发送
                    print(f"   ⚠️ 频率限制(42900)，已记录，不自动重试（可能已投递）: {target_name}")
                    return False
                else:
                    print(f"   ❌ 发送失败: {result}")
                    return False
                    
        except Exception as e:
            # 网络异常可安全重试（请求未到达服务器）
            if attempt < MAX_RETRIES - 1:
                print(f"   ⏳ 网络异常，{RETRY_DELAY}秒后重试: {e}")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"   ❌ 网络异常: {e}")
                return False
    
    return False


# ============ 预检（P0强制，v4.2新增） ============
def pre_check(date_str: str) -> tuple:
    """
    日报推送前强制预检 (3项检查)
    返回: (通过:bool, 错误信息:str, 数据:dict或None)
    
    检查项:
    1. JSON文件存在性+可解析
    2. 内容非空检查 (新闻条目>0)
    3. URL有效性 (禁止 # 占位符)
    
    注意：内容中的中文引号是允许的（如新闻标题中的引号），
    只要JSON语法正确（key/value用英文引号）即可。
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    
    # 1. JSON文件存在性 + 解析
    if not json_path.exists():
        return False, f"JSON文件不存在: {json_path}\n💡 请先运行: python3 scripts/gen_daily_json.py {date_str}", None
    
    try:
        content = json_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"JSON解析失败: {e}\n💡 请检查JSON格式", None
    except Exception as e:
        return False, f"读取JSON失败: {e}", None
    
    # 2. 内容非空检查
    tabs = data.get("tabs", [])
    total_news = sum(
        len(tab.get("news", {}).get("overseas", [])) + 
        len(tab.get("news", {}).get("china", []))
        for tab in tabs
    )
    if total_news == 0:
        return False, f"新闻条目为0，卡片将为空\n💡 请检查JSON数据内容", None
    
    # 3. URL有效性（禁止 # 占位符）
    invalid_urls = []
    for i, tab in enumerate(tabs):
        section_names = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业AI转型"]
        section_name = section_names[i] if i < len(section_names) else f"板块{i+1}"
        
        for region in ['overseas', 'china']:
            for item in tab.get('news', {}).get(region, []):
                url = item.get('url', '')
                title = item.get('title', '未知标题')
                
                # 空URL是允许的（路径B：封闭平台找不到公开链接时URL留空）
                if url == '#' or (url and not url.startswith('http')):
                    invalid_urls.append(f"  [{section_name}] {title[:30]} → {url}")
    
    if invalid_urls:
        return False, f"发现{len(invalid_urls)}个无效链接:\n" + "\n".join(invalid_urls[:5]) + ("\n  ..." if len(invalid_urls) > 5 else ""), None
    
    return True, "预检通过", data


# ============ 数据加载 ============
def load_json_data(date_str: str) -> Optional[Dict]:
    """从JSON文件加载日报数据（优先方式）"""
    json_file = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_file.exists():
        return None
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载JSON失败: {e}")
        return None


def parse_md_data(date_str: str) -> Optional[Dict]:
    """从MD文件解析日报数据（兜底方式）"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    md_file = DAILY_REPORTS_PATH / month_str / f"{date_str}.md"
    
    if not md_file.exists():
        return None
    
    content = md_file.read_text(encoding="utf-8")
    
    # 简化解析：提取板块标题和来源链接
    sections_config = [
        ("大模型", r"(?:## 一、大模型|## 板块一：大模型).*?(?=## (?:二、|板块二)|$)"),
        ("AI Coding", r"(?:## 二、AI Coding|## 板块二：AI Coding).*?(?=## (?:三、|板块三)|$)"),
        ("AI 应用", r"(?:## 三、AI 应用|## 板块三：AI).*?(?=## (?:四、|板块四)|$)"),
        ("AI 行业", r"(?:## 四、AI 行业|## 板块四：AI行业).*?(?=## (?:五、|板块五)|$)"),
        ("企业AI转型", r"(?:## 五、企业 AI 转型|## 板块五：企业AI转型).*?(?=## 📊|## 深度聚焦|$)"),
    ]
    
    tabs = []
    for name, pattern in sections_config:
        match = re.search(pattern, content, re.DOTALL)
        news_items = []
        
        if match:
            section_content = match.group(0)
            # 提取 ### 标题 + **来源**：[xxx](url) 格式
            sections = re.split(r'(?=^### )', section_content, flags=re.MULTILINE)
            for sec in sections:
                if not sec.strip().startswith('###'):
                    continue
                title_match = re.match(r'### ([^\n]+)', sec)
                if not title_match:
                    continue
                title = title_match.group(1).strip()
                source_match = re.search(r'\*\*来源\*\*：\[([^\]]+)\]\(([^)]+)\)', sec)
                if source_match:
                    url = source_match.group(2).strip()
                    news_items.append({"title": title, "url": url, "tag": ""})
        
        tabs.append({
            "news": {"overseas": news_items[:2], "china": news_items[2:4]},
            "focus": {"title": "", "summary": ""}
        })
    
    return {
        "coverage": {"overseas": 0, "china": 0},
        "heat_trend": {"title": "", "topics": []},
        "tabs": tabs
    }


# ============ 卡片构建 v3.5 ============
def build_card_v35(date_str: str, data: Dict) -> dict:
    """构建v3.5格式卡片（热度趋势+动态+深度聚焦）"""
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[date_obj.weekday()]
    month_str = date_obj.strftime("%Y-%m")
    report_url = f"{REPORT_BASE_URL}/{month_str}/{date_str}-v3.html"
    
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
    
    heat_lines = []
    if topics:
        heat_lines = [f"🔥 **热度趋势**（{heat_title}）", ""]
        for i, topic in enumerate(topics[:6]):
            rank = rank_icons[i] if i < len(rank_icons) else f"{i+1}️⃣"
            name = topic.get("name", "")
            days = topic.get("days", 0)
            sectors = topic.get("sectors", 2)
            trend_class = topic.get("trend_class", "stable")
            trend_icon = trend_icons.get(trend_class, "➡️")
            signal = topic.get("signal", "")
            
            heat_lines.append(f"- {rank} **{name}** — {days}天 · {sectors}板块 {trend_icon}")
            if signal:
                heat_lines.append(f"  → {signal}")
    
    heat_trend = "\n".join(heat_lines) if heat_lines else ""
    
    # ===== 各板块内容 =====
    tabs = data.get("tabs", [])
    section_names = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业AI转型"]
    section_icons = ["🧠", "⌨️", "📱", "🏭", "🔄"]
    
    # 标签图标映射
    tag_icons = {
        "hot": "🔥 热门",
        "new": "🆕 新发布",
        "trend": "📈 趋势",
        "report": "📊 报告",
        "china": "🇨🇳 国内"
    }
    
    sections = []
    for i, tab in enumerate(tabs):
        if i >= 5:
            break
        
        name = section_names[i]
        icon = section_icons[i]
        
        news_data = tab.get("news", {})
        overseas_news = news_data.get("overseas", [])
        china_news = news_data.get("china", [])
        focus = tab.get("deep_focus") or tab.get("focus", {})
        
        lines = [f"## {icon} {name}", "", "📰 **动态**"]
        
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
        
        # 深度聚焦（兼容 {summary} 和 {paragraphs[],takeaway} 两种格式）
        focus_title = focus.get("title", "")
        focus_summary = focus.get("summary", "")
        # 新格式: 从 paragraphs 拼接摘要
        if not focus_summary and focus.get("paragraphs"):
            focus_summary = " ".join(focus["paragraphs"])
        if focus_title or focus_summary:
            lines.append("")
            lines.append(f"💡 **深度聚焦** — {focus_title}")
            # 截取摘要前80字符
            if len(focus_summary) > 80:
                focus_summary = focus_summary[:80] + "..."
            if focus_summary:
                lines.append(f"→ {focus_summary}")
        
        sections.append("\n".join(lines))
    
    # 构建blocks
    blocks = [
        {
            "blockId": "header",
            "type": "content",
            "text": {"type": "kimMd", "content": f"# 📡 AI 日报（{date_str}，{weekday}）"},
        },
        {
            "blockId": "subtitle",
            "type": "content",
            "text": {"type": "kimMd", "content": f"🌍 海外{overseas}条 · 🇨🇳 国内{china}条 | 五大板块 · 每板块含动态/深度聚焦"},
        },
        {"blockId": "div0", "type": "divider"},
    ]
    
    # 热度趋势（如果有）
    if heat_trend:
        blocks.append({"blockId": "heat", "type": "content", "text": {"type": "kimMd", "content": heat_trend}})
        blocks.append({"blockId": "div_heat", "type": "divider"})
    
    # 各板块
    for i, section_content in enumerate(sections):
        blocks.append({"blockId": f"sec{i+1}", "type": "content", "text": {"type": "kimMd", "content": section_content}})
        blocks.append({"blockId": f"div{i+1}", "type": "divider"})
    
    # 林克能力更新（可选，从data中读取）
    capability_update = data.get("capability_update", "")
    if capability_update:
        blocks.append({
            "blockId": "capability",
            "type": "content",
            "text": {"type": "kimMd", "content": f"🤖 **林克能力更新**\n{capability_update}"},
        })
        blocks.append({"blockId": "div_cap", "type": "divider"})
    
    # 页脚和按钮
    blocks.append({
        "blockId": "footer",
        "type": "content",
        "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察*"},
    })
    blocks.append({
        "blockId": "buttons",
        "type": "action",
        "actions": [
            {"type": "button", "text": {"type": "plainText", "content": "📄 查看完整日报 >>"}, "style": "green", "url": report_url},
            {"type": "button", "text": {"type": "plainText", "content": "💡 了解AI洞察项目"}, "style": "blue", "url": PROJECT_URL},
        ],
        "layout": "two",
    })
    
    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": blocks,
    }


# ============ 主流程 ============
async def main():
    parser = argparse.ArgumentParser(description="AI日报 KIM 推送脚本")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--preview", action="store_true", help="先发给自己预览")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🚀 AI 日报推送 - {date_str}")
    if args.preview:
        print("📱 [预览模式] 发送给 shenlang")
    elif args.dry_run:
        print("🔍 [DRY-RUN 模式]")
    print("=" * 50)
    
    # 1. 预检（P0强制，3项检查）
    print("🔍 预检...")
    passed, msg, data = pre_check(date_str)
    
    if not passed:
        print(f"❌ 预检失败!")
        print(f"   {msg}")
        print(f"\n💡 请修复后重试: python3 scripts/send_ai_daily.py {date_str}")
        return
    
    # 统计
    tabs = data.get("tabs", [])
    total_news = sum(
        len(tab.get("news", {}).get("overseas", [])) + 
        len(tab.get("news", {}).get("china", []))
        for tab in tabs
    )
    heat_topics = len(data.get("heat_trend", {}).get("topics", []))
    print(f"✅ 预检通过!")
    print(f"   📊 {len(tabs)} 个板块, {total_news} 条新闻, {heat_topics} 个热度话题")
    
    # 2. 构建卡片
    print("🎨 构建卡片...")
    card = build_card_v35(date_str, data)
    print("✅ 卡片构建完成")
    
    # 3. 获取 Token
    print("🔑 获取 Access Token...")
    try:
        token = await get_access_token()
        print("✅ Token 获取成功")
    except Exception as e:
        print(f"❌ Token 获取失败: {e}")
        return
    
    # 4. 发送
    if args.preview:
        # 预览模式：发给自己
        print("\n📤 发送预览...")
        success = await send_to_target(
            token, card, "user", "shenlang", "shenlang (预览)", args.dry_run
        )
        if success:
            print("✅ 预览发送成功！请查看KIM消息")
        else:
            print("❌ 预览发送失败")
    else:
        # 群发模式（日报仅发指定2个群）
        print("📋 获取群列表...")
        all_groups = await get_bot_groups(token)
        if not all_groups:
            print("⚠️ 未找到任何群")
            return
        
        # 日报只发目标群
        groups = [g for g in all_groups if g["groupId"] in DAILY_TARGET_GROUPS]
        if not groups:
            print("⚠️ 未找到目标群（CodeFlicker + 研发效能中心）")
            return
        
        print(f"✅ 林克所在群数量: {len(all_groups)}，日报目标群: {len(groups)}")
        for g in groups:
            print(f"   → {g['groupName']} ({g['groupId']})")
        
        print("\n📤 开始推送...")
        success_count = 0
        fail_count = 0
        
        for i, group in enumerate(groups):
            group_id = group["groupId"]
            group_name = group["groupName"]
            
            print(f"[{i+1}/{len(groups)}] 发送到: {group_name}")
            
            success = await send_to_target(
                token, card, "group", group_id, group_name, args.dry_run
            )
            
            if success:
                print(f"   ✅ 发送成功")
                success_count += 1
            else:
                fail_count += 1
            
            # 群间间隔
            if i < len(groups) - 1 and not args.dry_run:
                await asyncio.sleep(SEND_INTERVAL)
        
        print("\n" + "=" * 50)
        print(f"📊 推送完成！成功: {success_count}，失败: {fail_count}")
    
    # 显示日报链接
    month_str = date_str[:7]
    print(f"📄 查看日报: {REPORT_BASE_URL}/{month_str}/{date_str}.html")


if __name__ == "__main__":
    asyncio.run(main())
