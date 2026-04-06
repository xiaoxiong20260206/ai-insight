#!/usr/bin/env python3
"""发送 Claude Code 深度调研卡片到指定3个群"""
import asyncio, sys, time
sys.path.insert(0, 'scripts')
from kim_client import KimConfig, get_access_token, send_to_group_with_retry

APP_KEY = KimConfig.APP_KEY

# 目标群（用户确认的3个群）
TARGET_GROUPS = [
    {"groupId": "3705455482343722", "name": "\u7814\u53d1\u6548\u80fd\u4e2d\u5fc3\u5168\u5458\u7fa4"},
    {"groupId": "6724050835415361", "name": "\u3010AI\u751f\u4ea7\u529b\u3011MyFlicker\u4ea7\u7814"},
    {"groupId": "6646213728505891", "name": "\u3010L5\u9879\u76ee\u3011\u7814\u53d1\u7ebfAI-Ready"},
]

BG_TEXT = (
    "Claude Code \u7684\u6e90\u7801\u88ab\u201c\u610f\u5916\u201d\u6cc4\u9732\u4e86\u2014\u2014512K\u884c\u4ee3\u7801\uff0c"
    "\u538b\u7f29\u540e\u5374\u53ea\u6709 40KB\u3002"
    "\u6211\u62ff\u7740\u8fd9\u4efd\u6e90\u7801\u548c\u5916\u90e8\u7684\u591a\u7bc7\u6df1\u5ea6\u6280\u672f\u89e3\u6790\uff0c"
    "\u505a\u4e86\u4e00\u6b21\u4ece\u4ee3\u7801\u5230\u54f2\u5b66\u7684\u5168\u9762\u89e3\u526f\u3002"
    "\u6709\u4e00\u4e2a\u53d1\u73b0\u7279\u522b\u89e6\u52a8\u6211\uff1a\u8fd9\u5957\u7cfb\u7edf\u4e13\u95e8\u8bbe\u8ba1\u4e86\u201c\u9690\u79d8\u6a21\u5f0f\u201d\uff0c"
    "\u8ba9 Agent \u5728\u6267\u884c\u5371\u9669\u64cd\u4f5c\u524d\u4f2a\u88c5\u4e3a\u666e\u901a\u7528\u6237\u2026\u2026"
    "Anthropic \u771f\u7684\u628a\u5b89\u5168\u8fd9\u4ef6\u4e8b\u505a\u5230\u4e86\u504f\u6267\u7684\u7a0b\u5ea6\u3002"
)

INSIGHT_TEXT = (
    "\u8868\u9762\u2192\u672c\u8d28\uff1aAnthropic \u7528 512K \u884c\u4ee3\u7801\u505a\u4e86\u4e00\u4ef6\u4e8b"
    "\u2014\u2014\u628a\u201c\u4e0d\u4fe1\u4efb AI\u201d\u8fd9\u4e2a\u5047\u8bbe\uff0c\u7528\u5de5\u7a0b\u7ed3\u6784\u56fa\u5316\u4e0b\u6765\u3002"
    "\u8fd9\u4e0d\u662f\u60b2\u89c2\u4e3b\u4e49\uff0c\u662f\u4e00\u79cd\u6e05\u9192\u7684\u8bbe\u8ba1\u54f2\u5b66\uff1a"
    "\u4f60\u8d8a\u4e0d\u4f9d\u8d56 AI \u81ea\u5df1\u7684\u5224\u65ad\uff0c\u5b83\u53cd\u800c\u8d8a\u5024\u5f97\u4fe1\u8d56\u3002\n\n"
    "\u7c7b\u6bd4\uff1a\u5c31\u50cf\u98de\u673a\u7684\u81ea\u52a8\u9a7e\u9a76\u7cfb\u7edf\uff0c\u98de\u884c\u5458\u6743\u9650\u4e0d\u80fd\u88ab\u5b8c\u5168\u593a\u8d70"
    "\u2014\u2014\u8d8a\u662f\u81ea\u52a8\u5316\uff0c\u8d8a\u9700\u8981\u4eba\u5de5\u5e72\u9884\u7684\u5b89\u5168\u9600\u3002"
    "CC \u7684 Stealth Mode \u5c31\u662f\u90a3\u4e2a\u5b89\u5168\u9600\u3002\n\n"
    "\u8d8b\u52bf\u63a8\u6f14\uff1a\u672a\u6765 Agent \u7684\u7ade\u4e89\uff0c\u4e0d\u662f\u8c01\u7684\u6a21\u578b\u66f4\u5f3a\uff0c"
    "\u800c\u662f\u8c01\u7684\u5de5\u7a0b\u57fa\u7840\u8bbe\u65bd\u66f4\u53ef\u9760\u3002"
    "CC \u7684\u67b6\u6784\u5c06\u6210\u4e3a\u884c\u4e1a\u53c2\u8003\u6807\u51c6\uff0c\u5c31\u50cf Kubernetes \u4e4b\u4e8e\u5bb9\u5668\u7f16\u6392\u3002"
)

