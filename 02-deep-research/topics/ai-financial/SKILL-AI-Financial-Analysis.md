# 金融从业者工作场景分析与可视化 Skill

> **版本**: 2.0.0  
> **适用场景**: 金融机构数字化转型、投研效能分析、Agent能力覆盖评估  
> **输出形式**: 交互式Web可视化页面（纯前端，可部署至Vercel/Netlify）

---

## 一、Skill 概述

### 1.1 目标
基于目标用户群体（如量化分析师、基金经理、风控专员、研究员等金融从业者）的日常工作场景，系统性地：
1. **梳理工作任务分类** - 按场景大类→场景子类→具体任务三层结构
2. **分析时间占比** - 量化每个任务在工作中的时长占比
3. **定义Agent类型** - 确定AI Agent的能力分类和覆盖范围
4. **匹配业界产品** - 关联海外和国内主流金融AI产品
5. **确定开发优先级** - 基于覆盖率给出P0-P4优先级建议
6. **生成可视化报告** - 输出交互式关系图和数据表格

### 1.2 输出物
- `index.html` - 主页面结构
- `styles.css` - 样式文件（现代化UI）
- `network-graph.js` - 关系图渲染和数据定义
- `main.js` - 交互逻辑
- `vercel.json` - 部署配置（可选）

---

## 二、分析方法论

### 2.1 工作场景分类原则

```
场景大类（2类）
├── 投研场景（占比约60%）
│   ├── 量化策略研发
│   ├── 因子分析
│   ├── 数据获取与清洗
│   ├── 回测与模拟
│   ├── 投资研究
│   ├── 市场分析
│   ├── 组合管理
│   └── 交易执行
└── 运营合规场景（占比约40%）
    ├── 风险控制
    ├── 合规审查
    ├── 报告撰写
    ├── 客户沟通
    ├── 知识管理
    ├── 会议效率
    ├── 数据报表
    └── 学习培训
```

### 2.2 时间占比估算规则

| 占比范围 | 分类 | 样式标识 |
|---------|------|---------|
| ≥10% | 高频任务 | `time-high`（红色加粗） |
| 3%-9% | 中频任务 | `time-medium`（橙色） |
| 1%-2.9% | 低频任务 | `time-low`（黄色） |
| <1% | 极低频任务 | `time-verylow`（灰色） |

**验证规则**：
- 投研场景任务时间占比总和 = 60%（±2%）
- 运营合规场景任务时间占比总和 = 40%（±2%）
- 所有任务时间占比总和 = 100%

### 2.3 Agent类型定义

| Agent类型 | 图标 | 核心能力 | 典型场景 |
|-----------|------|---------|---------|
| Quant Agent | 📈 | 策略编写、因子计算、回测分析、信号生成 | 占比最高，约25-30% |
| Research Agent | 🔬 | 行业调研、公司分析、深度报告、竞品分析 | 投研分析，约15-20% |
| Data Agent | 📊 | 数据获取、数据清洗、可视化、报表生成 | 数据处理，约12-15% |
| Risk Agent | ⚠️ | 风险评估、VaR计算、压力测试、合规检查 | 风控合规，约10-12% |
| Chatbot Agent | 💬 | 知识问答、文档写作、翻译、客户服务 | 通用对话，约10-12% |
| Workflow Agent | ⚙️ | 报告审核、流程自动化、邮件处理、审批流程 | 流程自动化，约8-10% |
| Trading Agent | 💹 | 订单管理、交易执行、执行分析、算法交易 | 交易执行，约5-8% |
| Browser Agent | 🌐 | 信息采集、舆情监控、公告抓取、网页自动化 | 信息获取，约3-5% |
| Background Agent | ⏰ | 定时任务、监控告警、自动化报告、日程管理 | 后台运行，约2-4% |

**验证规则**：所有Agent覆盖率总和 = 100%

### 2.4 业界产品选择原则

