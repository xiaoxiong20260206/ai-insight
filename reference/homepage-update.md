# 首页更新检查清单 (v2.1)

> **版本**: v2.1
> **更新时间**: 2026-03-09
> **对齐**: SKILL.md v7.5.0
> **职责边界**: 首页CSS/组件/部署由 `link-homepage` 技能管理，本文件负责AI洞察**业务数据**的首页同步

---

## AI-Insight 首页结构 (v2.1)

```
index.html (Tab式导航)
├── Header: AI-Insight 标题 + 导航
├── Stats Grid: 5个统计卡片（追踪人物/公司/信息源/深度调研/知识文档）
├── Tab Navigation: 4个Tab
│
├── Tab 1: 📰 日报 & 周报
│   ├── ⭐ 周报入口卡片（蓝紫渐变，当有周报时显示）← v2.1新增
│   ├── 最新日报列表 (6条)
│   └── 📅 日历视图 (紧凑版 280px，支持日报+周报标识)
│       ├── 有日报日期高亮（绿色）
│       ├── 有周报日期标识（蓝紫渐变小横条）← v2.1新增
│       └── 图例三项：有日报（绿）、有周报（蓝紫条）、今天（蓝框）
│
├── Tab 2: 🔬 深度调研
│   ├── 趋势洞察卡片网格
│   ├── 公司调研卡片网格
│   └── 专题调研卡片网格
│
├── Tab 3: 🎯 追踪体系 (展开式)
│   ├── 👤 人物追踪 (L1实践者+L2观察者+L3决策者，100+)
│   ├── 🏢 公司追踪 (按领域分类，140+)
│   └── 📡 信息源 (官方博客+Newsletter+公众号+社区+学术，200+)
│
└── Tab 4: 📚 知识库
    └── 知识卡片（四大维度）
```

---

## 交互组件

### 1. 日历视图 (Calendar)

**位置**: AI日报Tab底部
**尺寸**: 紧凑型 `max-width: 280px`

**功能**:
- 显示当月日历，有日报的日期绿色高亮
- **有周报的日期显示蓝紫渐变小横条** ← v2.1
- 点击跳转对应日报/周报（新标签页）
- 左右箭头切换月份
- 显示当月日报数量统计

**数据配置** (在index.html的JS中):
```javascript
// 日报数据
const reportsData = {
    '2026-03': [2, 3, 4, 5, 6, 7, 8],  // 3月有日报的日期
    '2026-02': [28],
};

// 周报数据：键为月份，值为 {日期: 周报文件名} ← v2.1新增
const weeklyReportsData = {
    '2026-03': {8: 'weekly-2026-W10'}  // 3月8日是W10最后一天
};

// ⚠️ P0 (经验#62): 当前月份必须动态读取，禁止硬编码数字
// ❌ 错误: let currentMonth = 3; （下个月就是 bug）
// ✅ 正确:
const today = new Date();
const todayYear = today.getFullYear();
const todayMonth = today.getMonth() + 1;
const todayDay = today.getDate();
let currentYear = todayYear;
let currentMonth = todayMonth; // 动态，不得改为硬编码
```

**周报日历标识规则 (v2.1)**:
- 周报标识放在该周最后一天（周六）
- CSS类 `.has-weekly` 使用 `::after` 伪元素
- 同时有日报+周报时，tooltip显示"X月X日 AI日报 + 📊 周报"
- 新增周报时只需在 `weeklyReportsData` 加一行数据

**CSS类**:
- `.calendar-container`: 容器
- `.calendar-grid`: 7列网格
- `.calendar-day`: 日期单元格
- `.calendar-day.has-report`: 有日报的日期
- `.calendar-day.has-weekly`: 有周报的日期 ← v2.1
- `.calendar-day.today`: 今天
- `.calendar-nav-btn`: 月份切换按钮

### 2. 周报入口卡片 (v2.1新增)

**位置**: AI日报Tab顶部（日报列表上方）
**样式**: 蓝紫渐变背景（`#EFF6FF → #F5F3FF`），与日报绿色系视觉区分
**内容**: 周号+日期范围 + "首期周报"徽章(badge) + Top5摘要

**CSS类**: `.weekly-report-card` + `.wrc-icon` / `.wrc-content` / `.wrc-title` / `.wrc-badge` / `.wrc-arrow`

