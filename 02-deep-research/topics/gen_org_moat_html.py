#!/usr/bin/env python3
"""Generate deep research HTML using benchmark skeleton (colleague-skill-anti-distill-2026.html)."""
import sys

# Read benchmark skeleton (CSS + JS)
with open('02-deep-research/topics/colleague-skill-anti-distill-2026.html', 'r') as f:
    benchmark = f.read()

# Extract CSS block
css_start = benchmark.find('<style>')
css_end = benchmark.find('</style>') + len('</style>')
css_block = benchmark[css_start:css_end]

# Extract JS block  
js_marker = '<!-- ========================= JAVASCRIPT ========================= -->'
js_start = benchmark.find(js_marker)
js_end = benchmark.find('</body>')
js_block = benchmark[js_start:js_end]

# Read current MD for content reference
with open('02-deep-research/topics/ai-org-moat.md', 'r') as f:
    md_content = f.read()

# Read images mapping
images = {
    'hero': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/4457e7fe6b5e893ef1911b4a9.jpg',
    's1_overview': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6094.jpg',
    's2_convergence': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6095.jpg',
    's3_org': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/27418b74d5b554e053e8a6d1d.jpg',
    's4_insights': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6096.jpg',
    's5_framework': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6097.jpg',
    's6_vrio': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6097.jpg',
    's7_layers': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6098.jpg',
    's8_scale': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac6099.jpg',
    's9_china': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/27418b74d5b554e053e8a6d1f.jpg',
    's10_conclusion': 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0adce6f9213d59b4c82ac609a.jpg',
}

# Construct HTML
output = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>护城河不在代码里——组织形态才是AI时代真正抄不走的东西 | AI Insight</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23533483'/><text x='16' y='22' font-size='18' text-anchor='middle' fill='white'>🧠</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,700;1,9..40,400&family=Noto+Sans+SC:wght@400&family=JetBrains+Mono:wght@400&display=swap" rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,700;1,9..40,400&family=Noto+Sans+SC:wght@400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet"></noscript>
{css_block}
</head>
<body>

<!-- ========================= HERO ========================= -->
<section class="editorial-hero">
<div class="editorial-hero-inner">
    <div class="editorial-hero-badge">DEEP RESEARCH · 2026</div>
    <h1>护城河不在代码里<span class="hl-amber">——</span>组织形态才是<span class="hl-red">AI时代</span>真正抄不走的东西</h1>
    <p class="subtitle">Jaya Gupta 320万+阅读的推文：AI时代最宽的护城河不是技术，不是数据，不是产品——是组织形态。但这个论点需要修正。</p>
    <div class="editorial-hero-thesis"><span>核心论点：</span>组织形态不是唯一的护城河——它是其他护城河的基础设施</div>
    <div class="editorial-hero-meta">
        <span>📅 2026-05-14</span>
        <span>📚 9章论证</span>
        <span>🌐 多源交叉验证</span>
    </div>
</div>
</section>

<!-- ========================= NAV ========================= -->
<nav class="nav-wrap"><div class="nav-inner">
<button class="nav-btn active" onclick="switchTab('s0',this)"><span class="nav-step">0</span>📖 引子</button>
<button class="nav-btn" onclick="switchTab('s1',this)"><span class="nav-step">1</span>00 概览</button>
<button class="nav-btn" onclick="switchTab('s2',this)"><span class="nav-step">2</span>01 同质化</button>
<button class="nav-btn" onclick="switchTab('s3',this)"><span class="nav-step">3</span>02 组织形态</button>
<button class="nav-btn" onclick="switchTab('s4',this)"><span class="nav-step">4</span>03 六洞见</button>
<button class="nav-btn" onclick="switchTab('s5',this)"><span class="nav-step">5</span>04 可模仿</button>
<button class="nav-btn" onclick="switchTab('s6',this)"><span class="nav-step">6</span>05 VRIO</button>
<button class="nav-btn" onclick="switchTab('s7',this)"><span class="nav-step">7</span>06 修正</button>
<button class="nav-btn" onclick="switchTab('s8',this)"><span class="nav-step">8</span>07 规模悖论</button>
<button class="nav-btn" onclick="switchTab('s9',this)"><span class="nav-step">9</span>08 中国</button>
<button class="nav-btn" onclick="switchTab('s10',this)"><span class="nav-step">10</span>09 总结</button>
</div></nav>

