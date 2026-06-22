# AI周报速查卡（v1.0 — 2026-06-22）

> cron agent用这个文件替代完整SKILL.md+output-format-spec.md+weekly-report.md三件套。
> 从~60KB→5KB，节省~55K input tokens/次。

## P0红线速查（9条致命项）

| # | 红线 | 一句话 |
|---|------|--------|
| 1 | uv run | python/python3 = P0违规 |
| 2 | MixCard脚本生成 | `build_insight_mixcard.py weekly`，禁止手写 |
| 3 | {{message}}禁令 | 卡片内容直接写完整文本 |
| 4 | HTML从JSON生成 | `gen_weekly_html.py`，禁止手拼HTML |
| 5 | JSON先validate | `gen_weekly_json.py --validate` |
| 6 | HTML≥50KB | `wc -c` 验证 |
| 7 | 搜索≤8次 | 同日报#18d |
| 8 | target必带 | message send带target={{OWNER_KIM_USERNAME}} |
| 9 | 三步部署 | git push + sync_to_external + frontend-cloud |

## 6步流程

```
Step 1: 采集本周日报数据（从daily-content JSON文件读取，不是重新搜索）
Step 2: 生成周报JSON → gen_weekly_json.py + --validate
Step 3: 生成周报HTML → gen_weekly_html.py
Step 4: 更新首页（tracking_section.html+最新周报链接）
Step 5: 三步部署
  5a: git add -A && git commit -m "📊 AI周报 YYYY-WXX" && git push
  5b: uv run scripts/sync_to_external.py --full --verify
  5c: cd public && npx -y --registry https://npm.corp.kuaishou.com @codeflicker/frontend-cloud-cli@latest deploy && cd ..
Step 5.5: 输出4个交付链接
Step 6: MixCard私发{{OWNER_KIM_USERNAME}} + token记录
```

## 关键命令

```bash
# Step 2: JSON生成+校验
uv run scripts/gen_weekly_json.py YYYY WXX --validate

# Step 3: HTML生成
uv run scripts/gen_weekly_html.py YYYY WXX

# Step 5b: 外部版同步
uv run scripts/sync_to_external.py --full --verify

# Step 6: MixCard
uv run scripts/build_insight_mixcard.py weekly --date YYYY-MM-DD --week WXX --output /tmp/card.json --with-summary
message(action=send, channel=kim, target={{OWNER_KIM_USERNAME}}, kimMixCard=<card>, message="")
```

## 交付链接模板

```
内部版：
1. 📄 https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
2. 🏠 https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/
外部版：
3. 📄 https://xiaoxiong20260206.github.io/ai-insight-public/01-daily-reports/YYYY-MM/weekly-YYYY-WXX.html
4. 🏠 https://xiaoxiong20260206.github.io/ai-insight-public/
```

## URL SSoT = scripts/config.py
内部版→frontend-cloud，外部版→GitHub Pages，禁止交叉。禁止手动cp HTML到外部仓库。
