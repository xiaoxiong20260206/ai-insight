# AI日报踩坑经验（Lessons Learned）

> **⚠️ 权威归档在顶层**: `reference/lessons-learned.md`（733行，v1.9，114条全量归档）。本文件是日报子集精简版。
> 每次重大问题修复后追加记录。按日期索引，每条包含：问题→根因→修复→举一反三。

---

## 2026-05-09: uv 命令在 isolated session 中找不到

**问题**: cron job 在 isolated session 里执行时，`uv` 命令找不到（PATH 缺少 `~/.local/bin`），导致 AI日报连续失败。

**根因**: isolated session 的 PATH 不包含用户级安装路径。容器环境每次重建后 `uv` 也可能丢失。

**修复**: cron payload 增加环境自检+自安装逻辑：
```bash
export PATH="$HOME/.local/bin:$PATH"
which uv || (curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH")
```

**举一反三**: 所有依赖用户级工具（uv/python3/npm等）的 cron job，都必须包含环境自检。不要假设 isolated session 的 PATH 包含任何特定路径。

---

## 2026-05-09: 域账号变更未全链路同步

**问题**: KIM域账号从 shenlang 改为 shenlang03，但 10 个 cron job、subscribers.json、USER.md 都还在用旧账号，日报推送到旧账号无法送达。

**根因**: 域账号变更时，没有检查所有引用点。cron delivery.to、subscribers 数据文件、USER.md、cron payload 中的硬编码用户名都需要同步。

**修复**: 逐一更新 10 个 cron delivery.to、subscribers.json、USER.md。

**举一反三**: 任何身份/账号变更（域账号、token、URL、仓库名），必须执行全链路扫描——grep 所有相关文件和配置，逐一更新。建议建立"变更清单"模板。

---

## 2026-05-11: MixCard 缺少 heat block（数据契约不一致）

**问题**: `build_insight_mixcard.py` 生成的卡片缺少热度趋势 block。脚本读 `heat_trend.topics`，但 cron session 生成的 JSON 数据只有 `heat_trend.top_items`。

**根因**: 数据生产方（cron session）和数据消费方（mixcard脚本）之间没有 schema 约定，字段名各自理解，导致兼容性断裂。

**修复**: 脚本改为兼容两种格式：优先读 `top_items`，fallback 到 `topics`；同时兼容 `title`/`name` 和 `trend`/`trend_class` 字段名差异。

**举一反三**: **所有脚本间数据传递必须有明确的数据契约**。当 JSON 结构有变更时，必须同步更新消费方脚本。最佳实践：在 config.py 或独立 schema 文件中定义字段映射，而非在脚本中硬编码字段名。

---

## 2026-05-11: 纯文本推送违反 P0 红线

**问题**: 因 MixCard 参数类型问题（kimMixCard 需要传 JSON object），改发纯文本消息，违反 workflow "禁止纯文本推送"的 P0 红线。

**根因**: 遇到技术障碍时急于送达，降级到更简单的方案。但降级方案违反了硬性约束。

**修复**: 坚持用 MixCard 卡片推送，通过手动构建完整 JSON object 解决参数类型问题。

**举一反三**: **遇到技术困难时，宁可延迟送达，不可降级到违反 P0/P1 约束的方案**。P0 红线是底线，不是"尽量满足"的建议。如果 MixCard 推送失败，应该排查原因并修复，而不是换成纯文本。

---

## 2026-05-11: cron session 搜索质量差（搜狗依赖44%+URL截断+source篡改）

**问题**: cron 自动生成的日报存在三类搜索质量问题：
1. 搜狗微信链接占比 44%（超过40%阈值）
2. 搜狗 URL 的 query 参数截断，实际无法访问原文章
3. source 字段被篡改（DeepLearning.AI→Mistral官方，伟略达→ISHIR）

**根因**: cron session 的搜索策略过度依赖搜狗微信搜索作为国内新闻源，没有强制要求真实文章 URL。source 篡改可能是 session 上下文压缩后的"优化"行为。

**修复**: 手动修复 URL 前缀、source 字段和地区分类。结构性问题（搜狗依赖）需改进搜索策略。

**举一反三**: 
1. **搜狗搜索URL只作为Step B兜底**（workflow已有规定但cron session未严格执行），优先找36kr/huxiu等公开转载平台
2. **搜索结果必须包含真实可访问的URL**，搜狗搜索URL仅作为"找不到公开转载时的最后手段"
3. **cron session缺乏质量验收环节**——session自生成+自推送+自标记完成，没有外部校验。需要：推送后由主session验证MixCard结构完整性

---

## 2026-05-11: cron 推送可观测性盲区

**问题**: cron job 执行完毕显示 `delivered=true`，但用户实际没收到 MixCard 卡片。delivery status 只反映"摘要推送"，不反映"session内部的MixCard推送结果"。

**根因**: cron delivery 机制和 session 内部 message 推送是两个独立的通道。delivery announce 推的是执行摘要，MixCard 推送是 session 内部的 message 调用。两者没有关联。

**修复**: 主session手动接力推送MixCard卡片。

**举一反三**: **自动化推送必须有端到端验证机制**：
1. cron session 推送 MixCard 后，应通过 message 工具发送一条"推送确认"消息给目标用户
2. 或在 workflow 中增加 Step 5.1："推送后5分钟，验证目标用户是否收到卡片（请求确认）"
3. 主session收到cron delivery announce后，应主动检查推送结果而非仅看 status

---

## 2026-05-26: MixCard双层JSON格式导致空消息（P0）

**问题**: cron session执行AI日报后，用户收到空消息。手动重发也收到空消息。

**根因**: `build_insight_mixcard.py`使用`--with-summary`参数时，输出格式为`{"card": {...}, "summary": "..."}`双层结构。但`message`工具的`kimMixCard`参数需要inner card格式（`config+blocks`直接在顶层）。传了双层结构后，KIM在JSON中找不到`blocks`字段（因为`blocks`在`card.blocks`而非顶层），渲染为空。

**验证**: 第三次发送时直接传inner card（去掉外层`card`键），卡片正常渲染。

**修复**:
1. `build_insight_mixcard.py`: 输出格式改为inner card（`config+updateMulti+blocks`直接在顶层），summary信息打印到stdout而非嵌入JSON
2. `ai_daily_orchestrator.py`: 去除重复代码，添加message参数必须传空字符串的警告
3. workflow.md/p0-redlines.md/SKILL.md: 添加`message=""`参数规范和inner card格式说明

**举一反三**: 
1. **所有MixCard推送场景必须使用inner card格式** — `kimMixCard`参数直接传`{config, blocks, updateMulti}`，不能传`{card: {...}}`
2. **脚本输出格式和消费方格式必须对齐** — 脚本输出的JSON格式必须和`message`工具的`kimMixCard`参数格式完全一致，不能有中间转换层
3. **空消息=格式问题而非内容问题** — MixCard内容完整但格式不对（双层→单层），KIM会渲染为空而非报错。这是最危险的silent failure

---

_更新于 2026-05-26 | v1.1 | 7条经验_