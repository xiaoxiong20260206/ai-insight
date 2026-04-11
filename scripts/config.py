"""
AI-Insight 项目全局配置 — 单一真相源 (SSoT)
============================================
所有脚本的 URL、路径、仓库名称 **必须从此文件 import**，禁止硬编码。

修改说明：
  - 内部仓库 GitHub 账号变更 → 只改 INTERNAL_GITHUB_USER
  - 外部仓库 GitHub 账号变更 → 只改 EXTERNAL_GITHUB_USER
  - 项目名称变更 → 改 INTERNAL_REPO_NAME / EXTERNAL_REPO_NAME

经验#73 (2026-04-10): 根治外部版同步静默失败根因
  原问题: EXPECTED_REMOTE 散落在 sync_to_external.py，与实际仓库不符，
  导致 remote 验证 return False，外部版从未真正 push。
  修复: 集中到此文件，全局唯一修改点。
"""
from pathlib import Path

# ============================================================
# 1. GitHub 账号 & 仓库名（唯一需要修改的地方）
# ============================================================
INTERNAL_GITHUB_USER = "xiaoxiong20260206"
INTERNAL_REPO_NAME   = "ai-insight"

EXTERNAL_GITHUB_USER = "xiaoxiong20260206"
EXTERNAL_REPO_NAME   = "ai-insight-public"

# ============================================================
# 2. 派生 URL（自动计算，无需手动维护）
# ============================================================
INTERNAL_PAGES_BASE = f"https://{INTERNAL_GITHUB_USER}.github.io/{INTERNAL_REPO_NAME}"
EXTERNAL_PAGES_BASE = f"https://{EXTERNAL_GITHUB_USER}.github.io/{EXTERNAL_REPO_NAME}"

INTERNAL_GITHUB_URL = f"https://github.com/{INTERNAL_GITHUB_USER}/{INTERNAL_REPO_NAME}"
EXTERNAL_GITHUB_URL = f"https://github.com/{EXTERNAL_GITHUB_USER}/{EXTERNAL_REPO_NAME}"

# 常用 URL 快捷方式
INTERNAL_HOMEPAGE  = f"{INTERNAL_PAGES_BASE}/"
EXTERNAL_HOMEPAGE  = f"{EXTERNAL_PAGES_BASE}/"
REPORT_BASE_URL    = f"{INTERNAL_PAGES_BASE}/01-daily-reports"

# ============================================================
# 3. 本地路径（相对 PROJECT_ROOT 自动计算）
# ============================================================
PROJECT_ROOT  = Path(__file__).parent.parent          # AI-Insight/
EXTERNAL_REPO = PROJECT_ROOT.parent / EXTERNAL_REPO_NAME  # ../ai-insight-public/
PUBLIC_PATH   = PROJECT_ROOT / "public"

# ============================================================
# 4. Git remote 验证（sync_to_external.py 使用）
# ============================================================
EXPECTED_REMOTE = f"github.com/{EXTERNAL_GITHUB_USER}/{EXTERNAL_REPO_NAME}"
EXTERNAL_CLONE_URL = f"{EXTERNAL_GITHUB_URL}.git"
