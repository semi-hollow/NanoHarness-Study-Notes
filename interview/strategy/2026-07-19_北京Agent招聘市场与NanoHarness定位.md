# 北京 Agent 招聘市场与 NanoHarness 定位

> 调研日期：2026-07-19  
> 用途：岗位选择、项目定位、简历表达和面试质疑应答  
> 结论状态：当前求职阶段的主决策依据；岗位市场变化后应重新核验

## 1. 先记住结论

NanoHarness 的方向没有做错，也不需要改造成 OpenClaw、OpenCode 或一个 LangGraph
应用才能成立。

真正的问题是两点：

1. 对外叙述以“自研 Runtime / 基础框架”为起点，主动引出了“为什么不用成熟框架”的质疑。
2. 项目已经实现大量机制，但公开结果还不足以证明这些机制改善了什么。

当前最合适的定位是：

> **NanoHarness 是一个面向真实代码仓库的可治理软件工程智能体与评测工作台。**
>
> 它从 issue 出发，在隔离 workspace 中完成代码检索、修改、验证和人工控制；底层
> Runtime 负责工具副作用治理、中断恢复、trace 和评测证据，避免把“生成了 patch”
> 误报成“解决了问题”。

这不是“退回普通 Agent 应用”，而是把产品行为放在前面，把 Runtime 和 Evaluation
作为技术深度放在后面。

### 1.1 关于“是否因为沉没成本才保留项目”的最终确认

这里需要把判断说得更严格：**纯 Agent Runtime 开源框架并不是当前求职目标下的最佳
展示形态。** 如果今天从零开始，项目不应该先实现大量 Port、Adapter 和通用能力，再寻找
产品任务；更合理的顺序是先完成一个真实垂直 Agent，再让实际失败驱动 Runtime 能力生长。

保留 NanoHarness 不是因为已经投入了很多代码，而是因为它已经不只是抽象框架：它能够从
repository issue 出发，执行仓库 checkout、上下文检索、模型工具循环、代码修改、验证和
SWE-bench 结果接入。现有代码具备软件工程 Agent 的产品内核，只是对外表达和量化证据仍然
过度偏向 Runtime。

因此最终选择不是“保留纯框架”，也不是“推倒后改成 OpenClaw/OpenCode”，而是：

```text
软件工程 Agent 产品任务
→ 自有 Runtime 治理与恢复
→ Evaluation 量化与失败闭环
```

如果真实 Smoke-5 与 official evaluation 最终证明 Agent 不能稳定完成任务，就不能继续靠
Runtime 名词和 UI 维持 Coding Agent 叙述。届时必须修复任务能力，或者诚实降级为
Runtime/Evaluation prototype。Benchmark 是这个定位能否成立的可证伪验收条件。

### 1.2 关于“平台能力是否向下兼容业务 Agent”的最终确认

Agent Platform、Runtime 和 Harness 在状态机、工具契约、恢复、隔离、并发、可观测性和
评测方面通常更深，但这不意味着掌握平台能力就天然掌握业务 Agent。

业务 Agent 还有不同的困难：领域建模、RAG 数据质量、外部系统集成、用户体验、线上 SLA、
成本和效果指标，以及在交付压力下选择成熟框架而不过度设计。两者是有较大交集的横向能力，
不是严格的上下级关系。

面试时不要说“Runtime 更难，所以我可以向下兼容应用开发”。更准确的表达是：

> 我的差异化优势在 Agent Runtime、工具治理和 Evaluation，这些能力可以迁移到业务 Agent
> 的稳定执行、人工控制和可观测性。同时，我有 Java 生产系统交付和 RAG/Context Platform
> 实践，因此也具备业务建模、系统集成和应用后端证据。实际业务交付时，我会优先复用
> LangGraph 等成熟框架，不会为了自研而自研。

对当前个人经历而言，NanoHarness 证明 Agent 深度，Agent Context Platform 证明检索与
Context Engineering，华为 Java 经历证明生产后端和业务交付。三者组合可以覆盖平台岗位和
应用岗位，但不能把单个 NanoHarness 项目包装成所有方向的完整经验证明。

## 2. 调研方法和边界

本轮目标是观察北京 Agent 研发市场在招聘什么，而不是制造一个虚假的岗位总数。

