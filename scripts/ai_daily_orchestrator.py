#!/usr/bin/env python3
"""
ai_daily_orchestrator.py — AI日报工作流状态机 v1.2

编排AI日报的完整流程，追踪状态和上下文，支持跨会话断点恢复。
设计原则: 脚本做苦力，Agent做决策，上下文不丢失。

v1.2更新 (2026-03-15):
  - complete --context: 步骤完成时记录上下文摘要（搜了什么/选了什么/为什么）
  - resume命令: 新会话第一个命令，输出结构化恢复简报（比status更丰富）
  - status增强: 附带已完成步骤的context摘要
  - Session Resume Protocol: 跨会话接力的根治方案

v1.1更新 (2026-03-15):
  - Step 2 complete时自动保存source字段快照（篡改检测基础）
  - finalize前新增Step 2.7: URL抽检+封闭平台链接合规（原手动步骤已脚本化）
  - 快照+质量门v8.0联动: 阻断source日期篡改绕过行为

工作流:
  Step 1: 搜索调研 [Agent]  — 热点探针 + 两层搜索 + 内容筛选
  Step 2: 内容生成 [Agent]  — 生成 MD + JSON
  Step 3: 质量验证 [脚本]   — 质量门 + HTML生成
  Step 4: 部署发布 [脚本]   — git deploy + 外部同步
  Step 5: KIM推送  [Agent确认] — 预览 → 用户确认 → 发群

用法:
  python3 scripts/ai_daily_orchestrator.py status [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py resume [--date YYYY-MM-DD]    # 跨会话恢复简报
  python3 scripts/ai_daily_orchestrator.py next   [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py complete --step N [--context "..."] [--date YYYY-MM-DD]
  python3 scripts/ai_daily_orchestrator.py finalize [--date YYYY-MM-DD]   # 运行 Step 3+4
  python3 scripts/ai_daily_orchestrator.py push [--date YYYY-MM-DD]       # 运行 Step 5
  python3 scripts/ai_daily_orchestrator.py reset --step N [--date YYYY-MM-DD]
"""

import hashlib
import json
import random
import re
import subprocess
import sys
import urllib.request
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

# ── Source快照 (v1.1 篡改检测) ─────────────────────────
def save_source_snapshot(date: str):
    """Step 2完成时保存source字段快照，用于后续质量门的篡改检测。
    
    机制: 记录所有source字段的原始内容和MD5 hash。
    如果Step 2完成后source被修改（但Step 2没被reset），质量门会报错。
    
    v1.1新增 (2026-03-15经验)
    """
    json_path = PROJECT_DIR / "data" / f"daily-content-{date}.json"
    if not json_path.exists():
        print(f"  ⚠️ JSON不存在，跳过快照保存")
        return
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        sources = []
        for tab_idx, tab in enumerate(data.get("tabs", [])):
            for region in ["overseas", "china"]:
                for idx, item in enumerate(tab.get("news", {}).get(region, [])):
                    sources.append({
                        "tab": tab_idx, "region": region, "idx": idx,
                        "source": item.get("source", ""),
                        "title": item.get("title", "")[:50]
                    })
        
        sources_json = json.dumps(sources, ensure_ascii=False)
        snapshot = {
            "created": datetime.now().isoformat(),
            "step": 2,
            "sources_hash": hashlib.md5(sources_json.encode()).hexdigest(),
            "sources_count": len(sources),
            "sources": sources,
        }
        
        snapshot_path = state_dir(date) / "source_snapshot.json"
        snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
        print(f"  📸 Source快照已保存 ({len(sources)}条, hash={snapshot['sources_hash'][:8]})")
    except Exception as e:
        print(f"  ⚠️ 快照保存失败: {e}")