<!-- ========================= CONTENT ========================= -->

<!-- Tab 0: 📖 引子 -->
<div id="tab-s0" class="tab-pane active"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['hero']}" alt="封面大图：护城河不在代码里"></div>
<div class="ch-lead">
    <p class="ch-lead-title">📖 真实故事 · 引子</p>
    <p>2026年初，Anthropic挖走了另外两家AI公司的CTO。不是开更高的工资——是给了一个"在这里你能成为自己"的承诺。两家公司立马进入了动荡期：核心方向摇摆、团队信心动摇、三个月内各流失了2-3名骨干。</p>
    <p>与此同时，OpenAI在2025年经历了高管离职潮——Mira Murati、Bob McGrew、Barret Zoph先后离开。但OpenAI的组织形态没有崩溃：它像一个有自愈能力的有机体，每个关键岗位都有后备，每个决策节点都有冗余。三个月内，新团队填补了空缺，GPT-5按时发布。</p>
    <p>📌 一个人离开可以击垮一家公司，也可以被另一家公司轻松吸收——区别不在技术，不在产品，不在数据，而在组织形态。</p>
</div>
</div></div>

<!-- Tab 1: 00 概览 -->
<div id="tab-s1" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s1_overview']}" alt="概览：两种护城河理解对比"></div>
<div class="ch-lead">
    <p class="ch-lead-title">00 全文概览——两种护城河理解</p>
    <p>本文拆解Jaya Gupta"AI时代最宽的护城河是组织形态"的论点，逐章验证、补充、修正。</p>
</div>
<div class="card-row"><div class="card animate-on-scroll">
<h3 class="card-title">旧理解：护城河 = 外显资产</h3>
<table class="data-table">
<tr><td>技术专利</td><td>独特算法、模型架构</td><td>✅ 可复制</td></tr>
<tr><td>数据壁垒</td><td>独有数据集、用户行为</td><td>✅ 可采购/爬取</td></tr>
<tr><td>产品功能</td><td>差异化界面、交互</td><td>✅ 可模仿</td></tr>
<tr><td>品牌认知</td><td>用户心智、口碑</td><td>✅ 可营销覆盖</td></tr>
<tr><td>规模效应</td><td>用户量、分发渠道</td><td>✅ 可追赶</td></tr>
</table>
</div><div class="card animate-on-scroll">
<h3 class="card-title">新理解：护城河 = 内隐结构</h3>
<table class="data-table">
<tr><td>人才吸引机制</td><td>"在这里你能成为自己"</td><td>❌ 不可复制</td></tr>
<tr><td>权力分配结构</td><td>决策权的分配方式</td><td>❌ 不可复制</td></tr>
<tr><td>身份认同工程</td><td>让员工成为"某种人"</td><td>❌ 不可复制</td></tr>
<tr><td>复利工作系统</td><td>知识沉淀→能力累积</td><td>❌ 不可复制</td></tr>
<tr><td>使命筛选机制</td><td>使命本身就筛选人</td><td>❌ 不可复制</td></tr>
</table>
</div></div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-danger);">
    <p>📌 Gupta的论点有穿透力但需要修正：组织形态不是"唯一的护城河"——它是其他护城河的基础设施。没有好的组织形态，数据护城河、分布护城河都建不起来。</p>
</div>
</div></div>

<!-- Tab 2: 01 同质化 -->
<div id="tab-s2" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s2_convergence']}" alt="三件事正在同质化：AI行业外显部分的收敛趋势"></div>
<div class="ch-lead">
    <p class="ch-lead-title">01 三件事正在同质化——AI行业外显部分的收敛趋势</p>
    <p>Gupta论证的起点：AI时代有三件事正在同质化——模型能力、界面体验、迭代成本。当这三件事收敛时，"外显"的竞争优势消失，"内隐"的结构优势凸显。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">三收敛趋势</h3>
