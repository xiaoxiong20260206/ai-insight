# 首页开发规范 (v1.0)

> **版本**: v1.0
> **创建**: 2026-05-11
> **背景**: 内外版首页多次被改坏（脱敏绕过/CSS损坏/破图残留/内部链接泄露），需系统性防退化

---

## 一、架构总览

```
┌─────────────────────────────────────────────────────┐
│ 首页双版本架构                                        │
├──────────────┬──────────────────────────────────────┤
│ 内部版        │ 外部版                                │
│ (保留林克身份) │ (零敏感词+零内部链接)                  │
├──────────────┼──────────────────────────────────────┤
│ index.html    │ ai-insight-public/index.html          │
│ → public/     │ （独立仓库，脱敏后部署）                │
│ → Pages部署   │ → Pages部署                           │
└──────────────┴──────────────────────────────────────┘
```

**CSS引用关系**：
- **日报/周报HTML**: 公共CSS变量+基础样式从 `qingshuang-research-style/references/base-styles.css` 动态引用（gen_daily_html.py 自动合并），项目定制样式从 `templates/ai-insight-custom.css` 读取
- **首页**: CSS内联在 `<style>` 块中（2098行），修改时必须对照 `qingshuang-research-style` 最新规范同步更新CSS变量定义
- ⚠️ 首页CSS不自动引用——因为首页CSS是高度定制化的（Tab导航/日历/统计卡片/知识库/追踪体系等），公共层和定制层已经深度耦合，无法简单拆分
- ⚠️ 每次修改首页CSS变量时，必须同时检查 `qingshuang-research-style/references/base-styles.css` 的最新版本，确保变量名和值一致

**部署链路**：
- 内部版：`sl-ai-insight/index.html` → `sl-ai-insight/public/index.html` → `xiaoxiong20260206.github.io/ai-insight/`
- 外部版：`sl-ai-insight/index.html` → `sanitize_html()` → `ai-insight-public/index.html` → `xiaoxiong20260206.github.io/ai-insight-public/`

---

## 二、内部版首页标准

### Header
```html
<header class="header">
    <div class="header-badge">
        <span>🔬</span>
        <span>AI行业洞察</span>
    </div>
    <h1 class="header-title">AI洞察 · 持续追踪AI行业动态</h1>
    <p class="header-subtitle">
        系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野
    </p>
</header>
```

**禁止项**：
- ❌ 头像图片 `<img>` 标签（之前有 `link-avatar-small.webp`，已移除）
- ❌ 个性化署名 div（之前有"林克 · 沈浪的AI分身"，已移除）

### Footer
```html
<footer class="footer">
    <div class="footer-brand">
        <span>🔬</span>
        <span>AI洞察 · 持续追踪 · 深度洞察</span>
    </div>
    <p>
        AI洞察 · 持续追踪AI行业动态
    </p>
</footer>
```

**禁止项**：
- ❌ 头像图片 `<img>` 标签（之前有 `link-avatar-small.webp` 40px版本）
- ❌ GitHub/项目说明/更新日志链接（这些文件不存在于线上）
- ❌ 个性化署名 div（"林克 · 沈浪的AI分身"）

### 知识库
- 内部版**可以**保留 `04-knowledge-base/*.md` 的 `<a>` 链接（文件存在于内部版仓库）
- 但知识库卡片使用 `onclick="toggleKBDimension(this)"` 展开/折叠交互，保持不变

---

## 三、外部版首页标准（比内部版更严格）

### Header — 与内部版完全一致
```html
<header class="header">
    <div class="header-badge">
        <span>🔬</span>
        <span>AI行业洞察</span>
    </div>
    <h1 class="header-title">AI洞察 · 持续追踪AI行业动态</h1>
    <p class="header-subtitle">
        系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野
    </p>
</header>
```

### Footer — 与内部版完全一致
```html
<footer class="footer">
    <div class="footer-brand">
        <span>🔬</span>
        <span>AI洞察 · 持续追踪 · 深度洞察</span>
    </div>
    <p>
        AI洞察 · 持续追踪AI行业动态
    </p>
</footer>
```

### 知识库 — 禁止内部链接
- ❌ `<a href="04-knowledge-base/...">` — 外部版不存在这些文件，点击会404
- ✅ 替换为 `<span class="kb-item-text">纯文本</span>`

### 日历 — 日报+周报双入口（v2.0 · 2026-05-20）

