# Crawl4AI - 开源LLM友好的网页爬虫

> **知识类型**: 产品概念/基础设施
> **来源**: GitHub、官方文档 (https://github.com/unclecode/crawl4ai, https://docs.crawl4ai.com)
> **更新时间**: 2026-03-05
> **版本**: v1.0

---

## 概述

**Crawl4AI** 是一款开源的、LLM友好的网页爬虫和抓取工具，专为大语言模型、AI Agent和数据管道设计。它能将网页内容转换为干净的、LLM可直接使用的Markdown格式，非常适合RAG（检索增强生成）和Agent应用。

### 关键数据

| 指标 | 数据 |
|------|------|
| **GitHub Stars** | 50,000+ ⭐ (GitHub #1 趋势爬虫) |
| **社区开发者** | 51,000+ |
| **当前版本** | v0.8.0 |
| **开源协议** | Apache 2.0 |
| **创建者** | Unclecode (Hossein) |
| **公司背景** | Kidocode (东南亚最大的青少年科技教育学校) |

### 定位

> "Crawl4AI turns the web into clean, LLM-ready Markdown for RAG, agents, and data pipelines."

Crawl4AI的核心理念是**数据民主化**：
- 完全开源，无需API密钥
- 不强制付费，任何人都可以访问自己的数据
- 高度可配置，满足不同场景需求

---

## 核心特性

### 1. LLM友好输出

| 特性 | 说明 |
|------|------|
| **Clean Markdown** | 生成干净、结构化的Markdown，准确保留格式 |
| **Fit Markdown** | 启发式过滤，去除噪音和无关内容，AI友好处理 |
| **Citations/References** | 将页面链接转换为编号引用列表 |
| **Custom Strategies** | 支持自定义Markdown生成策略 |
| **BM25 Algorithm** | 使用BM25算法提取核心信息，过滤无关内容 |

### 2. 结构化数据提取

| 方式 | 说明 |
|------|------|
| **LLM驱动提取** | 支持所有LLM（开源和商用）进行结构化数据提取 |
| **Chunking策略** | 实现分块（主题、正则、句子级）进行定向内容处理 |
| **Cosine Similarity** | 基于用户查询的相关内容块查找 |
| **CSS/XPath提取** | 快速的基于Schema的数据提取 |
| **Schema定义** | 定义自定义Schema从重复模式中提取结构化JSON |

### 3. 浏览器集成

- **托管浏览器**: 使用用户自有浏览器，避免Bot检测
- **远程浏览器控制**: 连接Chrome DevTools Protocol进行大规模数据提取
- **Browser Profiler**: 创建和管理持久化配置文件
- **Session管理**: 保存浏览器状态用于多步爬取
- **Proxy支持**: 无缝连接代理
- **多浏览器支持**: Chromium, Firefox, WebKit
- **动态视口调整**: 自动调整视口匹配页面内容

### 4. 爬取与抓取

- **媒体支持**: 提取图片、音频、视频
- **动态爬取**: 执行JS并等待异步内容
- **截图**: 爬取时捕获页面截图
- **全面链接提取**: 内部、外部链接和iframe内容
- **可定制Hooks**: 在每个步骤定义钩子自定义爬取行为
- **缓存**: 缓存数据提高速度
- **Lazy Load处理**: 等待图片完全加载
- **全页面扫描**: 模拟滚动加载动态内容

### 5. 部署能力

- **Docker化部署**: 优化的Docker镜像 + FastAPI服务
- **安全认证**: 内置JWT token认证
- **API网关**: 一键部署，安全token认证
- **可扩展架构**: 设计用于大规模生产
- **云部署**: 主流云平台配置

---

## 最新版本亮点 (v0.8.0)

### 崩溃恢复 (Crash Recovery)
```python
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

strategy = BFSDeepCrawlStrategy(
    max_depth=3,
    resume_state=saved_state,  # 从检查点继续
    on_state_change=save_to_redis,  # 每个URL后调用
)
```
- `on_state_change` 回调在每个URL后触发，实现实时状态持久化
- `resume_state` 参数从保存的检查点继续
- JSON可序列化状态，支持Redis/数据库存储
- 支持BFS、DFS、Best-First策略

### 预取模式 (Prefetch Mode)
```python
config = CrawlerRunConfig(prefetch=True)
result = await crawler.arun("https://example.com", config=config)
# 只返回HTML和链接 - 不生成markdown
```
- `prefetch=True` 跳过markdown、提取和媒体处理
- 比完整处理快5-10倍
- 适合两阶段爬取：先发现URL，再选择性处理

### 安全修复 (Docker API)
- Hooks默认禁用 (`CRAWL4AI_HOOKS_ENABLED=false`)
- `file://` URL在API端点被阻止
- `__import__` 从hook执行沙箱中移除

---

## MCP集成

Crawl4AI提供**MCP (Model Context Protocol)** 集成，可直接连接到AI工具：

```yaml
version: '3.8'
services:
  crawl4ai:
    image: unclecode/crawl4ai
    # MCP集成配置
```

这意味着Crawl4AI可以作为MCP Server，为Claude Code、Cursor等AI编程助手提供网页爬取能力。

---

## 使用场景

### 1. RAG管道数据获取
Crawl4AI专为RAG设计，输出干净的Markdown格式，可直接用于向量嵌入和知识库构建。

### 2. AI Agent网页交互
为AI Agent提供网页数据获取能力，支持：
- 信息收集
- 数据提取
- 网页监控

### 3. 数据管道ETL
异步高性能爬取，支持大规模数据采集和处理。

### 4. LLM训练数据准备
将网页内容转换为LLM友好格式，用于训练数据集构建。

---

## 快速开始

### 安装
```bash
pip install -U crawl4ai
crawl4ai-setup  # 设置浏览器
crawl4ai-doctor  # 验证安装
```

### 基本使用
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.example.com",
        )
        print(result.markdown)

asyncio.run(main())
```

### CLI使用
```bash
# 基本爬取输出markdown
crwl https://example.com -o markdown

# 深度爬取BFS策略，最多10页
crwl https://docs.crawl4ai.com --deep-crawl bfs --max-pages 10

# 使用LLM提取
crwl https://example.com/products -q "Extract all product prices"
```

### Docker部署
```bash
docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest

# 访问监控面板: http://localhost:11235/dashboard
# 访问Playground: http://localhost:11235/playground
```

---

## 与Firecrawl对比

| 维度 | Crawl4AI | Firecrawl |
|------|----------|-----------|
| **开源** | 完全开源 Apache 2.0 | 开源但有商业版 |
| **定价** | 免费 | 免费层有限，需付费 |
| **API密钥** | 不需要 | 需要注册获取 |
| **LLM输出** | Markdown优化 | Markdown优化 |
| **自托管** | 支持Docker | 支持但较复杂 |
| **MCP集成** | 支持 | 支持 |
| **Star数** | 50K+ | 较低 |
| **社区** | 活跃Discord | 活跃 |

---

## 创始人背景

**Unclecode (Hossein)**
- Crawl4AI创建者
- Kidocode创始人（东南亚最大的青少年科技与创业学校）
- NLP专业背景，研究生期间专注爬虫研究
- AI咨询师，专注合成数据研究
- Twitter: [@unclecode](https://x.com/unclecode)

### 创建故事
> "2023年，我需要web-to-Markdown功能。所谓的'开源'选项需要账户、API token和$16，而且还不满足需求。我进入turbo anger mode，几天内构建了Crawl4AI，然后它火了。现在它是GitHub上Star数最多的爬虫。"

---

## 为什么开发者选择Crawl4AI

1. **LLM就绪输出**: 智能Markdown，包含标题、表格、代码、引用提示
2. **实践中快速**: 异步浏览器池、缓存、最小跳数
3. **完全控制**: sessions、proxies、cookies、用户脚本、hooks
4. **自适应智能**: 学习站点模式，只探索重要内容
5. **随处部署**: 无需密钥，CLI和Docker，云友好

---

## 追踪价值

### 为什么要追踪
1. **开源Agent基础设施**: Crawl4AI是Agent生态的重要组件，为AI Agent提供网页数据获取能力
2. **LLM工具链**: 与RAG、数据管道深度集成，是AI开发的关键基础设施
3. **活跃发展**: 50K+ Star，持续更新，社区活跃
4. **MCP生态**: 已集成MCP协议，可直接连接到主流AI工具

### 追踪重点
- 新版本功能发布
- 与LLM/Agent框架的集成
- MCP生态发展
- 企业级功能进展
- Cloud API发布

---

## 参考资料

- [GitHub仓库](https://github.com/unclecode/crawl4ai)
- [官方文档](https://docs.crawl4ai.com)
- [Discord社区](https://discord.gg/jP8KfhDhyN)
- [Twitter](https://x.com/crawl4ai)
- [PyPI](https://pypi.org/project/crawl4ai/)

---

*最后更新: 2026-03-05*
