// ===== 任务数据 =====
const taskData = {
    research: {
        name: '投研场景',
        id: 'scene-research',
        timePercent: 60,
        subcategories: {
            '量化策略研发': {
                id: 'subcat-quant-dev',
                timePercent: 18,
                tasks: [
                    {
                        id: 'task-strategy-coding',
                        name: '策略编写',
                        timePercent: 8,
                        agent: 'Quant',
                        tech: 'LLM+量化框架',
                        products: ['聚宽', 'QuantConnect', '米筐', 'Alpaca'],
                        example: '编写均线交叉、动量等量化策略代码'
                    },
                    {
                        id: 'task-factor-compute',
                        name: '因子计算',
                        timePercent: 5,
                        agent: 'Quant',
                        tech: 'LLM+数据处理',
                        products: ['Wind', 'QuantConnect', '优矿'],
                        example: '计算Alpha因子、风险因子等'
                    },
                    {
                        id: 'task-backtest',
                        name: '回测分析',
                        timePercent: 5,
                        agent: 'Quant',
                        tech: '量化引擎',
                        products: ['聚宽', '米筐', 'Zipline'],
                        example: '历史数据回测、策略性能评估'
                    }
                ]
            },
            '投资研究': {
                id: 'subcat-invest-research',
                timePercent: 15,
                tasks: [
                    {
                        id: 'task-industry-research',
                        name: '行业研究',
                        timePercent: 6,
                        agent: 'Research',
                        tech: 'LLM+搜索',
                        products: ['Wind', 'Capital IQ', '萝卜投研', 'Perplexity'],
                        example: '行业趋势分析、产业链研究'
                    },
                    {
                        id: 'task-company-analysis',
                        name: '公司分析',
                        timePercent: 5,
                        agent: 'Research',
                        tech: 'LLM+数据分析',
                        products: ['Bloomberg', 'FactSet', '慧博投研'],
                        example: '财务分析、估值模型、竞争格局'
                    },
                    {
                        id: 'task-report-writing',
                        name: '研报撰写',
                        timePercent: 4,
                        agent: 'Research',
                        tech: 'LLM',
                        products: ['ChatGPT', 'Claude', 'Kimi', '通义千问'],
                        example: '投资建议、研究报告撰写'
                    }
                ]
            },
            '数据获取与清洗': {
                id: 'subcat-data-process',
                timePercent: 10,
                tasks: [
                    {
                        id: 'task-data-fetch',
                        name: '数据获取',
                        timePercent: 4,
                        agent: 'Data',
                        tech: 'API+爬虫',
                        products: ['Wind', 'Tushare', 'AKShare', 'Yahoo Finance'],
                        example: '行情数据、财务数据、另类数据获取'
                    },
                    {
                        id: 'task-data-clean',
                        name: '数据清洗',
                        timePercent: 3,
                        agent: 'Data',
                        tech: 'LLM+Python',
                        products: ['ChatGPT', 'Claude', 'Pandas'],
                        example: '缺失值处理、异常值检测、数据标准化'
                    },
                    {
                        id: 'task-data-viz',
                        name: '数据可视化',
                        timePercent: 3,
                        agent: 'Data',
                        tech: '可视化工具',
                        products: ['Tableau', 'Power BI', '帆软FineReport'],
                        example: '图表绘制、Dashboard制作'
                    }
                ]
            },
            '市场分析': {
                id: 'subcat-market-analysis',
                timePercent: 8,
                tasks: [
                    {
                        id: 'task-macro-analysis',
                        name: '宏观分析',
                        timePercent: 3,
                        agent: 'Research',
                        tech: 'LLM+数据',
                        products: ['Bloomberg', 'Wind', 'Perplexity'],
                        example: '宏观经济指标分析、货币政策解读'
                    },
                    {
                        id: 'task-sentiment-analysis',
                        name: '舆情分析',
                        timePercent: 3,
                        agent: 'Browser',
                        tech: 'NLP+爬虫',
                        products: ['同花顺', '东方财富', '雪球'],
                        example: '市场情绪监控、新闻事件追踪'
                    },
                    {
                        id: 'task-technical-analysis',
                        name: '技术分析',
                        timePercent: 2,
                        agent: 'Quant',
                        tech: '量化指标',
                        products: ['TradingView', '同花顺', 'Wind'],
                        example: '技术指标计算、形态识别'
                    }
                ]
            },
            '组合管理': {
                id: 'subcat-portfolio',
                timePercent: 5,
                tasks: [
                    {
                        id: 'task-portfolio-optimize',
                        name: '组合优化',
                        timePercent: 2,
                        agent: 'Quant',
                        tech: '优化算法',
                        products: ['MSCI Barra', 'Bloomberg PORT', 'Wind'],
                        example: 'Markowitz优化、风险平价配置'
                    },
                    {
                        id: 'task-rebalance',
                        name: '再平衡',
                        timePercent: 2,
                        agent: 'Trading',
                        tech: '交易算法',
                        products: ['恒生电子', 'Interactive Brokers'],
                        example: '定期调仓、动态对冲'
                    },
                    {
                        id: 'task-performance-attr',
                        name: '业绩归因',
                        timePercent: 1,
                        agent: 'Data',
                        tech: '归因模型',
                        products: ['Barra', 'FactSet', 'Wind'],
                        example: 'Brinson归因、风险归因'
                    }
                ]
            },
            '交易执行': {
                id: 'subcat-trading',
                timePercent: 4,
                tasks: [
                    {
                        id: 'task-order-exec',
                        name: '订单执行',
                        timePercent: 2,
                        agent: 'Trading',
                        tech: '交易系统',
                        products: ['恒生电子', 'Interactive Brokers', 'Alpaca'],
                        example: '算法交易、智能路由'
                    },
                    {
                        id: 'task-exec-analysis',
                        name: '执行分析',
                        timePercent: 2,
                        agent: 'Trading',
                        tech: 'TCA分析',
                        products: ['Bloomberg TCA', 'ITG', 'Wind'],
                        example: '滑点分析、成本归因'
                    }
                ]
            }
        }
    },
    operation: {
        name: '运营合规场景',
        id: 'scene-operation',
        timePercent: 40,
        subcategories: {
            '风险控制': {
                id: 'subcat-risk',
                timePercent: 12,
                tasks: [
                    {
                        id: 'task-risk-monitor',
                        name: '风险监控',
                        timePercent: 4,
                        agent: 'Risk',
                        tech: '风控系统',
                        products: ['MSCI RiskMetrics', 'Wind', '恒生风控'],
                        example: 'VaR计算、止损预警、敞口监控'
                    },
                    {
                        id: 'task-stress-test',
                        name: '压力测试',
                        timePercent: 3,
                        agent: 'Risk',
                        tech: '情景分析',
                        products: ["Moody's Analytics", 'Bloomberg', 'Wind'],
                        example: '极端情景模拟、压力测试报告'
                    },
                    {
                        id: 'task-credit-analysis',
                        name: '信用分析',
                        timePercent: 3,
                        agent: 'Risk',
                        tech: '评级模型',
                        products: ['中诚信', '联合资信', "Moody's"],
                        example: '信用评级、违约概率预测'
                    },
                    {
                        id: 'task-limit-manage',
                        name: '限额管理',
                        timePercent: 2,
                        agent: 'Risk',
                        tech: '风控规则',
                        products: ['恒生电子', 'Wind'],
                        example: '持仓限额、交易限制管理'
                    }
                ]
            },
            '合规审查': {
                id: 'subcat-compliance',
                timePercent: 6,
                tasks: [
                    {
                        id: 'task-compliance-check',
                        name: '合规检查',
                        timePercent: 3,
                        agent: 'Risk',
                        tech: '规则引擎',
                        products: ['恒生电子', 'Wind'],
                        example: '交易合规、持仓合规检查'
                    },
                    {
                        id: 'task-regulatory-report',
                        name: '监管报送',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: '报表系统',
                        products: ['恒生电子', '金证股份'],
                        example: '监管报表生成、自动报送'
                    },
                    {
                        id: 'task-policy-update',
                        name: '法规更新',
                        timePercent: 1,
                        agent: 'Browser',
                        tech: '信息采集',
                        products: ['Perplexity', '北大法宝', 'Kimi'],
                        example: '监管政策追踪、法规解读'
                    }
                ]
            },
            '报告撰写': {
                id: 'subcat-reporting',
                timePercent: 6,
                tasks: [
                    {
                        id: 'task-periodic-report',
                        name: '定期报告',
                        timePercent: 3,
                        agent: 'Chatbot',
                        tech: 'LLM',
                        products: ['ChatGPT', 'Claude', 'Kimi', 'WPS AI'],
                        example: '周报、月报、季报撰写'
                    },
                    {
                        id: 'task-invest-proposal',
                        name: '投资建议书',
                        timePercent: 2,
                        agent: 'Research',
                        tech: 'LLM+模板',
                        products: ['ChatGPT', 'Notion AI', '飞书文档'],
                        example: '投资方案、尽调报告'
                    },
                    {
                        id: 'task-presentation',
                        name: 'PPT制作',
                        timePercent: 1,
                        agent: 'Chatbot',
                        tech: 'LLM+设计',
                        products: ['Gamma', 'Beautiful.ai', 'WPS AI'],
                        example: '路演材料、投资汇报'
                    }
                ]
            },
            '客户沟通': {
                id: 'subcat-client',
                timePercent: 5,
                tasks: [
                    {
                        id: 'task-client-qa',
                        name: '客户答疑',
                        timePercent: 2,
                        agent: 'Chatbot',
                        tech: 'LLM',
                        products: ['ChatGPT', 'Kimi', '通义千问'],
                        example: '产品咨询、净值查询'
                    },
                    {
                        id: 'task-client-report',
                        name: '客户报告',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: '报表自动化',
                        products: ['帆软FineReport', 'Wind'],
                        example: '客户专属报告生成'
                    },
                    {
                        id: 'task-email-handle',
                        name: '邮件处理',
                        timePercent: 1,
                        agent: 'Workflow',
                        tech: 'LLM+邮件',
                        products: ['ChatGPT', 'Grammarly', '飞书'],
                        example: '邮件起草、回复建议'
                    }
                ]
            },
            '知识管理': {
                id: 'subcat-knowledge',
                timePercent: 4,
                tasks: [
                    {
                        id: 'task-knowledge-qa',
                        name: '知识问答',
                        timePercent: 2,
                        agent: 'Chatbot',
                        tech: 'RAG',
                        products: ['Kimi', 'ChatGPT', 'Perplexity'],
                        example: '内部知识库查询、历史研报检索'
                    },
                    {
                        id: 'task-doc-manage',
                        name: '文档管理',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: '知识库',
                        products: ['Notion', '飞书文档', 'Confluence'],
                        example: '研报归档、知识沉淀'
                    }
                ]
            },
            '会议效率': {
                id: 'subcat-meeting',
                timePercent: 3,
                tasks: [
                    {
                        id: 'task-meeting-minutes',
                        name: '会议纪要',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: 'ASR+LLM',
                        products: ['飞书妙记', 'Otter.ai', '讯飞听见'],
                        example: '投委会、路演会议记录'
                    },
                    {
                        id: 'task-meeting-schedule',
                        name: '日程管理',
                        timePercent: 1,
                        agent: 'Background',
                        tech: '日程系统',
                        products: ['飞书', 'Outlook', 'Calendly'],
                        example: '会议安排、日程提醒'
                    }
                ]
            },
            '数据报表': {
                id: 'subcat-data-report',
                timePercent: 2,
                tasks: [
                    {
                        id: 'task-auto-report',
                        name: '自动化报表',
                        timePercent: 1,
                        agent: 'Background',
                        tech: '定时任务',
                        products: ['帆软FineReport', 'Wind', 'Python'],
                        example: '日报、周报自动生成'
                    },
                    {
                        id: 'task-data-export',
                        name: '数据导出',
                        timePercent: 1,
                        agent: 'Data',
                        tech: '数据接口',
                        products: ['Wind', 'Bloomberg', 'Excel'],
                        example: '数据提取、格式转换'
                    }
                ]
            },
            '学习培训': {
                id: 'subcat-learning',
                timePercent: 2,
                tasks: [
                    {
                        id: 'task-skill-learning',
                        name: '技能学习',
                        timePercent: 1,
                        agent: 'Chatbot',
                        tech: 'LLM',
                        products: ['ChatGPT', 'Perplexity', 'Coursera'],
                        example: 'AI助手平台A学习、Python编程'
                    },
                    {
                        id: 'task-market-learning',
                        name: '市场学习',
                        timePercent: 1,
                        agent: 'Browser',
                        tech: '信息聚合',
                        products: ['雪球', '华尔街见闻', 'Bloomberg'],
                        example: '市场动态、投资理念学习'
                    }
                ]
            },
            '市场营销': {
                id: 'subcat-marketing',
                timePercent: 6,
                tasks: [
                    {
                        id: 'task-direct-sales',
                        name: '直销获客',
                        timePercent: 2,
                        agent: 'Chatbot',
                        tech: 'LLM+CRM',
                        products: ['Salesforce', '企业微信', '飞书'],
                        example: '高净值客户开发、投资者路演、产品推介'
                    },
                    {
                        id: 'task-channel-sales',
                        name: '代销渠道',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: 'CRM+报表',
                        products: ['Wind', '恒生电子', '帆软FineReport'],
                        example: '银行代销对接、券商渠道管理、FOF合作'
                    },
                    {
                        id: 'task-client-relationship',
                        name: '客户关系维护',
                        timePercent: 2,
                        agent: 'Chatbot',
                        tech: 'LLM+CRM',
                        products: ['ChatGPT', 'Kimi', '企业微信', '飞书'],
                        example: '定期回访、产品净值推送、投资观点分享'
                    }
                ]
            },
            '投资者服务': {
                id: 'subcat-investor-service',
                timePercent: 5,
                tasks: [
                    {
                        id: 'task-investor-report',
                        name: '投资者报告',
                        timePercent: 2,
                        agent: 'Research',
                        tech: 'LLM+模板',
                        products: ['ChatGPT', 'Claude', 'WPS AI', '帆软FineReport'],
                        example: '月度净值报告、业绩归因说明、投资策略解读'
                    },
                    {
                        id: 'task-investor-meeting',
                        name: '投资者会议',
                        timePercent: 2,
                        agent: 'Workflow',
                        tech: 'ASR+LLM',
                        products: ['飞书妙记', 'Otter.ai', '讯飞听见'],
                        example: '投资者大会筹备、路演材料准备、Q&A整理'
                    },
                    {
                        id: 'task-complaint-handle',
                        name: '投诉处理',
                        timePercent: 1,
                        agent: 'Chatbot',
                        tech: 'LLM+知识库',
                        products: ['Kimi', '通义千问', '企业微信'],
                        example: '客户投诉响应、问题跟踪、满意度回访'
                    }
                ]
            }
        }
    }
};

