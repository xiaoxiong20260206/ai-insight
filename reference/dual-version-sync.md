# 双版本同步

## 版本体系（v9.5 更正）

| 版本 | 路径 | GitHub Pages |
|------|------|--------------|
| 内部版 | `../AI-Insight/` | xiaoxiong20260206.github.io/ai-insight/ |
| public | `../AI-Insight/public/` | （同上，部署源） |
| **外部版** | `../ai-insight-public/` | **xiaoxiong20260206.github.io/ai-insight-public/** |

> **⚠️ 注意**: 外部版仓库是**独立仓库**（`ai-insight-public`），不是 `ai-research` 的子目录。
> `ai-research/ai-insight-public/` 是历史遗留的另一个副本，**已废弃**。

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