- BOSS 直聘网页对自动访问存在安全检查，无法可靠遍历 App 内全部实时职位。
- 本轮使用近期被公开搜索引擎索引的 BOSS 职位页和岗位摘要。
- 页面抓取时间主要分布在近 2 天到 4 周。
- 去重审阅了 40 余条与 Agent、智能体平台、AI Coding、Agent 评测、大模型应用后端相关的岗位摘要。
- 单个职位可能随时下线，因此本文只用于判断能力结构，不把任何职位视为长期有效。
- 不对各类别给出伪精确百分比，只保留稳定的相对数量和要求趋势。

主要公开样本：

- [北京 AI 开发工程师](https://www.zhipin.com/zhaopin/4bf879c1368205460nB_39q7Fg~~/)
- [北京智能体平台研发](https://www.zhipin.com/zhaopin/60a7e59fbe72b3640nB739q1Eg~~/)
- [北京大模型平台与评测](https://www.zhipin.com/zhaopin/225edc80cb172f1c0nB72dW8EQ~~/)
- [北京应用开发工程师](https://m.zhipin.com/zhaopin/93103d410e52827c1H143ti_FA~~/)
- [北京 Agent 初中级岗位](https://www.zhipin.com/zhaopin/814ba6a7c776bf5a0nB729q4Fg~~/)
- [百度 Coding Agent 策略岗位](https://www.zhipin.com/zhaopin/0cf11f29f1cde14e0nJz2N2_/)
- [字节 Agent 评测岗位](https://m.zhipin.com/zhaopin/981d2debbf57989e031509W7/)
- [DeepSeek Agent 执行环境岗位](https://cn.linkedin.com/jobs/view/%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%BC%80%E5%8F%91%E5%B7%A5%E7%A8%8B%E5%B8%88-at-deepseek-ai-4440391361)

## 3. 北京市场主要在招什么

### 3.1 业务 Agent、RAG 和应用后端

这是公开样本里数量最多的一类。典型要求包括：

- 把 Agent 接入客服、招聘、教育、办公、金融、游戏运营等真实流程。
- 使用 LangChain、LangGraph、LlamaIndex 等框架快速交付。
- RAG、知识库、检索、召回、重排、Prompt 和多轮对话。
- Python、Java 或 Go 后端，API、缓存、数据库、日志、监控和部署。
- 从业务反馈和效果数据中持续迭代，而不是只完成 demo。

NanoHarness 单独面对这类岗位不是最完整的业务案例，但个人的 Java 生产经验和
Agent Context Platform 可以补齐业务集成、RAG 和后端工程部分。没有必要把这些能力
全部塞回 NanoHarness。

### 3.2 Agent 平台、Runtime 和 Harness

数量少于普通应用岗，但技术要求与 NanoHarness 高度重合：

- Agent 开发范式和底层平台。
- 长程规划、Memory、工具调用准确率和状态管理。
- 多模型接入、工具扩展、持久化、稳定性和可观测性。
- 执行环境、快照、隔离、恢复和开发者体验。
- 与模型、研究和业务团队共同迭代 Harness 行为。

千问智能体平台、Coze、大模型开发平台、DeepSeek Harness 和 Kimi Code 属于这条主线。
这是 NanoHarness 最有辨识度的投递方向。

### 3.3 Coding Agent、Agent 评测和数据

这类岗位数量更少，但项目匹配度也很高：

- 代码仓库理解、任务拆解、工具选择和上下文管理。
- 真实工程任务、评测任务、能力维度和失败分析。
- trace、benchmark、回归集、数据闭环和模型行为判断。
- 成功率、成本、延迟、稳定性和安全边界的联合优化。

360 AI Coding、百度 Coding Agent 策略、字节 Agent 评测、DeepSeek Code Agent 数据
都可以用 NanoHarness 作为主项目。但前提是项目必须拿出真实 benchmark 结果，而不是
只有评测框架代码。

### 3.4 OpenClaw 相关岗位

OpenClaw 岗位确实存在，主要集中在：

- Skill 开发。
- 企业系统部署与接入。
- 办公、内容、设备或个人助理场景。
- 围绕特定 Agent 生态做产品化。

它是市场中的一个细分产品方向，不是 Agent 岗位的统一形态。把 NanoHarness 改名为
OpenClaw 类智能体不会自然增加匹配度，反而会丢失软件工程 Agent、执行治理和评测的差异化。

## 4. 投递策略

### 第一优先级

- Agent Harness 研发
- Coding Agent 研发
- Agent Runtime / 平台研发
- Agent 评测、模型数据和开发者基础设施
- AI Coding 和研发效能

NanoHarness 是主项目，Java 生产经验用于证明工程成熟度。

### 第二优先级

- Agent 应用后端
- 大模型应用开发
- 企业智能体平台
- Java + AI / Python + AI
- RAG 与知识工程

NanoHarness 证明 Agent 深度，Agent Context Platform 证明 RAG，华为经历证明生产交付。

### 谨慎投递

- 纯模型预训练、RL 算法、CUDA 和推理内核
- 强论文导向的算法研究
- 以 CV、语音或多模态模型训练为主的岗位

这些岗位的缺口不是给 NanoHarness 再加几个功能就能补齐，不应破坏项目重心。

## 5. 项目名称和对外口径

### 推荐名称

> **NanoHarness｜可治理的软件工程智能体与评测工作台**

英文副标题可以使用：

> A governed software-engineering agent with an inspectable runtime and evidence-driven evaluation.

### 可以说

- 面向真实代码仓库任务。
- 任务形态接近 Codex、Claude Code 或 OpenCode。
- 自己实现了一个小而可检查的 Agent kernel，用于控制 Coding Agent 的关键实验变量。
- Runtime 是产品内部的技术层，不是对所有框架的替代品。
- Evaluation 是能力闭环，不把 candidate patch 当作 solved。

### 不要说

- OpenCode 或 Claude Code 的替代品。
- OpenClaw 类通用个人智能体。
- 自研通用 Agent 基础框架。
- 比 LangGraph 更好的 Runtime。
- 企业级生产框架。
- 没有 official evidence 时声称 SWE-bench solved rate。

## 6. LangChain、LangGraph 与 Harness 的准确边界

根据 LangChain 官方当前定义：

- [LangChain](https://docs.langchain.com/oss/python/concepts/products) 是提供模型、工具、AgentLoop 和 middleware 抽象的 Agent framework。
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) 是面向长运行、有状态 Agent 的低层 orchestration runtime。
- [Deep Agents](https://docs.langchain.com/oss/python/concepts/products) 是在 Runtime 上增加 planning、文件系统、上下文管理和 subagent 的 Agent harness。
- LangGraph 已明确覆盖 durable execution、HITL、persistence、短期和长期 Memory、subgraph 等能力。

因此，不能把 NanoHarness 的价值建立在“LangGraph 没有恢复、HITL 或 Memory”上。

NanoHarness 真正可以强调的领域差异是：

- task-aware 工具可见性。
- 文件路径、命令、网络和 workspace policy。
- worktree / OCI 执行隔离。
- 副作用 fingerprint、幂等账本和 stale approval。
- 代码 patch、local verification 与 official evaluation 的证据分层。
- Coding Agent failure taxonomy 和 matched ablation。

这些能力也可以在 LangGraph 上实现。项目价值不是“只有自己写才做得到”，而是你完整
设计、实现并验证了这些边界，并能判断生产环境何时应该复用成熟框架。

## 7. 面试官质疑应答

### 7.1 为什么不用 LangChain 或 LangGraph，反而自己造轮子？

推荐回答：

> 我不认为自研 Runtime 普遍优于 LangGraph。对于普通业务 Agent，我会优先使用成熟框架，
> 获得编排、持久化、HITL 和生态集成。NanoHarness 不是为了替代 LangGraph，而是一个
> 窄而可检查的软件工程 Agent 实现。我重点研究的是 Coding Agent 特有的控制问题，例如
> 工具可见性、路径和命令策略、worktree/OCI 隔离、副作用指纹与幂等，以及
> candidate/local/official 三层评测证据。生产落地时，这些领域组件也可以接到 LangGraph
> 或其他编排 Runtime 上。

### 7.2 所以你做得比 LangGraph 更好吗？

推荐回答：

> 不是同一层面的全面竞争。LangGraph 在通用编排、持久化生态、部署和可视化上更成熟；
> NanoHarness 的优势是范围窄、依赖小、运行链路完全可检查，并对软件工程任务的副作用和
> 评测证据做了更具体的约束。我不会建议普通团队重复实现 LangGraph，但会保留这些 Coding
> Agent 领域策略和评测能力。

### 7.3 为什么不直接写成 LangGraph middleware？

推荐回答：

> 这是合理的产品化路径。项目初期我需要先固定 AgentLoop、工具执行和 evidence contract，
> 才能准确观察每个决策的因果关系。如果进入团队生产交付阶段，我会评估让 LangGraph
> 承担 orchestration 和 persistence，把现有 policy、environment、tool execution 和
> evaluation 作为独立组件复用，而不是坚持全部自研。

### 7.4 这个项目是不是主要为了学习底层原理？有什么生产收益？

推荐回答：

> 最初确实有建立完整底层认知的动机，但项目没有停在重复实现 ReAct。真实运行中出现的
> tool schema mismatch、重复副作用、stale approval、上下文溢出和错误 solved claim，
> 促使我把重点转到可治理执行和评测证据。它现在最直接的价值是作为 reference
> implementation 和实验平台，验证哪些 Runtime 设计能改善失败率、成本和恢复行为；我不会
> 把它包装成已经大规模生产验证的平台。

不要主动说“主要为了通过面试”。真实且专业的说法是：起点包含学习和技术验证，后来由
真实失败驱动形成了清晰的工程研究问题。

### 7.5 为什么不把它包装成 OpenClaw 或 OpenCode？

推荐回答：

> OpenClaw 更偏通用助理、Skill 生态和外部系统连接；NanoHarness 聚焦真实代码仓库任务，
> 产品任务形态更接近 Coding Agent。它可以说与 OpenCode/Codex 属于相邻产品类别，但目前
> 没有完整 IDE、成熟交互式 CLI 和大规模用户验证，因此不会声称是它们的替代品。

### 7.6 如果团队已经使用 LangGraph，你能做什么？

推荐回答：

> 我不会要求团队替换框架。我可以把 NanoHarness 中已经验证的工具治理、execution
> environment、checkpoint schema、operation ledger、evidence 和 evaluation 设计映射成
> LangGraph node、middleware、checkpointer 或外部 service，并用同一套 benchmark 验证迁移
> 前后的行为，而不是依赖个人偏好做技术选型。

### 7.7 你的 Benchmark 到底证明了什么？

当前诚实回答：

> 目前项目已经建立了 Smoke-5 选择契约、official result 接入、scorecard、failure
> taxonomy 和 matched ablation，但现有公开结果还不足以声称总体解决率。它首先证明了评测
> 口径和证据链是可执行的。下一步必须完成全量 Smoke-5、重复运行和 official evaluation，
> 才能回答具体 Runtime 设计改善了多少。

完成后应改为基于真实数字回答，不能继续只讲评测代码结构。

## 8. 当前项目的关键事实

以下结论来自 2026-07-19 的本地检查，后续可能变化：

- README 首屏以 Runtime 和大量能力列表为主，产品任务不够突出。
- Smoke-5 文档定义了 5 个 case。
- 检查到的 14 个本地 SWE-bench `results.json` 全部只运行了
  `astropy__astropy-12907`。
- 其中 5 次生成 candidate patch，未发现完成 official evaluation 的 run。
- Git 跟踪树中没有公开 scorecard、official result 或完整 benchmark summary。
- 当前 direct baseline 是“相同模型但不给工具”，只能说明工具价值，不是有竞争力的
  Agent baseline。
- GitHub 默认 `master` 仍停在 `5cb14fe`；最新功能位于开发分支，其中本地最新提交尚未
  push。公开展示前必须重新核验并合并。

这些事实不说明 Runtime 没有技术含量，只说明 offer-readiness 的最大缺口已经从“缺能力”
转为“缺实验结果和清晰展示”。

## 9. NanoHarness 调整方案

### P0：真实 Benchmark Campaign

目标：从“我实现了评测机制”升级到“我用评测证明并分析了 Runtime 行为”。

最低实验设计：

- 固定 Smoke-5 全部 5 个 case。
- 每个 case 至少 3 次重复运行。
- 固定代码 revision、provider/model、temperature、prompt、工具 schema、step/token budget。
- 运行顺序随机化或交错，避免服务时段和代码版本造成系统性偏差。
- 必须执行 official SWE-bench evaluation。
- 保存并公开 sanitized config、prediction、official result、scorecard 和失败案例。

核心指标：

- official resolved / official denominator。
- candidate patch rate。
- local verification rate。
- failure taxonomy 分布。
- token、成本和 wall-clock latency。
- tool call 数量、failed tool rate 和 repair rate。
- context compaction、Memory recall 和恢复事件，只作为机制指标，不代替正确率。

主 baseline：

- 同模型、同 prompt、同工具 schema、同预算的 minimal ReAct agent。
- 不把“完全不给工具”的 direct baseline 当成主要竞争对照。
- 对 routing、Memory、compaction、tool burst 等做一次只改变一个因素的 matched ablation。

LangGraph 不应作为第一优先级的“输赢 baseline”。框架实现与自研实现很难保证 prompt、
状态和工具执行完全一致，结论容易被混杂变量污染。它更适合作为互操作示例或工程取舍对照。

验收标准：

- README 能展示一张真实结果表。
- 至少一个 official resolved 成功案例和一个有清晰 root cause 的失败案例。
- 每个数字都能回到公开 artifact。
- 结果不好也如实报告，并从 failure taxonomy 得到下一轮改进。

### P1：产品优先的 GitHub 首页

README 首屏只回答五件事：

1. 用户给它什么：真实 repository issue。
2. Agent 做什么：理解、检索、修改、验证。
3. 为什么可信：隔离、审批、恢复和 evidence。
4. 效果如何：真实 benchmark summary。
5. 如何在五分钟内运行和审查。

能力列表收敛为四组：

- Solve：repository context、tool loop、patch、verification。
- Govern：tool policy、sandbox、approval、isolation。
- Recover：checkpoint、operation ledger、resume、fanout recovery。
- Evaluate：trace、scorecard、official result、failure taxonomy、ablation。

Public API、Port/Adapter、Hook、配置 schema 和全部 package 地图放在后半部分，不作为第一
印象。

### P1：可重复的面试展示

准备两个彼此独立的 demo：

- Product demo：真实模型处理一个仓库 issue，得到 patch、verification 和 evidence。
- Control-plane demo：确定性触发 HITL 或 write approval，展示 stop、checkpoint、人工决定、
  resume、幂等账本和最终副作用。

产品 demo 证明 Agent 能做任务；确定性 demo 证明 Runtime 控制面。两者不能互相冒充。

### P2：薄 LangGraph 互操作示例

在 benchmark 和 README 完成后，再考虑一个很小的示例：

- LangGraph 负责编排上层 workflow。
- NanoHarness `Harness.run` 作为“执行 repository task”的一个 node 或 service。
- 原有 Tool Policy、Environment 和 Evaluation 不重写。

这个示例的目标只是证明你会复用框架并能解释边界，不追求完整 feature parity，也不重写
AgentLoop。

### 明确不做

- 不把 NanoHarness 改造成通用 RAG 问答产品。
- 不为了岗位关键词增加假的 research/ops preset。
- 不重写成 LangGraph 项目。
- 不开发完整 IDE 或 OpenCode clone。
- 不继续堆新的 Runtime 名词，直到现有能力产生量化结果。
- 不把固定模型 showcase 当作 Agent 推理能力证据。

## 10. 五分钟展示面

### 0:00 到 0:30：一句话和问题

> Coding Agent 不难生成 patch，难的是让有副作用的长任务可治理、可恢复，并且知道 patch
> 到底有没有解决问题。NanoHarness 用一个真实 repository task 展示这条闭环。

### 0:30 到 1:30：任务与运行

- 展示 issue、base commit、provider/model 和固定配置。
- 启动 reference case 或打开已经公开的同配置 run。
- 展示 Agent 正在检索、调用工具和生成 patch，而不是先讲 package 结构。

### 1:30 到 2:30：结果证据

- candidate patch。
- local verification。
- official evaluation。
- token、成本、延迟和失败工具。
- 明确解释三层 evidence 的差异。

### 2:30 到 3:30：控制面

- 演示一次 HITL 或 write approval。
- 指出 checkpoint、operation fingerprint、stale detection 和 resume。
- 说明已经发生的副作用不会被假装回滚。

### 3:30 到 4:30：Benchmark 与失败闭环

- 展示 Smoke-5 的选择逻辑。
- 展示 baseline、variant 和重复运行。
- 展示一个成功 case 和一个失败 case。
- 从 failure taxonomy 指向下一步窄修复。

### 4:30 到 5:00：架构与框架选择

- `Harness.run` 是公开入口。
- AgentLoop 是内部 kernel。
- Policy、Environment、State 和 Evaluation 通过显式边界组合。
- LangGraph 可以承担上层编排，不需要否定成熟框架。

## 11. 最终决策

当前求职阶段不再扩展项目 scope，按以下顺序推进：

1. 完成真实 benchmark 和 official evidence。
2. 重写 README 首屏和五分钟演示路径。
3. 合并并发布当前开发分支。
4. 使用真实数字更新中文 CV。
5. 时间允许时补薄 LangGraph 互操作示例。

项目最终要证明的不是“我也能写一个框架”，而是：

> 我能定义软件工程 Agent 的关键失败问题，设计受治理的执行边界，用真实 benchmark 和
> trace 找到原因，并以可复现证据验证改进。
