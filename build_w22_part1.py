#!/usr/bin/env python3
"""Build W22 weekly HTML - Part 1: Write head + header + overview + top5 + insights"""
import os

W20_PATH = "01-daily-reports/2026-05/weekly-2026-W20.html"
W22_OUT = "01-daily-reports/2026-05/weekly-2026-W22.html"

w20 = open(W20_PATH).read()

# Get head section
head_start = w20.find('<!DOCTYPE')
head_end = w20.find('</head>') + len('</head>')
head = w20[head_start:head_end]

# Modify for W22
head = head.replace('AI 周报 2026-W20 (05.12-05.17)', 'AI 周报 2026-W22 (05.19-05.25)')
head = head.replace('2026年第20周AI行业动态精选：DeepSeek 500亿融资分水岭、Anthropic首超OpenAI、中国开源编码模型齐发、45%安全漏洞率、46%企业失败率', '2026年第22周AI行业动态精选：Google I/O Agent宣言、DeepSeek 700亿+永久降价75%、Anthropic估值9000亿反超OpenAI、AI编程三路线分化、四小龙估值破万亿+集体IPO')
head = head.replace('AI 周报 2026-W20 | AI洞察', 'AI 周报 2026-W22 | AI洞察')
head = head.replace("本周重大事件：DeepSeek 500亿分水岭、Anthropic首超OpenAI企业采用率、中国开源编码模型'落后叙事'失效、AI编程安全危机、企业AI46%失败率", '本周重大事件：Google I/O Agent宣言、DeepSeek 700亿+V4-Pro永久降价75%、Anthropic估值9000亿反超OpenAI、AI编程三路线分化、中国AI四小龙估值破万亿+集体IPO')

# Write file with head + first section of body
with open(W22_OUT, 'w') as f:
    f.write(head)
    f.write('\n<body>\n<a class="skip-to-content" href="#main-content">跳到主内容</a>\n\n<div class="layout-wrapper">\n')
    f.write('    <!-- SIDEBAR -->\n    <nav class="sidebar-nav" id="sidebar" aria-label="目录导航">\n        <div class="sidebar-doc-title">AI 周报 2026-W22</div>\n        <div class="toc-section">\n            <div class="toc-group-label">目录</div>\n            <a href="#overview"    class="toc-link">📋 本周概览</a>\n            <a href="#top5"        class="toc-link">🏆 Top 5 事件</a>\n            <a href="#insight"     class="toc-link">💡 周度洞察</a>\n            <a href="#linkinsight" class="toc-link">🧠 林克的洞察</a>\n            <a href="#llm"         class="toc-link">🧠 大模型</a>\n            <a href="#coding"      class="toc-link">⌨️ AI Coding</a>\n            <a href="#app"         class="toc-link">📱 AI 应用</a>\n            <a href="#industry"    class="toc-link">🏭 AI 行业</a>\n            <a href="#enterprise"  class="toc-link">🔄 企业AI转型</a>\n            <a href="#dailyindex"  class="toc-link">📅 日报索引</a>\n            <a href="#vocab"       class="toc-link">📖 技术词汇</a>\n            <a href="#narrative"   class="toc-link">🌊 宏观叙事</a>\n        </div>\n        <div class="reading-progress-wrap">\n            <div class="reading-progress-label">阅读进度</div>\n            <div class="reading-progress-track">\n                <div class="reading-progress-fill" id="readingProgress"></div>\n            </div>\n        </div>\n    </nav>\n    <button class="sidebar-collapse-btn" id="collapseBtn" title="折叠导航" aria-label="折叠导航">«</button>\n')

size = os.path.getsize(W22_OUT)
print(f"Part 1 written: {size} bytes")
