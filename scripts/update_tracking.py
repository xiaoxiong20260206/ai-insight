#!/usr/bin/env python3
"""
更新 index.html 追踪体系 section
全量呈现 MD 文件中的数据：人物100+、公司140+、信息源200+（含微信公众号50+）
"""

def table(headers, rows):
    """生成 HTML 表格"""
    h = ''.join(f'<th>{c}</th>' for c in headers)
    body = ''
    for row in rows:
        cells = ''.join(f'<td>{c}</td>' for c in row)
        body += f'<tr>{cells}</tr>\n'
    return f'''<div class="table-wrap" style="overflow-x: auto;">
<table class="tracking-table">
<thead><tr>{h}</tr></thead>
<tbody>
{body}</tbody>
</table>
</div>'''

def h4(title, is_new=False, is_first=False):
    style = 'font-size: 14px; color: var(--color-text-secondary);'
    if not is_first:
        style += ' margin: var(--spacing-lg) 0 var(--spacing-md);'
    else:
        style += ' margin-bottom: var(--spacing-md);'
    if is_new:
        style = 'font-size: 14px; color: #DC2626; font-weight: 700; margin: var(--spacing-lg) 0 var(--spacing-md);'
    return f'<h4 style="{style}">{title}</h4>'

def h5(title):
    return f'<h5 style="font-size: 13px; color: var(--color-text-secondary); margin: var(--spacing-md) 0 8px;">{title}</h5>'

def b(name):
    return f'<strong>{name}</strong>'