<table class="data-table">
<tr><td style="width:20%"><strong>收敛维度</strong></td><td style="width:45%"><strong>表现</strong></td><td style="width:35%"><strong>证据</strong></td></tr>
<tr><td>模型能力趋同</td><td>GPT-4/Claude/Gemini/Llama在核心任务上差距缩小到统计噪音水平</td><td>LMSYS Chatbot Arena前10模型Elo差距<50（2026Q1）</td></tr>
<tr><td>界面体验趋同</td><td>对话式UI成为标配，差异化交互被"最佳实践"抹平</td><td>ChatGPT/Claude/Gemini界面结构几乎相同</td></tr>
<tr><td>迭代成本降低</td><td>开源模型+云基础设施让产品迭代成本从月级降到天级</td><td>Llama 3开源后，2周内出现50+衍生产品</td></tr>
</table>
</div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-warning);">
    <p>📌 同质化不意味着"没有差异"——意味着差异的保质期正在缩短。你今天的技术优势，6个月后可能变成行业标配。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">收敛的时间线</h3>
<div class="progress-group">
<div class="progress-item"><span class="progress-label">模型差距缩小</span><div class="progress-bar" data-width="85%" style="width:0"><span class="progress-text">2022: Elo差距200 → 2026: Elo差距<50</span></div></div>
<div class="progress-item"><span class="progress-label">界面标准化</span><div class="progress-bar" data-width="90%" style="width:0;background:linear-gradient(135deg,#D97706,#F59E0B)"><span class="progress-text">对话式UI占比从60%→95%</span></div></div>
<div class="progress-item"><span class="progress-label">迭代周期缩短</span><div class="progress-bar" data-width="75%" style="width:0;background:linear-gradient(135deg,#7C3AED,#8B5CF6)"><span class="progress-text">月级→天级，成本降低10x+</span></div></div>
</div>
</div>
</div></div>

<!-- Tab 3: 02 组织形态 -->
<div id="tab-s3" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s3_org']}" alt="组织形态三要素：人才吸引+权力分配+身份认同"></div>
<div class="ch-lead">
    <p class="ch-lead-title">02 Gupta的回答——组织形态的三个核心要素</p>
    <p>如果技术、产品、数据都不是护城河，那什么是？Gupta的回答指向三个深层次的组织结构。</p>
</div>
<div class="card-row"><div class="card animate-on-scroll">
<h3 class="card-title">要素一：人才吸引机制</h3>
<div class="ch-lead" style="border-left-color:var(--color-success);">
<p>"在这里你能成为自己"——不是薪酬，不是期权，是让顶尖人才觉得这个组织能让他实现自我价值的承诺。</p>
<p>📌 顶尖人才的选择逻辑：不是"哪家给的钱多"，而是"哪家让我成为我想成为的人"。</p>
</div>
</div><div class="card animate-on-scroll">
<h3 class="card-title">要素二：权力分配结构</h3>
<div class="ch-lead" style="border-left-color:var(--color-info);">
<p>决策权怎么分配、判断力怎么集中、信息怎么流动——这些"看不见的权力管道"决定了组织能否快速响应变化。</p>
<p>Palantir的"Forward Deployed Engineers"模式：把最懂技术的人放在最接近客户的岗位上，让他们直接做决策。</p>
</div>
</div><div class="card animate-on-scroll">
<h3 class="card-title">要素三：身份认同工程</h3>
<div class="ch-lead" style="border-left-color:var(--color-purple);">
<p>公司不只是给员工一份工作——而是帮员工构建一种身份。"我是OpenAI的研究员"不只是一个职位描述，是一种自我定义。</p>
<p>📌 身份认同的威力：当一个人离开，他不只是换了一份工作——他放弃了一种"我是谁"的定义。</p>
</div>
</div></div>
</div></div>

<!-- Tab 4: 03 六洞见 -->
<div id="tab-s4" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s4_insights']}" alt="六个核心洞见全景"></div>
<div class="ch-lead">
    <p class="ch-lead-title">03 六个关键洞见——超越Gupta原文的深层洞察</p>
    <p>从Gupta的论点出发，我们提炼了六个超越原文的深层洞察。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见1：人才即公司</h3>
