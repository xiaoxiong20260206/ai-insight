# AI日报搜索关键词清单 (v4.1)

> **版本**: v4.1
> **更新时间**: 2026-03-20
> **说明**: 按板块组织的搜索关键词，用于 Step 1 两层搜索（含话题热词搜索策略）
> **v4.1变更**: 合并品牌重叠搜索，减少搜索次数 ~35次 → ~22次；固定信源改为直接 fetch_web 拉取

---

## 搜索架构

```
L1 广扫 (必做): search_web + weixin_search + xiaohongshu search
├── 海外搜索: 每板块1-2次（v4.1: 5板块共约10次）
├── 国内搜索: 每板块1-2次（v4.1: 合并品牌重叠，约8次）
├── 微信搜索: 每板块至少1次，全局不超过10次
│   ├── 轨道A 账号搜索: 按L1公众号名称搜索（v4.1: 2次广覆盖代替5次单板块）
│   └── 轨道B 话题搜索: 按海外热词翻译后的中文关键词搜索 ← v4.0新增
└── 小红书搜索: **强制搜索**国内热点和用户讨论 (P0必做，≥1条入报，质量门v9.1硬阻断)
                v4.1: "AI最新动态"与"大模型 今天"高度重叠，合并为2次

L1.5 固定信源直拉 (v4.1新增): fetch_web直接拉取，跳过搜索噪音
├── cursor.com/changelog — AI Coding最新版本
├── openai.com/blog — OpenAI官方公告
└── anthropic.com/news — Anthropic官方公告

L2 精研 (按需): 多轮 search_web + fetch_web
├── 触发: 多源共振≥3 或 突发事件
└── 限制: 每期最多2次
```

**v4.1 搜索次数目标**: 正常日 ~22次（原~35次），大事件日 ~27次

---

## ⭐ 微信话题热词搜索 (v4.0新增)

> **原理**: 账号搜索只能覆盖已知公众号的日常推送，话题搜索能发现追踪名单外的优质好文。
> **教训**: 2026-03-14日报0条微信直引，但当天有多篇OpenClaw安全预警、GTC深度分析等好文被遗漏。

### 执行方法
1. 完成海外搜索后，提取当天 **Top 2-3 热门关键词**
2. 将英文热词翻译/适配为中文搜索词
3. 在 `weixin_search` 中搜索，重点关注**深度解读类**文章

### 热词映射示例

| 海外热词 | 中文搜索词 |
|---------|-----------|
| GTC 2026 Feynman | `weixin_search("英伟达 GTC 费曼 深度")` |
| Claude Marketplace | `weixin_search("Claude 工具市场 解读")` |
| AI Agent sandbox | `weixin_search("AI智能体 沙箱 安全")` |
| Vibe Coding | `weixin_search("Vibe Coding 编程 方法论")` |
| GPT-5 self-learning | `weixin_search("GPT-5 自我学习 突破")` |
| BuzzFeed AI failure | `weixin_search("BuzzFeed AI转型 失败 教训")` |

### 筛选标准
- 有独到分析角度（非简单翻译/转载海外报道）
- 与日报已有条目形成互补（不重复）
- 每日至少从话题搜索中**采纳1篇**优质文章

---

## 🧠 大模型

### 海外搜索
```
"OpenAI GPT latest news today"
"Anthropic Claude update {今日日期}"
"Google Gemini news {今日日期}"
"Meta Llama update"
"AI model release {月份} 2026"
```

### 国内搜索
```
"DeepSeek 最新 发布"
"智谱 Moonshot kimi 最新"       # v4.1合并: 国内大模型综合一次搜索
"字节 AI 今天"                   # v4.1合并: 豆包+Trae+字节系统一搜索
"阿里 通义 Qwen 最新"
"百度 文心 ERNIE 最新"           # v4.1合并: 文心一言不再单独搜，与百度AI合并
```

> **v4.1注意**: 字节豆包(大模型)与Trae(AI Coding)的搜索已合并为一次 `"字节 AI 今天"`，
> 从两板块各搜一次减为共搜一次，去重工作由筛选阶段完成。

### 微信搜索
```
weixin_search("AI 今天")           # v4.1: 两次广覆盖替代5次单板块搜索
weixin_search("大模型 最新")
```

> **v4.1注意**: 微信轨道A原来5板块各搜1次，现在合并为2次广覆盖搜索（机器之心/量子位/新智元的内容不按板块区分），再用话题搜索补充领域深度。