1. **专业金融产品优先**：选择金融行业专用的数据终端和分析工具
2. **海外产品参考**：引入Bloomberg、Reuters等国际主流产品
3. **国内产品补充**：增加Wind、同花顺等国内金融数据产品
4. **AI产品融合**：结合通用AI助手提升效率
5. **链接可用**：所有产品必须提供有效的官网链接

**产品分类参考**：

| 类别 | 海外产品示例 | 国内产品示例 |
|-----|------------|------------|
| 量化平台 | QuantConnect, Alpaca, Zipline | 聚宽, 米筐RiceQuant, 优矿, 掘金量化 |
| 数据终端 | Bloomberg, Reuters, FactSet | Wind万得, 东方财富Choice, 同花顺iFinD |
| 研究工具 | Capital IQ, Sentieo, Visible Alpha | 萝卜投研, 慧博投研, 朝阳永续 |
| AI助手 | ChatGPT, Claude, Perplexity | Kimi, 通义千问, 豆包, 讯飞星火 |
| 风控合规 | Moody's Analytics, MSCI RiskMetrics | 中诚信, 联合资信, 鹏元资信 |
| 办公效率 | Notion AI, Grammarly, Gamma | 飞书文档, WPS AI, 飞书妙记 |
| 可视化工具 | Tableau, Power BI | 帆软FineReport, 永洪BI |
| 交易系统 | Interactive Brokers, TradeStation | 恒生电子, 金证股份 |

---

## 三、数据结构规范

### 3.1 任务数据结构

```javascript
const taskData = {
    research: {
        name: '投研场景',
        id: 'scene-research',
        timePercent: 60,  // 场景总占比
        subcategories: {
            '量化策略研发': {
                id: 'subcat-quant-dev',
                timePercent: 18,  // 子类总占比
                tasks: [
                    {
                        id: 'task-strategy-coding',
                        name: '策略编写',
                        timePercent: 8,  // 单任务占比
                        agent: 'Quant',  // 关联的Agent类型
                        tech: 'LLM+量化框架',      // 技术实现
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
        timePercent: 40,  // 场景总占比
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
                        example: 'CFA学习、Python编程'
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
            }
        }
    }
};
```

### 3.2 Agent数据结构

```javascript
const agentData = {
    'Quant': {
        id: 'agent-quant',
        name: 'Quant Agent',
        icon: '📈',
        coverage: 28,  // 覆盖率百分比
        techs: ['LLM', '量化框架', '优化算法'],
        description: '量化策略开发、因子计算、回测分析'
    },
    'Research': {
        id: 'agent-research',
        name: 'Research Agent',
        icon: '🔬',
        coverage: 18,
        techs: ['LLM', '搜索', '知识图谱'],
        description: '行业研究、公司分析、深度报告'
    },
    'Data': {
        id: 'agent-data',
        name: 'Data Agent',
        icon: '📊',
        coverage: 14,
        techs: ['数据处理', '可视化', 'ETL'],
        description: '数据获取、清洗、可视化'
    },
    'Risk': {
        id: 'agent-risk',
        name: 'Risk Agent',
        icon: '⚠️',
        coverage: 12,
        techs: ['风控模型', '规则引擎'],
        description: '风险监控、压力测试、合规检查'
    },
    'Chatbot': {
        id: 'agent-chatbot',
        name: 'Chatbot Agent',
        icon: '💬',
        coverage: 11,
        techs: ['LLM', 'RAG'],
        description: '知识问答、文档写作、客户服务'
    },
    'Workflow': {
        id: 'agent-workflow',
        name: 'Workflow Agent',
        icon: '⚙️',
        coverage: 9,
        techs: ['RPA', 'LLM'],
        description: '流程自动化、报告审核'
    },
    'Trading': {
        id: 'agent-trading',
        name: 'Trading Agent',
        icon: '💹',
        coverage: 5,
        techs: ['交易系统', '算法交易'],
        description: '订单执行、交易分析'
    },
    'Browser': {
        id: 'agent-browser',
        name: 'Browser Agent',
        icon: '🌐',
        coverage: 2,
        techs: ['爬虫', 'NLP'],
        description: '信息采集、舆情监控'
    },
    'Background': {
        id: 'agent-background',
        name: 'Background Agent',
        icon: '⏰',
        coverage: 1,
        techs: ['定时任务', '监控'],
        description: '自动化任务、定时报告'
    }
};
```

