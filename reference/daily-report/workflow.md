# AI日报执行流程 (v6.2)

> **版本**: v6.2 (Step 5 新增 mixCard 双路径推送，禁止纯文本降级)
> **更新时间**: 2026-04-29
> **核心原则**: 本文件包含执行AI日报所需的**全部规则**，无需跨文件查找

---

## ⚠️ 执行前必读

### 时间窗口定义 (P0)
```
N日日报 = 收录 N-1日08:00 ~ N日08:00 之间发生/发布的事件

例: 3月19日日报
├── 时间窗口: 2026-03-18 08:00 ~ 2026-03-19 08:00 (24小时)
├── 收录: 3月18日下午的产品更新、3月18日晚间的融资新闻、3月19日凌晨的公告
└── 不收录: 3月18日08:00前的任何内容（属于3月18日日报）
```

### 跨会话恢复协议 (v1.2)
当新会话接力未完成的日报时，**第一个命令必须是resume**：
```bash
python3 scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD
```
读完resume输出后，需要**验证**前序数据的合理性，不能盲目继续。

---

## 流程总览

```
Step 0.5 热点探针 → Step 1 两层搜索 → Step 2 内容生成 → Step 2.5 质量门
       ↓                  ↓                 ↓                  ↓
   锚定当日热点      L1广扫+L2精研      JSON+MD生成       19项检查

→ Step 3 HTML生成 → Step 4 部署 → Step 5 KIM推送 → Step 6 知识沉淀
         ↓               ↓              ↓               ↓
    gen_daily_html   6处联动+Git    预览→确认→发群      P1
```

---

## Step 0.5: 实时热点探针 (P0强制)

### 目标
日报必须以"今天发生了什么"为核心，而非"最近一周什么重要"。

### 执行步骤

1. **获取实时聚合**
   ```
   weixin_search("AI 今天")
   weixin_search("大模型 最新")
   # 小红书搜索（仅当用户要求时执行）
   # xiaohongshu search.sh "AI最新动态"
   ```

2. **识别当日热点**: 提取 Top 3-5 热点关键词

3. **大事件检测**: 
   - 如果Top 5热点中≥3条指向同一事件 → 标记为"大事件日"
   - 启用大事件分流搜索协议（见Step 1）

### ✅ Step 0.5 Checklist
- [ ] 搜索关键词包含日期锚定词（"today"/"今天"/完整日期）
- [ ] ❌ 禁止泛日期搜索如 "AI news March 2026"
- [ ] 识别出3-5个当日热点关键词
- [ ] 判断是否为"大事件日"

---

## Step 1: 两层搜索 (L1→L2)

### L1 广扫 (必做)

**工具**: `search_web` + `weixin_search` + `xiaohongshu search.sh`（小红书仅当用户要求时使用）

**板块搜索关键词**:

| 板块 | 海外关键词 | 国内关键词 |
|------|-----------|-----------|
| 🧠 大模型 | "OpenAI GPT latest news today", "Anthropic Claude update" | "DeepSeek 最新", "智谱 GLM 最新" |
| ⌨️ AI Coding | "Cursor changelog", "Claude Code news today" | "Trae 字节 AI编程", "通义灵码 更新" |
| 📱 AI应用 | "AI application news today", "ChatGPT update" | "kimi 产品更新", "豆包 功能 更新" |
| 🏭 AI行业 | "AI startup funding today", "AI company valuation" | "AI 融资 中国 2026" |
| 🔄 企业转型 | "enterprise AI transformation" | "企业 AI 转型 案例" |

### 微信公众号搜索4步法 (v5.0 — 必做)

| Step | 做什么 | 解决什么 |
|------|--------|---------|
| **Step 1 账号搜索** | 搜L1公众号（机器之心/量子位/新智元/宝玉） | 覆盖已知优质账号 |
| **Step 2 话题搜索** | 从海外热词提取2-3个中文搜索词 | **发现追踪名单外的好文** |
| **Step 3 质量筛选** | 有独到视角、非简单翻译 | 保证纳入的是好文章 |
| **Step 4 自检** | meta.data_sources如实记录 | 门控可验证 |

**话题搜索关键词映射**:
```
海外热词 "GTC 2026"        → weixin_search("英伟达 GTC 深度")
海外热词 "Claude Marketplace" → weixin_search("Claude 工具市场 解读")
```

