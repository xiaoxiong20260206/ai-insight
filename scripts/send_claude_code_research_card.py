#!/usr/bin/env python3
"""
Claude Code 深度调研 KIM 卡片推送脚本
=====================================
将 Claude Code 深度调研卡片推送到 KIM（私发预览 / 群发）

使用方式:
  python3 scripts/send_claude_code_research_card.py --preview      # 私发沈浪预览
  python3 scripts/send_claude_code_research_card.py --to-groups    # 群发（硬编码3个群）
  python3 scripts/send_claude_code_research_card.py --dry-run      # 试运行

作者: 林克 (沈浪的AI分身)
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kim_client import (
    KimConfig, get_access_token,
    send_to_user, send_to_all_groups
)

KimConfig.validate()

APP_KEY = KimConfig.APP_KEY

RESEARCH_URL = "https://xiaoxiong20260206.github.io/ai-insight/02-deep-research/topics/claude-code-source-analysis.html"
HOMEPAGE_URL = "https://xiaoxiong20260206.github.io/ai-insight/"
KIM_DOC_URL  = "https://INTERNAL_DOCS/d/home/fcACLzJsWsUleOZk0PAkdFrRP"


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



async def main():
    parser = argparse.ArgumentParser(description="Claude Code 深度调研卡片推送")
    parser.add_argument("--preview", action="store_true", help="私发给自己预览")
    parser.add_argument("--to-user", type=str, help="发送到指定用户")
    parser.add_argument("--to-groups", action="store_true", help="群发（硬编码3个群）")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际发送")
    args = parser.parse_args()

    if args.preview:
        args.to_user = "shenlang"
    if not args.to_user and not args.to_groups:
        print("请指定发送目标: --preview 或 --to-groups")
        return

    print("\U0001f50d Claude Code 深度调研卡片推送")
    if args.dry_run:
        print("   [DRY-RUN 模式]")
    print("=" * 55)

    print("\U0001f3a8 构建卡片...")
    card = build_card()
    print("\u2705 卡片构建完成")

    print("\U0001f511 获取 Token...")
    try:
        token = await get_access_token()
        print("\u2705 Token 获取成功")
    except Exception as e:
        print(f"\u274c Token 获取失败: {e}")
        return

    if args.to_user:
        print(f"\n\U0001f4e4 发送给用户: {args.to_user}")
        ok = await send_to_user(token, args.to_user, card, args.dry_run)
        if ok:
            print("\u2705 已私发成功！请检查 KIM 消息")
            print(f"\U0001f4c4 KIM Doc 文章：{KIM_DOC_URL}")
            print(f"\U0001f310 HTML 报告  ：{RESEARCH_URL}")
        else:
            print("\u274c 发送失败")

    if args.to_groups:
        print("\n\U0001f4e4 群发到所有群（硬编码3个群）...")
        success_count, fail_count = await send_to_all_groups(token, card, args.dry_run)
        print("\n" + "=" * 55)
        print(f"\U0001f4ca 完成！成功: {success_count}，失败: {fail_count}")
        if fail_count > 0:
            print("\u26a0\ufe0f  失败群请确认后重发")


if __name__ == "__main__":
    asyncio.run(main())
