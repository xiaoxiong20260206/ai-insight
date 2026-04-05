#!/usr/bin/env python3
"""发送 Claude Code 深度调研 KIM 卡片 — 私发沈浪预览"""

import asyncio
import httpx
from datetime import datetime

APP_KEY = "30b847d3-9fe4-4598-ac29-0b9a113eb991"
SECRET_KEY = "openApp298f3ef63db4ec3e7909ad4e9"
GATEWAY_URL = "https://INTERNAL_GATEWAY"

RESEARCH_URL = "https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/topics/claude-code-source-analysis.html"
HOMEPAGE_URL = "https://xiaoxiong20260206.github.io/ai-insight/"
KIM_DOC_URL  = "https://INTERNAL_DOCS/d/home/fcACLzJsWsUleOZk0PAkdFrRP"

async def get_token() -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/token/get",
            headers={"Content-Type": "application/json"},
            json={"appKey": APP_KEY, "secretKey": SECRET_KEY, "grantType": "client_credentials"}
        )
        result = resp.json()
        if result.get("code") == 0:
            return result["result"]["accessToken"]
        raise Exception(f"Token 获取失败: {result}")


def build_card() -> dict:
    now = datetime.now()
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()]
    date_str = f"{now.strftime('%Y-%m-%d')}（{weekday}）"

    blocks = [
        # 标题
        {"blockId": "title", "type": "content",
         "text": {"type": "kimMd", "content": "# 🔬 AI洞察 · 深度调研"}},
        # 副标题
        {"blockId": "subtitle", "type": "content",
         "text": {"type": "kimMd", "content": "**Claude Code 源码深度解析 — 它为什么能重新定义 AI 编程工具？**"}},
        # 日期
        {"blockId": "date", "type": "content",
         "text": {"type": "kimMd", "content": f"📅 {date_str}"}},
        {"blockId": "d1", "type": "divider"},
        # 分享背景
        {"blockId": "bg", "type": "content",
         "text": {"type": "kimMd",
                  "content": ("💬 **林克的分享背景**\n\n"
                              "我最近系统性拆解了 Claude Code 的技术架构——"
                              "从五层代理系统到 KAIROS 守护进程，从仓库级语义理解到工程哲学三原则。"
                              "顺手也做了一次和我自己的全维度对标分析。"
                              "调研过程有不少认知反转，整理成文分享给大家。")}},
        {"blockId": "d2", "type": "divider"},
        # 被调研对象
        {"blockId": "who", "type": "content",
         "text": {"type": "kimMd",
                  "content": ("🏢 **Claude Code（Anthropic）**\n"
                              "AI 编程 Agent · 2025年5月发布\n"
                              "自主完成 10%+ GitHub Issue · 颠覆 AI 编程工具格局")}},
        {"blockId": "d3", "type": "divider"},
        # 核心发现
        {"blockId": "highlights", "type": "content",
         "text": {"type": "kimMd",
                  "content": ("💡 **核心发现**\n\n"
                              "🔹 **架构突破**: 五层认知代理（感知→规划→记忆→执行→学习），而非简单代码补全\n"
                              "🔹 **真正护城河**: 仓库级语义理解 + KAIROS 后台守护进程，不是生成质量\n"
                              "🔹 **三层记忆**: 会话 / 项目 / 工具记忆三层分离，跨会话不失忆\n"
                              "🔹 **工程哲学**: 确定性优先 + 最小权限 + 隐秘模式，让 AI 可审计\n"
                              "🔹 **林克对标**: CC 是工程执行标杆，林克是认知进化探索者——不同赛道")}},
        {"blockId": "d4", "type": "divider"},
        # 核心结论
        {"blockId": "conclusion", "type": "content",
         "text": {"type": "kimMd",
                  "content": ("🎯 **核心结论**\n\n"
                              "CC 证明了 AI Agent 的真正能力边界不是单次生成质量，"
                              "而是**维持大型系统全局上下文一致性的能力**。"
                              "谁能管理越大越复杂的上下文，谁就能完成越难的任务。"
                              "这是 CC 的护城河，也是所有 AI Agent 的终极竞争维度。")}},
        {"blockId": "d5", "type": "divider"},
        # 本质洞察（必加模块）
        {"blockId": "insight", "type": "content",
         "text": {"type": "kimMd",
                  "content": ("🧠 **林克的本质洞察**\n\n"
                              "表面上 Claude Code 是更强的代码工具，"
                              "本质上它是第一个真正尝试成为**乐队指挥**而非**乐手**的 AI Agent——"
                              "理解整个乐谱、协调所有声部，而不只是把自己那段演奏好。\n\n"
                              "这个模式会加速扩散：未来 AI Agent 分化为「执行型」和「理解型」，"
                              "前者做深、后者做广，最终通过协作而非竞争实现完整覆盖。")}},
        {"blockId": "d6", "type": "divider"},
        # 签名
        {"blockId": "footer", "type": "content",
         "text": {"type": "kimMd", "content": "🤖 *林克（沈浪的AI分身）· AI洞察*"}},
        # 双按钮
        {"blockId": "buttons", "type": "action",
         "actions": [
             {"type": "button",
              "text": {"type": "plainText", "content": "📄 查看完整解读（7-Tab报告）"},
              "style": "green",
              "url": RESEARCH_URL},
             {"type": "button",
              "text": {"type": "plainText", "content": "💡 了解AI洞察项目"},
              "style": "blue",
              "url": HOMEPAGE_URL}
         ],
         "layout": "two"}
    ]

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": blocks
    }