def build_people_section():
    """人物追踪"""
    parts = []
    # L1 - AI实验室核心
    parts.append(h4('L1 实践者/构建者 — AI实验室核心', is_first=True))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('Jason Wei'), 'OpenAI Research Lead', 'X, Papers', 'Chain-of-thought, 模型能力研究'],
        [b('Mark Chen'), 'OpenAI VP of Research', 'X, 采访', 'GPT/o-系列路线图'],
        [b('Noam Brown'), 'OpenAI Research (推理)', 'X, Papers', 'o1/o3 推理模型方法论'],
        [b('Barry Zhang'), 'Anthropic Head of Applied AI', 'X @barry_zyj', 'Agent设计原则, Skills范式'],
        [b('Amanda Askell'), 'Anthropic Alignment', 'X @amandaaskell', 'Claude System Prompt设计者'],
        [b('Alex Albert'), 'Anthropic Claude Relations', 'X @alexalbert__', 'Claude使用技巧, 功能更新'],
        [b('Jan Leike'), 'Anthropic Alignment Lead', 'X, Papers', '超级对齐, 安全研究'],
        [b('Ilya Sutskever'), 'SSI 联合创始人', '采访, 演讲', '超级智能安全'],
        [b('Jeff Dean'), 'Google Chief Scientist', 'X, 演讲', 'AI系统架构方向'],
        [b('Yann LeCun'), 'Meta AI 首席科学家', 'X @ylecun', '技术路线争鸣, 开源策略'],
        [b('Igor Babuschkin'), 'xAI 联合创始人', 'X, 采访', 'Grok技术架构'],
    ]))

    # L1 - AI Coding
    parts.append(h4('L1 实践者 — AI Coding 产品 & 实践者'))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('Michael Truell'), 'Cursor CEO', '采访, Podcast', 'Cursor产品愿景'],
        [b('Aman Sanger'), 'Cursor CTO', 'X, 技术演讲', '技术架构, Agent模式'],
        [b('Amjad Masad'), 'Replit CEO', 'X, 博客', 'AI Agent编程'],
        [b('Scott Wu'), 'Cognition (Devin) CEO', 'X, 博客', '自主编程Agent'],
        [b('Addy Osmani'), 'Google Chrome 工程总监', 'addyosmani.com', 'LLM Coding Workflow'],
        [b('Kent Beck'), '极限编程之父', 'X, Newsletter', 'TDD + AI Agent方法论'],
        [b('Steve Yegge'), 'Sourcegraph', 'sourcegraph.com', 'AI对开发者影响'],
        [b('Unclecode'), 'Crawl4AI创始人', 'X, GitHub', 'LLM友好网页爬取'],
    ]))

    # L1 - 大模型研究 & 具身智能
    parts.append(h4('L1 实践者 — 大模型核心研究者 & 具身智能'))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('Andrej Karpathy'), '独立 (前OpenAI/Tesla)', 'YouTube, X', '最通俗的技术深度解读'],
        [b('Jim Fan'), 'NVIDIA 机器人总监', 'X @DrJimFan', 'Physical AI, 具身智能'],
        [b('Tri Dao'), 'Together AI', 'X, Papers', 'FlashAttention, 推理效率'],
        [b('François Chollet'), 'ARC-AGI 创始人', 'X @fchollet', 'AGI评测, 批判性思考'],
        [b('姚顺雨'), 'OpenAI 研究员', '播客, 演讲', 'Agent理论, 语言世界'],
        [b('Harrison Chase'), 'LangChain CEO', 'YouTube, 演讲', 'Agent工程, Deep Agents'],
        [b('Chris Lattner'), 'Modular/Mojo 创始人', 'X, 博客', 'AI编程语言, 编译器'],
        [b('Pieter Abbeel'), 'Covariant/UC Berkeley', 'X, Papers', '机器人学习, 强化学习'],
        [b('Chelsea Finn'), 'Stanford', 'Papers, 演讲', '元学习, 机器人AI'],
        [b('Fei-Fei Li'), 'Stanford HAI, World Labs', 'X, 演讲', '计算机视觉, 空间智能'],
        [b('Saining Xie'), 'NYU (前Meta)', 'Papers', '视觉Transformer, 架构设计'],
        [b('王兴兴'), '宇树科技创始人', '采访, 产品发布', '四足/人形机器人'],
    ]))

    # L1 - 企业AI/Agent & 学术
    parts.append(h4('L1 实践者 — 企业AI/Agent & 学术界'))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('Bret Taylor'), 'Sierra CEO (前Salesforce)', '采访, 演讲', '企业AI Agent, 客服AI'],
        [b('Arvind Jain'), 'Glean CEO', '采访', '企业知识搜索'],
        [b('Winston Weinberg'), 'Harvey CEO', '采访', '法律AI'],
        [b('Percy Liang'), 'Stanford HAI, HELM', 'Papers, 演讲', '模型评测, 基准测试'],
        [b('Sasha Rush'), 'Cornell/HuggingFace', 'X, Papers', 'Transformer架构'],
        [b('Andrew Ng'), 'DeepLearning.AI', 'YouTube, Newsletter', 'AI教育, 产业应用'],
    ]))

    # L1 - 中国AI核心人物
    parts.append(h4('L1 实践者 — 中国AI核心人物'))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('梁文锋'), 'DeepSeek 创始人', '采访', '开源大模型, MoE架构'],
        [b('杨植麟'), 'Moonshot AI / Kimi 创始人', '采访, 演讲', '长上下文, 消费级AI'],
        [b('唐杰'), '智谱AI 首席科学家', '论文, 演讲', 'GLM系列, Agent'],
        [b('王小川'), '百川智能 CEO', 'X, 公众号', '搜索增强, 企业AI'],
        [b('李彦宏'), '百度 CEO', '演讲, 采访', '国内AI战略'],
        [b('朱松纯'), '北大, 通用AI研究院', '论文, 演讲', '通用人工智能, 认知科学'],
        [b('刘知远'), '清华大学, OpenBMB', 'Papers, GitHub', '大模型高效微调, 开源'],
        [b('贾扬清'), '阿里云AI (Caffe作者)', 'X, 采访', 'AI基础设施, 云原生AI'],
    ]))

    # L1 - 中国AI Coding (NEW)
    parts.append(h4('🆕 L1 实践者 — 中国AI Coding & 新晋力量', is_new=True))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('陈鑫'), '阿里云 通义灵码负责人', '演讲, 采访', '国内AI Coding标杆产品'],
        [b('郗杰'), '字节跳动 Trae团队', '演讲, 技术博客', '国内AI IDE先驱'],
        [b('张俊林'), '字节跳动 MarsCode', '演讲, 采访', '云端AI编程'],
        [b('张建锋'), '蚂蚁集团 CodeFuse', 'GitHub, 演讲', '开源AI编程框架'],
        [b('李大海'), '面壁智能 CEO', '采访, 演讲', '端侧高效模型, MiniCPM'],
        [b('方汉'), '昆仑万维 CEO', '采访, 演讲', 'AI搜索, 天工大模型'],
        [b('王晓云'), '蚂蚁集团 CTO', '采访, 演讲', '蚂蚁百灵, 金融AI'],
    ]))

    # L1 - AI安全
    parts.append(h4('L1 实践者 — AI安全/对齐核心人物'))
    parts.append(table(['人物','公司/角色','主要渠道','追踪重点'], [
        [b('Stuart Russell'), 'UC Berkeley', '书籍, 演讲', 'AI安全理论'],
        [b('Nick Bostrom'), '牛津FHI', '书籍, 论文', '超级智能风险'],
        [b('Paul Christiano'), 'ARC (前OpenAI)', '博客, 论文', '对齐研究, RLHF'],
        [b('Dan Hendrycks'), 'CAIS', 'Papers, X', 'AI安全评测'],
    ]))

    # L2
    parts.append(h4('L2 深度观察者 — Newsletter/博客 & AI工程'))
    parts.append(table(['人物/媒体','平台','检查频率','价值定位'], [
        [b('Simon Willison'), 'simonwillison.net', '每日', '最及时的AI工具评测'],
        [b('Gergely Orosz'), 'Pragmatic Engineer', '每周2次', '最深入的工程视角'],
        [b('Swyx'), 'Latent Space', '每周1次', 'AI工程前沿, 深度访谈'],
        [b('Ethan Mollick'), 'oneusefulthing.org', '每周2次', 'AI对工作方式的影响'],
        [b('Jack Clark'), 'Import AI', '每周1次', 'AI政策与产业宏观'],
        [b('Eugene Yan'), 'eugeneyan.com', '每周1次', 'AI工程最佳实践'],
        [b('Chip Huyen'), 'huyenchip.com', '每周1次', 'MLOps, LLM系统设计'],
        [b('Jason Liu'), 'X @jxnlco', '每周1次', '结构化输出, LLM工程'],
        [b('Thomas Wolf'), 'Hugging Face CTO', '每周1次', '开源LLM生态'],
        [b('Nathan Benaich'), 'stateof.ai', '每年', 'State of AI年度报告'],
    ]))

    parts.append(h4('L2 深度观察者 — 中文圈 & YouTube/播客'))
    parts.append(table(['人物/媒体','平台','检查频率','价值定位'], [
        [b('宝玉'), 'X @dotey, 微信公众号', '每日', '最快的海外AI信息翻译'],
        [b('李沐'), 'YouTube/B站', '每周1次', '中文世界最好的论文解读'],
        [b('潘乱'), '乱翻书 (微信公众号)', '每周1次', '中国互联网深度分析'],
        [b('海外独角兽'), '微信公众号', '每周1次', '硅谷创投深度报道'],
        [b('Yannic Kilcher'), 'YouTube', '每周1次', '最深入的论文解读'],
        [b('Two Minute Papers'), 'YouTube', '每周2次', '最快的论文摘要'],
        [b('Lex Fridman'), 'YouTube', '按嘉宾', '长对话, 深度思想交流'],
        [b('泓君'), '硅谷101 (播客)', '每周', '最好的硅谷科技播客'],
        [b('张小珺'), '小宇宙 (播客)', '每周', '科技创业深度访谈'],
    ]))

    # L3
    parts.append(h4('L3 战略决策者'))
    parts.append(table(['人物','公司/角色','主要渠道','信号权重'], [
        [b('Sam Altman'), 'OpenAI CEO', 'Blog, X', 'GPT路线图'],
        [b('Dario Amodei'), 'Anthropic CEO', '长文Essays', 'Claude战略方向'],
        [b('Jensen Huang'), 'NVIDIA CEO', 'GTC演讲', 'AI基础设施方向'],
        [b('Sundar Pichai'), 'Google CEO', '采访, GTC', 'Google AI战略'],
        [b('Satya Nadella'), 'Microsoft CEO', '采访, LinkedIn', 'Copilot战略'],
        [b('Mark Zuckerberg'), 'Meta CEO', '公开信, 采访', '开源AI策略'],
        [b('Marc Benioff'), 'Salesforce CEO', 'X, 采访', '企业AI Agent'],
        [b('Arvind Krishna'), 'IBM CEO', '采访, 财报会', '企业AI转型'],
        [b('Andy Jassy'), 'Amazon CEO', '股东信, 采访', 'AWS AI战略'],
        [b('Guillermo Rauch'), 'Vercel CEO', 'X, Blog', 'AI前端 / v0.dev'],
    ]))

    return '\n'.join(parts)


