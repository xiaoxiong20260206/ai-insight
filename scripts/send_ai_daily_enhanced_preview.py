#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报 KIM 卡片 v3.1 - 2026-03-08
含热度趋势模块 + 分类标签 + 深度聚焦 + 规律洞察
"""

import asyncio
import httpx

APP_KEY = "30b847d3-9fe4-4598-ac29-0b9a113eb991"
SECRET_KEY = "openApp298f3ef63db4ec3e7909ad4e9"
GATEWAY_URL = "https://is-gateway.corp.kuaishou.com"
REPORT_URL = "https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/2026-03/2026-03-08-v3.html"
PROJECT_URL = "https://xiaoxiong20260206.github.io/ai-insight/"

LQ = "\u201c"
RQ = "\u201d"


def build_card():

    # heat trend
    heat_trend = "\n".join([
        "\U0001f525 **热度趋势**（近6期日报交叉分析，3/3-3/8）",
        "",
        "\U0001f947 **OpenAI GPT-5.x 密集发布** \u2014 6天连续 \u00b7 4板块 \U0001f4c8",
        "\u2192 一周四款：Instant\u2192Codex-Spark\u21925.4\u21925.4 Pro",
        "",
        "\U0001f948 **Anthropic 多线作战** \u2014 6天连续 \u00b7 3板块 \u27a1\ufe0f",
        "\u2192 App Store登顶\u2192国防争议\u2192$1700亿融资\u2192劳动力研究",
        "",
        "\U0001f949 **AI资本超级周期** \u2014 5天连续 \u00b7 行业 \U0001f4c8",
        "\u2192 Anthropic $1700亿 + 欧盟\u20ac7500万 + 3月首周3笔超$5亿",
        "",
        "4\ufe0f\u20e3 **AI Coding三国演义** \u2014 6天 \u00b7 Coding \u27a1\ufe0f",
        "5\ufe0f\u20e3 **Computer Use能力爆发** \u2014 3天 \u00b7 跨3板块 \u26a1\ufe0f 突发飙升",
        f"6\ufe0f\u20e3 **DeepSeek V4发布** \u2014 3天 \u00b7 大模型/行业 \U0001f195",
        f"7\ufe0f\u20e3 **\U0001f1e8\U0001f1f3 AI应用入口争夺** \u2014 3天 \u00b7 应用 \U0001f195",
    ])

    # sec1: foundation models
    sec1 = "\n".join([
        "\U0001f9e0 **大模型**",
        "\U0001f195 新模型 | [GPT-5.4：首个原生Computer Use通用模型](https://openai.com/index/introducing-gpt-5-4/)",
        "\U0001f195 新模型 | [GPT-5.3 Instant：更快更自然的日常对话](https://openai.com/index/gpt-5-3-instant/)",
        "\U0001f4ca 新评测 | [独立盲测GPT-5.4 vs Claude vs Gemini](https://natesnewsletter.substack.com/p/i-tested-gpt-54-against-claude-and)",
        f"\U0001f1e8\U0001f1f3 新模型 | [DeepSeek V4 Lite：原生多模态+国产芯片](https://www.cls.cn/detail/2298837)",
        "\U0001f1e8\U0001f1f3 新格局 | [LMSYS竞技场：GPT-5.4加入后国产模型跌出前十](https://zhuanlan.zhihu.com/p/670574382)",
        "",
        f"\U0001f4a1 **深度聚焦** \u2014 AI从{LQ}**对话伙伴**{RQ}变成{LQ}**计算机操作员**{RQ}",
        "\u2192 OSWorld 75.0%超越人类72.4%。**关注computer-use落地：RPA替代、自动化测试**",
        "",
        f"\U0001f52e **规律洞察** \u2014 技术平台化三阶段：工具\u2192协作\u2192自治",
        f"\u2192 Computer Use = AI进入协作阶段。12-18月内将出现首批{LQ}**无需确认**{RQ}的Agent产品",
    ])

    # sec2: AI Coding
    sec2 = "\n".join([
        "\u2328\ufe0f **AI Coding**",
        "\U0001f4c8 新格局 | [Cursor登Forbes封面：AI编程争霸战打响](https://www.forbes.com/sites/annatong/2026/03/05/cursor-goes-to-war-for-ai-coding-dominance/)",
        "\u2699\ufe0f 新技术 | [GPT-5.4 Computer Use + Playwright交互式调试](https://openai.com/index/introducing-gpt-5-4/)",
        "\U0001f4e6 新产品 | [Codex桌面应用登陆Windows](https://openai.com/index/introducing-the-codex-app/)",
        "\U0001f6e0\ufe0f 新实践 | [Anthropic研究：程序员75%任务已被AI覆盖](https://www.anthropic.com/research/labor-market-impacts)",
        "",
        f"\U0001f4a1 **深度聚焦** \u2014 AI编程的{LQ}**全栈化**{RQ}时刻",
        f"\u2192 从{LQ}写完给你跑{RQ}到{LQ}我写、我跑、我看、我改{RQ}。**AI Coding从提效工具变成生产力替代**",
    ])

    # sec3: AI applications
    sec3 = "\n".join([
        "\U0001f4f1 **AI 应用**",
        f"\u2699\ufe0f 新技术 | [GPT-5.4 Thinking支持{LQ}中途纠偏{RQ}](https://openai.com/index/introducing-gpt-5-4/)",
        "\U0001f6e0\ufe0f 新实践 | [Anthropic劳动力影响指数：编程75%/写作65%/分析60%](https://www.businessinsider.com/anthropic-is-tracking-the-jobs-most-exposed-to-ai-disruption-2026-3)",
        "\U0001f1e8\U0001f1f3 新产品 | [美团Tabbit AI浏览器公测：搜索+对话+任务执行](https://www.21jingji.com/article/20260303/herald/64d2c422041660c41845768679286e48.html)",
        "\U0001f1e8\U0001f1f3 新动态 | [阿里桌面Agent全面开放+Coze密集更新](https://finance.eastmoney.com/a/202603043660857296.html)",
        "",
        f"\U0001f4a1 **深度聚焦** \u2014 \U0001f1e8\U0001f1f3 AI浏览器：大厂为什么抢这个入口？",
        f"\u2192 浏览器是{LQ}**最后一个通用入口**{RQ}。**AI浏览器是普通用户接触Agent最自然的方式**",
    ])

    # sec4: AI industry
    sec4 = "\n".join([
        "\U0001f3ed **AI 行业**",
        "\U0001f4b0 融资 | [Anthropic估值$1700亿，18月涨9倍](https://news.crunchbase.com/ai/unicorn-anthropic-fund-valuation-raise-iconiq/)",
        f"\U0001f4b0 融资 | [欧盟\u20ac7500万EURO-3C项目启动](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence)",
        "\U0001f4c5 行业活动 | [NVIDIA GTC 2026下周开幕(3/16-19)](https://www.nvidia.cn/gtc-global/startups/)",
        "\U0001f1e8\U0001f1f3 新技术 | [DeepSeek V4适配国产芯片：独立于NVIDIA路线](https://hub.baai.ac.cn/view/52808)",
        "",
        f"\U0001f4a1 **深度聚焦** \u2014 AI资本的{LQ}**超级周期**{RQ}",
        "\u2192 三巨头总估值~$5830亿。**真正风险不在泡沫，在头部效应\u2014\u2014前3名可能拿走90%市场**",
    ])

    # sec5: Enterprise AI
    sec5 = "\n".join([
        "\U0001f504 **企业AI转型**",
        "\U0001f6e0\ufe0f 新实践 | [联想MWC展示可信AI企业方案](https://news.lenovo.com/pressroom/press-releases/adaptive-ai-pcs-modular-concepts-qira-rollout-mwc-2026/)",
        "\U0001f1e8\U0001f1f3 政策 | [武汉智能工厂奖励计划公示](https://jxj.wuhan.gov.cn/)",
        "\U0001f4ca 新评测 | [GPT-5.4 GDPval 83%，Excel建模87.3%](https://openai.com/index/introducing-gpt-5-4/)",
        "",
        "\U0001f4a1 **深度聚焦** \u2014 87.3%的Excel建模准确率意味着什么？",
        f"\u2192 AI从替代{LQ}辅助工作{RQ}到独立完成{LQ}核心工作{RQ}。**RPA厂商警惕\u2014\u2014AI直接操作桌面应用**",
    ])

    full_content = f"{heat_trend}\n\n---\n\n{sec1}\n\n---\n\n{sec2}\n\n---\n\n{sec3}\n\n---\n\n{sec4}\n\n---\n\n{sec5}"

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": "# \U0001f4e1 AI 日报（2026-03-08，周日）"},
            },
            {
                "blockId": "overview",
                "type": "content",
                "text": {"type": "kimMd", "content": full_content},
            },
            {"blockId": "div1", "type": "divider"},
            {
                "blockId": "footer",
                "type": "content",
                "text": {
                    "type": "kimMd",
                    "content": "*林克（沈浪的AI分身）\u00b7 AI洞察*",
                },
            },
            {
                "blockId": "buttons",
                "type": "action",
                "actions": [
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "\U0001f4c4 查看完整日报 >>"},
                        "style": "green",
                        "url": REPORT_URL,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plainText", "content": "了解AI洞察项目"},
                        "style": "blue",
                        "url": PROJECT_URL,
                    },
                ],
                "layout": "two",
            },
        ],
    }


async def main():
    card = build_card()
    print("Card v3.1 (with heat trend) built OK")

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
        resp = await client.post(
            f"{GATEWAY_URL}/openapi/v2/message/send",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            json={"username": "shenlang", "msgType": "mixCard", "mixCard": card},
        )
        result = resp.json()
        print(f"Result: {result}")
        if result.get("code") == 0:
            print("SUCCESS - card v3.1 sent to shenlang")
        else:
            print(f"FAILED: {result}")


if __name__ == "__main__":
    asyncio.run(main())
