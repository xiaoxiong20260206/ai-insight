#!/usr/bin/env python3
"""AI日报 HTML 展示验证器

在 gen_daily_html.py 生成 HTML 后、部署前执行。
检查 HTML 输出的展示完整性，包括：
1. 无未替换模板变量
2. 无空内容区域
3. 表格样式完整性
4. 内外部版本一致性
5. Tab 面板正确性
6. Footer 文案正确性

用法:
    uv run scripts/validate_daily_html.py 2026-06-29
    uv run scripts/validate_daily_html.py 2026-06-29 --external
"""

import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_PATH = PROJECT_ROOT / "01-daily-reports"
PUBLIC_PATH = PROJECT_ROOT / "public"
EXTERNAL_PATH = PROJECT_ROOT.parent / "ai-insight-public"


def validate_html(html: str, label: str = "") -> tuple:
    """验证单个 HTML 文件的展示完整性。
    
    Returns:
        (passed: bool, errors: list[str], warnings: list[str])
    """
    errors = []
    warnings = []
    prefix = f"[{label}] " if label else ""
    
    # ====== 1. 模板变量残留 ======
    template_leaks = re.findall(r'\{[A-Z_][A-Z_0-9]*(?:\[.*?\])?\}', html)
    if template_leaks:
        unique = sorted(set(template_leaks))
        errors.append(f"{prefix}发现{len(template_leaks)}处未替换模板变量: {', '.join(unique[:5])}")
    
    # ====== 2. 空内容区域 ======
    # 空overview-item-text
    empty_overview = re.findall(r'overview-item-text">\s*</div>', html)
    if empty_overview:
        errors.append(f"{prefix}overview空文字: {len(empty_overview)}处")
    
    # 空heat-header-title
    empty_heat_title = re.findall(r'heat-header-title">\s*</div>', html)
    if empty_heat_title:
        errors.append(f"{prefix}heat-header-title为空: {len(empty_heat_title)}处")
    
    # 空tbody（有表头无数据行）
    heat_tbody = re.search(r'heat-table.*?<tbody>(.*?)</tbody>', html, re.DOTALL)
    if heat_tbody and not heat_tbody.group(1).strip():
        errors.append(f"{prefix}heat-table tbody为空（有表头无数据）")
    elif heat_tbody:
        heat_rows = heat_tbody.group(1).count('<tr>')
        if heat_rows < 3:
            warnings.append(f"{prefix}heat-table仅{heat_rows}行，建议≥3")
    
    data_tbody = re.search(r'data-table.*?<tbody>(.*?)</tbody>', html, re.DOTALL)
    if data_tbody and data_tbody.group(1).strip() == '':
        # data_table可能为空但模块不渲染（设计允许）
        pass
    
    # ====== 3. Tab面板正确性 ======
    tab_panels = re.findall(r'class="tab-panel[^"]*"[^>]*data-tab="([^"]+)"[^>]*role="tabpanel"', html)
    if len(tab_panels) != 5:
        errors.append(f"{prefix}tab-panel数量={len(tab_panels)}, 要求=5")
    
    tab_btns = re.findall(r'class="tab-btn[^"]*"[^>]*data-tab="([^"]+)"', html)
    if len(tab_btns) != 5:
        errors.append(f"{prefix}tab-btn数量={len(tab_btns)}, 要求=5")
    
    # Tab面板有active
    has_active_panel = 'tab-panel active' in html or 'tab-btn active' in html
    if not has_active_panel:
        warnings.append(f"{prefix}无active tab/panel — 可能首屏空白")
    
    # CSS fallback (v5.2: first-of-type fallback removed — it caused bug where llm panel always showed)
    # No longer checking for first-of-type; JS controls tab visibility
    
    # ====== 4. 新闻条目 ======
    news_items = len(re.findall(r'class="news-item"', html))
    if news_items < 10:
        warnings.append(f"{prefix}新闻条目={news_items}, 建议≥10")
    
    # ====== 5. Footer 文案 ======
    footer = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.DOTALL)
    if footer:
        ft = re.sub(r'<[^>]+>', '', footer.group(0)).strip()
        # 检查不通顺的脱敏残留
        bad_patterns = ['的AI洞察', 'AI洞察的', '我是AI洞察', '的AI分身']
        for bp in bad_patterns:
            if bp in ft:
                errors.append(f"{prefix}footer含不通顺脱敏: '{bp}'")
        # 检查应包含首页链接
        if 'AI洞察首页' not in ft and 'ai-insight' not in footer.group(0).lower():
            warnings.append(f"{prefix}footer缺少首页链接")
    
    # ====== 6. 板块主题色 ======
    required_colors = ['#059669', '#2563EB', '#7C3AED', '#D97706', '#E11D48']
    missing_colors = [c for c in required_colors if c not in html]
    if missing_colors:
        warnings.append(f"{prefix}缺少板块主题色: {missing_colors}")
    
    # ====== 7. 清爽风格基础 ======
    has_mesh = 'radial-gradient' in html[:50000]
    if not has_mesh:
        warnings.append(f"{prefix}可能缺少清爽风格Mesh背景")
    
    passed = len(errors) == 0
    return passed, errors, warnings