// ===== 用户角色数据 (私募量化公司) =====
const userData = {
    'quant-analyst': {
        id: 'user-quant-analyst',
        name: '量化研究员',
        icon: '📈',
        description: '量化策略研发、因子挖掘、回测分析',
        relatedSubcategories: ['subcat-quant-dev', 'subcat-data-process', 'subcat-market-analysis'],
        cssClass: 'user-quant'
    },
    'fund-manager': {
        id: 'user-fund-manager',
        name: '基金经理',
        icon: '💼',
        description: '策略组合管理、风险控制、交易执行',
        relatedSubcategories: ['subcat-invest-research', 'subcat-portfolio', 'subcat-trading', 'subcat-risk'],
        cssClass: 'user-fund'
    },
    'risk-officer': {
        id: 'user-risk-officer',
        name: '风控合规',
        icon: '⚠️',
        description: '风险监控、压力测试、合规检查',
        relatedSubcategories: ['subcat-risk', 'subcat-compliance'],
        cssClass: 'user-risk'
    },
    'strategy-developer': {
        id: 'user-strategy-developer',
        name: '策略开发',
        icon: '�️',
        description: '策略编写、模型开发、算法优化',
        relatedSubcategories: ['subcat-quant-dev', 'subcat-data-process'],
        cssClass: 'user-strategy'
    },
    'trader': {
        id: 'user-trader',
        name: '交易员',
        icon: '💹',
        description: '算法交易、订单执行、执行分析',
        relatedSubcategories: ['subcat-trading', 'subcat-quant-dev'],
        cssClass: 'user-trader'
    },
    'data-engineer': {
        id: 'user-data-engineer',
        name: '数据工程',
        icon: '�',
        description: '数据采集、数据清洗、因子库维护',
        relatedSubcategories: ['subcat-data-process', 'subcat-data-report'],
        cssClass: 'user-data'
    },
    'market-manager': {
        id: 'user-market-manager',
        name: '市场人员',
        icon: '🤝',
        description: '投资者关系、渠道对接、产品路演',
        relatedSubcategories: ['subcat-marketing', 'subcat-investor-service', 'subcat-client', 'subcat-reporting'],
        cssClass: 'user-market'
    },
    'operation-staff': {
        id: 'user-operation-staff',
        name: '运营支持',
        icon: '⚙️',
        description: '报告生成、流程管理、数据报表',
        relatedSubcategories: ['subcat-reporting', 'subcat-data-report', 'subcat-meeting', 'subcat-knowledge'],
        cssClass: 'user-operation'
    }
};

