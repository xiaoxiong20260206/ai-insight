# Evolution Log — sl-ai-insight

## 2026-05-09 修炼洞察

### 洞察1: isolated session 环境不可靠
- **issue**: uv命令在isolated session PATH中缺失，导致AI日报3次失败
- **rule**: cron payload必须包含环境自检+自安装逻辑
- **action**: ✅ 已修复日报cron；⚠️ 其他uv依赖cron也应加自检
- **成熟度**: 🌿生长（第1次提取）

### 洞察2: 域账号变更需全链路同步
- **issue**: shenlang→shenlang03变更未同步到cron/subscribers/USER.md
- **rule**: 域账号变更必须更新所有引用点
- **action**: ✅ 已完成10个cron+subscribers+USER.md
- **成熟度**: 🌱萌芽（第1次提取）

### 洞察3: 日报MixCard结构不完整
- **issue**: 缺少内部版链接、林克说明段、订阅按钮
- **rule**: MixCard必须三要素齐全：内部链接+身份说明+订阅入口
- **action**: ⏳ 待确认内部版URL和按钮形式
- **成熟度**: 🌱萌芽（第1次提取，待验证）

### 洞察4: 重大事件进展追踪缺失
- **issue**: DeepSeek融资用的是旧链接($200亿)，实际已到$450亿+国家大基金
- **rule**: 搜索调研对重大事件必须做进展追踪，不只搜第一波报道
- **action**: ⏳ 需更新日报+补充workflow进展追踪规则
- **成熟度**: 🌱萌芽（第1次提取，待验证）

### 洞察5: mixcard脚本未引用config.py SSoT
- **issue**: INTERNAL_BASE硬编码而非从config.py import
- **rule**: URL配置必须从config.py SSoT读取，禁止硬编码
- **action**: ⏳ 待修复（先等内部版URL确认）
- **成熟度**: 🌱萌芽（第1次提取）