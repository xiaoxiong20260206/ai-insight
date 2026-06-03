# 页面底部"了解更多"模块规范 (v1.0)

> **版本**: v1.0
> **创建时间**: 2026-03-10
> **根因**: 2026-03-10纳瓦尔AI调研生成的HTML，"了解更多"模块只有相关链接，缺少林克介绍+首页入口。
> **教训**: 技能文档说"保留了解更多"，但没有给出具体HTML模板，导致实现不一致。

---

## 核心原则

**所有AI洞察项目生成的HTML页面（日报、周报、深度调研）底部必须包含统一的"了解更多"模块。**

这个模块的作用：
1. **项目介绍**: 让读者知道这是什么项目、谁在做
2. **首页入口**: 提供返回首页的快速通道
3. **相关资源**: 可选，列出本页相关的参考链接

---

## 标准HTML模板（P0强制使用）

> **v1.1 变更（2026-04-06）**：「所有深度调研」第二按钮已废弃移除。深度调研页面只保留「🏠 访问AI洞察首页」一个 CTA 按钮。
> **布局规范（v1.1）**：「了解更多」区块必须使用 `max-width:var(--content-max-width)` 外层包装，与页面 `.pg` 容器同宽；`.pg` 底部 padding 使用 `24px`（不再是 `80px`），区块上边距使用 `16px`，避免内容与区块之间出现过大空白。

### 完整版（深度调研使用，含相关资源）

```html
<!-- 了解更多 - 统一模块 -->
<div style="max-width:var(--content-max-width);margin:0 auto;padding:16px 20px 48px;">
<div style="background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #E7E5E4;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06),0 1px 2px rgba(31,35,40,.04)">
    <div style="font-size:16px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px">💡 了解更多</div>
    <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">
        我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。
    </p>
    <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
        <a href="https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#059669 0%,#10B981 100%);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
            🏠 访问AI洞察首页
        </a>
    </div>
    <!-- 以下为可选的相关资源部分，深度调研页面保留，日报/周报可省略 -->
    <div style="border-top:1px solid #E7E5E4;padding-top:12px;margin-top:12px;">
        <div style="font-size:13px;font-weight:600;color:#1C1917;margin-bottom:8px;">📚 参考来源</div>
        <ul style="list-style:none;padding:0;margin:0;font-size:13px;">
            <li style="margin-bottom:6px;"><a href="[链接1]" target="_blank" style="color:#2563EB;text-decoration:none;">[图标] [资源名称1]</a></li>
            <li style="margin-bottom:6px;"><a href="[链接2]" target="_blank" style="color:#2563EB;text-decoration:none;">[图标] [资源名称2]</a></li>
            <!-- 更多链接... -->
        </ul>
    </div>
</div>
</div>
```

### 简化版（日报/周报推荐使用）

```html
<!-- 了解更多 - 简化版 -->
<div style="margin-top:24px;background:linear-gradient(135deg,#F8FAFB 0%,#EEF2F6 100%);border:1px solid #F5F5F4;border-radius:14px;padding:24px;box-shadow:0 2px 8px rgba(31,35,40,.06),0 1px 2px rgba(31,35,40,.04)">
    <div style="font-size:16px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:8px">💡 了解更多</div>
    <p style="font-size:14px;color:#57534E;line-height:1.7;margin:0 0 12px 0">
        我是 <strong>林克</strong>，沈浪的AI分身。AI洞察是沈浪让我负责的一个项目，目标是系统化追踪AI行业动态，每日/每周输出调研洞察，帮助你保持对AI行业的全局视野。覆盖大模型、AI Coding、AI应用、AI行业投融资、企业AI转型五大领域。
    </p>
    <a href="https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,#059669 0%,#10B981 100%);color:#fff;border-radius:999px;font-size:13px;font-weight:600;text-decoration:none">
        🏠 访问AI洞察首页
    </a>
</div>
```

---

## 各类页面的使用规则

| 页面类型 | 使用模板 | 相关资源 | 位置 |
|---------|---------|---------|------|
| **AI日报** | 简化版 | ❌ 不需要 | 页面最底部，在JS脚本之前 |
| **AI周报** | 简化版 | ❌ 不需要 | 页面最底部，在JS脚本之前 |
| **深度调研** | 完整版 | ✅ 需要（标题"参考来源"） | 页面最底部，在JS脚本之前，使用 max-width 外层包装对齐 .pg 宽度 |

> **深度调研注意（2026-04-08 更新）**：深度调研报告采用长页面阅读体验，左侧已有锚点目录，
> **禁止在 footer 区域额外添加"← 返回深度调研首页"或"← 返回AI洞察首页"等文字返回链接**。
> 底部只保留"了解更多"模块（林克介绍 + AI洞察首页按钮 + 参考来源），不要其他导航。

---

## P0 强制检查

生成HTML页面后，必须检查以下内容：

- [ ] **底部有"了解更多"模块**
- [ ] **包含林克介绍段落**（"我是林克，沈浪的AI分身..."）
- [ ] **包含首页入口按钮**（"🏠 访问AI洞察首页"）
- [ ] **链接正确**（https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/）
- [ ] **深度调研页面有相关资源列表**

---

## 常见错误

### ❌ 错误1: 只有相关链接，没有林克介绍

```html
<!-- 错误示例 -->
<div class="learn-more">
    <h3>📚 了解更多</h3>
    <ul>
        <li><a href="https://xxx">链接1</a></li>
    </ul>
</div>
```

**问题**: 缺少林克介绍和首页入口按钮

### ❌ 错误2: 有林克介绍但没有首页按钮

```html
<!-- 错误示例 -->
<div>
    <p>我是林克...</p>
    <!-- 没有按钮！ -->
</div>
```

**问题**: 读者无法返回首页

### ✅ 正确示例

```html
<div style="...">
    <div>💡 了解更多</div>
    <p>我是<strong>林克</strong>，沈浪的AI分身。AI洞察是...</p>
    <a href="https://ai-insight-internal.frontend-cloud.corp.kuaishou.com/">🏠 访问AI洞察首页</a>
</div>
```

---

## 为什么这很重要

1. **品牌一致性**: 所有页面有统一的品牌露出
2. **用户导航**: 读者可以方便地返回首页发现更多内容
3. **项目介绍**: 新读者能快速了解AI洞察是什么
4. **闭环体验**: 从任何页面都能回到首页，形成内容闭环

---

## 脚本支持

日报生成脚本 `gen_daily_html.py` 已内置此模板，会自动生成正确的"了解更多"模块。

深度调研和周报需要手动添加（或从现有页面复制），确保格式一致。
