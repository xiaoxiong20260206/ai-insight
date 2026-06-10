# 双版本同步

## 版本体系（v9.6 更正）

| 版本 | 路径 | 部署地址 |
|------|------|----------|
| 内部版 | `public/` | ai-insight-internal.frontend-cloud.corp.kuaishou.com（快手内网） |
| 外部版 | `ai-insight-public/` | xiaoxiong20260206.github.io/ai-insight-public/（GitHub Pages） |

> **⚠️ 重要变更**: 内部版已从 GitHub Pages 迁移到快手 frontend-cloud 内网。`xiaoxiong20260206.github.io/ai-insight/` **已废弃，不再使用**。
> 内部版所有链接统一指向 `ai-insight-internal.frontend-cloud.corp.kuaishou.com`。

## 脱敏规则

- 林克 → AI洞察
- 沈浪 → (删除)
- 快手 → (删除)

## 同步命令

```bash
uv run scripts/sync_to_external.py --full --verify
```

## P0规则

- ⛔ **禁止 raw cp**（会泄漏未脱敏内容）
- 必须加 `--verify` 验证敏感词零残留
- 首页变更 = sync必跑
- ⛔ **禁止sync后不commit**（教训49）

## 外部版首页禁止订阅按钮（v10.1）

外部版首页 `index.html` 必须删除订阅按钮区块和 `<a href="./subscribe/">` 链接及相关样式。

## 手动修改外部版HTML的URL替换规则（P0 — 2026-06-01）

根因：手动修改外部版周报时（绕过sync_to_external.py），只替换了 `ai-insight/` → `ai-insight-public/` 但漏了 `-v3.html` → `.html`。外部版日报文件名为 `2026-05-25.html`，内部版为 `2026-05-25-v3.html`。两项替换必须同时做。

硬规则：
1. 修改外部版HTML后，必须 `grep -c "\-v3\.html"` 返回 0（文件名和URL里的 `-v3` 都不能残留）
2. 修改外部版HTML后，必须 `grep -c "ai-insight/"` 在日报链接区域返回 0（不能残留内部版URL）
3. `sync_to_external.py` 已有这两条规则（REPLACEMENTS列表），脚本流程自动处理——只有手动修改才需要人工检查

## 内部版订阅页面架构（v10.2）

Appwrite 前端云不支持快手 OAuth Provider。替代方案：使用工号输入模式，绕过 OAuth 依赖，直接写入订阅表。

```javascript
// 正确的订阅写入方式（无需 OAuth）
const appwrite = new AppwriteClient();
await appwrite.createDocument({
    username: 'shenlang',
    is_active: true,
    subscribed_at: new Date().toISOString()
});
```