**更新时机**: 每次发布新周报后，更新入口卡片的周号、日期、Top5摘要和链接

### 3. 展开式追踪体系 (Collapsible)

**交互**: 点击header展开/收起，不跳转文档
**内容**: 结构化表格展示完整追踪清单（由 `update_tracking.py` 脚本生成）
**层级**: L1/L2/L3分层，包含检查频率、追踪重点
**数量徽章**: 每个分类header显示数量（如 `100+`）

**CSS类**:
- `.collapsible-header` / `.collapsible-header.active`: 可点击header
- `.collapsible-content` / `.collapsible-content.active`: 折叠内容区

**JavaScript**:
```javascript
function toggleCollapsible(header) {
    const content = header.nextElementSibling;
    const isActive = header.classList.contains('active');
    header.classList.toggle('active', !isActive);
    content.classList.toggle('active', !isActive);
}
```

### 4. 链接行为

**规则**: 所有外部链接使用 `target="_blank"` 新标签页打开

---

## 首页统计卡片 (Stats Grid)

首页顶部5个统计卡片，**必须**与实际追踪数量同步：

| 卡片 | 数据来源 | 更新时机 | 当前值 |
|------|---------|---------|--------|
| **追踪人物** | `03-tracking-registry/people/index.md` | 追踪名单更新时 | 100+ |
| **追踪公司** | `03-tracking-registry/companies/index.md` | 追踪名单更新时 | 140+ |
| **信息源** | `03-tracking-registry/sources/index.md` | 追踪名单更新时 | 200+ |
| **深度调研** | `02-deep-research/` 目录文件数 | 新增调研报告时 | — |
| **知识文档** | `04-knowledge-base/` 目录文件数 | 新增知识文档时 | — |

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value green">100+</div>
        <div class="stat-label">追踪人物</div>
    </div>
    <!-- ... -->
</div>
```

---

## 更新触发条件

| 事件 | 需要更新 |
|------|----------|
| 新增日报 | 日报列表 + 日历数据 (reportsData) + 日报index页 |
| 新增周报 | **周报入口卡片 + 日历 weeklyReportsData + 日报index页** ← v2.1 |
| 新增深度研究 | 深度调研Tab卡片网格 |
| 更新追踪体系 | 运行 `update_tracking.py` + 手动更新统计卡片 |
| 新增月份 | 日历数据 (reportsData)，**`currentMonth` 无需手动修改**（已动态化，经验#62） |

> **⚠️ P0 (经验#62)**: `currentMonth` 和 `currentYear` 在 `index.html` 中**必须**动态读取 `todayMonth`/`todayYear`，
> 禁止硬编码为固定数字（如 `let currentMonth = 3`）。
> `daily_quality_gate.py` 已加入此项检查，任何硬编码都会触发质量门失败。

---

## 日报更新流程 (v3.4联动更新)

> **P0**: 每期日报发布时，以下6处**全部必须更新**，缺一不可：

| # | 文件 | 更新内容 | 验证方法 |
|---|------|---------|----------|
| 1 | `01-daily-reports/YYYY-MM/YYYY-MM-DD.md` | 日报源文件 | 文件存在 |
| 2 | `01-daily-reports/YYYY-MM/YYYY-MM-DD-v3.html` | 渲染版HTML | 文件存在+可浏览 |
| 3 | `01-daily-reports/YYYY-MM/YYYY-MM-DD.html` | 跳转页(→v3.html) | meta refresh指向正确 |
| 4 | `01-daily-reports/index.html` | 列表+统计数字 | 数字=实际条目数 |
| 5 | `index.html` 日报Tab | 新条目+日历数据 | 日历JS数组含当日 |
| 6 | `public/` 公开版 | **必须用 sync_to_public.py** | grep敏感词=0 + `-v3`链接=0 |

> **⚠️ -v3 文件名约定警示 (经验14)**:
> - **内部版**: 日报HTML使用 `-v3.html` 后缀（如 `2026-03-09-v3.html`），跳转页 `.html` 用 meta refresh 指向 `-v3.html`
> - **公开版(public/)**: `sync_to_public.py` 自动去掉 `-v3` 后缀，文件统一命名为 `.html`（如 `2026-03-09.html`）
> - **风险**: 内部版 `index.html` 的链接指向 `-v3.html`，如果 sync 未重跑或被绕过，public 版首页链接将指向不存在的文件 → **404**
> - **防线**: `--verify` 会检测 public/ 中 `-v3.html` 链接残留。**首页每次修改后必须重跑 sync**

---

## 周报更新流程 (v2.1新增)

每次发布新周报后**必须**更新：

| # | 文件/位置 | 更新内容 |
|---|---------|---------|
| 1 | `index.html` → `weeklyReportsData` | 添加周报日期映射 |
| 2 | `index.html` → 周报入口卡片 | 更新周号/日期/Top5摘要/链接 |
| 3 | `01-daily-reports/index.html` | 周报计数+链接 |

---

## 追踪体系更新流程 (v3.5 脚本化全量同步)

### ⚠️ P0规则: 更新追踪名单后必须运行同步脚本

> **教训 (2026-03-08)**: 追踪体系MD文件经多次更新，人物从85+→100+、公司130+→140+、信息源~90→200+，但首页HTML一直未同步，数据严重漂移。

### 更新步骤

```
1. 更新追踪名单MD文件
   └── 03-tracking-registry/{people,companies,sources}/index.md

