#!/usr/bin/env python3
"""
ai_daily_orchestrator.py — AI日报工作流状态机 v1.4

编排AI日报的完整流程，追踪状态和上下文，支持跨会话断点恢复。
设计原则: 脚本做苦力，Agent做决策，上下文不丢失。

v1.4更新 (2026-04-06):
  - P2-2 修复: get_next_action 中 in_progress 超时检测（>60min 自动 reset 为 pending）
  - 修复场景: finalize 阶段 Step 3/4 写 in_progress 后中途被 kill，系统永久卡死
  - Step 2 complete时前置执行URL抽检（早发现早修复，减少finalize阶段返工）
  - 来自skill-dojo技能修炼P0改进项

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
  Step 2: 内容生成 [Agent]  — 生成 MD + JSON + **URL预检**
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

# 导入 SSoT 配置
sys.path.insert(0, str(SCRIPT_DIR))
from config import EXTERNAL_REPO as EXTERNAL_REPO_PATH, EXTERNAL_CLONE_URL

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
    # 无效 step 参数：返回空字符串，调用方应检查空值（v9.7修复：原缺少兜底return）
    print(f"  ⚠️ 无效的 step 参数: {raw!r}，可用值: {list(STEP_NUM_MAP.keys()) + list(STEPS)}")
    return ""

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
    1. 随机抽检3个URL的HTTP可达性（v9.8: 并发化，串行60s→并发15s）
    2. 检查禁止的封闭平台链接模式
    3. 检查结果写入 state/url_check_cache.json，供 quality_gate check_link_validity 复用
    
    v1.1新增 — 将Skill文档中的Step 2.7从"Agent手动执行"改为"自动强制执行"
    v9.8改进 — ThreadPoolExecutor并发抽检 + 结果缓存消除质量门重复HTTP请求
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
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
        
        # 2. URL抽检 — v9.8: 并发化（原串行最坏60s → 并发最坏15s）
        url_check_results = {}  # url -> True/False/None
        if all_urls:
            sample = random.sample(all_urls, min(3, len(all_urls)))
            
            def _check_one_url(url_title_pair):
                url, title = url_title_pair
                try:
                    req = urllib.request.Request(url, method='HEAD')
                    req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight Orchestrator/1.1)')
                    resp = urllib.request.urlopen(req, timeout=10)
                    if resp.status >= 400:
                        return (url, False, f"{title}({resp.status})")
                    return (url, True, title)
                except Exception:
                    try:
                        req = urllib.request.Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (AI-Insight Orchestrator/1.1)')
                        resp = urllib.request.urlopen(req, timeout=10)
                        if resp.status >= 400:
                            return (url, False, f"{title}({resp.status})")
                        return (url, True, title)
                    except Exception:
                        return (url, False, f"{title}(不可达)")
            
            unreachable = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(_check_one_url, pair): pair for pair in sample}
                try:
                    for future in as_completed(futures, timeout=20):
                        try:
                            url, ok, label = future.result()
                            url_check_results[url] = ok
                            if not ok:
                                unreachable.append(label)
                        except Exception:
                            pass
                except Exception as timeout_err:
                    # v9.9修复: as_completed timeout 不阻断 — 网络GFW导致部分URL超时是正常现象
                    print(f"  ⚠️ URL抽检部分超时（网络波动，不阻断）: {timeout_err}")
                    # 收集已完成的结果
                    for fut, (url, title) in list(futures.items()):
                        if fut.done():
                            try:
                                u, ok, label = fut.result()
                                url_check_results[u] = ok
                                if not ok:
                                    unreachable.append(label)
                            except Exception:
                                pass
            
            if unreachable:
                for u in unreachable:
                    print(f"  ⚠️ 抽检不可达: {u}")
                issues.append(f"{len(unreachable)}/{len(sample)}个抽检URL不可达")
            else:
                print(f"  ✅ URL抽检通过 ({len(sample)}个并发检查均可达)")
        
        # 3. 写入缓存供 quality_gate check_link_validity 复用（消除重复HTTP请求）
        cache = {
            "date": date,
            "created": datetime.now().isoformat(),
            "forbidden": forbidden,
            "url_check_results": url_check_results,
            "sample_count": len(url_check_results),
        }
        cache_path = state_dir(date) / "url_check_cache.json"
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
        
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

# ── 命令: status ──────────────────────────────────────────
def cmd_status(date: str):
    # v1.3 自动修复：status 时也检测 Step 2 状态漂移
    _auto_heal_step2(date)
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
    v1.3新增 (2026-04-06) — resume时自动触发Step 2状态漂移检测修复
    """
    # v1.3 自动修复：resume 时检测 Step 2 状态漂移
    _auto_heal_step2(date)
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
        (f"01-daily-reports/{month}/{date}.html", "跳转页"),  # 修复v9.7: 原来错误地指向-v3.html
    ]
    
    for rel_path, desc in key_files:
        p = PROJECT_DIR / rel_path
        if p.exists():
            size_kb = p.stat().st_size // 1024
            size_display = f"{size_kb}KB" if size_kb >= 1 else f"{p.stat().st_size}B"
            print(f"  ✅ {desc}: {rel_path} ({size_display})")
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
def _auto_heal_step2(date: str) -> bool:
    """自动修复 Step 2 状态漂移（v1.3 — 2026-04-06 修复）。
    
    场景：launchd 触发的 Agent 会话在完成内容生成后会话中断，
    导致 daily-content-{date}.json 已存在但 state.json 中 step2 仍为 pending/in_progress。
    
    修复逻辑：
    - 检查 daily-content-{date}.json 存在 且 包含 ≥ 3 个 tab
    - 若 state 中 content 步骤状态不是 completed → 自动修复为 completed
    
    返回：True = 已自动修复，False = 无需修复或文件不存在
    """
    state = load_state(date)
    if state["steps"]["content"]["status"] == "completed":
        return False  # 已正常，无需修复
    
    content_file = PROJECT_DIR / f"data/daily-content-{date}.json"
    if not content_file.exists():
        return False
    
    try:
        content = json.loads(content_file.read_text())
        tabs = content.get("tabs", [])
        if len(tabs) < 3:
            return False  # 文件存在但不完整，不自动修复
        
        # 文件完整 → 自动修复状态
        mark_step(date, "content", "completed",
                  context=f"[自动修复] daily-content-{date}.json 已存在({len(tabs)}个tab)，会话断连导致状态未落盘，已自动修复",
                  auto_healed=True)
        print(f"  🔧 [自动修复] Step 2 状态漂移已修复：daily-content-{date}.json 存在({len(tabs)}个tab)，"
              f"但 state 为 {state['steps']['content']['status']}，已自动标记为 completed")
        return True
    except Exception as e:
        print(f"  ⚠️ Step 2 自动修复检查失败: {e}")
        return False


