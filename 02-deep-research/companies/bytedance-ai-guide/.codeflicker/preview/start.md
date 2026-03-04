# 字节跳动AI调研 启动指南

## 项目概述
这是一个静态 HTML 网站项目，介绍字节跳动 AI 相关内容。无需构建工具，使用任意静态服务器即可预览。

## 静态网站

### 快速启动

```bash
python3 -m http.server 8888
```

或者使用 Node.js 的 http-server（需要全局安装）：

```bash
npx http-server -p 8888
```

**启动后访问**：http://localhost:8888

```yaml
subProjectPath: .
command: python3 -m http.server 8888
cwd: .
port: 8888
previewUrl: http://localhost:8888
description: 字节跳动AI调研静态网站，包含AI历史、架构、Agent基础设施等多个页面
```

## 项目结构

- `index.html` - 入口页面（自动跳转到 home.html）
- `home.html` - 主页
- `pages/` - 各专题页面
  - `ai-history.html` - AI历史
  - `architecture.html` - 架构
  - `agent-infra.html` - Agent基础设施
  - `bytedance-journey.html` - 字节跳动历程
  - `finance-insights.html` - 财务洞察
  - `security-practice.html` - 安全实践
- `css/` - 样式文件
