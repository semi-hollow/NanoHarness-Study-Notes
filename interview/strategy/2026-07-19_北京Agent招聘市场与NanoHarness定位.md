# 北京 Agent 市场与 NanoHarness 定位

调研日期：2026-07-19。岗位会变化；本文只保留稳定决策，不维护职位清单。

## 最终结论

NanoHarness 不需要推倒重做成 OpenClaw、OpenCode 或 LangGraph 应用。当前最准确的定位是：

> **面向真实代码仓库的可治理软件工程智能体与评测工作台。**
>
> 它从 repository issue 出发，在隔离 workspace 中完成检索、修改和验证；内部 Runtime
> 治理 context、工具副作用、中断恢复和 trace，Evaluation 区分 candidate、local 与
> official evidence，并用重复实验检查 Runtime 改动。

先讲产品任务，再讲 Runtime 深度；不要以“我自研了一套通用框架”开场。

## 两个容易焦虑错的问题

### 是否只是因为沉没成本才保留项目

不是，但纯 Runtime 框架也不是最佳展示形态。如果从零开始，应先做真实垂直 Agent，再由失败
驱动 Runtime 生长。NanoHarness 值得保留，是因为它已经有 repository issue、checkout、
AgentLoop、patch、验证与 SWE-bench 主链，不只是 Port/Adapter 集合。

可证伪条件：如果 official campaign 证明任务能力长期不成立，就必须修任务或诚实降级为
Runtime/Evaluation prototype，不能靠 UI 和术语维持 Coding Agent 叙述。

### Runtime 是否天然向下兼容业务 Agent

不是严格上下级。Runtime/Harness 在状态、工具、恢复、隔离和评测上更深；业务 Agent 仍有
领域建模、RAG 数据质量、系统集成、SLA、成本和用户效果等独立难点。

正确口径：

> 我的差异化优势是 Agent Runtime、工具治理和 Evaluation，这些能力能迁移到业务 Agent 的
> 稳定执行与可观测性。业务交付时我会优先复用成熟框架，不会为了自研而自研。

## 市场岗位分成三类

| 方向 | 常见要求 | NanoHarness 作用 |
| --- | --- | --- |
| Agent Harness / Runtime / 平台 | 状态、工具、恢复、隔离、多模型、可观测性、DX | 最匹配，作为主项目 |
| Coding Agent / 评测 / 数据 | 仓库理解、执行环境、trace、benchmark、失败归因 | 高匹配，但必须有真实结果证据 |
| 业务 Agent / 应用后端 | LangGraph、RAG、业务集成、API、SLA、效果迭代 | 证明 Agent 深度，不能单独替代业务案例 |

投递优先级：Harness、Coding Agent、Agent Runtime、评测与开发者基础设施优先；业务 Agent
和大模型应用后端可投，但回答中要补生产后端与业务集成证据。纯预训练、CUDA、RL 算法或强
论文岗位的缺口不能靠给 NanoHarness 加功能解决。

## 对外口径

可以说：

- 面向真实代码仓库任务，产品形态与 Coding Agent 相邻。
- 自己实现了小而可检查的 Agent kernel，用于治理关键实验变量。
- Runtime 是产品内部技术层，不是所有框架的替代品。
- Evaluation 是能力闭环，不把 candidate patch 当成 solved。

不要说：

- Claude Code/OpenCode 替代品或 OpenClaw 类通用助理。
- 自研通用 Agent 基础框架、企业级生产框架、比 LangGraph 更好。
- 没有 official evidence 时声称 SWE-bench solved rate。
- “Runtime 更难，所以业务 Agent 可以向下兼容”。

## 框架质疑的回答

### 为什么不用 LangChain 或 LangGraph

> 我不认为自研 Runtime 普遍优于 LangGraph。普通业务 Agent 会优先复用成熟框架的编排、
> persistence、HITL 和生态。NanoHarness 是一个窄的 software-engineering Harness，研究
> task-aware tool visibility、路径与命令策略、worktree/OCI 隔离、副作用 fingerprint 与
> candidate/local/official 证据。生产中这些组件也可以接到 LangGraph 上。

### 你做得比 LangGraph 更好吗

> 不是全面竞争。LangGraph 的通用编排、持久化生态和部署更成熟；NanoHarness 范围更窄，
> 强项是软件工程任务的副作用与评测证据。我不会建议团队重复造通用 orchestration。

### 为什么不直接写成 LangGraph middleware

> 这是合理的生产路径。项目先固定 AgentLoop、tool execution 和 evidence contract，是为了
> 观察每个决策；进入团队交付时，可以让 LangGraph 承担 orchestration，把 policy、
> environment、ledger 和 evaluation 作为 middleware、node 或 service 复用。

### 项目是不是只为了学习底层原理

> 起点包含底层认知和技术验证，但真实运行暴露的 schema mismatch、重复副作用、stale
> approval、context overflow 和错误 solved claim，使项目收敛为可治理执行与证据问题。
> 当前价值是 reference implementation 和实验平台，不包装成大规模生产系统。

### 团队已经使用 LangGraph，你能做什么

> 我不会要求换框架。我会将已有 policy、execution environment、checkpoint schema、
> operation ledger 和 evaluation contract 映射为 node、middleware、checkpointer 或外部
> service，并用同一 benchmark 验证迁移行为。

## 公司经验与公开项目

推荐口径：

> 公司项目让我接触到弱模型 Tool Call、长任务中断、安全审批和失败定位等真实约束。
> NanoHarness 是公司资产之外的独立公开实现：代码、配置、数据和 artifact 都由个人构建或
> 来自公开 benchmark，没有复制公司代码、内部 prompt、模型参数或业务数据。工程经验影响了
> 问题选择，但公开实现和证据可以独立审查。

不要说“把公司项目开源了”，也不要把个人仓库放在华为项目名下造成资产归属误解。

## 当前最重要的缺口

项目形态、控制面和展示入口已经成立，最高价值缺口仍是**真实 official repeated campaign**：

1. 先完成 10-run pilot，验证 evaluator、成本和 artifact 契约。
2. 冻结配置后完成 Smoke-5、两个 preset、三次重复共 30 runs。
3. 发布成功和失败的 sanitized evidence bundle。
4. 只用真实 official denominator 和数字更新 README/CV。

两个 preset 同时改变 routing 与 Skill，是 multi-factor preset comparison；单机制因果仍需
matched ablation。Direct model 无工具 baseline 只作弱参考。

在这一步完成前，不继续堆新 Runtime 名词，不开发完整 IDE，也不为关键词增加假的
research/ops preset。薄 LangGraph 互操作示例是可选项，不阻塞投递。

## 自检

闭卷回答以下问题：

1. 为什么保留 NanoHarness 不是沉没成本决定？
2. 为什么 Runtime 不能简单说成向下兼容业务 Agent？
3. 为什么不用 LangGraph，回答中哪一句最容易变成“造轮子辩护”？
4. 公司经验与公开实现的资产边界是什么？
5. 什么结果会证伪当前项目定位？

每题必须先给结论，再给两点原因、一个项目证据和一个边界。说满两分钟还没有结论，判定
未通过。