### 3.3 产品链接数据结构

```javascript
const productLinks = {
    // === 量化平台 ===
    '聚宽': 'https://www.joinquant.com',
    '米筐': 'https://www.ricequant.com',
    '优矿': 'https://uqer.datayes.com',
    '掘金量化': 'https://www.myquant.cn',
    'QuantConnect': 'https://www.quantconnect.com',
    'Alpaca': 'https://alpaca.markets',
    'Zipline': 'https://www.zipline.io',
    
    // === 数据终端 ===
    'Wind': 'https://www.wind.com.cn',
    '东方财富Choice': 'https://choice.eastmoney.com',
    '同花顺iFinD': 'https://www.51ifind.com',
    'Bloomberg': 'https://www.bloomberg.com/professional',
    'Reuters': 'https://www.refinitiv.com',
    'FactSet': 'https://www.factset.com',
    'Tushare': 'https://tushare.pro',
    'AKShare': 'https://akshare.xyz',
    
    // === 研究工具 ===
    '萝卜投研': 'https://robo.datayes.com',
    '慧博投研': 'https://www.hibor.com.cn',
    '朝阳永续': 'https://www.go-goal.com',
    'Capital IQ': 'https://www.capitaliq.com',
    'Sentieo': 'https://sentieo.com',
    
    // === AI助手 ===
    'ChatGPT': 'https://chat.openai.com',
    'Claude': 'https://claude.ai',
    'Perplexity': 'https://perplexity.ai',
    'Kimi': 'https://kimi.moonshot.cn',
    '通义千问': 'https://tongyi.aliyun.com/qianwen',
    '豆包': 'https://www.doubao.com',
    '讯飞星火': 'https://xinghuo.xfyun.cn',
    
    // === 风控合规 ===
    'MSCI RiskMetrics': 'https://www.msci.com/riskmetrics',
    "Moody's Analytics": 'https://www.moodysanalytics.com',
    '中诚信': 'https://www.ccxi.com.cn',
    '联合资信': 'https://www.lhratings.com',
    
    // === 办公效率 ===
    'Notion': 'https://www.notion.so',
    'Notion AI': 'https://www.notion.so/product/ai',
    '飞书': 'https://www.feishu.cn',
    '飞书文档': 'https://www.feishu.cn/product/docs',
    '飞书妙记': 'https://www.feishu.cn/product/minutes',
    'WPS AI': 'https://ai.wps.cn',
    'Grammarly': 'https://www.grammarly.com',
    'Gamma': 'https://gamma.app',
    
    // === 可视化 ===
    'Tableau': 'https://www.tableau.com',
    'Power BI': 'https://powerbi.microsoft.com',
    '帆软FineReport': 'https://www.finereport.com',
    '永洪BI': 'https://www.yonghongtech.com',
    'TradingView': 'https://www.tradingview.com',
    
    // === 交易系统 ===
    '恒生电子': 'https://www.hundsun.com',
    '金证股份': 'https://www.szkingdom.com',
    'Interactive Brokers': 'https://www.interactivebrokers.com',
    'TradeStation': 'https://www.tradestation.com',
    
    // === 其他 ===
    '雪球': 'https://xueqiu.com',
    '华尔街见闻': 'https://wallstreetcn.com',
    '北大法宝': 'https://www.pkulaw.com',
    'Otter.ai': 'https://otter.ai',
    '讯飞听见': 'https://www.iflyrec.com',
    'Coursera': 'https://www.coursera.org',
    'Calendly': 'https://calendly.com',
    'Confluence': 'https://www.atlassian.com/software/confluence'
};
```

