#!/usr/bin/env python3
"""
AI日报 KIM 推送脚本 v2.0 (升级版)
================================
将 AI 日报推送到林克所在的所有 KIM 群

功能特性:
- 升级版卡片格式：五大板块 × 三子类（动态/观点/洞察）
- 每条动态带链接，点击可跳转原文
- 双按钮：查看完整日报 + 了解AI洞察项目
- 重试机制：遇到频率限制自动重试
- 间隔控制：群间2.5秒间隔

使用方式:
  python scripts/send_ai_daily.py                    # 推送今天的日报
  python scripts/send_ai_daily.py 2026-03-05         # 推送指定日期的日报
  python scripts/send_ai_daily.py --dry-run          # 试运行，不实际发送

作者: 林克 (沈浪的AI分身)
版本: 2.0.0
更新: 2026-03-05 - 升级卡片格式，增加子类展示和链接
"""

import asyncio
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

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
DAILY_REPORTS_PATH = Path(__file__).parent.parent / "01-daily-reports"
REPORT_BASE_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

# 推送配置
SEND_INTERVAL = 2.5  # 群间发送间隔(秒)，避免频率限制
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 5      # 重试间隔(秒)


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


async def send_to_group_with_retry(
    token: str, 
    group_id: str, 
    group_name: str,
    card: dict,
    dry_run: bool = False
) -> bool:
    """发送消息到群，带重试机制"""
    if dry_run:
        print(f"   🔍 [DRY-RUN] 将发送到: {group_name} ({group_id})")
        return True
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{GATEWAY_URL}/openapi/v2/message/send",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    },
                    json={
                        "groupId": group_id,
                        "msgType": "mixCard",
                        "mixCard": card
                    }
                )
                result = resp.json()
                
                if result.get("code") == 0:
                    return True
                
                if result.get("code") == 42900:
                    if attempt < MAX_RETRIES - 1:
                        print(f"   ⏳ 频率限制，{RETRY_DELAY}秒后重试 ({attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    else:
                        print(f"   ❌ 重试{MAX_RETRIES}次仍失败: {result}")
                        return False
                else:
                    print(f"   ❌ 发送失败: {result}")
                    return False
                    
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"   ⏳ 发送异常，{RETRY_DELAY}秒后重试: {e}")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"   ❌ 发送异常: {e}")
                return False
    
    return False


# ============ 内容提取 (升级版) ============
def extract_section_data(content: str, section_name: str, section_pattern: str) -> Dict:
    """
    从日报MD中提取单个板块的完整数据
    
    返回:
    {
        "news": [(title, url, summary), ...],  # 最多3条新闻
        "opinion": {"person": str, "quote": str, "url": str},
        "insight": str
    }
    """
    match = re.search(section_pattern, content, re.DOTALL)
    if not match:
        return {"news": [], "opinion": None, "insight": None}
    
    section_content = match.group(0)
    
    news_items = []
    
    # 方式1: 提取新闻动态（标题+链接）
    # 格式: - 🔴 **[标题](链接)** - 来源
    news_pattern = r'[🔴🟡]\s*\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*-\s*([^\n]+)'
    news_matches = re.findall(news_pattern, section_content)
    for title, url, source in news_matches[:3]:
        news_items.append((title.strip(), url.strip()))
    
    # 方式2: 如果方式1没有匹配到，尝试提取 ### 标题 + **来源**：[xxx](url) 格式
    if not news_items:
        # 提取所有 ### 标题，然后找对应的来源链接
        # 格式: ### 标题 ... **来源**：[来源名](链接)
        sections = re.split(r'(?=^### )', section_content, flags=re.MULTILINE)
        for sec in sections:
            if not sec.strip().startswith('###'):
                continue
            # 提取标题
            title_match = re.match(r'### ([^\n]+)', sec)
            if not title_match:
                continue
            title = title_match.group(1).strip()
            # 提取来源链接
            source_match = re.search(r'\*\*来源\*\*：\[([^\]]+)\]\(([^)]+)\)', sec)
            if source_match:
                url = source_match.group(2).strip()
                news_items.append((title, url))
                if len(news_items) >= 3:
                    break
    
    # 2. 提取观点
    opinion = None
    opinion_section = re.search(r'### 2\. 热门观点.*?(?=### 3\.|$)', section_content, re.DOTALL)
    if opinion_section:
        opinion_text = opinion_section.group(0)
        # 提取人物
        person_match = re.search(r'>\s*\*\*([^*]+)\*\*', opinion_text)
        # 提取引用
        quote_match = re.search(r'>\s*"([^"]+)"', opinion_text)
        # 提取来源链接
        source_match = re.search(r'来源:\s*\[([^\]]+)\]\(([^)]+)\)', opinion_text)
        
        if quote_match:
            person = person_match.group(1).strip() if person_match else "业内人士"
            # 清理人物名称中的换行
            person = person.split('\n')[0].strip()
            quote = quote_match.group(1).strip()
            # 截取前50字符
            if len(quote) > 50:
                quote = quote[:50] + "..."
            source_url = source_match.group(2) if source_match else ""
            opinion = {"person": person, "quote": quote, "url": source_url}
    
    # 3. 提取洞察（第一句话）
    insight = None
    insight_section = re.search(r'### 3\. 趋势洞察\n+\*\*([^*]+)\*\*', section_content)
    if insight_section:
        insight = insight_section.group(1).strip()
        # 截取前60字符
        if len(insight) > 60:
            insight = insight[:60] + "..."
    
    return {"news": news_items, "opinion": opinion, "insight": insight}


