# AI编程Prompt - 快手研发实习生AI产品分析系统

> **使用说明**：复制下方Prompt内容，粘贴给AI（如Claude、ChatGPT、Cursor等），即可重新生成该项目。

---

## 完整Prompt

```
请帮我创建一个"快手研发实习生AI产品 - 工作场景与任务分析"的可视化网页系统。

## 一、项目概述

这是一个面向快手内部员工的AI能力平台分析工具，通过可视化方式展示工程师日常工作场景与AI Agent类型的映射关系，帮助产品规划团队确定AI产品的开发优先级。

## 二、技术栈

- 纯前端项目：HTML5 + CSS3 + 原生JavaScript
- 不使用任何框架或库
- SVG用于绘制关系图
- 响应式设计

## 三、文件结构

创建4个文件：
1. index.html - 主页面
2. styles.css - 样式文件
3. main.js - 主交互逻辑
4. network-graph.js - 关系图渲染

## 四、页面结构

从上到下包含以下模块：

### 4.1 Header
- 标题："快手研发实习生AI产品 - 工作场景与任务分析"
- 副标题说明
- 渐变背景（快手品牌橙 #FF5500）

### 4.2 数据统计卡片（4个）
| 卡片 | 数值 | 说明 |
|------|------|------|
| 总工作任务数 | 41 | 覆盖工程师日常全场景 |
| 研发场景任务 | 22 | AI编程、代码审查等 |
| 非研发场景任务 | 19 | 文档写作、配图生成等 |
| Agent类型 | 9 | Coding、Chatbot、Workflow等 |

### 4.3 优先级分析结论
展示P0-P4五个优先级的开发建议：

**P0 最高优先级（立即开发）**
- Coding Agent：覆盖~45%工作时长
- Chatbot Agent：覆盖~8%时长

**P1 高优先级（近期开发）**
- Workflow Agent：代码审查、技术文档、会议纪要
- Workflow-Design Agent：图表绘制、配图生成
- 文档写作任务

**P2 中优先级（规划开发）**
- Research Agent：技术调研、竞品分析
- Workflow-Data Analysis Agent：日志分析、SQL查询

**P3 低优先级**
- Background Agent：后台自动化任务

**P4 探索性（技术储备）**
- Computer Use Agent
- Browser Use Agent

### 4.4 关系图可视化（核心功能）

绘制6列SVG关系图：
```
场景大类 → 场景子类 → 工作任务 → Agent类型 → 技术实现 → 业界产品
```

**交互功能：**
1. 点击任意节点高亮相关联的节点和连线
2. 鼠标悬浮显示Tooltip（包含时长占比、任务示例等）
3. 点击空白区域取消高亮

### 4.5 任务详细表格（2个）

**研发场景表格**（22个任务）和**非研发场景表格**（19个任务），列包括：
- 场景大类、场景子类、工作任务、每周时长占比、任务示例、Agent类型、技术实现、业界产品参考

### 4.6 Agent类型卡片

展示9种Agent的定义：
1. 💻 Coding Agent - 代码开发全流程
2. 💬 Chatbot Agent - 通用对话，RAG增强
3. ⚙️ Workflow Agent - 预定义流程自动化
4. 🎨 Workflow-Design Agent（子类）- 图表绘制、配图生成
5. 📊 Workflow-Data Analysis Agent（子类）- SQL生成、数据分析
6. 🔬 Research Agent - Web搜索、深度调研
7. 🌐 Browser Use Agent - 网页自动化
8. 🖥️ Computer Use Agent - 桌面GUI自动化
9. ⏰ Background Agent - 后台持续运行

## 五、完整任务数据

### 研发场景（22个任务）

| 子类 | 任务 | 时长占比 | Agent | 产品参考 |
|------|------|----------|-------|----------|
| AI编程 | 代码补全 | 20% | Coding | Copilot, Cursor |
| AI编程 | 代码生成 | 12% | Coding | Cursor, Claude Code |
| AI编程 | 代码重构 | 3% | Coding | Cursor |
| AI编程 | Bug修复 | 5% | Coding | Cursor |
| AI编程 | 小工具开发 | 2% | Coding | Replit |
| 代码审查 | Code Review | 4% | Workflow | CodeRabbit |
| 代码审查 | 安全检测 | 1% | Workflow | Snyk |
| 需求分析 | PRD解析 | 1% | Workflow | Notion AI |
| 需求分析 | 技术方案 | 2% | Research | Claude |
| 测试 | 单测生成 | 3% | Coding | Copilot |
| 测试 | 用例设计 | 1% | Workflow | ChatGPT |
| 技术文档 | API文档 | 2% | Workflow | Mintlify |
| 技术文档 | 代码注释 | 2% | Coding | Copilot |
| 图表绘制 | 架构图 | 1% | Design | Eraser |
| 图表绘制 | 流程图 | 1% | Design | Mermaid |
| 图表绘制 | ER图 | 0.5% | Design | dbdiagram |
| 数据分析 | 日志分析 | 1.5% | Data | ChatGPT |
| 数据分析 | 性能分析 | 1% | Data | Julius |
| 数据分析 | SQL查询 | 0.5% | Data | Hex |
| 自动化 | 文件管理 | 0.5% | Background | Claude Computer |
| 自动化 | 研发提醒 | 0.5% | Background | - |
| 自动化 | 后台任务 | 0.5% | Background | GitHub Actions |

### 非研发场景（19个任务）

| 子类 | 任务 | 时长占比 | Agent | 产品参考 |
|------|------|----------|-------|----------|
| 文档写作 | 博客/周报 | 2% | Chatbot | Notion AI |
| 文档写作 | 邮件撰写 | 2% | Chatbot | Gmail AI |
| 文档写作 | PPT生成 | 2% | Workflow | Gamma |
| 文档审查 | 文档Review | 1% | Workflow | Claude |
| 文档审查 | 文档润色 | 1% | Chatbot | Grammarly |
| 调研分析 | 技术调研 | 4% | Research | Perplexity |
| 调研分析 | 竞品分析 | 2% | Research | Perplexity |
| 调研分析 | 数据采集 | 1% | Browser | Browser Use |
| 会议效率 | 会议纪要 | 3% | Workflow | Otter |
| 知识问答 | 技术问答 | 5% | Chatbot | ChatGPT |
| 知识问答 | 内部知识 | 3% | Chatbot | Glean |
| 图片生成 | 配图生成 | 0.5% | Design | Midjourney |
| 图片生成 | 图表美化 | 0.5% | Design | Canva AI |
| 视频生成 | 演示视频 | 0.3% | Workflow | Sora |
| 视频生成 | 数字人 | 0.3% | Workflow | HeyGen |
| 视频生成 | 配音 | 0.4% | Workflow | Loom |
| 个人助理 | 日程管理 | 1% | Background | Motion |
| 个人助理 | 邮件处理 | 2% | Background | Superhuman |
| 个人助理 | 桌面自动化 | 0.5% | Computer | Claude Computer |
| 个人助理 | 表单填写 | 0.5% | Browser | Browser Use |
| 个人助理 | 信息推送 | 0.5% | Background | Feedly |

## 六、样式规格

### 颜色系统
- 主色：#FF5500（快手橙）
- 研发场景：#3B82F6（蓝色）
- 非研发场景：#8B5CF6（紫色）
- 背景：#F5F7FA

### 关系图节点渐变色
- 场景大类：#FF5500 → #FF7733
- 场景子类：#E67E22 → #F39C12
- 工作任务：#11998e → #38ef7d
- Agent类型：#667eea → #764ba2
- 技术实现：#4facfe → #00f2fe
- 业界产品：#f093fb → #f5576c

### Agent徽章颜色
- Coding Agent：粉色系（#FCE7F3）
- Chatbot Agent：绿色系（#D1FAE5）
- Workflow Agent：蓝色系（#DBEAFE）
- Research Agent：黄色系（#FEF3C7）
- Background Agent：紫色系（#EDE9FE）
- Browser Agent：青色系（#CCFBF1）
- Design Agent：粉色系
- Data Agent：天蓝色系（#CFFAFE）

## 七、交互细节

### 关系图交互
1. **点击高亮**：点击节点后，该节点及直接关联节点保持100%不透明度，其他节点降为25%，非关联连线降为8%
2. **Tooltip**：鼠标悬浮显示详细信息
   - 场景大类：名称、时长占比、子类数量
   - 场景子类：名称、时长占比、任务数量
   - 工作任务：名称、时长占比、业界产品、任务示例
3. **取消高亮**：再次点击同一节点或点击空白区域

### 性能优化
1. 使用节流函数处理Tooltip移动（16ms，约60fps）
2. 缓存DOM查询结果
3. 使用requestAnimationFrame进行批量样式更新
4. 使用事件委托减少事件监听器数量

## 八、响应式设计

- >1200px：4列卡片布局
- 768px-1200px：2列布局
- <768px：1列布局，表格字号缩小

## 九、开发路线图展示

在页面中展示分阶段开发建议：
- 第一阶段（1-2月）：Coding Agent + Chatbot Agent（覆盖50%+时长）
- 第二阶段（3-4月）：Workflow Agent（覆盖18%时长）
- 第三阶段（5-6月）：Research Agent（覆盖8%时长）
- 第四阶段（后续）：Background/Browser/Computer Agent

请按照以上规格生成完整的4个文件代码。
```