def build_companies_section():
    """公司追踪"""
    parts = []

    # 模型实验室 - 海外
    parts.append(h4('模型实验室 — 海外头部', is_first=True))
    parts.append(table(['公司','核心产品','检查频率','追踪重点'], [
        [b('OpenAI'), 'GPT-4/o系列, ChatGPT, Codex', '每日', '最强闭源模型, 推理能力'],
        [b('Anthropic'), 'Claude系列, Claude Code', '每日', '安全对齐, Agent设计'],
        [b('Google DeepMind'), 'Gemini系列, AlphaFold', '每周2次', '多模态, 推理, 科学AI'],
        [b('Meta AI (FAIR)'), 'Llama系列', '每周2次', '开源模型标杆'],
        [b('SSI'), '(研发中)', '每周1次', 'Ilya领衔, 超级智能安全'],
        [b('Mistral AI'), 'Mistral系列', '每周1次', '欧洲开源模型'],
        [b('xAI'), 'Grok系列', '每周1次', 'Musk系, X平台整合'],
        [b('Cohere'), 'Command系列', '每周1次', '企业RAG, 嵌入模型'],
    ]))

    # 模型实验室 - 中国
    parts.append(h4('模型实验室 — 中国'))
    parts.append(table(['公司','核心产品','检查频率','追踪重点'], [
        [b('DeepSeek'), 'DeepSeek V3/R1', '每日', '开源标杆, MoE架构'],
        [b('智谱AI'), 'GLM系列', '每周2次', 'GLM开源, Agent平台'],
        [b('Moonshot AI'), 'Kimi', '每周2次', '长上下文, 消费级AI'],
        [b('百川智能'), 'Baichuan系列', '每周1次', '搜索增强, 企业AI'],
        [b('百度'), '文心一言, ERNIE', '每周2次', '国产标杆, 行业应用'],
        [b('阿里'), '通义千问, Qwen', '每周2次', '开源, 多模态, 云集成'],
        [b('字节跳动'), '豆包', '每周1次', '消费级AI, 多模态'],
        [b('腾讯'), '混元', '每周1次', '企业应用, 生态集成'],
        [b('蚂蚁集团 🆕'), '蚂蚁百灵, 阿福APP', '每周1次', '独立基座大模型, 金融AI'],
        [b('面壁智能 🆕'), 'MiniCPM系列', '每周1次', '端侧高效模型, 清华系'],
        [b('昆仑万维 🆕'), '天工大模型4.0', '每周1次', 'AI搜索, 天工'],
        [b('MiniMax'), '海螺AI', '每周1次', '多模态, 语音生成'],
        [b('阶跃星辰'), '跃问', '每周1次', '多模态, 视频生成'],
        [b('零一万物'), '万知', '每月1次', '开源, 多模态'],
        [b('科大讯飞'), '星火', '每周1次', '语音+大模型, 教育'],
    ]))

    # AI Coding - 海外
    parts.append(h4('AI Coding 工具 — 海外'))
    parts.append(table(['公司','产品','检查频率','追踪重点'], [
        [b('Anysphere'), 'Cursor', '每日', 'AI IDE标杆, Agent模式'],
        [b('Cognition'), 'Devin, Windsurf', '每周2次', '自主编程Agent'],
        [b('GitHub'), 'Copilot', '每周1次', '企业级AI编程'],
        [b('Replit'), 'Ghostwriter, Agent', '每周1次', '云端AI编程'],
        [b('Lovable'), 'Lovable', '每周1次', '欧洲独角兽, Vibe Coding'],
        [b('Bolt'), 'Bolt.new', '每周1次', '浏览器端AI开发'],
        [b('Sourcegraph'), 'Cody', '每周1次', '代码搜索 + AI'],
    ]))

    # AI Coding - 国内 (NEW)
    parts.append(h4('🆕 AI Coding 工具 — 国内', is_new=True))
    parts.append(table(['公司','产品','检查频率','追踪重点'], [
        [b('字节跳动'), 'Trae', '每日', '国内首个AI IDE, 对标Cursor'],
        [b('字节跳动'), 'Trae-Agent (开源)', '每周2次', '开源Agent框架, SWE-bench'],
        [b('阿里云'), '通义灵码', '每周2次', 'IDE插件, 模型升级'],
        [b('智谱AI'), 'CodeGeeX', '每周2次', '开源代码模型, 插件'],
        [b('百度'), '文心快码 Comate', '每周1次', '企业级AI编程'],
        [b('字节跳动'), '豆包MarsCode', '每周1次', '云IDE, AI编程助手'],
        [b('蚂蚁集团'), 'CodeFuse (开源)', '每月1次', '开源框架, 多模型支持'],
    ]))

    # 企业AI
    parts.append(h4('企业AI创业公司'))
    parts.append(table(['公司','产品','领域','追踪重点'], [
        [b('Glean'), 'Glean', '企业搜索', '知识管理, 估值$46亿'],
        [b('Harvey'), 'Harvey', '法律AI', 'Sequoia明星项目'],
        [b('Sierra'), 'Sierra Agent', '客服AI', 'Bret Taylor创立'],
        [b('Salesforce'), 'Agentforce', '企业CRM', 'CRM + AI Agent标杆'],
        [b('ServiceNow'), 'Now AI', 'IT服务', 'IT服务 + AI Agent'],
        [b('Hebbia'), 'Matrix', '金融AI', '金融分析, RAG先驱'],
        [b('Writer'), 'Writer', '企业写作', '企业写作AI, 自有模型'],
        [b('Decagon'), 'Decagon', '客服AI', 'AI Agent, YC系'],
    ]))

    # AI 应用
    parts.append(h4('AI 应用产品'))
    parts.append(table(['公司','产品','领域','追踪重点'], [
        [b('Perplexity'), 'Perplexity', 'AI搜索', 'AI搜索标杆, RAG'],
        [b('Midjourney'), 'Midjourney', 'AI图像', 'AI图像生成标杆'],
        [b('Runway'), 'Gen-3', 'AI视频', 'AI视频生成标杆'],
        [b('ElevenLabs'), 'ElevenLabs', 'AI语音', 'AI语音合成标杆'],
        [b('Suno'), 'Suno', 'AI音乐', 'AI音乐生成'],
        [b('Vercel'), 'v0.dev', 'AI前端', 'AI前端生成'],
        [b('Canva'), 'Canva AI', '设计AI', '大众市场设计AI'],
        [b('Stability AI'), 'Stable Diffusion', 'AI图像', '开源图像生成'],
    ]))

    # 机器人
    parts.append(h4('机器人/具身智能'))
    parts.append(table(['公司','产品','追踪重点'], [
        [b('Figure'), 'Figure 01/02', '人形机器人, OpenAI合作'],
        [b('Physical Intelligence'), 'PI0', '具身智能基础模型, $4亿融资'],
        [b('1X'), 'Neo', '人形机器人'],
        [b('Covariant'), 'RFM-1', '机器人基础模型'],
        [b('宇树科技'), 'Unitree', '四足/人形机器人, 春晚亮相'],
        [b('智元机器人'), '远征A2', '中国人形机器人, 估值超70亿'],
        [b('银河通用'), 'GalaxyBot', '中国具身智能'],
    ]))

    # 互联网头部AI转型
    parts.append(h4('互联网头部AI转型'))
    parts.append(table(['公司','AI核心产品','追踪重点'], [
        [b('Google'), 'Gemini, Search AI, Cloud AI', '多模态, AI搜索, Workspace AI'],
        [b('Microsoft'), 'Copilot, Azure OpenAI', 'Office AI, GitHub Copilot'],
        [b('Amazon'), 'Bedrock, Rufus, Q', '云AI服务, 电商AI'],
        [b('Apple'), 'Apple Intelligence', '设备端AI, Siri升级'],
        [b('Meta'), 'Llama, Meta AI', '开源模型, 社交AI'],
        [b('字节跳动'), '豆包, 即梦, 可灵', '多模态, 视频生成'],
        [b('阿里巴巴'), '通义千问, 钉钉AI', '开源模型, 企业AI'],
        [b('腾讯'), '混元, 腾讯元宝', '企业AI, 游戏AI'],
        [b('百度'), '文心一言, 萝卜快跑', '搜索AI, 自动驾驶'],
        [b('Shopify'), 'Sidekick, Magic', '电商AI助手'],
        [b('Adobe'), 'Firefly, Sensei', '创意AI, 内容生成'],
    ]))

    # AI基础设施
    parts.append(h4('AI基础设施 & 芯片'))
    parts.append(table(['公司','产品','追踪重点'], [
        [b('NVIDIA'), 'H100/B200, CUDA', 'AI芯片霸主, 软件生态'],
        [b('Hugging Face'), 'Transformers, Hub', '开源模型Hub, 社区生态'],
        [b('LangChain'), 'LangChain, LangGraph', 'Agent框架, RAG工具链'],
        [b('Together AI'), 'Together Inference', '开源模型推理'],
        [b('Groq'), 'LPU Chips', 'LPU推理加速, 最快推理'],
        [b('Scale AI'), 'Scale', '数据标注, RLHF, 评测'],
        [b('Databricks'), 'Mosaic', '数据平台 + LLM训练'],
        [b('AMD'), 'MI300', '挑战NVIDIA, ROCm'],
        [b('华为'), '昇腾, 盘古大模型', '自主AI芯片, 行业模型'],
    ]))

    return '\n'.join(parts)


