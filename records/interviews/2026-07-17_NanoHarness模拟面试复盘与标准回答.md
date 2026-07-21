# NanoHarness 模拟面试复盘与标准回答

> 层级：[返回总入口](../../README.md) → C1 一手档案 → 真实面试复盘；只检索，不当通用答案稿。

> 依据：39 分钟模拟面试转写。本文只复盘 NanoHarness / Agent Harness 相关内容。

## 一、总体结论

这次不是“项目太弱”，而是**项目掌握度和回答结构没有把项目强度交付出来**。

| 维度 | 判断 | 主要问题 |
| --- | --- | --- |
| 项目工程能力 | 中上 | Runtime、Tool、Safety、Checkpoint、Trace、Evaluation 已形成主链路。 |
| Benchmark 设计 | 原实现有明显缺口，本轮已补核心契约 | 之前能跑 ID，却说不清 300-case 全集、五题选择方法、每题验收内容和结论边界。 |
| 项目掌握度 | 不稳定 | 把 Single Agent 空转误讲成 Fanout DAG 成环；把重复签名误讲成包含结果 hash。 |
| 基础知识 | 有两个危险缺口 | 不知道 temperature，并把它类比为置信度；Harness 定义只答“后端”。 |
| 表达 | 当前最大扣分项 | 经常先讲背景，没有先回答问题；出现自我否定、脏话、toy/为了面试等内部动机。 |

面试官真正想判断的不是你记住了多少 Agent 名词，而是：

1. 你能否把一个模糊效果问题转成可验证的实验；
2. 你是否知道项目真实做了什么、没做什么；
3. 你能否用清楚的因果链解释设计，而不是罗列能力；
4. 你是否对 Agent 行为有可复现的观察和判断。

## 二、问题诊断表

| 时间 | 问题 | 本次回答的问题 | 类型 | 正确处理 |
| --- | --- | --- | --- | --- |
| 00:10 | 怎么使用 Codex / Claude Code | 只说 GUI/CLI 和主观模型优劣，没有工作流、验收方式和高强度使用证据。 | 表达问题 | 用“任务分工 -> 隔离执行 -> diff/test/trace 验收”回答。 |
| 02:02 | 项目以什么为基础搭建 | 公司项目、个人项目和内部模型混在一起，容易引出保密与资产边界疑问。 | 口径问题 | 先区分公司经验与公开 clean-room 实现，再说公开版模型接口。 |
| 03:09 | 不同模型 Tool Call 有何区别 | 有真实经验，但散成重复调用、大输出、冲突、路由等现象，没有分类和证据。 | 表达问题 | 按协议遵循、工具选择、循环稳定性三层回答，再给 Harness 对策。 |
| 05:32 | 项目最核心的点 | 先讲 RAG 和评奖背景，迟迟没有说项目输入、输出、核心控制面。 | 表达问题 | 第一秒说 NanoHarness 是什么、解决什么问题，再展开。 |
| 08:41 | Benchmark 为什么可信 | 回答成运行指标；面试官追问数据怎么选，仍继续讲 metric。 | 表达 + 项目缺口 | 先讲目的、候选全集、采样方法、验收标签、结论边界。 |
| 13:59 | Benchmark size 多大 | 不知道当前使用的 Lite test 是 300。 | 知识问题 | 明确 Full 2,294、Lite test 300、Verified 500；项目候选全集是 Lite 300。 |
| 16:01 | Agent 一直空转怎么办 | 把 Single Agent Loop 误讲成 DAG 出环。 | Correctness 口径错误 | Single Loop 讲硬预算、重复 intent、连续失败、tool burst；DAG 只属于 Fanout。 |
| 18:31 | 重复动作怎样识别 | 说成 Tool + 入参 + 结果 hash。当前代码实际只对 Tool + canonical arguments 做 identity。 | Correctness 口径错误 | 结果不是发起动作前可用的身份；副作用另由 operation ledger/fingerprint 治理。 |
| 25:55 | temperature 是什么 | 不知道，随后类比置信度。 | 基础知识问题 | temperature 控制 sampling 随机性，不是模型置信度。 |
| 33:01 | NanoHarness 主要功能 | 只说“Coding Agent 原型”，过于空泛。 | 定位问题 | 用“真实仓库任务的 Runtime Control Plane + Evaluation Harness”定义。 |
| 33:46 | Harness 是什么 | 回答“就是后端”，没有说模型与 Harness 的边界。 | 基础知识 + 表达 | Harness 是围绕模型的确定性控制与评测层。 |
| 34:16 | 什么叫真实研发任务 | 最后答对了，但应该一开始就给具体流程。 | 表达问题 | issue + repo -> 澄清 -> 检索/编辑/测试 -> candidate patch + evidence。 |