// ===== Agent数据 =====
const agentData = {
    'Quant': {
        id: 'agent-quant',
        name: 'Quant Agent',
        icon: '📈',
        coverage: 28,
        techs: ['LLM', '量化框架', '优化算法'],
        description: '量化策略开发、因子计算、回测分析',
        cssClass: 'quant'
    },
    'Research': {
        id: 'agent-research',
        name: 'Research Agent',
        icon: '🔬',
        coverage: 18,
        techs: ['LLM', '搜索', '知识图谱'],
        description: '行业研究、公司分析、深度报告',
        cssClass: 'research'
    },
    'Data': {
        id: 'agent-data',
        name: 'Data Agent',
        icon: '📊',
        coverage: 14,
        techs: ['数据处理', '可视化', 'ETL'],
        description: '数据获取、清洗、可视化',
        cssClass: 'data'
    },
    'Risk': {
        id: 'agent-risk',
        name: 'Risk Agent',
        icon: '⚠️',
        coverage: 12,
        techs: ['风控模型', '规则引擎'],
        description: '风险监控、压力测试、合规检查',
        cssClass: 'risk'
    },
    'Chatbot': {
        id: 'agent-chatbot',
        name: 'Chatbot Agent',
        icon: '💬',
        coverage: 11,
        techs: ['LLM', 'RAG'],
        description: '知识问答、文档写作、客户服务',
        cssClass: 'chatbot'
    },
    'Workflow': {
        id: 'agent-workflow',
        name: 'Workflow Agent',
        icon: '⚙️',
        coverage: 9,
        techs: ['RPA', 'LLM'],
        description: '流程自动化、报告审核',
        cssClass: 'workflow'
    },
    'Trading': {
        id: 'agent-trading',
        name: 'Trading Agent',
        icon: '💹',
        coverage: 5,
        techs: ['交易系统', '算法交易'],
        description: '订单执行、交易分析',
        cssClass: 'trading'
    },
    'Browser': {
        id: 'agent-browser',
        name: 'Browser Agent',
        icon: '🌐',
        coverage: 2,
        techs: ['爬虫', 'NLP'],
        description: '信息采集、舆情监控',
        cssClass: 'browser'
    },
    'Background': {
        id: 'agent-background',
        name: 'Background Agent',
        icon: '⏰',
        coverage: 1,
        techs: ['定时任务', '监控'],
        description: '自动化任务、定时报告',
        cssClass: 'background'
    }
};