def get_next_action(date: str) -> dict:
    state = load_state(date)
    
    # v1.3 自动修复：检测并修复 Step 2 状态漂移（Agent会话中断未落盘）
    if state["steps"]["content"]["status"] != "completed":
        if _auto_heal_step2(date):
            state = load_state(date)  # 重新加载修复后的状态

    for key in STEP_ORDER:
        step = STEPS[key]
        s = state["steps"][key]

        # v1.4 修复（P2-2）: in_progress 超时检测
        # 场景：finalize 阶段 Step 3/4 写入 in_progress 后中途被 kill，
        #        get_next_action 不处理 in_progress 导致状态永久卡死
        # 策略：若 in_progress 超过 60 分钟仍未完成，自动 reset 为 pending 触发重跑
        if s["status"] == "in_progress":
            # v9.12 修复(2026-04-07): mark_step() 写入的是 "timestamp" 字段，不是 "completed_at"/"started_at"
            # 原来只读 completed_at/started_at，两者均不存在时 completed_at=None，超时永远不触发
            completed_at = s.get("timestamp") or s.get("completed_at") or s.get("started_at")
            if completed_at:
                try:
                    from datetime import datetime, timedelta
                    started = datetime.fromisoformat(completed_at.replace("Z", "+00:00")) if "T" in completed_at else datetime.now()
                    if (datetime.now() - started.replace(tzinfo=None)) > timedelta(minutes=60):
                        print(f"  🔧 [自动修复] {step['name']} in_progress 超时(>60min)，reset 为 pending")
                        mark_step(date, key, "pending", context="[自动修复] in_progress 超时 reset")
                        state = load_state(date)
                        s = state["steps"][key]
                except Exception:
                    pass

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
            '--context "搜索了N个海外源+N次微信双轨; 发现N个热点: ...; 选定N条新闻(海外N/国内N); 微信直引N条"'
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
    """一键执行: URL抽检 → 质量门 → HTML生成 → 部署 → 外部同步 → 林克首页"""
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

    # v9.9修复: finalize时传入 fix=True，让质量门自动修复"可修复项"（MD文件/6处联动/外部同步）
    gate_ok = run_quality_gate(date, fix=True)
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

    # --- Step 4.5 + 4.6: 外部版同步 & 林克首页 — v9.8: 并行化（两者完全独立）---
    print("\n  ⚡ Step 4.5+4.6: 外部版同步 & 林克首页同步（并行执行）...")
    from concurrent.futures import ThreadPoolExecutor as _TPE, as_completed as _ac
    
    sync_ok = False
    home_ok = True  # 首页同步不阻断
    
    with _TPE(max_workers=2) as _executor:
        fut_sync = _executor.submit(run_external_sync)
        fut_home = _executor.submit(run_link_homepage_sync)
        
        # 等待两者完成（最长等 sync_to_external 的 timeout）
        for fut in _ac([fut_sync, fut_home], timeout=200):
            try:
                fut.result()
            except Exception as _e:
                print(f"  ⚠️ 并行任务异常: {_e}")
        
        try:
            sync_ok = fut_sync.result()
        except Exception as _e:
            print(f"  ❌ 外部版同步异常: {_e}")
            sync_ok = False
        try:
            home_ok = fut_home.result()
        except Exception:
            home_ok = True  # 不阻断
    
    if not sync_ok:
        mark_step(date, "deploy", "failed", error="外部版同步失败")
        print("\n🚫 外部版同步失败，finalize 中止。")
        print("   请先解决外部版仓库问题，然后重新运行 finalize。")
        return False

    mark_step(date, "deploy", "completed")
    print("  ✅ Step 4 完成")

    # ===== 4位置终态摘要（v9.10新增：用户不必从截断的部署日志里自己找） =====
    _show_4_positions_summary(date)

    print(f"\n✅ Finalize 完成！下一步: KIM推送")
    print(f"   python3 scripts/send_ai_daily.py --preview")
    return True

