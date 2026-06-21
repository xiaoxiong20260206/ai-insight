# AI日报速查卡（v1.0 — 2026-06-22）

> cron agent用这个文件替代完整SKILL.md+workflow.md+output-format-spec.md三件套。
> 从46KB→5KB，节省~40K input tokens/次。

## P0红线速查（8条致命项）

| # | 红线 | 一句话 |
|---|------|--------|
| 1 | uv run | python/python3 = P0违规 |
| 2 | 搜索≤8次 | 总计8次，每板块海外1+微信1（#18d） |
| 3 | MixCard脚本生成 | `build_insight_mixcard.py`，禁止手写 |
| 4 | {{message}}禁令 | 卡片内容直接写完整文本 |
| 5 | 6处联动 | JSON+MD+HTML+首页+MixCard+外部版 |
| 6 | quality gate | 硬性失败=重做，软性=不阻断 |
| 7 | target必带 | 任何message send都必须带target=username:XXX |
| 8 | 禁止write覆盖token | 必须用`append_token_record.py`追加 |

## 6步流程

```
Step 0:   mkdir + 凭据恢复
Step 0.5: 热点探针（≤2次搜索）
Step 1:   搜索调研（≤6次搜索，5板块×1海外+1微信）
Step 2:   内容生成 → daily-content-YYYY-MM-DD.json + .md
Step 3+4: finalize（一键命令，含质量门+HTML+首页+部署）
Step 5:   MixCard → 只发shenlang03，>5人用子agent并行
Step 5.5: 输出4个交付链接（内部×2+外部×2）
```

## 搜索硬限制（P0红线#18d）

- **总计≤8次搜索**（热点探针≤2次 + 板块搜索≤6次）
- **每板块：海外1次 + 微信1次**
- **搜索结果数：--max-results 3**（tavily默认5条，改为3条省~40%搜索token）
- ❌ 超过8次 = P0违规

## 关键命令

```bash
# Step 3+4 一键finalize
uv run scripts/ai_daily_orchestrator.py finalize --date YYYY-MM-DD

# Step 5 MixCard生成+发送
uv run scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
# 发给shenlang03: message(action=send, channel=kim, target=username:shenlang03, kimMixCard=<card>, message="")

# Step 5 外部版同步
uv run scripts/sync_to_external.py --full --verify

# P2 token记录
uv run scripts/append_token_record.py --date YYYY-MM-DD --task "AI洞察日报(cron)" --in IN --out OUT --key "cron:2fc696f4" --note "cron_completion"
```

## 交付链接模板

```
内部版：
1. 📄 https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/YYYY-MM/YYYY-MM-DD.html
2. 🏠 https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/
外部版：
3. 📄 https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/YYYY-MM-DD.html
4. 🏠 https://xiaoxiong20260206.github.io/ai-insight-public/
```

## URL SSoT = scripts/config.py

所有链接从config.py派生，禁止硬编码。内部版→frontend-cloud，外部版→GitHub Pages，禁止交叉。
