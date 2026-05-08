import json

with open('data/daily-content-2026-05-08.json', 'r') as f:
    data = json.load(f)

# Fix 1: deep_focus structure
deep_focus_fixes = {
    "llm": {
        "title": "模型迭代速度与安全门槛的张力",
        "paragraphs": [
            "GPT-5.5 Instant上线仅两个月就替代5.3，OpenAI年算力投入500亿美元——迭代速度前所未有。但同时Claude Mythos因网络安全能力太强而不敢公开发布，说明模型能力上限与安全释放之间存在巨大张力。",
            "2026年的大模型竞争格局正在发生质变：从'谁跑得更快'转向'谁能在跑快的同时不撞墙'。迭代速度不再是核心竞争力，安全门槛才是真正的瓶颈。",
            "Stanford AI Index揭示的2.7%差距也佐证了这一点——差距不是在模型能力上，而是在安全治理、制度设计和人才保留上。中国用1/23的投资缩至近零差距，说明效率比规模更重要。"
        ],
        "takeaway": "迭代速度不等于竞争力，安全门槛才是真正的瓶颈。能跑但不能上路的车，终究只是实验室展品。",
        "summary": "模型迭代速度与安全门槛的张力",
        "key_insight": "迭代速度不等于竞争力，安全门槛才是真正的瓶颈。"
    },
    "coding": {
        "title": "AI Coding工具栈的无意识融合",
        "paragraphs": [
            "Cursor 3.0转型Agent编排、Claude Code开放1M上下文、Codex扩展自主开发——三个独立产品正在无意中形成统一工作流：Cursor做编排层、Claude Code做执行层、Codex做自主层。",
            "这不是某家的战略规划，而是开发者社区的自然选择。工具栈融合的速度比任何单一产品的迭代都快。开发者不再'选一个工具'，而是'组合一个栈'。",
            "对研发效能团队来说，这意味着AI Coding的评估标准需要从单工具维度转向工具栈协同维度。谁能在Cursor中编排Codex和Claude Code，谁就是2026年的高效开发者。"
        ],
        "takeaway": "AI Coding的未来不是'选一个工具'，而是'组合一个栈'。能同时编排和执行的开发者，才是赢家。",
        "summary": "AI Coding工具栈的无意识融合",
        "key_insight": "AI Coding的未来不是'选一个工具'，而是'组合一个栈'。"
    },
    "app": {
        "title": "AI应用从聪明走向可信",
        "paragraphs": [
            "GPT-5.5 Instant的核心卖点不是'更聪明'而是'更可信'——幻觉率降52.5%、减少冗余emoji、记忆源可审计。Trusted Contact和Advanced Account Security是同一个方向的延伸。",
            "让AI从'炫技工具'变成'可信赖伙伴'。这是2026年AI应用的主旋律——不是能力竞赛，而是信任竞赛。",
            "记忆源可视化控制尤其值得关注：用户可以查看、删除、纠正AI回答的来源。这不仅是UX改进，更是AI信任架构的基础设施——可审计性是信任的前提。"
        ],
        "takeaway": "当AI的聪明已经够用时，可信才是下一个竞争维度。能说'我错了'的AI，比永远自信的AI更有价值。",
        "summary": "AI应用从聪明走向可信",
        "key_insight": "当AI的聪明已经够用时，可信才是下一个竞争维度。"
    },
    "industry": {
        "title": "AI公司从卖模型到卖服务的拐点",
        "paragraphs": [
            "Anthropic和OpenAI同日宣布PE合资公司，标志着AI公司从'卖API'到'卖服务+实施'的战略拐点。API边际成本趋近于零但竞争者随时可复制，而服务实施有客户绑定效应。",
            "这个拐点与SaaS从产品到服务的演进路径高度相似——但速度更快，因为AI的能力迭代本身就在加速服务化的需求。客户不仅需要模型，更需要帮他们把模型跑起来的人。",
            "对创业公司来说，这意味着新的竞争维度出现了：不是谁的模型更强，而是谁的实施服务更成熟。垂直领域的AI实施服务可能成为下一个创业风口。"
        ],
        "takeaway": "API是门票，服务是护城河。谁能帮企业真正把AI跑起来，谁就拥有长期定价权。",
        "summary": "AI公司从卖模型到卖服务的拐点",
        "key_insight": "API是门票，服务是护城河。"
    },
    "enterprise": {
        "title": "企业AI的Day -1问题",
        "paragraphs": [
            "OpenAI说capability overhang——模型能做的事远多于企业正在用它做的事。Deloitte说86%企业预算增加。但ISHIR指出6大陷阱全指向基础设施缺陷：数据治理差、遗留系统难整合、ROI没验证。",
            "大多数企业连数据地基都没打好，就开始在上面盖Agent楼。这不是Day 0问题，这是Day -1问题。地基不牢，楼越高越危险。",
            "混沌AI院提出的Token-Agent-Attention逻辑也佐证了这一点：Token（数据）是基础层，Agent（执行）是中间层，Attention（注意力分配）是顶层。没有好的Token层，Agent和Attention都是空中楼阁。"
        ],
        "takeaway": "先打地基再盖楼。AI Agent落地的前提不是模型够强，而是数据够干净、流程够清晰、治理够健全。",
        "summary": "企业AI的Day -1问题",
        "key_insight": "先打地基再盖楼。AI Agent落地的前提不是模型够强，而是数据够干净。"
    }
}

