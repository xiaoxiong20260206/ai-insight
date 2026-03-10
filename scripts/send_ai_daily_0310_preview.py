#!/usr/bin/env python3
"""
AI日报KIM卡片发送 - 2026-03-10
发送对象: 沈浪个人预览（不发群）
版本: v3.4
"""

import asyncio
import httpx
from datetime import datetime

# 林克应用凭证
APP_KEY = "30b847d3-9fe4-4598-ac29-0b9a113eb991"
SECRET_KEY = "openApp298f3ef63db4ec3e7909ad4e9"
GATEWAY_URL = "https://is-gateway.corp.kuaishou.com"

async def get_access_token() -> str:
    """获取Access Token"""
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

async def send_to_user(token: str, username: str, card: dict) -> dict:
    """发送MixCard到指定用户"""
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
        return resp.json()

def build_daily_card_0310() -> dict:
    """构建2026-03-10 AI日报卡片 v3.4"""
    
    date_str = "2026-03-10"
    weekday = "周二"
    report_url = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/2026-03/2026-03-10-v3.html"
    insight_url = "https://xiaoxiong20260206.github.io/ai-insight/"
    
    # 热度趋势
    heat_trend = "\n".join([
        "\U0001f525 **热度趋势**（近7期日报交叉分析，3/4-3/10）",
        "",
        "- \U0001f947 **GPT-5.5/DeepSeek V3.5模型更新** \u2014 1天 \u00b7 4板块 \u26a1",
        "  \u2192 GPT-5.5预览版泄露+DeepSeek V3.5中文超越GPT-4",
        "- \U0001f948 **AI Coding工具格局剧变** \u2014 8天 \u00b7 3板块 \U0001f4c8",
        "  \u2192 Cursor Agent Swarm+Claude Code公测+95%使用率",
        "- \U0001f949 **具身智能融资+IPO潮** \u2014 7天 \u00b7 2板块 \U0001f4c8",
        "  \u2192 两月200亿+六家IPO+国资全面入场",
        "- 4\ufe0f\u20e3 **欧盟AI法案全面生效** \u2014 1天 \u26a1",
        "- 5\ufe0f\u20e3 **AI竞争转向组织能力** \u2014 2天 \U0001f195",
        "- 6\ufe0f\u20e3 **Gemini 2.0 Pro开放** \u2014 1天 \U0001f195",
    ])
    
    # 大模型板块
    section1 = "\n".join([
        "## \U0001f9e0 大模型",
        "",
        "\U0001f4f0 **动态**",
        "- \U0001f4e2 突发 | GPT-5.5预览版泄露：多模态提升40%，数学准确率92%",
        "- \U0001f4dc 政策 | 欧盟AI法案今日生效：全球首部全面监管，违规罚7%营收",
        "- \U0001f195 新模型 | Gemini 2.0 Pro开放：200万token上下文创纪录",
        "- \U0001f1e8\U0001f1f3 国内 | DeepSeek V3.5：中文推理超越GPT-4，API降价30%",
        "",
        "\U0001f4a1 **深度聚焦** \u2014 欧盟AI法案全球首部全面AI监管落地",
        "\u2192 高风险AI需注册备案，中国出海企业面临合规挑战",
    ])
    
    # AI Coding板块
    section2 = "\n".join([
        "## \u2328\ufe0f AI Coding",
        "",
        "\U0001f4f0 **动态**",
        "- \U0001f525 热点 | Cursor 0.46发布Agent Swarm：多代理协作编程时代开启",
        "- \U0001f525 热点 | Claude Code正式公测：终端AI编程助手，支持VS Code/Vim",
        "- \U0001f195 新产品 | Vercel V0.dev 3.0：AI组件支持实时协作，首屏提速35%",
        "- \U0001f1e8\U0001f1f3 国内 | 开源AI编辑器Void热度飙升：定位**开源Cursor**",
        "",
        "\U0001f4a1 **深度聚焦** \u2014 Agent Swarm开启多智能体协作新阶段",
        "\u2192 从单Agent辅助到多Agent并行，开发范式根本转变",
    ])
    
    # AI应用板块
    section3 = "\n".join([
        "## \U0001f4f1 AI 应用",
        "",
        "\U0001f4f0 **动态**",
        "- \U0001f195 新产品 | 微软Copilot Pro新增AI编程助手：30+语言全栈自动化",
        "- \U0001f195 新产品 | 英伟达RTX Pro 6000：96GB显存，本地跑70B模型",
        "- \U0001f1e8\U0001f1f3 国内 | 字节RLAIF框架开源：降低模型对齐成本60%",
    ])
    
    # AI行业板块
    section4 = "\n".join([
        "## \U0001f3ed AI 行业",
        "",
        "\U0001f4f0 **动态**",
        "- \U0001f525 热点 | 具身智能两月融资200亿：30+融资，7家新晋百亿独角兽",
        "- \U0001f525 热点 | 六家具身智能公司计划今年IPO：宇树最快5-6月上市",
        "- \U0001f4b0 融资 | 国资全面入场：大基金三期+中国石化+上汽金控领投",
        "",
        "\U0001f4a1 **深度聚焦** \u2014 具身智能IPO潮：从融资狂欢到上市竞速",
        "\u2192 复制2015自动驾驶融资狂潮，但窗口期更短",
    ])
    
    # 企业转型板块
    section5 = "\n".join([
        "## \U0001f504 企业AI转型",
        "",
        "\U0001f4f0 **动态**",
        "- \U0001f525 热点 | AI竞争从**模型能力**转向**组织交付能力**",
        "- \U0001f1e8\U0001f1f3 国内 | 中国AI付费用户破1亿：商业化加速，付费率22%",
        "",
        "\U0001f4a1 **深度聚焦** \u2014 AI竞争新维度：谁能让组织用起来",
        "\u2192 合规能力+落地能力+组织嵌入，技术只是入场券",
    ])
    
    # 页脚
    footer = "*林克（沈浪的AI分身）\u00b7 AI洞察*"
    
    # 构建卡片blocks
    blocks = [
        {"blockId": "header", "type": "content", "text": {"type": "kimMd", "content": f"# \U0001f4e1 AI 日报（{date_str}，{weekday}）"}},
        {"blockId": "d0", "type": "divider"},
        {"blockId": "heat", "type": "content", "text": {"type": "kimMd", "content": heat_trend}},
        {"blockId": "d1", "type": "divider"},
        {"blockId": "sec1", "type": "content", "text": {"type": "kimMd", "content": section1}},
        {"blockId": "d2", "type": "divider"},
        {"blockId": "sec2", "type": "content", "text": {"type": "kimMd", "content": section2}},
        {"blockId": "d3", "type": "divider"},
        {"blockId": "sec3", "type": "content", "text": {"type": "kimMd", "content": section3}},
        {"blockId": "d4", "type": "divider"},
        {"blockId": "sec4", "type": "content", "text": {"type": "kimMd", "content": section4}},
        {"blockId": "d5", "type": "divider"},
        {"blockId": "sec5", "type": "content", "text": {"type": "kimMd", "content": section5}},
        {"blockId": "d6", "type": "divider"},
        {"blockId": "footer", "type": "content", "text": {"type": "kimMd", "content": footer}},
        {
            "blockId": "buttons",
            "type": "action",
            "actions": [
                {
                    "type": "button",
                    "text": {"type": "plainText", "content": "\U0001f4c4 查看完整日报 >>"},
                    "style": "green",
                    "url": report_url
                },
                {
                    "type": "button",
                    "text": {"type": "plainText", "content": "\U0001f3e0 AI洞察首页"},
                    "style": "blue",
                    "url": insight_url
                }
            ],
            "layout": "two"
        }
    ]
    
    return {
        "config": {
            "forward": True,
            "forwardType": 2,
            "wideSelfAdaptive": True
        },
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": blocks
    }

async def main():
    print("=" * 50)
    print("\U0001f4e1 AI日报KIM卡片发送 - 2026-03-10")
    print("=" * 50)
    
    # 1. 获取token
    print("\n\U0001f511 获取Access Token...")
    token = await get_access_token()
    print(f"\u2705 Token获取成功")
    
    # 2. 构建卡片
    print("\n\U0001f4dd 构建日报卡片 v3.4...")
    card = build_daily_card_0310()
    print(f"\u2705 卡片构建完成，包含 {len(card['blocks'])} 个blocks")
    
    # 3. 发送给沈浪个人预览
    print("\n\U0001f4e4 发送给沈浪个人预览...")
    result = await send_to_user(token, "shenlang", card)
    
    if result.get("code") == 0:
        print(f"\u2705 发送成功!")
        print(f"   消息ID: {result.get('data', {}).get('msgId', 'N/A')}")
    else:
        print(f"\u274c 发送失败: {result}")
    
    print("\n" + "=" * 50)
    print("\U0001f4cb 说明: 此卡片仅发给用户个人预览，不发群")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