## 三、面试回答总规则

每题使用同一个三层结构：

1. **第一句直接结论**：回答面试官问的名词或判断。
2. **两到四个结构化要点**：讲设计和因果，不背模块清单。
3. **一个项目证据 + 一个边界**：指出代码/artifact，明确不能证明什么。

不要出现：

- “这个我还没细看”“这是我准备的稿”“我是为了面试才做大”；
- “toy project”“破烂”“Star 只有几个”；
- 把不知道的实现补成听起来高级的名词；
- 问 Benchmark 选择时继续答 token/tool-call 指标；
- 用“你说得对”代替自己的判断。

## 四、30 秒项目介绍

> NanoHarness 是我独立开源实现的精简 Agent Runtime Control Plane，目标是让模型在真实代码
> 仓库里完成 issue 定位、工具调用、修改和验证时，行为可控、可恢复、可观测、可评测。
> 模型负责提出下一步意图，Harness 负责 context 组装、工具可见性与执行、安全审批、checkpoint、
> trace 和最终 evidence。项目同时接入 SWE-bench-shaped loop，把 candidate patch、local
> validation 和 official result 严格分层，再用 matched ablation 判断某个 Runtime 设计到底
> 改善了质量、成本还是失败模式。

## 五、重点问题标准回答

### 1. 你怎样使用 Codex 和 Claude Code？

**30 秒主答：**

> 我把它们当工程协作者，而不是代码补全。复杂任务先让 Agent 读仓库、形成可检查的计划和
> 改动边界；互不影响的任务放到隔离 worktree 并行，存在依赖的任务按顺序做。生成代码后我
> 不以“模型说完成了”为验收，而是看 diff、类型/单测、运行 artifact 和 Git 状态。长任务会
> 拆成阶段，并保留 checkpoint 或 handoff，避免会话中断后从头猜。Codex 更常用于跨文件分析、
> 方案比较和 review，Claude Code 更常用于明确范围的实现；最终选择取决于任务证据，不固定押
> 某个模型。

追问模型差异时，讲具体行为：协议遵循、工具选择、长任务稳定性、修改质量；不要只说
“sense 更好”。

### 2. 公司项目与 NanoHarness 是什么关系？

> 公司项目让我接触到真实约束，例如弱模型 Tool Call、不完整需求、长任务中断、安全审批和
> 失败定位。NanoHarness 是我在公司资产之外独立实现的公开版本：代码、配置、数据和 artifact
> 都是自己构建或来自公开 benchmark，没有复制公司代码、内部 prompt、模型参数或业务数据。
> 因此我会说“工程经验影响了问题选择”，不会说“把公司项目开源了”。

### 3. 不同模型的 Tool Call 能力怎样比较？

