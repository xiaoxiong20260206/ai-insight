#!/usr/bin/env python3
"""
validate_daily_schema.py — AI日报 JSON Schema 自检工具 (v1.0)

用途：Subagent B (daily-content-agent) 生成 JSON 后立即调用，
      对照前日 JSON 验证所有字段名、类型、必填项，阻止 schema 错误流入质量门。

解决问题：
  - E1: source_url vs url 字段名不对
  - E2: summary vs details 字段名/类型不对
  - E3: heat_trend.topics 缺少 days/score/trend_class/trend_label
  - E4: data_snapshot 字段名不对
  - E5: tabs 顺序错误导致分类检查误报

用法：
  python3 scripts/validate_daily_schema.py YYYY-MM-DD
  python3 scripts/validate_daily_schema.py YYYY-MM-DD --show-schema   # 同时打印 schema 参照
  echo $?  # 0=通过, 1=失败
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# ==================== 配置 ====================

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"

# tabs 数组顺序（固定，不可改变）
REQUIRED_TABS_ORDER = ["models", "coding", "apps", "industry", "enterprise"]

# 新闻 item 必填字段及类型
NEWS_ITEM_REQUIRED = {
    "title": str,
    "source": str,
    "url": str,
    "date": str,
    "details": dict,  # 必须是 dict，不能是 string
}

# heat_trend.topics 必填字段
HEAT_TREND_TOPIC_REQUIRED = {
    "name": str,
    "heat": (int, float),
    "signal": str,
    "desc": str,
    "days": (int, float),
    "score": (int, float),
    "trend_class": str,
    "trend_label": str,
}

# data_snapshot 必填字段
DATA_SNAPSHOT_REQUIRED = {
    "metric": str,
    "value": str,
    "note": str,
}

# 顶层必填字段
TOP_LEVEL_REQUIRED = [
    "coverage", "overview", "heat_trend", "tabs",
    "data_snapshot", "watch_list", "references",
    "capability_update", "meta"
]

# ==================== 颜色输出 ====================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def ok(msg):
    print(f"  {GREEN}✅{RESET} {msg}")


def err(msg):
    print(f"  {RED}❌{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}⚠️{RESET}  {msg}")


def info(msg):
    print(f"  {CYAN}ℹ️{RESET}  {msg}")


# ==================== 验证函数 ====================

def validate(date_str: str, show_schema: bool = False) -> bool:
    """
    返回 True=通过, False=失败
    """
    errors = []
    warnings = []

    # ---- 加载当日 JSON ----
    json_path = DATA_DIR / f"daily-content-{date_str}.json"
    if not json_path.exists():
        print(f"{RED}❌ 文件不存在: {json_path}{RESET}")
        return False

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"{RED}❌ JSON 解析失败: {e}{RESET}")
        return False

    # ---- 加载前日 JSON（作为 schema 参照） ----
    yesterday = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    prev_path = DATA_DIR / f"daily-content-{yesterday}.json"
    prev_data = None
    if prev_path.exists():
        try:
            with open(prev_path, encoding="utf-8") as f:
                prev_data = json.load(f)
        except Exception:
            pass

    if show_schema and prev_data:
        print(f"\n{BOLD}{CYAN}═══ Schema 参照（前日 {yesterday}）═══{RESET}")
        try:
            prev_news = prev_data["tabs"][0]["news"]["overseas"]
            if prev_news:
                print(f"  新闻 item 字段:        {list(prev_news[0].keys())}")
        except Exception:
            pass
        try:
            prev_ht = prev_data["heat_trend"]["topics"]
            if prev_ht:
                print(f"  heat_trend.topics 字段: {list(prev_ht[0].keys())}")
        except Exception:
            pass
        try:
            prev_ds = prev_data["data_snapshot"]
            if prev_ds:
                print(f"  data_snapshot 字段:    {list(prev_ds[0].keys())}")
        except Exception:
            pass
        print()

    print(f"{BOLD}验证: {json_path.name}{RESET}")
    print("─" * 60)

    # ==================== 1. 顶层字段 ====================
    print(f"\n{BOLD}[1] 顶层必填字段{RESET}")
    for key in TOP_LEVEL_REQUIRED:
        if key not in data:
            errors.append(f"顶层缺少字段: '{key}'")
            err(f"缺少: {key}")
        else:
            ok(key)

    # ==================== 2. tabs 顺序 ====================
    print(f"\n{BOLD}[2] tabs 数组顺序（固定为 {REQUIRED_TABS_ORDER}）{RESET}")
    tabs = data.get("tabs", [])
    if len(tabs) != len(REQUIRED_TABS_ORDER):
        errors.append(f"tabs 数量应为 {len(REQUIRED_TABS_ORDER)}，实际 {len(tabs)}")
        err(f"tabs 数量错误: 期望 {len(REQUIRED_TABS_ORDER)}，实际 {len(tabs)}")
    else:
        actual_order = [t.get("id", "?") for t in tabs]
        if actual_order != REQUIRED_TABS_ORDER:
            errors.append(f"tabs 顺序错误: 期望 {REQUIRED_TABS_ORDER}，实际 {actual_order}")
            err(f"顺序错误: {actual_order}")
            err(f"期望顺序: {REQUIRED_TABS_ORDER}")
        else:
            ok(f"顺序正确: {actual_order}")

    # ==================== 3. 每个 tab 的字段 ====================
    print(f"\n{BOLD}[3] 每个 tab 的必填字段（news + deep_focus + pattern_insight_html）{RESET}")
    for i, tab in enumerate(tabs):
        tab_id = tab.get("id", f"tab[{i}]")

        # 3.1 news 结构
        news = tab.get("news", {})
        if not isinstance(news, dict):
            errors.append(f"{tab_id}: news 必须是 dict，实际 {type(news).__name__}")
            err(f"{tab_id}.news 类型错误")
        else:
            for region in ["overseas", "china"]:
                items = news.get(region, [])
                if not isinstance(items, list):
                    errors.append(f"{tab_id}.news.{region} 必须是 list")
                    err(f"{tab_id}.news.{region} 类型错误")
                else:
                    # 验证每条新闻
                    for j, item in enumerate(items):
                        for field, expected_type in NEWS_ITEM_REQUIRED.items():
                            if field not in item:
                                errors.append(f"{tab_id}.news.{region}[{j}] 缺少字段 '{field}'")
                                err(f"{tab_id}.news.{region}[{j}] 缺少: '{field}'（常见错误：source_url→url, summary→details）")
                            elif not isinstance(item[field], expected_type):
                                actual_type = type(item[field]).__name__
                                if field == "details" and isinstance(item[field], str):
                                    errors.append(f"{tab_id}.news.{region}[{j}].details 是 string，应为 dict {{finding:..., significance:...}}")
                                    err(f"{tab_id}.news.{region}[{j}].details 类型错误: 是 string，应为 dict")
                                else:
                                    errors.append(f"{tab_id}.news.{region}[{j}].{field} 类型错误: 期望 {expected_type.__name__}，实际 {actual_type}")
                                    err(f"{tab_id}.news.{region}[{j}].{field} 类型错误")

        # 3.2 deep_focus
        df = tab.get("deep_focus")
        if not df:
            errors.append(f"{tab_id} 缺少 deep_focus")
            err(f"{tab_id}: 缺少 deep_focus（质量门 P0 必填）")
        else:
            if not df.get("title"):
                errors.append(f"{tab_id}.deep_focus 缺少 title")
                err(f"{tab_id}.deep_focus: 缺少 title")
            paragraphs = df.get("paragraphs", [])
            if len(paragraphs) < 3:
                errors.append(f"{tab_id}.deep_focus.paragraphs 应有 3 段，实际 {len(paragraphs)} 段")
                err(f"{tab_id}.deep_focus.paragraphs: {len(paragraphs)} 段（需要 3 段）")
            if not df.get("takeaway"):
                errors.append(f"{tab_id}.deep_focus 缺少 takeaway")
                err(f"{tab_id}.deep_focus: 缺少 takeaway")
            if not errors or all(tab_id not in e for e in errors[-4:]):
                ok(f"{tab_id}.deep_focus ✓")

        # 3.3 pattern_insight_html
        pi = tab.get("pattern_insight_html", "")
        if len(pi) < 200:
            errors.append(f"{tab_id}.pattern_insight_html 太短 ({len(pi)} 字符，需 ≥200)")
            err(f"{tab_id}.pattern_insight_html: {len(pi)} 字符（需 ≥200，质量门 P0 必填）")
        else:
            ok(f"{tab_id}.pattern_insight_html: {len(pi)} 字符 ✓")

    # ==================== 4. heat_trend ====================
    print(f"\n{BOLD}[4] heat_trend 结构{RESET}")
    ht = data.get("heat_trend", {})
    topics = ht.get("topics", [])
    if not topics:
        errors.append("heat_trend.topics 为空")
        err("heat_trend.topics 为空")
    else:
        for i, topic in enumerate(topics):
            for field, expected_type in HEAT_TREND_TOPIC_REQUIRED.items():
                if field not in topic:
                    errors.append(f"heat_trend.topics[{i}] 缺少字段 '{field}'")
                    err(f"topics[{i}] 缺少: '{field}'")
                elif not isinstance(topic[field], expected_type if not isinstance(expected_type, tuple) else expected_type):
                    errors.append(f"heat_trend.topics[{i}].{field} 类型错误")
                    err(f"topics[{i}].{field} 类型错误")
        if not errors or all("topics" not in e for e in errors[-len(topics)*8:]):
            ok(f"heat_trend.topics: {len(topics)} 条，字段完整 ✓")

    # ==================== 5. data_snapshot ====================
    print(f"\n{BOLD}[5] data_snapshot 结构{RESET}")
    ds_list = data.get("data_snapshot", [])
    if not ds_list:
        warnings.append("data_snapshot 为空")
        warn("data_snapshot 为空")
    else:
        ds_errors = 0
        for i, ds in enumerate(ds_list):
            for field, expected_type in DATA_SNAPSHOT_REQUIRED.items():
                if field not in ds:
                    errors.append(f"data_snapshot[{i}] 缺少字段 '{field}'（常见错误：label→metric, source→note）")
                    err(f"data_snapshot[{i}] 缺少: '{field}'（常见：label→metric, trend→value, source→note）")
                    ds_errors += 1
        if ds_errors == 0:
            ok(f"data_snapshot: {len(ds_list)} 条，字段完整 ✓")

    # ==================== 6. overview 类型 ====================
    print(f"\n{BOLD}[6] overview 类型检查{RESET}")
    overview = data.get("overview")
    if overview is None:
        errors.append("overview 字段缺失")
        err("overview 字段缺失")
    elif isinstance(overview, str):
        errors.append("overview 是 string，应为 list（常见错误：直接写了字符串而非 [{icon,label,headline,text},...]）")
        err("overview 是 string，应为 list[{icon,label,headline,text}]（会导致 gen_daily_html.py AttributeError）")
    elif isinstance(overview, list):
        ok(f"overview: list，{len(overview)} 项 ✓")
    else:
        errors.append(f"overview 类型错误: {type(overview).__name__}")
        err(f"overview 类型错误: {type(overview).__name__}")

    # ==================== 7. capability_update 类型 ====================
    print(f"\n{BOLD}[7] capability_update 类型检查{RESET}")
    cu = data.get("capability_update")
    if cu is None:
        errors.append("capability_update 字段缺失")
        err("capability_update 缺失（林克自述，质量门 P0 必填）")
    elif isinstance(cu, dict):
        errors.append("capability_update 是 dict，应为 string（会导致 gen_daily_html.py AttributeError）")
        err("capability_update 是 dict，应为 string（林克自述正文，直接写字符串）")
    elif isinstance(cu, str):
        if len(cu) < 50:
            warnings.append(f"capability_update 过短 ({len(cu)} 字符)，建议 ≥100 字符")
            warn(f"capability_update 较短 ({len(cu)} 字符)")
        else:
            ok(f"capability_update: string，{len(cu)} 字符 ✓")

    # ==================== 8. meta.data_sources.weixin_direct_cite ====================
    print(f"\n{BOLD}[8] 微信直引数量{RESET}")
    try:
        weixin_cite = data["meta"]["data_sources"]["weixin_direct_cite"]
        if weixin_cite < 2:
            errors.append(f"weixin_direct_cite={weixin_cite}，需 ≥2（质量门 P0 红线）")
            err(f"weixin_direct_cite={weixin_cite}，需 ≥2")
        else:
            ok(f"weixin_direct_cite={weixin_cite} ✓")
    except KeyError as e:
        errors.append(f"meta.data_sources 缺少字段 {e}")
        err(f"meta.data_sources 缺少字段 {e}")

    # ==================== 9. 检查禁用 URL ====================
    print(f"\n{BOLD}[9] 禁用 URL 检查{RESET}")
    mp_weixin_count = 0
    sogou_redirect_count = 0
    for tab in tabs:
        for region in ["overseas", "china"]:
            for item in tab.get("news", {}).get(region, []):
                url = item.get("url", "")
                if "mp.weixin.qq.com" in url:
                    mp_weixin_count += 1
                    errors.append(f"禁用 URL: mp.weixin.qq.com（应改为 weixin.sogou.com/weixin?type=2&query=...）: {url[:60]}")
                if "weixin.sogou.com/link" in url:
                    sogou_redirect_count += 1
                    errors.append(f"禁用 URL: sogou 跳转链接（应改为 weixin.sogou.com/weixin?type=2&query=...）: {url[:60]}")

    if mp_weixin_count == 0 and sogou_redirect_count == 0:
        ok("无禁用 URL ✓")
    else:
        if mp_weixin_count > 0:
            err(f"发现 {mp_weixin_count} 个 mp.weixin.qq.com 链接（质量门 P0 红线）")
        if sogou_redirect_count > 0:
            err(f"发现 {sogou_redirect_count} 个 sogou 跳转链接")

    # ==================== 汇总 ====================
    print("\n" + "═" * 60)
    if errors:
        print(f"\n{RED}{BOLD}❌ Schema 验证失败：{len(errors)} 个错误{RESET}\n")
        print(f"{BOLD}错误清单：{RESET}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        if warnings:
            print(f"\n{YELLOW}警告（不阻断）：{RESET}")
            for w in warnings:
                print(f"  ⚠️  {w}")
        print(f"\n{YELLOW}💡 修复提示：{RESET}")
        print("  1. 对照前日 JSON 确认字段名（运行: python3 scripts/validate_daily_schema.py DATE --show-schema）")
        print("  2. news.item 字段：title, source, url, date, details（dict，不是 string）")
        print("  3. heat_trend.topics 字段：name, heat, signal, desc, days, score, trend_class, trend_label")
        print("  4. data_snapshot 字段：metric, value, note（不是 label/trend/source）")
        return False
    else:
        print(f"\n{GREEN}{BOLD}✅ Schema 验证通过！所有字段正确。{RESET}")
        if warnings:
            print(f"\n{YELLOW}警告（不阻断）：{RESET}")
            for w in warnings:
                print(f"  ⚠️  {w}")
        return True


# ==================== 入口 ====================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        today = datetime.now().strftime("%Y-%m-%d")
        date_str = today
    else:
        date_str = sys.argv[1]

    show_schema = "--show-schema" in sys.argv

    success = validate(date_str, show_schema=show_schema)
    sys.exit(0 if success else 1)
