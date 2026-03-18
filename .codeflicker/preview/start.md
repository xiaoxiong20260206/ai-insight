# AI-Insight 启动指南

## 项目概述
这是一个静态HTML项目，包含AI行业洞察的知识库页面。主要入口文件是index.html，无需构建步骤，直接通过本地HTTP服务器预览即可。

## 快速启动

### 方式一：使用 Python HTTP 服务器（推荐）

```bash
cd /Users/shenlang/Documents/Codeflicker/个人助理_V1/AI-Insight
python3 -m http.server 8080
```

**启动后访问**：http://localhost:8080

### 方式二：使用 Node.js serve

```bash
cd /Users/shenlang/Documents/Codeflicker/个人助理_V1/AI-Insight
npx serve -p 8080
```

**启动后访问**：http://localhost:8080

### 方式三：直接打开文件

```bash
open index.html
```

**注意**：直接打开可能会受到浏览器安全策略限制，推荐使用本地服务器方式。

```yaml
subProjectPath: .
command: python3 -m http.server 8080
cwd: .
port: 8080
previewUrl: http://localhost:8080
description: 静态HTML知识库页面，包含知识树可视化设计
```