def run_url_spot_check(date: str) -> bool:
    """Step 2.7脚本化: URL真实性抽检 + 封闭平台链接合规
    
    在finalize (Step 3+4) 之前自动执行:
    1. 随机抽检3个URL的HTTP可达性
    2. 检查禁止的封闭平台链接模式
    
    v1.1新增 — 将Skill文档中的Step 2.7从"Agent手动执行"改为"自动强制执行"
    """
    json_path = PROJECT_DIR / "data" / f"daily-content-{date}.json"
    if not json_path.exists():
        print(f"  ❌ JSON不存在")
        return False
    
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        
        # 收集所有URL
        all_urls = []
        forbidden = []
        
        FORBIDDEN_PATTERNS = [
            (r'mp\.weixin\.qq\.com', 'mp.weixin临时链接(约6h过期)'),
            (r'weixin\.sogou\.com/link\?', '搜狗跳转链接(数小时过期)'),
        ]
        
        for tab in data.get("tabs", []):
            for region in ['overseas', 'china']:
                for item in tab.get('news', {}).get(region, []):
                    url = item.get('url', '')
                    title = item.get('title', '')[:30]
                    
                    if url and url.startswith('http'):
                        all_urls.append((url, title))
                        
                        # 检查封闭平台禁止项
                        for pattern, desc in FORBIDDEN_PATTERNS:
                            if re.search(pattern, url):
                                forbidden.append(f"{title} → {desc}")
                                break
        
        issues = []
        
        # 1. 封闭平台链接检查
        if forbidden:
            for f in forbidden:
                print(f"  ❌ 禁止链接: {f}")
            issues.append(f"{len(forbidden)}个禁止的封闭平台链接")
        
        # 2. URL抽检 (最多3个)
        if all_urls:
            sample = random.sample(all_urls, min(3, len(all_urls)))
            unreachable = []
            for url, title in sample:
                try:
                    req = urllib.request.Request(url, method='HEAD')
                    req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight Orchestrator/1.1)')
                    resp = urllib.request.urlopen(req, timeout=10)
                    if resp.status >= 400:
                        unreachable.append(f"{title}({resp.status})")
                except Exception:
                    try:
                        req = urllib.request.Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight Orchestrator/1.1)')
                        resp = urllib.request.urlopen(req, timeout=10)
                        if resp.status >= 400:
                            unreachable.append(f"{title}({resp.status})")
                    except Exception:
                        unreachable.append(f"{title}(不可达)")
            
            if unreachable:
                for u in unreachable:
                    print(f"  ⚠️ 抽检不可达: {u}")
                issues.append(f"{len(unreachable)}/{len(sample)}个抽检URL不可达")
            else:
                print(f"  ✅ URL抽检通过 ({len(sample)}个均可达)")
        
        if issues:
            # 封闭平台链接是硬性失败，URL不可达是警告
            if forbidden:
                return False
            # URL不可达仅警告，不阻断（网络波动可能导致假阳性）
            print(f"  ⚠️ URL抽检有问题但不阻断（可能是网络波动）")
        
        return True
    except Exception as e:
        print(f"  ❌ URL抽检异常: {e}")
        return False
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
        # v1.2: 显示context摘要（截断到80字符）
        ctx = s.get("context", "")
        if ctx:
            print(f"       {ctx[:80]}{'...' if len(ctx) > 80 else ''}")

    # 下一步提示
    nxt = get_next_action(date)
    if nxt["action"] == "all_done":
        print(f"\n ✅ 日报已完成！")
    else:
        retry = " (重试)" if nxt.get("is_retry") else ""
        print(f"\n 下一步: Step {nxt['step']} {nxt['description']}{retry}")
    print()


