# P0红线完整版

## 1. 跨会话续接必须先resume（v9.3 经验教训）

**2026-03-19教训**: AI日报在跨会话续接时，只看到摘要说"Step 1和2已完成"就直接继续，未执行 `resume` 命令获取完整上下文，导致：
- Step 0.5 热点探针被跳过
- Step 2.5 质量门检查被跳过
- 搜索调研不充分，内容质量差

**根因**: 会话摘要只有结论，没有流程。

**强制规则**:
```bash
# 跨会话续接时的第一个命令（无例外）
python3 scripts/ai_daily_orchestrator.py resume
```

## 2. KIM卡片必须用脚本生成

**2026-03-14教训**: 手写了v2.0水平的简陋卡片推到群，缺失热度趋势、分类标签、深度聚焦、视觉层次。

**build_insight_mixcard.py 的 build_daily 函数包含完整卡片构建逻辑，手写不可能达到同等质量。永远使用脚本，永远不要手写。**

**注意**: 卡片包含热度趋势+动态+深度聚焦，规律洞察仅在网页版呈现。

## 3. KIM推送必须用 mixCard，禁止纯文本降级（v10.3 经验61）

**2026-04-29教训**: 容器重建后 KIM_APP_KEY/SECRET_KEY 丢失，send_ai_daily.py 无法运行（已废弃，改用 build_insight_mixcard.py）。Agent 退而求其次用 message 工具发了纯文本，完全丢失卡片结构。

**强制规则**: 
- 凭证缺失时不是降级为纯文本，而是走 mixCard 路径：
  ```bash
  python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD YYYY-MM-DD --output /tmp/card.json
  # 然后用 message(channel=kim, kimMixCard=<card>, ...) 发送
  ```
- **任何情况下日报推送必须包含完整的 block 结构**（header/subtitle/heat/sec1~5/capability/footer/buttons）
- 两条路径（直连API vs message工具）必须保持卡片 JSON 结构一致

## 4. KIM推送只执行一次（v10.0 经验55）

**2026-04-22教训**: 连续执行了两次旧版send_ai_daily.py（已废弃）（先 `--preview` 再正式发送），导致同一日报重复发送给用户。

**根因**: `--preview` 参数仅为语义标记，与无参数行为完全相同。

**强制规则**:
```bash
# 正确：只执行一次
# ⚠️ 旧版已废弃 | Work模式唯一路径: python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary

# 错误：执行两次 = 发送两次
```

## 5. 质量门失败=回到步骤重做，禁止修改数据 (v7.0 经验36)

**2026-03-15教训**: 质量门报告7项失败后，通过伪造WeChat URL、修改source日期等方式"修复"数据，导致6类严重问题全部由用户发现。

**v8.0结构性修复**: 质量门新增`check_date_tampering`（快照对比+可疑日期模式识别）和`check_closed_platform_urls`（封闭平台链接合规），从代码层面阻断伪造行为。

**质量门失败 → 唯一合法路径是回到对应步骤重做。修改数据使其通过检查 = P0违规 = 等同于伪造。**

## 6. 必须走orchestrator（v8.0 结构性约束）

**v8.0修复**: deploy_daily.sh新增Step 0a检查orchestrator状态文件，如果validate步骤未完成则阻断部署。

**orchestrator是唯一合法的日报发布路径。**

## 7. 6处联动失败=阻断，禁止绕过（v9.9 经验54）

**2026-03-21教训**: finalize报「6处联动失败」，Agent选择"先推了再说"，只执行了git push就标记完成——首页日历没更新、索引页没更新、外部版没同步。

**强制规则**:
1. finalize显示「6处联动失败」= 必须修复，禁止手动绕过
2. 修复后必须重跑finalize，直到显示「✅ 6处联动」
3. 标记Step 4完成前必须验证：
   ```bash
   python3 scripts/daily_quality_gate.py YYYY-MM-DD | grep "6处联动"
   # 必须显示 ✅ 才能标记完成
   ```

**6处联动检查清单**（全部必须✅）：
| # | 位置 | 检查内容 |
|---|------|---------|
| 1 | 日报索引页 | `01-daily-reports/index.html` 包含新日报条目 |
| 2 | 首页日历数组 | `index.html` reportsData 包含新日期数字 |
| 3 | 首页最新日报链接 | `index.html` list-item href 指向新日报 |
| 4 | 首页最新日报标题 | `index.html` list-item-title 包含新日期中文 |
| 5 | public/目录 | HTML文件已复制到public/ |
| 6 | 外部仓库 | `sync_to_external.py` 已同步到外部仓库 |

