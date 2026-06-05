#!/usr/bin/env python3
"""
AI洞察外部版本同步脚本 v2.2
============================
将脱敏后的 public/ 内容同步到外部公开仓库 (ai-insight-public)

v2.2 变更 (2026-05-26):
- 🔥 P0修复：sync_all() 跳过 public/index.html（原始内部版，含林克/沈浪等敏感词）
  根因：public/index.html 是内部版Pages部署源（v3.0注释"保留原始内容"），含4处林克+沈浪+快手等敏感词
  sync_all() 之前无差别复制全部文件，导致外部仓库 index.html 被原始版覆盖，
  推送到 GitHub Pages 后外部首页泄露内部身份信息。
  修复：index.html 由 sync_to_public.py 的 sync_index_html() 单独处理（先 sanitize_html 再写入），
  sync_all() 只负责非首页文件。

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
import fcntl
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from config import (
    EXPECTED_REMOTE, EXTERNAL_CLONE_URL,
    EXTERNAL_REPO, PUBLIC_PATH as PUBLIC_DIR,
    EXTERNAL_GITHUB_USER, EXTERNAL_REPO_NAME,
    PROJECT_ROOT,
)

# ---- 兼容旧变量名 ----
EXTERNAL_REPO = EXTERNAL_REPO  # 来自 config.py
PUBLIC_DIR    = PUBLIC_DIR


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
    # ⭐ v2.2修复（P0）：跳过根级 index.html — 它是内部版原始文件（含林克/沈浪/快手等敏感词）
    # 根因：public/index.html = 内部版Pages部署源（v3.0注释"保留原始内容"），不应出现在外部仓库
    #       外部版 index.html 由 sync_to_public.py 的 sync_index_html() 单独 sanitize 后写入
    #       如果这里也复制，就会覆盖已经脱敏的版本，推送到 GitHub Pages 后泄露内部身份
    # ⭐ v2.2修复：明确过滤 -v3.html 文件（内部版专有文件，不应出现在外部仓库）
    # 根因经验：public/ 目录中若存在 -v3.html，会触发外部仓库的敏感词检测失败
    copied_count = 0
    skipped_v3 = 0
    skipped_index = 0
    for src_path in PUBLIC_DIR.rglob("*"):
        if not src_path.is_file():
            continue
        
        rel_path = src_path.relative_to(PUBLIC_DIR)
        if any(part.startswith('.') for part in rel_path.parts):
            continue
        
        # 🔥 P0：跳过根级 index.html（内部版，含敏感词）
        if rel_path == Path("index.html"):
            skipped_index += 1
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
    if skipped_index > 0:
        print(f"  ⏭️ 已跳过根级 index.html（由 sync_to_public.py 单独脱敏处理）")
    print(f"✅ 已复制 {copied_count} 个文件")
    return True


def fix_footer_urls() -> int:
    """替换外部仓库中日报/周报HTML的footer首页URL
    
    P0 #18 规则：内部版日报footer→内部首页URL，外部版日报footer→外部首页URL
    sync_to_external.py 同步后，外部版HTML中可能残留内部URL，需要批量替换。
    
    Returns:
        修复的文件数
    """
    from config import INTERNAL_PAGES_BASE, EXTERNAL_PAGES_BASE
    
    internal_url = f'{INTERNAL_PAGES_BASE}/"'
    external_url = f'{EXTERNAL_PAGES_BASE}/"'
    # 也处理旧版错误URL（缺少-public后缀）
    wrong_external_url = 'https://xiaoxiong20260206.github.io/ai-insight/"'
    
    fixed = 0
    for html_file in EXTERNAL_REPO.rglob("*.html"):
        if not html_file.is_file():
            continue
        # 只处理01-daily-reports下的日报/周报HTML
        rel = html_file.relative_to(EXTERNAL_REPO)
        if not str(rel).startswith("01-daily-reports/"):
            continue
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        # 替换内部URL→外部URL
        if internal_url in new_content:
            new_content = new_content.replace(internal_url, external_url)
        # 替换错误外部URL→正确外部URL（缺少-public后缀）
        if wrong_external_url in new_content:
            new_content = new_content.replace(wrong_external_url, external_url)
        
        if new_content != content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            fixed += 1
    
    if fixed > 0:
        print(f"  ✅ 已修复 {fixed} 个文件的footer首页URL（内部→外部）")
    return fixed


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


EXPECTED_REMOTE = EXPECTED_REMOTE  # from config
# MIRROR_REMOTE_NAME/MIRROR_REMOTE_URL: 双仓库模式已废弃（经验#73）


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
        print(f"   请克隆仓库: git clone https://github.com/xiaoxiong20260206/ai-insight-public.git {repo_path}")
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
                print(f"   ✅ 已从 .git_disabled 恢复 .git 目录，继续执行推送...")
                # ⭐ v2.6修复（经验#71）：恢复后不能 return False！
                # 旧逻辑 return False 导致推送中止，下次仍然失败；
                # 恢复完成后应继续走 git rev-parse 验证，通过则 return True。
                # 不在此处 return，继续向下执行 rev-parse 验证
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
        # v2.4修复(#113): 同时接受 HTTPS 和 SSH 格式的 remote URL
        #   HTTPS: https://github.com/xiaoxiong20260206/ai-insight-public.git
        #   SSH:   git@github.com:xiaoxiong20260206/ai-insight-public.git
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True
        )
        actual_remote = remote_result.stdout.strip()
        # 提取仓库标识：无论 HTTPS(/分隔) 还是 SSH(:分隔)，都取 user/repo 部分
        remote_repo_id = actual_remote
        for prefix in ["https://github.com/", "git@github.com:", "ssh://git@github.com/"]:
            if actual_remote.startswith(prefix):
                remote_repo_id = actual_remote[len(prefix):].rstrip(".git")
                break
        if remote_repo_id != f"{EXTERNAL_GITHUB_USER}/{EXTERNAL_REPO_NAME}":
            print(f"❌ [ABORT] remote 验证失败！")
            print(f"   期望仓库: {EXTERNAL_GITHUB_USER}/{EXTERNAL_REPO_NAME}")
            print(f"   实际 remote: {actual_remote}")
            print(f"   解析仓库ID: {remote_repo_id}")
            print(f"   请执行: git -C {EXTERNAL_REPO} remote set-url origin https://github.com/{EXTERNAL_GITHUB_USER}/{EXTERNAL_REPO_NAME}.git")
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
        print("✅ 已推送到 xiaoxiong20260206/ai-insight-public")

        # v2.7: 双仓库逻辑已移除，origin 即为 xiaoxiong20260206/ai-insight-public

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

    # ⭐ v2.7新增（经验#72）：进程级并发锁，防止多个 launchd 定时任务同时操作同一 git 仓库
    # 根因：AI日报(8:00) 和 phase4/deploy_daily(5:00) 都会触发本脚本，
    #        若前一个进程还在 git pull/add/commit 时被后一个中断，.git 会进入损坏状态
    LOCK_FILE = "/tmp/ai-insight-external-sync.lock"
    lock_fd = open(LOCK_FILE, "w")
    try:
        # 非阻塞加锁：如果已被另一进程占用，立即退出（避免无限等待）
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(f"{os.getpid()}\n")
        lock_fd.flush()
        print(f"🔒 进程锁已获取 (PID={os.getpid()})")
    except OSError:
        # 读取当前占用锁的 PID
        try:
            with open(LOCK_FILE) as f:
                other_pid = f.read().strip()
        except Exception:
            other_pid = "unknown"
        print(f"⏭️  [SKIP] 另一个 sync_to_external.py 进程正在运行 (PID={other_pid})，本次跳过")
        print(f"   若需强制执行，请先确认另一进程已结束: kill {other_pid}")
        lock_fd.close()
        sys.exit(0)  # 正常退出（不是错误），让调用方继续
    
    try:
        _run_main_logic(args)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass


def _run_main_logic(args) -> None:
    """主逻辑（从 main 拆出，确保 finally 中解锁时逻辑干净）"""
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
        # v2.6 修复(2026-04-07): 原为 return（退出码0），deploy_daily.sh 无法感知失败
        # 必须以非零退出码退出，确保调用方（deploy_daily.sh/orchestrator）能捕获同步失败
        print("❌ [ABORT] sync_all() 失败，外部文件同步中止")
        sys.exit(1)
    
    # 步骤 3.5: 修复footer首页URL（P0 #18：内部版URL→外部版URL）
    fix_footer_urls()
    
    # 步骤 4: Git 推送
    if not args.no_push:
        git_push()
    
    print()
    print("=" * 50)
    print("📊 同步完成!")
    print(f"🔗 外部版本: https://xiaoxiong20260206.github.io/ai-insight-public/ (GitHub Pages)")


if __name__ == "__main__":
    main()
