# 泄露复查方法（与本次检查一致）

复查只读取状态码和返回码，不打印或保存 token、secretKey。只在平台授权或明确的安全复验任务中执行，凭据通过交互输入，不能放进命令行、截图、聊天或固定临时文件。不发送消息、不枚举群组。

## 1. 凭据有效性

对泄露的 appKey/secretKey 请求 token 端点：

请求体为 `appKey`、`secretKey` 和 `grantType=client_credentials`，响应仅在内存中解析并丢弃。只输出 HTTP 状态、业务返回码、appId 和是否包含 accessToken，不能输出完整响应、cookie 或 token。

判定：

- 旧凭据被拒绝：HTTP 200、业务码为明确的凭据错误（本次旧 KIM 凭据为 `40109 secret.key.error`），且无 accessToken。这证明该次换取被拒绝，不单独证明吊销时间、所有凭据均失效或已签发 token 失效，仍需平台确认。
- 仍有效：返回 `code=0` 且存在 accessToken，说明必须继续吊销。
- 无法判断：网络超时、403／SSO 页面、5xx、非 JSON、未知错误码，以及 `code=0` 但无 token 等不一致响应。不能把这些情况当成吊销成功。

## 2. 旧提交是否仍可读取

直接请求泄露提交的原始文件，不经过当前分支：

```bash
curl -s -o /tmp/old-file -w '%{http_code}\n' \
  'https://raw.githubusercontent.com/<owner>/<repo>/<旧commit>/<文件路径>'
grep -c '<旧密钥特征>' /tmp/old-file
```

判定：

- 匿名请求确认返回 404：该指定路径在该次检查不可读，不代表其他路径、fork 或缓存全部清理。
- HTTP 200 且确认获得预期源文件、正文无旧密钥：该文件不再包含所检查旧值，不代表整个提交已清理。
- 返回 200 且仍包含旧密钥：GitHub 缓存/不可达提交仍在，需要 GitHub Support 或信安处理；本地历史重写无法覆盖。
- 超时、403、429、5xx、登录页或错误正文：检查不确定，不能用“未搜索到密钥”判为通过。

## 3. 新历史全量扫描

```bash
gitleaks git <repo> --log-opts=--all --redact --no-banner
git log --all --oneline -S'<旧密钥特征>'
git rev-list --all | xargs -I{} git grep -I -l -F '<旧密钥特征>' {} --
```

Gitleaks 退出码 0 表示未发现告警；`git log -S` 成功且无输出表示未发现匹配变更。`git grep` 的退出码 1 表示没有匹配，0 表示发现匹配，大于 1 表示命令错误；因此不能要求上述所有命令都退出 0。逐个检查全部可达提交，发现任何匹配或扫描错误都不能通过。该结论不覆盖 GitHub 缓存和他人副本。

## 4. 结论口径

- 凭据已吊销 + 新历史干净 + 旧提交不可读：复检通过。
- 凭据已吊销 + 新历史干净 + 旧提交仍可读：凭据风险已降低，但历史残留未关闭，不能报告完全通过。