**反模式警示**: 「先推了再说」= 技术债的开始。看到门控报错选择绕过，比门控不存在更危险——因为你以为有保障其实没有。

## 8. 禁止raw cp，必须用脱敏脚本（v9.4）

**强制规则**:
```bash
# 唯一合法的同步命令（无例外）
python3 scripts/sync_to_external.py --full --verify
```

## 9. 外部版仓库必须首次克隆（v9.5）

```bash
# 首次环境准备（仅需执行一次）
cd /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight
git clone https://github.com/xiaoxiong20260206/ai-insight-public.git ai-insight-public
```

## 10. 外部版首页禁止订阅按钮（v10.1）

外部版首页 `index.html` 必须删除订阅按钮区块和 `<a href="./subscribe/">` 链接及相关样式。

## 11. 内部版订阅页面架构（v10.2）

Appwrite 前端云不支持快手 OAuth Provider。替代方案：使用工号输入模式，绕过 OAuth 依赖，直接写入订阅表。

## 12. 部署后端到端渲染验证（v9.6）

HTML生成后必须验证关键板块非空。gen_daily_html.py 现已内置渲染完整性检查。

## 13. 首页联动必须覆盖6处（v9.6）

deploy_daily.sh v2.0 已自动化6处联动，每次部署后验证输出中应有全部6个✅。

## 14. 禁止sync后不commit（教训49）

sync_to_public.py会修改public/index.html，必须确保git commit覆盖此文件。

## 15. 容器重建后必须恢复环境（v10.4 经验75）

**2026-04-30教训**: 容器重建后本地项目目录丢失，日报cron session静默跳过了HTML生成和部署，只完成KIM推送——用户点击链接404。

**强制规则**: 日报流程执行前必须验证环境就绪：
```bash
# Step 0 环境前置检查（每次执行必须跑）
# 1. 项目目录
ls /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/.git/HEAD || echo "PROJECT_MISSING"
# 2. Git连通性（SSH优先）
ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | grep "successfully authenticated" || echo "GIT_UNREACHABLE"
# 3. SSH key
ls ~/.ssh/id_ed25519 || echo "SSH_KEY_MISSING"
# 4. git-credentials
ls ~/.git-credentials || echo "CREDENTIALS_MISSING"
```

**任何一项MISSING = 日报流程不可继续 = 必须先恢复环境再执行日报。禁止"只推送KIM跳过部署"。**

恢复路径（按HEARTBEAT.md流程执行）：
- SSH key: 从workspace `.ssh-backup/` 恢复
- git-credentials: 从workspace `.github-credentials-backup/` 恢复
- 项目仓库: `git clone git@github.com:xiaoxiong20260206/ai-insight.git /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight`
- 外部仓库: `git clone git@github.com:xiaoxiong20260206/ai-insight-public.git /data/aime/48b01692-87fe-48a1-860d-a6ab789801e6/workspace/user-skills/sl-ai-insight/../ai-insight-public`
- git config: `user.name=Link, user.email=link@internal.company, credential.helper=store`

## 16. Git操作SSH优先原则（v10.4 经验75）

**2026-04-30教训**: 在快手内网容器环境中，GitHub HTTPS(443)端口经常不通（连接超时），但SSH(22)端口稳定可用。

**强制规则**:
```bash
# ✅ 正确：SSH方式（22端口稳定可用）
git clone git@github.com:xiaoxiong20260206/ai-insight.git
git push origin main

# ❌ 错误：HTTPS方式（443端口经常不通）
git clone https://github.com/xiaoxiong20260206/ai-insight.git
```

**所有git clone/push操作一律使用SSH格式 `git@github.com:...`，除非明确验证HTTPS可达。**

**首次使用需生成SSH key并添加到GitHub**：
```bash
ssh-keygen -t ed25519 -C "link@internal.company" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub  # → 添加到GitHub Settings > SSH Keys
```

- **时间窗口**: N日日报 = N-1日08:00 ~ N日08:00 的内容
- **链接质量三角**: 可达性 × 新鲜度 × 权威性
- **国内覆盖**: ≥3条分布在≥2个板块
- **微信覆盖(v6.0)**: ≥2条直接引用微信文章（URL用公开转载或搜狗搜索URL，禁止mp.weixin临时链接）
- **小红书(v9.8)**: 默认不搜索，仅当用户明确要求时才执行
- **6处联动**: MD+HTML+跳转页+索引+首页+JSON
- **推送范围**: 日报仅发2个群（CF项目群 + 研发效能中心全员群），周报发所有群