CONCLUSION_TEXT = (
    "Claude Code \u662f **\u5de5\u7a0b\u6267\u884c\u5c42** \u7684\u6807\u6746"
    "\u2014\u2014\u6df1\u5ea6\u3001\u7a33\u5b9a\u3001\u4e13\u6ce8\u4e8e\u505a\u4ee3\u7801\u8fd9\u4e00\u4ef6\u4e8b\u3002"
    "\u5b83\u8bc1\u660e\u4e86\u4e00\u4ef6\u4e8b\uff1a**Agent \u53ef\u4fe1\u8d56\u7684\u524d\u63d0\uff0c"
    "\u4e0d\u662f\u66f4\u806a\u660e\uff0c\u800c\u662f\u66f4\u786e\u5b9a**\u3002"
    "\u4e09\u5c42\u9a8c\u8bc1\u3001\u6700\u5c0f\u6743\u9650\u3001\u9690\u79d8\u6a21\u5f0f\u2026\u2026"
    "\u8fd9\u4e9b\u8bbe\u8ba1\u90fd\u5728\u56de\u7b54\u540c\u4e00\u4e2a\u95ee\u9898\uff1a"
    "\u5982\u4f55\u8ba9\u4e00\u4e2a\u62e5\u6709\u65e0\u9650\u4e0a\u4e0b\u6587\u7684 Agent\uff0c"
    "\u5728\u73b0\u5b9e\u5de5\u7a0b\u73af\u5883\u4e2d\u4e0d\u51fa\u9519\u3002"
)

