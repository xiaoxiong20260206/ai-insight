# 公司安全要求验收对照表

核验日期：2026-11-13。总体结论：代码及受控历史整改完成，安全事件尚未完全闭环。

| 公司要求／问题 | 已做修改／处置 | 实测效果 | 状态 |
| --- | --- | --- | --- |
| 废弃 KIM OpenAPI 不再保留凭据 | 删除旧脚本、机器人、凭据配置及相关技能；补充清理旧 APP_KEY 历史 | 受控历史的针对性扫描未发现本案旧值 | 已整改 |
| 完整 Git 历史清理 | ai-insight 已重写；personal-assistant 再补充重写并移除旧技能备份、yuque-publisher、kim-ai-bot 历史路径 | personal-assistant 最新 main 为 881cd4f5；本地对齐并清理不可达对象 | 已推送 |
| 扩大检查范围 | 安装 Gitleaks 8.30.1，执行全可达历史和本地技能目录扫描 | 发现备份历史 54 条告警、7 个不同匹配值；全部替换／移除后重新扫描为 0 | 已整改 |
| 防止忽略本地技能副本 | 删除 MyFlicker、CodeFlicker 的含硬编码语雀凭据技能；修改 Coze 文档中的演示凭据为明确占位符 | 两套 skills 目录的 Gitleaks 扫描退出码均为 0、告警均为 0 | 已验证 |
| 提交前阻断 | 启用暂存内容扫描及 Gitleaks；补充重命名／类型改变文件、.env.*、大写 API_KEY、JSON 字段、私钥标记检查 | 已实际阻断测试源码中的私钥字面量；改为运行时拼接测试数据后正常提交。没有关闭扫描来通过提交 | 已验证 |
| 推送前阻断历史泄露 | 新增 pre-push 执行 Gitleaks 全可达历史扫描；三个本地仓库共用扫描入口 | AI-Insight 修改提交 4593b617，已推送；全历史扫描通过 | 已启用 |
| 避免误报掩盖问题 | 搜狗公开文章跳转 URL 的查询 token 经人工核验为非应用凭据，仅对白名单文件中确定的 URL 行作窄范围允许 | AI-Insight 原 3 条告警不再误报；没有关闭通用规则或允许整个文件 | 已核验 |
| 公开产物安全 | 文件扫描扩展到不同扩展名；归档、超限文件、符号链接阻断；同步 pull/stash 恢复后再次扫描 | ai-insight-public 文件扫描通过，Git 历史 Gitleaks 扫描为 0 告警 | 已验证 |
| 回归验证 | 执行扫描器测试、格式差异检查及实际提交／推送门禁 | 7 项 unittest 通过；git diff --check 通过 | 已验证 |
| 凭据吊销／轮换 | 已向公司指南指定联系人 liruisheng 发送两组凭据失效、已签发 token 处置及异常调用核验请求；废弃功能无需下发新凭据 | 消息发送成功，但没有平台失效证明。新发现的语雀等第三方凭据也需要所有者确认失效 | 未关闭 |
| GitHub 缓存、PR、fork | 已排查公开 refs、开放 PR 和 fork；准备不含密钥的 GitHub Support 请求 | 旧提交匿名请求仍返回 HTTP 200；没有 Support 受理单或缓存清理证明。fork 不受本账号直接控制 | 未关闭 |
| 技能市场历史版本 | 已移除本地技能和受控备份，但未据此宣称市场版本删除 | 尚无市场下线、历史版本删除或市场安全扫描验收结果 | 未关闭 |
| 协作者避免旧历史回灌 | 受控本地仓库已经同步新历史，配置提交／推送门禁；查询 ai-insight 协作者仅返回本人账号 | 不能证明所有旧克隆和 fork 已迁移。克隆到新设备后仍需启用 hooks 并安装 Gitleaks | 部分完成 |
| 新发现：ks-ai-productivity-landing | 公开历史含 MyFlicker 凭据，已重写 21/40 个提交，移除日志文件，替换 6 个不同匹配值并强推 | 新 main 为 bc13185；Gitleaks 全历史 0 告警，针对性残留 0；本地副本已对齐并清理不可达对象 | 已整改 |
| 新发现：appId 559979 | MyFlicker 凭据仍可换 token；已向 liruisheng 发送吊销、token 处置和异常调用核验请求 | 2026-11-13 复查返回 code=0 且存在 accessToken，说明仍有效；请求已发送但无失效证明 | 未关闭 |
| 原 KIM appId 559645 | 用旧凭据复查 token 端点 | 返回 40109 secret.key.error，无 accessToken，旧凭据已不可用；吊销时间待平台确认 | 待平台确认 |
| 旧提交缓存复查 | 直接请求旧 commit 原始文件 | ai-insight b10d70a4 仍返回 200 且含旧 KIM 凭据；ks-ai-productivity-landing 的 5b90e2c 等旧提交仍返回 200 且含 MF 凭据 | 未关闭 |

## 本轮最终扫描

| 扫描对象 | 扫描方式 | 结果 |
| --- | --- | --- |
| AI-Insight | Gitleaks git --log-opts=--all | 退出码 0，0 告警（上述搜狗 URL 窄范围规则生效） |
| github-backup／personal-assistant | Gitleaks git --log-opts=--all | 退出码 0，0 告警 |
| ai-insight-public | Gitleaks git --log-opts=--all | 退出码 0，0 告警 |
| MyFlicker skills | Gitleaks dir | 退出码 0，0 告警 |
| CodeFlicker skills | Gitleaks dir | 退出码 0，0 告警 |

扫描未发现问题不等于凭据已失效，也不保证扫描器识别所有未知格式。该结论仅适用于上述对象和已扫描可达历史，不覆盖 GitHub 不可达缓存、他人设备、技能市场和服务端权限。

## 完全闭环仍需取得

1. 平台及相应第三方凭据所有者的失效证明，包含已签发 token 的处置结论。
2. GitHub Support／信安对缓存和 fork 的处置记录；本轮没有提交成功证明，不把草稿算作已提交。
3. 技能市场当前版本和历史版本的下线／整改验收证明。
4. 旧副本所有者完成历史迁移或给出可接受的风险处置确认。

未取得以上证明前，不报告「完全符合公司安全标准」或「所有风险排除」。