// ===== 产品链接 =====
const productLinks = {
    // 量化平台
    '聚宽': 'https://www.joinquant.com',
    '米筐': 'https://www.ricequant.com',
    '优矿': 'https://uqer.datayes.com',
    '掘金量化': 'https://www.myquant.cn',
    'QuantConnect': 'https://www.quantconnect.com',
    'Alpaca': 'https://alpaca.markets',
    'Zipline': 'https://www.zipline.io',
    
    // 数据终端
    'Wind': 'https://www.wind.com.cn',
    '东方财富': 'https://www.eastmoney.com',
    '东方财富Choice': 'https://choice.eastmoney.com',
    '同花顺': 'https://www.10jqka.com.cn',
    '同花顺iFinD': 'https://www.51ifind.com',
    'Bloomberg': 'https://www.bloomberg.com/professional',
    'Bloomberg TCA': 'https://www.bloomberg.com/professional/product/transaction-cost-analysis',
    'Bloomberg PORT': 'https://www.bloomberg.com/professional/product/portfolio-analytics',
    'Reuters': 'https://www.refinitiv.com',
    'FactSet': 'https://www.factset.com',
    'Tushare': 'https://tushare.pro',
    'AKShare': 'https://akshare.xyz',
    'Yahoo Finance': 'https://finance.yahoo.com',
    'TradingView': 'https://www.tradingview.com',
    'ITG': 'https://www.intlgroup.com',
    
    // 研究工具
    '萝卜投研': 'https://robo.datayes.com',
    '慧博投研': 'https://www.hibor.com.cn',
    '朝阳永续': 'https://www.go-goal.com',
    'Capital IQ': 'https://www.capitaliq.com',
    'Sentieo': 'https://sentieo.com',
    
    // AI助手
    'ChatGPT': 'https://chat.openai.com',
    'Claude': 'https://claude.ai',
    'Perplexity': 'https://perplexity.ai',
    'Kimi': 'https://kimi.moonshot.cn',
    '通义千问': 'https://tongyi.aliyun.com/qianwen',
    '豆包': 'https://www.doubao.com',
    '讯飞星火': 'https://xinghuo.xfyun.cn',
    
    // 风控合规
    'MSCI RiskMetrics': 'https://www.msci.com/riskmetrics',
    'MSCI Barra': 'https://www.msci.com/barra',
    'Barra': 'https://www.msci.com/barra',
    "Moody's Analytics": 'https://www.moodysanalytics.com',
    "Moody's": 'https://www.moodys.com',
    '中诚信': 'https://www.ccxi.com.cn',
    '联合资信': 'https://www.lhratings.com',
    '恒生电子': 'https://www.hundsun.com',
    '恒生风控': 'https://www.hundsun.com',
    '金证股份': 'https://www.szkingdom.com',
    
    // 办公效率
    'Notion': 'https://www.notion.so',
    'Notion AI': 'https://www.notion.so/product/ai',
    '飞书': 'https://www.feishu.cn',
    '飞书文档': 'https://www.feishu.cn/product/docs',
    '飞书妙记': 'https://www.feishu.cn/product/minutes',
    'WPS AI': 'https://ai.wps.cn',
    'Grammarly': 'https://www.grammarly.com',
    'Gamma': 'https://gamma.app',
    'Beautiful.ai': 'https://www.beautiful.ai',
    'Confluence': 'https://www.atlassian.com/software/confluence',
    'Outlook': 'https://outlook.live.com',
    'Calendly': 'https://calendly.com',
    
    // 可视化
    'Tableau': 'https://www.tableau.com',
    'Power BI': 'https://powerbi.microsoft.com',
    '帆软FineReport': 'https://www.finereport.com',
    '永洪BI': 'https://www.yonghongtech.com',
    'Pandas': 'https://pandas.pydata.org',
    'Python': 'https://www.python.org',
    'Excel': 'https://www.microsoft.com/excel',
    
    // 交易系统
    'Interactive Brokers': 'https://www.interactivebrokers.com',
    'TradeStation': 'https://www.tradestation.com',
    
    // CRM与企业协作
    'Salesforce': 'https://www.salesforce.com',
    '企业微信': 'https://work.weixin.qq.com',
    
    // 其他
    '雪球': 'https://xueqiu.com',
    '华尔街见闻': 'https://wallstreetcn.com',
    '北大法宝': 'https://www.pkulaw.com',
    'Otter.ai': 'https://otter.ai',
    '讯飞听见': 'https://www.iflyrec.com',
    'Coursera': 'https://www.coursera.org'
};