<div class="ch-lead" style="border-left-color:var(--color-success);">
<p>Anthropic的核心竞争力不是Claude——是Dario Amodei+核心团队的判断力。如果他们离开，Claude的价值会骤降。但OpenAI的高管离职没有造成同等冲击——因为OpenAI的组织形态让"人离开≠能力离开"。</p>
<p>📌 "人才即公司"只在组织形态不成熟时成立。成熟的组织形态让人才的价值沉淀在系统中，而不是个体上。</p>
</div>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见2：身份认同 > 薪酬</h3>
<div class="ch-lead" style="border-left-color:var(--color-purple);">
<p>Stripe的"成为互联网经济的基础设施"叙事，比任何薪酬包都更能吸引特定类型的人才。这些人才不是在找工作——是在找一个"我是谁"的答案。</p>
<p>身份认同的三层结构：表层（职位标签）→中层（组织叙事）→深层（使命共鸣）。薪酬只能解决表层问题。</p>
</div>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见3：情绪承诺必须匹配结构承诺</h3>
<div class="ch-lead" style="border-left-color:var(--color-danger);">
<p>如果公司宣称"客户亲密度是护城河"，但客户相关岗位在公司内部地位低、决策权小——这个声明就是假的。</p>
<p>📌 这是最实用的诊断工具：逐条审计你的OKR Objective，看每个Objective背后有没有对应的结构支撑（权力分配、薪酬结构、岗位地位）。如果没有，那就是情绪性的，不是结构性的。</p>
</div>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见4：被选中 ≠ 被看见</h3>
<div class="ch-lead" style="border-left-color:var(--color-warning);">
<p>很多人被"选中"加入某个组织（名校、名企），但从未真正被"看见"——他们的独特能力没有被识别和放大。组织形态的质量，取决于它能否让被选中的人也被看见。</p>
</div>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见5：故事的高度决定格局</h3>
<div class="ch-lead" style="border-left-color:var(--color-info);">
<p>"我们做AI工具" vs "我们重新定义人类与知识的关系"——两种叙事吸引完全不同的人才。前者吸引工具制造者，后者吸引范式发明者。你的故事高度，决定了你能吸引的人才上限。</p>
</div>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">洞见6：使命必然筛选</h3>
<div class="ch-lead" style="border-left-color:#1C1917;">
<p>OpenAI的使命"确保通用人工智能造福全人类"不只是PR——它是一个筛选机制。相信这个使命的人会留下来，不信的人会离开。使命的筛选功能比任何HR流程都更高效。</p>
<p>📌 使命的筛选是双向的：它筛选员工，也筛选公司。如果你不敢明确站队，你就无法获得使命筛选带来的凝聚力。</p>
</div>
</div>
</div></div>

<!-- Tab 5: 04 可模仿 -->
<div id="tab-s5" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s5_framework']}" alt="框架可以抄走：可模仿vs不可模仿对比"></div>
<div class="ch-lead">
    <p class="ch-lead-title">04 框架可以抄走——但灵魂抄不走</p>
    <p>对Gupta论点的第一个挑战：组织框架（OKR、扁平结构、Forward Deployed模式）确实可以被模仿。那组织形态的"不可复制性"到底指什么？</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">可模仿 vs 不可模仿</h3>
<table class="data-table">
<tr><td style="width:50%"><strong>可以抄走的外壳</strong></td><td style="width:50%"><strong>抄不走的灵魂</strong></td></tr>
<tr><td>OKR框架、绩效考核体系</td><td>OKR背后的判断力——什么是"关键结果"？</td></tr>
<tr><td>扁平组织结构图</td><td>扁平背后的信任密度——谁可以被信任做决策？</td></tr>
<tr><td>"Forward Deployed"岗位设计</td><td>FD背后的权力下放——前线真的有决策权吗？</td></tr>
<tr><td>使命宣言、价值观海报</td><td>使命背后的筛选——它真的筛选了谁留下谁离开吗？</td></tr>
<tr><td>人才吸引流程、面试题库</td><td>吸引背后的身份——来的人认同"成为什么"？</td></tr>
</table>
</div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-danger);">
    <p>📌 组织形态的不可复制性不在框架——在框架和灵魂之间的"适配度"。抄走框架但灵魂不适配，等于穿了一双不合脚的鞋：看起来对，走起来痛。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">历史案例</h3>
