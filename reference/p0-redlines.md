# P0红线 — 精简版（v12.0 · 2026-05-11）

> **核心原则**：只有6条需要Agent自觉遵守。其余校验已内置到脚本。
> **旧版19条红线归档** → `reference/p0-redlines-archive-v11.md`

---

## 🔴 红线1：续接必须先 resume（无例外）

```bash
python3 scripts/ai_daily_orchestrator.py resume --date YYYY-MM-DD
```
读完resume输出后，**验证**前序数据的合理性，不能盲目继续。

## 🔴 红线2：KIM卡片必须用脚本生成（禁止手写）

```bash
python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
# 然后读取 card.json，用 message(channel=kim, kimMixCard=<card>) 发送
```
脚本自带校验：6锚点完整性 + kimMd格式 + {{message}}扫描 + URL格式。手写=必错=空卡片。

## 🔴 红线3：mixCard只推一次（禁止重复）

preview和正式推送是同一个命令。不要执行两次。

## 🔴 红线4：质量门硬性失败=重做（禁止绕过）

| 失败类型 | 处理方式 |
|---------|---------|
| **硬性失败**（板块缺失、JSON结构错、HTML空壳） | 回到对应步骤重做，禁止修改数据 |
| **软性失败**（搜狗URL占比、微信链接格式、覆盖度略低） | 警告不阻断，继续部署 |

## 🔴 红线5：环境前置检查（每次执行必做）

```bash
ls user-skills/sl-ai-insight/.git/HEAD || echo "PROJECT_MISSING"
ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | grep "successfully" || echo "GIT_UNREACHABLE"
ls ~/.ssh/id_ed25519 || echo "SSH_KEY_MISSING"
ls ~/.git-credentials || echo "CREDENTIALS_MISSING"
```
任何项MISSING = 先恢复环境再执行。恢复流程见 HEARTBEAT.md。

## 🔴 红线6：fail loud, don't fail silent

找不到文件时报错退出，禁止静默降级为空内容兜底卡片。
空卡片比报错更危险——用户看到空卡片会以为内容真没了，报错反而能触发修复。

---

## 📋 已转移到脚本自动校验的规则（Agent不需要检查）

| 旧红线编号 | 内容 | 现在由谁校验 |
|-----------|------|-------------|
| #2 KIM卡片必须用脚本 | 手写JSON格式必错 | `build_insight_mixcard.py` 6锚点+kimMd校验 |
| #3 禁止纯文本降级 | mixCard结构完整性 | `build_insight_mixcard.py` 锚点校验 |
| #7 6处联动 | 首页+索引+public+外部 | `update_homepage.py` + `deploy_daily.sh` + `sync_to_external.py` |
| #8 禁止raw cp | 脱敏脚本 | `sync_to_public.py` + `sync_to_external.py` |
| #15 容器重建恢复 | 环境检查 | 红线5 + HEARTBEAT.md |
| #16 SSH优先 | Git操作 | `deploy_daily.sh` + orchestrator |
| #17 失败自修复 | 重试机制 | orchestrator finalize 自动重试 |
| #18 Work模式唯一路径 | mixCard路径 | orchestrator cmd_push |
| #19 卡片结构锚定 | 6锚点 | `build_insight_mixcard.py` ANCHOR_NAMES |

---

## 推送范围

| 类型 | 推送范围 | 禁止 |
|------|---------|------|
| 日报 | 私发订阅者 | ❌ 禁止群发 |
| 周报 | 发所有群 | 正常 |

KIM群聊必须用 `space:<groupId>` 格式，禁止裸传 groupId。

---

_更新于 2026-05-11 · v12.0 · 从19条精简到6条核心红线_