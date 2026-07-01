#!/usr/bin/env python3
"""优化AI洞察外部版首页 - 追踪体系+知识库Tab的6项改进"""
import re

HTML = '/data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/index.html'

with open(HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 优化1: 追踪体系 - 搜索/过滤框
# ============================================================
search_box = '''
                <!-- 搜索过滤 -->
                <div class="tracking-search" style="margin: var(--spacing-md) 0 var(--spacing-lg); position: relative;">
                    <input type="text" id="trackingSearch" placeholder="🔍 搜索人物、公司、关键词…" 
                        style="width: 100%; padding: 12px 16px 12px 44px; font-size: 15px; border: 2px solid var(--color-border); border-radius: var(--radius-lg); background: var(--color-bg); color: var(--color-text-primary); outline: none; transition: border-color 0.2s, box-shadow 0.2s;"
                        onfocus="this.style.borderColor='var(--color-success)'; this.style.boxShadow='0 0 0 3px rgba(5,150,105,0.1)'"
                        onblur="this.style.borderColor='var(--color-border)'; this.style.boxShadow='none'"
                        oninput="filterTracking(this.value)">
                    <svg style="position: absolute; left: 14px; top: 13px; width: 20px; height: 20px; color: var(--color-text-muted);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="5"/><path d="M21 21l-4.35-4.35"/></svg>
                    <div id="trackingSearchInfo" style="font-size: 12px; color: var(--color-text-muted); margin-top: 6px;"></div>
                </div>
'''

old_marker = '''                </div>
                
                <!-- 人物追踪 -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">👤</span>'''

new_marker = '''                </div>
''' + search_box + '''
                <!-- 人物追踪 -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">👤</span>'''

content = content.replace(old_marker, new_marker, 1)

# ============================================================
# 优化2: L1/L2/L3层级左边条颜色区分
# ============================================================
tracking_start = content.find('<article id="tracking"')
tracking_end = content.find('</article>', tracking_start) + len('</article>')
tracking_section = content[tracking_start:tracking_end]

h4_pattern = r'<h4 style="font-size: 14px; color: (var\(--color-text-secondary\)|#DC2626)(; font-weight: 700)?; margin: var\(--spacing-lg\) 0 var\(--spacing-md\);">(.*?)</h4>'

def replace_h4(match):
    color = match.group(1)
    bold = match.group(2) or ''
    text = match.group(3)
    if text.startswith('L1') or '\U0001f197' in text:
        tier_color = '#059669'
    elif text.startswith('L2'):
        tier_color = '#2563EB'
    elif text.startswith('L3'):
        tier_color = '#9CA3AF'
    else:
        tier_color = '#059669'
    return f'<h4 style="font-size: 14px; color: {color}{bold}; margin: var(--spacing-lg) 0 var(--spacing-md); border-left: 3px solid {tier_color}; padding-left: 10px;">{text}</h4>'

tracking_section = re.sub(h4_pattern, replace_h4, tracking_section)
content = content[:tracking_start] + tracking_section + content[tracking_end:]

# ============================================================
# 优化3: 知识库条目链接化
# ============================================================
kb_links = {
    'AI发展史与能力矩阵': '02-deep-research/topics/ai-history-capability-matrix/index.html',
    'AI下半场理论': '02-deep-research/topics/ai-second-half/index.html',
    '推理模型专题': '02-deep-research/topics/reasoning-models/index.html',
    'Gemini 3系列': '02-deep-research/topics/gemini-3/index.html',
    'GPT-5系列演进': '02-deep-research/topics/gpt-5/index.html',
    'MCP协议全解': '02-deep-research/topics/mcp-protocol/index.html',
    'AI Coding工具演进': '02-deep-research/topics/ai-coding-tools/index.html',
    'Agent架构': '02-deep-research/topics/agent-architecture/index.html',
    'Ambient Agents': '02-deep-research/topics/ambient-agents/index.html',
    'AI转型方法论': '02-deep-research/topics/ai-transformation-methodology/index.html',
    '软件工程3.0': '02-deep-research/topics/software-engineering-3/index.html',
    'AI Studio产品方案': '02-deep-research/topics/ai-studio/index.html',
}

for text, url in kb_links.items():
    old_item = f'<span class="item-text">{text}</span>'
    new_item = f'<a href="{url}" target="_blank" class="kb-item-link" style="color: inherit; text-decoration: none; display: inline;"><span class="item-text">{text}</span></a>'
    content = content.replace(old_item, new_item, 1)

# ============================================================
# 优化4: NEW标签自动化
# ============================================================
content = re.sub(
    r'<div\s+class="kb-item new">',
    '<div class="kb-item new" data-added="2026-06">',
    content
)
content = content.replace(
    '<span class="item-tag new">NEW</span>',
    '<span class="item-tag new" data-type="auto">NEW</span>'
)

# ============================================================
# 优化5: 知识库搜索框 + section-header
# ============================================================
kb_search = '''
                <!-- 知识搜索 -->
                <div class="kb-search" style="margin: var(--spacing-md) 0 var(--spacing-lg); position: relative;">
                    <input type="text" id="kbSearch" placeholder="🔍 搜索知识条目…" 
                        style="width: 100%; padding: 12px 16px 12px 44px; font-size: 15px; border: 2px solid var(--color-border); border-radius: var(--radius-lg); background: var(--color-bg); color: var(--color-text-primary); outline: none; transition: border-color 0.2s, box-shadow 0.2s;"
                        onfocus="this.style.borderColor='#7C3AED'; this.style.boxShadow='0 0 0 3px rgba(124,58,237,0.1)'"
                        onblur="this.style.borderColor='var(--color-border)'; this.style.boxShadow='none'"
                        oninput="filterKnowledge(this.value)">
                    <svg style="position: absolute; left: 14px; top: 13px; width: 20px; height: 20px; color: var(--color-text-muted);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="5"/><path d="M21 21l-4.35-4.35"/></svg>
                    <div id="kbSearchInfo" style="font-size: 12px; color: var(--color-text-muted); margin-top: 6px;"></div>
                </div>
'''

old_kb = '''            <section class="section">
                <!-- 知识库架构可视化 - 精简版 -->
                <div class="kb-architecture">'''

new_kb = '''            <section class="section">
                <div class="section-header">
                    <div class="section-icon">📚</div>
                    <div>
                        <h2 class="section-title">知识库</h2>
                        <p class="section-desc">按维度体系化沉淀的AI行业知识（点击条目查看深度调研）</p>
                    </div>
                </div>
''' + kb_search + '''
                <!-- 知识库架构可视化 - 精简版 -->
                <div class="kb-architecture">'''

content = content.replace(old_kb, new_kb, 1)

# ============================================================
# 优化6: CSS + JS
# ============================================================
kb_css = '''
        /* 知识库条目链接化hover */
        .kb-item-link:hover .item-text {
            color: var(--color-success);
            text-decoration: underline;
            text-underline-offset: 3px;
        }
'''

content = content.replace('</style>', kb_css + '    </style>')

js_code = """
        
        // ============ 追踪体系搜索过滤 ============
        function filterTracking(query) {
            const q = query.toLowerCase().trim();
            const ta = document.getElementById('tracking');
            if (!ta) return;
            const rows = ta.querySelectorAll('.tracking-table tbody tr');
            let vis = 0;
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (!q || text.includes(q)) { row.style.display = ''; vis++; }
                else { row.style.display = 'none'; }
            });
            ta.querySelectorAll('.tracking-table').forEach(table => {
                const tbody = table.querySelectorAll('tbody tr');
                const visRows = Array.from(tbody).filter(r => r.style.display !== 'none');
                const wrap = table.closest('.table-wrap');
                const h4 = wrap ? wrap.previousElementSibling : null;
                if (visRows.length === 0) { if(h4) h4.style.display='none'; if(wrap) wrap.style.display='none'; }
                else { if(h4) h4.style.display=''; if(wrap) wrap.style.display=''; }
            });
            const info = document.getElementById('trackingSearchInfo');
            if (q) info.textContent = '找到 ' + vis + '/' + rows.length + ' 条匹配';
            else info.textContent = '';
        }
        
        // ============ 知识库搜索过滤 ============
        function filterKnowledge(query) {
            const q = query.toLowerCase().trim();
            const ka = document.getElementById('knowledge');
            if (!ka) return;
            const items = ka.querySelectorAll('.kb-item');
            let vis = 0;
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (!q || text.includes(q)) { item.style.display = ''; vis++; }
                else { item.style.display = 'none'; }
            });
            if (q) ka.querySelectorAll('.kb-dimension').forEach(d => d.setAttribute('data-expanded','true'));
            ka.querySelectorAll('.kb-foundation').forEach(f => {
                const tags = f.querySelectorAll('.foundation-tags span, .foundation-items span');
                let has = false;
                tags.forEach(t => { if(!q||t.textContent.toLowerCase().includes(q)){t.style.display='';has=true;}else{t.style.display='none';} });
                f.style.display = has || !q ? '' : 'none';
            });
            const info = document.getElementById('kbSearchInfo');
            if (q) info.textContent = '找到 ' + vis + '/' + items.length + ' 条匹配';
            else { info.textContent = ''; ka.querySelectorAll('.kb-dimension').forEach(d => d.setAttribute('data-expanded','false')); }
        }
        
        // ============ NEW标签自动化(30天过期) ============
        (function autoExpireNEW() {
            const now = new Date();
            const thirtyDays = 30*24*60*60*1000;
            document.querySelectorAll('.item-tag.new[data-type="auto"]').forEach(tag => {
                const item = tag.closest('.kb-item');
                if(!item) return;
                const added = item.getAttribute('data-added');
                if(!added) return;
                const d = new Date(added + '-15');
                if(now - d > thirtyDays) { tag.style.display='none'; item.classList.remove('new'); }
            });
        })();
"""

content = content.replace('</script>', js_code + '\n    </script>')

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 全部6项优化已写入")
