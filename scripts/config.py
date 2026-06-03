"""
AI-Insight 项目全局配置 — 单一真相源 (SSoT)
============================================
所有脚本的 URL、路径、仓库名称 **必须从此文件 import**，禁止硬编码。

修改说明：
  - 内部版 URL 变更 → 只改 INTERNAL_PAGES_BASE
  - 外部版 URL 变更 → 只改 EXTERNAL_PAGES_BASE
  - 项目名称变更 → 改 INTERNAL_REPO_NAME / EXTERNAL_REPO_NAME

2026-06-03: 从 GitHub Pages 迁移到 frontend-cloud（快手内部）
"""

from pathlib import Path

# ============================================================
# 1. GitHub 仓库名（Git push 仍用 GitHub）
# ============================================================
INTERNAL_GITHUB_USER = "xiaoxiong20260206"
INTERNAL_REPO_NAME   = "ai-insight"

EXTERNAL_GITHUB_USER = "xiaoxiong20260206"
EXTERNAL_REPO_NAME   = "ai-insight-public"

# ============================================================
# 2. 派生 URL（内部版 frontend-cloud，外部版 GitHub Pages）
# ============================================================
INTERNAL_PAGES_BASE = "https://ai-insight-internal.frontend-cloud.corp.kuaishou.com"
EXTERNAL_PAGES_BASE = "https://xiaoxiong20260206.github.io/ai-insight-public"

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
