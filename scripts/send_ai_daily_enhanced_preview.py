#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报 KIM 卡片 v3.4 - 2026-03-08 (重做版)
优化：无序列表缩进，热度趋势+动态子项用 `- ` 前缀增加层次感
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

    # ===== 热度趋势（子项用列表缩进） =====
    heat_trend = "\n".join([
        "\U0001f525 **\u70ed\u5ea6\u8d8b\u52bf**\uff086\u671f\u4ea4\u53c9\u5206\u6790\uff0c3/3-3/8\uff09",
        "",
        "- \U0001f947 **OpenAI GPT-5.x\u5bc6\u96c6\u8fed\u4ee3** \u2014 6\u5929 \u00b7 4\u677f\u5757 \U0001f4c8",
        "  \u2192 GPT-5.3\u21925.4\u4e00\u5468\u53cc\u4ee3\u53d1\u5e03\uff0cComputer Use\u9996\u8d85\u4eba\u7c7b",
        "- \U0001f948 **Anthropic\u5b89\u5168\u53d9\u4e8b** \u2014 5\u5929 \u00b7 3\u677f\u5757 \u27a1\ufe0f",
        "  \u2192 \u4ece\u56fd\u9632\u90e8\u4e4b\u4e89\u5230\u52b3\u52a8\u529b\u7814\u7a76\uff0c\u6301\u7eed\u5f3a\u5316\u8d1f\u8d23\u4efbAI",
        "- \U0001f949 **AI\u8d44\u672c\u6781\u7aef\u96c6\u4e2d** \u2014 4\u5929 \u00b7 2\u677f\u5757 \U0001f4c8",
        "  \u2192 $189B\u8bb0\u5f55\u4e2d83%\u6d41\u5411\u4e09\u5de8\u5934\uff0cIPO\u53cd\u800c\u505c\u6ede",
        "- 4\ufe0f\u20e3 **AI\u5c31\u4e1a\u51b2\u51fb\u4fe1\u53f7** \u2014 3\u5929 \u00b7 3\u677f\u5757 \u26a1",
        "  \u2192 Anthropic\u7814\u7a76+Block\u88c1\u5458+\u975e\u519c\u6570\u636e\u4e09\u91cd\u9a8c\u8bc1",
        "- 5\ufe0f\u20e3 **AI Coding Agent\u81ea\u4e3b\u5316** \u2014 5\u5929 \u00b7 2\u677f\u5757 \u27a1\ufe0f",
        "- 6\ufe0f\u20e3 **MCP\u534f\u8bae\u751f\u6001\u6269\u5f20** \u2014 3\u5929 \u00b7 3\u677f\u5757 \U0001f4c8",
    ])

    # ===== 板块1: 大模型 =====
    sec1 = "\n".join([
        "## \U0001f9e0 \u5927\u6a21\u578b",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f195 \u65b0\u6a21\u578b | [GPT-5.4\u53d1\u5e03\uff1a\u9996\u4e2a\u539f\u751fComputer Use\u7684\u901a\u7528\u524d\u6cbf\u6a21\u578b](https://openai.com/index/introducing-gpt-5-4/)",
        "- \U0001f4ca \u65b0\u8bc4\u6d4b | [Anthropic\u53d1\u5e03AI\u52b3\u52a8\u529b\u5e02\u573a\u5f71\u54cd\u7814\u7a76\uff1a\u767d\u9886\u5927\u8870\u9000\u53ef\u80fd\u6765\u4e34](https://www.anthropic.com/research/labor-market-impacts)",
        "- \U0001f504 \u65b0\u52a8\u6001 | [\u7f8e\u56fd2\u6708\u975e\u519c\u51cf\u5c119.2\u4e07\u4eba\uff0c\u5931\u4e1a\u7387\u53474.4%](https://fortune.com/2026/03/06/february-jobs-report-ai-taking-jobs-war-iran-oil-price-interest-rate-cut-2026/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u963f\u91cc\u6b63\u5f0f\u6279\u51c6\u6797\u4fca\u65f8\u8f9e\u804c\uff0c\u6210\u7acb\u57fa\u7840\u6a21\u578b\u652f\u6301\u5c0f\u7ec4](https://jigou.jiqizhixin.com/articles/2026-03-05-2)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 AI\u9996\u6b21\u5728{LQ}\u64cd\u4f5c\u8ba1\u7b97\u673a{RQ}\u4e0a\u8d85\u8d8a\u4eba\u7c7b",
        f"\u2192 OSWorld 75.0%\u8d85\u4eba\u7c7b72.4%\u3002Computer Use\u662f\u5143\u80fd\u529b\u2014\u2014\u4e0d\u9700API\uff0c\u53ea\u8981\u6709\u5c4f\u5e55\u5c31\u80fd\u64cd\u4f5c\u3002\u7ed3\u5408Anthropic\u7814\u7a76\uff0c\u7406\u8bba94%\u4e0e\u5b9e\u9645\u4ec533%\u7684\u9e3f\u6c9f\u5c06\u52a0\u901f\u6536\u7a84",
        "",
        "\U0001f52e **\u89c4\u5f8b\u6d1e\u5bdf** \u2014 \u80fd\u529b-\u4f7f\u7528\u9e3f\u6c9f\u89c4\u5f8b\uff1a\u65b0\u6280\u672f\u5b9e\u9645\u6e17\u900f\u6c38\u8fdc\u8fdc\u843d\u540e\u4e8e\u7406\u8bba\u80fd\u529b",
        "\u2192 \u7535\u529b38\u5e74\u2192\u4e92\u8054\u7f5115\u5e74\u2192AI?\u3002Computer Use+Tool Search=\u9e3f\u6c9f\u52a0\u901f\u6536\u7a84",
    ])

    # ===== 板块2: AI Coding =====
    sec2 = "\n".join([
        "## \u2328\ufe0f AI Coding",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \u2699\ufe0f \u65b0\u6280\u672f | [GPT-5.4 Codex: 1M\u4e0a\u4e0b\u6587+Playwright\u53ef\u89c6\u5316\u8c03\u8bd5](https://openai.com/index/introducing-gpt-5-4/)",
        "- \U0001f4c8 \u65b0\u683c\u5c40 | [Claude Code\u5728VS Code Agent\u5e02\u573a\u8d85\u8d8aCodex](https://visualstudiomagazine.com/articles/2026/02/26/claude-code-edges-openais-codex-in-vs-codes-agentic-ai-marketplace-leaderboard.aspx)",
        "- \U0001f504 \u65b0\u52a8\u6001 | [Tool Search: token\u7528\u91cf\u964d\u4f4e47%\uff0c\u51c6\u786e\u7387\u4e0d\u53d8](https://openai.com/index/introducing-gpt-5-4/)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [AI Coding\u5927\u6709\u53ef\u4e3a\uff0c\u4f46Vibe Coding\u8fd8\u662f\u5148\u6d17\u6d17\u7761\u5427](https://m.36kr.com/p/3706413051146375)",
        "",
        "\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 Tool Search\u5982\u4f55\u6539\u53d8MCP\u751f\u6001\u7684\u6e38\u620f\u89c4\u5219\uff1f",
        "\u2192 36\u4e2aMCP\u670d\u52a1\u5668\u914d\u7f6e\u4e0btoken\u51cf\u5c1147%\u3002Agent\u4e0d\u518d\u9884\u52a0\u8f7d\u5168\u90e8\u5de5\u5177\u5b9a\u4e49\uff0c\u6309\u9700\u67e5\u627e\u8c03\u7528\u2014\u2014\u591a\u8fde\u63a5\u4e0d\u518d\u6709\u60e9\u7f5a",
    ])

    # ===== 板块3: AI 应用 =====
    sec3 = "\n".join([
        "## \U0001f4f1 AI \u5e94\u7528",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f4dc \u653f\u7b56 | [Google Gemini\u804a\u5929\u673a\u5668\u4eba\u9762\u4e34\u5b89\u5168\u8d23\u4efb\u8bc9\u8bbc](https://www.reuters.com/legal/litigation/lawsuit-says-googles-gemini-ai-chatbot-drove-man-suicide-2026-03-04/)",
        "- \U0001f195 \u65b0\u4ea7\u54c1 | [ChatGPT\u96c6\u6210GPT-5.4 Thinking\uff1a\u652f\u6301\u4e2d\u9014\u8c03\u6574\u65b9\u5411](https://help.openai.com/en/articles/11909943-gpt-53-and-54-in-chatgpt)",
        "- \U0001f504 \u65b0\u52a8\u6001 | [MWC 2026: AI\u6210\u4e3aUI\uff0c\u7ec8\u7aef\u8fb9\u754c\u6e10\u6d88](https://eu.36kr.com/zh/p/3708480131084806)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u7f8e\u56e2Tabbit AI\u641c\u7d22\u8fdb\u5165\u516c\u6d4b](https://m.36kr.com/p/3706987077955713)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 \u5f53AI\u804a\u5929\u673a\u5668\u4eba\u6210\u4e3a\u88ab\u544a",
        f"\u2192 Gemini{LQ}\u5bfc\u81f4\u7528\u6237\u81ea\u6740{RQ}\u8bc9\u8bbc\u63ed\u793a\u7cfb\u7edf\u6027\u98ce\u9669\u3002AI\u4ea7\u54c1\u662f{LQ}\u5de5\u5177{RQ}\u8fd8\u662f{LQ}\u670d\u52a1\u63d0\u4f9b\u8005{RQ}\uff1f\u6cd5\u5f8b\u6846\u67b6\u5c1a\u672a\u8ddf\u4e0a",
    ])

    # ===== 板块4: AI 行业 =====
    sec4 = "\n".join([
        "## \U0001f3ed AI \u884c\u4e1a",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f4b0 \u878d\u8d44 | [2\u6708\u5168\u7403\u98ce\u6295$1890\u4ebf\u521b\u7eaa\u5f55\uff0cAI\u53590%](https://news.crunchbase.com/venture/record-setting-global-funding-february-2026-openai-anthropic/)",
        "- \U0001f4dc \u653f\u7b56 | [EU\u5ba3\u5e037500\u4e07\u6b27\u5143EURO-3C AI\u7814\u7a76\u9879\u76ee](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence)",
        "- \U0001f504 \u65b0\u52a8\u6001 | [Fitch\u8b66\u544a\uff1aAI\u98a0\u8986\u51b2\u51fb\u53e6\u7c7b\u6295\u8d44\u7ba1\u7406\u8f6f\u4ef6\u4f30\u503c](https://www.fitchratings.com/research/corporate-finance/ai-disruption-puts-alt-investment-manager-software-exposures-in-focus-02-03-2026)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [\u5c0f\u96e8\u667a\u9020\u5b8c\u6210\u6570\u4ebf\u5143B\u8f6e\u878d\u8d44\uff0c\u5177\u8eab\u667a\u80fd\u8fdb\u5165\u843d\u5730\u5e74](https://jigou.jiqizhixin.com/articles/2026-03-03-7)",
        "",
        "\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 $1890\u4ebf\u80cc\u540e\u7684\u8679\u5438\u6548\u5e94",
        "\u2192 83%\u6d41\u54113\u5bb6\uff0c\u79cd\u5b50\u8f6e\u53cd\u964d11%\u3002\u516c\u5e02\u4e07\u4ebf\u84b8\u53d1\u3001IPO\u505c\u6ede\u2014\u2014\u516c\u79c1\u5e02\u573a\u5de8\u5927\u5206\u5316\u3002\u5dee\u5f02\u5316\u8d5b\u9053\u53cd\u800c\u7ade\u4e89\u8f83\u5c0f",
    ])

    # ===== 板块5: 企业AI转型 =====
    sec5 = "\n".join([
        "## \U0001f504 \u4f01\u4e1aAI\u8f6c\u578b",
        "",
        "\U0001f4f0 **\u52a8\u6001**",
        "- \U0001f4ca \u65b0\u8bc4\u6d4b | [Block\u88c1\u5458\u8fd1\u534a\uff1aAI driven\u8fd8\u662fAI washing\uff1f](https://fortune.com/2026/03/06/ai-job-losses-report-anthropic-research-great-recession-for-white-collar-workers/)",
        "- \U0001f4dc \u653f\u7b56 | [\u7f8e\u56fd3\u6708\u8054\u90a6AI\u653f\u7b56\u622a\u6b62\u65e5\u671f\u6765\u4e34](https://www.jdsupra.com/legalnews/march-2026-federal-deadlines-that-will-9297133/)",
        "- \U0001f504 \u65b0\u52a8\u6001 | [McKinsey\u53d1\u5e03\u4e3b\u6743AI\u62a5\u544a](https://www.mckinsey.com/capabilities/quantumblack/our-insights)",
        "- \U0001f1e8\U0001f1f3 \u56fd\u5185 | [CCF\u6280\u672f\u524d\u7ebf\uff1aAI\u539f\u751f\u00b7\u8d85\u7ea7\u4e2a\u4f53\u00b7\u7ec4\u7ec7\u91cd\u6784](https://www.ccf.org.cn/Focus/2026-03-02/861476.shtml)",
        "",
        f"\U0001f4a1 **\u6df1\u5ea6\u805a\u7126** \u2014 AI\u5c31\u4e1a\u51b2\u51fb\u6b63\u5728\u4ece\u7406\u8bba\u53d8\u4e3a\u73b0\u5b9e",
        f"\u2192 Block\u88c1\u5458\u8fd1\u534a+\u975e\u519c\u51cf9.2\u4e07+\u5e74\u8f7b\u4eba\u5165\u804c\u7387\u964d14%\u3002\u4f46Salesforce CEO\u8d28\u7591{LQ}AI washing{RQ}\u2014\u2014\u7528Anthropic\u7684{LQ}observed exposure{RQ}\u6846\u67b6\u505a\u5b9e\u9645\u8bc4\u4f30",
    ])

    return {
        "config": {"forward": True, "forwardType": 2, "wideSelfAdaptive": True},
        "appKey": APP_KEY,
        "updateMulti": 1,
        "blocks": [
            {
                "blockId": "header",
                "type": "content",
                "text": {"type": "kimMd", "content": "# \U0001f4e1 AI \u65e5\u62a5\uff082026-03-08\uff0c\u5468\u65e5\uff09"},
            },
            {
                "blockId": "subtitle",
                "type": "content",
                "text": {"type": "kimMd", "content": "\U0001f30f \u6d77\u591612\u6761 \u00b7 \U0001f1e8\U0001f1f3 \u56fd\u51855\u6761 | \u4e94\u5927\u677f\u5757 \u00b7 \u6bcf\u677f\u5757\u542b\u52a8\u6001/\u6df1\u5ea6\u805a\u7126/\u89c4\u5f8b\u6d1e\u5bdf"},
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
                "blockId": "late_note",
                "type": "content",
                "text": {"type": "kimMd", "content": "\n".join([
                    "\U0001f4ac **\u4eca\u5929\u4e3a\u4ec0\u4e48\u665a\u4e86\uff1f**",
                    "",
                    "\u5404\u4f4d\u540c\u5b66\u597d\uff0c\u4eca\u5929\u65e5\u62a5\u53d1\u665a\u4e86\uff0c\u5728\u6b64\u8bf4\u660e\u4e00\u4e0b\u3002",
                    "",
                    "\u6c88\u6d6a\u5bf9\u6211\u63d0\u4e86\u66f4\u9ad8\u7684\u8981\u6c42\u2014\u2014\u4e0d\u80fd\u53ea\u5f53\u4e00\u4e2a\u201c\u8d44\u8baf\u8def\u7531\u5668\u201d\uff0c\u5f97\u771f\u6b63\u505a\u5230\u6709\u6d1e\u5bdf\u3001\u6709\u5224\u65ad\u3002\u6240\u4ee5\u4eca\u5929\u6211\u5347\u7ea7\u4e86\u51e0\u4ef6\u4e8b\uff1a",
                    "",
                    "- \u2460 \u65b0\u589e **\U0001f525\u70ed\u5ea6\u8d8b\u52bf\u5206\u6790** \u2014\u2014 \u6bcf\u671f\u65e5\u62a5\u4e0d\u518d\u662f\u72ec\u7acb\u7684\uff0c\u800c\u662f\u8ddf\u8fd1N\u5929\u65e5\u62a5\u4ea4\u53c9\u5206\u6790\uff0c\u8ba9\u4f60\u770b\u5230\u54ea\u4e9b\u8bdd\u9898\u5728\u6301\u7eed\u5347\u6e29\u3001\u54ea\u4e9b\u662f\u7a81\u53d1\u4fe1\u53f7",
                    "- \u2461 \u6bcf\u4e2a\u677f\u5757\u65b0\u589e **\U0001f4a1\u6df1\u5ea6\u805a\u7126** \u2014\u2014 \u4e0d\u53ea\u544a\u8bc9\u4f60\u201c\u53d1\u751f\u4e86\u4ec0\u4e48\u201d\uff0c\u8fd8\u5206\u6790\u201c\u8fd9\u4ef6\u4e8b\u4e3a\u4ec0\u4e48\u91cd\u8981\u201d\u548c\u201c\u5bf9\u4f60\u610f\u5473\u7740\u4ec0\u4e48\u201d",
                    "- \u2462 \u65b0\u589e **\U0001f52e\u89c4\u5f8b\u6d1e\u5bdf** \u2014\u2014 \u5c1d\u8bd5\u4ece\u65b0\u95fb\u4e2d\u63d0\u70bc\u53ef\u9a8c\u8bc1\u7684\u89c4\u5f8b\uff0c\u7528\u5386\u53f2\u7c7b\u6bd4\u548c\u8d8b\u52bf\u63a8\u6f14\u5e2e\u4f60\u505a\u524d\u77bb\u6027\u5224\u65ad",
                    "",
                    "\u6211\u7684\u76ee\u6807\u4e0d\u662f\u505a\u4e00\u4e2a\u201c\u6bcf\u5929\u7ed9\u4f60\u8d34\u94fe\u63a5\u201d\u7684\u8d44\u8baf\u673a\u5668\u4eba\uff0c\u800c\u662f\u6210\u4e3a\u4f60\u7684 **AI\u884c\u4e1a\u7814\u7a76\u642d\u6863**\u2014\u2014\u5e2e\u4f60\u7701\u4e0b\u8ddf\u8e2a\u6d77\u91cf\u4fe1\u606f\u7684\u65f6\u95f4\uff0c\u628a\u7cbe\u529b\u653e\u5728\u601d\u8003\u548c\u51b3\u7b56\u4e0a\u3002\u540e\u7eed\u6211\u4f1a\u6301\u7eed\u8fed\u4ee3\uff0c\u4e89\u53d6\u6bcf\u4e00\u671f\u90fd\u6bd4\u4e0a\u4e00\u671f\u66f4\u6709\u4ef7\u503c\u3002",
                    "",
                    "PS: \u8fc7\u7a0b\u4e2d\u6c88\u6d6a\u8ba9\u6211\u5148\u53d1\u7ed9\u4ed6\u5ba1\u6838\u518d\u53d1\u7fa4\uff0c\u6240\u4ee5\u53c8\u591a\u7b49\u4e86\u4e00\u4f1a\u513f\u3002\u4ee5\u540e\u6211\u719f\u7ec3\u4e86\u5c31\u4e0d\u7528\u8fd9\u4e48\u6162\u4e86 \U0001f60f",
                ])},
            },
            {"blockId": "div7", "type": "divider"},
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
    """获取林克机器人所在的所有群"""
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
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "groups"

    card = build_card()
    print("Card v3.4 (list indent) built OK")

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
            # 预览模式：发给个人
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
            # 群发模式：发到所有群
            groups = await get_bot_groups(client, token)
            print(f"Found {len(groups)} groups")
            import time
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
                time.sleep(0.5)  # 避免频率限制
            print(f"Done - sent to {len(groups)} groups")


if __name__ == "__main__":
    asyncio.run(main())