> 我从三层看。第一层是协议遵循：能否输出合法 tool name、JSON arguments 和 call/result
> 对应关系。第二层是工具选择：在当前任务和可见工具集合中，能否选到最合适的工具并给出正确
> 参数。第三层是循环稳定性：是否重复读取、超额 fanout、在失败后修复，还是持续空转。
>
> Harness 的对策也对应三层：ToolCallNormalizer 只修确定性格式；ToolRouter 按任务收敛可见
> 工具；StepController 与 ToolExecutionPipeline 限制重复 intent、连续失败和单 turn burst；
> trace 把失败归到 schema、routing、provider 或 loop，而不是笼统说模型不行。能力判断必须
> 来自 matched case 的成功率、tool failure 和成本，不能只靠主观体验。

### 4. Harness 到底是什么？

> 模型决定“想做什么”，Harness 决定“模型看到什么、能调用什么、动作怎样执行、状态怎样
> 保存、失败怎样恢复、结果怎样验收”。所以它是围绕模型的确定性运行时控制与评测层，包括
> context、tool schema、execution policy、state、trace、recovery 和 evaluation；它可以部署在
> 后端，但“后端”不是定义。

### 5. 什么叫真实研发任务？

> 输入不是一道孤立代码题，而是现有仓库、固定 base commit 和 issue。Agent 需要先理解需求，
> 必要时向人澄清，再检索文件、阅读调用链、修改代码、运行测试，最后输出 candidate patch 和
> 可审计 evidence。NanoHarness 目前覆盖这条 repo-level code repair 链路，不声称是完整 IDE。

### 6. Benchmark 为什么选 SWE-bench？

> 我的目标不是测模型会不会生成代码，而是测 Harness 能否帮助同一模型在真实仓库任务上更
> 稳定地完成定位、修改和验证。SWE-bench 提供真实 issue、固定 base commit 和可执行测试，
> 能把“看起来合理”变成 per-case resolved/unresolved，因此适合做纵向闭环。它不能覆盖 HITL、
> Memory、安全审批和 Fanout 冲突，这些由另一层确定性 regression 验收。

### 7. 五个 Case 怎么选？为什么只有五个？

**90 秒完整回答：**

> 项目当前候选全集是 SWE-bench Lite test 的 300 个 case。Smoke-5 是从这 300 个里人工分层
> 选的低成本机制回归集，不是随机样本，也不代表总体 resolved rate。
>
> 选择时有三类约束。第一，五题来自五个仓库和五种问题族：算法组合、类型边界、公共 API
> 解析、AST rewrite、继承与对象布局。第二，每题只有一个源码文件、最多三个参考 hunk，便于
> 把失败归因到 Harness，而不是被超大任务吞没；同时 patch 规模从 +1/-1 到 +51/-16，仍保留
> 差异。第三，每题都有 FAIL_TO_PASS 和 PASS_TO_PASS，既检查目标修复，也检查回归。
>
> 五题的作用是每次 Runtime 改动后快速发现代码定位、Tool Loop、验证或 evidence pipeline
> 是否退化。真正质量结论按层级看：candidate patch 只代表有 diff；local verified 只代表记录
> 的本地验证；只有 official per-case report 才计 resolved。要对外推总体能力，需要 Lite 300
> 或 Verified 的里程碑评测；要归因某个 Harness 因素，还要固定 model、temperature、case、
> environment 和预算，做多次 matched runs。

现场证据：

```bash
forge bench cases
forge bench case astropy__astropy-12907
forge bench swebench --regression-set smoke-5 --temperature 0 --evaluate
```

### 8. 一个 Case 具体怎样评？

> 先 checkout 数据集记录的 base commit。Agent 只获得 issue 和仓库，不获得 test patch 或 gold
> patch。运行后得到 trace、usage 和 candidate diff；FAIL_TO_PASS 是修复前失败、修复后必须
> 通过的目标测试，PASS_TO_PASS 是原本通过、修改后必须继续通过的回归测试。Official harness
> 应用 candidate patch 后执行这两组测试并给出 per-case outcome。项目默认隐藏 test/gold patch，
> 只有运行后人工复盘才显式打开，防止数据泄漏。

### 9. Agent 一直不给最终答案、又没有明显错误，怎么办？

