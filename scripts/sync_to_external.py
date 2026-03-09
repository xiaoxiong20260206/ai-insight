#!/usr/bin/env python3
"""
AI洞察外部版本同步脚本 v2.1
============================
将脱敏后的 public/ 内容同步到外部公开仓库 (ai-insight-public)

v2.1 变更 (2026-03-09):
- 新增 --full 模式: 自动先执行 sync_to_public.py --full
- 新增 --clean 模式: 清理外部仓库中已不存在于 public/ 的文件
- 新增 --verify 模式: 同步前验证敏感词零残留
- 改善错误处理: pull --rebase 冲突时自动恢复

使用方式:
  python scripts/sync_to_external.py                     # 同步 public/ → 外部仓库
  python scripts/sync_to_external.py --full              # 先全量脱敏，再推送（推荐）
  python scripts/sync_to_external.py --full --verify     # 全量+验证+推送（最安全）
  python scripts/sync_to_external.py --no-push           # 只复制不推送
  python scripts/sync_to_external.py --clean             # 清理外部仓库过期文件

作者: AI洞察
版本: 2.1.0
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
EXTERNAL_REPO = PROJECT_ROOT.parent / "ai-insight-public"


def run_sync_to_public(verify: bool = False) -> bool:
    """运行 sync_to_public.py --full --force（v2.1新增）"""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "sync_to_public.py"),
           "--full", "--force"]
    if verify:
        cmd.append("--verify")
    
    print("🔄 步骤 1/2: 执行内部版→公开版同步...")
    print("-" * 40)
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    print()
    
    if result.returncode != 0:
        print("❌ sync_to_public.py 失败，中止外部同步")
        return False
    return True


def sync_all() -> bool:
    """同步 public/ 目录的所有内容到外部仓库"""
    if not PUBLIC_DIR.exists():
        print(f"❌ public目录不存在: {PUBLIC_DIR}")
        print(f"   请先运行: python3 scripts/sync_to_public.py --full --force")
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
        
        rel_path = src_path.relative_to(PUBLIC_DIR)
        if any(part.startswith('.') for part in rel_path.parts):
            continue
        
        dst_path = EXTERNAL_REPO / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        copied_count += 1
    
    print(f"✅ 已复制 {copied_count} 个文件")
    return True


def clean_stale_files() -> int:
    """
    清理外部仓库中 public/ 已不存在的文件（v2.1新增）
    
    Returns:
        删除的文件数
    """
    if not EXTERNAL_REPO.exists():
        return 0
    
    deleted = 0
    for ext_file in EXTERNAL_REPO.rglob("*"):
        if not ext_file.is_file():
            continue
        
        rel_path = ext_file.relative_to(EXTERNAL_REPO)
        # 跳过 .git 和隐藏文件
        if any(part.startswith('.') for part in rel_path.parts):
            continue
        # 跳过 README.md（外部仓库专有）
        if rel_path.name == "README.md" and len(rel_path.parts) == 1:
            continue
        
        # 如果 public/ 中不存在该文件，删除
        public_counterpart = PUBLIC_DIR / rel_path
        if not public_counterpart.exists():
            ext_file.unlink()
            print(f"  🗑️ 已删除过期文件: {rel_path}")
            deleted += 1
    
    # 清理空目录
    for dir_path in sorted(EXTERNAL_REPO.rglob("*"), reverse=True):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            rel = dir_path.relative_to(EXTERNAL_REPO)
            if not any(part.startswith('.') for part in rel.parts):
                dir_path.rmdir()
    
    if deleted > 0:
        print(f"✅ 已清理 {deleted} 个过期文件")
    else:
        print("✅ 无过期文件需要清理")
    return deleted


def git_push() -> bool:
    """提交并推送到外部仓库"""
    try:
        os.chdir(EXTERNAL_REPO)
        
        # 先 pull --rebase 避免冲突
        pull_result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            capture_output=True, text=True
        )
        if pull_result.returncode != 0:
            # rebase 冲突，自动恢复
            if "CONFLICT" in (pull_result.stdout + pull_result.stderr):
                print("⚠️ Rebase 冲突，自动恢复...")
                subprocess.run(["git", "rebase", "--abort"], capture_output=True)
                subprocess.run(["git", "reset", "--hard", "origin/main"], capture_output=True)
                # 重新执行同步
                os.chdir(PROJECT_ROOT)
                sync_all()
                os.chdir(EXTERNAL_REPO)
        
        # git add
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # 检查是否有变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True
        )
        if not result.stdout.strip():
            print("ℹ️  无变更需要提交")
            return True
        
        # git commit
        commit_msg = f"📤 同步外部版本: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True, capture_output=True
        )
        print(f"✅ 已提交: {commit_msg}")
        
        # git push
        subprocess.run(
            ["git", "push", "origin", "main"],
            check=True, capture_output=True
        )
        print("✅ 已推送到 xiaoxiong20260206/ai-insight-public")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        if e.stderr:
            stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
            print(f"   stderr: {stderr}")
        return False
    finally:
        os.chdir(PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="AI洞察外部版本同步脚本 v2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --full --verify    # 全量脱敏+验证+推送（推荐）
  %(prog)s --full             # 全量脱敏+推送
  %(prog)s                    # 仅推送 public/ 当前内容
  %(prog)s --clean            # 清理过期文件
        """
    )
    parser.add_argument("--no-push", action="store_true", help="不自动推送到远程")
    parser.add_argument("--full", action="store_true", help="先执行全量脱敏同步 (v2.1)")
    parser.add_argument("--verify", action="store_true", help="同步前验证敏感词 (v2.1)")
    parser.add_argument("--clean", action="store_true", help="清理外部仓库过期文件 (v2.1)")
    args = parser.parse_args()
    
    print("🔄 AI洞察外部版本同步 v2.1")
    print("=" * 50)
    print(f"📁 源目录: {PUBLIC_DIR}")
    print(f"📁 目标仓库: {EXTERNAL_REPO}")
    print()
    
    # 步骤 1: 全量脱敏（可选）
    if args.full:
        if not run_sync_to_public(args.verify):
            sys.exit(1)
        print("🔄 步骤 2/2: 推送到外部仓库...")
        print("-" * 40)
    
    # 步骤 2: 清理过期文件（可选）
    if args.clean:
        print("🧹 清理过期文件...")
        clean_stale_files()
        print()
    
    # 步骤 3: 复制文件
    if not sync_all():
        return
    
    # 步骤 4: Git 推送
    if not args.no_push:
        git_push()
    
    print()
    print("=" * 50)
    print("📊 同步完成!")
    print(f"🔗 外部版本: https://xiaoxiong20260206.github.io/ai-insight-public/")


if __name__ == "__main__":
    main()