---

## 分步骤Prompt（如果需要分步生成）

### Step 1: 创建基础HTML结构

```
创建一个index.html文件，包含以下结构：
1. Header区域 - 快手品牌橙渐变背景
2. 4个数据统计卡片
3. 优先级分析结论区域（P0-P4）
4. 关系图容器div
5. 两个表格区域（研发场景/非研发场景）
6. 9个Agent类型定义卡片
7. Footer

使用语义化HTML，引入styles.css、main.js、network-graph.js
```

### Step 2: 创建样式文件

```
创建styles.css，实现以下样式：

1. CSS变量定义：
   - 主色#FF5500，研发色#3B82F6，非研发色#8B5CF6
   - 阴影、圆角、背景色系统

2. Header样式：渐变背景，白色文字，大阴影

3. 卡片样式：
   - 左边框5px彩色
   - Hover效果：上移4px+阴影增强
   - Grid响应式布局

4. 优先级卡片：P0红/P1橙/P2黄/P3蓝/P4灰边框

5. 表格样式：
   - 斑马纹
   - 粘性表头
   - 时长占比颜色编码（≥10%红，3-9%橙，1-2%黄，<1%灰）

6. Agent徽章：不同类型不同渐变色

7. 关系图容器和Tooltip样式

8. 响应式断点：1200px/768px/600px
```

