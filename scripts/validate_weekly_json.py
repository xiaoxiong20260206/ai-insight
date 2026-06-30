#!/usr/bin/env python3
"""AI周报 JSON Schema 验证器 (2026-06-30)"""

import sys, json, re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT / "data"

WEEKLY_SCHEMA = {
    "week_id": {"type": str, "required": True, "pattern": r"^\d{4}-W\d{2}$"},
    "week_num": {"type": (str, int), "required": True},
    "date_range": {"type": str, "required": True},
    "top5": {"type": list, "required": True, "min_len": 5,
             "item_schema": {"rank": int, "title": str, "desc": str, "why": str, "accent": str}},
    "insights": {"type": list, "required": False, "min_len": 0},
    "link_insight": {"type": dict, "required": False},
    "sections": {"type": dict, "required": True,
                 "expected_keys": ["llm", "coding", "app", "industry", "enterprise"]},
    "overview": {"type": dict, "required": True},
    "daily_index": {"type": list, "required": True, "min_len": 7},
    "vocab": {"type": list, "required": False},
    "narrative": {"type": dict, "required": False},
}

def validate(week_id: str) -> list:
    json_file = DATA_DIR / f"weekly-content-{week_id}.json"
    if not json_file.exists():
        return [f"❌ JSON文件不存在: {json_file}"]
    
    with open(json_file, encoding="utf-8") as f:
        d = json.load(f)
    
    errors = []
    warnings = []
    
    for key, spec in WEEKLY_SCHEMA.items():
        if spec.get("required") and key not in d:
            errors.append(f"❌ 缺少必填字段: {key}")
        elif key in d:
            expected_type = spec.get("type")
            if expected_type and not isinstance(d[key], expected_type):
                errors.append(f"❌ {key} 类型错误: 期望{expected_type.__name__}, 实际{type(d[key]).__name__}")
            if spec.get("pattern") and not re.match(spec["pattern"], str(d[key])):
                errors.append(f"❌ {key} 格式不匹配: {spec['pattern']}")
            if spec.get("min_len") and len(d[key]) < spec["min_len"]:
                warnings.append(f"⚠️ {key} 条目不足: {len(d[key])} < {spec['min_len']}")
            if spec.get("expected_keys"):
                missing = set(spec["expected_keys"]) - set(d[key].keys())
                if missing:
                    errors.append(f"❌ sections缺少板块: {missing}")
                extra = set(d[key].keys()) - set(spec["expected_keys"])
                if extra:
                    warnings.append(f"⚠️ sections有多余板块: {extra}")
    
    # 检查 top5 每条必须有 rank/title/desc/why
    for i, item in enumerate(d.get("top5", [])):
        for field in ["rank", "title", "desc", "why"]:
            if field not in item or not item[field]:
                errors.append(f"❌ top5[{i}] 缺少: {field}")
    
    # 检查 daily_index 至少7条（一周7天）
    di = d.get("daily_index", [])
    if len(di) < 7:
        warnings.append(f"⚠️ daily_index 只有 {len(di)} 条（期望7天）")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("用法: uv run scripts/validate_weekly_json.py <YYYY-WXX>")
        sys.exit(1)
    week_id = sys.argv[1]
    errors, warnings = validate(week_id)
    for e in errors: print(e)
    for w in warnings: print(w)
    if errors:
        print(f"\n❌ 验证失败: {len(errors)} 错误")
        sys.exit(1)
    else:
        print(f"\n✅ 验证通过" + (f" ({len(warnings)} 警告)" if warnings else ""))
        sys.exit(0)

if __name__ == "__main__":
    main()