// ===== 优先级数据 =====
const priorityData = [
    {
        level: 'P0',
        title: '核心投研能力',
        coverage: '46%',
        agents: ['Quant', 'Research'],
        description: '量化策略和投资研究'
    },
    {
        level: 'P1',
        title: '数据与风控',
        coverage: '26%',
        agents: ['Data', 'Risk'],
        description: '数据处理和风险管理'
    },
    {
        level: 'P2',
        title: '效率提升',
        coverage: '20%',
        agents: ['Chatbot', 'Workflow'],
        description: '日常沟通和流程自动化'
    },
    {
        level: 'P3',
        title: '交易执行',
        coverage: '5%',
        agents: ['Trading'],
        description: '订单执行和交易分析'
    },
    {
        level: 'P4',
        title: '辅助能力',
        coverage: '3%',
        agents: ['Browser', 'Background'],
        description: '信息采集和后台任务'
    }
];

// ===== 构建关系图数据 =====
function buildNetworkData() {
    const nodes = [];
    const links = [];
    const productTaskMap = {};
    const productAgentMap = {};
    
    // 添加用户角色节点（第0列，最左边）
    Object.entries(userData).forEach(([userKey, user]) => {
        nodes.push({
            id: user.id,
            name: user.name,
            type: 'user',
            icon: user.icon,
            description: user.description,
            relatedSubcategories: user.relatedSubcategories,
            cssClass: user.cssClass,
            userKey: userKey,
            column: 0
        });
    });
    
    // 添加场景子类节点（第1列）- 跳过场景大类
    Object.entries(taskData).forEach(([sceneKey, scene]) => {
        // 添加场景子类节点（第1列）
        Object.entries(scene.subcategories).forEach(([subcatName, subcat]) => {
            nodes.push({
                id: subcat.id,
                name: subcatName,
                type: 'subcat',
                timePercent: subcat.timePercent,
                parentScene: scene.id,
                column: 1
            });
            
            // 添加任务节点（第2列）
            subcat.tasks.forEach(task => {
                nodes.push({
                    id: task.id,
                    name: task.name,
                    type: 'task',
                    timePercent: task.timePercent,
                    agent: task.agent,
                    tech: task.tech,
                    products: task.products,
                    example: task.example,
                    parentSubcat: subcat.id,
                    parentScene: scene.id,
                    column: 2
                });
                
                // 子类->任务连线
                links.push({
                    source: subcat.id,
                    target: task.id,
                    type: 'subcat-task'
                });
                
                // 记录产品-任务关系
                task.products.forEach(product => {
                    if (!productTaskMap[product]) {
                        productTaskMap[product] = [];
                    }
                    productTaskMap[product].push(task.id);
                    
                    if (!productAgentMap[product]) {
                        productAgentMap[product] = new Set();
                    }
                    productAgentMap[product].add(task.agent);
                });
            });
        });
    });
    
    // 添加用户角色->场景子类连线
    Object.entries(userData).forEach(([userKey, user]) => {
        user.relatedSubcategories.forEach(subcatId => {
            // 检查子类是否存在
            const subcatExists = nodes.some(n => n.id === subcatId && n.type === 'subcat');
            if (subcatExists) {
                links.push({
                    source: user.id,
                    target: subcatId,
                    type: 'user-subcat'
                });
            }
        });
    });
    
    // 添加Agent节点（第3列）
    Object.entries(agentData).forEach(([agentKey, agent]) => {
        nodes.push({
            id: agent.id,
            name: agent.name,
            type: 'agent',
            icon: agent.icon,
            coverage: agent.coverage,
            techs: agent.techs,
            description: agent.description,
            cssClass: agent.cssClass,
            agentKey: agentKey,
            column: 3
        });
    });
    
    // 添加任务->Agent连线
    nodes.filter(n => n.type === 'task').forEach(task => {
        const agentId = agentData[task.agent]?.id;
        if (agentId) {
            links.push({
                source: task.id,
                target: agentId,
                type: 'task-agent'
            });
        }
    });
    
    // 收集所有产品并添加节点（第5列）
    const allProducts = new Set();
    nodes.filter(n => n.type === 'task').forEach(task => {
        task.products?.forEach(p => allProducts.add(p));
    });
    
    allProducts.forEach(product => {
        nodes.push({
            id: `product-${product}`,
            name: product,
            type: 'product',
            url: productLinks[product] || '#',
            relatedTasks: productTaskMap[product] || [],
            relatedAgents: Array.from(productAgentMap[product] || []),
            column: 4
        });
    });
    
    // 添加任务->产品连线
    nodes.filter(n => n.type === 'task').forEach(task => {
        task.products?.forEach(product => {
            links.push({
                source: task.id,
                target: `product-${product}`,
                type: 'task-product'
            });
        });
    });
    
    return { nodes, links };
}

