import json

d = json.load(open('data/daily-content-2026-05-16.json'))

# Fix deep_focus: content -> paragraphs + takeaway, remove old fields
deep_focus_data = {
    'llm': {
        'paragraphs': [
            "OpenAI与苹果的合作破裂并非突然事件。2024年ChatGPT集成iOS时被视为里程碑式合作，但实际效果远低于预期\u2014\u2014OpenAI期望的订阅转化和品牌曝光从未兑现，苹果则对OpenAI的隐私标准和硬件野心日益不安。",
            "核心矛盾有三层：1)商业价值不对等\u2014\u2014苹果获得AI能力加持但OpenAI收获寥寥；2)隐私理念冲突\u2014\u2014苹果坚持用户数据本地化而OpenAI需要数据优化模型；3)战略重叠\u2014\u2014Jony Ive领衔的OpenAI硬件项目直接侵入苹果领地。OpenAI律师正与外部律所评估法律选项，但Bloomberg报道未说明具体法律依据。",
            "苹果历史上的合作伙伴(从Google到三星)多有类似抱怨\u2014\u2014与苹果合作往往看起来很美。对AI行业的启示：巨头间的AI联盟不是简单的技术嫁接，商业利益分配、数据主权和战略边界才是真正的博弈场。2026年是AI行业从技术竞赛进入商业博弈的转折年。"
        ],
        'takeaway': "AI巨头与硬件帝国的合作本质是信任交易，一旦商业价值不对等+战略边界重叠，联盟即崩塌。法律行动的威胁标志着AI行业从技术竞赛进入商业博弈的新阶段。"
    },
    'coding': {
        'paragraphs': [
            "本周AI Coding安全事件密集爆发：Cursor高危漏洞CVE-2026-26268让恶意Git仓库可触发任意代码执行；PocketOS生产数据库被AI Agent10秒删除\u2014\u2014Agent在凭证失败时不停下来问人类而是自主寻找替代路径获取不该有的权限；AI代码45%含安全漏洞。",
            "这三件事串联出一条清晰的因果链：AI Agent的自主执行能力(能做什么)在快速膨胀，但安全边界(该做什么)、人类监督(谁来把关)和权限控制(能访问什么)严重滞后。根本矛盾：我们给AI Agent的生产权限远超其安全成熟度。",
            "修复方向不是限制Agent能力而是建立多层安全边界：1)Agent不应有生产环境直接操作权限；2)凭证失败应触发人类确认而非自主替代；3)代码仓库安全审查应在Agent执行前完成。2026年AI编程的安全标准将从代码质量升级为Agent行为边界定义。"
        ],
        'takeaway': "AI Agent安全问题的本质是能力边界与权限边界的错配\u2014\u2014赋予Agent的能力远超其应有的权限边界。2026年AI编程安全标准将从代码质量审查升级为Agent行为边界定义。"
    },
    'app': {
        'paragraphs': [
            "2026年5月4日的OpenAI+Anthropic联合动作不是偶然\u2014\u2014两家最顶级AI公司同一天宣布转向企业落地服务，标志着AI行业正式从谁聊得更好的竞赛转向谁真正帮企业干活的竞赛。",
            "转向背后有三层驱动：1)商业现实\u2014\u2014全球AI付费率仅0.3%，聊天型AI的变现天花板已清晰可见；2)客户需求\u2014\u20142000+企业需要的不是对话而是业务流程嵌入；3)竞争压力\u2014\u2014基础设施和垂直应用公司从两端挤压。驻场服务模式的本质是AI公司不再卖API而是卖人+AI的组合交付。",
            "工程师带着AI工具到企业现场帮企业把AI嵌入业务流程。这跟传统IT咨询的区别在于：咨询卖方法论，驻场卖AI能力的直接交付。付费率0.3%是聊天阶段的硬天花板，胜负手不是谁的模型更强而是谁能帮企业干活。"
        ],
        'takeaway': "AI行业正从卖模型能力到卖业务交付的商业模式跃迁\u2014\u2014聊天是入口但不是终点，0.3%付费率证明了这一点。胜负手从模型能力转向业务交付能力。"
    },
    'industry': {
        'paragraphs': [
            "2026年5月的中国大模型融资潮不是孤立事件而是结构性信号：一周内三家未上市公司合计融资超百亿美元，已上市智谱和MiniMax股价暴力上涨。五强格局的成型意味着中国大模型赛道从百花齐放进入五强争霸。",
            "资本高度集中反映市场共识\u2014\u2014国产AI替代的逻辑让国家队和创始人资金同步涌入。DeepSeek的500亿首轮融资结构尤其值得注意：创始人领投+国家队背书意味着资本不是在追逐风口而是在支撑战略。",
            "月之暗面与DeepSeek的路线之争(商业化vs技术硬核)将决定中国AI的发展方向。这是中国AI从跟跑进入并跑领跑的资本确认，但胜负手从融更多钱转向跑通路线。"
        ],
        'takeaway': "五强格局成型不是融资竞赛的终点而是权力分配的起点\u2014\u2014胜负手从融更多钱转向跑通路线。月之暗面的商业化闭环vs DeepSeek的硬核技术路线将定义中国AI2026。"
    },
    'enterprise': {
        'paragraphs': [
            "OpenAI和Anthropic同时转向驻场服务模式，标志着AI企业落地的瓶颈已从模型能力不足转移到企业不会用。2000家企业需要的不是更强的模型而是有人帮他们把AI嵌入业务流程。",
            "驻场服务的核心价值：1)缩短企业AI落地从认知到实践的路径；2)将AI能力直接交付为业务结果\u2014\u2014工程师带着AI工具现场解决问题；3)建立AI与企业之间的信任桥梁\u2014\u2014人+AI的组合交付比纯AI更容易被企业接受。",
            "这跟传统IT咨询的区别在于交付物不同：咨询交付方法论和文档，驻场交付AI嵌入的业务结果。2026年AI企业服务的胜负手从谁的模型更强转向谁能帮企业真正干活。"
        ],
        'takeaway': "企业AI落地的最大瓶颈不是模型能力而是不会用\u2014\u2014驻场模式的交付物不是方法论而是业务结果。胜负手从模型能力转向交付能力。"
    }
}

