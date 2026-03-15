#!/usr/bin/env python3
"""
AI日报质量门脚本 (Quality Gate)
================================
集中所有P0检查点，一次性验证日报完整性和正确性

使用方式:
  python scripts/daily_quality_gate.py                    # 检查今天的日报
  python scripts/daily_quality_gate.py 2026-03-11         # 检查指定日期
  python scripts/daily_quality_gate.py 2026-03-11 --fix   # 检查并尝试修复部分问题

检查项 (15项):
  1. JSON数据文件存在性
  2. 中文引号检测
  3. 链接有效性 (禁止#占位符 + URL真实性抽检)
  4. 内容非空检查
  5. ⭐ [v2.0新增] 时效性验证 (发布日期在时间窗口内)
  6. ⭐ [v8.0新增] 日期篡改检测 (快照对比+可疑模式识别)
  7. ⭐ [v8.0新增] 封闭平台链接合规 (禁mp.weixin临时+禁搜狗跳转)
  8. ⭐ [v3.0新增] 板块分类验证
  9. ⭐ [v4.0新增] 地区分类验证
  10. ⭐ [v3.0新增] 跨天去重
  11. ⭐ [v5.0新增] 信息源多样性 (微信覆盖>=2 + 单源集中度<=40%)
  12. ⭐ [v2.0新增] HTML链接规范 (target="_blank" + 无#占位)
  13. MD/HTML文件存在性
  14. 6处联动更新检查
  15. 外部版同步检查

作者: 林克 (沈浪的AI分身)
版本: v8.0.0 (2026-03-15)

v8.0更新:
- 新增日期篡改检测 (check_date_tampering) — 双保险: 快照对比+可疑模式识别
- 新增封闭平台链接合规 (check_closed_platform_urls) — Step 2.7脚本化
- 经验来源: 2026-03-15教训 — source日期篡改绕过时效检查=P0违规

v2.0更新:
- 新增时效性验证检查 (check_date_window)
- 新增HTML链接规范检查 (check_html_links)
- 时效性违规阻断日报发布
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, List, Dict, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data"
DAILY_REPORTS_PATH = PROJECT_ROOT / "01-daily-reports"
PUBLIC_PATH = PROJECT_ROOT / "public"
EXTERNAL_PATH = PROJECT_ROOT.parent / "ai-insight-public"

# 检查结果
class CheckResult:
    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False, severity: str = "error"):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable
        self.severity = severity  # "error" | "warning"
    
    def __str__(self):
        if self.passed:
            status = "✅"
        elif self.severity == "warning":
            status = "⚠️"
        else:
            status = "❌"
        fix_hint = " (可修复)" if not self.passed and self.fixable else ""
        return f"{status} {self.name}: {self.message}{fix_hint}"


def check_json_exists(date_str: str) -> CheckResult:
    """检查1: JSON数据文件存在性"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if json_path.exists():
        return CheckResult("JSON文件", True, f"存在 ({json_path.name})")
    else:
        return CheckResult("JSON文件", False, f"不存在: {json_path}", fixable=True)


def check_chinese_quotes(date_str: str) -> CheckResult:
    """检查2: JSON语法层面的中文引号检测（只检测key/value外层引号）"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("中文引号", False, "JSON文件不存在，跳过")
    
    try:
        content = json_path.read_text(encoding="utf-8")
        
        # 尝试解析JSON，如果成功说明语法正确
        try:
            json.loads(content)
            return CheckResult("中文引号", True, "JSON语法正确")
        except json.JSONDecodeError as e:
            # 检查错误信息是否与中文引号相关
            if '"' in content or '"' in content:
                # 检查是否在JSON key/value位置使用了中文引号
                # 模式: 中文引号后面紧跟字母/数字/冒号，或前面紧跟冒号/逗号
                import re
                pattern = r'[""]\s*[:\[\{,]|[:\[\{,]\s*[""]'
                if re.search(pattern, content):
                    return CheckResult("中文引号", False, f"JSON语法中使用了中文引号: {e}", fixable=True)
            return CheckResult("中文引号", False, f"JSON解析失败: {e}", fixable=True)
    except Exception as e:
        return CheckResult("中文引号", False, f"读取失败: {e}")


def check_link_validity(date_str: str) -> CheckResult:
    """检查3: 链接有效性 (禁止#占位符 + v7.0 URL真实性抽检)"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("链接有效", False, "JSON文件不存在，跳过")
    
    try:
        import urllib.request
        import random
        
        data = json.loads(json_path.read_text(encoding="utf-8"))
        invalid_count = 0
        invalid_examples = []
        all_urls = []
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    url = item.get('url', '')
                    if url == '#' or (url and not url.startswith('http')):
                        invalid_count += 1
                        if len(invalid_examples) < 3:
                            invalid_examples.append(f"{item.get('title', '')[:20]}→")
                    elif url.startswith('http'):
                        all_urls.append((url, item.get('title', '')[:30]))
        
        # v7.0: URL真实性抽检 — 随机抽取最多3个URL做HTTP HEAD验证
        unreachable = []
        if all_urls:
            sample = random.sample(all_urls, min(3, len(all_urls)))
            for url, title in sample:
                try:
                    req = urllib.request.Request(url, method='HEAD')
                    req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight QualityGate/7.0)')
                    resp = urllib.request.urlopen(req, timeout=10)
                    if resp.status >= 400:
                        unreachable.append(f"{title}({resp.status})")
                except Exception as e:
                    # 某些站点拒绝HEAD请求，尝试GET
                    try:
                        req = urllib.request.Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight QualityGate/7.0)')
                        resp = urllib.request.urlopen(req, timeout=10)
                        if resp.status >= 400:
                            unreachable.append(f"{title}({resp.status})")
                    except Exception:
                        unreachable.append(f"{title}(不可达)")
        
        issues = []
        if invalid_count > 0:
            examples = ", ".join(invalid_examples)
            issues.append(f"{invalid_count}个无效链接: {examples}")
        if unreachable:
            issues.append(f"抽检不可达: {', '.join(unreachable)}")
        
        if issues:
            return CheckResult("链接有效", False, "; ".join(issues) + " (可修复)", fixable=True)
        return CheckResult("链接有效", True, f"所有链接有效(抽检{min(3, len(all_urls))}个URL可达)")
    except Exception as e:
        return CheckResult("链接有效", False, f"检查失败: {e}")