---

## 四、可视化规范

### 4.1 页面结构

```
┌─────────────────────────────────────────────────────────┐
│                      Header                              │
│       金融从业者工作场景分析 + 副标题描述                 │
├─────────────────────────────────────────────────────────┤
│                   统计卡片区域                            │
│    [总任务数] [投研任务] [运营合规任务] [Agent类型数]      │
├─────────────────────────────────────────────────────────┤
│                  开发优先级分析                           │
│   [P0卡片] [P1卡片] [P2卡片] [P3卡片] [P4卡片]            │
├─────────────────────────────────────────────────────────┤
│                    关系图区域                             │
│  场景大类 → 场景子类 → 工作任务 → Agent类型               │
│                                  ↘ 业界产品               │
├─────────────────────────────────────────────────────────┤
│                   开发路线图                              │
│   [阶段1] → [阶段2] → [阶段3] → [阶段4]                   │
├─────────────────────────────────────────────────────────┤
│                  投研场景表格                             │
├─────────────────────────────────────────────────────────┤
│                运营合规场景表格                           │
├─────────────────────────────────────────────────────────┤
│                 Agent类型卡片                            │
├─────────────────────────────────────────────────────────┤
│                     Footer                               │
└─────────────────────────────────────────────────────────┘
```

### 4.2 关系图规范

**5列布局**：
1. **场景大类**（金色渐变 - 代表金融）
2. **场景子类**（绿色渐变）
3. **工作任务**（蓝色/紫色渐变）
4. **Agent类型**（青色渐变）
5. **业界产品**（粉色渐变）

**交互规范**：
- **悬浮**：显示Tooltip，包含详细信息
- **点击节点**：高亮相关联的节点和连线
- **点击产品文字**：跳转产品官网（新窗口）
- **点击产品背景**：高亮关联的任务和Agent
- **点击空白**：取消所有高亮

### 4.3 配色规范

```css
:root {
    /* 主色 - 金融主题 */
    --primary-color: #D4AF37;  /* 金色 */
    
    /* 场景色 */
    --research-color: #3B82F6;      /* 投研场景-蓝色 */
    --operation-color: #8B5CF6;     /* 运营合规-紫色 */
    
    /* 优先级色 */
    --p0-color: #DC2626;       /* P0-红色 */
    --p1-color: #EA580C;       /* P1-橙色 */
    --p2-color: #CA8A04;       /* P2-黄色 */
    --p3-color: #2563EB;       /* P3-蓝色 */
    --p4-color: #64748B;       /* P4-灰色 */
    
    /* Agent徽章色 */
    --badge-quant-bg: #FEF3C7;
    --badge-quant-text: #D97706;
    --badge-research-bg: #DBEAFE;
    --badge-research-text: #2563EB;
    --badge-data-bg: #D1FAE5;
    --badge-data-text: #059669;
    --badge-risk-bg: #FEE2E2;
    --badge-risk-text: #DC2626;
    --badge-chatbot-bg: #E0E7FF;
    --badge-chatbot-text: #4F46E5;
    --badge-workflow-bg: #F3E8FF;
    --badge-workflow-text: #7C3AED;
    --badge-trading-bg: #ECFDF5;
    --badge-trading-text: #10B981;
    --badge-browser-bg: #F0F9FF;
    --badge-browser-text: #0284C7;
    --badge-background-bg: #F5F5F5;
    --badge-background-text: #6B7280;
}
```

### 4.4 响应式断点

| 断点 | 布局调整 |
|-----|---------|
| > 1200px | 4列统计卡片，5列优先级卡片，3列Agent卡片 |
| 768-1200px | 2列统计卡片，3列优先级卡片，2列Agent卡片 |
| < 768px | 1列布局，关系图可横向滚动 |

---

## 五、交互规范

### 5.1 Tooltip内容