### 小红书搜索 (可选 — 仅当用户要求时执行)

> **v9.8变更**: 小红书搜索从P0强制改为可选，默认不执行。仅当用户明确要求"搜索小红书"或"包含小红书"时才执行。

```bash
# 仅当用户要求时执行:
cd /path/to/xiaohongshu/scripts
./search.sh "AI最新动态"
./search.sh "大模型 今天"
./search.sh "{当日热点关键词}"
```

**要求**: 如用户要求搜索小红书，则至少1条小红书来源进入日报

### 大事件分流搜索 (仅大事件日启用)

当Step 0.5标记为"大事件日"时：
1. **Phase 1**: 大事件搜索 — 该事件最多占4条新闻
2. **Phase 2**: 独立板块搜索 — 对每个板块用排除关键词独立搜索
   - 例: GTC日，AI Coding搜 `"Cursor OR Copilot -GTC -NVIDIA"`
3. **Phase 3**: 小红书+微信照常执行，不可跳过
4. **Phase 4**: 板块均衡自检 — 5个板块各至少1条

### ✅ Step 1 Checklist
- [ ] 海外搜索完成（每板块1-2次）
- [ ] 国内搜索完成（独立执行，非翻译海外结果）
- [ ] 微信搜索完成（账号搜索+话题搜索，全局≤10次）
- [ ] 小红书搜索完成（**仅当用户要求时**，≥1条入报）
- [ ] 如为大事件日，完成分流搜索
- [ ] 标记完成：`python3 scripts/ai_daily_orchestrator.py complete --step 1 --context "搜索概要"`

---

## Step 2: 内容生成 (JSON+MD)

> **v9.8优化**: Step 2 显式分为 3 个子任务，降低单步工作量、便于定位失败环节：
> - **Step 2a — 新闻筛选与分类**: 从搜索结果中筛选候选新闻，纯文本列表形式，不写 JSON
> - **Step 2b — 链接处理与验证**: 处理封闭平台链接决策树，标注每条链接的最终 URL
> - **Step 2c — JSON 组装**: 基于已验证的候选列表按字段模板填写完整 JSON + MD
>
> 好处: 2a 失败无需重做 2b/2c 的链接处理结果；URL 预检（Step 2.7）可在 2b 后立即执行。

### JSON必填字段 (P0 — v6.0明确)

```json
{
  "coverage": { "overseas": N, "china": M },
  "overview": [...],           // 5个板块的今日总览
  "heat_trend": {...},         // 热度趋势分析
  "tabs": [...],               // 5个板块新闻
  "data_snapshot": [...],      // 数据速览表格
  "watch_list": [...],         // 观察名单
  "references": [...],         // 参考资料
  "capability_update": "...",  // ⭐ 林克自述 (P0必填 — v6.0新增)
  "meta": {
    "date": "YYYY-MM-DD",
    "time_window": "N-1日08:00 ~ N日08:00",
    "data_sources": {
      "overseas_search": N,
      "weixin_search": M,
      "xiaohongshu": K,        // 可选，仅当用户要求时才需≥1
      "weixin_direct_cite": L  // ⭐ 必须≥2 (P0 — v9.1)
    }
  }
}
```

### 林克自述 (capability_update) 规范

**必填内容**（每期选1-2个）:
- 当日最重要的洞察/信号
- 林克对趋势的个人视角解读
- PS彩蛋（可选，带自嘲或幽默）

**示例**:
```
🤖 **林克自述**

今天的核心信号是GPT-5.4发布仅3天就被Claude超越——大模型竞争从月度迭代进入周度竞争周期。

对开发者来说，这意味着"选边站"越来越难，"多模型策略"成为刚需。

PS: 模型发布速度比我写日报还快，再这样下去我得考虑让AI帮我写日报了... 等等，我就是AI 🤔
```

### 板块分类规则

| 板块 | 边界 | 典型内容 |
|------|------|---------|
| 🧠 大模型 | 基础模型能力、训练技术 | GPT-5.4能力、DeepSeek发布 |
| ⌨️ AI Coding | 编程工具、IDE、代码助手 | Cursor更新、Claude Code |
| 📱 AI应用 | Agent应用、用户端产品 | ChatGPT周活、OpenClaw |
| 🏭 AI行业 | 投融资、政策、市场格局 | OpenAI估值、VC投资 |
| 🔄 企业转型 | 企业AI落地、提效案例 | 企业AI转型案例 |

