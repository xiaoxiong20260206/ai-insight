#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报 KIM 卡片 v3.4 - 2026-03-09
热度趋势+动态+深度聚焦+规律洞察，无序列表缩进
"""

import asyncio
import sys
from pathlib import Path

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
REPORT_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/2026-03/2026-03-09.html"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

LQ = "\u201c"
RQ = "\u201d"


def build_card():

    # ===== 热度趋势（7期交叉分析，3/3-3/9） =====
    heat_trend = "\n".join([
        "\U0001f525 **\u70ed\u5ea6\u8d8b\u52bf**\uff087\u671f\u4ea4\u53c9\u5206\u6790\uff0c3/3-3/9\uff09",
        "",
        "- \U0001f947 **OpenAI GPT-5.x\u751f\u6001\u6269\u5f20** \u2014 7\u5929 \u00b7 4\u677f\u5757 \U0001f4c8",
        "  \u2192 Excel\u91d1\u878d\u96c6\u6210+NATO\u5408\u4f5c+Codex\u7206\u53d1\u589e\u957f",
        "- \U0001f948 **AI Coding\u5de5\u5177\u683c\u5c40\u5267\u53d8** \u2014 7\u5929 \u00b7 3\u677f\u5757 \U0001f4c8",
        "  \u2192 Claude Code\u4ec5\u20098\u6708\u767b\u9876+55%\u5de5\u7a0b\u5e08\u5e38\u7528Agent",
        "- \U0001f949 **\u5177\u8eab\u667a\u80fd\u878d\u8d44\u4e95\u55b7** \u2014 6\u5929 \u00b7 2\u677f\u5757 \U0001f4c8",
        "  \u2192 \u94f6\u6cb3\u901a\u752825\u4ebf+\u661f\u52a8\u7eaa\u514310\u4ebf\uff0c\u5355\u5468\u787035\u4ebf",
        "- 4\ufe0f\u20e3 **AI\u5c31\u4e1a\u51b2\u51fb\u5b9e\u8bc1\u5316** \u2014 5\u5929 \u00b7 3\u677f\u5757 \u27a1\ufe0f",
        "  \u2192 Block\u88c1\u5458+Anthropic\u7814\u7a76\u6301\u7eed\u53d1\u9175",
        "- 5\ufe0f\u20e3 **\u4e2d\u56fdAI\u786c\u4ef6+\u5e94\u7528\u52a0\u901f** \u2014 4\u5929 \u00b7 3\u677f\u5757 \u26a1",
        "  \u2192 \u5343\u95ee\u773c\u955c\u9996\u9500+\u767d\u6cfd\u5f00\u6e90+Mooni\u7206\u6b3e",
        "- 6\ufe0f\u20e3 **AI\u6570\u5b66/\u79d1\u7814\u80fd\u529b\u7a81\u7834** \u2014 3\u5929 \u00b7 2\u677f\u5757 \U0001f195",
        "  \u2192 Claude\u653b\u514b\u56fe\u8bba\u731c\u60f3+\u9ad8\u5fb7\u7eb3\u80cc\u4e66",
    ])

    # ===== 板块1: 大模型 =====
    sec1 = "\n".join([
        "## \U0001f9e0 \u5927\u6a21\u578b",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f195 \u65b0\u7a81\u7834 | [Claude Opus 4.6\u72ec\u7acb\u653b\u514b\u56fe\u8bba\u731c\u60f3\uff0c\u9ad8\u5fb7\u7eb3\u8fde\u5199Shock\uff01Shock\uff01](https://www.anthropic.com/research/claude-math-breakthroughs)",
        "- \U0001f4ca \u65b0\u8bc4\u6d4b | [906\u4eba\u8c03\u67e5\uff1aAnthropic\u6a21\u578b\u4e3b\u5bfc\u7f16\u7801\u4efb\u52a1](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [GPT-5.4+Thinking\u52a0\u5165LMSYS\uff0c\u56fd\u4ea7\u6a21\u578b\u8dcc\u51fa\u524d\u5341](https://zhuanlan.zhihu.com/p/670574382)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u901a\u4e49\u5343\u95ee3.5\u53d1\u5e03\uff1a3970\u4ebf\u53c2\u6570\uff0cAPI\u4f4e\u81f30.8\u5143/\u767e\u4e07Token](http://field.10jqka.com.cn/20260302/c675000614.shtml)",
        "",
        "\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 AI\u4ece\u8ba1\u7b97\u5de5\u5177\u5230\u521b\u9020\u6027\u5408\u4f5c\u8005\u7684\u8d28\u53d8",
        f"\u2192 31\u6b65\u5c31\u6784\u9020\u6027\u89e3\u51b3\u56fe\u8bba\u96be\u9898\u2014\u2014\u4e0d\u662f\u66b4\u529b\u641c\u7d22\uff0c\u662f{LQ}**\u7ea4\u7ef4\u5206\u89e3**{RQ}+{LQ}**bump\u89c4\u5219**{RQ}\u7684\u521b\u9020\u6027\u6d1e\u5bdf",
        "",
        "\U0001f52e **\u89c4\u5f8b\u6d1e\u5bdf** \u2014 \u5de5\u5177\u2192\u52a9\u624b\u2192\u5408\u4f5c\u8005\u4e09\u9636\u6bb5\u89c4\u5f8b",
        "\u2192 Mathematica\u2192AlphaFold/Copilot\u2192Claude\u653b\u514b\u731c\u60f3\u3002\u4e0b\u4e00\u6b65\uff1aAI\u4e3b\u52a8\u63d0\u51fa\u7814\u7a76\u95ee\u9898",
    ])

    # ===== 板块2: AI Coding =====
    sec2 = "\n".join([
        "## \u2328\ufe0f AI Coding",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f4c8 \u65b0\u683c\u5c40 | [Claude Code\u4ec58\u6708\u767b\u9876\uff0c95%\u5de5\u7a0b\u5e08\u6bcf\u5468\u7528AI](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026)",
        "- \U0001f195 \u65b0\u4ea7\u54c1 | [Figma\u96c6\u6210GitHub Copilot\uff1a\u8bbe\u8ba1\u5230\u5f00\u53d1\u5de5\u4f5c\u6d41\u6253\u901a](https://www.figma.com/release-notes/)",
        "- \U0001f4c8 \u65b0\u683c\u5c40 | [OpenAI Codex\u7206\u53d1\u589e\u957f\uff1a\u5df2\u8fbe\u5230Cursor 60%\u4f7f\u7528\u91cf](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u56fd\u5185AI Coding\u683c\u5c40\uff1aTrae/\u901a\u4e49\u7075\u7801/MarsCode\u4e09\u8db3\u9f0e\u7acb](https://aicoding.csdn.net/)",
        "",
        "\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 Claude Code\u5d1b\u8d77\u63ed\u793a\u7ade\u4e89\u80dc\u8d1f\u624b",
        f"\u2192 55%\u5de5\u7a0b\u5e08\u5e38\u7528Agent\uff0cStaff+\u7ea7\u522b63.5%\u4f7f\u7528\u7387\u6700\u9ad8\u2014\u2014{LQ}**AI\u4e3b\u8981\u5e2e\u521d\u7ea7**{RQ}\u7684\u5047\u8bbe\u88ab\u9893\u8986",
    ])

    # ===== 板块3: AI 应用 =====
    sec3 = "\n".join([
        "## \U0001f4f1 AI \u5e94\u7528",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f195 \u65b0\u4ea7\u54c1 | [ChatGPT for Excel\u53d1\u5e03\uff1a\u6295\u884c\u5efa\u6a21\u51c6\u786e\u7387\u7ffb\u500d\u81f387.3%](https://openai.com/index/chatgpt-for-excel/)",
        "- \u2699\ufe0f \u65b0\u6280\u672f | [\u9ad8\u901a\u53d1\u5e03\u53ef\u7a7f\u6234AI\u5e73\u53f0\uff1a20\u4ebf\u53c2\u6570\u5927\u6a21\u578b\u88c5\u5165\u624b\u8868](https://www.qualcomm.com/news/releases/2026/03/qualcomm-snapdragon-wearable-platform-elite)",
        "- \U0001f4c8 \u65b0\u683c\u5c40 | [OpenClaw\u767b\u9876GitHub\u661f\u6807\u5386\u53f2\u7b2c\u4e00\uff0c100\u5929\u8d85\u8d8aLinux](https://github.com/AustrianCodeWriter/OpenClaw)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u5343\u95eeAI\u773c\u955c\u53d1\u552e\uff1aG1\u5230\u624b\u4ef71997\u5143\uff0c\u8d70\u51fa\u624b\u673a\u8fdb\u5165\u7269\u7406\u4e16\u754c](https://mp.weixin.qq.com/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [Mooni M1\u62102026\u5e74\u9996\u4e2aAI\u786c\u4ef6\u7206\u6b3e\uff1a\u6708\u950010\u4e07\u53f0](https://mp.weixin.qq.com/)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 AI+Excel\uff1a{LQ}**\u7279\u6d1b\u4f0a\u6728\u9a6c**{RQ}\u6218\u7565",
        f"\u2192 10\u4ebf\u7528\u6237\u7684Excel+GPT-5.4+9\u5927\u91d1\u878d\u6570\u636e\u6e90\u4e09\u5408\u4e00\uff0c\u91d1\u878d\u884c\u4e1a\u5de5\u4f5c\u6d41\u5373\u5c06\u88ab\u91cd\u6784",
    ])

    # ===== 板块4: AI 行业 =====
    sec4 = "\n".join([
        "## \U0001f3ed AI \u884c\u4e1a",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f504 \u65b0\u52a8\u6001 | [OpenAI\u6d3d\u8c08\u4e0e\u5317\u7ea6AI\u5408\u4f5c\uff0c\u5df2\u63a5\u5165\u7f8e\u56fd\u9632\u90e8\u673a\u5bc6\u7f51\u7edc](https://www.wsj.com/)",
        "- \U0001f4b0 \u878d\u8d44 | [Lotus Health AI\u83b7$4200\u4e07\uff1aAI\u91cd\u6784\u521d\u7ea7\u533b\u7597](https://mp.weixin.qq.com/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u94f6\u6cb3\u901a\u7528\u673a\u5668\u4eba\u5b8c\u621025\u4ebf\u878d\u8d44\uff1a\u5177\u8eab\u667a\u80fd\u5355\u8f6e\u65b0\u9ad8](https://mp.weixin.qq.com/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u661f\u52a8\u7eaa\u5143\u5b8c\u621010\u4ebf\u878d\u8d44\uff0c\u4f30\u503c\u7834\u767e\u4ebf](https://mp.weixin.qq.com/)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 \u4e00\u542835\u4ebf\uff1a\u5177\u8eab\u667a\u80fd\u6210{LQ}**\u56fd\u5bb6\u961f**{RQ}\u6700\u7231",
        f"\u2192 \u56fd\u5bb6AI\u4ea7\u4e1a\u57fa\u91d1+\u4e2d\u56fd\u77f3\u5316\u7b49\u56fd\u8d44\u5927\u4e3e\u5165\u573a\uff0c\u5177\u8eab\u667a\u80fd\u662f{LQ}**AI+\u5236\u9020\u4e1a**{RQ}\u7684\u56fd\u5bb6\u7ea7\u65b9\u6848",
    ])

    # ===== 板块5: 企业AI转型 =====
    sec5 = "\n".join([
        "## \U0001f504 \u4f01\u4e1aAI\u8f6c\u578b",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f4ca \u65b0\u62a5\u544a | [Deloitte\u53d1\u5e032026\u4f01\u4e1aAI\u73b0\u72b6\uff1aAI\u6295\u8d44\u56de\u62a5\u5f00\u59cb\u5151\u73b0](https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html)",
        "- \u2699\ufe0f \u65b0\u6280\u672f | [IBM Agentic AI\u9a71\u52a8FlashSystem\u81ea\u4e3b\u5b58\u50a8](https://newsroom.ibm.com/next-generation-ibm-flashsystem-portfolio)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u6dd8\u5b9d\u95ea\u8d2d\u5f00\u6e90\u9910\u996eAI\u5927\u6a21\u578b\u767d\u6cfd\uff1a\u7d2f\u8ba1\u8c03\u7528\u8d8510\u4ebf\u6b21](https://mp.weixin.qq.com/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u65e0\u95ee\u667a\u79d1\u53d1\u5e03\u9996\u4e2a\u7269\u7406AI\u6570\u636e\u57fa\u5ea7\u5e73\u53f0](https://www.qbitai.com/2026/03/384449.html)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 {LQ}**\u767d\u6cfd**{RQ}\u6a21\u5f0f\uff1a\u5782\u76f4\u884c\u4e1aAI\u7684\u6b63\u786e\u6253\u5f00\u65b9\u5f0f",
        f"\u2192 8B\u53c2\u6570\u4e13\u7cbe\u6a21\u578b\u5728\u7279\u5b9a\u573a\u666f\u5b8c\u5168\u80dc\u4efb\uff0c\u6210\u672c\u4ec5\u4e3a\u901a\u7528\u5927\u6a21\u578b\u7684\u767e\u5206\u4e4b\u4e00\u3002{LQ}**\u5f00\u6e90\u6a21\u578b+\u5782\u76f4\u5fae\u8c03**{RQ}\u662f\u4f01\u4e1a\u6700\u4f73\u8def\u5f84",
    ])

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": "# \U0001f4e1 AI \u65e5\u62a5\uff082026-03-09\uff0c\u5468\u4e00\uff09"},
            },
            {
                "blockId": "subtitle",
                "type": "content",
                "text": {"type": "kimMd", "content": "\U0001f30f \u6d77\u591610\u6761 \u00b7 \U0001f1e8\U0001f1f3 \u56fd\u51858\u6761 | \u4e94\u5927\u677f\u5757 \u00b7 \u6bcf\u677f\u5757\u542b\u52a8\u6001/\u6df1\u5ea6\u805a\u7126/\u89c4\u5f8b\u6d1e\u5bdf"},
            },
            {"blockId": "div0", "type": "divider"},
            {"blockId": "heat", "type": "content", "text": {"type": "kimMd", "content": heat_trend}},
            {"blockId": "div1", "type": "divider"},
            {"blockId": "sec1", "type": "content", "text": {"type": "kimMd", "content": sec1}},
            {"blockId": "div2", "type": "divider"},
            {"blockId": "sec2", "type": "content", "text": {"type": "kimMd", "content": sec2}},
            {"blockId": "div3", "type": "divider"},
            {"blockId": "sec3", "type": "content", "text": {"type": "kimMd", "content": sec3}},
            {"blockId": "div4", "type": "divider"},
            {"blockId": "sec4", "type": "content", "text": {"type": "kimMd", "content": sec4}},
            {"blockId": "div5", "type": "divider"},
            {"blockId": "sec5", "type": "content", "text": {"type": "kimMd", "content": sec5}},
            {"blockId": "div6", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {"type": "kimMd", "content": "*\u6797\u514b\uff08\u6c88\u6d6a\u7684AI\u5206\u8eab\uff09\u00b7 AI\u6d1e\u5bdf*"},
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {"type": "button", "text": {"type": "plainText", "content": "\U0001f4c4 \u67e5\u770b\u5b8c\u6574\u65e5\u62a5 >>"}, "style": "green", "url": REPORT_URL},
                    {"type": "button", "text": {"type": "plainText", "content": "\U0001f3e0 AI\u6d1e\u5bdf\u9996\u9875"}, "style": "blue", "url": PROJECT_URL},
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
    mode = sys.argv[1] if len(sys.argv) > 1 else "groups"

    card = build_card()
    print("Card v3.4 (2026-03-09) built OK")

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
            resp = await client.post(
                f"{GATEWAY_URL}/openapi/v2/message/send",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                json={"username": "shenlang", "msgType": "mixCard", "mixCard": card},
            )
            result = resp.json()
            print(f"Preview result: {result}")
            if result.get("code") == 0:
                print("SUCCESS - sent to shenlang (preview)")
            else:
                print(f"FAILED: {result}")
        else:
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
