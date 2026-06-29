# AI日报发布前验证用例（v1.0）

> 每次日报 Step 2 完成后、Step 3 finalize 之前执行。全部通过才允许推送给用户和订阅者。
> 验证不通过 → 回到对应 Step 修复 → 重新验证 → 直到全部通过。

---

## 验证时机

```
Step 1 搜索 → Step 2 内容生成 → ⭐ 本验证 → Step 3 finalize → Step 5 推送
```

## 验证方式

由执行 agent 在 Step 2 完成后逐项检查，输出验证报告。硬性项（🔴）任一不通过即阻断；软性项（🟡）不阻断但需记录。

---

## 🔴 硬性验证项（必须全部通过）

### V1. 时间窗口 — 新闻必须在本周期内

| # | 检查项 | 规则 | 方法 |
|---|--------|------|------|
| V1.1 | source 日期在窗口内 | 每条 news 的 source 字段日期 = N-1日 或 N日 | 质量门 `check_date_window` |
| V1.2 | URL 嵌入日期在窗口内 | URL 中的日期比日报日期早 ≤3 天 | 质量门 v13.0 URL 二次验证 |
| V1.3 | 无旧新闻充数 | 禁止把上周/更早的新闻以当期日期写入 | Step 1 原始素材交叉比对 |

**V1.3 执行方法**：Step 2 生成 JSON 后，逐条 news 的 title 前 20 字去 Step 1 搜索结果里匹配。找不到对应来源的条目 → 标记为疑似自增 → 删除。

### V2. URL 真实性 — 每条链接必须可点击

| # | 检查项 | 规则 | 方法 |
|---|--------|------|------|
| V2.1 | 无空 URL | 非微信来源的 news 条目 url 字段不得为空 | `check_link_validity` |
| V2.2 | 无锚点占位符 | URL 不得以 `#coding` `#industry` `#enterprise` 等板块名结尾 | `check_link_validity` v12.0 |
| V2.3 | URL 格式合法 | 必须以 `http://` 或 `https://` 开头 | `check_link_validity` |
| V2.4 | URL 抽检可达 | 随机抽 3 条 URL 做 HEAD 请求，2xx/3xx = 通过 | orchestrator Step 2.7 |

### V3. 微信信源 — 国内新闻必须有公众号直引

| # | 检查项 | 规则 | 方法 |
|---|--------|------|------|
| V3.1 | 微信直引 ≥ 2 条 | 全报至少 2 条 source 包含 `(微信)` 标注 | `check_source_diversity` |

### V4. 内容完整性 — 结构不能缺

| # | 检查项 | 规则 | 方法 |
|---|--------|------|------|
| V4.1 | 5 个板块齐全 | tabs 包含 tab_llm / tab_coding / tab_app / tab_industry / tab_enterprise | `check_content_nonempty` |
| V4.2 | 每板块有新闻 | 每个板块 overseas+china 合计 ≥ 2 条 | `check_content_nonempty` |
| V4.3 | 深度聚焦完整 | 5 个板块的 deep_focus 各含 ≥ 3 段 paragraphs + takeaway | `check_deep_focus` |
| V4.4 | 规律洞察完整 | 5 个板块的 pattern_insight_html 各含 pi-card 结构 | `check_pattern_insight` |
| V4.5 | 林克自述已填 | capability_update 字段非空且 ≥ 100 字 | `check_capability_update` |

### V5. 外部版安全 — 脱敏零泄露

| # | 检查项 | 规则 | 方法 |
|---|--------|------|------|
| V5.1 | 外部版零敏感词 | `ai-insight-public/` 对应日报 HTML 不含 `林克` `沈浪` `AI分身` `MyFlicker` | `sync_to_external.py --verify` |
| V5.2 | 外部版 footer URL 正确 | 外部版日报 footer 指向 `xiaoxiong20260206.github.io` 而非内部版 | `sync_to_external.py` URL 替换校验 |

---

## 🟡 软性验证项（不阻断，但需记录和修复建议）

### V6. 内容质量

| # | 检查项 | 规则 | 说明 |
|---|--------|------|------|
| V6.1 | 总条目 15~25 条 | 海外+国内合计 15~25 条为健康区间 | <15 条说明搜索不够充分 |
| V6.2 | 板块均衡 | 单板块 ≤ 6 条，最低 ≥ 2 条 | 偏差过大说明搜索倾斜 |
| V6.3 | 同报 URL 去重 | 同一 URL 不在同一板块的 news 中出现 2 次 | 跨板块引用（洞察区）不在此限 |
| V6.4 | 分类准确性 | 海外/中国区分类符合公司归属 | DeepSeek→china, OpenAI→overseas |

### V7. 部署验证

| # | 检查项 | 规则 | 说明 |
|---|--------|------|------|
| V7.1 | 内部版可访问 | frontend-cloud 日报 URL 返回 200 | 部署后 curl 验证 |
| V7.2 | 外部版可访问 | GitHub Pages 日报 URL 返回 200 | 部署后 curl 验证 |
| V7.3 | MixCard 投递成功 | deliveryStatus = delivered | 推送后检查 |

---

## 验证报告格式

每次验证输出如下格式：

```
📋 日报验证报告 — 2026-06-29

🔴 硬性项（7/7 通过）
  ✅ V1.1 时间窗口 — 19/19 条在窗口内
  ✅ V1.2 URL嵌入日期 — 0 条超3天
  ✅ V1.3 原始素材比对 — 19/19 条有搜索来源
  ✅ V2.1-2.4 URL真实性 — 0 空/0 锚点/3 抽检全可达
  ✅ V3.1 微信直引 — 4 条（≥2）
  ✅ V4.1-4.5 内容完整性 — 5板块/深度聚焦/规律洞察/自述全部OK
  ✅ V5.1-5.2 外部版安全 — 零敏感词/footer正确

🟡 软性项
  ✅ V6.1 总条目 — 19条（健康）
  ⚠️ V6.2 板块均衡 — 大模型6条（建议≤5）
  ✅ V6.3 同报去重 — 无重复
  ⚠️ V6.4 分类准确性 — DeepSeek V4 已归china ✅

结论：✅ 全部硬性项通过，可以推送
```

---

## 验证不通过的处理

| 失败项 | 处理方式 | 回退到 |
|--------|---------|--------|
| V1.x 时间窗口 | 删除超窗条目 → 从 Step 1 素材补充 | Step 2 |
| V2.x URL 问题 | 搜真实 URL 替换，或删除无来源条目 | Step 2 |
| V3.1 微信不足 | 补搜微信公众号 | Step 1 |
| V4.x 结构缺失 | 补充对应板块内容 | Step 2 |
| V5.x 脱敏失败 | 重新 `sync_to_public.py --full --force` | Step 3 |

**循环上限：3 轮**。3 轮仍不通过 → 暂停推送，向用户报告问题，等用户决定。

---

_版本 v1.0 · 2026-06-29 · 基于质量门 v13.0 + P0 #0 时间窗口铁律_
