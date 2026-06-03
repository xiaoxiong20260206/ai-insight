# 信息图-章节映射规则（P0 — 2026-06-01）

**根因**：并行生图（`&`后台进程）后，bash 输出顺序取决于哪个进程先完成，不是按 prompt 顺序。拿到 URL 后直接按"第N个→第N章"假设映射，没有逐张验证内容。加上 AI 生图模型无法可靠渲染中文文字，连验证都做不到。导致图片和章节错位——第三章的图跑到第二章。

**硬规则**：

1. **信息密度高的配图（含数据/文字/对比）必须用 HTML→截图路径，不用 AI 生图**
   - AI 生图模型（Gemini）无法可靠渲染中文文字和数据，只擅长风格和构图
   - 数据图表、信息图、对比图 → `html-screenshot` skill（HTML写内容→Puppeteer截图→文字100%可控）
   - 艺术插画、情绪封面、概念图 → `designai-generate-image` skill（这些场景文字精度不重要）

2. **生图后必须逐张验证内容-章节对应关系**
   - 拿到图片后，用 `read` 工具查看每张图的实际内容
   - 确认图片内容与要放置的章节主题完全匹配
   - 发现错位 → 立即修正映射，不能假设"第一个=第一章"

3. **禁止并行生图后无验证直接写入文档**
   - 并行生图（`&`）的输出顺序不等于 prompt 顺序
   - 必须等全部完成 → 逐张验证 → 建立确认的映射表 → 再写入文档
   - 映射表格式：`| 章节名 | CDN URL | 验证结果(✅/❌) |`

4. **CDN上传：本地截图用 design-ai CDN endpoint**
   - KCDN busi_id=12276 无权限
   - 用 `curl -X POST "https://design-out.staging.kuaishou.com/private-api/common/upload-file"` + SSO cookies + `-F "file=@路径;type=image/png" -F "uploadType=2"` 上传
   - 脚本示例：`uv run --with requests --refresh-package ks_aimate bash upload_cdn.sh`（含 SmartSSOSession cookie 获取）