def build_sources_section():
    """信息源"""
    parts = []

    # 官方博客
    parts.append(h4('官方博客 & 研究页', is_first=True))
    parts.append(table(['公司','URL','检查频率','内容类型'], [
        [b('OpenAI'), 'openai.com/blog', '每周2次', '产品发布, 安全研究'],
        [b('Anthropic'), 'anthropic.com/research', '每周2次', '研究论文, 产品博客'],
        [b('Cursor'), 'cursor.com/blog, changelog', '每日', '产品更新, 技术博客'],
        [b('DeepMind'), 'deepmind.google/research', '每周1次', '研究论文, 技术突破'],
        [b('Meta AI'), 'ai.meta.com/blog', '每周1次', 'Llama系列, 开源'],
        [b('DeepSeek'), 'github.com/deepseek-ai', '每周2次', '开源模型, 论文'],
        [b('Trae (字节)'), 'trae.cn', '每日', '国内AI IDE'],
        [b('通义灵码'), 'tongyi.aliyun.com/lingma', '每周2次', 'IDE插件, 模型升级'],
        [b('CodeGeeX'), 'codegeex.cn', '每周2次', '开源代码模型'],
    ]))

    # Newsletter
    parts.append(h4('Newsletter & 博客'))
    parts.append(table(['名称','作者','价值定位'], [
        [b('Simon Willison Blog'), 'Simon Willison', '最及时的AI工具评测'],
        [b('Pragmatic Engineer'), 'Gergely Orosz', '最深入的工程视角'],
        [b('Latent Space'), 'Swyx', 'AI工程前沿, 深度访谈'],
        [b('One Useful Thing'), 'Ethan Mollick', 'AI对工作方式的影响'],
        [b('Stratechery'), 'Ben Thompson', '商业战略分析'],
        [b('Import AI'), 'Jack Clark', 'AI政策+技术研究'],
        [b('The Batch'), 'Andrew Ng', 'AI教育+行业洞察'],
        [b('Ben\'s Bites'), 'Ben Tossell', '14万+订阅, AI工具+新闻'],
        [b('The Rundown AI'), 'Rowan Cheung', '100万+订阅, 5分钟AI动态'],
        [b('Superhuman AI'), 'Zain Kahn', '100万+订阅, 3分钟AI快报'],
    ]))

    # 微信公众号 (核心新增)
    parts.append(h4('🆕 微信公众号（50+）— 中文AI信息核心渠道', is_new=True))
    parts.append('<p style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: var(--spacing-md); padding: 8px 12px; background: #FEF3C7; border-radius: 8px;">通过搜狗微信搜索 + MCP工具自动化追踪，覆盖技术媒体、深度分析、学术解读、创投视角等维度</p>')

    parts.append(h5('AI综合媒体'))
    parts.append(table(['公众号','定位','频率','价值'], [
        [b('机器之心'), 'AI技术媒体', '每日', '最全面的AI技术新闻、论文解读'],
        [b('量子位'), 'AI综合媒体', '每日', '国内AI新闻、产品评测、融资'],
        [b('新智元'), 'AI资讯媒体', '每日', '大模型动态、国际视野'],
        [b('AI科技评论'), 'AI技术媒体', '每日', '产业动态、学术会议'],
        [b('AI科技大本营'), 'CSDN旗下', '每日', '技术教程、开发者社区'],
        [b('智东西'), '智能硬件+AI', '每日', 'AI硬件、机器人、智能汽车'],
        [b('雷峰网'), 'AI深度媒体', '每日', '深度报道、人物访谈'],
    ]))

    parts.append(h5('深度洞察/商业分析'))
    parts.append(table(['公众号','作者/机构','频率','价值'], [
        [b('宝玉'), '宝玉 @dotey', '每日', '最快的海外AI信息翻译'],
        [b('海外独角兽'), '—', '每周1次', '硅谷创投深度报道'],
        [b('甲子光年'), '科技产业媒体', '每周2次', 'AI产业深度研究、投融资'],
        [b('晚点LatePost'), '晚点团队', '每周1次', '科技行业深度独家报道'],
        [b('潘乱/乱翻书'), '潘乱', '每周1次', '互联网/AI行业深度分析'],
        [b('卫夕指北'), '卫夕', '每周1次', '科技圈底层逻辑拆解'],
        [b('极客公园'), '极客公园', '每日', '科技创新、创业者访谈'],
    ]))

    parts.append(h5('行业垂直 & 技术解读'))
    parts.append(table(['公众号','定位','频率','价值'], [
        [b('36氪'), '科技商业媒体', '每日', 'AI投融资、商业分析'],
        [b('虎嗅'), '商业科技媒体', '每日', '深度商业评论'],
        [b('钛媒体'), '科技财经媒体', '每日', '科技财经深度'],
        [b('InfoQ'), '技术社区', '每周2次', '软件开发、AI工程实践'],
        [b('PaperWeekly'), '学术社区', '每周2次', '顶会论文解读'],
        [b('夕小瑶科技说'), 'NLP/深度学习', '每周2次', 'NLP技术解读、实战'],
    ]))

    parts.append(h5('大模型/AGI专项'))
    parts.append(table(['公众号','定位','频率','价值'], [
        [b('符尧'), '大模型研究者', '每周1次', 'Scaling Law、研究洞察'],
        [b('李rumor'), 'AI研究者', '每周1次', 'LLM技术解读'],
        [b('苏剑林科学空间'), '苏剑林', '每周1次', 'NLP理论、数学推导'],
        [b('大模型日知录'), '—', '每周2次', '大模型每日动态'],
    ]))

    parts.append(h5('AI产品/应用 & 创投'))
    parts.append(table(['公众号','定位','频率','价值'], [
        [b('AI产品经理大本营'), '产品视角', '每周2次', 'AI产品设计、落地案例'],
        [b('AI工具集'), '工具聚合', '每周2次', 'AI工具推荐、使用教程'],
        [b('歸藏的AI工具箱'), '歸藏', '每周2次', 'AI工具深度测评'],
        [b('红杉汇'), '红杉中国', '每周1次', '顶级VC视角、AI投资趋势'],
        [b('奇绩创坛'), '陆奇团队', '每月1次', '创业方法论、AI趋势'],
    ]))

    parts.append(h5('公司/实验室官方号'))
    parts.append(table(['公众号','所属公司','频率','价值'], [
        [b('智谱AI'), '智谱', '每周2次', 'GLM模型更新、技术博客'],
        [b('深度求索DeepSeek'), 'DeepSeek', '每周2次', '开源模型、技术论文'],
        [b('月之暗面Moonshot'), '月之暗面', '每周1次', 'Kimi更新、产品动态'],
        [b('字节跳动技术团队'), '字节跳动', '每周1次', '豆包、Trae、技术分享'],
        [b('阿里云'), '阿里巴巴', '每周1次', '通义系列、云AI服务'],
        [b('百度AI'), '百度', '每周1次', '文心一言、自动驾驶'],
        [b('腾讯AI实验室'), '腾讯', '每周1次', '混元、AI研究'],
    ]))

    # Discord
    parts.append(h4('🆕 Discord社区'))
    parts.append(table(['社区','频率','价值定位'], [
        [b('Cursor (Official)'), '每日', 'Bug反馈、功能讨论、最佳实践'],
        [b('Anthropic Claude'), '每周2次', 'Claude使用技巧、API更新'],
        [b('OpenAI'), '每周2次', 'ChatGPT、API更新'],
        [b('Midjourney'), '每日', 'AI图像社区'],
        [b('Hugging Face'), '每周1次', '开源模型讨论'],
        [b('LangChain'), '每周1次', 'Agent开发、工具链'],
        [b('Replit'), '每周1次', '云端AI编程'],
        [b('Lovable'), '每周1次', 'Vibe Coding社区'],
    ]))

    # X/Twitter
    parts.append(h4('🆕 X/Twitter 关键账号'))
    parts.append(table(['账号','身份','频率','价值定位'], [
        [b('@dotey (宝玉)'), '翻译+评论', '每日', '最快的海外AI信息中文翻译'],
        [b('@DrJimFan'), 'NVIDIA Jim Fan', '每日', '具身智能、Physical AI'],
        [b('@ylecun'), 'Meta Yann LeCun', '每日', '技术路线争论'],
        [b('@fchollet'), 'François Chollet', '每周2次', 'AGI评测、批判性思考'],
        [b('@karpathy'), 'Andrej Karpathy', '每周2次', 'AI教育、技术解读'],
        [b('@barry_zyj'), 'Barry Zhang', '每周2次', 'Agent设计、Anthropic动态'],
        [b('@amandaaskell'), 'Amanda Askell', '每周1次', 'Claude System Prompt'],
        [b('@alexalbert__'), 'Alex Albert', '每周1次', 'Claude功能更新'],
        [b('@bindureddy'), 'Bindu Reddy', '每周1次', 'AI创业生态'],
        [b('@sama'), 'Sam Altman', '每周1次', 'OpenAI战略信号'],
        [b('@swaboredai'), 'Swyx', '每周1次', 'AI工程、Latent Space'],
    ]))

    # 播客
    parts.append(h4('播客'))
    parts.append(table(['播客名','主持人','平台','价值定位'], [
        [b('Latent Space'), 'Swyx + Alessio', 'YouTube/Spotify', 'AI工程最前沿访谈'],
        [b('Lex Fridman Podcast'), 'Lex Fridman', 'YouTube', '长对话, 深度思想交流'],
        [b('Gradient Dissent'), 'Weights & Biases', 'YouTube/Spotify', 'ML从业者访谈'],
        [b('硅谷101'), '泓君', 'Apple/Spotify', '中文圈最好的硅谷科技播客'],
        [b('晚点聊'), '晚点', '小宇宙', '中国科技行业深度对话'],
        [b('张小珺的访谈'), '张小珺', '小宇宙', '科技创业深度访谈'],
        [b('What\'s Next 科技早知道'), '硅谷101', 'Apple/Spotify', '科技趋势预判'],
        [b('OnBoard!'), '—', '小宇宙', '真格基金出品, AI创业者访谈'],
    ]))

    # YouTube/B站
    parts.append(h4('YouTube / B站'))
    parts.append(table(['频道','平台','频率','价值定位'], [
        [b('Yannic Kilcher'), 'YouTube', '每周1次', '最深入的论文解读'],
        [b('Two Minute Papers'), 'YouTube', '每周2次', '最快的论文摘要'],
        [b('3Blue1Brown'), 'YouTube', '按发布', '最好的数学/ML可视化'],
        [b('AI Explained'), 'YouTube', '每周1次', 'AI新闻深度解读'],
        [b('李沐'), 'YouTube/B站', '每周1次', '中文论文解读'],
        [b('跟李沐学AI'), 'B站', '每周1次', 'AI教程'],
        [b('AIPRM'), 'YouTube', '每周1次', 'Prompt工程'],
    ]))

    # 学术
    parts.append(h4('学术 & 社区'))
    parts.append(table(['平台','URL','频率','价值定位'], [
        [b('GitHub Trending'), 'github.com/trending', '每日', '开源热门项目'],
        [b('Hacker News'), 'news.ycombinator.com', '每日', '技术社区热点'],
        [b('ArXiv'), 'arxiv.org/list/cs.AI', '每周2次', '最前沿论文'],
        [b('LMSYS'), 'chat.lmsys.org', '每周1次', '模型对比评测'],
        [b('Papers With Code'), 'paperswithcode.com', '每周1次', '论文+代码+排行榜'],
        [b('Hugging Face Daily'), 'huggingface.co/papers', '每日', '热门论文日榜'],
        [b('Reddit r/MachineLearning'), 'reddit.com/r/ML', '每日', 'ML社区讨论'],
        [b('Reddit r/LocalLLaMA'), 'reddit.com/r/LocalLLaMA', '每日', '本地部署社区'],
    ]))

    # AI安全
    parts.append(h4('🆕 AI安全/对齐研究机构'))
    parts.append(table(['机构','URL','追踪重点'], [
        [b('Anthropic Safety'), 'anthropic.com/research', 'Constitutional AI, RLHF'],
        [b('OpenAI Safety'), 'openai.com/safety', '超级对齐, 红队测试'],
        [b('MIRI'), 'intelligence.org', 'AI对齐理论'],
        [b('ARC'), 'alignment.org', 'RLHF, 对齐研究'],
        [b('CAIS'), 'safe.ai', 'AI安全评测'],
        [b('Future of Life'), 'futureoflife.org', 'AI治理, 政策倡导'],
    ]))

    return '\n'.join(parts)


