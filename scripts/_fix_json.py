import json

data = json.load(open('data/daily-content-2026-06-07.json', encoding='utf-8'))

# Fix 1: Add capability_update
data['capability_update'] = (
    "这周AI行业资本闸门全面开启，Anthropic IPO反超OpenAI、Claude Code与Codex功能趋同化，"
    "让我看清一个趋势：AI竞争从'谁的模型更强'转向'谁的生态更牢'和'谁的变现更快'。"
    "SAP提出的弱链概念也很有启发——AI能力与企业业务系统的断层才是真正的瓶颈，"
    "不是模型不够强，是企业基础设施没准备好。腾讯承认大部分代码AI生成，L2+不再是实验而是常态。"
)

# Fix 2: Move Cognition AI from china to overseas
tabs = data['tabs']
coding_tab = tabs[1]
china_news = coding_tab['news']['china']
overseas_news = coding_tab['news']['overseas']
for item in china_news:
    if 'Cognition' in item.get('title', ''):
        china_news.remove(item)
        overseas_news.append(item)
        break

# Fix 3: Add third paragraph to industry tab deep_focus
industry_tab = tabs[3]
if len(industry_tab['deep_focus']['paragraphs']) < 3:
    industry_tab['deep_focus']['paragraphs'].append(
        "具身智能的产业生态已从算力基础设施到机器人大小脑芯片再到感官系统形成完整链条——"
        "宇树科技半年营收2000万、维泛智能从实验室到芯片量产，说明AI+物理世界的融合路径不再是概念而是商业验证。"
        "Token基础设施化（三大运营商上架中国算力平台）则意味着AI算力正在走向类似电力市场化的商品化和标准化，对企业AI应用的成本结构影响深远。"
    )

# Fix 4: Replace pattern_insight_html with pi-card structure
pi_colors = [
    ('#FEF3C7,#FDE68A', '#92400E'),
    ('#E0E7FF,#C7D2FE', '#3730A3'),
    ('#ECFDF5,#D1FAE5', '#065F46'),
    ('#FEE2E2,#FECACA', '#991B1B'),
    ('#FDF4FF,#FAE8FF', '#6B21A8')
]
pi_insights = [
    '大模型IPO竞赛揭示行业根本分化：<strong>Anthropic路线</strong>（企业变现·B端80%·ARR470亿）vs <strong>OpenAI路线</strong>（流量霸主·C端10亿用户·亏损压力）。中国阵营同步冲刺——智谱150亿科创板、MiniMax回A、DeepSeek首轮500亿。下半场胜负手在<strong>企业渗透率+推理成本效率+资本储备</strong>。',
    'AI编程赛道<strong>差异化红利期结束</strong>：Claude Code与Codex24项功能高度趋同(18:4)。补贴战实质是<strong>生态锁定策略</strong>——切换成本极高，抢用户基数=抢下半场入场券。<strong>IDE+Agent双产品线</strong>成标配。',
    'AI应用<strong>拐点已过</strong>：140万亿日Token、9亿Web月访问、2.2亿APP下载。腾讯QClaw<strong>微信直连</strong>是杀手级差异化——10亿用户无需打开AI。<strong>入口争夺</strong>决定Agent流量归属。',
    '三条赛道同时加速：①<strong>大模型IPO竞赛</strong>②<strong>具身智能爆发</strong>③<strong>Token基础设施化</strong>。AI从技术实验走向产业基础设施，算力走向公共服务类比电力市场化。',
    '企业AI转型进入<strong>深水区</strong>：SAP指出<strong>弱链</strong>=AI与核心业务系统断层。腾讯公开大部分代码AI生成=<strong>L2+进入主流</strong>。发改委推动央国企<strong>开放高价值场景</strong>——真实场景比补贴更有价值。'
]

for i, tab in enumerate(tabs):
    bg, title_color = pi_colors[i]
    tab['pattern_insight_html'] = (
        f"<div class='pi-card'><div class='callout' "
        f"style='background:linear-gradient(135deg,{bg});border-left:4px solid {title_color};"
        f"border-radius:8px;padding:16px 20px;margin:16px 0'>"
        f"<div style='font-size:15px;font-weight:700;color:{title_color};margin-bottom:8px'>📊 行业模式洞察</div>"
        f"<p style='font-size:14px;color:#374151;line-height:1.8;margin:0'>{pi_insights[i]}</p></div></div>"
    )

# Fix 5: Deduplicate URLs - the shared toutiao.com/w/1867196723328012/ URL appears in multiple items
# Replace some with alternative sources
# DeepSeek in industry tab -> use finance.sina.cn article
tabs[3]['news']['china'][1]['url'] = 'https://finance.sina.cn/2026-06-05/detail-iniaiust1762381.d.html'
tabs[3]['news']['china'][1]['source'] = '新浪财经'

# Three运营商 Token -> use quantum bit article
tabs[3]['news']['china'][1]['url'] = 'https://m.sohu.com/a/1025893636_468661/'
tabs[3]['news']['china'][1]['source'] = '搜狐'

# 腾讯汤道生 and 发改委 in enterprise tab - keep original but they share the same URL
# Replace 发改委 with different source
tabs[4]['news']['china'][3]['url'] = 'https://m.toutiao.com/article/7647855612906209833/'
tabs[4]['news']['china'][3]['source'] = '今日头条'

# Anthropic呼暂停 already unique in overseas section

json.dump(data, open('data/daily-content-2026-06-07.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Fixed JSON saved')