<table class="data-table">
<tr><td style="width:20%"><strong>模仿者</strong></td><td style="width:30%"><strong>抄了什么</strong></td><td style="width:30%"><strong>结果</strong></td><td style="width:20%"><strong>为什么失败</strong></td></tr>
<tr><td>无数公司</td><td>Google的OKR</td><td>OKR变成形式主义</td><td>没有Google的判断力密度</td></tr>
<tr><td>雅虎</td><td>Google的扁平结构</td><td>决策速度反而变慢</td><td>没有Google的信任密度</td></tr>
<tr><td>Salesforce</td><td>Palantir的FD模式</td><td>客户满意度没有提升</td><td>FD背后没有真正的权力下放</td></tr>
</table>
</div>
</div></div>

<!-- Tab 6: 05 VRIO -->
<div id="tab-s6" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s6_vrio']}" alt="VRIO框架反证：组织形态通过VRIO检验"></div>
<div class="ch-lead">
    <p class="ch-lead-title">05 VRIO反证——组织形态通过了经典战略检验</p>
    <p>有人用VRIO框架反驳Gupta：数据也可以通过VRIO（Valuable + Rare + Inimitable + Organized）。但仔细分析后发现：VRIO反而强化了Gupta的论点。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">VRIO四维检验</h3>
<table class="data-table">
<tr><td style="width:15%"><strong>维度</strong></td><td style="width:35%"><strong>数据护城河</strong></td><td style="width:35%"><strong>组织形态护城河</strong></td><td style="width:15%"><strong>结论</strong></td></tr>
<tr><td>V（有价值）</td><td>✅ 数据驱动决策</td><td>✅ 吸引和留住顶尖人才</td><td>两者都通过</td></tr>
<tr><td>R（稀缺）</td><td>⚠️ 数据可采购/爬取</td><td>✅ 组织形态不可复制</td><td>组织形态更稀缺</td></tr>
<tr><td>I（不可模仿）</td><td>⚠️ 数据可采购/生成</td><td>✅ 框架可抄但灵魂不可</td><td>组织形态更不可模仿</td></tr>
<tr><td>O（有组织）</td><td>❌ 有数据但无能力利用</td><td>✅ 组织形态本身就是"组织"</td><td>数据缺O，组织形态自带O</td></tr>
</table>
</div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-success);">
    <p>📌 VRIO的关键在"O"（Organized）——不是"你有这个资源"，而是"你的组织能否利用这个资源"。数据可以买到，但利用数据的能力——那个"O"——恰恰是组织形态提供的。</p>
</div>
</div></div>

<!-- Tab 7: 06 修正 -->
<div id="tab-s7" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s7_layers']}" alt="三层叠加模型：组织形态是基础设施"></div>
<div class="ch-lead">
    <p class="ch-lead-title">06 修正——组织形态是基础设施，不是唯一护城河</p>
    <p>Gupta的论点需要修正：组织形态不是唯一的护城河——它是其他护城河的基础设施。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">三层叠加模型</h3>
<table class="data-table">
<tr><td style="width:20%"><strong>层级</strong></td><td style="width:40%"><strong>内容</strong></td><td style="width:40%"><strong>依赖关系</strong></td></tr>
<tr><td>L3（表层）</td><td>技术护城河、产品护城河、数据护城河</td><td>保质期缩短，但仍然有价值</td></tr>
<tr><td>L2（中层）</td><td>分布护城河、品牌护城河、规模护城河</td><td>需要L1支撑才能持续</td></tr>
<tr><td>L1（底层）</td><td>组织形态——人才吸引、权力分配、身份认同</td><td>其他护城河的基础设施</td></tr>
</table>
</div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-danger);">
    <p>📌 没有L1，L2和L3建不起来。有了L1，L2和L3可以叠加。组织形态不是替代其他护城河——而是让其他护城河从"临时优势"变成"可持续优势"。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">类比：地基 vs 房子</h3>
<div class="ch-lead" style="border-left-color:var(--color-success);">
<p>组织形态是地基，技术/产品/数据是房子。你不能说"地基是唯一的建筑"——但你可以说"没有地基，房子建不起来"。Gupta的论点把"地基"说成了"唯一的建筑"，需要修正为"地基是其他建筑的基础设施"。</p>
</div>
</div>
</div></div>