**交互规则**：
- 同一天既有日报又有周报 → 点击弹出选择菜单（日报/周报二选一），不直接跳日报
- 仅日报 → 直接跳日报
- 仅周报 → 直接跳周报
- 选择菜单向下弹出（`top: calc(100% + 8px)`），避免第一行溢出页面顶部

**视觉规则**：
- 日报格：绿色高亮
- 日报+周报格：绿→蓝渐变背景 + 底部小条
- 仅周报格：普通背景 + 底部小条
- hover 时小条颜色适配（渐变格 hover 时小条变白）

**图例**：四种状态——日报 / 日报+周报 / 仅周报 / 今天

**往期周报快速导航**：
- 最新周报卡片下方新增 pill 列表（W10→W20），圆角标签样式
- 新增周报时需手动追加 pill

**日历数据**：
- `reportsData`：键为 `YYYY-MM`，值为日期数组
- `weeklyReportsData`：键为 `YYYY-MM`，值为 `{日期: 'weekly-YYYY-Wxx'}`
- 新增日报/周报后必须同步更新两个数据对象

### Stats 区域 — 硬编码维护

首页统计数字（追踪人物/公司/信息源/深度调研/日报周报）是硬编码，无数据源联动。

**维护规则**：
- 每月至少检查一次，与实际数据对齐
- 修改时同步内部版和外部版（外部版不含内部专属统计）

### 本质洞察区块

- ❌ 禁止硬编码日期（如"2026-03-06更新"）——写"持续迭代"或动态日期
- ✅ 每次知识库更新后检查此区块描述是否过时

### 敏感词零容忍清单

| 类别 | 禁止词 | 原因 |
|------|--------|------|
| 个人身份 | 林克、沈浪、shenlang03、shenlang | 内部项目身份 |
| 公司 | 快手、Kuaishou、kuaishou | 公司绑定 |
| 内部平台 | CodeFlicker、MyFlicker、myflicker | 内部产品名 |
| 内部工具 | KATE、天策、天玑、KwaiBI | 内部平台代号 |
| 身份描述 | AI分身、让我负责、AI数字分身 | 暗示个人身份 |
| 内部体系 | 小无相功、SKILL.md、KIM Doc | 内部方法论 |
| 内网地址 | docs.corp.kuaishou.com | 内网地址 |
| 订阅按钮 | ./subscribe/ | 内部KIM订阅 |

---

## 四、脱敏流程（唯一合法路径）

### ⛔ P0 绝对禁止

**禁止 `cp index.html ai-insight-public/index.html`**
这是导致首页改坏的根因（2026-05-11事故）。直接复制会暴露林克/沈浪/快手/内部链接。

### ✅ 唯一合法路径

```
index.html → sanitize_html() → ai-insight-public/index.html
```

三种触发方式（任选其一）：

```bash
# 方式1: 全量同步（推荐）
python3 scripts/sync_to_public.py --full --force --with-index --verify

# 方式2: 仅首页同步
python3 scripts/sync_to_public.py --all --force --with-index

# 方式3: update_homepage.py（自动调用sanitize_html）
python3 scripts/update_homepage.py 2026-05-11
```

⚠️ `update_homepage.py` v2.0 已内置 `sanitize_html()` 调用，无需额外步骤。

### 脱敏脚本内置防护

| 防护项 | 规则 | 原因 |
|--------|------|------|
| CSS颜色值 | `(?<![0-9A-Fa-f#])CF(?![0-9A-Fa-f])` | 防止 #ECFDF5/8B5CF6 中的CF被替换 |
| 头像图片 | `display:none` 替代文件名替换 | 防止破图占位 |
| Footer头像div | 专用正则清除 | 防止"林克·沈浪的AI分身"残留 |
| Footer链接 | GitHub/项目说明/更新日志整段删除 | 文件不存在于外部版 |
| 知识库链接 | `<a>` → `<span class="kb-item-text">` | 04-knowledge-base不存在于外部版 |

---

## 五、update_homepage.py 防退化规范

### 必须遵守

1. **`sync_public_homepage()` 必须调用 `sanitize_html()`**
   - 不调用 = 裸复制 = 敏感词泄露到外部版
   - 当前代码已修复（v2.0），但每次修改此函数时必须重新确认

2. **`public/index.html` 是内部版部署源**
   - `public/index.html` = `index.html` 的直接复制（保留林克身份）
   - 这是正确的——内部版 Pages 从 `public/` 部署，保留林克身份是合法的