# ── 命令: resume (v1.2 跨会话恢复) ───────────────────────
def cmd_resume(date: str):
    """生成结构化的跨会话恢复简报。
    
    新会话接力时的第一个命令。比status更丰富：
    - 输出每个已完成步骤的context摘要（做了什么、为什么这么做）
    - 扫描关键产出文件的存在性和大小
    - 读取source快照信息
    - 收集所有遗留issues
    - 给出明确的下一步操作指令
    
    v1.2新增 (2026-03-15经验 — 跨会话上下文丢失根治方案)
    """
    state = load_state(date)
    
    # 统计进度
    completed = sum(1 for k in STEP_ORDER if state["steps"][k]["status"] == "completed")
    total = len(STEP_ORDER)
    
    print(f"\n🔄 AI日报工作流恢复 — {date}")
    print("=" * 50)
    
    nxt = get_next_action(date)
    if nxt["action"] == "all_done":
        print(f"📍 进度: {completed}/{total} 全部完成")
    else:
        print(f"📍 进度: {completed}/{total} 已完成, 下一步: Step {nxt['step']} {nxt['description']}")
    
    # ── 已完成步骤摘要 ──
    has_context = False
    has_issues = False
    all_issues = []
    
    print(f"\n📋 已完成步骤:")
    for key in STEP_ORDER:
        step = STEPS[key]
        s = state["steps"][key]
        if s["status"] != "completed":
            continue
        
        ts = s.get("timestamp", "")
        ctx = s.get("context", "")
        issues = s.get("issues", [])
        
        print(f"  Step {step['step_num']} {step['name']} [{ts}]:")
        if ctx:
            has_context = True
            # 按分号分行显示
            for part in ctx.split(";"):
                part = part.strip()
                if part:
                    print(f"    {part}")
        else:
            print(f"    (无上下文记录 — 建议reset后用 --context 重新complete)")
        
        if issues:
            has_issues = True
            for issue in issues:
                print(f"    ⚠️ {issue}")
                all_issues.append(issue)
    
    # ── 产出文件扫描 ──
    print(f"\n📦 产出文件:")
    month = date[:7]  # YYYY-MM
    key_files = [
        (f"data/daily-content-{date}.json", "JSON数据"),
        (f"01-daily-reports/{month}/{date}.md", "Markdown"),
        (f"01-daily-reports/{month}/{date}-v3.html", "HTML页面"),
        (f"01-daily-reports/{month}/{date}-v3.html", "跳转页"),
    ]
    
    for rel_path, desc in key_files:
        p = PROJECT_DIR / rel_path
        if p.exists():
            size = p.stat().st_size
            lines = len(p.read_text(encoding="utf-8").splitlines()) if size < 500000 else "?"
            print(f"  ✅ {desc}: {rel_path} ({lines}行)")
        else:
            print(f"  ❌ {desc}: {rel_path} (不存在)")
    
    # ── Source快照 ──
    snapshot_path = state_dir(date) / "source_snapshot.json"
    if snapshot_path.exists():
        try:
            snap = json.loads(snapshot_path.read_text())
            print(f"\n📸 Source快照: {snap.get('sources_count', '?')}条, "
                  f"hash={snap.get('sources_hash', '?')[:12]}, "
                  f"创建于 {snap.get('created', '?')[:16]}")
        except Exception:
            print(f"\n📸 Source快照: 存在但读取失败")
    else:
        print(f"\n📸 Source快照: 不存在")
    
    # ── 遗留问题 ──
    if all_issues:
        print(f"\n⚠️ 遗留问题 ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  - {issue}")
    
    # ── 无上下文提醒 ──
    if not has_context:
        print(f"\n💡 提示: 所有已完成步骤均无context记录。")
        print(f"   建议后续complete时使用 --context 参数保存上下文:")
        print(f"   python3 scripts/ai_daily_orchestrator.py complete --step N --context \"做了什么;关键决策;遗留问题\"")
    
    # ── 下一步 ──
    if nxt["action"] != "all_done":
        print(f"\n▶️ 下一步:")
        if nxt["action"] == "agent_review":
            print(f"  {nxt.get('instruction', '')}")
        else:
            print(f"  {nxt.get('command', '')}")
    else:
        print(f"\n✅ 工作流已全部完成，无待执行步骤。")
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
            "完成后执行: python3 scripts/ai_daily_orchestrator.py complete --step 1 "
            '--context "搜索了N个海外源+N次微信双轨+N次小红书; 发现N个热点: ...; 选定N条新闻(海外N/国内N); 微信直引N条"'
        )
    elif key == "content":
        return (
            f"生成AI日报内容 ({date})。"
            "按 daily-report/workflow.md 的 Step 3 生成 MD + JSON 文件。"
            "完成后执行: python3 scripts/ai_daily_orchestrator.py complete --step 2 "
            '--context "N条新闻(海外N/国内N), N个板块; 微信直引N条; 关键编辑决策: ..."'
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
    """一键执行: URL抽检 → 质量门 → HTML生成 → 部署 → 外部同步"""
    print(f"\n🚀 AI日报 Finalize: {date}")
    print("=" * 50)

    # --- Step 2.7: URL抽检 (v1.1新增，原Skill文档手动步骤现已自动化) ---
    print("\n📋 Step 2.7: URL抽检 + 封闭平台链接合规")
    url_ok = run_url_spot_check(date)
    if not url_ok:
        print("\n🚫 URL抽检失败（存在禁止的封闭平台链接），请修复后重试。")
        print("   提示: 回到 Step 1/2 替换违规链接。")
        return False
    print("  ✅ Step 2.7 通过")

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
    args = {"command": None, "date": None, "step_raw": None, 
            "preview": False, "context": None, "artifacts": None, "issues": None}
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--date" and i + 1 < len(sys.argv):
            args["date"] = sys.argv[i + 1]; i += 2
        elif arg == "--step" and i + 1 < len(sys.argv):
            args["step_raw"] = sys.argv[i + 1]; i += 2
        elif arg == "--context" and i + 1 < len(sys.argv):
            args["context"] = sys.argv[i + 1]; i += 2
        elif arg == "--artifacts" and i + 1 < len(sys.argv):
            args["artifacts"] = sys.argv[i + 1]; i += 2
        elif arg == "--issues" and i + 1 < len(sys.argv):
            args["issues"] = sys.argv[i + 1]; i += 2
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
        
        # v1.2: 收集上下文参数
        extra = {}
        if args.get("context"):
            extra["context"] = args["context"]
        if args.get("artifacts"):
            extra["artifacts"] = [a.strip() for a in args["artifacts"].split(",")]
        if args.get("issues"):
            extra["issues"] = [i.strip() for i in args["issues"].split(",")]
        
        mark_step(date, step_key, "completed", **extra)
        step = STEPS[step_key]
        print(f"✅ Step {step['step_num']}  {step['name']} 已标记完成")
        
        if extra.get("context"):
            print(f"  📝 上下文: {extra['context'][:80]}{'...' if len(extra['context']) > 80 else ''}")
        else:
            print(f"  💡 建议: 使用 --context \"做了什么;关键决策\" 记录上下文，便于跨会话恢复")
        
        # v1.1: Step 2完成时自动保存source快照
        if step_key == "content":
            save_source_snapshot(date)

    elif cmd == "reset":
        if not step_key:
            print("❌ 需要 --step N 参数"); sys.exit(1)
        mark_step(date, step_key, "pending")
        step = STEPS[step_key]
        print(f"🔄 Step {step['step_num']}  {step['name']} 已重置")

    elif cmd == "resume":
        cmd_resume(date)

    elif cmd == "finalize":
        cmd_finalize(date)

    elif cmd == "push":
        cmd_push(date, preview_only=args["preview"])

    else:
        print(f"未知命令: {cmd}")
        print("可用: status, resume, next, complete, reset, finalize, push")
        sys.exit(1)

if __name__ == "__main__":
    main()