> Single AgentLoop 没有 DAG。它的最终停机保证来自硬边界：max steps、timeout、累计 cost、
> 连续失败、完全相同的 tool intent 重复，以及单次响应的 tool-call burst 上限。重复 intent 的
> identity 是 tool name + canonical arguments，不包含执行结果；read 类重复可以给一次恢复提示，
> 写类副作用由 approval、operation ledger 和 target fingerprint 防止重复或 stale 执行。
>
> HITL 只用于缺少用户决策或需求澄清，不是所有 no-progress 的万能解。当前项目还没有对
> “参数不同但语义上没有新进展”的多步轨迹做通用判断，这类情况最后由 hard budget 停机并交给
> trace/failure taxonomy 复盘。Fanout 的 DAG 是另一条路径，并且在 worker 启动前就验证无环，
> 不能拿它解释 Single Agent 空转。

### 10. Temperature 是什么？项目怎样用？

> Temperature 控制 sampling 分布的随机性，不是模型置信度。低 temperature 让输出更集中，
> 高 temperature 增加候选差异。正式 Coding benchmark 默认固定为 0，并把 temperature 写入
> HTTP 请求、run artifact 和 ablation identity，避免两边采样配置不同却归因给 Runtime。
>
> 高 temperature 多次运行可以用于发现不稳定 case，但这是 hard-case mining，不是 official
> score。模型自报 confidence 只能是弱信号，不能替代人工标签或可执行测试。当前没有承诺跨
> provider seed；provider 支持时再记录 seed，否则使用明确 repetition index。

## 六、项目问题与本轮处理结果

| 项目问题 | 状态 | 现在的证据 |
| --- | --- | --- |
| 不知道候选全集和五题选择逻辑 | 已补 | `BenchmarkSetProfile` + `forge bench cases`。 |
| 不知道每个 case 具体做什么、怎样测 | 已补 | `forge bench case <id>` 展示 issue、F2P、P2P。 |
| 打开原始 JSON 才能讲题 | 已补 | 中文 Markdown/JSON presentation，可输出独立文档。 |
| test patch / gold patch 泄漏边界只是口头约定 | 已补 | 默认隐藏，显式 `--show-test-patch/--show-gold` 才可见，并有 secret regression test。 |
| temperature 未进入真实请求和实验身份 | 已补 | CLI/Workbench -> HTTP payload -> result/report/scorecard -> ablation gate。 |
| Smoke-5 是否代表总体能力 | 明确不代表 | 文档和 catalog 写入 claim boundary。 |
| Smoke-5 多次 official evidence matrix | 未完成 | 需要真实模型成本和 official evaluator 环境，不应伪造。 |
| 语义 no-progress 检测 | 未完成且不宜仓促补 | 当前只有 exact repeat + hard budgets；通用语义判断需权衡误杀。 |
| 无偏 holdout / milestone 评测 | 未完成 | 日常调试不应继续针对 test gold 调参；后续建立 dev/holdout 并里程碑跑全量。 |

## 七、面试前最小演练

1. 不看稿，在 30 秒内说完项目定位。
2. 不看稿，在 90 秒内回答候选全集、为什么五题、五题类型、指标层级、结论边界。
3. 现场执行 `forge bench cases` 和一个 `forge bench case`。
4. 画出 Single AgentLoop 停机链，明确说“这里没有 DAG”。
5. 用一句话解释 temperature，并说出它为什么必须进入实验 identity。
6. 把每个回答录音；如果第一句没有直接回答问题，重录。

## 八、最终判断

NanoHarness 目前足以支撑 Agent Harness 工程面试中的深入追问，但前提是你把它讲成一个
**有明确输入输出、真实控制路径、实验契约和边界意识的工程系统**。不要再用功能数量证明
深度。真正有说服力的是：你能解释为什么这样设计、失败时怎样定位、证据能证明什么，以及
哪些结论现在还不能说。