def validate_internal_external_consistency(internal_html: str, external_html: str) -> tuple:
    """检查内外部版本一致性。"""
    errors = []
    warnings = []
    
    # 外部版敏感词
    sensitive = ['林克', '沈浪', 'AI分身', 'MyFlicker']
    for word in sensitive:
        count = external_html.count(word)
        if count > 0:
            errors.append(f"[外部版] 敏感词残留: '{word}' ×{count}")
    
    # 外部版 -v3 链接残留
    v3_links = re.findall(r'\d{4}-\d{2}-\d{2}-v3\.html', external_html)
    if v3_links:
        errors.append(f"[外部版] -v3.html链接残留: {len(v3_links)}处")
    
    # 外部版内部URL残留
    int_urls = re.findall(r'frontend-cloud\.corp\.kuaishou\.com', external_html)
    if int_urls:
        errors.append(f"[外部版] 内部URL残留: {len(int_urls)}处")
    
    # 结构一致性：两者tab数量应相同
    int_tabs = len(re.findall(r'tab-btn', internal_html))
    ext_tabs = len(re.findall(r'tab-btn', external_html))
    if int_tabs != ext_tabs:
        warnings.append(f"内外版tab-btn数不一致: 内部={int_tabs}, 外部={ext_tabs}")
    
    passed = len(errors) == 0
    return passed, errors, warnings


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI日报 HTML 展示验证器")
    parser.add_argument("date", help="日期 YYYY-MM-DD")
    parser.add_argument("--external", action="store_true", help="同时验证外部版")
    args = parser.parse_args()
    
    date_str = args.date
    month_str = date_str[:7]
    
    # 内部版
    internal_path = REPORTS_PATH / month_str / f"{date_str}-v3.html"
    if not internal_path.exists():
        print(f"❌ 内部版HTML不存在: {internal_path}")
        sys.exit(2)
    
    internal_html = internal_path.read_text(encoding="utf-8")
    
    print(f"🔍 AI日报 HTML 展示验证 — {date_str}")
    print("=" * 50)
    
    # 验证内部版
    int_passed, int_errors, int_warnings = validate_html(internal_html, "内部版")
    
    # 验证public版
    public_path = PUBLIC_PATH / "01-daily-reports" / month_str / f"{date_str}.html"
    pub_passed, pub_errors, pub_warnings = True, [], []
    if public_path.exists():
        pub_html = public_path.read_text(encoding="utf-8")
        pub_passed, pub_errors, pub_warnings = validate_html(pub_html, "public版")
    
    # 验证外部版
    ext_passed, ext_errors, ext_warnings = True, [], []
    cons_passed, cons_errors, cons_warnings = True, [], []
    if args.external:
        ext_path = EXTERNAL_PATH / "01-daily-reports" / month_str / f"{date_str}.html"
        if ext_path.exists():
            ext_html = ext_path.read_text(encoding="utf-8")
            ext_passed, ext_errors, ext_warnings = validate_html(ext_html, "外部版")
            cons_passed, cons_errors, cons_warnings = validate_internal_external_consistency(internal_html, ext_html)
        else:
            ext_errors = [f"外部版HTML不存在: {ext_path}"]
            ext_passed = False
    
    all_errors = int_errors + pub_errors + ext_errors + cons_errors
    all_warnings = int_warnings + pub_warnings + ext_warnings + cons_warnings
    
    if all_warnings:
        print(f"⚠️ {len(all_warnings)} 个警告:")
        for w in all_warnings:
            print(f"  ⚠️ {w}")
    
    if all_errors:
        print(f"❌ {len(all_errors)} 个错误（阻断部署）:")
        for e in all_errors:
            print(f"  ❌ {e}")
    
    passed = not all_errors
    if passed:
        print(f"✅ HTML 展示验证通过")
        if all_warnings:
            print(f"   （{len(all_warnings)}项警告不阻断）")
        sys.exit(0)
    else:
        print(f"❌ HTML 展示验证失败 — 修复后再部署")
        sys.exit(1)


if __name__ == "__main__":
    main()
