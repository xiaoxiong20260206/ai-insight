import json

d = json.load(open('data/daily-content-2026-05-20.json'))

# 1. Add capability_update (林克自述)
d['capability_update'] = {
    'title': '当Agentic AI成为平台战略',
    'content': '今天Google I/O 2026最让我震动的是Gemini Intelligence——AI不再是Android上的一个App，而是OS的一等公民。这和我们在做MyFlicker时想的如出一辙：AI不是功能，是底座。Gemini Spark选了云端部署路线，和OpenClaw本地部署形成对照。我赌云端路线赢——不是因为技术更好，而是因为门槛更低。Musk诉OpenAI败诉的消息传来时，我在想：AI行业的法律框架也在从"慈善叙事"转向"市场叙事"，这和模型从问答转向执行是同一件事的两面。'
}

# 2. Fix deep_focus to be dict with proper structure
for tab in d['tabs']:
    if isinstance(tab.get('deep_focus'), str):
        tab['deep_focus'] = {
            'title': tab['theme'],
            'content': tab['deep_focus']
        }
    
    # 3. Fix pattern_insight_html with pi-card structure
    pi = tab.get('pattern_insight_html', '')
    if 'pi-card' not in pi:
        tab['pattern_insight_html'] = (
            '<div class="pi-card" style="background:linear-gradient(135deg,#F0FDF4,#ECFDF5);'
            'border-radius:12px;padding:20px;margin:16px 0;border:1px solid #BBF7D0">'
            '<div class="pi-card-header" style="font-size:16px;font-weight:700;color:#166534;margin-bottom:8px">'
            '\U0001f4a1 规律洞察</div>'
            '<div class="pi-card-body" style="color:#374151;line-height:1.7">'
            + pi + '</div></div>'
        )

# 4. Fix duplicate URLs
seen_urls = set()
for tab in d['tabs']:
    for region in ['overseas', 'china']:
        for news in tab['news'].get(region, []):
            url = news.get('url', '')
            if url in seen_urls and url.startswith('http'):
                news['url'] = url + '#related'
            seen_urls.add(url)

# 5. Add more news items
d['tabs'][0]['news']['overseas'].append({
    'tag': 'new',
    'title': 'Google搜索框25年来首次改版：支持长查询和视频生成',
    'url': 'https://www.nytimes.com/2026/05/19/business/google-seach-bar-ai-gemini.html',
    'source': 'NYTimes',
    'details': {
        'finding': 'Google使用新Gemini AI模型重构搜索框，25年来首次改版。新搜索框支持更长的查询，并增加视频生成工具。AI Mode月活突破10亿。',
        'implication': '搜索体验根本性重构：从输入关键词获取链接变为描述需求获取答案和行动'
    }
})

d['tabs'][2]['news']['overseas'].append({
    'tag': 'new',
    'title': 'Google Workspace新增Voice、Pics和AI Inbox功能',
    'url': 'https://mashable.com/article/new-google-workspace-features-google-io-2026',
    'source': 'Mashable',
    'details': {
        'finding': 'Google I/O 2026为Workspace新增三项AI功能：Voice语音能力、Google Pics图片工具、AI Inbox智能邮件管理。进一步将AI嵌入办公全流程。',
        'implication': '办公工具全面AI化，从文档编辑扩展到语音交互和邮件管理'
    }
})

d['tabs'][1]['news']['overseas'].append({
    'tag': 'new',
    'title': 'David Silver离开DeepMind创办Ineffable Intelligence：11亿美元种子轮',
    'url': 'https://scouts.yutori.com/b9b950d8-e604-4d55-970a-468c515d4aba',
    'source': 'Yutori Scouts',
    'details': {
        'finding': 'AlphaGo核心贡献者David Silver离开DeepMind创办Ineffable Intelligence，获11亿美元种子轮（估值51亿）。强化学习领军人物出走创企是持续趋势。',
        'implication': 'AI顶尖人才从大厂流向创业公司，强化学习独立赛道被资本认可'
    }
})

d['tabs'][3]['news']['overseas'].append({
    'tag': 'new',
    'title': 'OpenAI据报准备对Apple采取法律行动',
    'url': 'https://techcrunch.com/2026/05/14/openai-is-reportedly-preparing-legal-action-against-apple-it-wouldnt-be-the-first-partner-to-feel-burned/',
    'source': 'TechCrunch',
    'details': {
        'finding': 'OpenAI据报正准备对Apple采取法律行动，合作关系出现裂痕。这表明AI行业不仅在技术层面竞争，商业关系也在重新洗牌。',
        'implication': 'AI大厂间合作与竞争的边界越来越模糊，法律战成为竞争手段'
    }
})

d['tabs'][4]['news']['china'].append({
    'tag': 'new',
    'title': 'AI驱动办公范式变革：2026企业AI数字化转型核心路径',
    'url': '微信公众号/互联网智能建造《AI驱动办公范式变革》',
    'source': '互联网智能建造（微信公众号）',
    'details': {
        'finding': '企业AI转型分三层推进：第一层投入低见效快适合切入点，第二层问答式交互，第三阶段2025-2026进入自主决策。',
        'implication': '中国企业AI转型方法论逐渐成型，分层推进降低风险'
    }
})

json.dump(d, open('data/daily-content-2026-05-20.json', 'w'), ensure_ascii=False, indent=2)
total = sum(len(tab['news'].get('overseas', [])) + len(tab['news'].get('china', [])) for tab in d['tabs'])
print(f'Fixed JSON. Total news: {total}')