def check_content_nonempty(date_str: str) -> CheckResult:
    """检查4: 内容非空检查"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("内容非空", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        tabs = data.get("tabs", [])
        total_news = sum(
            len(tab.get("news", {}).get("overseas", [])) + 
            len(tab.get("news", {}).get("china", []))
            for tab in tabs
        )
        
        if total_news == 0:
            return CheckResult("内容非空", False, "新闻条目为0")
        return CheckResult("内容非空", True, f"{len(tabs)}板块, {total_news}条新闻")
    except Exception as e:
        return CheckResult("内容非空", False, f"检查失败: {e}")


def check_date_window(date_str: str) -> CheckResult:
    """检查5: ⭐ [v2.0新增] 时效性验证 - 新闻发布日期必须在时间窗口内
    
    规则: N日日报只收录 N-1日08:00 ~ N日08:00 之间发布的新闻
    
    检查方法:
    1. 解析source字段中的日期 (格式: "来源 · 3月10日" 或 "来源 · 2026-03-10")
    2. 检查日期是否在时间窗口内
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("时效性", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        report_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 时间窗口: N-1日08:00 ~ N日08:00
        # 简化为: 发布日期必须是 N日 或 N-1日
        valid_dates = [
            report_date.strftime("%m月%d日"),                    # 3月11日
            (report_date - timedelta(days=1)).strftime("%m月%d日"),  # 3月10日
            report_date.strftime("%Y-%m-%d"),                    # 2026-03-11
            (report_date - timedelta(days=1)).strftime("%Y-%m-%d"),  # 2026-03-10
            f"{report_date.month}月{report_date.day}日",         # 3月11日 (无前导0)
            f"{(report_date - timedelta(days=1)).month}月{(report_date - timedelta(days=1)).day}日",  # 3月10日
        ]
        # 去除前导0的版本
        valid_dates.extend([
            f"{report_date.month}月{report_date.day}日",
            f"{report_date.month}月{report_date.day - 1}日" if report_date.day > 1 else "",
        ])
        valid_dates = [d for d in valid_dates if d]  # 过滤空字符串
        
        out_of_window = []
        total_checked = 0
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    source = item.get('source', '')
                    total_checked += 1
                    
                    # 提取日期部分 (格式: "来源 · 日期")
                    if '·' in source:
                        date_part = source.split('·')[-1].strip()
                    else:
                        date_part = source
                    
                    # 检查是否在有效日期范围内
                    is_valid = any(valid_date in date_part for valid_date in valid_dates)
                    
                    if not is_valid and date_part:
                        # 尝试解析日期判断是否过时
                        # 匹配 "X月Y日" 格式
                        match = re.search(r'(\d+)月(\d+)日', date_part)
                        if match:
                            month, day = int(match.group(1)), int(match.group(2))
                            try:
                                news_date = datetime(report_date.year, month, day)
                                days_diff = (report_date - news_date).days
                                if days_diff > 1:  # 超过时间窗口
                                    title = item.get('title', '')[:25]
                                    out_of_window.append(f"{title}...({date_part})")
                            except ValueError:
                                pass
        
        if out_of_window:
            examples = "; ".join(out_of_window[:3])
            suffix = f" (+{len(out_of_window)-3}条)" if len(out_of_window) > 3 else ""
            return CheckResult(
                "时效性", False, 
                f"⚠️ {len(out_of_window)}条新闻超出时间窗口: {examples}{suffix}",
                fixable=False,
                severity="error"
            )
        
        return CheckResult("时效性", True, f"全部{total_checked}条新闻在时间窗口内")
    except Exception as e:
        return CheckResult("时效性", False, f"检查失败: {e}")


def check_board_classification(date_str: str) -> CheckResult:
    """检查6: ⭐ [v3.0新增] 板块分类验证 - 新闻是否被放到了正确的板块
    
    规则（基于 daily-report.md L439-466 板块定义）:
    - 大模型: 模型训练/推理/架构/Benchmark/蒸馏/CVPR等学术会议论文
    - AI Coding: IDE/代码补全/代码审查/代码生成/DevOps
    - AI 应用: 面向终端用户的产品/Workspace/Agent平台/社交
    - AI 行业: 投融资/算力基建/行业会议/人事变动/开源生态
    - 企业AI转型: 企业落地/政策法规/安全合规/军事化/监管
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("板块分类", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        # 板块关键词映射 (tab index → 板块名 → 典型关键词)
        board_keywords = {
            0: {  # 大模型
                "name": "大模型",
                "positive": ["模型", "benchmark", "训练", "推理", "蒸馏", "CVPR", "NeurIPS", "ICML", "ICLR",
                            "参数", "token", "多模态", "视觉", "3D", "扩散", "生成", "开源模型",
                            "Foundation Model", "架构", "注意力", "Transformer"],
                "negative": ["融资", "收购", "估值", "军事", "法规", "IDE", "代码补全", "Cursor",
                            "Agent", "个人Agent", "用户", "产品", "App"]
            },
            1: {  # AI Coding
                "name": "AI Coding",
                "positive": ["代码", "编程", "IDE", "Cursor", "Copilot", "Code Review", "DevOps",
                            "代码生成", "代码审查", "代码补全", "编译", "debug", "开发工具"],
                "negative": ["融资", "军事", "办公", "Workspace", "模型训练", "CVPR", "3D"]
            },
            2: {  # AI 应用
                "name": "AI 应用",
                "positive": ["用户", "产品", "App", "Workspace", "办公", "社交", "Agent",
                            "Agent平台", "个人Agent", "Manus", "OpenClaw", "Gemini", "ChatGPT",
                            "搜索", "翻译", "客服", "助手", "Perplexity", "Character"],
                "negative": ["融资", "军事", "模型训练", "CVPR", "benchmark"]
            },
            3: {  # AI 行业
                "name": "AI 行业",
                "positive": ["融资", "投资", "估值", "收购", "IPO", "算力", "数据中心", "芯片",
                            "GTC", "会议", "峰会", "圆桌", "开源生态", "人事", "离职", "创业"],
                "negative": ["军事", "法规", "监管", "安全警示"]
            },
            4: {  # 企业AI转型
                "name": "企业AI转型",
                "positive": ["企业", "落地", "政策", "法规", "监管", "安全", "军事", "军方",
                            "合规", "伦理", "红线", "诉讼", "国防", "CNCERT"],
                "negative": ["融资", "模型训练", "IDE"]
            }
        }
        
        suspects = []
        
        for tab_idx, tab in enumerate(data.get("tabs", [])):
            if tab_idx not in board_keywords:
                continue
            board = board_keywords[tab_idx]
            
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    title = item.get('title', '')
                    finding = item.get('details', {}).get('finding', '')
                    text = f"{title} {finding}"
                    
                    # 检查: 如果匹配了其他板块的positive关键词 比当前板块更多
                    current_score = sum(1 for kw in board["positive"] if kw in text)
                    
                    for other_idx, other_board in board_keywords.items():
                        if other_idx == tab_idx:
                            continue
                        other_score = sum(1 for kw in other_board["positive"] if kw in text)
                        
                        # 如果另一个板块匹配得更好，且当前板块的negative关键词命中
                        neg_hit = any(kw in text for kw in board.get("negative", []))
                        if other_score > current_score and neg_hit:
                            suspects.append(
                                f"[{board['name']}→{other_board['name']}?] {title[:30]}..."
                            )
                            break
        
        if suspects:
            examples = "; ".join(suspects[:3])
            return CheckResult(
                "板块分类", False,
                f"⚠️ {len(suspects)}条新闻可能分类错误: {examples}",
                fixable=False,
                severity="warning"
            )
        
        return CheckResult("板块分类", True, "所有新闻板块分类合理")
    except Exception as e:
        return CheckResult("板块分类", False, f"检查失败: {e}")


def check_region_classification(date_str: str) -> CheckResult:
    """检查6b: ⭐ [v4.0新增] 地区分类验证 - overseas/china是否正确
    
    规则（按公司/机构总部所在地分类，不按新闻来源语言分类）:
    - overseas(海外): 总部在中国大陆以外的公司/机构/组织
    - china(国内): 总部在中国大陆的公司/机构/组织
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("地区分类", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        # 已知公司/机构→地区映射（持续扩充）
        overseas_keywords = [
            # 大模型公司
            "OpenAI", "Anthropic", "Google", "DeepMind", "Meta", "Microsoft",
            "Apple", "Amazon", "AWS", "xAI", "Grok",
            "Mistral", "Cohere", "Stability", "Midjourney", "Runway",
            # AI Coding
            "Cursor", "GitHub", "Copilot", "Vercel", "Hugging Face",
            "Replit", "Bolt", "Windsurf", "Codeium", "Devin", "Cognition",
            # AI应用/Agent
            "Manus", "Perplexity", "Character.AI", "Inflection", "Notion",
            "OpenClaw",
            # 芯片/硬件
            "NVIDIA", "英伟达", "AMD", "Intel", "Qualcomm", "ARM",
            "Tesla", "特斯拉",
            # 行业/政策
            "METR", "FDA", "EU", "欧盟", "GTC", "GDC",
            # 消费电子
            "Samsung", "三星", "Sony", "索尼", "Toyota", "丰田",
            # AI基础设施
            "Databricks", "Snowflake", "Scale AI", "Together AI",
            "Salesforce", "Adobe", "Palantir",
            # AI框架
            "LangChain", "LlamaIndex",
            # 知名人物
            "Simon Willison", "Andrej Karpathy", "Sam Altman",
        ]
        
        china_keywords = [
            # 互联网巨头
            "百度", "阿里", "腾讯", "字节", "华为", "小米", "OPPO", "vivo",
            "美团", "京东", "拼多多", "滴滴", "蚂蚁", "网易", "荣耀",
            # 家电/制造
            "海尔", "格力", "联想", "比亚迪", "大疆", "商汤", "旷视",
            # AI大模型
            "DeepSeek", "深度求索", "幻方量化", "智谱", "Moonshot", "月之暗面", "Kimi",
            "零一万物", "昆仑万维", "科大讯飞", "通义", "文心",
            "阶跃星辰", "StepFun", "MiniMax", "百川智能", "面壁智能",
            "智源研究院", "BAAI",
            # AI Coding
            "Trae", "通义灵码", "CodeGeeX",
            # 应用/平台
            "闲鱼", "淘宝", "天猫", "支付宝", "微信", "抖音", "快手",
            "小红书", "B站", "哔哩哔哩", "WPS", "金山",
            # 车企AI
            "蔚来", "理想", "小鹏", "极氪", "吉利",
            # 媒体/会议
            "新华网", "人民网", "央视", "CCTV", "中国", "国内",
            "AWE", "WAIC", "世界人工智能大会",
        ]
        
        suspects = []
        
        for tab_idx, tab in enumerate(data.get("tabs", [])):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    title = item.get('title', '')
                    source = item.get('source', '')
                    text = f"{title} {source}"
                    
                    # 检测: overseas新闻是否包含china关键词
                    if region == 'overseas':
                        china_hits = [kw for kw in china_keywords if kw in text]
                        overseas_hits = [kw for kw in overseas_keywords if kw in text]
                        if china_hits and not overseas_hits:
                            suspects.append(
                                f"[overseas→china?] {title[:35]}... (命中: {', '.join(china_hits[:2])})"
                            )
                    
                    # 检测: china新闻是否包含overseas关键词
                    elif region == 'china':
                        overseas_hits = [kw for kw in overseas_keywords if kw in text]
                        china_hits = [kw for kw in china_keywords if kw in text]
                        if overseas_hits and not china_hits:
                            suspects.append(
                                f"[china→overseas?] {title[:35]}... (命中: {', '.join(overseas_hits[:2])})"
                            )
        
        if suspects:
            examples = "; ".join(suspects[:3])
            return CheckResult(
                "地区分类", False,
                f"⚠️ {len(suspects)}条新闻可能地区分类错误: {examples}",
                fixable=False,
                severity="warning"
            )
        
        return CheckResult("地区分类", True, "所有新闻地区分类合理")
    except Exception as e:
        return CheckResult("地区分类", False, f"检查失败: {e}")


def check_cross_day_dedup(date_str: str) -> CheckResult:
    """检查7: ⭐ [v3.0新增] 跨天去重+同报去重验证
    
    规则:
    1. 同一条新闻不应在连续3天日报中重复出现（旧闻三连报）
    2. 同一条新闻不应在同一天日报的不同板块中重复出现
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("去重", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        report_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 1. 收集当天所有新闻标题和URL
        current_items = []
        for tab_idx, tab in enumerate(data.get("tabs", [])):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    current_items.append({
                        "title": item.get('title', ''),
                        "url": item.get('url', ''),
                        "tab": tab_idx
                    })
        
        issues = []
        
        # 2. 同报去重: 检查同一URL在不同tab中出现
        url_tabs = {}
        for ci in current_items:
            url = ci["url"]
            if url and url in url_tabs:
                issues.append(f"同报重复: {ci['title'][:20]}...(出现在tab{url_tabs[url]}和tab{ci['tab']})")
            elif url:
                url_tabs[url] = ci["tab"]
        
        # 3. 跨天去重: 检查前3天的日报
        prev_titles = set()
        for days_back in range(1, 4):
            prev_date = report_date - timedelta(days=days_back)
            prev_path = DATA_PATH / f"daily-content-{prev_date.strftime('%Y-%m-%d')}.json"
            if prev_path.exists():
                try:
                    prev_data = json.loads(prev_path.read_text(encoding="utf-8"))
                    for tab in prev_data.get("tabs", []):
                        for region in ['overseas', 'china']:
                            for item in tab.get('news', {}).get(region, []):
                                prev_titles.add(item.get('title', '').strip())
                except Exception:
                    pass
        
        # 检查当天新闻是否与前3天重复
        for ci in current_items:
            title = ci["title"].strip()
            if title and title in prev_titles:
                issues.append(f"跨天重复: {title[:25]}...")
        
        # 模糊匹配: 标题相似度 > 80% (简化版：提取关键实体比较)
        for ci in current_items:
            title = ci["title"].strip()
            for pt in prev_titles:
                # 去掉来源和日期后比较核心内容
                core_current = re.sub(r'[\[\]|·\d月日年]', '', title)
                core_prev = re.sub(r'[\[\]|·\d月日年]', '', pt)
                if len(core_current) > 10 and len(core_prev) > 10:
                    # 简单Jaccard相似度
                    set_c = set(core_current)
                    set_p = set(core_prev)
                    intersection = set_c & set_p
                    union = set_c | set_p
                    if union and len(intersection) / len(union) > 0.75:
                        if title not in prev_titles:  # 排除精确匹配已报告的
                            issues.append(f"疑似旧闻: {title[:25]}...")
                            break
        
        if issues:
            # 去重issues
            unique_issues = list(dict.fromkeys(issues))
            examples = "; ".join(unique_issues[:3])
            suffix = f" (+{len(unique_issues)-3}条)" if len(unique_issues) > 3 else ""
            return CheckResult(
                "去重", False,
                f"⚠️ {len(unique_issues)}处重复: {examples}{suffix}",
                fixable=False,
                severity="warning"
            )
        
        return CheckResult("去重", True, f"无重复 (当天{len(current_items)}条 vs 前3天{len(prev_titles)}条)")
    except Exception as e:
        return CheckResult("去重", False, f"检查失败: {e}")


def check_source_diversity(date_str: str) -> CheckResult:
    """检查X: [v5.0新增] 信息源多样性检查（含微信公众号覆盖）
    
    规则:
    1. 微信公众号覆盖: 新闻条目中至少2条来自或引用微信公众号
       (url含 mp.weixin.qq.com / weixin.sogou.com，或 source 标注"微信")
    2. 信息源集中度: 单一域名占比不超过40%
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("信息源多样性", False, "JSON数据文件不存在", severity="warning")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        # 收集所有新闻条目
        all_items = []
        for tab in data.get("tabs", []):
            news = tab.get("news", {})
            for region in ["overseas", "china"]:
                for item in news.get(region, []):
                    all_items.append(item)
        
        if not all_items:
            return CheckResult("信息源多样性", False, "无新闻条目", severity="warning")
        
        # --- 检查1: 微信公众号覆盖 ---
        weixin_direct = 0    # URL直接指向微信文章
        weixin_crossref = 0  # source字段提到微信（交叉引用）
        for item in all_items:
            url = item.get("url", "")
            source = item.get("source", "")
            
            # 直接引用：URL指向微信
            if "mp.weixin.qq.com" in url or "weixin.sogou.com" in url:
                weixin_direct += 1
            # 交叉引用：source字段提到微信但URL不是微信
            elif "微信" in source or "公众号" in source:
                weixin_crossref += 1
        
        # --- 检查2: 信息源集中度 ---
        from urllib.parse import urlparse
        domain_counts: Dict[str, int] = {}
        for item in all_items:
            url = item.get("url", "")
            try:
                domain = urlparse(url).netloc
                if domain:
                    # 统一到主域名 (去掉www/eu等前缀)
                    parts = domain.split(".")
                    if len(parts) > 2:
                        domain = ".".join(parts[-2:])
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except Exception:
                pass
        
        total = len(all_items)
        issues = []
        
        # 微信覆盖不足：直接引用微信文章 < 2 篇
        weixin_total = weixin_direct + weixin_crossref
        if weixin_direct < 2:
            if weixin_crossref > 0:
                issues.append(
                    f"微信公众号直接引用{weixin_direct}条(交叉引用{weixin_crossref}条)，"
                    f"建议将优质公众号文章作为主要信源而非仅背景参考"
                )
            else:
                issues.append(f"微信公众号覆盖为0(要求>=2条直接引用)")
        
        # 信息源集中度
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            ratio = count / total
            if ratio > 0.4:
                issues.append(f"{domain}占比{ratio:.0%}({count}/{total}条)过高")
        
        if issues:
            detail = "; ".join(issues)
            return CheckResult("信息源多样性", False, detail, severity="warning")
        
        # 构建通过消息
        domain_summary = ", ".join(f"{d}({c})" for d, c in 
                                   sorted(domain_counts.items(), key=lambda x: -x[1])[:5])
        weixin_msg = f"微信直引{weixin_direct}+交叉{weixin_crossref}"
        return CheckResult(
            "信息源多样性", True, 
            f"{weixin_msg}, Top域名: {domain_summary}"
        )
    except Exception as e:
        return CheckResult("信息源多样性", False, f"检查失败: {e}", severity="warning")


def check_html_links(date_str: str) -> CheckResult:
    """检查6: ⭐ [v2.0新增] HTML链接规范
    
    规则:
    1. 所有外部链接必须有 target="_blank"
    2. 禁止 href="#" 占位符
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    html_path = DAILY_REPORTS_PATH / month_str / f"{date_str}-v3.html"
    
    if not html_path.exists():
        return CheckResult("HTML链接", False, "HTML文件不存在，跳过", severity="warning")
    
    try:
        content = html_path.read_text(encoding="utf-8")
        
        issues = []
        
        # 检查 href="#" 占位符
        hash_links = len(re.findall(r'href="#"', content))
        if hash_links > 0:
            issues.append(f"{hash_links}个#占位符")
        
        # 检查外部链接是否有 target="_blank"
        # 匹配 <a href="http... 但没有 target="_blank"
        external_links = re.findall(r'<a\s+href="https?://[^"]+"\s*>', content)
        missing_target = [link for link in external_links if 'target=' not in link]
        if missing_target:
            issues.append(f"{len(missing_target)}个链接缺少target")
        
        if issues:
            return CheckResult("HTML链接", False, ", ".join(issues), fixable=True)
        
        # 统计正确链接数
        correct_links = len(re.findall(r'target="_blank"', content))
        return CheckResult("HTML链接", True, f"{correct_links}个外部链接格式正确")
    except Exception as e:
        return CheckResult("HTML链接", False, f"检查失败: {e}")


def check_md_html_exists(date_str: str) -> CheckResult:
    """检查7: MD/HTML文件存在性"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    month_dir = DAILY_REPORTS_PATH / month_str
    
    md_file = month_dir / f"{date_str}.md"
    html_file = month_dir / f"{date_str}-v3.html"
    redirect_file = month_dir / f"{date_str}.html"
    
    missing = []
    if not md_file.exists():
        missing.append("MD")
    if not html_file.exists():
        missing.append("HTML(-v3)")
    if not redirect_file.exists():
        missing.append("HTML(跳转)")
    
    if missing:
        return CheckResult("文件存在", False, f"缺失: {', '.join(missing)}", fixable=True)
    return CheckResult("文件存在", True, "MD+HTML+跳转页均存在")


def check_six_locations(date_str: str) -> CheckResult:
    """检查8: 6处联动更新检查"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    issues = []
    
    # 1. 日报索引页 (01-daily-reports/index.html)
    index_file = DAILY_REPORTS_PATH / "index.html"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        if date_str not in content:
            issues.append("日报索引页未更新")
    
    # 2. 首页 (index.html) - 检查reportsData
    homepage = PROJECT_ROOT / "index.html"
    if homepage.exists():
        content = homepage.read_text(encoding="utf-8")
        if date_str not in content:
            issues.append("首页日历数据未更新")
    
    if issues:
        return CheckResult("6处联动", False, ", ".join(issues), fixable=True)
    return CheckResult("6处联动", True, "首页+索引页均已更新")


def check_external_sync(date_str: str) -> CheckResult:
    """检查9: 外部版同步检查"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    
    # 检查public目录
    public_html = PUBLIC_PATH / "01-daily-reports" / month_str / f"{date_str}.html"
    
    # 检查外部仓库
    external_html = EXTERNAL_PATH / "01-daily-reports" / month_str / f"{date_str}.html"
    
    issues = []
    if not public_html.exists():
        issues.append("public/未同步")
    if EXTERNAL_PATH.exists() and not external_html.exists():
        issues.append("外部仓库未同步")
    
    if issues:
        return CheckResult("外部同步", False, ", ".join(issues), fixable=True)
    
    # 如果外部仓库不存在，只检查public
    if not EXTERNAL_PATH.exists():
        if public_html.exists():
            return CheckResult("外部同步", True, "public/已同步 (外部仓库不存在)")
    
    return CheckResult("外部同步", True, "public/+外部仓库均已同步")


def check_date_tampering(date_str: str) -> CheckResult:
    """检查14: [v8.0新增] source日期篡改检测
    
    双保险机制:
    1. 可疑模式识别（独立于orchestrator，永远生效）
       - 检测"X月Y日热议/持续/最新"等软化过时日期的常见模式
       - 仅在解析出的日期超出时间窗口时触发（窗口内的"热议"标注合法）
    2. 快照对比（仅在orchestrator模式下生效）
       - 对比Step 2完成时的source快照，发现未经授权的修改
    
    经验来源: 2026-03-15教训 — Agent将source日期从"3月10日"改为"3月14日热议"
    绕过时效性检查。本检查让这种绕过行为不再可能。
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("日期篡改", True, "JSON文件不存在，跳过")
    
    try:
        import hashlib
        
        data = json.loads(json_path.read_text(encoding="utf-8"))
        report_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 有效日期范围: N-1日 和 N日
        valid_days = {report_date.day, (report_date - timedelta(days=1)).day}
        valid_months = {report_date.month, (report_date - timedelta(days=1)).month}
        
        # ── 保险1: 可疑模式识别 ──
        # 常见的日期软化pattern（用于模糊化过时日期）
        SOFTENING_PATTERNS = [
            (r'(\d+)月(\d+)日\s*热议', '热议'),
            (r'(\d+)月(\d+)日\s*持续', '持续'),
            (r'(\d+)月(\d+)日\s*最新', '最新'),
            (r'(\d+)月(\d+)日\s*独家', '独家'),
            (r'(\d+)月(\d+)日\s*热度不减', '热度不减'),
            (r'(\d+)月(\d+)日\s*持续发酵', '持续发酵'),
            (r'(\d+)月(\d+)日\s*引发关注', '引发关注'),
        ]
        
        suspicious_items = []
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    source = item.get('source', '')
                    title = item.get('title', '')[:30]
                    
                    for pattern, label in SOFTENING_PATTERNS:
                        match = re.search(pattern, source)
                        if match:
                            month, day = int(match.group(1)), int(match.group(2))
                            # 只有日期超出窗口时才算可疑
                            # (窗口内的"独家"/"热议"是合法标注)
                            if day not in valid_days or month not in valid_months:
                                try:
                                    news_date = datetime(report_date.year, month, day)
                                    days_diff = (report_date - news_date).days
                                    if days_diff > 1:
                                        suspicious_items.append(
                                            f"{title}(source含'{label}'但日期为{month}月{day}日，"
                                            f"距日报{days_diff}天)"
                                        )
                                except ValueError:
                                    pass
                            break
        
        # ── 保险2: 快照对比 ──
        snapshot_path = PROJECT_ROOT / "data" / "daily-workflow" / date_str / "source_snapshot.json"
        snapshot_mismatch = False
        snapshot_msg = ""
        
        if snapshot_path.exists():
            try:
                snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                
                # 从当前JSON重建sources列表
                current_sources = []
                for tab_idx, tab in enumerate(data.get("tabs", [])):
                    for region in ["overseas", "china"]:
                        for idx, item in enumerate(tab.get("news", {}).get(region, [])):
                            current_sources.append({
                                "tab": tab_idx, "region": region, "idx": idx,
                                "source": item.get("source", ""),
                                "title": item.get("title", "")[:50]
                            })
                
                current_hash = hashlib.md5(
                    json.dumps(current_sources, ensure_ascii=False).encode()
                ).hexdigest()
                
                if current_hash != snapshot.get("sources_hash", ""):
                    # source字段有变化 — 检查orchestrator状态
                    orch_state_path = PROJECT_ROOT / "data" / "daily-workflow" / date_str / "state.json"
                    step2_was_reset = False
                    if orch_state_path.exists():
                        orch_state = json.loads(orch_state_path.read_text())
                        content_status = orch_state.get("steps", {}).get("content", {}).get("status", "")
                        # 如果Step 2已被reset，说明是合法的重新编辑
                        step2_was_reset = content_status in ("pending", "failed")
                    
                    if not step2_was_reset:
                        # Step 2仍为completed但source变了 → 非法篡改
                        # 找出具体变化
                        old_sources = {(s["tab"], s["region"], s["idx"]): s["source"] 
                                      for s in snapshot.get("sources", [])}
                        changed = []
                        for cs in current_sources:
                            key = (cs["tab"], cs["region"], cs["idx"])
                            old = old_sources.get(key, "")
                            if old and old != cs["source"]:
                                changed.append(f'"{old[:25]}"→"{cs["source"][:25]}"')
                        
                        if changed:
                            snapshot_mismatch = True
                            snapshot_msg = f"Step 2完成后source被修改({len(changed)}处): {'; '.join(changed[:2])}"
            except Exception:
                pass  # 快照损坏不影响其他检查
        
        # ── 汇总结果 ──
        issues = []
        
        if snapshot_mismatch:
            issues.append(f"⛔ 快照对比: {snapshot_msg}")
        
        if suspicious_items:
            examples = "; ".join(suspicious_items[:2])
            issues.append(f"可疑日期模式: {examples}")
        
        if issues:
            severity = "error" if snapshot_mismatch else "error"
            return CheckResult(
                "日期篡改", False,
                " | ".join(issues),
                fixable=False,
                severity=severity
            )
        
        # 通过信息
        snap_info = "有快照✓" if snapshot_path.exists() else "无快照"
        return CheckResult("日期篡改", True, f"未检测到篡改({snap_info})")
    except Exception as e:
        return CheckResult("日期篡改", False, f"检查失败: {e}")


def check_closed_platform_urls(date_str: str) -> CheckResult:
    """检查15: [v8.0新增] 封闭平台链接合规检查
    
    将Step 2.7的封闭平台链接规则脚本化:
    - 禁止 mp.weixin.qq.com (任何形式，含src=11&timestamp临时URL)
    - 禁止 weixin.sogou.com/link?url= (搜狗跳转链接，数小时过期)
    - 允许 weixin.sogou.com/weixin?type=2&query= (搜狗搜索URL，永久稳定)
    - 允许 xiaohongshu.com/explore/<noteId> (小红书永久链接，但noteId必须真实)
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("封闭平台链接", True, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        FORBIDDEN_PATTERNS = [
            (r'mp\.weixin\.qq\.com', 'mp.weixin临时链接'),
            (r'weixin\.sogou\.com/link\?', '搜狗跳转链接(过期)'),
        ]
        
        violations = []
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    url = item.get('url', '')
                    title = item.get('title', '')[:25]
                    
                    for pattern, desc in FORBIDDEN_PATTERNS:
                        if re.search(pattern, url):
                            violations.append(f"{title}({desc})")
                            break
        
        if violations:
            examples = "; ".join(violations[:3])
            return CheckResult(
                "封闭平台链接", False,
                f"{len(violations)}个违规链接: {examples}",
                fixable=False,
                severity="error"
            )
        
        return CheckResult("封闭平台链接", True, "无违规封闭平台链接")
    except Exception as e:
        return CheckResult("封闭平台链接", False, f"检查失败: {e}")


def check_xhs_note_validity(date_str: str) -> CheckResult:
    """检查16: [v8.1新增] 小红书noteId真实性验证
    
    2026-03-15教训: Agent编造了格式正确但不存在的noteId (65f4e2a0..., 65f5a3b1...),
    质量门无法检测——HTTP HEAD对SPA返回200(假阴性), 随机抽检也可能漏过。
    
    验证策略:
    1. 提取所有xiaohongshu.com/explore/<noteId>链接
    2. 格式校验: noteId必须是24位hex
    3. 时间戳校验: noteId前8位是MongoDB ObjectId时间戳,
       必须在报告日期前90天以内(太旧=可能是编造的过期ID)
    4. 如无XHS链接则跳过
    
    注意: XHS的ObjectId中间字节通常为全零(00000000), 这是正常现象, 不能作为判断依据
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("小红书noteId", True, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        xhs_urls = []
        # 收集所有 xiaohongshu URL (url字段 + xhs_url字段)
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    for field in ['url', 'xhs_url']:
                        url = item.get(field, '')
                        if 'xiaohongshu.com/explore/' in url:
                            match = re.search(r'xiaohongshu\.com/explore/([a-f0-9]+)', url)
                            if match:
                                note_id = match.group(1)
                                title = item.get('title', '')[:25]
                                xhs_urls.append((note_id, title, field))
        
        if not xhs_urls:
            return CheckResult("小红书noteId", True, "无小红书链接，跳过")
        
        violations = []
        import time as _time
        
        # 报告日期的时间戳
        from datetime import datetime as _dt
        report_date = _dt.strptime(date_str, "%Y-%m-%d")
        report_ts = int(report_date.timestamp())
        
        for note_id, title, field in xhs_urls:
            # 检查1: noteId长度必须是24位hex
            if len(note_id) != 24:
                violations.append(f"{title}(noteId长度{len(note_id)}≠24, field={field})")
                continue
            
            # 检查2: 必须是合法hex
            try:
                int(note_id, 16)
            except ValueError:
                violations.append(f"{title}(noteId非法hex: {note_id[:12]}..., field={field})")
                continue
            
            # 检查3: MongoDB ObjectId时间戳校验
            # 前8位hex = Unix时间戳
            # 合理范围: 报告日期前90天 ~ 报告日期+1天
            ts = int(note_id[:8], 16)
            min_ts = report_ts - 90 * 86400   # 90天前
            max_ts = report_ts + 86400         # 明天
            
            if ts < min_ts:
                days_ago = (report_ts - ts) // 86400
                violations.append(
                    f"{title}(noteId时间戳过旧: {note_id[:8]}→{days_ago}天前, "
                    f"超过90天窗口, field={field})"
                )
            elif ts > max_ts:
                violations.append(
                    f"{title}(noteId时间戳在未来: {note_id[:8]}, field={field})"
                )
        
        if violations:
            examples = "; ".join(violations[:3])
            return CheckResult(
                "小红书noteId", False,
                f"{len(violations)}个疑似伪造: {examples}",
                fixable=False,
                severity="error"
            )
        
        return CheckResult(
            "小红书noteId", True, 
            f"{len(xhs_urls)}个XHS链接格式+时间戳校验通过"
        )
    except Exception as e:
        return CheckResult("小红书noteId", False, f"检查失败: {e}")


def run_all_checks(date_str: str) -> Tuple[List[CheckResult], int, int]:
    """运行所有检查"""
    checks = [
        check_json_exists,
        check_chinese_quotes,
        check_link_validity,
        check_content_nonempty,
        check_date_window,           # v2.0新增
        check_date_tampering,        # v8.0新增 - 日期篡改检测(双保险)
        check_closed_platform_urls,  # v8.0新增 - 封闭平台链接合规
        check_xhs_note_validity,     # v8.1新增 - 小红书noteId真实性验证
        check_board_classification,  # v3.0新增
        check_region_classification, # v4.0新增
        check_cross_day_dedup,       # v3.0新增
        check_source_diversity,      # v5.0新增 - 信息源多样性+微信覆盖
        check_html_links,            # v2.0新增
        check_md_html_exists,
        check_six_locations,
        check_external_sync,
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for check_func in checks:
        result = check_func(date_str)
        results.append(result)
        if result.passed:
            passed += 1
        else:
            failed += 1
    
    return results, passed, failed


def fix_chinese_quotes(date_str: str) -> bool:
    """修复中文引号"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return False
    
    try:
        content = json_path.read_text(encoding="utf-8")
        content = content.replace('"', '"').replace('"', '"')
        json_path.write_text(content, encoding="utf-8")
        # 验证JSON有效性
        json.loads(content)
        return True
    except Exception:
        return False


def fix_html_links(date_str: str) -> bool:
    """修复HTML链接"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month_str = date_obj.strftime("%Y-%m")
    html_path = DAILY_REPORTS_PATH / month_str / f"{date_str}-v3.html"
    
    if not html_path.exists():
        return False
    
    try:
        content = html_path.read_text(encoding="utf-8")
        
        # 添加 target="_blank" rel="noopener" 到所有外部链接
        def add_target_blank(match):
            tag = match.group(0)
            if 'target=' not in tag:
                return tag[:-1] + ' target="_blank" rel="noopener">'
            return tag
        
        content = re.sub(r'<a\s+href="https?://[^"]+"\s*>', add_target_blank, content)
        html_path.write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False


def fix_external_sync(date_str: str) -> bool:
    """修复外部同步"""
    try:
        # 运行同步脚本
        result = subprocess.run(
            ["python3", "scripts/sync_to_public.py", "--full", "--force", "--verify"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # 推送到外部仓库
            subprocess.run(
                ["python3", "scripts/sync_to_external.py", "--clean"],
                cwd=PROJECT_ROOT,
                capture_output=True
            )
            return True
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="AI日报质量门检查 v2.0")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复部分问题")
    parser.add_argument("--quiet", "-q", action="store_true", help="只输出结果摘要")
    parser.add_argument("--check-date", action="store_true", help="只运行时效性检查")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🔍 AI日报质量门检查 v8.0 - {date_str}")
    print("=" * 50)
    
    # 如果只检查时效性
    if args.check_date:
        result = check_date_window(date_str)
        print(result)
        return 0 if result.passed else 1
    
    # 运行所有检查
    results, passed, failed = run_all_checks(date_str)
    total_checks = len(results)
    
    # 输出结果
    if not args.quiet:
        for result in results:
            print(result)
        print()
    
    # 统计
    print(f"📊 检查完成: {passed}/{total_checks} 通过, {failed}/{total_checks} 失败")
    
    # 尝试修复
    if args.fix and failed > 0:
        print("\n🔧 尝试自动修复...")
        fixed = 0
        
        for result in results:
            if not result.passed and result.fixable:
                if result.name == "中文引号":
                    if fix_chinese_quotes(date_str):
                        print(f"  ✅ {result.name}: 已修复")
                        fixed += 1
                    else:
                        print(f"  ❌ {result.name}: 修复失败")
                elif result.name == "HTML链接":
                    if fix_html_links(date_str):
                        print(f"  ✅ {result.name}: 已修复")
                        fixed += 1
                    else:
                        print(f"  ❌ {result.name}: 修复失败")
                elif result.name == "外部同步":
                    if fix_external_sync(date_str):
                        print(f"  ✅ {result.name}: 已修复")
                        fixed += 1
                    else:
                        print(f"  ❌ {result.name}: 修复失败")
                elif result.name == "时效性":
                    print(f"  ⚠️ {result.name}: 需手动删除过时新闻并重新生成")
                else:
                    print(f"  ⏭️ {result.name}: 需手动修复")
        
        if fixed > 0:
            print(f"\n🔄 已修复 {fixed} 项，重新检查...")
            results, passed, failed = run_all_checks(date_str)
            print(f"📊 重新检查: {passed}/{total_checks} 通过, {failed}/{total_checks} 失败")
    
    # 最终结果
    if failed == 0:
        print("\n✅ 质量门通过！可以安全推送日报。")
        return 0
    else:
        # 检查是否有时效性错误（严重错误）
        timeliness_failed = any(r.name == "时效性" and not r.passed for r in results)
        if timeliness_failed:
            print(f"\n🚫 时效性检查未通过！请删除超出时间窗口的新闻后重新生成。")
            print("   规则: N日日报只收录 N-1日08:00 ~ N日08:00 的内容")
        else:
            print(f"\n❌ 质量门未通过 ({failed}项失败)，请修复后重试。")
        print("💡 提示: 使用 --fix 参数可尝试自动修复部分问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
