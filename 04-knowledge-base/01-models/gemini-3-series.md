# Gemini 3.1 Flash-Lite 模型详解

> **知识类型**: 模型解析
> **来源**: Google AI Developer Documentation
> **更新时间**: 2026-03-05
> **版本**: v1.0

---

## 概述

Gemini 3.1 Flash-Lite Preview 是 Gemini 3 系列首款 Flash-Lite 模型，于 2026年3月3日发布。

### 产品定位

| 维度 | 说明 |
|------|------|
| **模型系列** | Gemini 3.1 |
| **产品线** | Flash-Lite (轻量快速版) |
| **目标场景** | 高吞吐量、低成本、速度敏感型应用 |
| **状态** | Preview (预览版) |

---

## Gemini 3系列演进

```
时间线:
2025.11.18 ─ Gemini 3 Pro Preview 发布 (首款Gemini 3)
2025.12.17 ─ Gemini 3 Flash Preview 发布
2026.01.29 ─ Computer Use支持
2026.02.19 ─ Gemini 3.1 Pro Preview 发布
2026.02.26 ─ Gemini 3 Pro Preview 将于3月9日下线
2026.03.03 ─ Gemini 3.1 Flash-Lite Preview 发布
```

---

## Flash-Lite 产品线定位

### 各版本对比

| 版本 | 特点 | 适用场景 |
|------|------|---------|
| **Pro** | 最强推理能力、最完整功能 | 复杂任务、高精度需求 |
| **Flash** | 平衡性能与成本 | 通用场景、日常任务 |
| **Flash-Lite** | 极致速度与成本 | 高吞吐量、延迟敏感 |

### Flash-Lite的价值主张

> "Fast + Cheap + Good Enough"

1. **速度优先**: 优化推理延迟
2. **成本最低**: 适合大规模部署
3. **够用即可**: 牺牲部分能力换取效率

---

## 行业对比

### 同类模型对比

| 厂商 | 轻量模型 | 发布时间 |
|------|---------|---------|
| **Google** | Gemini 3.1 Flash-Lite | 2026.03 |
| **OpenAI** | GPT-5.3 Instant | 2026.03 |
| **Anthropic** | Claude Instant系列 | 持续迭代 |

### 市场趋势

> "Flash-Lite成为各家必争之地"

轻量模型竞争的核心是：
- 开发者日常任务的"默认选择"
- API调用量的主要承载者
- 成本敏感客户的首选

---

## 技术亮点

### Gemini 3系列新特性

1. **Computer Use**: 支持计算机使用工具
2. **Media Resolution**: 可配置媒体分辨率
3. **Thought Signatures**: 思考签名
4. **Thinking Levels**: 可配置思考级别
5. **Multimodal Function Responses**: 多模态函数响应
6. **Code Execution with Images**: 带图像的代码执行

---

## 迁移指南

### 即将下线的模型

| 模型 | 下线时间 |
|------|---------|
| `gemini-3-pro-preview` | 2026.03.09 |
| `gemini-2.0-flash` | 2026.06.01 |
| `gemini-2.0-flash-001` | 2026.06.01 |
| `gemini-2.0-flash-lite` | 2026.06.01 |

### 迁移建议

1. **从 Gemini 2.0 Flash-Lite**: 直接迁移到 Gemini 3.1 Flash-Lite
2. **从 Gemini 3 Pro Preview**: 迁移到 Gemini 3.1 Pro Preview
3. **API端点**: 更新到 `gemini-3.1-flash-lite-preview`

---

## API使用

### 模型名称

```
gemini-3.1-flash-lite-preview
```

### 获取API Key

1. 访问 [AI Studio](https://aistudio.google.com/)
2. 生成免费 Gemini API Key
3. 或使用 Google Cloud Vertex AI

---

## 相关知识

- [[Gemini 3 系列]] - 完整模型家族
- [[Flash vs Instant]] - 各厂商轻量模型对比
- [[模型选型指南]] - 如何选择合适的模型

---

## 参考资料

- [Gemini API Release Notes](https://ai.google.dev/gemini-api/docs/changelog)
- [Gemini 3.1 Flash-Lite Model Page](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)

---

*最后更新: 2026-03-05*
*整理者: 林克 AI 助手*
