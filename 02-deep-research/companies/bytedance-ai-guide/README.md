# 字节AI开挂指南

一份带你看懂字节跳动AI全栈布局的轻松向研究报告。

## 📖 内容概览

本项目是一个多页面的调研报告网站，包含以下章节：

1. **AI三国杀** - AI发展简史与当前格局
2. **字节AI布局** - 从短视频公司到全栈AI巨头的进化之路
3. **Agent基础设施** - Agent Infra全家桶深度解析
4. **安全实践** - AI安全与隐私保护最佳实践
5. **金融洞察** - 给决策者的AI转型实战手册

## 🚀 在线预览

访问 [GitHub Pages](https://xiaoxiong20260206.github.io/bytedance-ai-guide/) 查看在线版本。

## 🛠️ 本地运行

```bash
# 使用Python启动本地服务器
python3 -m http.server 8888

# 或使用项目自带的缓存优化服务器
python3 server.py
```

然后访问 http://localhost:8888/home.html

## 📁 项目结构

```
├── home.html                 # 首页
├── pages/
│   ├── ai-history.html      # AI发展简史
│   ├── bytedance-ai.html    # 字节AI布局
│   ├── agent-infra.html     # Agent基础设施
│   ├── security-practice.html # 安全实践
│   └── finance-insights.html  # 金融洞察
├── css/
│   ├── styles.css           # 主样式文件
│   └── styles.min.css       # 压缩版样式
├── js/
│   └── nav.js               # 导航脚本
└── server.py                # 本地服务器（含缓存优化）
```

## 📝 技术栈

- 纯HTML/CSS/JavaScript，无框架依赖
- 响应式设计，支持移动端
- 清爽调研报告风格（基于GitHub设计规范）
- CSS变量系统，易于主题定制

## 📄 许可证

MIT License

## 🙏 致谢

- 字节跳动各产品线公开资料
- 行业研究报告与技术文档
