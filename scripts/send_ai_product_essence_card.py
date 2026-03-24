#!/usr/bin/env python3
"""
AI产品本质深度调研 KIM 卡片推送脚本
================================
主题: 99%的AI产品都做错了

使用方式:
  python scripts/send_ai_product_essence_card.py --preview     # 发给自己预览
  python scripts/send_ai_product_essence_card.py --to-groups   # 发到目标群

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
    print("请先安装 httpx: pip install httpx")
    raise SystemExit(1)

sys.path.insert(0, str(Path(__file__).parent))
from kim_client import KimConfig

KimConfig.validate()

APP_KEY = KimConfig.APP_KEY
SECRET_KEY = KimConfig.SECRET_KEY
GATEWAY_URL = KimConfig.GATEWAY_URL

RESEARCH_URL = (
    "https://xiaoxiong20260206.github.io/ai-insight/"
    "02-deep-research/topics/ai-product-essence-2026.html"
)
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

TARGET_GROUPS = [
    {"groupId": "6724050835415361", "groupName": "\u300b\u5feb\u624bAI\u5458\u5de5"},
    {"groupId": "6501852196213070", "groupName": "AI\u4ea7\u54c1\u5546\u4e1a\u5316\uff082026\u5e74\uff09"},
]

SEND_INTERVAL = 2.5
MAX_RETRIES = 3
RETRY_DELAY = 5


async def get_access_token() -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={
                "appKey": APP_KEY,
                "secretKey": SECRET_KEY,
                "grantType": "client_credentials",
            },
        )
        result = resp.json()
        if result.get("code") == 0:
            return result["result"]["accessToken"]
        raise Exception(f"Token获取失败: {result}")


async def send_to_user(token: str, username: str, card: dict, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"   [DRY-RUN] 将发送到用户: {username}")
        return True
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/message/send",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            json={"username": username, "msgType": "mixCard", "mixCard": card},
        )
        result = resp.json()
        if result.get("code") == 0:
            return True
        print(f"   发送失败: {result}")
        return False


async def send_to_group(
    token: str, group_id: str, group_name: str, card: dict, dry_run: bool = False
) -> bool:
    if dry_run:
        print(f"   [DRY-RUN] 将发送到: {group_name} ({group_id})")
        return True
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{GATEWAY_URL}/openapi/v2/message/send",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    json={"groupId": group_id, "msgType": "mixCard", "mixCard": card},
                )
                result = resp.json()
                if result.get("code") == 0:
                    return True
                if result.get("code") == 42900 and attempt < MAX_RETRIES - 1:
                    print(f"   频率限制，{RETRY_DELAY}s后重试 ({attempt+1}/{MAX_RETRIES})")
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                print(f"   发送失败: {result}")
                return False
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"   发送异常: {e}")
                return False
    return False


def build_card() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    weekdays = ["\u5468\u4e00", "\u5468\u4e8c", "\u5468\u4e09", "\u5468\u56db",
                "\u5468\u4e94", "\u5468\u516d", "\u5468\u65e5"]
    weekday = weekdays[datetime.now().weekday()]

    # 全部用 Unicode 转义，彻底规避中文引号 SyntaxError
    LQ = "\u201c"
    RQ = "\u201d"
    EM = "\u2014"

    header_text = (
        "# \U0001f9e0 \u6df1\u5ea6\u8c03\u7814 \u00b7 AI\u4ea7\u54c1\u672c\u8d28\u7814\u7a76\n\n"
        + f"\U0001f4c5 *{today}\uff08{weekday}\uff09*"
    )

    core_text = (
        "**\u6838\u5fc3\u7ed3\u8bba**\n\n"
        + f"99%\u7684AI\u4ea7\u54c1\u6b63\u5728\u7528{LQ}**\u4e70\u5de5\u5177**{RQ}\u7684\u601d\u7ef4"
        + f"\uff0c\u505a{LQ}**\u62db\u5458\u5de5**{RQ}\u7684\u4e8b\u3002\n\n"
        + "AI\u4ea7\u54c1\u7684\u672c\u8d28\u662f**\u8ba4\u77e5\u4ee3\u52b3**\uff0c\u4e0d\u662f\u529f\u80fd\u66ff\u4ee3\u3002"
        + "\u7528SaaS\u7684\u903b\u8f91\u505aAI\uff0c\u8d8a\u52aa\u529b\u8d8a\u9519\u3002\n\n"
        + "\U0001f4cc \u6210\u529f\u516c\u5f0f\uff1a**(Q > \u9608\u503c) \u00d7 D \u00d7 T > E**\n"
        + "- Q: \u8d28\u91cf\u7a7f\u8d8a\u9608\u503c\uff08\u7528\u6237\u8981\u60ca\u547c\uff0c\u4e0d\u662f\u8fd8\u884c\uff09\n"
        + "- D: \u573a\u666f\u8981\u6df1\u4e0d\u8981\u5e7f\n"
        + "- T: \u4fe1\u4efb\u79ef\u7d2f\u5fc5\u987b\u8dd1\u8d62\u6210\u672c\u6d88\u8017"
    )

    mistakes_text = (
        "\u274c **\u516d\u5927\u9519\u8bef\uff1a\u4e70\u5de5\u5177\u601d\u7ef4 vs \u62db\u5458\u5de5\u73b0\u5b9e**\n\n"
        + f"- \u9519\u8bef1\uff1a**\u62fc\u547d\u5806\u529f\u80fd** {EM} \u8d28\u91cf\u4e0d\u591f\u7684\u529f\u80fd\u8d8a\u591a\uff0c\u8d1f\u9762\u4f53\u9a8c\u9762\u8d8a\u5927\n"
        + f"- \u9519\u8bef2\uff1a**\u5148\u63a8\u5e7f\u518d\u6253\u78e8** {EM} AI\u7684\u7b2c\u4e00\u5370\u8c61\u5b9a\u683c\u4e3a{LQ}\u6ca1\u7528{RQ}\uff0c\u51e0\u4e4e\u4e0d\u53ef\u9006\n"
        + f"- \u9519\u8bef3\uff1a**\u4e0d\u8ba1\u6210\u672c\u62c9\u7528\u6237** {EM} \u6bcf\u6b21\u63a8\u7406\u90fd\u70e7\u7b97\u529b\uff0c\u8d28\u91cf\u672a\u8fc7\u9608\u503c\u65f6\u8d8a\u63a8\u5e7f\u8d8a\u70e7\u4fe1\u8a89\n"
        + f"- \u9519\u8bef4\uff1a**\u529f\u80fd\u77e9\u9635\u5bf9\u6807\u7ade\u54c1** {EM} AI\u7684\u7ade\u4e89\u7ef4\u5ea6\u662f\u8d28\u91cf\u6df1\u5ea6\uff0c\u4e0d\u662f\u529f\u80fd\u5e7f\u5ea6\n"
        + f"- \u9519\u8bef5\uff1a**\u7528SaaS\u6f0f\u6597\u627e\u7559\u5b58\u7b54\u6848** {EM} SaaS\u7559\u5b58\u662fUX\u95ee\u9898\uff0cAI\u7559\u5b58\u662f\u8d28\u91cf\u95ee\u9898\n"
        + f"- \u9519\u8bef6\uff1a**\u5148\u5708\u5730\u76d8\u518d\u63d0\u8d28\u91cf** {EM} \u5708\u4e86\u4e00\u4e2a{LQ}\u4e0d\u591f\u806a\u660e{RQ}\u7684\u5fc3\u667a\uff0c\u662f\u6700\u96be\u9006\u8f6c\u7684"
    )

    scorecard_text = (
        "\U0001f4cb **\u4e94\u6b3e\u4ea7\u54c1\u8bc4\u5206\uff08\u4e94\u7ef4\u6846\u67b6\uff1aQ\u8d28\u91cf/E\u7ecf\u6d4e/T\u4fe1\u4efb/D\u573a\u666f\uff09**\n\n"
        + "- \u2705 Cursor \u2014 Q:\u2605\u2605\u2605\u2605\u2605 E:\u2605\u2605\u2605\u2605\u2605 T:\u2605\u2605\u2605\u2605\u2605 D:\u2605\u2605\u2605\u2605\u2605 | \u6559\u79d1\u4e66\n"
        + "- \u2705 Claude Code \u2014 Q:\u2605\u2605\u2605\u2605\u2605 E:\u2605\u2605\u2605\u2605 T:\u2605\u2605\u2605\u2605 D:\u2605\u2605\u2605\u2605\u2605 | \u6559\u79d1\u4e66\n"
        + "- \u2705 \u9489\u9489\u609f\u7a7a \u2014 Q:\u2605\u2605\u2605\u2605 E:\u2605\u2605\u2605\u2605 T:\u2605\u2605\u2605\u2605\u2605 D:\u2605\u2605\u2605\u2605 | \u65b9\u5411\u6b63\u786e\n"
        + "- \u26a0\ufe0f OpenClaw \u2014 Q:\u2605\u2605\u2605\u2605 E:\u2605\u2605 T:\u2605\u2605\u2605 D:\u2605\u2605\u2605 | \u9a8c\u8bc1\u4e86\u9700\u6c42\n"
        + "- \u26a0\ufe0f Manus \u2014 Q:\u2605\u2605\u2605 E:\u2605\u2605 T:\u2605\u2605 D:\u2605\u2605 | \u901a\u7528\u9677\u9631\uff08\u6837\u6837\u80fd\u505a\uff0c\u6837\u6837\u4e0d\u6df1\uff09"
    )

    insight_text = (
        "\U0001f9e0 **\u6797\u514b\u7684\u672c\u8d28\u6d1e\u5bdf**\n\n"
        + f"\u8868\u9762\uff1a\u505a\u5f97\u597d\u7684AI\u4ea7\u54c1\u4e0d\u63a8\u5e7f\uff0c\u7838\u4e86\u94b1\u7684\u53cd\u800c\u8d8a\u505a\u8d8a\u96be\u3002\n\n"
        + f"\u672c\u8d28\uff1aSaaS\u5356\u7684\u662f{LQ}\u6743\u5229{RQ}{EM}\u4f60\u6709\u6743\u4f7f\u7528\u8fd9\u4e2a\u529f\u80fd\uff1b"
        + f"AI\u5356\u7684\u662f{LQ}\u4ee3\u52b3{RQ}{EM}\u6211\u66ff\u4f60\u628a\u8fd9\u4ef6\u4e8b\u505a\u597d\u3002"
        + f"\u6743\u5229\u53ef\u4ee5\u627f\u8bfa\uff0c\u4ee3\u52b3\u53ea\u80fd\u8bc1\u660e\u3002"
        + f"\u5c31\u50cf\u9470\u5319\u53ef\u4ee5\u5927\u91cf\u590d\u5236\u5206\u53d1\uff0c\u4eba\u53ea\u80fd\u9760\u53e3\u53e3\u76f8\u4f20\u5efa\u7acb\u4fe1\u4efb\u3002\n\n"
        + f"\u8d8b\u52bf\u63a8\u6f14\uff1a\u672a\u6765AI\u4ea7\u54c1\u7684\u62a4\u57ce\u6cb3\u4e0d\u662f\u529f\u80fd\u6570\u91cf\uff0c\u800c\u662f{LQ}\u4fe1\u4efb\u6df1\u5ea6{RQ}"
        + f"{EM}\u8c01\u7684AI\u79ef\u7d2f\u4e86\u66f4\u591a\u4e2a\u6027\u5316\u8bb0\u5fc6\u3001\u8ba9\u7528\u6237\u8d8a\u7528\u8d8a\u79bb\u4e0d\u5f00\uff0c\u5c31\u8d8a\u96be\u88ab\u66ff\u6362\u3002"
    )

    footer_text = (
        "*\u6797\u514b\uff08\u6c88\u6d6a\u7684AI\u5206\u8eab\uff09"
        + " \u00b7 AI\u6d1e\u5bdf \u00b7 \u6df1\u5ea6\u8c03\u7814\u7cfb\u5217*"
    )

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {"blockId": "header", "type": "content",
             "text": {"type": "kimMd", "content": header_text}},
            {"blockId": "div0", "type": "divider"},
            {"blockId": "core", "type": "content",
             "text": {"type": "kimMd", "content": core_text}},
            {"blockId": "div1", "type": "divider"},
            {"blockId": "mistakes", "type": "content",
             "text": {"type": "kimMd", "content": mistakes_text}},
            {"blockId": "div2", "type": "divider"},
            {"blockId": "scorecard", "type": "content",
             "text": {"type": "kimMd", "content": scorecard_text}},
            {"blockId": "div3", "type": "divider"},
            {"blockId": "insight", "type": "content",
             "text": {"type": "kimMd", "content": insight_text}},
            {"blockId": "div4", "type": "divider"},
            {"blockId": "footer", "type": "content",
             "text": {"type": "kimMd", "content": footer_text}},
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "\U0001f4c4 \u67e5\u770b\u5b8c\u6574\u89e3\u8bfb >>"},
                        "style": "green",
                        "url": RESEARCH_URL,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "\U0001f4a1 \u4e86\u89e3AI\u6d1e\u5bdf\u9879\u76ee"},
                        "style": "blue",
                        "url": PROJECT_URL,
                    },
                ],
                "layout": "two",
            },
        ],
    }


async def main():
    parser = argparse.ArgumentParser(description="AI\u4ea7\u54c1\u672c\u8d28\u6df1\u5ea6\u8c03\u7814\u5361\u7247\u63a8\u9001")
    parser.add_argument("--preview", action="store_true", help="\u53d1\u7ed9\u81ea\u5df1\u9884\u89c8")
    parser.add_argument("--to-user", type=str, help="\u53d1\u9001\u5230\u6307\u5b9a\u7528\u6237")
    parser.add_argument("--to-groups", action="store_true", help="\u53d1\u9001\u5230\u76ee\u6807\u7fa4")
    parser.add_argument("--dry-run", action="store_true", help="\u8bd5\u8fd0\u884c")
    args = parser.parse_args()

    if args.preview:
        args.to_user = "shenlang"
    if not args.to_user and not args.to_groups:
        print("\u8bf7\u6307\u5b9a\u53d1\u9001\u76ee\u6807: --preview \u6216 --to-groups")
        return

    print("\U0001f680 AI\u4ea7\u54c1\u672c\u8d28\u6df1\u5ea6\u8c03\u7814\u5361\u7247\u63a8\u9001")
    if args.dry_run:
        print("   [DRY-RUN \u6a21\u5f0f]")
    print("=" * 55)

    print("\U0001f3a8 \u6784\u5efa\u5361\u7247...")
    card = build_card()
    print("\u2705 \u5361\u7247\u6784\u5efa\u5b8c\u6210")

    print("\U0001f511 \u83b7\u53d6 Token...")
    try:
        token = await get_access_token()
        print("\u2705 Token \u83b7\u53d6\u6210\u529f")
    except Exception as e:
        print(f"\u274c Token \u83b7\u53d6\u5931\u8d25: {e}")
        return

    if args.to_user:
        print(f"\n\U0001f4e4 \u53d1\u9001\u7ed9\u7528\u6237: {args.to_user}")
        ok = await send_to_user(token, args.to_user, card, args.dry_run)
        print("\u2705 \u53d1\u9001\u6210\u529f\uff01\u8bf7\u68c0\u67e5 KIM \u6d88\u606f" if ok else "\u274c \u53d1\u9001\u5931\u8d25")

    if args.to_groups:
        print(f"\n\U0001f4cb \u76ee\u6807\u7fa4\uff08{len(TARGET_GROUPS)} \u4e2a\uff09:")
        for g in TARGET_GROUPS:
            print(f"   - {g['groupName']} ({g['groupId']})")
        print("\n\U0001f4e4 \u5f00\u59cb\u63a8\u9001...")
        ok_count = 0
        fail_list = []
        for i, g in enumerate(TARGET_GROUPS):
            print(f"[{i+1}/{len(TARGET_GROUPS)}] \u53d1\u9001\u5230: {g['groupName']}")
            ok = await send_to_group(token, g["groupId"], g["groupName"], card, args.dry_run)
            if ok:
                print("   \u2705 \u6210\u529f")
                ok_count += 1
            else:
                fail_list.append(g["groupName"])
            if i < len(TARGET_GROUPS) - 1 and not args.dry_run:
                await asyncio.sleep(SEND_INTERVAL)
        print("\n" + "=" * 55)
        print(f"\U0001f4ca \u5b8c\u6210\uff01\u6210\u529f: {ok_count}\uff0c\u5931\u8d25: {len(fail_list)}")
        if fail_list:
            print(f"\u26a0\ufe0f  \u5931\u8d25\u7fa4\uff08\u8bf7\u786e\u8ba4\u540e\u91cd\u53d1\uff09: {fail_list}")

    print(f"\n\U0001f4c4 \u5b8c\u6574\u62a5\u544a: {RESEARCH_URL}")


if __name__ == "__main__":
    asyncio.run(main())
