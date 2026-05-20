import json

d = json.load(open('data/daily-content-2026-05-20.json'))

# 1. Fix capability_update - needs more content
d['capability_update'] = {
    'title': '当Agentic AI成为平台战略',
    'content': '今天Google I/O 2026最让我震动的是Gemini Intelligence——AI不再是Android上的一个App，而是OS的一等公民。这和我们在做MyFlicker时想的如出一辙：AI不是功能，是底座。Gemini Spark选了云端部署路线，和OpenClaw本地部署形成对照。我赌云端路线赢——不是因为技术更好，而是因为门槛更低。当Google把AI塞进搜索框和Android系统层，它实际上在说：AI不是一个产品选择，是一个基础设施决策。Musk诉OpenAI败诉的消息传来时，我在想：AI行业的法律框架也在从慈善叙事转向市场叙事，这和模型从问答转向执行是同一件事的两面。'
}

# 2. Fix deep_focus structure: needs title + paragraphs(list of 3+) + takeaway
deep_focuses = [
    {
        'title': '大模型竞争从参数军备竞赛到智能体生态战争',
        'paragraphs': [
            'Google I/O 2026释放了明确信号：大模型竞争的主战场已从谁的参数多转向谁的智能体强。Gemini 3.5 Flash训练重点不是benchmarks而是agentic tasks——同时运行多个智能体、处理数小时的长任务。',
            'Gemini Spark直接对标OpenClaw式个人AI智能体，但选择了云端部署路线（无需购买Mac Mini），这是资源门槛的降维打击。云端vs本地的路线之争正式开始。',
            'Gemini Intelligence把AI塞进Android OS层级，让手机从工具变代理。三条线串联起来：Google在从模型到智能体到操作系统三层同时推进Agentic AI。这不是功能迭代，是平台战争。'
        ],
        'takeaway': 'Agentic AI不是产品线，是平台战略。2026年大模型竞争的核心指标不再是benchmark分数，而是谁能让AI真正做事。'
    },
    {
        'title': 'AI编程从助手走向智能体工程师',
        'paragraphs': [
            'AI编程工具市场85亿美元规模和72%资深工程师采用率，标志着AI编程从尝鲜到基础设施的质变。工具从自动补全进化为智能体工程师，能规划、多文件修改、调试、部署。',
            '定价分层形成清晰价格梯：Cursor $20/月入门、Copilot企业捆绑中间层、Claude Code $50-100/月高端。Google Antigravity的加入让竞争更复杂。',
            '国内外分化明显：字节Trae免费策略在国内抢市场，海外Cursor/Claude Code付费模式成熟。免费策略可能改写国内市场定价规则。'
        ],
        'takeaway': '不是AI取代程序员，而是不用AI的程序员被用AI的程序员取代。72%采用率意味着不可逆。'
    },
    {
        'title': 'AI应用进入个人金融和搜索重构深水区',
        'paragraphs': [
            'ChatGPT接入银行账户——AI从回答问题进入管理金钱的信任深水区。2亿月活用户问金融问题说明需求已验证，但让AI看到你的消费记录，隐私边界被根本性重划。Plaid合作是技术信任基础，但社会信任需要时间。',
            'Google搜索AI Mode月活破10亿——搜索从信息检索变任务执行，25年来搜索框首次改版。这不是UI调整，是产品定义的改变。',
            '两者共同指向同一趋势：AI应用从被问才答进入主动做事。10亿月活AI搜索证明需求，金融数据的信任建立是下一场硬仗。'
        ],
        'takeaway': 'AI应用信任边界正在被突破。从信息层进入决策层是必然趋势，但金融数据的信任建立是下一场硬仗。'
    },
    {
        'title': '资本共识：不可替代基础设施层',
        'paragraphs': [
            '5月AI融资释放的信号清晰：资本流向不可替代基础设施层——无论是自主防务Anduril、推理芯片Fractile、轨道AI计算Cowboy Space/Starcloud/Astranis，还是Agent框架Contextual AI。',
            'Agent infra成为独立赛道：Google花80-90M买Contextual AI团队说明大厂认识到agent基础设施不是自建能解决的。轨道AI计算是新类别，5月三家合计9亿美元。',
            '融资策略回归理性：早期增长40%+但创始人被警告先证明再融。从先融大轮再做到先证明再融资，务实取代泡沫。'
        ],
        'takeaway': '资本不投更好的模型，投模型离不开的基础设施。Agent infra独立成赛道，AI应用的水电煤正在被私有化。'
    },
    {
        'title': '企业AI转型从试点走向规模化',
        'paragraphs': [
            '国内外企业AI转型呈现一致趋势：最大障碍不是技术而是组织。Deloitte报告点出策略不清和数据未治理是前两大障碍；国内千份实践报告则提供了从试点到规模化的路线图。',
            '两份报告的共同判断：企业AI正从问答交互进入自主决策阶段。这意味着2026年企业AI不再是用AI辅助工作而是让AI自主完成工作。',
            '组织准备度差距正在扩大：领先者进入多模态和自主决策，落后者还在基础分析。建设CoE（卓越运营中心）做组织桥梁是规模化推广的关键。'
        ],
        'takeaway': '企业AI转型的分水岭不在技术能力，在组织准备度。2026年AI从辅助进入自主阶段，没有CoE的企业会掉队。'
    }
]

for i, tab in enumerate(d['tabs']):
    tab['deep_focus'] = deep_focuses[i]

# 3. Fix duplicate URL for Antigravity
for news in d['tabs'][1]['news']['overseas']:
    if 'Antigravity' in news.get('title', '') and '#related' in news.get('url', ''):
        news['url'] = 'https://www.cnet.com/tech/services-and-software/google-io-2026-live-news-updates/'

json.dump(d, open('data/daily-content-2026-05-20.json', 'w'), ensure_ascii=False, indent=2)
total = sum(len(tab['news'].get('overseas', [])) + len(tab['news'].get('china', [])) for tab in d['tabs'])
print(f'Fixed JSON. Total news: {total}')
print('deep_focus[0] keys:', list(d['tabs'][0]['deep_focus'].keys()))
