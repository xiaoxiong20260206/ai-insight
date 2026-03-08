#!/usr/bin/env python3
"""
深度调研专题 KIM 推送脚本 v1.0
================================
将深度调研专题推送到 KIM（支持个人/群推送）

功能特性:
- 深度调研专题卡片：提炼核心洞察 + 6大趋势 + 4大原理
- 双按钮：查看完整报告 + 了解AI洞察项目
- 支持发送到个人或群
- 重试机制：遇到频率限制自动重试

使用方式:
  python scripts/send_deep_research_card.py --to-user shenlang    # 发给个人（预览）
  python scripts/send_deep_research_card.py --to-groups           # 发送到所有群
  python scripts/send_deep_research_card.py --dry-run             # 试运行，不实际发送

作者: 林克 (沈浪的AI分身)
版本: 1.0.0
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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

# 深度调研链接
RESEARCH_URL = "https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/trends/ai-leaders-2026.html"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

# 推送配置
SEND_INTERVAL = 2.5  # 群间发送间隔(秒)
MAX_RETRIES = 3
RETRY_DELAY = 5


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
    """获取林克机器人所在的所有群"""
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
            return [
                {
                    "groupId": g.get("groupId", ""),
                    "groupName": g.get("name", "未知群"),
                    "memberCount": g.get("userCount", 0)
                }
                for g in groups
            ]
        return []


async def send_to_user(token: str, username: str, card: dict, dry_run: bool = False) -> bool:
    """发送消息到个人"""
    if dry_run:
        print(f"   🔍 [DRY-RUN] 将发送到用户: {username}")
        return True
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/message/send",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "username": username,
                "msgType": "mixCard",
                "mixCard": card
            }
        )
        result = resp.json()
        if result.get("code") == 0:
            return True
        print(f"   ❌ 发送失败: {result}")
        return False


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


# ============ 卡片构建 ============
def build_deep_research_card() -> dict:
    """
    构建深度调研专题卡片
    
    内容结构：
    - 标题：📚 深度调研 · AI大神看2026年下半场
    - 核心洞察
    - 6大趋势精华（每个1句话）
    - 4大底层原理（简述）
    - 双按钮：查看报告 + 了解项目
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[datetime.now().weekday()]
    
    # 核心洞察
    core_insight = """🎯 **核心范式转变**
从"构建更强大的模型"转向"设计更好的任务、环境和反馈循环"——这是真正的"下半场"。"""
    
    # 6大趋势（精炼版）
    trends = """🔥 **六大趋势洞察**

1️⃣ **简单优先** — 复杂度是毒药，能画决策树就别用Agent
2️⃣ **Skills > 多Agent** — 单一通用Agent + 可扩展Skills库
3️⃣ **环境Agent崛起** — 从对话式触发转向事件驱动后台运行
4️⃣ **Vibe → Agentic Engineering** — 从松散原型转向生产级实践
5️⃣ **上下文为王** — Context管理成为核心竞争力
6️⃣ **TDD文艺复兴** — 测试不再只是质量保障，而是Agent的训练数据"""
    
    # 4大原理
    principles = """🔮 **四大底层原理**

• **复杂度守恒** — 复杂度只能转移，不能消除
• **泛化即压缩** — 语言是最高效的泛化工具
• **反馈环路必要** — 智能需要与环境的反馈循环
• **抽象层级** — 高层通用但难用，低层专用但可控"""
    
    # 来源说明
    sources = """📊 **信息覆盖**
9位AI领域顶级人物 × 11篇核心分享
姚顺雨 | Barry Zhang | Andrej Karpathy | Addy Osmani | Simon Willison | Harrison Chase | Jim Fan | Dario Amodei"""
    
    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": f"# 📚 深度调研 · AI大神看2026年下半场"}
            },
            {
                "blockId": "date",
                "type": "content",
                "text": {"type": "kimMd", "content": f"📅 *{today}（{weekday}）发布*"}
            },
            {"blockId": "div0", "type": "divider"},
            {
                "blockId": "insight",
                "type": "content",
                "text": {"type": "kimMd", "content": core_insight}
            },
            {"blockId": "div1", "type": "divider"},
            {
                "blockId": "trends",
                "type": "content",
                "text": {"type": "kimMd", "content": trends}
            },
            {"blockId": "div2", "type": "divider"},
            {
                "blockId": "principles",
                "type": "content",
                "text": {"type": "kimMd", "content": principles}
            },
            {"blockId": "div3", "type": "divider"},
            {
                "blockId": "sources",
                "type": "content",
                "text": {"type": "kimMd", "content": sources}
            },
            {"blockId": "div4", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {"type": "kimMd", "content": "*林克（沈浪的AI分身）· AI洞察 · 深度调研系列*"}
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "📄 查看完整报告 >>"},
                        "style": "green",
                        "url": RESEARCH_URL
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
    parser = argparse.ArgumentParser(description="深度调研专题 KIM 推送脚本 v1.0")
    parser.add_argument("--to-user", type=str, help="发送到指定用户（用户名）")
    parser.add_argument("--to-groups", action="store_true", help="发送到所有群")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()
    
    if not args.to_user and not args.to_groups:
        print("❌ 请指定发送目标: --to-user <username> 或 --to-groups")
        print("   示例: python scripts/send_deep_research_card.py --to-user shenlang")
        return
    
    print("🚀 深度调研专题推送 v1.0")
    print(f"   主题: AI大神看2026年下半场")
    print(f"{'🔍 [DRY-RUN 模式]' if args.dry_run else ''}")
    print("=" * 50)
    
    # 1. 构建卡片
    print("🎨 构建深度调研卡片...")
    card = build_deep_research_card()
    print("✅ 卡片构建完成")
    
    # 2. 获取 Token
    print("🔑 获取 Access Token...")
    try:
        token = await get_access_token()
        print("✅ Token 获取成功")
    except Exception as e:
        print(f"❌ Token 获取失败: {e}")
        return
    
    # 3. 发送
    if args.to_user:
        # 发送给个人
        print(f"\n📤 发送给用户: {args.to_user}")
        success = await send_to_user(token, args.to_user, card, args.dry_run)
        if success:
            print("✅ 发送成功！请检查 KIM 消息")
        else:
            print("❌ 发送失败")
    
    if args.to_groups:
        # 发送到所有群
        print("\n📋 获取群列表...")
        groups = await get_bot_groups(token)
        if not groups:
            print("⚠️ 未找到任何群")
            return
        print(f"✅ 林克所在群数量: {len(groups)}")
        
        print("\n📤 开始推送到所有群...")
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
            
            if i < len(groups) - 1 and not args.dry_run:
                await asyncio.sleep(SEND_INTERVAL)
        
        print("\n" + "=" * 50)
        print(f"📊 推送完成！成功: {success_count}，失败: {fail_count}")
    
    print(f"\n📄 查看报告: {RESEARCH_URL}")


if __name__ == "__main__":
    asyncio.run(main())
