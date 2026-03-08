#!/usr/bin/env python3
"""
AI日报外部版本同步脚本
======================
将脱敏后的日报同步到外部公开仓库 (ai-insight-public)

功能:
1. 从 public/ 目录复制所有脱敏后的内容
2. 保持与 public/ 目录相同的目录结构
3. 提交并推送到 xiaoxiong20260206/ai-insight-public

使用方式:
  python scripts/sync_to_external.py                    # 同步所有内容
  python scripts/sync_to_external.py --no-push          # 只复制，不推送

前置条件:
  1. 已运行 sync_to_public.py 生成脱敏版本
  2. ../ai-insight-public/ 仓库存在

作者: 林克 (沈浪的AI分身)
版本: 2.0.0
"""

import argparse
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
EXTERNAL_REPO = PROJECT_ROOT.parent / "ai-insight-public"


def sync_all() -> bool:
    """
    同步 public/ 目录的所有内容到外部仓库
    
    Returns:
        是否成功同步
    """
    if not PUBLIC_DIR.exists():
        print(f"❌ public目录不存在: {PUBLIC_DIR}")
        print(f"   请先运行: python3 scripts/sync_to_public.py")
        return False
    
    if not EXTERNAL_REPO.exists():
        print(f"❌ 外部仓库不存在: {EXTERNAL_REPO}")
        print(f"   请先克隆: git clone https://github.com/xiaoxiong20260206/ai-insight-public.git ../ai-insight-public")
        return False
    
    # 复制所有内容 (保持目录结构, 排除隐藏文件/目录)
    copied_count = 0
    for src_path in PUBLIC_DIR.rglob("*"):
        if not src_path.is_file():
            continue
        
        # 排除隐藏文件和 .git 目录下的文件
        rel_path = src_path.relative_to(PUBLIC_DIR)
        if any(part.startswith('.') for part in rel_path.parts):
            continue
        
        dst_path = EXTERNAL_REPO / rel_path
        
        # 确保目标目录存在
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        copied_count += 1
    
    print(f"✅ 已复制 {copied_count} 个文件")
    return True


def git_push() -> bool:
    """提交并推送到外部仓库"""
    try:
        os.chdir(EXTERNAL_REPO)
        
        # git add
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # 检查是否有变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            print("ℹ️  无变更需要提交")
            return True
        
        # git commit
        commit_msg = f"📤 同步外部版本: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
            capture_output=True
        )
        print(f"✅ 已提交: {commit_msg}")
        
        # git push origin main
        subprocess.run(
            ["git", "push", "origin", "main"],
            check=True,
            capture_output=True
        )
        print("✅ 已推送到 xiaoxiong20260206/ai-insight-public")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")
        return False
    finally:
        os.chdir(PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="AI日报外部版本同步脚本")
    parser.add_argument("--no-push", action="store_true", help="不自动推送到远程")
    args = parser.parse_args()
    
    print("🔄 AI洞察外部版本同步")
    print("=" * 50)
    print(f"📁 源目录: {PUBLIC_DIR}")
    print(f"📁 目标仓库: {EXTERNAL_REPO}")
    print()
    
    # 同步文件
    if not sync_all():
        return
    
    # Git 推送
    if not args.no_push:
        git_push()
    
    print()
    print("=" * 50)
    print("📊 同步完成!")
    print(f"🔗 外部版本: https://xiaoxiong20260206.github.io/ai-insight-public/")


if __name__ == "__main__":
    main()