**任务节点**：
```
任务名称
时长占比：8%
所属场景：投研场景 - 量化策略研发
Agent类型：Quant
任务示例：编写均线交叉、动量等量化策略代码
业界产品：聚宽, QuantConnect, 米筐
```

**产品节点**：
```
🔗 产品名称
点击文字：跳转产品官网
点击背景：显示关联关系
关联Agent：Quant, Data
关联任务：策略编写, 因子计算...
https://product-url.com
```

### 5.2 表格产品链接

表格中的产品名称自动转换为可点击的超链接：
- 点击后新窗口打开产品官网
- 链接样式：主色调，悬浮时显示下划线

---

## 六、质量检查清单

### 6.1 数据一致性

- [ ] 投研场景时间占比总和 = 60%（±2%）
- [ ] 运营合规场景时间占比总和 = 40%（±2%）
- [ ] 所有Agent覆盖率总和 = 100%
- [ ] 任务数量与表格标题一致
- [ ] 所有产品都有对应的官网链接

### 6.2 交互功能

- [ ] 节点悬浮显示Tooltip
- [ ] 节点点击高亮关联节点
- [ ] 产品文字点击跳转官网
- [ ] 产品背景点击显示关联
- [ ] 表格产品名可点击跳转
- [ ] 响应式布局正常

### 6.3 视觉效果

- [ ] Header渐变动画效果（金融主题金色）
- [ ] 卡片悬浮上浮效果
- [ ] 入场动画效果
- [ ] 滚动条美化
- [ ] Tooltip毛玻璃效果

---

## 七、执行流程

### Step 1: 需求分析
1. 确定目标用户群体（如：量化分析师、基金经理、风控专员）
2. 收集金融工作场景和任务清单
3. 估算各任务时间占比

### Step 2: 数据整理
1. 按三层结构组织任务数据（投研/运营合规）
2. 定义Agent类型和覆盖率（Quant、Research、Risk等）
3. 匹配海外+国内金融产品
4. 收集所有产品官网链接

### Step 3: 代码实现
1. 创建 `index.html` 页面结构
2. 创建 `styles.css` 样式文件
3. 创建 `network-graph.js` 数据和关系图
4. 创建 `main.js` 交互逻辑
5. 创建 `vercel.json` 部署配置

### Step 4: 质量验证
1. 检查数据一致性
2. 测试所有交互功能
3. 验证产品链接可用性
4. 测试响应式布局

### Step 5: 部署发布
1. 本地预览验证
2. 部署至Vercel
3. 分享公开链接

---

## 八、示例Prompt

当需要执行此Skill时，可使用以下Prompt：

```
请按照"金融从业者工作场景分析与可视化Skill"完成以下任务：

1. 目标用户：[填写目标用户，如：私募基金量化研究员]
2. 分析维度：工作场景分类、时间占比、Agent类型、业界产品
3. 输出要求：
   - 交互式Web可视化页面
   - 5列关系图（场景→子类→任务→Agent→产品）
   - 支持金融产品链接跳转
   - 部署至Vercel

请严格按照Skill规范完成数据分析和代码实现。
```

### 典型用户示例

| 用户角色 | 重点场景 | 核心Agent |
|---------|---------|-----------|
| 量化分析师 | 量化策略研发、因子分析、回测 | Quant Agent |
| 基金经理 | 投资研究、组合管理、交易执行 | Research Agent, Trading Agent |
| 风控专员 | 风险监控、压力测试、合规检查 | Risk Agent |
| 研究员 | 行业研究、公司分析、研报撰写 | Research Agent |
| FOF投资经理 | 基金筛选、组合配置、业绩归因 | Research Agent, Data Agent |
| 交易员 | 订单执行、执行分析、算法交易 | Trading Agent |

---

## 九、版本记录

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| 1.0.0 | 2026-02-01 | 初始版本，AI工程师场景 |
| 2.0.0 | 2026-02-01 | 重构为金融从业者场景，新增量化、风控、基金等角色 |

---

**Skill维护者**: AI Studio  
**最后更新**: 2026-02-01