// ===== 渲染关系图 =====
function renderNetworkGraph() {
    const container = document.getElementById('network-graph');
    const { nodes, links } = buildNetworkData();
    
    const width = container.clientWidth || 1400;
    // 计算产品节点数量，动态调整高度，确保每个产品节点有足够的垂直空间
    const productCount = nodes.filter(n => n.type === 'product').length;
    const taskCount = nodes.filter(n => n.type === 'task').length;
    const maxRowCount = Math.max(productCount, taskCount);
    const minRowHeight = 35; // 每行最小高度
    const height = Math.max(1400, maxRowCount * minRowHeight);
    
    // 清空容器
    container.innerHTML = '';
    
    // 创建SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // 定义渐变
    const defs = svg.append('defs');
    
    // 场景渐变
    const sceneGradient = defs.append('linearGradient')
        .attr('id', 'scene-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    sceneGradient.append('stop').attr('offset', '0%').attr('stop-color', '#D4AF37');
    sceneGradient.append('stop').attr('offset', '100%').attr('stop-color', '#F4E5A3');
    
    // 子类渐变
    const subcatGradient = defs.append('linearGradient')
        .attr('id', 'subcat-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    subcatGradient.append('stop').attr('offset', '0%').attr('stop-color', '#10B981');
    subcatGradient.append('stop').attr('offset', '100%').attr('stop-color', '#6EE7B7');
    
    // 任务渐变
    const taskGradient = defs.append('linearGradient')
        .attr('id', 'task-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    taskGradient.append('stop').attr('offset', '0%').attr('stop-color', '#3B82F6');
    taskGradient.append('stop').attr('offset', '100%').attr('stop-color', '#93C5FD');
    
    // Agent渐变
    const agentGradient = defs.append('linearGradient')
        .attr('id', 'agent-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    agentGradient.append('stop').attr('offset', '0%').attr('stop-color', '#8B5AI助手平台6');
    agentGradient.append('stop').attr('offset', '100%').attr('stop-color', '#C4B5FD');
    
    // 产品渐变
    const productGradient = defs.append('linearGradient')
        .attr('id', 'product-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    productGradient.append('stop').attr('offset', '0%').attr('stop-color', '#EC4899');
    productGradient.append('stop').attr('offset', '100%').attr('stop-color', '#F9A8D4');
    
    // 用户角色渐变
    const userGradient = defs.append('linearGradient')
        .attr('id', 'user-gradient')
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '100%');
    userGradient.append('stop').attr('offset', '0%').attr('stop-color', '#F97316');
    userGradient.append('stop').attr('offset', '100%').attr('stop-color', '#FDBA74');
    
    // 计算节点位置（现在有5列）
    const columnWidth = width / 5;
    const columnX = [
        columnWidth * 0.5,
        columnWidth * 1.5,
        columnWidth * 2.5,
        columnWidth * 3.5,
        columnWidth * 4.5
    ];
    
    // 按列分组节点
    const nodesByColumn = [[], [], [], [], []];
    nodes.forEach(node => {
        nodesByColumn[node.column].push(node);
    });
    
    // 计算每列节点的Y位置
    nodesByColumn.forEach((columnNodes, col) => {
        const spacing = height / (columnNodes.length + 1);
        columnNodes.forEach((node, i) => {
            node.x = columnX[col];
            node.y = spacing * (i + 1);
        });
    });
    
    // 创建节点ID映射
    const nodeMap = {};
    nodes.forEach(node => {
        nodeMap[node.id] = node;
    });
    
    // 绘制连线
    const linkGroup = svg.append('g').attr('class', 'links');
    
    const linkElements = linkGroup.selectAll('path')
        .data(links)
        .enter()
        .append('path')
        .attr('d', d => {
            const source = nodeMap[d.source];
            const target = nodeMap[d.target];
            if (!source || !target) return '';
            
            const midX = (source.x + target.x) / 2;
            return `M ${source.x} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x} ${target.y}`;
        })
        .attr('fill', 'none')
        .attr('stroke', 'rgba(212, 175, 55, 0.3)')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.5)
        .attr('data-source', d => d.source)
        .attr('data-target', d => d.target);
    
    // 绘制节点
    const nodeGroup = svg.append('g').attr('class', 'nodes');
    
    const nodeElements = nodeGroup.selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .attr('class', d => `node node-${d.type}`)
        .attr('transform', d => `translate(${d.x}, ${d.y})`)
        .attr('data-id', d => d.id)
        .style('cursor', 'pointer');
    
    // 节点背景
    nodeElements.append('rect')
        .attr('class', 'node-bg')
        .attr('x', d => d.type === 'product' ? -60 : (d.type === 'user' ? -50 : -45))
        .attr('y', -12)
        .attr('width', d => d.type === 'product' ? 120 : (d.type === 'user' ? 100 : 90))
        .attr('height', 24)
        .attr('rx', 12)
        .attr('fill', d => {
            switch(d.type) {
                case 'user': return 'url(#user-gradient)';
                case 'scene': return 'url(#scene-gradient)';
                case 'subcat': return 'url(#subcat-gradient)';
                case 'task': return 'url(#task-gradient)';
                case 'agent': return 'url(#agent-gradient)';
                case 'product': return 'url(#product-gradient)';
                default: return '#94A3B8';
            }
        })
        .attr('opacity', 0.9)
        .style('cursor', d => d.type === 'product' ? 'pointer' : 'pointer');
    
    // 节点文字
    nodeElements.append('text')
        .attr('class', 'node-text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', 'white')
        .attr('font-size', d => (d.type === 'scene' || d.type === 'user') ? '12px' : '11px')
        .attr('font-weight', d => (d.type === 'scene' || d.type === 'user') ? '600' : '500')
        .style('cursor', d => d.type === 'product' ? 'pointer' : 'pointer')
        .style('pointer-events', 'all')
        .text(d => {
            if (d.type === 'user') {
                return `${d.icon} ${d.name}`;
            }
            if (d.type === 'agent') {
                return `${d.icon} ${d.name.replace(' Agent', '')}`;
            }
            // 显示完整的产品名称
            if (d.type === 'product') {
                return d.name.length > 12 ? d.name.slice(0, 12) + '...' : d.name;
            }
            // 其他类型也增加显示长度
            const maxLen = 8;
            return d.name.length > maxLen ? d.name.slice(0, maxLen) + '...' : d.name;
        });
    
    // Tooltip
    const tooltip = d3.select('#tooltip');
    
    nodeElements
        .on('mouseenter', function(event, d) {
            let content = '';
            
            if (d.type === 'task') {
                content = `
                    <div class="tooltip-title">${d.name}</div>
                    <div class="tooltip-content">
                        <div class="tooltip-row"><span class="tooltip-label">时长占比：</span>${d.timePercent}%</div>
                        <div class="tooltip-row"><span class="tooltip-label">Agent类型：</span>${d.agent}</div>
                        <div class="tooltip-row"><span class="tooltip-label">技术实现：</span>${d.tech}</div>
                        <div class="tooltip-row"><span class="tooltip-label">任务示例：</span>${d.example}</div>
                        <div class="tooltip-row"><span class="tooltip-label">业界产品：</span>${d.products?.join(', ')}</div>
                    </div>
                `;
            } else if (d.type === 'product') {
                content = `
                    <div class="tooltip-title">🔗 ${d.name}</div>
                    <div class="tooltip-content">
                        <div>点击文字：跳转产品官网</div>
                        <div>点击背景：显示关联关系</div>
                        <div class="tooltip-row"><span class="tooltip-label">关联Agent：</span>${d.relatedAgents?.join(', ')}</div>
                        <div style="margin-top:4px;font-size:0.8em;color:rgba(255,255,255,0.6)">${d.url}</div>
                    </div>
                `;
            } else if (d.type === 'agent') {
                content = `
                    <div class="tooltip-title">${d.icon} ${d.name}</div>
                    <div class="tooltip-content">
                        <div class="tooltip-row"><span class="tooltip-label">覆盖率：</span>${d.coverage}%</div>
                        <div class="tooltip-row"><span class="tooltip-label">核心能力：</span>${d.description}</div>
                        <div class="tooltip-row"><span class="tooltip-label">技术栈：</span>${d.techs?.join(', ')}</div>
                    </div>
                `;
            } else if (d.type === 'scene' || d.type === 'subcat') {
                content = `
                    <div class="tooltip-title">${d.name}</div>
                    <div class="tooltip-content">
                        <div class="tooltip-row"><span class="tooltip-label">时间占比：</span>${d.timePercent}%</div>
                    </div>
                `;
            } else if (d.type === 'user') {
                content = `
                    <div class="tooltip-title">${d.icon} ${d.name}</div>
                    <div class="tooltip-content">
                        <div class="tooltip-row"><span class="tooltip-label">工作重点：</span>${d.description}</div>
                        <div class="tooltip-row"><span class="tooltip-label">关联场景：</span>${d.relatedSubcategories?.length || 0}个子场景</div>
                    </div>
                `;
            }
            
            tooltip.html(content)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .classed('show', true);
        })
        .on('mousemove', function(event) {
            tooltip
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseleave', function() {
            tooltip.classed('show', false);
        });
    
    // 为所有节点的背景添加点击事件（高亮关联）
    nodeElements.select('rect.node-bg')
        .on('click', function(event, d) {
            event.stopPropagation();
            // 高亮关联节点
            highlightConnected(d.id, nodes, links, nodeElements, linkElements);
        });
    
    // 非产品节点的文字也可以点击高亮
    nodeElements.filter(d => d.type !== 'product')
        .select('text.node-text')
        .on('click', function(event, d) {
            event.stopPropagation();
            highlightConnected(d.id, nodes, links, nodeElements, linkElements);
        });
    
    // 产品节点文字点击跳转链接（单独处理）
    nodeElements.filter(d => d.type === 'product')
        .select('text.node-text')
        .on('click', function(event, d) {
            event.stopPropagation();
            if (d.url && d.url !== '#') {
                window.open(d.url, '_blank');
            }
        })
        .style('text-decoration', 'underline')
        .style('cursor', 'pointer');
    
    // 点击空白取消高亮
    svg.on('click', function() {
        resetHighlight(nodeElements, linkElements);
    });
}

// ===== 高亮关联节点 =====
function highlightConnected(nodeId, nodes, links, nodeElements, linkElements) {
    const connectedNodes = new Set([nodeId]);
    
    // 对于产品节点，只高亮关联的任务和Agent
    const clickedNode = nodes.find(n => n.id === nodeId);
    
    if (clickedNode && clickedNode.type === 'product') {
        // 产品节点：高亮关联的任务
        clickedNode.relatedTasks?.forEach(taskId => {
            connectedNodes.add(taskId);
        });
        // 高亮关联的Agent
        clickedNode.relatedAgents?.forEach(agentKey => {
            const agent = agentData[agentKey];
            if (agent) {
                connectedNodes.add(agent.id);
            }
        });
    } else {
        // 其他节点：使用链接关系
        links.forEach(link => {
            if (link.source === nodeId) {
                connectedNodes.add(link.target);
            } else if (link.target === nodeId) {
                connectedNodes.add(link.source);
            }
        });
    }
    
    nodeElements.style('opacity', function(d) {
        return connectedNodes.has(d.id) ? 1 : 0.2;
    });
    
    linkElements.style('opacity', function(d) {
        // 对于产品节点，只高亮与关联任务相关的连线
        if (clickedNode && clickedNode.type === 'product') {
            const isRelatedLink = connectedNodes.has(d.source) && connectedNodes.has(d.target);
            return isRelatedLink ? 1 : 0.1;
        }
        return (d.source === nodeId || d.target === nodeId) ? 1 : 0.1;
    }).style('stroke', function(d) {
        if (clickedNode && clickedNode.type === 'product') {
            const isRelatedLink = connectedNodes.has(d.source) && connectedNodes.has(d.target);
            return isRelatedLink ? '#d4af37' : 'rgba(212, 175, 55, 0.3)';
        }
        return (d.source === nodeId || d.target === nodeId) ? '#d4af37' : 'rgba(212, 175, 55, 0.3)';
    }).style('stroke-width', function(d) {
        if (clickedNode && clickedNode.type === 'product') {
            const isRelatedLink = connectedNodes.has(d.source) && connectedNodes.has(d.target);
            return isRelatedLink ? 2.5 : 1.5;
        }
        return (d.source === nodeId || d.target === nodeId) ? 2.5 : 1.5;
    });
}

// ===== 重置高亮 =====
function resetHighlight(nodeElements, linkElements) {
    nodeElements.style('opacity', 1);
    linkElements
        .style('opacity', 0.6)
        .style('stroke', 'rgba(212, 175, 55, 0.3)')
        .style('stroke-width', 1.5);
}

// ===== 导出数据和函数 =====
window.taskData = taskData;
window.agentData = agentData;
window.productLinks = productLinks;
window.priorityData = priorityData;
window.renderNetworkGraph = renderNetworkGraph;
