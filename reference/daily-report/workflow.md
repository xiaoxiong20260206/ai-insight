# AI日报执行流程 (v7.0 精简版)

> **版本**: v7.0 (2026-05-11: 精简版)
> **原则**: 本文件只写"做什么→调用什么→看什么输出"。执行细节由脚本自动处理。
> **⚠️ 生成任何输出前，先读 `reference/output-format-spec.md`（HTML/卡片/Doc公共规范）**

---

## ⚠️ 执行前必读（2条）

1. **续接必须先resume**: `python3 scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD`
2. **环境检查**: `ls user-skills/sl-ai-insight/.git/HEAD && ssh -o ConnectTimeout=5 -T git@github.com`

---

## 流程总览

```
Step 1: 搜索调研 → orchestrator complete --step 1
Step 2: 内容生成 → orchestrator complete --step 2
Step 3+4: finalize → orchestrator finalize（一键命令，内部自动执行5个子步骤）
Step 5: KIM推送 → build_insight_mixcard.py → message(kimMixCard)
```

---

## Step 0.5: 实时热点探针

搜索当日AI热点，识别 Top 3-5 热点关键词。**时间窗口**: N日日报 = N-1日08:00 ~ N日08:00。

搜索关键词必须包含日期锚定词（"today"/"今天"/完整日期），禁止泛日期搜索。

---

## Step 1: 两层搜索 (L1→L2)

| 板块 | 海外关键词 | 国内关键词 |
|------|-----------|-----------|
| 🧠 大模型 | "OpenAI GPT latest news today" | "DeepSeek 最新" |
| ⌨️ AI Coding | "Cursor changelog", "Claude Code news" | "Trae 字节 AI编程" |
| 📱 AI应用 | "AI application news today" | "kimi 产品更新" |
| 🏭 AI行业 | "AI startup funding today" | "AI 融资 中国 2026" |
| 🔄 企业转型 | "enterprise AI transformation" | "企业 AI 转型 案例" |

微信公众号搜索：先账号搜索（机器之心/量子位/新智元/宝玉），再话题搜索。

完成标记:
```bash
python3 scripts/ai_daily_orchestrator.py complete --step 1 --context "搜索N个源; 热点: ...; 选定N条(海外N/国内N)"
```

---

## Step 2: 内容生成

生成 `data/daily-content-YYYY-MM-DD.json` (JSON数据) + `01-daily-reports/YYYY-MM/YYYY-MM-DD.md` (Markdown)。

**JSON必要字段**: tabs(5个板块各含news+deep_focus+pattern_insight_html) + overview + heat_trend + coverage + watch_list

完成标记:
```bash
python3 scripts/ai_daily_orchestrator.py complete --step 2 --context "N条(海外N/国内N), N板块; 微信N条"
```

完成后orchestrator自动执行URL抽检(Step 2.7)。

---

## Step 3+4: Finalize（一键命令）

```bash
python3 scripts/ai_daily_orchestrator.py finalize --date YYYY-MM-DD
```

finalize内部自动执行：
1. URL抽检 → 2. 质量门(硬性阻断/软性警告) → 3. HTML生成+自校验 → 4. 首页更新 → 5. 部署+外部同步+Pages验证

**质量门分级**:
- ❌ 硬性失败（板块缺失/JSON结构错/HTML空壳）= 阻断，必须回到Step 1/2重做
- ⚠️ 软性失败（搜狗URL占比/链接格式/覆盖度略低）= 警告不阻断

**finalize失败时**: 检查错误信息 → 区分硬性/软性 → 硬性重做/软性可继续push

---

## Step 5: KIM推送

```bash
# 1. 生成mixCard（脚本自带6锚点校验+kimMd格式校验+{{message}}扫描）
python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary

# 2. 读取卡片JSON，发送
# message(channel=kim, kimMixCard=<card>, target="username:shenlang03")

# 3. 标记完成
python3 scripts/ai_daily_orchestrator.py complete --step 5
```

**推送范围**: 日报只私发订阅者，❌禁止群发。

---

## 搜索策略优化（2026-05-11新增）

### 问题：搜狗链接占比44%超阈值、URL截断、source篡改

### 优化措施:
1. **精准搜索优先**: 具体产品名+日期锚定 > 泛搜索
2. **微信账号搜索为主**: 机器之心/量子位/新智元/宝玉 > 话题搜索
3. **搜狗URL占比硬限制≤30%**: 超过则替换为微信公众号原文链接
4. **同报URL去重**: JSON生成后自动检测同一URL出现多次，保留一条
5. **URL可达性校验**: orchestrator Step 2.7自动抽检3个URL

---

## 失败自修复原则

1. 任何步骤失败 = 立即尝试修复，不停下来汇报
2. 修复路径优先级: 环境问题→直接替换重试; 数据问题→回步骤重做; 推送问题→切换路径
3. 最多重试3次
4. 完成优先于完美
5. fail loud, don't fail silent

---

_更新于 2026-05-11 · v7.0 · 精简版，529行→核心流程_