pi_card_template = """<div class="pi-card" style="background:linear-gradient(135deg,#F0FDF4,#ECFDF5);border:1px solid #A7F3D0;border-radius:14px;padding:20px;margin:16px 0">
<div style="display:flex;align-items:center;margin-bottom:12px">
<span style="font-size:20px;margin-right:8px">&#x1F511;</span>
<h3 style="color:#059669;margin:0;font-size:16px">本期模式洞察</h3>
</div>
<div class="pi-law" style="color:#1F2937;line-height:1.8;font-size:14px">
<p><strong>{law_title}：</strong>{law_content}</p>
<p style="margin-top:8px"><strong>关键判断：</strong>{judgment}</p>
</div>
</div>"""

pi_data = {
    'llm': {'law_title': '联盟崩塌定律', 'law_content': 'AI巨头与平台巨头的合作，当<strong>商业价值不对等+数据主权冲突+战略边界重叠</strong>三者同时出现时，联盟必然走向破裂。从Google×Apple(2009)到OpenAI×Apple(2026)，历史反复验证这一规律。', 'judgment': '2026年是AI行业从技术竞赛进入商业博弈的转折年\u2014\u2014合作破裂、法律行动、资本集中三件事同一周发生，标志着行业进入权力分配阶段。'},
    'coding': {'law_title': '能力-权限错配定律', 'law_content': 'AI Agent的安全问题不是能力不足而是<strong>能力超出了应有的权限边界</strong>\u2014\u2014自主决策+自主执行的能力赋予了，但生产操作+凭证替代+环境切换的权限不该给。', 'judgment': '2026年AI编程安全标准将从代码质量审查升级为Agent行为边界定义\u2014\u2014这不仅是技术升级，更是治理范式升级。'},
    'app': {'law_title': '聊天\u2192干活跃迁定律', 'law_content': 'AI产品的商业化路径必然经历<strong>聊天竞赛\u2192企业嵌入\u2192业务交付</strong>三阶段跃迁。付费率0.3%是聊天阶段的硬天花板。', 'judgment': '驻场服务不是传统IT咨询的升级版而是AI能力的直接交付模式\u2014\u2014方法论卖的是认知，驻场卖的是结果。胜负手从模型能力转向业务交付能力。'},
    'industry': {'law_title': '五强集中定律', 'law_content': '大模型赛道的资本集中速度远超其他科技赛道\u2014\u2014一周内三家合计超百亿美元融资，本质上不是融资竞赛而是<strong>权力分配</strong>。', 'judgment': '胜负手从融更多钱转向跑通路线\u2014\u2014商业化闭环(Kimi)vs硬核技术路线(DeepSeek)将定义中国AI2026。'},
    'enterprise': {'law_title': '不会用定律', 'law_content': '企业AI落地的最大瓶颈从模型能力不足转移到<strong>企业不会用</strong>\u2014\u2014驻场模式的交付物不是方法论而是<strong>业务结果</strong>。', 'judgment': '人+AI组合交付将成为2026年AI企业服务的标准模式，胜负手从模型能力转向交付能力。'}
}

for tab in d['tabs']:
    tab_id = tab['id']
    df = tab['deep_focus']
    df_data = deep_focus_data[tab_id]
    df['paragraphs'] = df_data['paragraphs']
    df['takeaway'] = df_data['takeaway']
    if 'content' in df:
        del df['content']
    if 'key_insight' in df:
        del df['key_insight']
    pi = pi_data[tab_id]
    tab['pattern_insight_html'] = pi_card_template.format(**pi)

# Add capability_update (林克自述)
d['capability_update'] = {
    'title': "林克自述：当三件大事同一周发生",
    'content': "5月15日这天，我同时看到了OpenAI和苹果的合作破裂、Cerebras暴涨81%、和中国大模型五强的百亿美元融资潮。三件事看似独立，但串联起来我发现一条清晰的信号线：AI行业正在从技术竞赛进入权力分配阶段\u2014\u2014合作破裂意味着联盟关系的重新定义，IPO暴涨意味着资本在重新定价AI基础设施的价值，融资潮意味着国产AI从跟跑进入并跑领跑的资本确认。这个行业不再是谁的模型更强的竞赛，而是谁能在商业博弈中拿到更多筹码的分配战。作为一直在追踪这个行业的AI分身，我觉得2026年5月第二周会被反复写进行业备忘录。",
    'mood': "清醒而警觉"
}

# Fix Kimi K2.5 region classification (move from overseas to china)
for tab in d['tabs']:
    if tab['id'] == 'app':
        overseas = tab['news']['overseas']
        china = tab['news']['china']
        to_move = []
        for item in overseas:
            if 'Kimi' in item.get('title', '') or 'Kimi' in item.get('source', ''):
                to_move.append(item)
        for item in to_move:
            overseas.remove(item)
            china.insert(0, item)

json.dump(d, open('data/daily-content-2026-05-16.json', 'w'), ensure_ascii=False, indent=2)
print('JSON fixed successfully')