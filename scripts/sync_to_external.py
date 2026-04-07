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
        print(f"   请先克隆: git clone https://github.com/my-ai-research-lab/ai-insight-public.git ../ai-insight-public")
        return False
    
    # 复制所有内容 (保持目录结构, 排除隐藏文件/目录)
    # ⭐ v2.2修复：明确过滤 -v3.html 文件（内部版专有文件，不应出现在外部仓库）
    # 根因经验：public/ 目录中若存在 -v3.html，会触发外部仓库的敏感词检测失败
    copied_count = 0
    skipped_v3 = 0
    for src_path in PUBLIC_DIR.rglob("*"):
        if not src_path.is_file():
            continue
        
        rel_path = src_path.relative_to(PUBLIC_DIR)
        if any(part.startswith('.') for part in rel_path.parts):
            continue
        
        # 过滤 -v3.html 文件（内部版，不对外公开）
        if src_path.stem.endswith('-v3') and src_path.suffix == '.html':
            skipped_v3 += 1
            continue
        
        dst_path = EXTERNAL_REPO / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        copied_count += 1
    
    if skipped_v3 > 0:
        print(f"  ⏭️ 已过滤 {skipped_v3} 个内部版 -v3.html 文件")
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


EXPECTED_REMOTE = "github.com/my-ai-research-lab/ai-insight-public"
MIRROR_REMOTE_NAME = "mirror"  # xiaoxiong20260206/ai-insight-public
MIRROR_REMOTE_URL = "https://github.com/xiaoxiong20260206/ai-insight-public.git"
MIRROR_EXPECTED = "github.com/xiaoxiong20260206/ai-insight-public"


def is_valid_git_repo(repo_path: Path) -> bool:
    """
    前置检查：验证目录是有效的 git 仓库（.git 目录完整且包含 HEAD）
    
    v2.5 新增（经验#70 — 2026-04-07：.git 目录被损坏成空壳导致外部推送静默失败）
    根因：.git/ 仅含 AUTO_MERGE 一个文件时，git 命令全部失败，但调用方捕获不到，
    sync_to_external 报"remote 验证失败"并 return False，deploy_daily 不阻断，
    用户看到"部署完成"但外部仓库实际未更新。
    
    修复策略：在任何 git 操作前先做此前置检查，失败时输出清晰诊断和修复命令。
    """
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print(f"❌ [GIT INTEGRITY] .git 目录不存在: {git_dir}")
        print(f"   请克隆仓库: git clone https://github.com/my-ai-research-lab/ai-insight-public.git {repo_path}")
        return False
    
    # .git 可能是文件（submodule）或目录，只检查目录形式
    if git_dir.is_dir():
        head_file = git_dir / "HEAD"
        config_file = git_dir / "config"
        if not head_file.exists() or not config_file.exists():
            print(f"❌ [GIT INTEGRITY] .git 目录损坏（缺少 HEAD 或 config）: {git_dir}")
            # 检查是否存在 .git_disabled 备份
            disabled = repo_path / ".git_disabled"
            if disabled.exists() and (disabled / "HEAD").exists():
                print(f"   发现 .git_disabled 备份，正在自动恢复...")
                import shutil
                shutil.rmtree(str(git_dir))
                disabled.rename(git_dir)
                print(f"   ✅ 已从 .git_disabled 恢复 .git 目录，请重新运行部署命令")
            else:
                print(f"   未找到 .git_disabled 备份，请手动修复或重新克隆仓库")
            return False
    
    # 用 git rev-parse 做最终验证
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "--git-dir"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ [GIT INTEGRITY] git rev-parse 失败，仓库状态异常: {repo_path}")
        print(f"   stderr: {result.stderr.strip()}")
        return False
    
    return True