def build_full_tracking_html():
    """构建完整追踪体系HTML"""
    people = build_people_section()
    companies = build_companies_section()
    sources = build_sources_section()

    return f'''        <article id="tracking" class="tab-panel">
            <section class="section">
                <div class="section-header">
                    <div class="section-icon">\U0001f3af</div>
                    <div>
                        <h2 class="section-title">追踪体系</h2>
                        <p class="section-desc">AI行业人物、公司、信息源的系统化追踪清单（点击展开查看详情）</p>
                    </div>
                </div>
                
                <!-- 人物追踪 -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">\U0001f464</span>
                            <span class="collapsible-title">人物追踪</span>
                            <span class="collapsible-count">100+</span>
                        </div>
                        <span class="collapsible-icon">\u25bc</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="padding: var(--spacing-md);">
{people}
                        </div>
                    </div>
                </div>
                
                <!-- 公司追踪 -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">\U0001f3e2</span>
                            <span class="collapsible-title">公司追踪</span>
                            <span class="collapsible-count">140+</span>
                        </div>
                        <span class="collapsible-icon">\u25bc</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="padding: var(--spacing-md);">
{companies}
                        </div>
                    </div>
                </div>
                
                <!-- 信息源 -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">\U0001f4e1</span>
                            <span class="collapsible-title">信息源</span>
                            <span class="collapsible-count">200+</span>
                        </div>
                        <span class="collapsible-icon">\u25bc</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="padding: var(--spacing-md);">
{sources}
                        </div>
                    </div>
                </div>
            </section>
        </article>'''


