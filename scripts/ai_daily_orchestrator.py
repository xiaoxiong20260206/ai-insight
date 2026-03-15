#!/usr/bin/env python3
"""
ai_daily_orchestrator.py — AI日报工作流状态机 v1.0

编排AI日报的完整流程，追踪状态，支持断点恢复。
设计原则: 脚本做苦力，Agent做决策。

工作流:
  Step 1: 搜索调研 [Agent]  — 热点探针 + 两层搜索 + 内容筛选
  Step 2: 内容生成 [Agent]  — 生成 MD + JSON
  Step 3: 质量验证 [脚本]   — 质量门 + HTML生成
  Step 4: 部署发布 [脚本]   — git deploy + 外部同步
  Step 5: KIM推送  [Agent确认] — 预览 → 用户确认 → 发群

用法:
  python3 scripts/ai_daily_orchestrator.py status [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py next   [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py complete --step N [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py finalize [--date YYYY-MM-DD]   # 运行 Step 3+4
  python3 scripts/ai_daily_orchestrator.py push [--date YYYY-MM-DD]       # 运行 Step 5
  python3 scripts/ai_daily_orchestrator.py reset --step N [--date YYYY-MM-DD]
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent

# ── Step 定义 ─────────────────────────────────────────────
STEPS = {
    "search":   {"name": "搜索调研",   "executor": "agent",  "step_num": 1},
    "content":  {"name": "内容生成",   "executor": "agent",  "step_num": 2},
    "validate": {"name": "质量验证",   "executor": "script", "step_num": 3},
    "deploy":   {"name": "部署发布",   "executor": "script", "step_num": 4},
    "push":     {"name": "KIM推送",   "executor": "agent",  "step_num": 5},
}

STEP_ORDER = ["search", "content", "validate", "deploy", "push"]
STEP_NUM_MAP = {str(s["step_num"]): k for k, s in STEPS.items()}  # "1" → "search"

# ── 状态管理 ──────────────────────────────────────────────
def state_dir(date: str) -> Path:
    d = PROJECT_DIR / "data" / "daily-workflow" / date
    d.mkdir(parents=True, exist_ok=True)
    return d

def state_path(date: str) -> Path:
    return state_dir(date) / "state.json"

def load_state(date: str) -> dict:
    p = state_path(date)
    if p.exists():
        return json.loads(p.read_text())
    return {
        "date": date,
        "steps": {k: {"status": "pending"} for k in STEP_ORDER},
        "created": datetime.now().isoformat(),
    }

def save_state(date: str, state: dict):
    state["updated"] = datetime.now().isoformat()
    state_path(date).write_text(json.dumps(state, indent=2, ensure_ascii=False))

def mark_step(date: str, step_key: str, status: str, **extra):
    state = load_state(date)
    # 重置时清理旧字段
    if status == "pending":
        state["steps"][step_key] = {"status": "pending"}
    else:
        state["steps"][step_key]["status"] = status
        state["steps"][step_key]["timestamp"] = datetime.now().strftime("%H:%M:%S")
        for k, v in extra.items():
            state["steps"][step_key][k] = v
        # 清理不相关字段
        if status == "completed" and "error" in state["steps"][step_key]:
            del state["steps"][step_key]["error"]
    save_state(date, state)

def resolve_step(raw: str) -> str:
    """将 step 编号转为内部 key"""
    if not raw:
        return ""
    if raw in STEP_NUM_MAP:
        return STEP_NUM_MAP[raw]
    if raw in STEPS:
        return raw
    return raw

# ── 命令: status ──────────────────────────────────────────
def cmd_status(date: str):
    state = load_state(date)
    icons = {"pending": "⬜", "completed": "✅", "failed": "❌", "skipped": "⏭️"}

    print(f"\n📋 AI日报工作流状态 — {date}")
    print("=" * 50)
    for key in STEP_ORDER:
        step = STEPS[key]
        s = state["steps"][key]
        icon = icons.get(s["status"], "❓")
        ts = f' [{s["timestamp"]}]' if "timestamp" in s else ""
        err = f' ⚠️ {s["error"][:60]}' if s.get("error") else ""
        print(f"  {icon} Step {step['step_num']}  {step['name']} [{step['executor']}]{ts}{err}")

    # 下一步提示
    nxt = get_next_action(date)
    if nxt["action"] == "all_done":
        print(f"\n ✅ 日报已完成！")
    else:
        retry = " (重试)" if nxt.get("is_retry") else ""
        print(f"\n 下一步: Step {nxt['step']} {nxt['description']}{retry}")
    print()

# ── 命令: next ────────────────────────────────────────────
def get_next_action(date: str) -> dict:
    state = load_state(date)

    for key in STEP_ORDER:
        step = STEPS[key]
        s = state["steps"][key]

        if s["status"] in ("pending", "failed"):
            is_retry = s["status"] == "failed"
            num = step["step_num"]

            if step["executor"] == "agent":
                return {
                    "action": "agent_review",
                    "step": num,
                    "step_key": key,
                    "description": step["name"],
                    "is_retry": is_retry,
                    "instruction": _agent_instruction(key, date, is_retry),
                }
            else:
                cmd = _script_command(key, date)
                return {
                    "action": "run_script",
                    "step": num,
                    "step_key": key,
                    "description": step["name"],
                    "is_retry": is_retry,
                    "command": cmd,
                }

    return {"action": "all_done", "date": date}

def _agent_instruction(key: str, date: str, is_retry: bool) -> str:
    if key == "search":
        return (
            f"执行AI日报搜索调研 ({date})。"
            "按 daily-report/workflow.md 的 Step 0.5 + Step 1 + Step 2 执行。"
            "完成后执行: python3 scripts/ai_daily_orchestrator.py complete --step 1"
        )
    elif key == "content":
        return (
            f"生成AI日报内容 ({date})。"
            "按 daily-report/workflow.md 的 Step 3 生成 MD + JSON 文件。"
            "完成后执行: python3 scripts/ai_daily_orchestrator.py complete --step 2"
        )
    elif key == "push":
        prefix = "重试" if is_retry else "执行"
        return (
            f"{prefix}KIM推送 ({date})。"
            "先预览: python3 scripts/send_ai_daily.py --preview\n"
            "确认后发群: python3 scripts/send_ai_daily.py\n"
            "完成后执行: python3 scripts/ai_daily_orchestrator.py complete --step 5"
        )
    return ""

def _script_command(key: str, date: str) -> str:
    if key == "validate":
        return f"python3 scripts/ai_daily_orchestrator.py finalize --date {date}"
    elif key == "deploy":
        return f"python3 scripts/ai_daily_orchestrator.py finalize --date {date}"
    return ""

# ── 命令: finalize (Step 3 + Step 4) ─────────────────────
def cmd_finalize(date: str) -> bool:
    """一键执行: 质量门 → HTML生成 → 部署 → 外部同步"""
    print(f"\n🚀 AI日报 Finalize: {date}")
    print("=" * 50)

    # --- Step 3: 质量验证 ---
    print("\n📋 Step 3: 质量门检查")
    mark_step(date, "validate", "in_progress")

    gate_ok = run_quality_gate(date)
    if not gate_ok:
        mark_step(date, "validate", "failed", error="质量门未通过")
        print("\n🚫 质量门失败，请修复后重试。")
        print("   提示: 回到 Step 1/2 修复内容，不要修改数据绕过检查。")
        return False

    # HTML 生成
    html_ok = run_html_gen(date)
    if not html_ok:
        mark_step(date, "validate", "failed", error="HTML生成失败")
        return False

    mark_step(date, "validate", "completed")
    print("  ✅ Step 3 完成")

    # --- Step 4: 部署发布 ---
    print("\n📋 Step 4: 部署发布")
    mark_step(date, "deploy", "in_progress")

    deploy_ok = run_deploy(date)
    if not deploy_ok:
        mark_step(date, "deploy", "failed", error="部署失败")
        return False

    sync_ok = run_external_sync()
    if not sync_ok:
        mark_step(date, "deploy", "failed", error="外部同步失败")
        return False

    mark_step(date, "deploy", "completed")
    print("  ✅ Step 4 完成")

    print(f"\n✅ Finalize 完成！下一步: KIM推送")
    print(f"   python3 scripts/send_ai_daily.py --preview")
    return True

def run_quality_gate(date: str) -> bool:
    """运行质量门检查"""
    try:
        result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "daily_quality_gate.py"), date],
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        # 检查是否有硬性失败
        if "❌ 质量门未通过" in result.stdout:
            # 区分 warning vs hard fail
            lines = result.stdout.split("\n")
            hard_fails = [l for l in lines if l.startswith("❌") and "⚠️" not in l]
            if hard_fails:
                return False
        return True
    except Exception as e:
        print(f"  ❌ 质量门执行失败: {e}")
        return False

def run_html_gen(date: str) -> bool:
    """生成HTML页面"""
    try:
        result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "gen_daily_html.py"), date],
            capture_output=True, text=True, timeout=60, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print(f"  ✅ HTML生成完成")
            return True
        else:
            print(f"  ❌ HTML生成失败: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ HTML生成异常: {e}")
        return False

def run_deploy(date: str) -> bool:
    """执行部署 (deploy_daily.sh 但跳过质量门，因为已经检查过)"""
    try:
        result = subprocess.run(
            ["bash", str(SCRIPT_DIR / "deploy_daily.sh"), date],
            capture_output=True, text=True, timeout=300,
            cwd=str(PROJECT_DIR),
            env={**__import__("os").environ, "SKIP_GATE": "1"}  # 已在 Step 3 检查过
        )
        if result.returncode == 0:
            print(f"  ✅ 部署完成")
            # 显示部署结果的最后几行
            for line in result.stdout.strip().split("\n")[-5:]:
                print(f"    {line}")
            return True
        else:
            print(f"  ❌ 部署失败 (exit={result.returncode})")
            print(f"    {result.stderr[:300]}")
            return False
    except Exception as e:
        print(f"  ❌ 部署异常: {e}")
        return False

def run_external_sync() -> bool:
    """外部版同步"""
    try:
        result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "sync_to_external.py"), "--full", "--verify"],
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print(f"  ✅ 外部同步完成")
            return True
        else:
            print(f"  ⚠️ 外部同步警告 (exit={result.returncode})")
            # 不阻断，只记录
            return True
    except Exception as e:
        print(f"  ⚠️ 外部同步异常: {e}")
        return True  # 不阻断

# ── 命令: push (Step 5) ──────────────────────────────────
def cmd_push(date: str, preview_only: bool = False) -> bool:
    """KIM推送"""
    args = ["python3", str(SCRIPT_DIR / "send_ai_daily.py"), date]
    if preview_only:
        args.append("--preview")

    print(f"\n📤 KIM{'预览' if preview_only else '推送'}: {date}")
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print(result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)
            if not preview_only:
                mark_step(date, "push", "completed")
            return True
        else:
            print(f"  ❌ 推送失败: {result.stderr[:200]}")
            if not preview_only:
                mark_step(date, "push", "failed", error=f"exit={result.returncode}")
            return False
    except Exception as e:
        print(f"  ❌ 推送异常: {e}")
        return False

# ── CLI ───────────────────────────────────────────────────
def parse_args():
    args = {"command": None, "date": None, "step_raw": None, "preview": False}
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--date" and i + 1 < len(sys.argv):
            args["date"] = sys.argv[i + 1]; i += 2
        elif arg == "--step" and i + 1 < len(sys.argv):
            args["step_raw"] = sys.argv[i + 1]; i += 2
        elif arg == "--preview":
            args["preview"] = True; i += 1
        elif not arg.startswith("--") and args["command"] is None:
            args["command"] = arg; i += 1
        else:
            i += 1
    if not args["date"]:
        args["date"] = datetime.now().strftime("%Y-%m-%d")
    return args

def main():
    args = parse_args()
    date = args["date"]
    cmd = args["command"] or "status"
    step_key = resolve_step(args["step_raw"] or "") if args["step_raw"] else None

    if cmd == "status":
        cmd_status(date)

    elif cmd == "next":
        action = get_next_action(date)
        print(json.dumps(action, indent=2, ensure_ascii=False))

    elif cmd == "complete":
        if not step_key:
            print("❌ 需要 --step N 参数"); sys.exit(1)
        mark_step(date, step_key, "completed")
        step = STEPS[step_key]
        print(f"✅ Step {step['step_num']}  {step['name']} 已标记完成")

    elif cmd == "reset":
        if not step_key:
            print("❌ 需要 --step N 参数"); sys.exit(1)
        mark_step(date, step_key, "pending")
        step = STEPS[step_key]
        print(f"🔄 Step {step['step_num']}  {step['name']} 已重置")

    elif cmd == "finalize":
        cmd_finalize(date)

    elif cmd == "push":
        cmd_push(date, preview_only=args["preview"])

    else:
        print(f"未知命令: {cmd}")
        print("可用: status, next, complete, reset, finalize, push")
        sys.exit(1)

if __name__ == "__main__":
    main()
