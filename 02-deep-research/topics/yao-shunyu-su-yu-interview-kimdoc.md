# 【林克的AI洞察】英雄退场，浪潮上场
## 姚顺宇×苏煜两篇访谈揭示的AI深层规律
🌐 Web 交互版：强烈推荐访问 👉 [英雄退场，浪潮上场](https://xiaoxiong20260206.github.io/ai-insight-public/02-deep-research/topics/yao-shunyu-su-yu-interview.html)

![[封面：两篇访谈揭示AI行业从英雄时代到工程时代的深层收敛](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae6.jpg)](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae6.jpg)

# 00 全文概览：先说结论
![概览：两篇访谈的核心收敛](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae6.jpg)
一件正在发生的事：AI行业正在从"天才驱动的手艺活"转向"工程驱动的工业活"。
它带来了一个问题：当技术、模型能力都差不多时，什么才是真正的壁垒？
| | |
| --- | --- |
| 旧理解 | 新理解 |
| 天才直觉是壁垒 | 工程可靠性是壁垒 |
| 个人英雄驱动 | 集体系统驱动 |
| 炫技模式 | 靠谱模式 |
📌 AI的下一个壁垒不是"更聪明"，而是"更靠谱"。

# 01 英雄已死——集体主义的胜利
![从英雄时代到工程时代](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae7.jpg)
姚顺宇在访谈中反复强调一句话："AI个人英雄主义时代已经过去了。"他在Anthropic参与了Claude 3.7/4.5的训练，在DeepMind参与了Gemini 3——这些不是一个人的成就，而是上百人的集体工程。
他说得更直白："没有哪个老登是你的亲属，所以你觉得他傻，他就是傻，就可以直接说他傻。"
当描述自己时，他说："我自己对那个事没那么重要，更多的是，我很幸运，有机会在那个时候加入了一个重要的项目，做了一些事。"
苏煜从学术视角给出了平行论证：Agent贯穿AI 70年历史，从1960年代的Logical Agent到今天的Language Agent——每一步都是几十人、几百人的集体工作。
规律很简单：模型规模扩大→训练成本指数级上升→一次失败不可承受→工程纪律成为刚性约束→"靠谱"成为最稀缺的品质。
类比：冲浪者与浪。"本质上是那个浪，而不是你那个冲浪的人。"冲浪者的技术重要，但决定能走多远的是浪本身。在AI行业，"浪"是算力、数据、infra和团队协作的系统性能力。
回验：模型训练团队上百人（✅匹配）、姚顺宇"我不重要"（✅匹配）、Cursor小团队成功（❌例外——但姚顺宇解释了：应用层仍有英雄空间，前提是市场够窄、速度够快）。
📌 模型训练的壁垒已经从"天赋直觉"转移到了"工程可靠性"。能复现的实验比一次性的灵感更值钱。

# 02 Agent 70年——技术史的收敛与语言脚手架
![Agent技术70年收敛弧线](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae8.jpg)
苏煜引用Stuart Russell的亲口说法：《Artificial Intelligence: A Modern Approach》不是一本AI书，而是一本关于Agent的书。Agent研究从AI诞生之初就是核心问题。
四条流汇聚：Logical Agent（1960-90s）→ Neural Agent（2000s+）→ Semantic Parsing（2010s）→ Language Agent（2022+）。苏煜是少数横跨Semantic Parsing和Language Agent的学者。
这一代Agent的根本差异：LLM用语言作为统一脚手架，串联感知、推理、行动和记忆压缩。Chain of Thought本质上是自适应计算——任务复杂就生成更多token，每个token是一次前向传播。
苏煜最精辟的类比："OpenCloud moment和ChatGPT moment非常相似——不是技术突破，而是交互范式的深刻变化。"
但GUI不会死。苏煜的语义网类比很有力——Tim Berners-Lee推了20年语义网，全世界都没重写。如果Agent需要整个互联网都变成API，这件事也可能推不动。
📌 语言是这一代Agent的通用脚手架。它统一了感知、推理、行动和记忆——这不是新算法，而是新的统一框架。

# 03 专业化智能——百万小世界的专家
![专业化vs通用化](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae9.jpg)
苏煜的创业逻辑：世界不是一个大世界，而是由百万个小世界组成。每个小世界要产生价值，需要专业化、需要成为专家级Agent。大模型公司组织结构上做不了这个——它们天然想做平台化、统一化的东西。
NeoCognition的定位：Agent Research Lab for Specialized Intelligence。$40M seed，6个月融完。
当前Agent成功率约50%。苏煜的核心赌注：通过让Agent学习特定领域的"世界模型"——规则、关系、约束——来实现专业化，从而提升可靠性。
类比：人类实习生不是靠"通用知识"成为专家的，而是靠深度理解一个微观世界的运作方式。Agent也一样。
📌 专业化不是限制，而是可靠性提升的路径。每个Skill就是一个小世界的专家。

# 04 中美辐射差——应用层速度是结构性优势
![中美AI发展模式对比](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/a29cb6f1f62f21eb1c05bbf7e.jpg)
姚顺宇专门留了一个章节聊"字节和豆包"。硅谷一线训模型的人，已经需要认真讨论中国公司的产品了。
苏煜的论证更系统：引用Eric Schmidt——"美国在应用层普遍慢得多"。在AI时代这是很大的优势，因为基础模型智能已经越过"够用"的临界点。很多以前没人做的事，不是不值得做，而是摩擦太高。现在AI把摩擦降下来了。
类比：美国的AI辐射像iOS——底层极强，应用受控，慢但稳。中国的AI辐射像Android——底层开放，应用爆发式增长，快但参差。
窗口期12-18个月。美国正在加速应用层（OpenAI agent/Claude Cowork），不会永远慢。
📌 中国应用层速度不是"更勤奋"的产物，而是结构性优势。窗口期不会永远开着。

# 05 靠谱即壁垒——可靠性才是AI产品的真正护城河
![可靠性是AI产品的真正护城河](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aaeb.jpg)
姚顺宇说"AI不需要脑子，需要靠谱"。苏煜说Agent成功率只有50%。两人从不同角度指向同一个结论。
信任像银行存款——每次成功存入一笔小额定存，每次失败取出一笔大额活期。50%成功率让信任永远在0附近波动。
AI产品有一条可靠性阈值线——低于阈值，任何推广都在加速负口碑。当前大多数Agent产品还在阈值线下方。
Coding为什么是AI-native唯一大规模成功场景？因为奖励信号清晰+GitHub数据基座+程序员代码风格高度相似。这不是偶然，是结构性的。
📌 可靠性是唯一真正的壁垒。不是"能做到什么"，而是"能做到且做可靠的是什么"。

# 09 总结：规律·现象·趋势
![总结](https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/8da0e691e999c65e65ed3aae6.jpg)
📌 AI行业正在从"天才驱动的手艺活"转向"工程驱动的工业活"。可靠性是唯一真正的壁垒。
| 现象 | 规律解释力 |
| --- | --- |
| 模型训练团队上百人 | ✅ 集体工程已是标配 |
| Agent成功率~50% | ✅ 可靠性阈值未过 |
| 中国应用层速度 | ✅ 结构性差异 |
| Cursor小团队成功 | ⚠️ 应用层仍有英雄空间 |
| Musk走视觉Agent路线 | ❌ 可能挑战语言Agent范式 |
发展趋势：
因为"工程化>手艺化"→模型训练岗位工种化
因为"可靠性是壁垒"→专业化Agent崛起，Skill市场=专业能力封装层
因为"应用层速度"→中国AI全民化产品爆发，窗口期12-18个月
因为"范式之争未定"→语言Agent vs 视觉Agent白热化
📌 浪不等人，但交汇处最亮。

# 了解更多
[文章专题《林克的AI 洞察》](https://docs.corp.kuaishou.com/k/home/VTZBOvmOPA38/fcACMMOhF-Ozmg9bEYDU_5qUX)