### Step 3: 创建关系图渲染逻辑

```
创建network-graph.js，实现以下功能：

1. 数据定义：
   - taskData: 包含dev和nondev两个场景，每个场景有多个子类，每个子类有多个任务
   - agentData: 9种Agent类型及其关联技术
   - techData: 9种技术实现
   - productsData: 26个业界产品
   - techProductMapping: 技术到产品的映射关系

2. 渲染函数renderNetworkGraph()：
   - 6列布局：场景大类→场景子类→工作任务→Agent类型→技术实现→业界产品
   - 使用贝塞尔曲线绘制连线
   - 节点使用渐变色矩形+居中文字

3. 布局算法：
   - 左3列按数据顺序垂直排列
   - Agent列根据关联任务Y坐标平均值定位
   - Tech列根据关联Agent Y坐标平均值定位
   - Product列根据关联Tech Y坐标平均值定位

4. SVG生成：渐变定义、列标题、连线组、各类型节点组
```

### Step 4: 创建主交互逻辑

```
创建main.js，实现以下功能：

1. 节流函数throttle(fn, delay)

2. DOM缓存：缓存connections和nodes查询结果

3. highlightRelated(nodeId)函数：
   - 收集直接关联节点
   - 使用requestAnimationFrame批量更新样式
   - 高亮节点不透明度100%，其他25%
   - 高亮连线不透明度100%，其他8%

4. resetHighlight()函数：恢复所有样式

5. Tooltip函数：
   - showSceneTooltip/showSubcatTooltip/showTaskTooltip
   - 定位函数positionTooltip
   - hideTooltip
   - moveTooltip使用节流

6. 事件委托：在container上监听click

7. MutationObserver：监听SVG变化清除缓存
```

---

## 快速验证Prompt

```
请帮我创建一个工程师AI工具分析的可视化网页：
1. 统计41个工作任务（22个研发+19个非研发）
2. 匹配9种Agent类型
3. 绘制6列SVG关系图（场景→子类→任务→Agent→技术→产品）
4. 支持点击高亮和Tooltip
5. 使用快手品牌橙(#FF5500)为主色
6. 纯HTML/CSS/JS实现
```

---

## 关键数据快速参考

### Agent时长占比排序
1. Coding Agent: ~45%
2. Chatbot Agent: ~13%
3. Workflow Agent: ~12%
4. Research Agent: ~8%
5. Background Agent: ~5%
6. Workflow-Design Agent: ~4%
7. Workflow-Data Analysis Agent: ~3%
8. Browser Use Agent: ~1.5%
9. Computer Use Agent: ~0.5%

### 技术实现列表
LLM、代码索引、RAG、WebSearch、BrowserUse、ComputerUse、调度器、图表引擎、SQL引擎

### 业界产品列表
Copilot, Cursor, Claude Code, Claude, ChatGPT, Replit, CodeRabbit, Snyk, Notion AI, Mintlify, Eraser, Mermaid, dbdiagram, Julius, Hex, GitHub Actions, Gmail AI, Gamma, Grammarly, Perplexity, Browser Use, Otter, Glean, Midjourney, Canva AI, Sora, HeyGen, Loom, Motion, Superhuman, Feedly

---

*Prompt文档结束 - 使用上述Prompt可以让AI重新生成完整项目*