def git_push() -> bool:
    """提交并推送到外部仓库"""
    try:
        # ⭐ v2.5新增：前置检查外部仓库 git 完整性（防 .git 空壳导致静默失败）
        if not is_valid_git_repo(EXTERNAL_REPO):
            return False

        os.chdir(EXTERNAL_REPO)

        # ⭐ v2.3新增：推送前验证 remote 是否指向正确仓库（防止推错账号）
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True
        )
        actual_remote = remote_result.stdout.strip()
        if EXPECTED_REMOTE not in actual_remote:
            print(f"❌ [ABORT] remote 验证失败！")
            print(f"   期望包含: {EXPECTED_REMOTE}")
            print(f"   实际 remote: {actual_remote}")
            print(f"   请执行: git -C {EXTERNAL_REPO} remote set-url origin https://github.com/my-ai-research-lab/ai-insight-public.git")
            return False
        
        # v2.2修复(经验#63): pull --rebase 前先 stash，防止 unstaged changes 中断同步
        # 若有本地未提交变更（如上次 sync 中途失败留下的文件），直接 pull 会报：
        # "cannot pull with rebase: You have unstaged changes" → 走非冲突分支 return False
        stash_result = subprocess.run(
            ["git", "stash"],
            capture_output=True, text=True
        )
        has_stash = "No local changes to save" not in stash_result.stdout
        if has_stash:
            print(f"  ℹ️  已暂存本地变更（stash），pull 后自动恢复")

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
            else:
                # pull 失败但非冲突（网络超时/refs错误/认证失败等）—— 必须阻断
                # 先恢复 stash，避免内容丢失
                if has_stash:
                    subprocess.run(["git", "stash", "pop"], capture_output=True)
                print(f"❌ git pull --rebase 失败（非冲突原因），中止推送")
                print(f"   stdout: {pull_result.stdout[:200]}")
                print(f"   stderr: {pull_result.stderr[:200]}")
                return False
        
        # pull 成功后恢复 stash（stash 的内容会被 git add -A 统一提交）
        if has_stash:
            pop_result = subprocess.run(["git", "stash", "pop"], capture_output=True, text=True)
            if pop_result.returncode != 0:
                print(f"  ⚠️  stash pop 失败（可能已有同名文件），继续执行: {pop_result.stderr[:100]}")
        
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
        print("✅ 已推送到 my-ai-research-lab/ai-insight-public")

        # ⭐ v2.4新增：同步推送到 mirror 仓库（xiaoxiong20260206/ai-insight-public）
        # 保持双仓库内容一致，xiaoxiong20260206.github.io/ai-insight-public/ 同步更新
        _push_to_mirror()

        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        if e.stderr:
            stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
            print(f"   stderr: {stderr}")
        return False
    finally:
        os.chdir(PROJECT_ROOT)


def _push_to_mirror() -> None:
    """
    将当前提交同步推送到 mirror remote（xiaoxiong20260206/ai-insight-public）
    v2.4新增：保持双仓库内容一致，失败只 WARN 不阻断主流程
    """
    try:
        # 检查 mirror remote 是否已配置
        check = subprocess.run(
            ["git", "remote", "get-url", MIRROR_REMOTE_NAME],
            capture_output=True, text=True
        )
        if check.returncode != 0:
            # mirror remote 不存在，自动添加
            print(f"  ℹ️  mirror remote 不存在，自动添加: {MIRROR_REMOTE_URL}")
            subprocess.run(
                ["git", "remote", "add", MIRROR_REMOTE_NAME, MIRROR_REMOTE_URL],
                check=True, capture_output=True
            )
        else:
            actual = check.stdout.strip()
            if MIRROR_EXPECTED not in actual:
                print(f"  ⚠️  [WARN] mirror remote 指向异常: {actual}，跳过镜像推送")
                return

        # 推送到 mirror
        push_result = subprocess.run(
            ["git", "push", MIRROR_REMOTE_NAME, "main"],
            capture_output=True, text=True
        )
        if push_result.returncode == 0:
            print("✅ 已同步推送到 xiaoxiong20260206/ai-insight-public (mirror)")
        else:
            stderr = push_result.stderr.strip()
            print(f"  ⚠️  [WARN] mirror 推送失败（不影响主流程）: {stderr[:200]}")
    except Exception as e:
        print(f"  ⚠️  [WARN] mirror 推送异常（不影响主流程）: {e}")


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
    print(f"🔗 外部版本 (my-ai-research-lab): https://my-ai-research-lab.github.io/ai-insight-public/")
    print(f"🔗 外部版本 (xiaoxiong20260206): https://xiaoxiong20260206.github.io/ai-insight-public/")


if __name__ == "__main__":
    main()