### 优先信源
- openai.com/blog （L1.5直拉）
- anthropic.com/news （L1.5直拉）
- deepseek.com
- 机器之心、量子位、新智元

---

## ⌨️ AI Coding

### 海外搜索
```
"Cursor changelog {月份} 2026"
"Claude Code news today"
"GitHub Copilot update"
"AI coding tools latest"
"Codex CLI update"
```

### 国内搜索 (v4.1刷新)
```
"Trae 通义灵码 AI编程 最新"      # v4.1合并: Trae+通义灵码一次搜索
"CodeBuddy Comate AI编程"
"AI 编程 工具 国内 2026"
```

> ⚠️ **v4.1注意**:
> - MarsCode 已于2025年更名为 Trae（同一产品），不再单独搜索
> - CodeGeeX 已降级为插件
> - 字节AI编程(Trae)与字节大模型的搜索已合并到大模型板块的 `"字节 AI 今天"`

### 微信搜索
```
weixin_search("AI编程 最新")
weixin_search("代码助手")
```

### 优先信源
- cursor.com/changelog （L1.5直拉）
- trae.ai / trae.cn (字节)
- tongyi.aliyun.com (阿里)
- codebuddy.qq.com (腾讯)
- comate.baidu.com (百度)

---

## 📱 AI 应用

### 海外搜索
```
"AI application news today"
"ChatGPT update {月份} 2026"
"AI app launch"
"AI agent product"
```

### 国内搜索
```
"AI产品 发布 中国"
"kimi 豆包 AI应用 更新"          # v4.1合并: kimi+豆包应用层面一次搜索
"国内 AI应用 新品"
```

> **v4.1注意**: 豆包应用层面的搜索与大模型板块的字节系搜索有重叠，
> 均由大模型板块的 `"字节 AI 今天"` 覆盖，此处只保留kimi+豆包应用功能角度的搜索。

### 微信搜索
```
weixin_search("AI产品 最新")
weixin_search("AI应用 发布")
```

### 优先信源
- mashable.com
- techcrunch.com
- 36kr.com
- sspai.com (少数派)

---

## 🏭 AI 行业

### 海外搜索
```
"AI startup funding {月份} 2026"
"AI company valuation"
"AI investment news today"
"AI VC deal"
```

### 国内搜索
```
"AI 融资 中国 2026"
"国内 AI创业 融资"
"中国 AI估值 最新"
"AI 投资 国内"
```

### 微信搜索
```
weixin_search("AI融资")
weixin_search("AI投资")
```

### 优先信源
- news.crunchbase.com
- techcrunch.com/category/venture
- 36kr.com (投融资)
- 融中财经

---

## 🔄 企业AI转型

### 海外搜索
```
"enterprise AI transformation"
"AI productivity enterprise"
"AI digital transformation case"
```

### 国内搜索
```
"企业 AI 转型 案例"
"AI 数字化转型 中国"
"制造业 智能化 AI"
"国内 企业AI 实践"
"AI 提效 案例 中国"
```

### 微信搜索
```
weixin_search("企业AI转型")
weixin_search("数字化转型")
```

### 优先信源
- ibm.com/think
- mckinsey.com/capabilities/quantumblack
- 各企业官网新闻
- 政府经信委网站

---

## 日期锚定规则 (v4.0)

**所有搜索必须包含日期锚定词**:

```
❌ 错误 (泛日期):
"AI news March 2026"
"大模型 最新"

✅ 正确 (精确日期):
"AI news March 11 2026 today"
"大模型 今天 3月11日"
"OpenAI March 11"
```

---

## 小红书强制搜索 (P0)

> v4.1: 合并高度重叠的关键词，从3次减为2次

```
xiaohongshu.search("AI 今天")          # 合并原来的"AI最新动态"+"大模型 今天"
xiaohongshu.search("{当日热点关键词}")
```

**要求**: 至少1条小红书来源进入日报，质量门v9.1硬阻断

---

## 实时信源 (Step 0.5)

**优先获取实时聚合，锚定当日热点**:

| 优先级 | 信源 | 用途 |
|--------|------|------|
| P0 | 新浪AI热点小时报 | 按小时更新 |
| P0 | weixin_search("AI 今天") | 公众号当日推送 |
| P1 | 36kr.com/newsflashes | 国内创投实时 |
| P1 | IT之家AI频道 | 科技实时聚合 |

---

## 配置保鲜 (每月1日)

每月需检查并更新:
1. 产品URL是否仍在运营
2. 产品名称是否变更
3. 新进入者/退出者
4. 搜索关键词有效性