def _show_4_positions_summary(date: str) -> None:
    """
    finalize完成后显示4位置同步状态摘要（v9.10新增）
    
    用户在orchestrator路径下无需从截断的部署日志里自己找验证结果。
    4位置：①内部日报 ②内部首页 ③外部日报(public) ④外部仓库日报
    """
    import os
    month = date[:7]
    all_ok = True
    
    print("\n📊 4位置同步状态摘要:")
    
    # ① 内部日报
    p1 = PROJECT_DIR / "01-daily-reports" / month / f"{date}-v3.html"
    if p1.exists():
        kb = p1.stat().st_size // 1000
        print(f"  ① 内部日报:    ✅ {kb}KB")
    else:
        print(f"  ① 内部日报:    ❌ 文件不存在 ({p1.name})")
        all_ok = False
    
    # ② 内部首页
    p2 = PROJECT_DIR / "index.html"
    if p2.exists():
        content = p2.read_text(encoding="utf-8")
        has_date = date in content
        has_link = "林克" in content
        status = "✅" if (has_date and has_link) else "⚠️"
        detail = f"日期{'✅' if has_date else '❌'} 林克{'✅' if has_link else '❌(疑似污染)'}"
        print(f"  ② 内部首页:    {status} {detail}")
        if not (has_date and has_link):
            all_ok = False
    else:
        print(f"  ② 内部首页:    ❌ index.html 不存在")
        all_ok = False
    
    # ③ 外部日报 (public/)
    p3 = PROJECT_DIR / "public" / "01-daily-reports" / month / f"{date}.html"
    if p3.exists():
        kb = p3.stat().st_size // 1000
        print(f"  ③ 外部日报(public): ✅ {kb}KB")
    else:
        print(f"  ③ 外部日报(public): ❌ 不存在（需 sync_to_public --full --force）")
        all_ok = False
    
    # ④ 外部仓库日报
    p4 = EXTERNAL_REPO_PATH / "01-daily-reports" / month / f"{date}.html"
    if p4.exists():
        kb = p4.stat().st_size // 1000
        print(f"  ④ 外部仓库日报: ✅ {kb}KB")
    elif EXTERNAL_REPO_PATH.exists():
        print(f"  ④ 外部仓库日报: ❌ 仓库存在但文件不存在（需 sync_to_external --full --verify）")
        all_ok = False
    else:
        print(f"  ④ 外部仓库日报: ⚠️ 外部仓库目录不存在（先 git clone ai-insight-public）")
        all_ok = False
    
    if all_ok:
        print("  ✅ 全部4个位置已同步，可以推送KIM了！")
    else:
        print("  ⚠️ 有位置未同步，请按上方提示手动修复")