### 链接质量三角 (P0)

```
         可达性
          /\
         /  \
        /    \
       /      \
      /________\
   新鲜度    权威性

三者必须同时满足，缺一不可。
```

### 封闭平台链接决策树

```
微信公众号来源:
  ├─ Step A: 搜索公开转载 (36kr/huxiu)
  │     └─ 找到 → 使用转载链接
  ├─ Step B: 使用搜狗搜索URL
  │     └─ weixin.sogou.com/weixin?type=2&query={标题}
  └─ Step C: 不放链接
        └─ url=""，title写准确，source标注(微信)

小红书来源:
  └─ 使用 explore/<noteId> 永久链接

⛔ 绝对禁止:
  - mp.weixin.qq.com/s?src=11&timestamp=... (临时URL)
  - weixin.sogou.com/link?url=... (跳转链接)
  - 首页/通用页凑数
  - 编造URL
```

### 地区分类规则
- **海外**: 总部在海外的公司/产品
- **国内**: 总部在中国的公司/产品
- **微信/小红书来源 → 默认放国内区域**

### ✅ Step 2 Checklist
- [ ] JSON包含所有必填字段
- [ ] `capability_update` 已填写（林克自述）
- [ ] `meta.data_sources.xiaohongshu` ≥ 1（仅当用户要求搜索小红书时）
- [ ] `meta.data_sources.weixin_direct_cite` ≥ 2
- [ ] 5个板块各有新闻（均衡分布）
- [ ] 所有新闻在时间窗口内
- [ ] 微信来源正确放入国内区域
- [ ] 链接无占位符(#)，无封闭平台临时链接
- [ ] 标记完成：`python3 scripts/ai_daily_orchestrator.py complete --step 2 --context "N条新闻(海外X/国内Y)，5板块均衡"`

---

## Step 2.5: 质量门验证 (19项检查)

### 执行命令
```bash
python3 scripts/daily_quality_gate.py YYYY-MM-DD
```

### 19项检查清单

| # | 检查项 | 级别 | 说明 |
|---|--------|------|------|
| 1 | JSON文件存在 | ERROR | - |
| 2 | 中文引号检测 | ERROR | 可修复 |
| 3 | 链接有效性+URL抽检 | ERROR | 可修复 |
| 4 | 内容非空 | ERROR | - |
| 5 | 板块均衡 | ERROR | 5个tab每个至少有内容 |
| 6 | 内容量 | WARNING | 防修复缩水 |
| 7 | 时效性验证 | ERROR | N-1日08:00~N日08:00窗口 |
| 8 | 日期篡改检测 | ERROR | 快照对比+可疑模式 |
| 9 | 封闭平台链接合规 | ERROR | 禁mp.weixin+禁搜狗跳转 |
| 10 | 小红书noteId真实性 | ERROR | ObjectId时间戳验证 |
| 11 | 板块分类验证 | ERROR | v9.1升级 |
| 12 | 地区分类验证 | ERROR | v9.1升级 |
| 13 | 跨天去重 | WARNING | - |
| 14 | 信息源多样性 | ERROR | 微信≥2+小红书≥1+集中度≤40% |
| 15 | HTML链接规范 | ERROR | target=_blank |
| 16 | MD/HTML文件存在 | ERROR | - |
| 17 | 6处联动更新 | ERROR | 可修复 |
| 18 | 外部版同步 | ERROR | 可修复 |
| 19 | **capability_update存在** | ERROR | **v6.0新增** |

### 修复策略三原则

| 策略 | 做法 | 判定 |
|------|------|------|
| **删减型** | 删除不合格内容 | ❌ 禁止 |
| **绕过型** | 修改数据使其"通过" | ⛔ 红线 |
| **替换型** | 重新搜索合格内容替换 | ✅ 正确 |

**类比**: 病人发烧39°C，给他敷冰块降到35°C——症状消失了，但病人快冻死了。正确做法是找病因对症下药。

### ✅ Step 2.5 Checklist
- [ ] 运行 `daily_quality_gate.py`
- [ ] 所有ERROR级别检查通过
- [ ] 如有失败，回到对应步骤修复（不是修改数据绕过）
- [ ] 修复后检查副作用（新闻条数下降>30%需暂停）

---

## Step 3: HTML生成

### 执行命令
```bash
python3 scripts/gen_daily_html.py YYYY-MM-DD
```

### 输出文件
```
01-daily-reports/YYYY-MM/
├── YYYY-MM-DD.md          # Markdown源文件
├── YYYY-MM-DD-v3.html     # HTML渲染版
└── YYYY-MM-DD.html        # 跳转页

data/
└── daily-content-YYYY-MM-DD.json  # KIM推送数据源
```

### ✅ Step 3 Checklist
- [ ] HTML生成无报错
- [ ] 本地预览页面渲染正常
- [ ] 5个板块Tab都有内容
- [ ] 标记完成：`python3 scripts/ai_daily_orchestrator.py complete --step 3`

---

## Step 4: 部署 (6处联动)

### 必须更新的6个位置

| # | 位置 | 说明 |
|---|------|------|
| 1 | `01-daily-reports/YYYY-MM/YYYY-MM-DD.md` | 源文件 |
| 2 | `01-daily-reports/YYYY-MM/YYYY-MM-DD-v3.html` | HTML版 |
| 3 | `01-daily-reports/YYYY-MM/YYYY-MM-DD.html` | 跳转页 |
| 4 | `01-daily-reports/index.html` | 列表+统计 |
| 5 | `index.html` | 首页日历数据 |
| 6 | `data/daily-content-*.json` | KIM数据源 |

### 一键部署
```bash
# 推荐使用orchestrator finalize（含质量门）
python3 scripts/ai_daily_orchestrator.py finalize --fix

# 或手动部署（需先通过质量门）
./scripts/deploy_daily.sh YYYY-MM-DD
```

### Git提交
```bash
git add -A
git commit -m "feat: AI日报 YYYY-MM-DD

内容概要:
- 大模型: ...
- AI Coding: ...
- ...

数据统计: N条新闻 (海外X/国内Y)"
git push origin main
```

### ✅ Step 4 Checklist
- [ ] 6处联动全部更新
- [ ] Git commit + push 完成
- [ ] GitHub Pages部署成功（可能需等待1-2分钟）
- [ ] 标记完成：`python3 scripts/ai_daily_orchestrator.py complete --step 4`

---

## Step 5: KIM推送 (⚡P0 — 结构性约束)

### ❌ 禁止（P0硬性约束）
- ❌ **禁止手写卡片**: 不得用write_to_file创建临时推送脚本或编写纯文本消息冒充卡片
- ❌ **禁止简化卡片**: 不得省略热度趋势、深度聚焦、林克自述、双按钮
- ❌ **禁止重复发送**: 只需调用一次
- ❌ **禁止纯文本推送**: 必须使用 mixCard 卡片，不得用普通 message 代替

### 推送路径（Work模式唯一路径）

> ⚠️ **Work模式说明**: 运行环境无 KIM_APP_KEY/SECRET_KEY 环境变量，旧版直连 KIM API（路径B）**不可用**。必须使用路径 A。

#### 路径 A（唯一可用）: mixCard 通过 message 工具发送

```bash
# 1. 生成 mixCard JSON（推荐用统一生成器）
python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary

# 2. 读取 card.json + summary，作为 message 工具的参数
#    Agent 调用:
#    message(
#        channel="kim",
#        target="username:shenlang",
#        kimMixCard=<card.json 中 card 字段的 JSON 对象>,
#        message=<card.json 中 summary 字段>
#    )
```

> 旧版脚本 `build_daily_mixcard.py` 和 `send_ai_daily.py` 已被统一脚本 `build_insight_mixcard.py` 替代，不再推荐使用。

### ⚠️ 卡片结构锚定（两路径必须一致）
卡片必须包含以下 blocks，顺序不得颠倒：
1. `header` — 标题 "📡 AI 日报（日期，周X）"
2. `subtitle` — "🌍 海外X条 · 🇨🇳 国内Y条 | 五大板块..."
3. `heat` — 🔥 热度趋势（Top 5-6，rank icons + 趋势 icons + signal）
4. `sec1~sec5` — 5 板块（🧠大模型 / ⌨️AI Coding / 📱AI 应用 / 🏭AI 行业 / 🔄企业转型），每板块含：
   - 📰 动态（海外 Top 3 + 国内 Top 2，markdown 链接格式）
   - 💡 深度聚焦（title + summary + 关键判断）
5. `capability` — 🤖 林克自述
6. `footer` — "*林克（沈浪的AI分身）· AI洞察*"
7. `buttons` — 双按钮（📄 查看完整日报 + 💡 了解AI洞察项目）
8. 各 block 之间用 `divider` 分隔

config: `{"forward": true, "forwardType": 3, "wideSelfAdaptive": true}`, `updateMulti: 1`

### 推送范围说明
| 类型 | 推送范围 | 备注 |
|------|---------|------|
| AI日报 | shenlang + 所有活跃订阅者 | 读取 `data/subscribers.json`，逐一私发 MixCard |
| AI周报 | 所有群 | 周报才群发 |

### 订阅者推送流程（Step 5.5 — 日报专属）
> 订阅数据存储在 `data/subscribers.json`，由 MyFlicker 通过 KIM 消息自动管理。

```bash
# 1. 读取订阅列表
cat data/subscribers.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
active = [s for s in data['subscribers'] if s['is_active'] and s['username'] != 'shenlang']
for s in active:
    print(f'{s[\"username\"]}|{s.get(\"kwaiUserId\", \"\")}')
"
# 2. 对每个订阅者，使用 message 工具发送同一份 MixCard（复用 Step 5 生成的 card.json）
#    message(channel="kim", target="username:XXX", kimMixCard=<card>, message=<summary>)
# 3. 记录推送结果
```

### ✅ Step 5 Checklist
- [ ] 使用路径 A（统一生成器 build_insight_mixcard.py）
- [ ] 生成 mixCard JSON → 通过 message + kimMixCard 发送
- [ ] 在 KIM 中确认收到卡片，**验证包含热度趋势+5板块+深度聚焦+林克自述+双按钮**
- [ ] 标记完成：`python3 scripts/ai_daily_orchestrator.py complete --step 5`

---

## Step 6: 知识沉淀 (P1)

从 🔴 重要资讯中按板块分流沉淀:
- 大模型 → `04-knowledge-base/01-models/`
- AI Coding → `04-knowledge-base/02-agents/`
- AI行业 → `04-knowledge-base/03-ai-companies/`
- 企业转型 → `04-knowledge-base/04-enterprise-ai/`

---

## 完成摘要 (P0强制输出)

每次日报完成后必须输出:

```markdown
| 步骤 | 状态 |
|------|------|
| 搜索调研 | ✅ 海外+国内独立搜索, 微信×N次, 小红书×M次 |
| 内容生成 | ✅ 5板块×N条, 国内≥3条, 林克自述已填写 |
| 质量验证 | ✅ 19项检查通过 |
| HTML生成 | ✅ MD+HTML+JSON |
| 部署更新 | ✅ 6处联动完成 |
| KIM推送 | ✅ 预览确认 → 正式发群 |
| Git提交 | ✅ 已push |

📄 日报: https://xiaoxiong20260206.github.io/ai-insight/01-daily-reports/YYYY-MM/YYYY-MM-DD.html
```

---

## 附录A: 常见错误与教训索引

| 错误类型 | 经验编号 | 简述 |
|---------|---------|------|
| 删减型修复 | 经验41 | 修复时删除内容导致缩水，应替换而非删除 |
| 数据伪造 | 经验36 | 编造URL/修改日期绕过检查=P0红线 |
| 大事件隧道视野 | v9.0 | GTC主导导致AI Coding 0条，需分流搜索 |
| 林克自述缺失 | v6.0 | capability_update字段遗漏 |
| 微信直引不足 | v9.1 | 交叉引用≠直接引用，需话题搜索补充 |
| 小红书跳过 | v9.1 | 小红书搜索是P0必做，不是可选 |

详细教训记录见 `lessons-learned.md`

---

## 附录B: 脚本速查

| 脚本 | 用途 |
|------|------|
| `ai_daily_orchestrator.py status` | 查看当前进度 |
| `ai_daily_orchestrator.py complete --step N` | 标记步骤完成 |
| `ai_daily_orchestrator.py finalize --fix` | 质量门+部署 |
| `daily_quality_gate.py YYYY-MM-DD` | 运行19项检查 |
| `gen_daily_html.py YYYY-MM-DD` | 生成HTML |
| `build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json` | 生成mixCard JSON |
| `deploy_daily.sh YYYY-MM-DD` | 一键部署 |