def read_daily_report_v2(date_str: str) -> Optional[Dict]:
    """
    从日报MD文件中提取升级版内容
    
    返回各板块的完整数据，包含链接
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    md_file = DAILY_REPORTS_PATH / month_str / f"{date_str}.md"
    
    if not md_file.exists():
        return None
    
    content = md_file.read_text(encoding="utf-8")
    
    # 板块配置：(名称, 图标, 正则模式)
    # 支持两种格式：旧版 "## 一、大模型" 和 新版 "## 板块一：大模型动态"
    sections_config = [
        ("大模型", "🧠", r"(?:## 一、大模型|## 板块一：大模型).*?(?=## (?:二、|板块二)|$)"),
        ("AI Coding", "💻", r"(?:## 二、AI Coding|## 板块二：AI Coding).*?(?=## (?:三、|板块三)|$)"),
        ("AI 应用", "📱", r"(?:## 三、AI 应用|## 板块三：AI).*?(?=## (?:四、|板块四)|$)"),
        ("AI 行业", "🏭", r"(?:## 四、AI 行业|## 板块四：AI行业).*?(?=## (?:五、|板块五)|$)"),
        ("企业AI转型", "🔄", r"(?:## 五、企业 AI 转型|## 板块五：企业AI转型).*?(?=## 📊|## 深度聚焦|$)"),
    ]
    
    result = {}
    for name, icon, pattern in sections_config:
        data = extract_section_data(content, name, pattern)
        result[name] = {"icon": icon, "data": data}
    
    return result


def build_card_v2(date_str: str, sections: Dict) -> dict:
    """
    构建升级版 MixCard 卡片
    
    格式：
    - 每板块显示：动态(带链接) + 观点(带链接) + 洞察
    - 底部双按钮：查看日报 + 了解项目
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[date_obj.weekday()]
    month_str = date_obj.strftime("%Y-%m")
    report_url = f"{REPORT_BASE_URL}/{month_str}/{date_str}.html"
    
    # 构建内容
    section_blocks = []
    section_order = ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业AI转型"]
    
    for section_name in section_order:
        section_info = sections.get(section_name, {})
        icon = section_info.get("icon", "📌")
        data = section_info.get("data", {})
        
        lines = [f"{icon} **{section_name}**"]
        
        # 动态
        news = data.get("news", [])
        if news:
            lines.append("📰 *动态*")
            for title, url in news:
                # 为每条新闻生成简短摘要（从标题提取关键信息）
                lines.append(f"• [{title}]({url})")
        
        # 观点
        opinion = data.get("opinion")
        if opinion and opinion.get("quote"):
            if opinion.get("url"):
                lines.append(f"\n💬 *观点* — [{opinion['person']}]({opinion['url']}): \"{opinion['quote']}\"")
            else:
                lines.append(f"\n💬 *观点* — {opinion['person']}: \"{opinion['quote']}\"")
        
        # 洞察
        insight = data.get("insight")
        if insight:
            lines.append(f"\n💡 *洞察* — {insight}")
        
        section_blocks.append("\n".join(lines))
    
    # 用分割线连接各板块
    full_content = "\n\n---\n\n".join(section_blocks)
    
    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": f"# 📡 AI 日报（{date_str}，{weekday}）"}
            },
            {
                "blockId": "overview",
                "type": "content",
                "text": {"type": "kimMd", "content": full_content}
            },
            {"blockId": "div1", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察*"}
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "📄 查看完整日报 >>"},
                        "style": "green",
                        "url": report_url
                    },
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "了解AI洞察项目"},
                        "style": "blue",
                        "url": PROJECT_URL
                    }
                ],
                "layout": "two"
            }
        ]
    }


