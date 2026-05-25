#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI周报 JSON 生成器
==================
定义周报JSON schema + 生成空白模板 + 验证已有JSON

用法:
  uv run scripts/gen_weekly_json.py --date 2026-W22 --template   # 生成空白模板
  uv run scripts/gen_weekly_json.py --date 2026-W22 --validate   # 验证已有JSON
  uv run scripts/gen_weekly_json.py --date 2026-W22              # 同--template
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "01-daily-reports"
INTERNAL_BASE = "https://xiaoxiong20260206.github.io/ai-insight"


def compute_week_dates(week_id: str):
    """从 YYYY-WXX 计算日期范围"""
    year = int(week_id.split("-W")[0])
    week_num = int(week_id.split("-W")[1])
    iso_monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u")
    coverage_monday = iso_monday - timedelta(days=7)
    coverage_sunday = iso_monday - timedelta(days=1)
    return {
        "year": year,
        "week_num": week_num,
        "iso_monday": iso_monday,
        "coverage_monday": coverage_monday,
        "coverage_sunday": coverage_sunday,
        "month_str": coverage_sunday.strftime("%Y-%m"),
        "date_range": f"{coverage_monday.strftime('%m/%d')}-{coverage_sunday.strftime('%m/%d')}",
    }


def generate_template(week_id: str) -> dict:
    """生成空白周报JSON模板"""
    dates = compute_week_dates(week_id)
    coverage_monday = dates["coverage_monday"]
    coverage_sunday = dates["coverage_sunday"]
    
    # 日报索引（自动填充URL模板）
    daily_index = []
    for i in range(7):
        d = coverage_monday + timedelta(days=i)
        month_str = d.strftime("%Y-%m")
        daily_index.append({
            "date": d.strftime("%Y-%m-%d"),
            "weekday": ["周一","周二","周三","周四","周五","周六","周日"][i],
            "url": f"{INTERNAL_BASE}/01-daily-reports/{month_str}/{d.strftime('%Y-%m-%d')}-v3.html",
            "title": "AI洞察日报",
            "keywords": "（填入关键词，逗号分隔）"
        })
    
    template = {
        "week_id": week_id,
        "date_range": dates["date_range"],
        "year": dates["year"],
        "week_num": dates["week_num"],
        "title": f"AI 周报 {dates['year']}年第{dates['week_num']}周",
        "description": "（一段话总结本周核心信号）",
        "overview": {
            "table_rows": [
                {"dimension": "🧠 大模型", "signal": "（本周核心信号）"},
                {"dimension": "⌨️ AI Coding", "signal": "（本周核心信号）"},
                {"dimension": "📱 AI 应用", "signal": "（本周核心信号）"},
                {"dimension": "🏭 AI 行业", "signal": "（本周核心信号）"},
                {"dimension": "🔄 企业AI转型", "signal": "（本周核心信号）"},
            ],
            "stats": [
                {"value": "（数字）", "label": "（标签）", "class": "stat-purple"},
                {"value": "（数字）", "label": "（标签）", "class": "stat-success"},
                {"value": "（数字）", "label": "（标签）", "class": "stat-info"},
                {"value": "（数字）", "label": "（标签）", "class": "stat-warning"},
                {"value": "（数字）", "label": "（标签）", "class": "stat-danger"},
            ]
        },
        "top5": [
            {"rank": 1, "label": "（标签如：Agent宣言）", "title": "（完整标题）", "source": "（来源：CNET · URL）", "desc": "（详细描述3-5句）", "why": "（关键判断+影响分析）", "accent": "purple"},
            {"rank": 2, "label": "", "title": "", "source": "", "desc": "", "why": "", "accent": "info"},
            {"rank": 3, "label": "", "title": "", "source": "", "desc": "", "why": "", "accent": "success"},
            {"rank": 4, "label": "", "title": "", "source": "", "desc": "", "why": "", "accent": "danger"},
            {"rank": 5, "label": "", "title": "", "source": "", "desc": "", "why": "", "accent": "warning"},
        ],
        "insights": [
            {"tag_label": "洞察一", "title": "（洞察标题）", "content": "（详细内容，2-3段）", "trend_links": [{"text": "（链接文字）", "url": "（日报URL）"}]},
            {"tag_label": "洞察二", "title": "", "content": "", "trend_links": []},
        ],
        "link_insight": {
            "intro_callout": "（一句话核心判断，加粗）",
            "turning_point": {"content": "（拐点描述，2-3段）", "class": "callout-info"},
            "paradox": {"content": "（悖论描述，2-3段）", "class": "callout-success"},
            "takeaway": {"content": "（对从业者的启示，1-3条）", "class": "callout-warning"}
        },
        "sections": {
            "llm": {
                "id": "llm",
                "icon": "🧠",
                "title": "大模型本周动态",
                "callout": "（本周主线描述）",
                "callout_class": "callout-info",
                "table": [
                    {"date": "05-19", "event": "[标题](URL)", "source": "[来源](URL)", "importance": "⭐⭐⭐⭐⭐"},
                ],
                "stats": [{"value": "", "label": "", "class": "stat-purple"}]
            },
            "coding": {
                "id": "coding",
                "icon": "⌨️",
                "title": "AI Coding本周动态",
                "callout": "", "callout_class": "callout-danger",
                "table": [], "stats": []
            },
            "app": {
                "id": "app",
                "icon": "📱",
                "title": "AI应用本周动态",
                "callout": "", "callout_class": "callout-warning",
                "table": [], "stats": []
            },
            "industry": {
                "id": "industry",
                "icon": "🏭",
                "title": "AI行业本周动态",
                "callout": "", "callout_class": "callout-success",
                "table": [], "stats": []
            },
            "enterprise": {
                "id": "enterprise",
                "icon": "🔄",
                "title": "企业AI转型本周动态",
                "callout": "", "callout_class": "callout-warning",
                "table": [], "stats": []
            }
        },
        "daily_index": daily_index,
        "vocab": [
            {"term": "（术语）", "definition": "（定义2-3句）", "source": "（来源）"},
        ],
        "narrative": {
            "title": "（宏观叙事标题）",
            "intro_callout": "（一句话核心判断，加粗）",
            "main_blocks": [
                {"content": "（宣言描述，2-3段）", "class": "callout-info"},
                {"content": "（定价描述，2-3段）", "class": "callout-success"},
                {"content": "（对从业者的启示，2-3段）", "class": "callout-warning"},
            ],
            "conclusion_callout": "（结论段落：发动机决定上限，整车决定交付）"
        }
    }
    return template


