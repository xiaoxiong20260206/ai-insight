#!/usr/bin/env python3
"""AI日报 JSON Schema 验证器

验证 daily-content-YYYY-MM-DD.json 是否符合 data/daily-schema.json 的结构契约。
在 gen_daily_html.py 生成 HTML 之前执行，不符合则阻断。

用法:
    uv run scripts/validate_daily_json.py 2026-06-29
    uv run scripts/validate_daily_json.py 2026-06-29 --strict  # 额外检查内容质量
"""

import sys
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data"
SCHEMA_PATH = DATA_PATH / "daily-schema.json"


def validate_json(date_str: str, strict: bool = False) -> tuple:
    """验证 JSON 文件是否符合 schema。
    
    Returns:
        (passed: bool, errors: list[str], warnings: list[str])
    """
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return False, [f"JSON文件不存在: {json_path}"], []
    
    if not SCHEMA_PATH.exists():
        return False, [f"Schema文件不存在: {SCHEMA_PATH}"], []
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"JSON解析失败: {e}"], []
    
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Schema解析失败: {e}"], []
    
    errors = []
    warnings = []
    
    # ====== 必填字段检查 ======
    required_top = ["date", "tabs", "overview", "heat_trend", "coverage", "capability_update"]
    for field in required_top:
        if field not in data:
            errors.append(f"缺少必填字段: {field}")
    
    # ====== tabs 结构检查 ======
    tabs = data.get("tabs", [])
    if len(tabs) != 5:
        errors.append(f"tabs 数量={len(tabs)}, 要求=5")
    
    required_tab_ids = {"tab_llm", "tab_coding", "tab_app", "tab_industry", "tab_enterprise"}
    actual_tab_ids = {t.get("id", "") for t in tabs}
    missing_ids = required_tab_ids - actual_tab_ids
    if missing_ids:
        errors.append(f"缺少板块ID: {missing_ids}")
    
    for i, tab in enumerate(tabs):
        tab_id = tab.get("id", f"tab[{i}]")
        # 必填子字段
        for field in ["id", "title", "news", "deep_focus", "pattern_insight_html"]:
            if field not in tab:
                errors.append(f"tab[{i}]({tab_id}) 缺少字段: {field}")
        
        # news 结构
        news = tab.get("news", {})
        for region in ["overseas", "china"]:
            if region not in news:
                errors.append(f"tab[{i}]({tab_id}) 缺少 news.{region}")
            else:
                for j, item in enumerate(news[region]):
                    for field in ["title", "url", "source", "summary", "region"]:
                        if field not in item:
                            errors.append(f"tab[{i}]({tab_id}).{region}[{j}] 缺少字段: {field}")
                    # URL检查（非微信源不能为空）
                    url = item.get("url", "")
                    source = item.get("source", "")
                    if url and not url.startswith(("http://", "https://")) and not url.startswith("#"):
                        warnings.append(f"tab[{i}]({tab_id}).{region}[{j}] URL格式异常: {url[:40]}")
                    elif not url and "微信" not in source and "量子位" not in source and "新智元" not in source:
                        if strict:
                            errors.append(f"tab[{i}]({tab_id}).{region}[{j}] 非微信源URL为空")
        
        # deep_focus 结构
        df = tab.get("deep_focus", {})
        if not isinstance(df, dict):
            errors.append(f"tab[{i}]({tab_id}) deep_focus 不是dict")
        else:
            for field in ["title", "paragraphs", "takeaway"]:
                if field not in df:
                    errors.append(f"tab[{i}]({tab_id}).deep_focus 缺少字段: {field}")
            if isinstance(df.get("paragraphs"), list) and len(df["paragraphs"]) == 0:
                warnings.append(f"tab[{i}]({tab_id}).deep_focus.paragraphs 为空数组")
        
        # pattern_insight_html
        pi = tab.get("pattern_insight_html", "")
        if not pi or len(pi) < 50:
            errors.append(f"tab[{i}]({tab_id}) pattern_insight_html 过短或为空({len(pi)}chars)")
    
    # ====== overview 检查 ======
    overview = data.get("overview", [])
    if len(overview) != 5:
        errors.append(f"overview 数量={len(overview)}, 要求=5")
    for i, ov in enumerate(overview):
        has_text = bool(ov.get("text", "").strip())
        has_headline = bool(ov.get("headline", "").strip())
        has_summary = bool(ov.get("summary", "").strip())
        if not (has_text or has_headline or has_summary):
            errors.append(f"overview[{i}]({ov.get('label','')}) text/headline/summary 全部为空 — 页面将显示空卡片")
    
    # ====== heat_trend 检查 ======
    heat = data.get("heat_trend", {})
    topics = heat.get("topics", [])
    if not topics:
        # 检查 fallback 格式
        has_rising = bool(heat.get("rising", []))
        has_stable = bool(heat.get("stable", []))
        has_cooling = bool(heat.get("cooling", []))
        if not (has_rising or has_stable or has_cooling):
            errors.append(f"heat_trend 无 topics 数组也无 rising/stable/cooling — 热度表将为空")
    
    # ====== data_table 检查 ======
    data_table = data.get("data_table", data.get("data_snapshot", []))
    if not data_table:
        warnings.append(f"data_table/data_snapshot 为空 — 数据速览模块将不渲染")
    else:
        for i, d in enumerate(data_table):
            if "metric" not in d or "value" not in d:
                errors.append(f"data_table[{i}] 缺少 metric 或 value 字段")
    
    # ====== capability_update 检查 ======
    cap = data.get("capability_update", "")
    if not cap or len(cap) < 50:
        errors.append(f"capability_update 过短或为空({len(cap)}chars)")
    
    # ====== coverage 检查 ======
    cov = data.get("coverage", {})
    total = cov.get("overseas", 0) + cov.get("china", 0)
    if total == 0:
        errors.append(f"coverage 海外+国内=0，无新闻")
    
    if strict:
        # 微信直引 ≥2
        wechat = cov.get("wechat", 0)
        if wechat < 2:
            warnings.append(f"微信直引={wechat}, 建议≥2")
    
    passed = len(errors) == 0
    return passed, errors, warnings


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI日报 JSON Schema 验证器")
    parser.add_argument("date", help="日期 YYYY-MM-DD")
    parser.add_argument("--strict", action="store_true", help="严格模式（含内容质量检查）")
    args = parser.parse_args()
    
    if not re.match(r"\d{4}-\d{2}-\d{2}", args.date):
        print(f"❌ 日期格式错误: {args.date}")
        sys.exit(2)
    
    passed, errors, warnings = validate_json(args.date, strict=args.strict)
    
    print(f"🔍 AI日报 JSON Schema 验证 — {args.date}")
    print("=" * 50)
    
    if errors:
        print(f"❌ {len(errors)} 个错误（阻断部署）:")
        for e in errors:
            print(f"  ❌ {e}")
    
    if warnings:
        print(f"⚠️ {len(warnings)} 个警告:")
        for w in warnings:
            print(f"  ⚠️ {w}")
    
    if passed:
        print(f"✅ JSON Schema 验证通过")
        if warnings:
            print(f"   （{len(warnings)}项警告不阻断）")
        sys.exit(0)
    else:
        print(f"❌ JSON Schema 验证失败 — 修复后再生成 HTML")
        sys.exit(1)


if __name__ == "__main__":
    main()