# ============ 主流程 ============
async def main():
    parser = argparse.ArgumentParser(description="AI日报 KIM 推送脚本 v2.0")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🚀 AI 日报推送 v2.0 - {date_str}")
    print(f"{'🔍 [DRY-RUN 模式]' if args.dry_run else ''}")
    print("=" * 50)
    
    # 1. 读取日报内容 (升级版)
    print("📖 读取日报内容...")
    sections = read_daily_report_v2(date_str)
    if not sections:
        print(f"❌ 找不到日报文件: {date_str}")
        print(f"   请确认文件存在: {DAILY_REPORTS_PATH / date_str[:7] / f'{date_str}.md'}")
        return
    
    # 统计提取结果
    total_news = sum(len(s["data"]["news"]) for s in sections.values())
    print(f"✅ 成功读取 {len(sections)} 个板块, {total_news} 条新闻")
    
    # 2. 构建卡片 (升级版)
    print("🎨 构建升级版消息卡片...")
    card = build_card_v2(date_str, sections)
    print("✅ 卡片构建完成（带链接 + 双按钮）")
    
    # 3. 获取 Token
    print("🔑 获取 Access Token...")
    try:
        token = await get_access_token()
        print("✅ Token 获取成功")
    except Exception as e:
        print(f"❌ Token 获取失败: {e}")
        return
    
    # 4. 获取群列表
    print("📋 获取群列表...")
    groups = await get_bot_groups(token)
    if not groups:
        print("⚠️ 未找到任何群")
        return
    print(f"✅ 林克所在群数量: {len(groups)}")
    for g in groups:
        print(f"   - {g['groupName']} ({g['groupId']})")
    
    # 5. 发送到所有群
    print("\n📤 开始推送...")
    success_count = 0
    fail_count = 0
    
    for i, group in enumerate(groups):
        group_id = group["groupId"]
        group_name = group["groupName"]
        
        print(f"[{i+1}/{len(groups)}] 发送到: {group_name}")
        
        success = await send_to_group_with_retry(
            token, group_id, group_name, card, args.dry_run
        )
        
        if success:
            print(f"   ✅ 发送成功")
            success_count += 1
        else:
            fail_count += 1
        
        # 群间间隔
        if i < len(groups) - 1 and not args.dry_run:
            await asyncio.sleep(SEND_INTERVAL)
    
    # 6. 统计结果
    print("\n" + "=" * 50)
    print(f"📊 推送完成！成功: {success_count}，失败: {fail_count}")
    print(f"📄 查看日报: {REPORT_BASE_URL}/{date_str[:7]}/{date_str}.html")


if __name__ == "__main__":
    asyncio.run(main())
