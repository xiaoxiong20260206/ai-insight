# 泄露复查方法（与本次检查一致）

复查只读取状态码和返回码，不打印或保存 token、secretKey。

## 1. 凭据有效性

对泄露的 appKey/secretKey 请求 token 端点：

```bash
curl -s -o /tmp/token-check.json -w '%{http_code}\n' \
  -X POST https://is-gateway.corp.kuaishou.com/token/get \
  -H 'Content-Type: application/json' \
  -d '{"appKey":"<旧appKey>","secretKey":"<旧secretKey>","grantType":"client_credentials"}'

python3 -c 'import json;d=json.load(open("/tmp/token-check.json"));r=d.get("result") or {};print(d.get("code"),d.get("message"),r.get("appId"),bool(r.get("accessToken")))'
```

判定：

- 吊销成功：返回非 0 业务码（本次旧 KIM 凭据为 `40109 secret.key.error`），且无 accessToken。
- 仍有效：返回 `code=0` 且存在 accessToken，说明必须继续吊销。

## 2. 旧提交是否仍可读取

直接请求泄露提交的原始文件，不经过当前分支：

```bash
curl -s -o /tmp/old-file -w '%{http_code}\n' \
  'https://raw.githubusercontent.com/<owner>/<repo>/<旧commit>/<文件路径>'
grep -c '<旧密钥特征>' /tmp/old-file
```

判定：

- 返回 404，或文件不再包含旧密钥：该提交已不可读或已清理。
- 返回 200 且仍包含旧密钥：GitHub 缓存/不可达提交仍在，需要 GitHub Support 或信安处理；本地历史重写无法覆盖。

## 3. 新历史全量扫描

```bash
gitleaks git <repo> --log-opts=--all --redact --no-banner
git log --all --oneline -S'<旧密钥特征>'
git rev-list --all | xargs -I{} git grep -I -l -F '<旧密钥特征>' {} --
```

三条命令均无输出/退出码为 0，才可认定可达历史干净。该结论不覆盖 GitHub 缓存和他人副本。

## 4. 结论口径

- 凭据已吊销 + 新历史干净 + 旧提交不可读：复检通过。
- 凭据已吊销 + 新历史干净 + 旧提交仍可读：凭据风险已降低，但历史残留未关闭，不能报告完全通过。
