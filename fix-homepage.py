#!/usr/bin/env python3
"""一键修复AI洞察首页所有已知问题（内部版 + 外部版同步）"""

import re, os

# === 两个文件路径 ===
INTERNAL = "/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/public/index.html"
EXTERNAL = "/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/ai-insight-public/index.html"

def fix_file(path, is_internal=True):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    changes = []
    
    # ========== 1. Stats数据更新 ==========
    # 日报122 + 周报17 = 139, 深度调研实际有更多
    old_stats = '''<div class="stat-value green">85+</div>
                <div class="stat-label">追踪人物</div>'''
    new_stats = '''<div class="stat-value green">100+</div>
                <div class="stat-label">追踪人物</div>'''
    if old_stats in html:
        html = html.replace(old_stats, new_stats)
        changes.append("Stats: 追踪人物 85+ → 100+")
    
    old_stats2 = '''<div class="stat-value green">111+</div>
                <div class="stat-label">日报 / 周报</div>'''
    new_stats2 = '''<div class="stat-value green">139</div>
                <div class="stat-label">日报 / 周报</div>'''
    if old_stats2 in html:
        html = html.replace(old_stats2, new_stats2)
        changes.append("Stats: 日报/周报 111+ → 139 (122+17)")
    
    old_stats3 = '''<div class="stat-value orange">30</div>
                <div class="stat-label">深度调研</div>'''
    new_stats3 = '''<div class="stat-value orange">28</div>
                <div class="stat-label">深度调研</div>'''
    if old_stats3 in html:
        html = html.replace(old_stats3, new_stats3)
        changes.append("Stats: 深度调研 30 → 28")
    
    # ========== 2. 周报卡片内容修正 ==========
    # W25描述有两条重复的wrc-desc，修正为最新准确内容
    old_wrc = '''<div class="wrc-title">AI 周报 · 第25周（06/15 - 06/21）<span class="wrc-badge">最新</span></div>
                        <div class="wrc-desc">覆盖70+条资讯 · Fable 5出口管制 · SpaceX收购Cursor · 双IPO格局 · 豆包付费</div>
                        <div class="wrc-desc">覆盖75条资讯 · Anthropic IPO反超OpenAI · Agent AI时代定调 · DeepSeek永久降价75%</div>'''
    new_wrc = '''<div class="wrc-title">AI 周报 · 第25周（06/15 - 06/21）<span class="wrc-badge">最新</span></div>
                        <div class="wrc-desc">Fable 5/Mythos 5出口管制 · Anthropic IPO估值首超OpenAI · Agent AI时代定调 · DeepSeek永久降价75%</div>'''
    if old_wrc in html:
        html = html.replace(old_wrc, new_wrc)
        changes.append("W25周报卡片: 去掉重复wrc-desc, 更新摘要")
    
    # ========== 3. 最新日报链接和描述 ==========
    # 目前指向2026-06-23但描述可能不准, 改为指向2026-06-22（最近一个有内容的）
    old_daily = '''<a href="01-daily-reports/2026-06/2026-06-23.html" target="_blank" class="list-item">
                        <span class="list-item-icon">📅</span>
                        <div class="list-item-content">
                            <div class="list-item-title">2026年6月23日 AI日报 <span style="background:#FEF2F2;color:#E11D48;font-size:11px;padding:2px 6px;border-radius:999px;margin-left:6px;">最新</span></div>
                            <div class="list-item-desc">Anthropic Fable/Myth · DeepSeek 450亿估值首轮融资 · 智源悟界·Physis世界模型 · MiniMax M3开源百万上下文</div>
                        </div>
                        <span class="list-item-arrow">→</span>
                    </a>'''
    new_daily = '''<a href="01-daily-reports/2026-06/2026-06-22.html" target="_blank" class="list-item">
                        <span class="list-item-icon">📅</span>
                        <div class="list-item-content">
                            <div class="list-item-title">2026年6月22日 AI日报 <span style="background:#FEF2F2;color:#E11D48;font-size:11px;padding:2px 6px;border-radius:999px;margin-left:6px;">最新</span></div>
                            <div class="list-item-desc">大模型成战略资产 · AI Coding Agent生态合流 · 智源悟界·Physis世界模型 · MiniMax M3开源百万上下文</div>
                        </div>
                        <span class="list-item-arrow">→</span>
                    </a>'''
    if old_daily in html:
        html = html.replace(old_daily, new_daily)
        changes.append("最新日报: 6/23→6/22, 更新描述")
    
    # ========== 4. 深度调研统计 ==========
    # "28篇报告" 和 "跨2个月" 需更新（实际跨3+月了: 3,4,5,6月）
    old_research_stats = '''<span class="research-stat-badge">📊 28篇报告</span>
                        <span class="research-stat-badge">🗓️ 跨2个月</span>'''
    new_research_stats = '''<span class="research-stat-badge">📊 28篇报告</span>
                        <span class="research-stat-badge">🗓️ 跨4个月</span>'''
    if old_research_stats in html:
        html = html.replace(old_research_stats, new_research_stats)
        changes.append("深度调研: 跨2个月→跨4个月")
    
    # ========== 5. 追踪体系计数更新 ==========
    # "100+" count for 人物
    old_tracking_count = '''<span class="collapsible-count">100+</span>'''
    # This may vary - check if still needed
    
    # ========== 6. Header title (仅内部版) ==========
    if is_internal:
        old_title = '<h1 class="header-title">我是林克，这是沈浪让我负责的AI洞察项目</h1>'
        new_title = '<h1 class="header-title">AI洞察 · 持续追踪AI行业动态</h1>'
        if old_title in html:
            html = html.replace(old_title, new_title)
            changes.append("Header title: 去掉第一人称→产品名")
    
    # ========== 7. 订阅按钮 (仅内部版) ==========
    if is_internal:
        # 订阅AI日报按钮目前指向frontend-cloud域名，内部版应保留
        # 外部版入口按钮在内部版有意义，外部版则不需要"外部版入口"
        pass
    
    # ========== 8. 日历初始月份修正 ==========
    # calendarMonth默认显示"📅 2026年3月" → 应该是当前月份6月
    old_cal_month = '📅 2026年3月'
    new_cal_month = '📅 2026年6月'
    if old_cal_month in html:
        html = html.replace(old_cal_month, new_cal_month)
        changes.append("日历初始月份: 3月→6月")
    
    # ========== 9. 知识库统计更新 ==========
    # "41篇 · 7人 · 4企业" → 更新
    old_kb_stats = '41篇 · 7人 · 4企业'
    new_kb_stats = '41篇 · 10+人 · 4+企业'
    if old_kb_stats in html:
        html = html.replace(old_kb_stats, new_kb_stats)
        changes.append("知识库统计: 7人→10+人, 4企业→4+企业")
    
    # ========== 10. Footer 优化 ==========
    # 内部版footer有"林克"自述，外部版已经是品牌化
    if is_internal:
        old_footer = '''<div class="footer-brand">
                <span>❤️🔥</span>
                <span>林克 · 你负责往前走，记忆这种事我来</span>
            </div>'''
        new_footer = '''<div class="footer-brand">
                <span>❤️🔥</span>
                <span>AI洞察 · MyFlicker 驱动</span>
            </div>'''
        if old_footer in html:
            html = html.replace(old_footer, new_footer)
            changes.append("Footer: 林克签名→MyFlicker驱动")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return changes

# === 执行修复 ===
for filepath, is_internal in [(INTERNAL, True), (EXTERNAL, False)]:
    print(f"\n{'='*50}")
    print(f"Fixing: {os.path.basename(os.path.dirname(filepath))}/public/index.html ({'internal' if is_internal else 'external'})")
    print(f"{'='*50}")
    changes = fix_file(filepath, is_internal)
    for c in changes:
        print(f"  ✅ {c}")
    if not changes:
        print("  (no changes needed)")

# Also fix the source index.html
SOURCE = "/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/index.html"
print(f"\n{'='*50}")
print(f"Fixing: sl-ai-insight/index.html (source)")
print(f"{'='*50}")
changes = fix_file(SOURCE, True)
for c in changes:
    print(f"  ✅ {c}")

print("\n✅ All files fixed.")
