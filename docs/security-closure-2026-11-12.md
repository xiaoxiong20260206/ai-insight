# KIM OpenAPI 泄露处置：未关闭事项

复核日期：2026-11-12。结论：不能判定全部排除。21:38 后继续按用户授权清理并执行公司指南。

## 已验证

- AI-Insight 本地 Git 对象库未命中本案旧 APP_KEY 或两组 SECRET_KEY。
- personal-assistant 先前仍有 50 个对象含旧 APP_KEY。已补充重写 161 个提交，移除三项含共享凭据的技能历史，并清除 OpenAPI 密钥格式、本案 APP_KEY 和另一硬编码凭据；隔离副本全对象扫描 0 命中。远端 main 已从 3ba87ef5 更新为 2535db0d，本地已对齐并清理不可达对象。
- 公开产物目录 ai-insight-public 的凭据扫描通过。
- 扫描器修正了正常根级 .git 的误拦截，扩展到 Python、.env、无扩展名和二进制文件；归档、超限文件及符号链接阻断发布。
- 外部同步在 pull/stash 恢复后再次扫描，避免只检查同步前状态。
- 6 项扫描器回归测试通过。项目及两份本地技能副本一致。
- 已添加并启用提交前暂存内容扫描；构造测试证明凭据提交被阻断，普通内容可以通过。
- 防复发代码已提交并推送至 ai-insight main，提交 126f0560。三个本地仓库（AI-Insight、github-backup、ai-insight-public）均已启用提交前扫描。github-backup 本地全部 Git 对象复核 0 命中上述凭据模式。远端两个仓库公开 Git refs 查询均只有 main；本轮查询 ai-insight 的开放 PR 为 0，未据此断言历史 PR 缓存不存在。
- 已删除 MyFlicker、CodeFlicker 本地三个含共享凭据技能的 SKILL.md，以及备份中的对应技能。没有调用这些共享凭据，也没有修改其他所有者的平台凭据。

## 尚未关闭

1. 旧提交仍可匿名读取且含本案 SECRET_KEY：
   https://raw.githubusercontent.com/xiaoxiong20260206/ai-insight/b10d70a4dbc05c4aed18a7c3fb1364f80c605cd1/scripts/send_openclaw_card.py
2. panscake/ai-insight 的 main 下 scripts/send_ai_daily.py 和 scripts/send_deep_research_card.py 仍命中 OpenAPI 密钥格式。未调用凭据接口。
3. Zhang-Yuanhang/ai-insight 与 ungjwefmoym3slo1-crypto/ai-insight 各有 2250 个 .git_disabled 元数据路径；本轮未完成其 Git 对象内容验证。
4. 平台侧凭据吊销未获证明。停止使用、删除脚本和历史重写均不等于服务端吊销。已通过 SSO 消息能力向指南指定联系人 liruisheng 请求使两组泄露凭据失效、处理已签发 token、提供失效证明并核查异常调用，消息接口返回成功。等待平台确认，不代表已吊销。
5. 删除本地技能并不等于删除技能市场当前版本和历史版本。市场侧下线、更新扫描及历史删除需要技能所有者或信安处理。

## GitHub Support 请求草稿（未发送）

仓库 xiaoxiong20260206/ai-insight 曾发布应用凭据，已重写所管理仓库历史。旧提交 b10d70a4dbc05c4aed18a7c3fb1364f80c605cd1 的 scripts/send_openclaw_card.py 仍可匿名读取敏感信息。请协助清除受影响的缓存视图、不可达提交和相关引用，并指导处理 fork network 中的残留。相关 fork 包括 panscake/ai-insight、Zhang-Yuanhang/ai-insight 和 ungjwefmoym3slo1-crypto/ai-insight。此请求不应包含明文密钥。

## 平台及信安核验请求（已向 liruisheng 发送，待回复）

请确认本案废弃 KIM OpenAPI 应用（此前记录 appId 559645）的全部泄露凭据均已吊销，提供不含密钥的吊销时间及状态证明，并核查泄露期间是否存在异常调用。如 MyFlicker 对应应用与该 appId 不同，请同时核验另一应用，避免只关闭其中一组。

## 关闭条件

- 两组泄露凭据均有平台失效证明。
- 旧提交和 fork 残留已清理或有平台/信安确认的处置记录。
- 补充清理旧 APP_KEY 后重新验证相关仓库历史（补充清理已执行）。
- 防复发修改验证通过并按授权发布。

以上事项未全部满足之前，不报告「问题全部排除」。

## 公司文档依据

- https://docs.corp.kuaishou.com/d/home/fcAAu5pQ-D90Uaaf30PAR9CmN/
- https://docs.corp.kuaishou.com/d/home/fcACJTHvbB9wv_FJ0AMTRZCJ-
- https://docs.corp.kuaishou.com/k/home/VfN7Pb329vTU/fcAABTTcpbocPTDSUzpxbyxps?ro=false

关键要求：泄露凭据先吊销或轮换；清理完整历史与全部引用；排查缓存和 fork；协作者避免回灌旧历史；提交前扫描；需要继续使用的技能迁移 OBO/SSO、环境注入或 keycenter；技能市场历史版本删除在反馈表备注并由信安处理。已废弃功能不再保留凭据或申请新凭据。
