#!/usr/bin/env python3
"""
OpenClaw 深度洞察 KIM 推送脚本
================================
将 OpenClaw（小龙虾）深度调研专题推送到 KIM

使用方式:
  python3 scripts/send_openclaw_card.py --to-user shenlang    # 发给个人（预览）
  python3 scripts/send_openclaw_card.py --to-groups           # 发送到所有群
  python3 scripts/send_openclaw_card.py --dry-run             # 试运行

作者: 林克 (沈浪的AI分身)
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    raise SystemExit(1)

# 使用公共模块加载凭证
sys.path.insert(0, str(Path(__file__).parent))
from kim_client import KimConfig

KimConfig.validate()

# ============ 配置 ============
APP_KEY = KimConfig.APP_KEY
SECRET_KEY = KimConfig.SECRET_KEY
GATEWAY_URL = KimConfig.GATEWAY_URL

# OpenClaw 深度调研链接
RESEARCH_URL = "https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/topics/openclaw-deep-research-2026.html"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

# 推送配置
SEND_INTERVAL = 2.5
MAX_RETRIES = 3
RETRY_DELAY = 5

# Chinese quotes as variables to avoid encoding issues
LQ = '\u201c'  # left double quotation mark
RQ = '\u201d'  # right double quotation mark


# ============ API 调用 ============
async def get_access_token() -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={"appKey": APP_KEY, "secretKey": SECRET_KEY, "grantType": "client_credentials"}
        )
        result = resp.json()
        if result.get("code") == 0:
            return result["result"]["accessToken"]
        raise Exception(f"Token failed: {result}")


async def get_bot_groups(token: str) -> list:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/group/bot/list",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            json={"pageSize": 50}
        )
        result = resp.json()
        if result.get("code") == 0:
            groups = result.get("data", {}).get("groups", [])
            return [{"groupId": g.get("groupId", ""), "groupName": g.get("name", "unknown"), "memberCount": g.get("userCount", 0)} for g in groups]
        return []


async def send_to_user(token: str, username: str, card: dict, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"   [DRY-RUN] user: {username}")
        return True
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/message/send",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            json={"username": username, "msgType": "mixCard", "mixCard": card}
        )
        result = resp.json()
        if result.get("code") == 0:
            return True
        print(f"   FAIL: {result}")
        return False


async def send_to_group_with_retry(token: str, group_id: str, group_name: str, card: dict, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"   [DRY-RUN] group: {group_name} ({group_id})")
        return True
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{GATEWAY_URL}/openapi/v2/message/send",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                    json={"groupId": group_id, "msgType": "mixCard", "mixCard": card}
                )
                result = resp.json()
                if result.get("code") == 0:
                    return True
                if result.get("code") == 42900:
                    if attempt < MAX_RETRIES - 1:
                        print(f"   Rate limited, retry in {RETRY_DELAY}s ({attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                print(f"   FAIL: {result}")
                return False
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"   Error, retry in {RETRY_DELAY}s: {e}")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"   FAIL: {e}")
                return False
    return False


# ============ 卡片构建 ============
def build_openclaw_card() -> dict:
    """构建 OpenClaw 深度洞察卡片"""
    today = datetime.now().strftime("%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[datetime.now().weekday()]

    # 标题
    header_text = f'# \U0001f99e 深度洞察 \u00b7 OpenClaw\uff1a\u5f53AI\u957f\u51fa{LQ}\u624b\u811a{RQ}'

    # 副标题
    subtitle_text = f'\U0001f4c5 *{today}\uff08{weekday}\uff09\u00b7 \u5f00\u6e90\u4e3b\u6743\u667a\u80fd\u4f53\u7684\u5d1b\u8d77\u3001\u672c\u8d28\u4e0e\u672a\u6765*'

    # 核心洞察
    core_insight = (
        f'\U0001f3af **\u4e00\u53e5\u8bdd\u672c\u8d28**\n'
        f'OpenClaw\u6807\u5fd7\u7740AI\u4ece{LQ}**\u5de5\u5177**{RQ}\u53d8\u6210{LQ}**\u5458\u5de5**{RQ}'
        f'\u2014\u2014\u4eba\u4ece{LQ}\u64cd\u4f5c\u8005{RQ}\u53d8\u6210\u4e86{LQ}\u7ba1\u7406\u8005{RQ}\u3002'
        f'\u4ee5\u524d\u4f60\u7528AI\u67e5\u4e1c\u897f\u3001\u8981\u5efa\u8bae\uff0c\u4f46\u6d3b\u8fd8\u662f\u4f60\u81ea\u5df1\u5e72\u3002\u73b0\u5728AI\u76f4\u63a5\u5e2e\u4f60\u5e72\u6d3b\u4e86\u3002'
    )

    # 关键数据
    key_stats = (
        '\U0001f4ca **\u5173\u952e\u6570\u636e**\n\n'
        '\u2022 \u2b50 **239K+ Stars** \u2014 GitHub\u53f2\u4e0a\u6700\u5feb\uff0c6\u5468\u7834\u7eaa\u5f55\n'
        '\u2022 \U0001f4b0 **$300-750/\u6708** \u2014 \u91cd\u5ea6\u4f7f\u7528API\u8d39\u7528\uff0c\u6709\u4eba\u8bf4\u6bd4\u623f\u79df\u8d35\n'
        '\u2022 \U0001f916 **140\u4e07** Agent \u5728 Moltbook \u4e0a\u81ea\u4e3b\u793e\u4ea4\n'
        '\u2022 \U0001f3e2 \u521b\u59cb\u4eba\u88ab **OpenAI** \u96c7\u7528\uff0c\u8d1f\u8d23 bringing agents to everyone'
    )

    # AI进化四阶段
    evolution = (
        '\U0001f504 **AI\u8fdb\u5316\u56db\u9636\u6bb5**\n\n'
        f'1\ufe0f\u20e3 **\u5b57\u5178** \u2014 \u4f60\u95ee\u5b83\u7b54\uff08ChatGPT\u65f6\u4ee3\uff09\n'
        f'2\ufe0f\u20e3 **\u987e\u95ee** \u2014 AI\u7ed9\u5efa\u8bae\uff0c\u4f60\u505a\u51b3\u7b56\uff08Copilot\u65f6\u4ee3\uff09\n'
        f'3\ufe0f\u20e3 **\u5458\u5de5** \u2b05\ufe0f \u2014 AI\u81ea\u4e3b\u5e72\u6d3b\uff0c\u4f60\u6765\u7ba1\u7406\uff08**OpenClaw\u65f6\u4ee3**\uff09\n'
        f'4\ufe0f\u20e3 **\u56e2\u961f** \u2014 \u591aAgent\u534f\u4f5c\uff0c\u4eba\u53ea\u7ba1\u65b9\u5411'
    )

    # 核心类比
    analogy = (
        f'\U0001f99e **\u6838\u5fc3\u7c7b\u6bd4**\n'
        f'\u4ee5\u524d\u7684AI\u50cf**\u5ba0\u7269**\u2014\u2014\u4f60\u547d\u4ee4\u3001\u5b83\u6267\u884c\u3002'
        f'OpenClaw\u50cf\u4f60\u96c7\u7684**\u7b2c\u4e00\u4e2a\u5458\u5de5**\u2014\u2014\u81ea\u4e3b\u5de5\u4f5c\u3001\u80fd\u72af\u5927\u9519\u3001\u9700\u8981\u4fe1\u4efb\u3002'
        f'\u4f46\u5b83\u8df3\u8fc7\u4e86\u9762\u8bd5\u548c\u8bd5\u7528\u671f\uff0c'
        f'**\u7b2c\u4e00\u5929\u5c31\u62ff\u5230\u4e86\u6240\u6709\u7cfb\u7edf\u6743\u9650**\u3002'
    )

    # 终极判断
    verdict = (
        f'\U0001f52e **\u7ec8\u6781\u5224\u65ad**\n'
        f'\u771f\u6b63\u7684\u8d62\u5bb6\u4e0d\u662f\u9020\u6700\u5f3aAgent\u7684\u516c\u53f8\uff0c'
        f'\u800c\u662f\u4e3aAI\u5458\u5de5\u6784\u5efa\u6700\u597d{LQ}**HR\u7cfb\u7edf**{RQ}\u7684\u516c\u53f8\u3002\n'
        f'\u5c0f\u9f99\u867e\u6253\u5f00\u4e86\u5927\u95e8\uff0c\u4f46\u8d70\u8fdb\u53bb\u4f4f\u4e0b\u6765\u7684\uff0c\u4f1a\u662f\u53e6\u4e00\u6279\u4eba\u3002'
    )

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": header_text}
            },
            {
                "blockId": "subtitle",
                "type": "content",
                "text": {"type": "kimMd", "content": subtitle_text}
            },
            {"blockId": "div0", "type": "divider"},
            {
                "blockId": "insight",
                "type": "content",
                "text": {"type": "kimMd", "content": core_insight}
            },
            {"blockId": "div1", "type": "divider"},
            {
                "blockId": "stats",
                "type": "content",
                "text": {"type": "kimMd", "content": key_stats}
            },
            {"blockId": "div2", "type": "divider"},
            {
                "blockId": "evolution",
                "type": "content",
                "text": {"type": "kimMd", "content": evolution}
            },
            {"blockId": "div3", "type": "divider"},
            {
                "blockId": "analogy",
                "type": "content",
                "text": {"type": "kimMd", "content": analogy}
            },
            {"blockId": "div4", "type": "divider"},
            {
                "blockId": "verdict",
                "type": "content",
                "text": {"type": "kimMd", "content": verdict}
            },
            {"blockId": "div5", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {"type": "kimMd", "content": '*\u6797\u514b\uff08\u6c88\u6d6a\u7684AI\u5206\u8eab\uff09\u00b7 AI\u6d1e\u5bdf \u00b7 \u6df1\u5ea6\u6d1e\u5bdf\u7cfb\u5217*'}
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": '\U0001f99e \u67e5\u770b\u5b8c\u6574\u62a5\u544a >>'},
                        "style": "green",
                        "url": RESEARCH_URL
                    },
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": '\U0001f3e0 \u4e86\u89e3AI\u6d1e\u5bdf\u9879\u76ee'},
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
    parser = argparse.ArgumentParser(description='OpenClaw deep insight KIM push')
    parser.add_argument('--to-user', type=str, help='Send to user')
    parser.add_argument('--to-groups', action='store_true', help='Send to all groups')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    args = parser.parse_args()

    if not args.to_user and not args.to_groups:
        print('Please specify: --to-user <username> or --to-groups')
        return

    title = f'OpenClaw: \u5f53AI\u957f\u51fa{LQ}\u624b\u811a{RQ}'
    print(f'\U0001f99e OpenClaw deep insight push')
    print(f'   Topic: {title}')
    if args.dry_run:
        print('   [DRY-RUN mode]')
    print('=' * 50)

    # 1. Build card
    print('Building card...')
    card = build_openclaw_card()
    print('Card built OK')

    # 2. Get Token
    print('Getting access token...')
    try:
        token = await get_access_token()
        print('Token OK')
    except Exception as e:
        print(f'Token FAIL: {e}')
        return

    # 3. Send
    if args.to_user:
        print(f'\nSending to user: {args.to_user}')
        success = await send_to_user(token, args.to_user, card, args.dry_run)
        if success:
            print('Send OK! Check KIM.')
        else:
            print('Send FAIL')

    if args.to_groups:
        print('\nGetting group list...')
        groups = await get_bot_groups(token)
        if not groups:
            print('No groups found')
            return
        print(f'Groups count: {len(groups)}')

        print('\nPushing to all groups...')
        success_count = 0
        fail_count = 0

        for i, group in enumerate(groups):
            group_id = group['groupId']
            group_name = group['groupName']
            print(f'[{i+1}/{len(groups)}] {group_name}')
            success = await send_to_group_with_retry(token, group_id, group_name, card, args.dry_run)
            if success:
                print(f'   OK')
                success_count += 1
            else:
                fail_count += 1
            if i < len(groups) - 1 and not args.dry_run:
                await asyncio.sleep(SEND_INTERVAL)

        print('\n' + '=' * 50)
        print(f'Done! Success: {success_count}, Fail: {fail_count}')

    print(f'\nReport: {RESEARCH_URL}')


if __name__ == '__main__':
    asyncio.run(main())