def run_quality_gate(date: str, fix: bool = False) -> bool:
    """运行质量门检查（v9.9修复: fix=True时自动修复可修复项，可修复项失败不阻断）"""
    try:
        cmd = ["python3", str(SCRIPT_DIR / "daily_quality_gate.py"), date]
        if fix:
            cmd.append("--fix")
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        print(result.stdout[-800:] if len(result.stdout) > 800 else result.stdout)
        # 检查是否有硬性失败
        if "❌ 质量门未通过" in result.stdout:
            # v9.9: 区分硬性失败 vs 可修复项失败
            # 可修复项格式: "❌ xxx: ... (可修复)"，由 --fix 后续处理
            lines = result.stdout.split("\n")
            hard_fails = [l for l in lines if l.startswith("❌") and "(可修复)" not in l and "⚠️" not in l and "质量门未通过" not in l]
            if hard_fails:
                return False
            # 所有失败都是可修复项：不阻断，打印提示
            if fix:
                print("  ✅ 质量门: 所有失败均为可修复项，已自动修复")
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
    """执行部署 (deploy_daily.sh 但跳过质量门，因为已经检查过)
    
    v9.11 修复(2026-04-07): 传入 SKIP_EXTERNAL=1 防止 deploy_daily.sh Step 6 再次执行
    sync_to_external.py —— orchestrator 的 run_external_sync() 已在 Step 4.5 独立负责外部同步，
    若两者并发执行会导致外部仓库收到两次 git push，产生竞态和重复 commit。
    """
    try:
        result = subprocess.run(
            ["bash", str(SCRIPT_DIR / "deploy_daily.sh"), date],
            capture_output=True, text=True, timeout=300,
            cwd=str(PROJECT_DIR),
            env={**__import__("os").environ, "SKIP_GATE": "1", "SKIP_EXTERNAL": "1"}  # SKIP_GATE: 已在Step3检查；SKIP_EXTERNAL: 由orchestrator Step4.5统一同步
        )
        if result.returncode == 0:
            print(f"  ✅ 部署完成")
            # 显示部署结果的最后15行（覆盖 Step 7 全部4位置验证内容）
            # ⚠️ v9.10修复: -5太少，Step 7的4位置验证（约10行）全被截断，用户看不到
            for line in result.stdout.strip().split("\n")[-15:]:
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
    """外部版同步（v9.5: 失败必须阻断）"""
    print("\n  📤 Step 4.5: 外部版同步...")
    try:
        result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "sync_to_external.py"), "--full", "--verify"],
            capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print(f"  ✅ 外部版同步完成")
            return True
        else:
            print(f"  ❌ 外部版同步失败 (exit={result.returncode})")
            print(f"     输出: {result.stdout[-500:]}" if result.stdout else "")
            print(f"     错误: {result.stderr[-500:]}" if result.stderr else "")
            print("\n  💡 如果是仓库不存在，请先执行:")
            print("     cd /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight")
            print(f"     git clone {EXTERNAL_CLONE_URL} ai-insight-public")
            return False  # v9.5: 必须阻断，不能静默通过
    except Exception as e:
        print(f"  ❌ 外部版同步异常: {e}")
        return False  # v9.5: 必须阻断