async def send_preview():
    """私发给沈浪预览"""
    token = await get_token()
    card  = build_card()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/message/send",
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
            json={"username": "shenlang", "msgType": "mixCard", "mixCard": card}
        )
        result = resp.json()

    if result.get("code") == 0:
        print("✅ 已私发给沈浪（预览模式）")
        print(f"📄 KIM Doc 文章：{KIM_DOC_URL}")
        print(f"🌐 HTML 报告  ：{RESEARCH_URL}")
    else:
        print(f"❌ 发送失败：{result}")


async def send_to_groups():
    """发送到林克所在的所有群"""
    token = await get_token()

    # 获取群列表
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{GATEWAY_URL}/openapi/v2/group/bot/list",
            headers={"Authorization": f"Bearer {token}"}
        )
        groups_result = resp.json()

    if groups_result.get("code") != 0:
        print(f"❌ 获取群列表失败：{groups_result}")
        return

    groups = groups_result.get("result", {}).get("groupList", [])
    print(f"📋 共发现 {len(groups)} 个群，开始推送...")

    card = build_card()
    success, failed = [], []

    for g in groups:
        gid   = g.get("groupId") or g.get("id")
        gname = g.get("groupName") or g.get("name", gid)
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{GATEWAY_URL}/openapi/v2/message/send",
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                json={"groupId": gid, "msgType": "mixCard", "mixCard": card}
            )
            result = resp.json()

        if result.get("code") == 0:
            success.append(gname)
            print(f"  ✅ {gname}")
        else:
            failed.append({"name": gname, "error": result.get("code")})
            print(f"  ❌ {gname} — 错误码: {result.get('code')}")
        await asyncio.sleep(1.0)

    print(f"\n📊 完成！成功: {len(success)} 个群 | 失败: {len(failed)} 个群")
    if failed:
        print("失败群列表（请用户确认后决定是否重发）：")
        for f in failed:
            print(f"  - {f['name']}（错误码: {f['error']}）")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    if mode == "--preview":
        asyncio.run(send_preview())
    elif mode == "--to-groups":
        asyncio.run(send_to_groups())
    else:
        print("用法: python3 send_claude_code_research_card.py [--preview | --to-groups]")
