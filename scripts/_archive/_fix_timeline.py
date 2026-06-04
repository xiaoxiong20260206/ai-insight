#!/usr/bin/env python3
"""
Fix timeline: split May reports out of April, add missing May reports.
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the timeline-container section
tc_start = content.find('<!-- 时间轴 -->')
tc_end_marker = '</div>\n                </div>'  # End of timeline-container + its parent

# Find the actual end - look for the closing tags after the "earlier" section
# The structure is: timeline-container > (timeline-month * 3) + closing divs
# We need to find where the container closes

# Strategy: replace the entire content between timeline-container opening and its close
# First, let's identify the exact sections

# April section start
april_start = content.find('data-month="2026-04"')
# March section start  
march_start = content.find('data-month="2026-03"')
# Earlier section start
earlier_start = content.find('data-month="earlier"')

# Find the end of the earlier section (closing divs)
# After earlier section cards, there are closing divs for: timeline-cards, timeline-month, timeline-container
temp = content[earlier_start:]
# Find the pattern: </div> (timeline-cards) \n </div> (timeline-month) \n more closings
earlier_cards_end = temp.find('</div>\n                    </div>')
if earlier_cards_end < 0:
    earlier_cards_end = temp.find('</div>\r\n                    </div>')

# The end of the entire timeline-container section
# We need to find the right closing. Let's count divs.
container_start_pos = content.find('<div class="timeline-container">')
depth = 0
container_end_pos = None
for i in range(container_start_pos, len(content)):
    if content[i:i+4] == '<div':
        depth += 1
    elif content[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            container_end_pos = i + 6
            break

# Extract the existing cards from April section
april_section = content[april_start:march_start]

# Find all cards in April
april_cards = re.findall(
    r'<a href="02-deep-research/[^"]*"[^>]*class="timeline-card[^"]*"[^>]*>.*?</a>',
    april_section,
    re.DOTALL
)

# Split into May and April cards
may_cards = []
actual_april_cards = []

for card in april_cards:
    # Check if the card's date is in May
    if '2026-05-' in card or '05-10' in card or '05-07' in card or '05-14' in card or '05-21' in card or '05-20' in card:
        may_cards.append(card)
    else:
        actual_april_cards.append(card)

# Also check March section for any May cards
march_section = content[march_start:earlier_start]
march_cards_in_march = re.findall(
    r'<a href="02-deep-research/[^"]*"[^>]*class="timeline-card[^"]*"[^>]*>.*?</a>',
    march_section,
    re.DOTALL
)

# Any May cards in March? (pine-ai-native-team was found there)
may_in_march = []
actual_march_cards = []
for card in march_cards_in_march:
    if '2026-05-' in card:
        may_in_march.append(card)
    else:
        actual_march_cards.append(card)

may_cards.extend(may_in_march)

# Add missing May reports
new_may_cards = [
    '''                            <a href="02-deep-research/topics/ai-org-moat-deep-research-2026.html" target="_blank" class="timeline-card cat-trend">
                                <div class="tc-header">
                                    <span class="tc-icon">🏢</span>
                                    <span class="tc-title">护城河不在代码里——组织形态才是AI时代真正抄不走的东西</span>
                                    <span class="tc-tag trend">趋势</span>
                                    <span class="tc-tag" style="background:#FEF2F2;color:#E11D48;">最新</span>
                                </div>
                                <div class="tc-desc">技术会趋同，产品会被抄，但组织抄不走——从 Anthropic/Stripe/字节/华为四案例拆解 AI 时代真正的护城河：组织形态而非技术本身</div>
                                <div class="tc-meta">📅 2026-05-14 · 组织AI · 护城河</div>
                            </a>''',
    '''                            <a href="02-deep-research/topics/ai-coding-to-ai-work.html" target="_blank" class="timeline-card cat-topic">
                                <div class="tc-header">
                                    <span class="tc-icon">⚔️</span>
                                    <span class="tc-title">从 AI Coding 到 AI Work</span>
                                    <span class="tc-tag topic">专题</span>
                                    <span class="tc-tag" style="background:#FEF2F2;color:#E11D48;">最新</span>
                                </div>
                                <div class="tc-desc">腾讯与阿里双案例深度分析，以及快手的定位——从 AI Coding 工具到 AI Work 平台的范式跃迁</div>
                                <div class="tc-meta">📅 2026-05-21 · AI Coding · 平台演进</div>
                            </a>''',
    '''                            <a href="02-deep-research/topics/yao-shunyu-su-yu-interview.html" target="_blank" class="timeline-card cat-trend">
                                <div class="tc-header">
                                    <span class="tc-icon">🎯</span>
                                    <span class="tc-title">英雄退场，浪潮上场</span>
                                    <span class="tc-tag trend">趋势</span>
                                    <span class="tc-tag" style="background:#FEF2F2;color:#E11D48;">最新</span>
                                </div>
                                <div class="tc-desc">姚顺宇×苏煜两篇访谈揭示的AI深层规律——英雄退场的背后是系统性浪潮的来临</div>
                                <div class="tc-meta">📅 2026-05-21 · 人物访谈 · 趋势研判</div>
                            </a>''',
]

may_cards.extend(new_may_cards)

# Remove "最新" tags from older May cards (keep only on the newest ones)
# Actually keep "最新" only on the 05-21 cards

# Build new timeline
# Count per section
april_count = len(actual_april_cards)
march_count = len(actual_march_cards) 
earlier_count = len(re.findall(
    r'<a href="02-deep-research/[^"]*"[^>]*class="timeline-card[^"]*"[^>]*>.*?</a>',
    content[earlier_start:container_end_pos],
    re.DOTALL
))

# Build May section
may_section = f'''                    <!-- 2026年5月 -->
                    <div class="timeline-month" data-month="2026-05">
                        <div class="timeline-month-header">
                            <div class="timeline-month-label">5月<br>2026</div>
                            <div class="timeline-month-dot">
                                <div class="timeline-dot-outer"><div class="timeline-dot-inner"></div></div>
                            </div>
                            <div class="timeline-month-info">
                                <span class="timeline-month-title">2026年5月</span>
                                <span class="timeline-month-count">{len(may_cards)}篇</span>
                            </div>
                        </div>
                        <div class="timeline-cards">
{chr(10).join(may_cards)}
                        </div>
                    </div>

'''

# Build April section (with corrected count)
april_section_new = f'''                    <!-- 2026年4月 -->
                    <div class="timeline-month" data-month="2026-04">
                        <div class="timeline-month-header">
                            <div class="timeline-month-label">4月<br>2026</div>
                            <div class="timeline-month-dot">
                                <div class="timeline-dot-outer"><div class="timeline-dot-inner"></div></div>
                            </div>
                            <div class="timeline-month-info">
                                <span class="timeline-month-title">2026年4月</span>
                                <span class="timeline-month-count">{april_count}篇</span>
                            </div>
                        </div>
                        <div class="timeline-cards">
{chr(10).join(actual_april_cards)}
                        </div>
                    </div>

'''

# Get March section - rebuild with just the March cards
march_section_new = f'''                    <!-- 2026年3月 -->
                    <div class="timeline-month" data-month="2026-03">
                        <div class="timeline-month-header">
                            <div class="timeline-month-label">3月<br>2026</div>
                            <div class="timeline-month-dot">
                                <div class="timeline-dot-outer"><div class="timeline-dot-inner"></div></div>
                            </div>
                            <div class="timeline-month-info">
                                <span class="timeline-month-title">2026年3月</span>
                                <span class="timeline-month-count">{march_count}篇</span>
                            </div>
                        </div>
                        <div class="timeline-cards">
{chr(10).join(actual_march_cards)}
                        </div>
                    </div>

'''

# Get the "earlier" section as-is
earlier_section = content[earlier_start:container_end_pos]
# Extract just the earlier month block
earlier_month_match = re.search(
    r'<div class="timeline-month" data-month="earlier">.*',
    earlier_section,
    re.DOTALL
)

# Reconstruct
new_timeline = f'''                <!-- 时间轴 -->
                <div class="timeline-container">
                    
{may_section}{april_section_new}{march_section_new}                </div>'''

# Replace in content
old_timeline = content[tc_start:container_end_pos]
new_content = content[:tc_start] + new_timeline + content[container_end_pos:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Timeline fixed!")
print(f"   May: {len(may_cards)} reports (3 moved + 3 new)")
print(f"   April: {april_count} reports")
print(f"   March: {march_count} reports")
