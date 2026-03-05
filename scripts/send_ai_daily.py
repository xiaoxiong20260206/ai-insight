#!/usr/bin/env python3
"""
AI日报 KIM 推送脚本
====================
将 AI 日报推送到林克所在的所有 KIM 群

使用方式:
  python scripts/send_ai_daily.py                    # 推送今天的日报
  python scripts/send_ai_daily.py 2026-03-05         # 推送指定日期的日报
  python scripts/send_ai_daily.py --dry-run          # 试运行，不实际发送

作者: 林克 (沈浪的AI分身)
版本: 1.1.0
更新: 2026-03-05 - 增加重试机制、群名获取、间隔控制
"""

import asyncio
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import httpx
except ImportError:
    print("❌ 请先安装 httpx: pip install httpx")
    exit(1)


# ============ 配置 ============
APP_KEY = "30b847d3-9fe4-4598-ac29-0b9a113eb991"
SECRET_KEY = "openApp298f3ef63db4ec3e7909ad4e9"
GATEWAY_URL = "https://INTERNAL_GATEWAY"

# 日报路径 (相对于项目根目录)
DAILY_REPORTS_PATH = Path(__file__).parent.parent / "01-daily-reports"
REPORT_BASE_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports"

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
            # 直接使用API返回的群信息（name字段包含群名）
            enriched_groups = []
            for group in groups:
                enriched_groups.append({
                    "groupId": group.get("groupId", ""),
                    "groupName": group.get("name", "未知群"),  # API返回的是name字段
                    "memberCount": group.get("userCount", 0)
                })
            return enriched_groups
        return []


async def get_group_info(token: str, group_id: str) -> dict:
    """获取单个群的详细信息（备用方法，目前未使用）"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{GATEWAY_URL}/openapi/v2/group/info",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                json={"groupId": group_id}
            )
            result = resp.json()
            if result.get("code") == 0:
                return result.get("data", {})
    except Exception:
        pass
    return {}


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
                
                # 频率限制错误，需要重试
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


# ============ 内容提取 ============
def read_daily_report(date_str: str) -> Optional[dict]:
    """从日报MD文件中提取内容"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    md_file = DAILY_REPORTS_PATH / month_str / f"{date_str}.md"
    
    if not md_file.exists():
        return None
    
    content = md_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    # 定义板块标记
    section_markers = {
        "## 一、大模型": "大模型",
        "## 二、AI Coding": "AI Coding",
        "## 三、AI 应用": "AI 应用",
        "## 四、AI 行业": "AI 行业",
        "## 五、企业 AI 转型": "企业AI转型",
    }
    
    result = {}
    current_section = None
    items = []
    
    for i, line in enumerate(lines):
        # 检查板块切换
        for marker, name in section_markers.items():
            if line.startswith(marker):
                if current_section and items:
                    result[current_section] = items[:3]  # 每板块最多3条
                current_section = name
                items = []
                break
        
        # 提取新闻标题
        if current_section and ("🔴" in line or "🟡" in line) and "**[" in line:
            match = re.search(r'\*\*\[([^\]]+)\]', line)
            if match:
                items.append(match.group(1).strip())
    
    # 保存最后一个板块
    if current_section and items:
        result[current_section] = items[:3]
    
    return result


def build_card(date_str: str, sections: dict) -> dict:
    """构建 MixCard 卡片"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[date_obj.weekday()]
    month_str = date_obj.strftime("%Y-%m")
    
    section_icons = {
        "大模型": "🧠",
        "AI Coding": "💻",
        "AI 应用": "📱",
        "AI 行业": "🏭",
        "企业AI转型": "🔄",
    }
    
    content_blocks = []
    for section in ["大模型", "AI Coding", "AI 应用", "AI 行业", "企业AI转型"]:
        items = sections.get(section, ["暂无更新"])
        icon = section_icons.get(section, "📌")
        item_lines = [f"{i}. {item}" for i, item in enumerate(items, 1)]
        block_content = f"{icon} **{section}**\n" + "\n".join(item_lines)
        content_blocks.append(block_content)
    
    overview_text = "\n\n".join(content_blocks)
    report_url = f"{REPORT_BASE_URL}/{month_str}/{date_str}.html"
    
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
                "text": {"type": "kimMd", "content": overview_text}
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
                    }
                ],
                "layout": "auto"
            }
        ]
    }


# ============ 主流程 ============
async def main():
    parser = argparse.ArgumentParser(description="AI日报 KIM 推送脚本")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🚀 AI 日报推送 - {date_str}")
    print(f"{'🔍 [DRY-RUN 模式]' if args.dry_run else ''}")
    print("=" * 50)
    
    # 1. 读取日报内容
    print("📖 读取日报内容...")
    sections = read_daily_report(date_str)
    if not sections:
        print(f"❌ 找不到日报文件: {date_str}")
        print(f"   请确认文件存在: {DAILY_REPORTS_PATH / date_str[:7] / f'{date_str}.md'}")
        return
    print(f"✅ 成功读取 {len(sections)} 个板块")
    
    # 2. 构建卡片
    print("🎨 构建消息卡片...")
    card = build_card(date_str, sections)
    print("✅ 卡片构建完成")
    
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
        
        # 群间间隔，避免频率限制
        if i < len(groups) - 1 and not args.dry_run:
            await asyncio.sleep(SEND_INTERVAL)
    
    # 6. 统计结果
    print("\n" + "=" * 50)
    print(f"📊 推送完成！成功: {success_count}，失败: {fail_count}")
    print(f"📄 查看日报: {REPORT_BASE_URL}/{date_str[:7]}/{date_str}.html")


if __name__ == "__main__":
    asyncio.run(main())
