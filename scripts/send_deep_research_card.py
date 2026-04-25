#!/usr/bin/env python3
"""
深度调研专题 KIM 推送脚本 (通用版，持续迭代)
================================
将深度调研专题推送到 KIM（支持个人/群推送）

功能特性:
- 深度调研专题卡片：提炼核心洞察 + 6大趋势 + 4大原理
- 双按钮：查看完整报告 + 了解AI洞察项目
- 支持发送到个人或群
- 重试机制：遇到频率限制自动重试

使用方式:
  python scripts/send_deep_research_card.py --preview             # 发给自己预览
  python scripts/send_deep_research_card.py --to-user shenlang   # 发给指定用户
  python scripts/send_deep_research_card.py --to-groups          # 发送到所有群
  python scripts/send_deep_research_card.py --dry-run            # 试运行

作者: 林克 (沈浪的AI分身)
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 使用公共模块加载凭证
sys.path.insert(0, str(Path(__file__).parent))
from kim_client import (
    KimConfig, get_access_token,
    send_to_user, send_to_all_groups
)

KimConfig.validate()

# ============ 配置 ============
APP_KEY = KimConfig.APP_KEY

# 深度调研链接（⚠️ 必须使用外部公开版 ai-insight-public，否则群成员访问404）
RESEARCH_URL = "https://xiaoxiong20260206.github.io/ai-insight-public/02-deep-research/trends/ai-leaders-2026.html"
from config import EXTERNAL_HOMEPAGE as PROJECT_URL

# 推送配置（统一从 KimConfig 读取）
SEND_INTERVAL = KimConfig.SEND_INTERVAL
MAX_RETRIES = KimConfig.MAX_RETRIES
RETRY_DELAY = KimConfig.RETRY_DELAY


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
    parser = argparse.ArgumentParser(description="深度调研专题 KIM 推送脚本")
    parser.add_argument("--preview", action="store_true", help="发给自己预览")
    parser.add_argument("--to-user", type=str, help="发送到指定用户（用户名）")
    parser.add_argument("--to-groups", action="store_true", help="发送到所有群")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()
    
    # --preview 等价于 --to-user shenlang
    if args.preview:
        args.to_user = "shenlang"
    
    if not args.to_user and not args.to_groups:
        print("❗ 请指定发送目标: --preview 或 --to-user <username> 或 --to-groups")
        print("   示例: python scripts/send_deep_research_card.py --preview")
        return
    
    print("🚀 深度调研专题推送")
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
        # 发送到所有群（使用 kim_client.send_to_all_groups）
        success_count, fail_count = await send_to_all_groups(token, card, args.dry_run)
        print("\n" + "=" * 50)
        print(f"📊 推送完成！成功: {success_count}，失败: {fail_count}")
    
    print(f"\n📄 查看报告: {RESEARCH_URL}")


if __name__ == "__main__":
    asyncio.run(main())