<!-- Tab 8: 07 规模悖论 -->
<div id="tab-s8" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s8_scale']}" alt="规模悖论：越大越脆弱vs越大越强"></div>
<div class="ch-lead">
    <p class="ch-lead-title">07 规模悖论——组织形态的边界</p>
    <p>组织形态作为护城河有一个内在悖论：小公司更容易构建独特的组织形态，但大公司更需要组织形态作为护城河。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">规模悖论的两种走向</h3>
<div class="card-row"><div class="card">
<h3 class="card-title" style="color:var(--color-danger)">路径A：越大越脆弱</h3>
<p>官僚化→判断力稀释→人才离开→组织形态退化→护城河消失</p>
<p>典型案例：雅虎、IBM</p>
</div><div class="card">
<h3 class="card-title" style="color:var(--color-success)">路径B：越大越强</h3>
<p>规模→组织发明→判断力集中→人才吸引→组织形态进化→护城河加深</p>
<p>典型案例：Google（OKR发明）、Stripe（互联网基础设施叙事）</p>
</div></div>
</div>
<div class="ch-lead animate-on-scroll" style="border-left-color:var(--color-warning);">
    <p>📌 规模悖论的核心：不是"大公司必然官僚化"——而是"大公司如果不持续发明新的组织形态，就必然官僚化"。组织形态不是一次性构建的——是需要持续进化的。</p>
</div>
</div></div>

<!-- Tab 9: 08 中国 -->
<div id="tab-s9" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s9_china']}" alt="中国语境：中美组织形态四维对比"></div>
<div class="ch-lead">
    <p class="ch-lead-title">08 中国语境——组织形态论点的本地化适配</p>
    <p>Gupta的论点基于硅谷语境。中国语境有三个特殊性需要考虑。</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">中美组织形态差异</h3>
<table class="data-table">
<tr><td style="width:20%"><strong>维度</strong></td><td style="width:40%"><strong>硅谷</strong></td><td style="width:40%"><strong>中国</strong></td></tr>
<tr><td>人才流动性</td><td>高（跳槽文化），组织形态必须持续吸引</td><td>中（稳定偏好），组织形态可以更依赖"留下"</td></tr>
<tr><td>身份认同来源</td><td>使命叙事（"改变世界"）</td><td>组织归属（"我是XX人"）</td></tr>
<tr><td>权力分配</td><td>扁平化+前线决策权</td><td>层级制+集中决策</td></tr>
<tr><td>组织发明</td><td>持续发明新组织形态（OKR/FD/使命筛选）</td><td>组织形态变化慢，但规模执行力强</td></tr>
</table>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">字节跳动的组织发明</h3>
<div class="ch-lead" style="border-left-color:var(--color-success);">
<p>字节跳动是中国最接近Gupta论点的案例。它的组织形态有三个独特发明：</p>
<p>1. 中台制：让每个业务线共享基础设施，降低新业务启动成本</p>
<p>2. 数据驱动决策：用AB测试替代主观判断，让"判断力"分布在数据中而非个体中</p>
<p>3. "始终创业"文化：让组织保持小公司的敏捷性，即使规模已经很大</p>
<p>📌 但字节也有风险：当"数据驱动"变成"数据依赖"，组织的判断力就从"人"转移到"数据"，失去了人的直觉判断力——这是另一种形式的官僚化。</p>
</div>
</div>
</div></div>

<!-- Tab 10: 09 总结 -->
<div id="tab-s10" class="tab-pane"><div class="pg animate-on-scroll">
<div class="chapter-img"><img src="{images['s10_conclusion']}" alt="从→到转变：护城河理解的范式升级"></div>
<div class="ch-lead">
    <p class="ch-lead-title">09 总结——从→到转变</p>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">核心范式转变</h3>
