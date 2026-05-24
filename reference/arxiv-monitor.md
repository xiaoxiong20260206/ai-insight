# arXiv 学术论文监控 (v9.3)

基于 OpenClaw 社区 arxiv-watcher 技能理念，为 AI-Insight 增加学术信源覆盖。

## 触发词
"arXiv论文"、"AI学术动态"、"最新论文"、"论文监控"

## 核心能力

自动从 arXiv 获取 AI 相关领域的最新论文，支持：
- **主题过滤**: cs.AI, cs.LG, cs.CL, cs.CV 等
- **关键词过滤**: agent, reasoning, coding, LLM 等
- **相关度排序**: 基于关键词权重自动排序
- **每日/每周摘要**: 生成结构化报告

## 快速执行

```bash
# 获取过去1天的AI论文
uv run scripts/fetch_arxiv.py --days 1

# 获取过去7天论文摘要（适合周报）
uv run scripts/fetch_arxiv.py --days 7 --summary

# 按关键词过滤
uv run scripts/fetch_arxiv.py --keywords "agent" "LLM" "coding"

# 输出JSON格式（供日报系统集成）
uv run scripts/fetch_arxiv.py --days 1 --json --output data/arxiv-daily.json
```

## 与日报集成

日报搜索阶段可选调用 arXiv 监控：
1. **Step 1.5 (可选)**: 执行 `uv run scripts/fetch_arxiv.py --days 1` 查看当日论文
2. 如有高相关度论文（⭐⭐⭐及以上），可纳入日报"AI前沿"板块
3. 论文信源标注为 `arXiv [cs.XX]`

## 监控分类

| 分类 | 含义 | 检查频率 |
|------|------|----------|
| cs.AI | Artificial Intelligence | 每日 |
| cs.LG | Machine Learning | 每日 |
| cs.CL | Computation and Language (NLP) | 每日 |
| cs.CV | Computer Vision | 每周 |
| cs.RO | Robotics | 每周 |