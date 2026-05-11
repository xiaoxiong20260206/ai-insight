# 经验提炼：HTML 结构修复铁律

> 来源：2026-05-11 Anthropic金融Agent深度调研 sidebar 导航重构（7轮失败复盘）
> 验证次数：1次
> 信号强度：🔴强

---

## 铁律一：结构性异常 → 立刻 git reset，不要手术

**场景**：文件里出现多个 `<body>` / `<main>` / `</html>`，或内容块嵌套重复

**错误做法**：继续在破损文件上 patch（字符串替换/插入/截断）→ 负反馈循环，每次修复引入新问题

**正确做法**：
```bash
# 1. 从 git 找到最近的干净提交
git log --oneline -10
git show <commit>:<file> > /tmp/clean_base.html

# 2. 验证干净性
python3 -c "
html = open('/tmp/clean_base.html').read()
print(f'main={html.count(\"<main \")} body={html.count(\"</body>\")} sections={html.count(\"section-card\")}')
"

# 3. 以干净内容为基础重建，而不是修改破损文件
```

---

## 铁律二：写入后立刻验证，不允许假设成功

**场景**：Python `str.replace()` 插入 HTML 块，锚点字符串不匹配时静默失败

**正确做法**：
```python
# 写入后立刻最小验证
html = p.read_text("utf-8")
assert "<nav" in html, "nav HTML not written!"
assert html.count("<main ") == 1, f"Wrong main count"
assert html.count("section-card") >= 14, f"Missing sections"
```

---

## 铁律三：在 /tmp 验证渲染，再覆盖源文件

```bash
cp <output> /tmp/test.html
agent-browser open "file:///tmp/test.html"
agent-browser eval "document.querySelectorAll('.section-card').length"
# 确认正常后再覆盖源文件
```

---

## 铁律四：sync 脚本管理的目录，只改源头

**sl-ai-insight 工作流**：
```
内部版 (sl-ai-insight/)
  → sync_to_public.py → public/
  → sync_to_external.py → ai-insight-public/ (GitHub Pages)
```

**铁律**：只改 `sl-ai-insight/`，让脚本生成下游。直接改 `ai-insight-public/` 会在下次 sync 被覆盖。

---

## 铁律五：委托子Agent后必须验证产出

```bash
# 子Agent完成后第一件事
wc -c <file>     # 文件是否变了？
git diff --stat  # 有什么变化？
```

不信任摘要，只信任文件里的实际内容。
