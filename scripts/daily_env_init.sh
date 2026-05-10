#!/bin/bash
# AI日报环境初始化脚本 — 固化环境检查，不再靠agent"记得"
# 用法: source scripts/daily_env_init.sh
# 或: bash scripts/daily_env_init.sh && export PATH=...

set -e

echo "=== AI日报环境初始化 ==="

# 1. PATH 设置
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"
echo "[1/4] PATH 已设置: $PATH"

# 2. uv 检查
if command -v uv &>/dev/null; then
    UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
    echo "[2/4] ✅ uv 可用: $UV_VERSION"
else
    echo "[2/4] ❌ uv 不可用，尝试安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        echo "[2/4] ✅ uv 安装成功: $(uv --version)"
    else
        echo "[2/4] ⛔ uv 安装失败，日报无法继续"
        exit 1
    fi
fi

# 3. python3 检查
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>/dev/null || echo "unknown")
    echo "[3/4] ✅ python3 可用: $PY_VERSION"
else
    echo "[3/4] ⛔ python3 不可用，日报无法继续"
    exit 1
fi

# 4. Git 检查
if command -v git &>/dev/null; then
    echo "[4/4] ✅ git 可用: $(git --version)"
else
    echo "[4/4] ⛔ git 不可用"
    exit 1
fi

echo "=== 环境初始化完成，所有工具可用 ==="
echo "⚠️ 注意: 所有脚本命令必须用 python3（不是 python）和 uv run（不是 python/python3 直接执行带依赖的脚本）"