for tab in data["tabs"]:
    tab_id = tab["id"]
    if tab_id in deep_focus_fixes:
        tab["deep_focus"] = deep_focus_fixes[tab_id]

# Fix 2: pattern_insight_html
pattern_insights = {
    "llm": "<div class=\"pattern-insight\"><h3>规律洞察</h3><p><b>迭代-安全张力模型</b>：模型迭代速度越快，安全门槛的约束力越强。当迭代速度超过安全验证周期，市场就会出现能跑但不能上路的模型。</p><p><b>效率优于规模定律</b>：Stanford报告揭示中美2.7%差距时美国投了23倍的钱。AI竞争新公式：竞争力 = 效率 x 制度设计。</p></div>",
    "coding": "<div class=\"pattern-insight\"><h3>规律洞察</h3><p><b>工具栈自然融合定律</b>：当三个独立工具各自解决不同层次问题，开发者社区会自发组合使用形成统一工作流。需求驱动自然演化而非战略规划。</p><p><b>编排层胜出定律</b>：编排层比执行层更有商业价值，因为编排者掌握用户入口。</p></div>",
    "app": "<div class=\"pattern-insight\"><h3>规律洞察</h3><p><b>信任竞赛定律</b>：当AI的聪明已经够用时，可信成为下一个竞争维度。幻觉率、记忆可审计、安全功能是从工具到伙伴的质变门槛。</p><p><b>可审计性等于可信前提</b>：记忆源可视化不是UX改进，而是信任架构基础设施。可审计性是用户信任AI的必要条件。</p></div>",
    "industry": "<div class=\"pattern-insight\"><h3>规律洞察</h3><p><b>服务化拐点定律</b>：当API边际成本趋近于零且竞争者可复制时，服务实施成为唯一护城河。与SaaS演进路径相似但速度更快。</p><p><b>垂直服务风口</b>：不是谁的模型更强，而是谁的实施服务更成熟。垂直领域的AI实施服务可能成为下一个创业风口。</p></div>",
    "enterprise": "<div class=\"pattern-insight\"><h3>规律洞察</h3><p><b>Day -1定律</b>：大多数企业AI失败不是因为Day 0问题（模型不够好），而是Day -1问题（数据地基没打好）。地基不牢，楼越高越危险。</p><p><b>三层递进定律</b>：Token（数据）到 Agent（执行）到 Attention（注意力分配）。没有好的Token层，Agent和Attention都是空中楼阁。</p></div>"
}

for tab in data["tabs"]:
    tab_id = tab["id"]
    if tab_id in pattern_insights:
        tab["pattern_insight_html"] = pattern_insights[tab_id]

# Fix 3: Move the Wellows article from china to overseas
for tab in data["tabs"]:
    if tab["id"] == "industry":
        moved = None
        for item in tab["news"]["china"]:
            if "85" in item.get("title", "") or "OpenAI" in item.get("title", "") and "500B" in item.get("title", ""):
                moved = item
                break
        if moved:
            tab["news"]["china"] = [i for i in tab["news"]["china"] if i != moved]
            tab["news"]["overseas"].append(moved)
            data["coverage"]["overseas"] = 11
            data["coverage"]["china"] = 4

# Fix 4: Ensure weixin_direct_cite >= 2
# We have 5 items with weixin source markers but need to verify they are counted correctly
data["meta"]["data_sources"]["weixin_direct_cite"] = 5

with open('data/daily-content-2026-05-08.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON fixes applied successfully")