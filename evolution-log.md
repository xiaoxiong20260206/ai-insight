# Evolution Log — sl-ai-insight

## 2026-05-09 修炼洞察

### 洞察1: isolated session 环境不可靠
- **issue**: uv命令在isolated session PATH中缺失，导致AI日报3次失败
- **rule**: cron payload必须包含环境自检+自安装逻辑
- **action**: ✅ 已修复日报cron；✅ 已修复技能度量周统计cron
- **成熟度**: 🌿生长（第1次提取→第2次提取修复2个cron）

### 洞察2: 域账号变更需全链路同步
- **issue**: shenlang→shenlang03变更未同步到cron/subscribers/USER.md
- **rule**: 域账号变更必须更新所有引用点
- **action**: ✅ 已完成10个cron+subscribers+USER.md
- **成熟度**: 🌱萌芽（第1次提取）

### 洞察3: 日报MixCard结构不完整
- **issue**: 缺少内部版链接、林克说明段、订阅按钮
- **rule**: MixCard必须三要素齐全：内部链接+身份说明+订阅入口
- **action**: ⏳ 待确认订阅按钮形式
- **成熟度**: 🌱萌芽（第1次提取，待验证）

### 洞察4: 重大事件进展追踪缺失
- **issue**: DeepSeek融资用的是旧链接($200亿)，实际已到$450亿+国家大基金
- **rule**: 搜索调研对重大事件必须做进展追踪，不只搜第一波报道
- **action**: ✅ 05-10/05-11日报已包含最新进展
- **成熟度**: 🌿生长（第1次提取→第2次验证生效）

### 洞察5: mixcard脚本未引用config.py SSoT
- **issue**: INTERNAL_BASE硬编码而非从config.py import
- **rule**: URL配置必须从config.py SSoT读取，禁止硬编码
- **action**: ⏳ 待修复（先等内部版URL确认）
- **成熟度**: 🌱萌芽（第1次提取）

## 2026-05-11 修炼洞察

### 洞察6: 数据契约不一致是自动化流程的慢性杀手
- **issue**: build_insight_mixcard.py读`heat_trend.topics`但数据写`heat_trend.top_items`，导致heat block缺失
- **rule**: 所有脚本间数据传递必须有明确schema约定，消费方必须兼容生产方的多种数据格式
- **action**: ✅ 已修复脚本（兼容top_items+topics两种格式）
- **成熟度**: 🌿生长（第1次提取→第2次代码修复生效）

### 洞察7: P0降级违规——遇到技术困难时宁可延迟不可降级
- **issue**: MixCard推送参数类型问题→改发纯文本→违反P0红线"禁止纯文本推送"
- **rule**: P0红线是底线不是建议，遇到技术困难宁可延迟送达不可降级方案
- **action**: ✅ 已补充到workflow P0红线
- **成熟度**: 🌿生长（第1次提取→第2次写入skill规则）

### 洞察8: 搜狗搜索依赖过度+URL截断+source篡改
- **issue**: cron session搜索质量差：sogou占比44%超阈值+URL截断+source篡改
- **rule**: 搜狗搜索URL只作Step B兜底，优先36kr/huxiu公开转载；搜索结果必须包含真实可访问URL
- **action**: ✅ 已补充workflow搜索质量红线
- **成熟度**: 🌿生长（第1次提取→第2次写入skill规则）

### 洞察9: 推送可观测性盲区——delivered≠实际送达
- **issue**: cron delivered=true但用户没收到MixCard卡片，delivery机制和session内部推送是两个独立通道
- **rule**: 自动化推送必须有端到端验证，推送后必须验证卡片结构完整性
- **action**: ✅ 已补充workflow推送验证规则
- **成熟度**: 🌿生长（第1次提取→第2次写入skill规则）
### [2026-06-14] cron周补录：sl-ai-insight被调用
- **来源任务**：skill_calls.md周度兜底补录
- **模式描述**：该技能在本周6/10-6/14被每日AI洞察cron调用5次，产出日报5份+周报1份。关键洞察：基建竞赛加速+AI编程速度悖论+企业AI三重门+豆包付费+监管套利。W24周报首页部署失败暴露git push≠网页部署问题，已修复
- **成熟度**：🌱萌芽
