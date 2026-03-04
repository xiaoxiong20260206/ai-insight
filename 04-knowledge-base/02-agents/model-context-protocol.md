# Model Context Protocol (MCP) 专题

> **知识类型**: 概念 + 协议规范
> **来源**: Anthropic官方文档、MCP官网、Agentic AI Foundation
> **更新时间**: 2026-03-05
> **版本**: v1.0

---

## 概述

Model Context Protocol (MCP) 是一个开源标准，用于连接AI应用与外部系统。就像USB-C为电子设备提供标准化连接方式一样，MCP为AI应用提供了连接外部系统的标准化方式。

**核心价值**: 替代碎片化的集成方案，用单一协议连接所有数据源和工具。

---

## 核心架构

### 基本概念

```
┌─────────────────┐     MCP协议     ┌─────────────────┐
│   MCP Client    │◄───────────────►│   MCP Server    │
│  (AI应用)        │                 │  (数据/工具)      │
│  Claude/ChatGPT │                 │  GitHub/Slack   │
└─────────────────┘                 └─────────────────┘
```

- **MCP Client**: AI应用（如Claude Desktop、ChatGPT、Cursor）
- **MCP Server**: 暴露数据和工具的服务端（如数据库、API、文件系统）
- **MCP协议**: 标准化的双向通信协议

### MCP Server类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **数据源** | 连接数据存储 | Google Drive, 本地文件, 数据库 |
| **工具** | 执行特定功能 | 搜索引擎, 计算器, Web爬虫 |
| **工作流** | 专业化提示词 | 代码审查, 文档生成 |

---

## 发展历程

| 时间 | 里程碑 |
|------|--------|
| **2024.11.25** | Anthropic首次发布MCP，开源协议规范和SDK |
| **2025.11.25** | MCP一周年，发布异步操作、无状态等新特性 |
| **2025.12.09** | Anthropic将MCP捐赠给Linux Foundation下的AAIF |

### 生态规模 (截至2025.12)

- **10,000+** 活跃公开MCP Server
- **97M+** 月SDK下载量 (Python + TypeScript)
- **75+** Claude官方Connector

---

## 平台采用

### AI产品

| 产品 | 公司 | 集成方式 |
|------|------|---------|
| **Claude Desktop** | Anthropic | 原生支持 |
| **ChatGPT** | OpenAI | 已采用 |
| **Gemini** | Google | 已采用 |
| **Microsoft Copilot** | Microsoft | 已采用 |
| **Cursor** | Anysphere | 原生支持 |
| **VS Code** | Microsoft | 已采用 |

### 云基础设施

| 提供商 | 支持内容 |
|--------|---------|
| **AWS** | 企业级MCP部署支持 |
| **Google Cloud** | MCP基础设施托管 |
| **Microsoft Azure** | MCP服务部署 |
| **Cloudflare** | MCP Server托管 |

---

## Agentic AI Foundation (AAIF)

### 背景

2025年12月9日，Anthropic将MCP捐赠给Linux Foundation下新成立的**Agentic AI Foundation (AAIF)**。

### 创始成员

| 角色 | 成员 |
|------|------|
| **联合创始人** | Anthropic, Block, OpenAI |
| **支持方** | Google, Microsoft, AWS, Cloudflare, Bloomberg |

### 创始项目

| 项目 | 来源 | 说明 |
|------|------|------|
| **MCP** | Anthropic | AI应用连接外部系统的协议 |
| **goose** | Block | Agent开发框架 |
| **AGENTS.md** | OpenAI | Agent规范文件格式 |

### 使命

确保Agentic AI以透明、协作的方式发展，服务公共利益。通过战略投资、社区建设和开放标准共同开发来实现。

---

## 技术规范

### 协议特性 (2025.11版本)

| 特性 | 说明 |
|------|------|
| **异步操作** | 支持异步工具调用 |
| **无状态** | Server可无状态运行 |
| **Server身份** | Server身份验证机制 |
| **官方扩展** | 可插拔扩展架构 |

### SDK支持

| 语言 | SDK | 状态 |
|------|-----|------|
| **Python** | mcp-python | 官方 |
| **TypeScript** | mcp-ts | 官方 |
| **其他语言** | 社区SDK | 活跃开发中 |

### 预置Server

官方提供的预置MCP Server:

- **Google Drive** - 文件访问
- **Slack** - 消息/频道
- **GitHub** - 仓库/PR/Issue
- **Git** - 本地Git操作
- **Postgres** - 数据库查询
- **Puppeteer** - 浏览器自动化

---

## 应用场景

### 个人助理增强

```
Agent + MCP
    ├── Google Calendar → 日程管理
    ├── Notion → 知识库访问
    └── Gmail → 邮件处理
= 更个性化的AI助理
```

### AI编程增强

```
Claude Code + MCP
    ├── Figma Server → 读取设计稿
    ├── GitHub Server → 代码仓库
    └── 本地文件 → 项目代码
= 从设计到代码的全流程AI
```

### 企业数据分析

```
企业ChatBot + MCP
    ├── 数据库1 → 销售数据
    ├── 数据库2 → 用户数据
    └── 数据库3 → 财务数据
= 跨系统数据分析能力
```

---

## MCP与Agent的关系

### 定位

MCP是Agent的**基础设施层**，提供工具连接标准。

```
Agent应用层
    │
    ├── Agent逻辑 (规划、推理、执行)
    │
    └── MCP协议层 ← 工具连接标准
            │
            └── 各类MCP Server
```

### 与Agent框架的关系

| 框架 | MCP角色 |
|------|--------|
| **LangChain/LangGraph** | 可作为Tool实现 |
| **Eino/veADK** | 可集成MCP Server |
| **扣子/Coze** | 可通过MCP连接外部工具 |

---

## 为什么MCP重要

### 对开发者

- **减少开发时间**: 不再为每个数据源写适配器
- **标准化集成**: 一次开发，处处可用
- **开源透明**: MIT协议，可自由使用和修改

### 对AI应用

- **扩展能力**: 接入生态中所有MCP Server
- **上下文连贯**: 跨工具和数据集保持上下文
- **用户体验提升**: 更强大的功能集成

### 对终端用户

- **更强大的AI**: AI可访问你的数据并代你执行操作
- **个性化**: 连接你自己的工具和数据
- **隐私可控**: 本地部署，数据不出本地

---

## 参考资料

- [MCP官方网站](https://modelcontextprotocol.io/)
- [Anthropic MCP发布公告](https://www.anthropic.com/news/model-context-protocol)
- [AAIF捐赠公告](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [MCP GitHub仓库](https://github.com/modelcontextprotocol)

---

## 相关知识

- [[Agent架构]] - MCP是Agent工具连接的标准协议
- [[Anthropic公司画像]] - MCP的创建者
- [[Agent基础设施]] - MCP属于Agent Dev基础设施

---

*最后更新: 2026-03-05*