def run_link_homepage_sync() -> bool:
    """林克首页日报数据同步（v9.5 新增）"""
    print("\n  📤 Step 4.6: 林克首页日报数据同步...")
    homepage_scripts = PROJECT_DIR.parent / "scripts"
    link_homepage = PROJECT_DIR.parent / "link-homepage"
    
    if not homepage_scripts.exists():
        print(f"  ⚠️ 首页脚本目录不存在: {homepage_scripts}")
        print("     跳过林克首页更新（不阻断）")
        return True  # 不阻断，因为这是可选依赖
    
    try:
        # Step 1: 生成日报数据
        result = subprocess.run(
            ["python3", str(homepage_scripts / "generate_daily_report.py")],
            capture_output=True, text=True, timeout=60, cwd=str(PROJECT_DIR.parent)
        )
        if result.returncode != 0:
            print(f"  ⚠️ 日报数据生成失败: {result.stderr[:200]}")
            return True  # 不阻断
        
        # Step 2: 部署首页
        result = subprocess.run(
            ["bash", str(homepage_scripts / "update-homepage.sh"), "auto: 日报联动更新"],
            capture_output=True, text=True, timeout=180, cwd=str(PROJECT_DIR.parent)
        )
        if result.returncode == 0:
            print(f"  ✅ 林克首页更新完成")
        else:
            print(f"  ⚠️ 林克首页部署警告: {result.stderr[:200]}")
        
        return True
    except Exception as e:
        print(f"  ⚠️ 林克首页更新异常: {e}")
        return True  # 不阻断

# ── 命令: push (Step 5) ──────────────────────────────────
def cmd_push(date: str, preview_only: bool = True) -> bool:
    """KIM推送（默认 preview_only=True，即私发给 shenlang，不发群）
    AI 日报统一走 --preview 模式（私发）；如需群发需显式传入 preview_only=False。
    """
    # 2026-04-02 修复：日报 Step5 统一私发（--preview），禁止默认群发
    # 根因：之前 preview_only=False 导致直接群发，违反 Skill 规范
    args = ["python3", str(SCRIPT_DIR / "send_ai_daily.py"), date, "--preview"]

    print(f"\n📤 KIM私发（--preview → shenlang）: {date}")
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=120, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            print(result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)
            mark_step(date, "push", "completed")
            return True
        else:
            print(f"  ❌ 推送失败: {result.stderr[:200]}")
            mark_step(date, "push", "failed", error=f"exit={result.returncode}")
            return False
    except Exception as e:
        print(f"  ❌ 推送异常: {e}")
        return False

# ── CLI ───────────────────────────────────────────────────
def parse_args():
    args = {"command": None, "date": None, "step_raw": None, 
            "preview": False, "context": None, "artifacts": None, "issues": None}
    argv = sys.argv  # 先捕获sys.argv引用
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--date" and i + 1 < len(argv):
            args["date"] = argv[i + 1]; i += 2
        elif arg == "--step" and i + 1 < len(argv):
            args["step_raw"] = argv[i + 1]; i += 2
        elif arg == "--context" and i + 1 < len(argv):
            args["context"] = argv[i + 1]; i += 2
        elif arg == "--artifacts" and i + 1 < len(argv):
            args["artifacts"] = argv[i + 1]; i += 2
        elif arg == "--issues" and i + 1 < len(argv):
            args["issues"] = argv[i + 1]; i += 2
        elif arg == "--preview":
            args["preview"] = True; i += 1
        elif not arg.startswith("--") and args["command"] is None:
            args["command"] = arg; i += 1
        else:
            i += 1
    if not args["date"]:
        args["date"] = datetime.now().strftime("%Y-%m-%d")
    # 日期格式验证：必须是YYYY-MM-DD格式，防止斜杠/无分隔符等错误格式导致断点恢复失效
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', args["date"]):
        print(f"❌ 日期格式错误: {args['date']!r}，必须是YYYY-MM-DD格式，例: 2026-03-20")
        sys.exit(1)
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
        # v1.2: Step 2完成时前置执行URL抽检（早发现早修复，减少finalize阶段的返工）
        if step_key == "content":
            save_source_snapshot(date)
            print("\n📋 Step 2.7 前置检查: URL抽检 + 封闭平台链接合规")
            url_ok = run_url_spot_check(date)
            if not url_ok:
                print("  ⚠️ 发现链接问题，建议在finalize前修复（finalize会再次检查）")
            else:
                print("  ✅ URL抽检预检通过，可以安全执行 finalize")

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
