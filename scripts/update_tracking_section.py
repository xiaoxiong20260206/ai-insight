#!/usr/bin/env python3
"""
更新 index.html 中的追踪体系 section，全量呈现 MD 文件中的数据。
包括：人物100+、公司140+、信息源200+（含微信公众号50+）
"""
import re

def build_tracking_html():
    """构建完整的追踪体系 HTML"""
    return '''        <article id="tracking" class="tab-panel">
            <section class="section">
                <div class="section-header">
                    <div class="section-icon">🎯</div>
                    <div>
                        <h2 class="section-title">追踪体系</h2>
                        <p class="section-desc">AI行业人物、公司、信息源的系统化追踪清单（点击展开查看详情）</p>
                    </div>
                </div>
                
                <!-- ========== 人物追踪 ========== -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">👤</span>
                            <span class="collapsible-title">人物追踪</span>
                            <span class="collapsible-count">100+</span>
                        </div>
                        <span class="collapsible-icon">▼</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="padding: var(--spacing-md);">
                            <!-- L1 实践者/构建者 -->
                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin-bottom: var(--spacing-md);">L1 实践者/构建者 — AI实验室核心</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Jason Wei</strong></td><td>OpenAI Research Lead</td><td>X, Papers</td><td>Chain-of-thought, 模型能力研究</td></tr>
                                        <tr><td><strong>Mark Chen</strong></td><td>OpenAI VP of Research</td><td>X, 采访</td><td>GPT/o-系列路线图, 代码生成</td></tr>
                                        <tr><td><strong>Noam Brown</strong></td><td>OpenAI Research (推理)</td><td>X, Papers</td><td>o1/o3 推理模型方法论</td></tr>
                                        <tr><td><strong>Barry Zhang</strong></td><td>Anthropic Head of Applied AI</td><td>X @barry_zyj</td><td>Agent设计原则, Skills范式</td></tr>
                                        <tr><td><strong>Amanda Askell</strong></td><td>Anthropic Alignment/Prompt</td><td>X @amandaaskell</td><td>Claude System Prompt设计者</td></tr>
                                        <tr><td><strong>Alex Albert</strong></td><td>Anthropic Claude Relations</td><td>X @alexalbert__</td><td>Claude使用技巧, 功能更新</td></tr>
                                        <tr><td><strong>Jan Leike</strong></td><td>Anthropic Alignment Lead</td><td>X, Papers</td><td>超级对齐, 安全研究</td></tr>
                                        <tr><td><strong>Ilya Sutskever</strong></td><td>SSI 联合创始人</td><td>采访, 演讲</td><td>超级智能安全, 技术路线</td></tr>
                                        <tr><td><strong>Jeff Dean</strong></td><td>Google Chief Scientist</td><td>X, 演讲</td><td>AI系统架构方向</td></tr>
                                        <tr><td><strong>Yann LeCun</strong></td><td>Meta AI 首席科学家</td><td>X @ylecun</td><td>技术路线争鸣, 开源策略</td></tr>
                                        <tr><td><strong>Igor Babuschkin</strong></td><td>xAI 联合创始人</td><td>X, 采访</td><td>Grok技术架构</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L1 实践者 — AI Coding 产品 & 实践者</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Michael Truell</strong></td><td>Cursor CEO</td><td>采访, Podcast</td><td>Cursor产品愿景</td></tr>
                                        <tr><td><strong>Aman Sanger</strong></td><td>Cursor CTO</td><td>X, 技术演讲</td><td>技术架构, Agent模式</td></tr>
                                        <tr><td><strong>Amjad Masad</strong></td><td>Replit CEO</td><td>X, 博客</td><td>AI Agent编程</td></tr>
                                        <tr><td><strong>Scott Wu</strong></td><td>Cognition (Devin) CEO</td><td>X, 博客</td><td>自主编程Agent</td></tr>
                                        <tr><td><strong>Addy Osmani</strong></td><td>Google Chrome 工程总监</td><td>addyosmani.com</td><td>LLM Coding Workflow</td></tr>
                                        <tr><td><strong>Kent Beck</strong></td><td>极限编程之父</td><td>X, Pragmatic Engineer</td><td>TDD + AI Agent方法论</td></tr>
                                        <tr><td><strong>Steve Yegge</strong></td><td>Sourcegraph</td><td>sourcegraph.com</td><td>AI对开发者影响</td></tr>
                                        <tr><td><strong>Unclecode</strong></td><td>Crawl4AI创始人</td><td>X, GitHub</td><td>LLM友好网页爬取</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L1 实践者 — 大模型核心研究者 & 具身智能</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Andrej Karpathy</strong></td><td>独立 (前OpenAI/Tesla)</td><td>YouTube, X</td><td>最通俗的技术深度解读</td></tr>
                                        <tr><td><strong>Jim Fan</strong></td><td>NVIDIA 机器人总监</td><td>X @DrJimFan</td><td>Physical AI, 具身智能</td></tr>
                                        <tr><td><strong>Tri Dao</strong></td><td>Together AI</td><td>X, Papers</td><td>FlashAttention, 推理效率</td></tr>
                                        <tr><td><strong>François Chollet</strong></td><td>ARC-AGI 创始人</td><td>X @fchollet</td><td>AGI评测, 批判性思考</td></tr>
                                        <tr><td><strong>姚顺雨</strong></td><td>OpenAI 研究员</td><td>播客, 演讲</td><td>Agent理论, 语言世界</td></tr>
                                        <tr><td><strong>Harrison Chase</strong></td><td>LangChain CEO</td><td>YouTube, 演讲</td><td>Agent工程, Deep Agents</td></tr>
                                        <tr><td><strong>Chris Lattner</strong></td><td>Modular/Mojo 创始人</td><td>X, 博客</td><td>AI编程语言, 编译器</td></tr>
                                        <tr><td><strong>Pieter Abbeel</strong></td><td>Covariant/UC Berkeley</td><td>X, Papers</td><td>机器人学习, 强化学习</td></tr>
                                        <tr><td><strong>Chelsea Finn</strong></td><td>Stanford</td><td>Papers, 演讲</td><td>元学习, 机器人AI</td></tr>
                                        <tr><td><strong>Fei-Fei Li</strong></td><td>Stanford HAI, World Labs</td><td>X, 演讲</td><td>计算机视觉, 空间智能</td></tr>
                                        <tr><td><strong>王兴兴</strong></td><td>宇树科技创始人</td><td>采访, 产品发布</td><td>四足/人形机器人</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L1 实践者 — 企业AI/Agent & 学术界</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Bret Taylor</strong></td><td>Sierra CEO (前Salesforce)</td><td>采访, 演讲</td><td>企业AI Agent, 客服AI</td></tr>
                                        <tr><td><strong>Arvind Jain</strong></td><td>Glean CEO</td><td>采访</td><td>企业知识搜索</td></tr>
                                        <tr><td><strong>Winston Weinberg</strong></td><td>Harvey CEO</td><td>采访</td><td>法律AI</td></tr>
                                        <tr><td><strong>Percy Liang</strong></td><td>Stanford HAI, HELM</td><td>Papers, 演讲</td><td>模型评测, 基准测试</td></tr>
                                        <tr><td><strong>Sasha Rush</strong></td><td>Cornell/HuggingFace</td><td>X, Papers</td><td>Transformer架构, 高效推理</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L1 实践者 — 中国AI核心人物</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>梁文锋</strong></td><td>DeepSeek 创始人</td><td>采访</td><td>开源大模型, MoE架构</td></tr>
                                        <tr><td><strong>杨植麟</strong></td><td>Moonshot AI / Kimi 创始人</td><td>采访, 演讲</td><td>长上下文, 消费级AI</td></tr>
                                        <tr><td><strong>唐杰</strong></td><td>智谱AI 首席科学家</td><td>论文, 演讲</td><td>GLM系列, Agent</td></tr>
                                        <tr><td><strong>王小川</strong></td><td>百川智能 CEO</td><td>X, 公众号</td><td>搜索增强, 企业AI</td></tr>
                                        <tr><td><strong>李彦宏</strong></td><td>百度 CEO</td><td>演讲, 采访</td><td>国内AI战略</td></tr>
                                        <tr><td><strong>朱松纯</strong></td><td>北大, 通用人工智能研究院</td><td>论文, 演讲</td><td>通用人工智能, 认知科学</td></tr>
                                        <tr><td><strong>刘知远</strong></td><td>清华大学, OpenBMB</td><td>Papers, GitHub</td><td>大模型高效微调, 开源</td></tr>
                                        <tr><td><strong>贾扬清</strong></td><td>阿里云AI (Caffe作者)</td><td>X, 采访</td><td>AI基础设施, 云原生AI</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">🆕 L1 实践者 — 中国AI Coding & 新晋力量</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>陈鑫</strong></td><td>阿里云 通义灵码负责人</td><td>演讲, 采访</td><td>国内AI Coding标杆产品</td></tr>
                                        <tr><td><strong>郗杰</strong></td><td>字节跳动 Trae团队</td><td>演讲, 技术博客</td><td>国内AI IDE先驱, 对标Cursor</td></tr>
                                        <tr><td><strong>张俊林</strong></td><td>字节跳动 MarsCode</td><td>演讲, 采访</td><td>云端AI编程, 零配置开发环境</td></tr>
                                        <tr><td><strong>张建锋</strong></td><td>蚂蚁集团 CodeFuse</td><td>GitHub, 演讲</td><td>开源AI编程框架</td></tr>
                                        <tr><td><strong>李大海</strong></td><td>面壁智能 CEO</td><td>采访, 演讲</td><td>端侧高效模型, MiniCPM系列</td></tr>
                                        <tr><td><strong>方汉</strong></td><td>昆仑万维 CEO</td><td>采访, 演讲</td><td>AI搜索, 天工大模型</td></tr>
                                        <tr><td><strong>王晓云</strong></td><td>蚂蚁集团 CTO</td><td>采访, 演讲</td><td>蚂蚁百灵大模型, 金融AI</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L1 实践者 — AI安全/对齐核心人物</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Stuart Russell</strong></td><td>UC Berkeley</td><td>书籍, 演讲</td><td>AI安全理论</td></tr>
                                        <tr><td><strong>Nick Bostrom</strong></td><td>牛津FHI</td><td>书籍, 论文</td><td>超级智能风险</td></tr>
                                        <tr><td><strong>Paul Christiano</strong></td><td>ARC (前OpenAI)</td><td>博客, 论文</td><td>对齐研究, RLHF</td></tr>
                                        <tr><td><strong>Dan Hendrycks</strong></td><td>CAIS</td><td>Papers, X</td><td>AI安全评测</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- L2 深度观察者 -->
                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L2 深度观察者 — Newsletter/博客 & AI工程实践</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物/媒体</th><th>平台</th><th>检查频率</th><th>价值定位</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Simon Willison</strong></td><td>simonwillison.net</td><td>每日</td><td>最及时的AI工具评测</td></tr>
                                        <tr><td><strong>Gergely Orosz</strong></td><td>Pragmatic Engineer</td><td>每周2次</td><td>最深入的工程视角</td></tr>
                                        <tr><td><strong>Swyx</strong></td><td>Latent Space</td><td>每周1次</td><td>AI工程前沿, 深度访谈</td></tr>
                                        <tr><td><strong>Ethan Mollick</strong></td><td>oneusefulthing.org</td><td>每周2次</td><td>AI对工作方式的影响</td></tr>
                                        <tr><td><strong>Jack Clark</strong></td><td>Import AI</td><td>每周1次</td><td>AI政策与产业宏观视角</td></tr>
                                        <tr><td><strong>Andrew Ng</strong></td><td>deeplearning.ai/the-batch</td><td>每周1次</td><td>AI教育与产业洞察</td></tr>
                                        <tr><td><strong>Eugene Yan</strong></td><td>eugeneyan.com</td><td>每周1次</td><td>AI工程最佳实践, LLM应用</td></tr>
                                        <tr><td><strong>Chip Huyen</strong></td><td>huyenchip.com</td><td>每周1次</td><td>MLOps, LLM系统设计</td></tr>
                                        <tr><td><strong>Jason Liu</strong></td><td>X @jxnlco</td><td>每周1次</td><td>结构化输出, LLM工程</td></tr>
                                        <tr><td><strong>Thomas Wolf</strong></td><td>Hugging Face CTO</td><td>每周1次</td><td>开源LLM生态</td></tr>
                                        <tr><td><strong>Nathan Benaich</strong></td><td>stateof.ai</td><td>每年</td><td>State of AI年度报告</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L2 深度观察者 — 中文圈 & YouTube/播客</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物/媒体</th><th>平台</th><th>检查频率</th><th>价值定位</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>宝玉</strong></td><td>X @dotey, 微信公众号</td><td>每日</td><td>最快的海外AI信息翻译</td></tr>
                                        <tr><td><strong>李沐</strong></td><td>YouTube/B站</td><td>每周1次</td><td>中文世界最好的论文解读</td></tr>
                                        <tr><td><strong>潘乱</strong></td><td>乱翻书 (微信公众号)</td><td>每周1次</td><td>中国互联网行业深度分析</td></tr>
                                        <tr><td><strong>海外独角兽</strong></td><td>微信公众号</td><td>每周1次</td><td>硅谷创投深度报道</td></tr>
                                        <tr><td><strong>Yannic Kilcher</strong></td><td>YouTube</td><td>每周1次</td><td>最深入的论文解读</td></tr>
                                        <tr><td><strong>Two Minute Papers</strong></td><td>YouTube</td><td>每周2次</td><td>最快的论文摘要</td></tr>
                                        <tr><td><strong>Lex Fridman</strong></td><td>YouTube</td><td>按嘉宾</td><td>长对话, 深度思想交流</td></tr>
                                        <tr><td><strong>泓君</strong></td><td>硅谷101 (播客)</td><td>每周</td><td>中文圈最好的硅谷科技播客</td></tr>
                                        <tr><td><strong>张小珺</strong></td><td>小宇宙 (播客)</td><td>每周</td><td>中国科技创业深度访谈</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- L3 战略决策者 -->
                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">L3 战略决策者</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>人物</th><th>公司/角色</th><th>主要渠道</th><th>信号权重</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>Sam Altman</strong></td><td>OpenAI CEO</td><td>Blog, X</td><td>GPT路线图</td></tr>
                                        <tr><td><strong>Dario Amodei</strong></td><td>Anthropic CEO</td><td>长文Essays</td><td>Claude战略方向</td></tr>
                                        <tr><td><strong>Jensen Huang</strong></td><td>NVIDIA CEO</td><td>GTC演讲</td><td>AI基础设施方向</td></tr>
                                        <tr><td><strong>Sundar Pichai</strong></td><td>Google CEO</td><td>采访, GTC</td><td>Google AI战略</td></tr>
                                        <tr><td><strong>Satya Nadella</strong></td><td>Microsoft CEO</td><td>采访, LinkedIn</td><td>Copilot战略</td></tr>
                                        <tr><td><strong>Mark Zuckerberg</strong></td><td>Meta CEO</td><td>公开信, 采访</td><td>开源AI策略</td></tr>
                                        <tr><td><strong>Marc Benioff</strong></td><td>Salesforce CEO</td><td>X, 采访</td><td>企业AI Agent</td></tr>
                                        <tr><td><strong>Arvind Krishna</strong></td><td>IBM CEO</td><td>采访, 财报会</td><td>企业AI转型</td></tr>
                                        <tr><td><strong>Thomas Kurian</strong></td><td>Google Cloud CEO</td><td>采访</td><td>云AI战略</td></tr>
                                        <tr><td><strong>Andy Jassy</strong></td><td>Amazon CEO</td><td>股东信, 采访</td><td>AWS AI战略</td></tr>
                                        <tr><td><strong>Guillermo Rauch</strong></td><td>Vercel CEO</td><td>X, Blog</td><td>AI前端 / v0.dev</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ========== 公司追踪 ========== -->
                <div class="category-section">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <div class="collapsible-left">
                            <span class="collapsible-emoji">🏢</span>
                            <span class="collapsible-title">公司追踪</span>
                            <span class="collapsible-count">140+</span>
                        </div>
                        <span class="collapsible-icon">▼</span>
                    </div>
                    <div class="collapsible-content">
                        <div style="padding: var(--spacing-md);">
                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin-bottom: var(--spacing-md);">模型实验室 — 海外头部</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>公司</th><th>核心产品</th><th>检查频率</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>OpenAI</strong></td><td>GPT-4/o系列, ChatGPT, Codex</td><td>每日</td><td>最强闭源模型, 推理能力</td></tr>
                                        <tr><td><strong>Anthropic</strong></td><td>Claude系列, Claude Code</td><td>每日</td><td>安全对齐, Agent设计</td></tr>
                                        <tr><td><strong>Google DeepMind</strong></td><td>Gemini系列, AlphaFold</td><td>每周2次</td><td>多模态, 推理, 科学AI</td></tr>
                                        <tr><td><strong>Meta AI (FAIR)</strong></td><td>Llama系列</td><td>每周2次</td><td>开源模型标杆</td></tr>
                                        <tr><td><strong>SSI</strong></td><td>(研发中)</td><td>每周1次</td><td>Ilya领衔, 超级智能安全</td></tr>
                                        <tr><td><strong>Mistral AI</strong></td><td>Mistral系列</td><td>每周1次</td><td>欧洲开源模型</td></tr>
                                        <tr><td><strong>xAI</strong></td><td>Grok系列</td><td>每周1次</td><td>Musk系, X平台整合</td></tr>
                                        <tr><td><strong>Cohere</strong></td><td>Command系列</td><td>每周1次</td><td>企业RAG, 嵌入模型</td></tr>
                                    </tbody>
                                </table>
                            </div>

                            <h4 style="font-size: 14px; color: var(--color-text-secondary); margin: var(--spacing-lg) 0 var(--spacing-md);">模型实验室 — 中国</h4>
                            <div class="table-wrap" style="overflow-x: auto;">
                                <table class="tracking-table">
                                    <thead><tr><th>公司</th><th>核心产品</th><th>检查频率</th><th>追踪重点</th></tr></thead>
                                    <tbody>
                                        <tr><td><strong>DeepSeek</strong></td><td>DeepSeek V3/R1</td><td>每日</td><td>开源标杆, MoE架构</td></tr>
                                        <tr><td><strong>智谱AI</strong></td><td>GLM系列</td><td>每周2次</td><td>GLM开源, Agent平台</td></tr>
                                        <tr><td><strong>Moonshot AI</strong></td><td>Kimi</td><td>每周2次</td><td>长上下文, 消费级AI</td></tr>
                                        <tr><td><strong>百川智能</strong></td><td>Baichuan系列</td><td>每周1次</td><td>搜索增强, 企业AI</td></tr>
                                        <tr><td><st