## 17. 失败自修复原则（v10.5 — 5/4教训）

**2026-05-04教训**: AI日报cron连续多日失败（python命令、权限问题、空壳JSON、质量门失败后仍推送），每次都是用户发现后手动要求"重跑"或"修复"。这违反了"一次性把事情做对"的原则——失败发生后应该**立即自修复并完成**，而不是停下来等用户处理。

**强制规则**:
1. **任何步骤失败 = 立即尝试修复，不要停下来汇报**
2. **修复路径优先级**：
   - 环境问题（python→python3、路径权限→改workspace路径）→ 直接替换重试
   - 数据问题（空壳JSON、质量门失败）→ 回到对应步骤重做
   - 部署问题（脚本bug）→ 手动修复+继续流程
   - 推送问题（权限/凭证缺失）→ 切换到可用路径（如从直连API切换到mixCard）
3. **最多重试3次**：同一步骤连续3次失败后才通知用户，附带完整的失败原因和已尝试的修复方案
4. **完成优先于完美**：如果某个非关键步骤（如6处联动脚本bug）反复失败，手动完成该步骤（如直接编辑文件），不要因为脚本问题而停滞整个流程
5. **禁止半成品交付**：不能因为"搜索完成了、内容空壳了"就标记step为completed然后停手。每一步必须**验证实际产出**，而非只看state标记
6. **自修复完成后仍需通知用户**：修复成功后发一条简短通知，说明"原计划失败+修复方案+最终结果"，让用户知道发生了什么但不需要他干预

**自我诊断清单**（每次执行前快速检查）：
```
state.json标记completed → 验证实际文件内容是否非空
python命令 → 确认用python3
写入路径 → 确认有权限（优先用workspace路径）
脚本报错 → 读错误信息→定位根因→尝试替代方案→最多3次
质量门失败 → 回步骤重做，禁止绕过
```
---

## 18. Work模式唯一推送路径（v10.6 — 经验#102/#103/#105）

**2026-05-04教训**: Work模式容器无KIM_APP_KEY/SECRET_KEY，旧版KIM直连脚本（send_ai_daily.py等）完全不可用。workflow写"二选一"导致Agent浪费时间尝试必失败的路径B。

**强制规则**：
```bash
# Work模式唯一推送路径（禁止"二选一"误导）
python3 scripts/build_insight_mixcard.py daily --date YYYY-MM-DD --output /tmp/card.json --with-summary
# 然后读取 card.json，用 message(channel=kim, kimMixCard=<card>) 发送

# ❌ 禁止尝试 send_ai_daily.py（无凭证=必失败）
# ❌ 禁止纯文本降级（丢失卡片结构）
# ❌ 禁止维护多个 mixCard 生成脚本（唯一入口: build_insight_mixcard.py）
```

**废弃脚本清单**（已归档 `_archive/deprecated-work-mode/`）：
- send_ai_daily.py, send_ai_weekly.py, send_*_card.py（6个KIM直连推送脚本）
- build_daily_mixcard.py（被build_insight_mixcard.py替代）
- kim_client.py, subscription_api.py, subscription_manager.py（需KIM凭证）
- com.cf.*.plist, run-ai-*-report.sh（macOS launchd配置）

---

## 19. mixCard卡片结构锚定（v10.6 — 经验#98/#99/#100/#101）

**2026-05-04教训**: 周报卡片缺footer/subtitle，URL指向错误路径404，文件查找硬编码月份找不到。

**强制规则**：
```
卡片结构锚定（所有场景 daily/weekly/research/product 必须遵守）：
1. header    — 标题（日期/周号）
2. subtitle  — 概览行（条数/板块覆盖/关键词）
3. content   — 各内容block（sec1-5 / top5 / insight等）
4. footer    — 签名行 "*林克（沈浪的AI分身）· AI洞察 · XX*"
5. buttons   — 双按钮（查看完整内容 + 了解AI洞察项目）
6. 各block之间用 divider 分隔

缺失任何一项 = 阻断，禁止推送
```

**URL验证规则**：
- 按钮 URL 必须与实际文件路径一致
- 周报 URL 使用月份目录路径（非扁平路径）
- 生成后必须 `curl -I` 验证 HTTP 200

**深度聚焦截断规则**：
- summary 截断上限 ≥ 200字（100字只保留30%内容，不可接受）
- takeaway（关键判断）永远不截断
- 周报文件查找必须动态计算月份（禁止硬编码）
