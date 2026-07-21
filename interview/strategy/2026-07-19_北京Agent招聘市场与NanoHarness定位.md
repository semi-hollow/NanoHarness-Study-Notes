# 北京 Agent 市场与 NanoHarness 定位

> 层级：[返回总入口](../../README.md) → B1 按需查询 → 定位与取舍；不进入顺序通读。

研究日期：2026-07-19。岗位会变化；本文只维护稳定定位、架构取舍和项目硬约束，不维护职位清单。

## 最终定位

> **面向真实代码仓库的可治理软件工程 Agent 与评测工作台。**

它从 repository issue/base commit 出发，在隔离 workspace 中完成检索、修改和验证；Runtime
治理 Context、工具副作用、中断恢复和 trace；Evaluation 区分 candidate、local、official
Evidence，并用重复实验检查 Runtime 改动。

产品和工程形态锁定为：

> **统一薄 CLI 与单一 Runtime Public API + 深度 Agent Runtime 机制 + 统一 Run Story 与可审计 Evidence**

不开发复杂 TUI、IDE、会话壳或插件市场。先讲真实任务，再讲 Runtime 深度；不要以“自研通用
框架”开场。

## 项目四条硬约束

状态与副作用正确、Evidence 真实可信是不可牺牲的底线。在满足底线的方案中，按以下原则决策。

### 原则一：面试回报优先

任何新增或保留的类、方法、文件、CLI、Artifact 或能力必须回答：

1. 解决什么真实 Agent Runtime 问题？
2. 支撑哪个高频面试问题？
3. 是否位于黄金主链；若否，属于哪层追问？
4. 产生或保护什么可验证 Evidence？
5. 增加多少学习成本，有没有更简单方案？
6. 不做它会失去什么当前能力？

“更规范”“以后可能扩展”“更像框架”不能单独成为进入 Core 的理由。

### 原则二：理解成本必须有预算

| 项目 | Interview Core 预算 |
| --- | --- |
| 黄金主链 | 1 条 |
| Runtime Public API | `Harness.run` 1 个 |
| Core CLI | `run / inspect / demo`；Operator 另有 `resume` |
| 首轮核心文件 | 10–12 个，最多 15 个且必须解释增加收益 |
| Runtime construction owner | 1 个 |
| Single-run Evidence Read Model | 1 个 |
| 五分钟 Demo | 1 个真实 Run Story + 1 次 approval/recovery |

这些是阅读和 owner 预算，不是机械 LOC KPI。数字增加时必须同时说明新增语义和删除/合并机会。

### 原则三：一个抽象必须有明确收益

可保留的收益：表达真实领域状态、管理安全/生命周期、隔离外部基础设施、支持有价值的测试替身、
或消除多个调用方的重复。

重点审计：一行转发 Wrapper、无新增语义的 Service、只复制字段的 Mapper、为了目录整齐拆出的
模块、没有真实边界/替身价值的单实现 Port、重复 Builder/Projection/Renderer、无生产调用方入口。
审计结论只能是保留并解释、合并、内联、降为 Advanced 或删除，不能以六边形纯度自动保留。

### 原则四：代码与 Artifact 必须自定位

任意 Core symbol 应在两分钟内回答：黄金主链位置、规范上游、下一 owner、状态/副作用、不变量、
Evidence 和删除影响。Core docstring/关键注释解释“为什么、何时、失败语义”，不逐行复述代码；
只标规范上游，完整 callers 由 Call Hierarchy 计算。

任意 run artifact 应能查到 type/path、producer/phase、consumer、source event、authority、
proves/does-not-prove 与可重建性。文件名和目录 glob 不是语义合同。

## 架构与范围决策

六边形架构保留，但只保护真实边界：Domain 表达状态/规则，Application 编排 use case，Port
隔离模型/状态/Git/文件/进程/evaluator，Adapter 实现 I/O，Wiring 唯一装配。Presentation 只翻译
输入和渲染输出，不重新装配 Runtime，也不重新推断状态。

Core：Single run、Context、Tool Governance、HITL/Recovery、Operation Ledger、Run Story/Evidence。

