#!/usr/bin/env python3
import re, shutil

HTML_PATH = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/01-daily-reports/2026-06/weekly-2026-W24.html'
PUBLIC_PATH = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/public/01-daily-reports/2026-06/weekly-2026-W24.html'

with open(HTML_PATH, encoding='utf-8') as f:
    html = f.read()

NEW_LINKINSIGHT = '''<section id="linkinsight">
<div class="doc-chapter-label animate-on-scroll">林克的洞察</div>
<h2 class="animate-on-scroll" style="font-size:var(--heading-2);font-weight:700;color:var(--color-text-primary);margin-bottom:20px;display:flex;align-items:center;gap:8px;">
  <svg class="meta-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8c0 3.4 2.1 6.3 5 7.5V22h6v-4.5c2.9-1.2 5-4.1 5-7.5a8 8 0 0 0-8-8z"/><line x1="12" y1="12" x2="12" y2="18"/></svg>
  林克的洞察
</h2>

<div class="pi-card animate-on-scroll">
  <div class="pi-header">
    <span class="pi-badge">本周主线</span>
    <span class="pi-title">从技术竞赛到系统竞争——三条线索汇成同一拐点</span>
  </div>
  <div class="pi-row highlight">
    <div class="pi-row-label">信号</div>
    <div class="pi-row-content">本周三条线索交汇：谷歌800亿+DeepSeek 500亿→算力基建；Fable/Mythos双轨→安全分层商业模式；豆包付费→AI应用商业化拐点。三者不是独立事件，而是同一底层逻辑的不同表现。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label">本质</div>
    <div class="pi-row-content">AI行业正在从"技术竞赛"转向"系统竞争"。技术竞赛比谁的模型更强，系统竞争比谁的基础设施更厚、商业模式更可持续、安全合规更完善。模型价格战97.5%是催化剂——近乎免费的模型让围绕模型的生态才真正开始值钱。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label l2">判断</div>
    <div class="pi-row-content"><strong>当模型价格跌幅97.5%，模型本身不再是商品——算力基础设施、Agent调用和垂直场景才是新的价值锚点。</strong>DeepSeek用500亿押注算力基建而非研发下一个模型版本，本质是在赌"拥有算力的人定义AI定价权"。</div>
  </div>
</div>

<div class="pi-card animate-on-scroll">
  <div class="pi-header">
    <span class="pi-badge">监管悖论</span>
    <span class="pi-title">刹车油门同踩——AI监管与商业化的策略博弈</span>
  </div>
  <div class="pi-row highlight">
    <div class="pi-row-label">现象</div>
    <div class="pi-row-content">Anthropic和OpenAI在冲刺IPO（AI行业IPO管线总规模3.6万亿美元）的同时，同步呼吁前沿AI硬监管。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label">解读</div>
    <div class="pi-row-content">这不是矛盾——率先呼吁监管的玩家，通常是最有能力满足监管要求的玩家。更高的准入门槛=更厚的护城河。这是AI版本的监管套利。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label l2">风险</div>
    <div class="pi-row-content">RSI（递归自我改进）值得严肃对待。80%+代码由AI自写、8倍效率提升——如果属实，AI自迭代速度已超传统监管框架响应周期。当前"刹车"是策略性减速，<strong>2027年前后可能不得不变成实质性的</strong>。</div>
  </div>
</div>

<div class="pi-card animate-on-scroll">
  <div class="pi-header">
    <span class="pi-badge">行动建议</span>
    <span class="pi-title">对AI从业者的三条启示</span>
  </div>
  <div class="pi-row highlight">
    <div class="pi-row-label">启示①</div>
    <div class="pi-row-content"><strong>不要做中间层。</strong>AI行业正在杠铃化：要么向上走（算力基建/Agent框架/安全审查），要么向下走（极致垂直行业AI）。通用AI聊天产品的窗口正在关闭，97.5%价格战+免费化会把中间层挤压出清。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label">启示②</div>
    <div class="pi-row-content"><strong>安全分层是新护城河。</strong>"同一模型不同安全配置"的分层能力正在成为进入企业市场的关键门槛。国内模型厂商如果只追求参数规模而不建立安全分层体系，将很难突破企业市场。</div>
  </div>
  <div class="pi-row">
    <div class="pi-row-label l2">启示③</div>
    <div class="pi-row-content"><strong>信任是下一个瓶颈。</strong>85%开发者用AI编程但仅3%高度信任，这个差距就是下一个增长空间。谁能把AI编码从黑箱变成可审计的工程流程，谁就赢得下一个10倍用户增长。</div>
  </div>
</div>

</section>'''

old_sec = re.search(r'<section id="linkinsight">.*?</section>', html, re.DOTALL)
if old_sec:
    html = html[:old_sec.start()] + NEW_LINKINSIGHT + html[old_sec.end():]
    print("linkinsight section 替换成功")
else:
    print("未找到linkinsight section")
    exit(1)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
shutil.copy(HTML_PATH, PUBLIC_PATH)

size = len(html.encode())
pi_card_count = html.count('class="pi-card animate-on-scroll"')
pi_header_count = html.count('class="pi-header"')
pi_row_count = html.count('class="pi-row')
print(f"文件大小: {size:,} bytes")
print(f"pi-card: {pi_card_count}, pi-header: {pi_header_count}, pi-row: {pi_row_count}")

# 合规检查
issues = []
if '{{' in html: issues.append("模板变量")
if 'href=""' in html: issues.append("空href")
if '我是' not in html or '林克' not in html: issues.append("了解更多缺失")
print("合规:" + ("✅" if not issues else "❌ " + str(issues)))