2. ⭐ 运行追踪体系同步脚本（P0必做）
   └── python3 scripts/update_tracking.py
   └── 脚本自动：定位section边界 → 生成全量HTML → 替换旧内容 → 更新徽章数字

3. 手动更新统计卡片数字（⚠️ 脚本不会自动更新）
   └── 修改 .stats-grid 中的人物/公司/信息源数字

4. 本地预览验证
   └── python3 -m http.server <port>
   └── 检查追踪体系三个展开区域内容正确

5. Git提交并部署
   └── git add -A && git commit && git push origin main

6. ⚠️ 公开版同步（P0，如涉及首页变更）
   └── python3 scripts/sync_to_public.py --all --force --with-index
   └── python3 scripts/sync_to_external.py
   └── grep敏感词验证
```

**关键约束**:
- ❌ 禁止直接手动编辑HTML追踪section（应修改脚本后重跑）
- 数据流向: MD文件 → update_tracking.py → HTML展示

---

## 部署流程

### 标准部署
```bash
cd ../AI-Insight
git add .
git commit -m "Update: [更新内容摘要]"
git push origin main
# 等待 GitHub Actions 完成 (~60秒)
```

### 验证部署
```bash
gh api repos/[GITHUB_USER]/ai-insight/actions/runs --jq '.workflow_runs[0] | {status, conclusion}'
curl -I https://[GITHUB_USER].github.io/ai-insight/
```

### 常见问题
1. **部署锁冲突**: 等60秒后重新push，或手动取消进行中的部署
2. **Actions失败**: 检查Actions日志，常见原因：文件路径错误/HTML语法错误
3. **页面未更新**: CDN缓存，硬刷新(Cmd+Shift+R)或等5分钟

---

## 更新检查总清单

### 新增日报后
- [ ] 日报文件已生成 (MD + HTML)
- [ ] `index.html` 日报Tab列表已更新
- [ ] `index.html` 日历数据 (reportsData) 已更新
- [ ] `01-daily-reports/index.html` 已更新（列表+统计数字）
- [ ] Git已提交并推送
- [ ] **公开版已同步** (sync_to_public.py --full --force --verify + sync_to_external.py)
- [ ] **`--verify` 通过**: 敏感词=0 且 `-v3`链接残留=0 ← 经验14

### 新增周报后 (v2.1)
- [ ] 周报文件已生成 (MD + HTML)
- [ ] **`index.html` 日历 weeklyReportsData 已更新**
- [ ] **`index.html` 周报入口卡片已更新（周号/日期/摘要/链接）**
- [ ] **`01-daily-reports/index.html` 周报计数+链接已更新**
- [ ] Git已提交并推送

### 新增深度研究后
- [ ] 研究文件已生成
- [ ] **`index.html` 深度调研Tab已更新（新卡片放最前面）** ← P0
- [ ] `02-deep-research/index.md` 已更新
- [ ] Git已提交并推送

### 更新追踪体系后 (v3.5)
- [ ] 源文件 `03-tracking-registry/` 已更新
- [ ] **已运行 `python3 scripts/update_tracking.py`** ← P0
- [ ] `index.html` 统计卡片数字已手动更新
- [ ] 本地预览验证三个展开区域内容正确
- [ ] Git已提交并推送
- [ ] 公开版已同步
