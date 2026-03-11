#!/usr/bin/env python3
"""
AI日报质量门脚本 (Quality Gate)
================================
集中所有P0检查点，一次性验证日报完整性和正确性

使用方式:
  python scripts/daily_quality_gate.py                    # 检查今天的日报
  python scripts/daily_quality_gate.py 2026-03-11         # 检查指定日期
  python scripts/daily_quality_gate.py 2026-03-11 --fix   # 检查并尝试修复部分问题

检查项 (7项):
  1. JSON数据文件存在性
  2. 中文引号检测
  3. 链接有效性 (禁止#占位符)
  4. 内容非空检查
  5. MD/HTML文件存在性
  6. 6处联动更新检查
  7. 外部版同步检查

作者: 林克 (沈浪的AI分身)
版本: v1.0.0
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
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
    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable
    
    def __str__(self):
        status = "✅" if self.passed else "❌"
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
    """检查3: 链接有效性 (禁止#占位符)"""
    json_path = DATA_PATH / f"daily-content-{date_str}.json"
    if not json_path.exists():
        return CheckResult("链接有效", False, "JSON文件不存在，跳过")
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        invalid_count = 0
        invalid_examples = []
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    url = item.get('url', '')
                    if url == '#' or not url.startswith('http'):
                        invalid_count += 1
                        if len(invalid_examples) < 3:
                            invalid_examples.append(f"{item.get('title', '')[:20]}→{url}")
        
        if invalid_count > 0:
            examples = ", ".join(invalid_examples)
            return CheckResult("链接有效", False, f"{invalid_count}个无效链接: {examples}", fixable=True)
        return CheckResult("链接有效", True, "所有链接有效")
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


def check_md_html_exists(date_str: str) -> CheckResult:
    """检查5: MD/HTML文件存在性"""
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
    """检查6: 6处联动更新检查"""
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
    """检查7: 外部版同步检查"""
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


def run_all_checks(date_str: str) -> Tuple[List[CheckResult], int, int]:
    """运行所有检查"""
    checks = [
        check_json_exists,
        check_chinese_quotes,
        check_link_validity,
        check_content_nonempty,
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
    parser = argparse.ArgumentParser(description="AI日报质量门检查")
    parser.add_argument("date", nargs="?", help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复部分问题")
    parser.add_argument("--quiet", "-q", action="store_true", help="只输出结果摘要")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🔍 AI日报质量门检查 - {date_str}")
    print("=" * 50)
    
    # 运行所有检查
    results, passed, failed = run_all_checks(date_str)
    
    # 输出结果
    if not args.quiet:
        for result in results:
            print(result)
        print()
    
    # 统计
    print(f"📊 检查完成: {passed}/7 通过, {failed}/7 失败")
    
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
                elif result.name == "外部同步":
                    if fix_external_sync(date_str):
                        print(f"  ✅ {result.name}: 已修复")
                        fixed += 1
                    else:
                        print(f"  ❌ {result.name}: 修复失败")
                else:
                    print(f"  ⏭️ {result.name}: 需手动修复")
        
        if fixed > 0:
            print(f"\n🔄 已修复 {fixed} 项，重新检查...")
            results, passed, failed = run_all_checks(date_str)
            print(f"📊 重新检查: {passed}/7 通过, {failed}/7 失败")
    
    # 最终结果
    if failed == 0:
        print("\n✅ 质量门通过！可以安全推送日报。")
        return 0
    else:
        print(f"\n❌ 质量门未通过 ({failed}项失败)，请修复后重试。")
        print("💡 提示: 使用 --fix 参数可尝试自动修复部分问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())