Follow-up/Advanced：Memory、Skills、MCP、Sequential Multi-Agent、Fanout、完整 Benchmark/Campaign、
默认只读 Workbench/UI。保留实现和边界，但退出首轮阅读和五分钟主演示。

文档同样受预算约束：架构事实进入主仓既有 ARCHITECTURE/README；学习解释进入本仓既有 owner；
实施计划进入 issue/commit/history。不新增平行“治理说明”或“回答稿”。

## 岗位匹配

| 方向 | NanoHarness 的作用 |
| --- | --- |
| Agent Harness / Runtime / 平台 | 最匹配：状态、工具、恢复、隔离、观测与 DX |
| Coding Agent / 评测 / 数据 | 高匹配，但必须有真实 official result 与 badcase |
| 业务 Agent / 应用后端 | 证明 Agent 深度；仍需补业务建模、RAG、API/SLA 与集成经历 |

优先投递 Harness、Coding Agent、Agent Runtime、Evaluation 和开发者基础设施。纯预训练、CUDA、
RL 算法或强论文岗位的缺口，不能靠继续给 NanoHarness 加功能解决。

## 对外口径

可以说：

- 面向真实仓库任务，产品形态与 Coding Agent 相邻。
- 实现了小而可检查的 Agent kernel，用来治理关键实验变量。
- Runtime 是产品内部技术层，不是所有框架的替代品。
- Evaluation 是能力闭环，不把 candidate patch 当 solved。

不要说：

- 现有编码助手的替代品或通用助手。
- 企业级生产框架、distributed swarm、全面优于 LangGraph。
- 没有 official Evidence 时声称 SWE-bench solved rate。
- “Runtime 更难，所以向下兼容所有业务 Agent”。

## LangGraph 质疑

### 为什么没有直接使用 LangGraph

> 我不认为自研 Runtime 普遍优于 LangGraph。普通业务 Agent 会优先复用成熟框架的编排、
> persistence、HITL 和部署生态。NanoHarness 范围更窄，用完整实现观察 coding-specific 的工具
> 可见性、命令/路径策略、worktree/OCI 隔离、operation identity 和 candidate/local/official
> Evidence。生产中这些组件也能接入 LangGraph。

### 团队已经使用 LangGraph时怎么办

> 不要求换框架。我会把 policy、execution environment、checkpoint schema、operation ledger 和
> evaluation contract 映射为 node、middleware、checkpointer 或 service，并用同一 benchmark
> 验证迁移行为。

项目价值来自可检查的机制与证据，不来自重复实现通用 orchestration。

## 公司经验与公开项目边界

> 公司项目让我接触弱模型 Tool Call、长任务中断、安全审批和失败定位等真实约束。NanoHarness
> 是公司资产之外的独立 clean-room 实现：代码、配置、数据和 artifact 由个人构建或来自公开
> benchmark；工程经验影响了问题选择，但未复制公司代码、prompt、参数或业务数据。

不要说“把公司项目开源了”，也不要把个人仓库放在公司项目名下造成资产归属误解。

## 真实性优先级

最高价值缺口仍是真实 official repeated campaign：

1. 先完成 10-run pilot，验证 evaluator、成本和 artifact 合同。
2. 冻结配置后完成 Smoke-5、两个 preset、三次重复共 30 runs。
3. 发布成功与失败的 sanitized evidence bundle。
4. 只用真实 official denominator 更新 README/CV。

两个 preset 同时改变 routing 与 Skill，只能比较整体 preset；单机制因果需要 matched ablation。
入口/可读性整改可以并行，但不能长期阻塞真实 run，也不能用 deterministic Demo 替代。

## 自检

1. 用六个 ROI 问题审查一个你想新增的抽象。
2. 为什么保留六边形架构不等于保留所有 Port/Wrapper？
3. 随机 symbol 与 artifact 各怎样在两分钟内完成自定位？
4. 为什么不直接使用 LangGraph，哪句话最容易变成“造轮子辩护”？
5. 什么 official 结果会证伪当前定位，届时应怎样诚实降级？

每题先给结论，再给两点原因、一个项目 Evidence 和一个边界；两分钟没有结论即未通过。