3. **外部版同步必须走 `ai-insight-public/` 仓库**
   - 脱敏后的内容写入 `../ai-insight-public/index.html`
   - 然后 push 到 `ai-insight-public` 仓库的 `main` 分支

4. **验证步骤不可跳过**
   ```bash
   # 验证外部版零敏感词
   cd ../ai-insight-public
   for word in 林克 沈浪 快手 kuaishou shenlang MyFlicker CodeFlicker KATE 天策 天玑 KwaiBI; do
       grep -i "$word" index.html && echo "FAIL: $word found" || true
   done
   # 验证CSS颜色值完好
   grep '#ECFDF5' index.html && grep '#8B5CF6' index.html
   # 验证无破图
   grep 'ai-insight-logo.webp' index.html && echo "FAIL: broken img" || echo "OK: no broken img"
   # 验证无内部链接
   grep '04-knowledge-base' index.html && echo "FAIL: internal links" || echo "OK: no internal links"
   # 验证无Footer链接
   grep 'README.md' index.html | grep -v 'var(--' && echo "FAIL: footer links" || echo "OK: no footer links"
   ```

---

## 六、首页改坏历史教训

| # | 事故 | 根因 | 修复 |
|---|------|------|------|
| 1 | 2026-05-11 外部版暴露林克/沈浪/快手 | `update_homepage.py` 裸复制绕过脱敏 | `sync_public_homepage()` 改为调用 `sanitize_html()` |
| 2 | 2026-05-11 CSS颜色值损坏 | `(r'CF', 'AI助手平台')` 无差别替换，#ECFDF5→#EAI助手平台DF5 | CF规则加 lookbehind `(?<![0-9A-Fa-f#])CF(?![0-9A-Fa-f])` |
| 3 | 2026-05-11 Header/Footer破图 | `link-avatar-small.webp`→`ai-insight-logo.webp` 替换文件名而非删除 | 改为隐藏img + 专用div清除规则 |
| 4 | 2026-05-11 Footer脱敏残留 | "林克·沈浪的AI分身"→"AI洞察·的AI洞察" | 专用footer div清除规则 |
| 5 | 2026-05-11 知识库链接404 | 外部版保留 `04-knowledge-base/*.md` 的 `<a>` 链接 | `sanitize_html()` 内置 `<a>`→`<span>` 替换 |
| 6 | 2026-05-11 Footer链接404 | 外部版保留 GitHub/README.md/CHANGELOG.md 链接 | REPLACEMENTS 新增 footer链接整段删除规则 |

---

## 七、首页修改 Checklist

每次修改 `index.html`（内部版首页）后：

- [ ] 修改内容在内部版正常（保留林克身份）
- [ ] 运行 `python3 scripts/sync_to_public.py --full --force --with-index --verify`
- [ ] 验证 `ai-insight-public/index.html` 零敏感词
- [ ] 验证 `ai-insight-public/index.html` CSS颜色值完好（ECFDF5/8B5CF6）
- [ ] 验证 `ai-insight-public/index.html` 无破图（ai-insight-logo.webp=0）
- [ ] 验证 `ai-insight-public/index.html` 无内部链接（04-knowledge-base=0）
- [ ] 验证 `ai-insight-public/index.html` 无Footer链接（README.md=0，排除CSS变量）
- [ ] **⚠️ 2026-05-20 新增：验证外部版 Header/Footer 无"林克/沈浪/AI分身"残留**（`grep -n '林克\|沈浪\|AI分身' ai-insight-public/index.html`）
- [ ] **⚠️ 2026-05-20 新增：验证外部版深度调研区无"林克实现"残留**
- [ ] Push 两个仓库：`sl-ai-insight` + `ai-insight-public`
- [ ] 等部署后截图验证线上效果

### 外部版脱敏事后验证（2026-05-20 教训）

sync_to_public.py 的正则脱敏可能遗漏新增内容（如 Header 区新增了 img+div 结构但正则未覆盖）。

**验证命令（每次改首页后必跑）**：
```bash
cd ai-insight-public/
grep -n '林克\|沈浪\|AI分身\|link-avatar-small\|让我负责' index.html && echo "FAIL: 身份泄露" || echo "OK"
```

**如果 FAIL**：直接手动修复外部版 `index.html`，再 push。不要依赖 `sync_to_public.py` 重跑（它可能从内部版重新覆盖，带着同样的泄露）。

---

*创建于 2026-05-11，基于6次首页改坏事故总结*
*更新于 2026-05-20，新增日历双入口规范、外部版脱敏验证、Stats维护*