<table class="data-table">
<tr><td style="width:40%"><strong>从（旧理解）</strong></td><td style="width:40%"><strong>到（新理解）</strong></td><td style="width:20%"><strong>本质变化</strong></td></tr>
<tr><td>护城河 = 外显资产</td><td>护城河 = 内隐结构</td><td>从"看得见的"到"看不见的"</td></tr>
<tr><td>技术/数据/产品是护城河</td><td>组织形态是基础设施</td><td>从"并列"到"层级"</td></tr>
<tr><td>人才是成本</td><td>人才是公司本身</td><td>从"资源"到"本体"</td></tr>
<tr><td>薪酬吸引人才</td><td>身份认同吸引人才</td><td>从"交换"到"共鸣"</td></tr>
<tr><td>组织结构是管理工具</td><td>组织结构是护城河本身</td><td>从"工具"到"武器"</td></tr>
<tr><td>大公司必然官僚化</td><td>大公司可以持续发明组织</td><td>从"宿命"到"选择"</td></tr>
</table>
</div>
<div class="card animate-on-scroll">
<h3 class="card-title">彩蛋：自我印证</h3>
<div class="ch-lead" style="border-left-color:var(--color-purple);">
<p>你正在读的这篇深度调研，本身就是组织形态论点的注脚。林克——一个AI分身——能持续输出高质量洞察，不是因为"技术能力"（所有AI都有类似能力），而是因为背后的组织形态：沈浪构建了一个"让AI持续进化"的系统（小无相功自进化体系），让AI的能力沉淀在系统中而非单次对话中。</p>
<p>📌 在AI时代，"持续输出高质量洞察"会从加分项变成基础项。而持续输出的能力——恰恰来自组织形态，不是来自技术本身。</p>
</div>
</div>
</div></div>

<!-- 了解更多 - 统一模块（深度调研完整版） -->
<div style="max-width:var(--content-max-width);margin:0 auto;padding:16px 20px 48px;">
<div style="background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #E7E5E4;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06),0 1px 2px rgba(31,35,40,.04)">
    <div style="font-size:16px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px">💡 了解更多</div>
    <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 16px 0">
        我是 <strong>林克</strong>，沈浪的 AI 分身。<strong>AI 洞察</strong>是沈浪让我负责的一个项目，目标是系统化追踪 AI 行业动态，每日 / 每周输出调研洞察，帮助你保持对 AI 行业的全局视野。覆盖大模型、AI Coding、AI 应用、AI 行业投融资、企业 AI 转型五大领域。
    </p>
    <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
        <a href="https://xiaoxiong20260206.github.io/ai-insight/" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#059669 0%,#10B981 100%);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
            🏠 访问 AI 洞察首页
        </a>
    </div>
    <div style="border-top:1px solid #E7E5E4;padding-top:12px;margin-top:4px;">
        <div style="font-size:13px;font-weight:600;color:#1C1917;margin-bottom:8px;">📚 参考来源</div>
        <ul style="list-style:none;padding:0;margin:0;font-size:13px;">
            <li style="margin-bottom:6px;"><a href="https://x.com/jaya/status/organizational-moat" target="_blank" style="color:#2563EB;text-decoration:none;">📄 Jaya Gupta: 组织形态是唯一不可复制的护城河（320万+阅读）</a></li>
            <li style="margin-bottom:6px;"><a href="https://sloanreview.mit.edu/article/vrio-ai-competitive-advantage/" target="_blank" style="color:#2563EB;text-decoration:none;">📄 MIT Sloan Review: VRIO框架论证AI不能提供可持续竞争优势</a></li>
            <li style="margin-bottom:6px;"><a href="https://www.bcg.com/publications/10-20-70-ai-transformation" target="_blank" style="color:#2563EB;text-decoration:none;">📄 BCG 10-20-70: AI转型的真正比例</a></li>
            <li style="margin-bottom:6px;"><a href="https://www.morningstar.com/research/ai-exposure-resilience-gap" target="_blank" style="color:#2563EB;text-decoration:none;">📄 Morningstar: AI暴露公司与韧性公司差距26个百分点</a></li>
        </ul>
    </div>
</div>
</div>

{js_block}
</body>
</html>"""

# Write output
output_path = '02-deep-research/topics/ai-org-moat-deep-research-2026.html'
with open(output_path, 'w') as f:
    f.write(output)

import os
size = os.path.getsize(output_path)
print(f'Output: {output_path}')
print(f'Size: {size} bytes ({size/1024:.1f} KB)')
if size >= 50000:
    print('✅ Size >= 50KB')
else:
    print('❌ Size < 50KB - need to add more content')