def validate_json(week_id: str) -> bool:
    """验证周报JSON格式"""
    dates = compute_week_dates(week_id)
    json_path = DATA_DIR / f"weekly-content-{week_id}.json"
    
    if not json_path.exists():
        print(f"❌ JSON文件不存在: {json_path}")
        return False
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    
    errors = []
    warnings = []
    
    # P0检查
    required_fields = ["week_id", "date_range", "year", "week_num", "title",
                       "overview", "top5", "insights", "link_insight", "sections",
                       "daily_index", "vocab", "narrative"]
    for f in required_fields:
        if f not in data:
            errors.append(f"缺失必填字段: {f}")
    
    # Top5必须有5条
    if "top5" in data and len(data["top5"]) != 5:
        errors.append(f"Top5条数={len(data['top5'])}, 期望5")
    
    # 5板块必须都有
    section_keys = ["llm", "coding", "app", "industry", "enterprise"]
    if "sections" in data:
        for k in section_keys:
            if k not in data["sections"]:
                errors.append(f"缺失板块: {k}")
    
    # 每个板块必须有table（至少1条）和stats
    if "sections" in data:
        for k in section_keys:
            sec = data["sections"].get(k, {})
            if "table" not in sec:
                warnings.append(f"板块{k}没有table")
            elif len(sec["table"]) < 1:
                warnings.append(f"板块{k}的table为空")
    
    # daily_index必须有7条
    if "daily_index" in data and len(data["daily_index"]) != 7:
        errors.append(f"日报索引条数={len(data['daily_index'])}, 期望7")
    
    # date_range必须包含日期格式
    if "date_range" in data and "/" not in data["date_range"]:
        warnings.append("date_range格式可能不正确（期望MM/DD-MM/DD）")
    
    # {{message}}检查
    json_str = json.dumps(data)
    if "{{message}}" in json_str or "{{" in json_str:
        errors.append("JSON包含{{...}}占位符（P0红线）")
    
    # docs.corp.kuaishou.com检查
    if "docs.corp.kuaishou.com" in json_str:
        warnings.append("JSON包含内部链接docs.corp.kuaishou.com（应替换为公开URL）")
    
    if errors:
        print(f"\n❌ 硬性错误 ({len(errors)}):")
        for e in errors:
            print(f"  • {e}")
        return False
    
    if warnings:
        print(f"\n⚠️ 软性警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  • {w}")
    
    print(f"\n✅ 周报JSON校验通过 ({len(data['top5'])} Top5 + {len(section_keys)} 板块 + {len(data['daily_index'])} 日报索引)")
    return True


def main():
    parser = argparse.ArgumentParser(description="AI周报JSON生成器")
    parser.add_argument("date", nargs="?", help="周号 YYYY-WXX")
    parser.add_argument("--template", "-t", action="store_true", help="生成空白模板")
    parser.add_argument("--validate", "-v", action="store_true", help="验证已有JSON")
    args = parser.parse_args()
    
    if not args.date:
        args.date = datetime.now().strftime("%G-W%V")
    
    week_id = args.date
    
    DATA_DIR.mkdir(exist_ok=True)
    
    if args.validate:
        ok = validate_json(week_id)
        sys.exit(0 if ok else 1)
    
    # 生成模板
    template = generate_template(week_id)
    out_path = DATA_DIR / f"weekly-content-{week_id}.json"
    out_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 周报JSON模板已生成: {out_path}")
    print(f"   填写内容后，用 gen_weekly_html.py 从JSON生成HTML")


if __name__ == "__main__":
    main()