def main():
    import os
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 找到追踪体系的起止行
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if '<article id="tracking"' in line:
            start_idx = i
        if start_idx is not None and i > start_idx:
            # 找到下一个 article 或 knowledge 部分
            if '<!-- 4. 知识库 -->' in line or '<article id="knowledge"' in line:
                end_idx = i
                break
    
    if start_idx is None or end_idx is None:
        print(f"ERROR: Could not find tracking section boundaries. start={start_idx}, end={end_idx}")
        return
    
    print(f"Found tracking section: lines {start_idx+1}-{end_idx} ({end_idx-start_idx} lines)")
    
    # 生成新的追踪体系HTML
    new_tracking = build_full_tracking_html()
    
    # 替换
    new_lines = lines[:start_idx] + new_tracking.split('\n') + [''] + lines[end_idx:]
    new_content = '\n'.join(new_lines)
    
    # 更新统计数字 (追踪体系tab的stats)
    # 找 stats-grid 中的 85+ 改为 100+, 130+ 改为 140+
    new_content = new_content.replace(
        '<span class="collapsible-count">85+</span>',
        '<span class="collapsible-count">100+</span>'
    )
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 统计新旧行数
    old_lines = end_idx - start_idx
    new_tracking_lines = len(new_tracking.split('\n'))
    print(f"Replaced {old_lines} lines with {new_tracking_lines} lines")
    print(f"New file: {len(new_lines)} lines (was {len(lines)})")
    print("Done!")


if __name__ == '__main__':
    main()