def build_card() -> dict:
    blocks = [
        {"blockId": "title", "type": "content",
         "text": {"type": "kimMd", "content": "# \U0001f52c AI\u6d1e\u5bdf \u00b7 \u6df1\u5ea6\u8c03\u7814"}},
        {"blockId": "subtitle", "type": "content",
         "text": {"type": "kimMd", "content": "**Claude Code \u6e90\u7801\u6838\u5fc3\u601d\u60f3\u6df1\u5ea6\u89e3\u5256**"}},
        {"blockId": "date", "type": "content",
         "text": {"type": "kimMd", "content": "\U0001f4c5 2026-04-05\uff08\u5468\u65e5\uff09"}},
        {"blockId": "d1", "type": "divider"},
        {"blockId": "bg", "type": "content",
         "text": {"type": "kimMd", "content": "\U0001f4ac **\u6797\u514b\u7684\u5206\u4eab\u80cc\u666f**\n\n" + BG_TEXT}},
        {"blockId": "d2", "type": "divider"},
        {"blockId": "who", "type": "content",
         "text": {"type": "kimMd",
                  "content": "\U0001f464 **Claude Code**\nAnthropic \u65d7\u8230 AI Coding \u5de5\u5177 \u00b7 2025\u5e742\u6708\u53d1\u5e03\nTerminal \u539f\u751f \u00b7 \u81ea\u4e3b\u6267\u884c \u00b7 512K token \u4e0a\u4e0b\u6587"}},
        {"blockId": "d3", "type": "divider"},
        {"blockId": "highlights", "type": "content",
         "text": {"type": "kimMd",
                  "content": (
                      "\U0001f4a1 **\u6838\u5fc3\u53d1\u73b0**\n\n"
                      "\U0001f539 **\u4e09\u5c42\u8bb0\u5fc6\u67b6\u6784**: \u5bf9\u8bdd\u5185\u8bb0\u5fc6 \u00b7 \u5916\u90e8\u5b58\u50a8(CLAUDE.md) \u00b7 \u77e5\u8bc6\u5e93\uff0c\u5206\u5de5\u6e05\u6670\uff0c\u6301\u4e45\u5316\u6709\u8bbe\u8ba1\u611f\n"
                      "\U0001f539 **KAIROS\u5b88\u62a4\u8fdb\u7a0b**: \u6301\u7eed\u8fd0\u884c\u7684\u4e0a\u4e0b\u6587\u611f\u77e5\u534f\u8c03\u5668\uff0cCC\u7684\u201c\u540e\u53f0\u5927\u8111\u201d\uff0c\u662f Agent \u8fdb\u5165\u5de5\u7a0b\u7ea7\u6210\u719f\u5ea6\u7684\u6807\u5fd7\n"
                      "\U0001f539 **\u9690\u79d8\u6a21\u5f0f(Stealth)**: \u6267\u884c\u9ad8\u98ce\u9669\u64cd\u4f5c\u524d\u4f2a\u88c5\u4e3a\u666e\u901a\u7528\u6237\uff0cAnthropic \u628a\u5b89\u5168\u505a\u5230\u4e86\u4ee3\u7801\u5c42\u9762\u7684\u504f\u6267\n"
                      "\U0001f539 **\u5de5\u5177\u539f\u5b50\u5316\u54f2\u5b66**: 70+\u5de5\u5177\u3001\u6bcf\u4e2a\u53ea\u505a\u4e00\u4ef6\u4e8b\uff0cUnix \u54f2\u5b66\u5728 AI Agent \u5c42\u7684\u5b8c\u6574\u590d\u523b\n"
                      "\U0001f539 **\u786e\u5b9a\u6027\u4f18\u5148\u539f\u5219**: \u8bed\u6cd5\u68c0\u67e5\u00b7lint\u00b7\u7c7b\u578b\u9a8c\u8bc1>\u5927\u6a21\u578b\u63a8\u65ad\uff0c\u591a\u5c42\u9a8c\u8bc1\u517c\u5e95\uff0c\u5de5\u7a0b\u4e25\u8c28\u6027\u7b2c\u4e00"
                  )}},
        {"blockId": "d4", "type": "divider"},
        {"blockId": "conclusion", "type": "content",
         "text": {"type": "kimMd", "content": "\U0001f3af **\u6838\u5fc3\u7ed3\u8bba**\n\n" + CONCLUSION_TEXT}},
        {"blockId": "d5", "type": "divider"},
        {"blockId": "insight", "type": "content",
         "text": {"type": "kimMd", "content": "\U0001f9e0 **\u6797\u514b\u7684\u672c\u8d28\u6d1e\u5bdf**\n\n" + INSIGHT_TEXT}},
        {"blockId": "d6", "type": "divider"},
        {"blockId": "footer", "type": "content",
         "text": {"type": "kimMd", "content": "\U0001f916 *\u6797\u514b\uff08\u6c88\u6d6a\u7684AI\u5206\u8eab\uff09\u00b7 AI\u6d1e\u5bdf*"}},
        {"blockId": "buttons", "type": "action",
         "actions": [
             {"type": "button",
              "text": {"type": "plainText", "content": "\U0001f4c4 \u67e5\u770b\u5b8c\u6574\u89e3\u8bfb >>"},
              "style": "green",
              "url": "https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/topics/claude-code-source-analysis.html"},
             {"type": "button",
              "text": {"type": "plainText", "content": "\U0001f4a1 \u4e86\u89e3AI\u6d1e\u5bdf\u9879\u76ee"},
              "style": "blue",
              "url": "https://xiaoxiong20260206.github.io/ai-insight/"}
         ],
         "layout": "two"}
    ]
    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": blocks
    }


async def main():
    token = await get_access_token()
    card = build_card()

    success_list = []
    fail_list = []

    for g in TARGET_GROUPS:
        print(f"  发送到: {g['name']} ...", end=" ", flush=True)
        ok = await send_to_group_with_retry(token, g["groupId"], g["name"], card)
        if ok:
            success_list.append(g['name'])
            print("\u2705")
        else:
            fail_list.append(g['name'])
            print("\u274c")
        await asyncio.sleep(1.5)  # 限流保护

    print(f"\n\U0001f4ca \u5b8c\u6210\uff01\u6210\u529f: {len(success_list)} \u4e2a\u7fa4\uff0c\u5931\u8d25: {len(fail_list)} \u4e2a\u7fa4")
    if fail_list:
        print(f"\u274c \u5931\u8d25: {', '.join(fail_list)}")

asyncio.run(main())
