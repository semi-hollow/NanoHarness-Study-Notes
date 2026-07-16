# Benchmark 闭环设计与面试表达

## 先说结论

NanoHarness 已经实现 SWE-bench 的 case 加载、仓库 checkout、Agent 执行、patch 导出、
official evaluator 适配、scorecard、failure taxonomy 和 matched ablation。现在还新增了
类型化 Smoke-5 选择契约、单 case inspector、默认防泄漏展示，以及进入真实请求和实验身份的
sampling temperature；当前不足主要是尚未形成多次 official run 的统计证据。

代码中配置了 5 个固定 SWE-bench Lite test case，历史运行 artifact 实际主要集中在
`astropy__astropy-12907`。因此现在可以声称：

> 项目打通了真实代码修复 benchmark 的执行与证据链，建立了可审计的 Smoke-5 regression
> contract，并能一条命令解释每题输入和测试义务。

现在还不能声称：

> 项目已经在 5 个 case 上完成稳定评测，或可以用这 5 个 case 的 resolved rate 代表整体
> SWE-bench 能力。

## SWE-bench 有多大

以项目当前使用的数据族为准：

| 数据集 | 规模 | 适合用途 |
| --- | ---: | --- |
| SWE-bench Full | 2,294 个 test instance，来自 12 个 Python 仓库 | 全面研究评测，成本高 |
| SWE-bench Lite | 300 个 test instance，另有 23 个 dev instance | 低成本迭代和标准化评测 |
| SWE-bench Verified | 500 个经工程师人工确认可解的 instance | 更可靠的最终能力评测 |

官方资料：

- [SWE-bench 原始论文](https://arxiv.org/abs/2310.06770)
- [SWE-bench Lite](https://www.swebench.com/lite.html)
- [SWE-bench Verified](https://www.swebench.com/verified.html)
- [官方 Evaluation Harness](https://www.swebench.com/SWE-bench/reference/harness/)

Lite 的 300 个 test case 不是简单随机缩小。官方筛选掉了依赖图片或外链、问题描述过短、
修改多个文件、gold patch 超过 3 个 hunk、创建或删除文件等任务。因此 Lite 更便宜、更稳定，
但也天然弱化了多文件修改和长程工程任务。

## 为什么 NanoHarness 选择 SWE-bench Lite

选择它不是因为它最全面，而是因为它同时满足五个工程条件：

1. 输入来自真实 GitHub issue，而不是人工编造 prompt。
2. Agent 必须在真实仓库中做定位、阅读、工具调用、修改和验证。
3. 每个 case 有 base commit 和可执行测试，可以形成客观 outcome。
4. 官方 Docker harness 可以把 candidate patch 与 official resolved 分开。
5. 300 个 Lite case 比 2,294 个 Full case 更适合个人项目反复迭代。

它特别适合验证 Coding Harness 的纵向闭环，但不能覆盖通用 Agent 的全部能力。Memory、HITL、
partial recovery、tool safety 和 fanout conflict 仍需要项目自己的确定性 regression case。

## 当前五个 Case 是什么

这 5 个 case 来自 Lite test split 中 5 个不同仓库，覆盖不同代码形态和 patch 规模。

| Case | 问题类型 | Gold patch 特征 | Official test obligation | Harness 价值 |
| --- | --- | --- | --- | --- |
| `astropy__astropy-12907` | 嵌套模型组合的算法正确性 | 1 文件、1 hunk、`+1/-1` | 2 个 fail-to-pass、13 个 pass-to-pass | 非平凡定位、矩阵语义、极小 patch |
| `django__django-11133` | `memoryview` 类型边界兼容 | 1 文件、1 hunk、`+1/-1` | 1 个 fail-to-pass、64 个 pass-to-pass | framework API、类型转换、回归面较大 |
| `matplotlib__matplotlib-18869` | 顶层版本信息和版本解析 | 1 文件、1 hunk、`+51/-16` | 4 个 fail-to-pass、3 个 pass-to-pass | public API、较大实现 patch、多输入语义 |
| `pytest-dev__pytest-5103` | `all/any` assertion AST rewrite | 1 文件、3 hunks、`+25/-0` | 1 个 fail-to-pass、64 个 pass-to-pass | parser/AST reasoning、错误报告质量 |
| `sympy__sympy-20590` | 继承链和 `__slots__` 对象布局 | 1 文件、1 hunk、`+5/-0` | 1 个 fail-to-pass、21 个 pass-to-pass | 大仓导航、继承语义、性能相关回归 |

### 为什么只选五个

最诚实的答案是：

> 这五个是低成本、高异质性的工程回归样本，不是统计代表性样本。我希望每次修改 Harness
> 后都能负担得起重复运行，同时覆盖算法、类型边界、公共 API、AST 和继承语义。它们用于
> 发现 runtime regression，不用于报告 leaderboard 水平。

当前选择仍然是人工启发式选择，集合目标、候选全集、约束、覆盖维度和每题入选原因已经进入
机器可读 `BenchmarkSetProfile`；它仍没有覆盖多文件任务。面试时不要把“来自五个仓库”说成
“代表整个 Lite 分布”。

直接查看：

```bash
forge bench cases
forge bench case astropy__astropy-12907
```

第二条命令默认只显示 issue、base commit、F2P 和 P2P，不显示 official test patch 或 gold
patch。运行后复盘才显式使用 `--show-test-patch` 或 `--show-gold`。

## 一个 Case 怎样变成完整证据链

```text
frozen dataset instance
  -> checkout exact base_commit
  -> freeze model/runtime/environment identity
  -> AgentLoop executes governed tools
  -> trace.json + usage.json + patch.diff
  -> local validation
  -> official SWE-bench evaluator
  -> per-case resolved / unresolved / evaluator error
  -> failure taxonomy + scorecard
```

每个 case 至少产生五类指标：

| 层级 | 指标 | 能回答的问题 |
| --- | --- | --- |
| Outcome | official resolved、local verified | 最终修复是否正确 |
| Reachability | patch generated、正确文件是否被定位 | Agent 是否到达有效修改阶段 |
| Runtime behavior | steps、tool calls、failed/repeated calls、recovery | Harness 为什么成功或失败 |
| Resource | tokens、cost、latency | 改进是否更高效 |
| Governance | blocked action、approval、overflow、stale state | 安全和恢复边界是否生效 |

`patch generated` 只能证明产生了候选修改；`local verified` 只能证明本地记录的验证通过；只有
official per-case report 明确 `resolved=true`，才能计入 official resolved rate。

## 怎样量化 Harness 改进

不要把所有指标压成一个“综合分”。采用有优先级的多维 scorecard：

1. 第一优先级：固定分母上的 official resolved rate。
2. 质量不下降时，再比较总 token、总成本、P50/P95 latency、tool failure rate。
3. 用 `cost / resolved case` 衡量单位有效修复成本。
4. 用 failure taxonomy 观察失败从哪一层迁移，而不是只看总分。
5. Safety invariant 单独判断，危险越界不能用更高 resolved rate 抵消。

比较 Runtime A/B 时必须固定：

- dataset、split、case id 和 dataset revision；
- base commit、official evaluator 和 container image；
- provider、实际 model、prompt、tool surface 和预算；
- 除声明 factor 外的所有配置；
- 并发策略和重复次数。

每个 variant 至少重复 3 次。即使 temperature 为 0，provider 和工具轨迹仍可能存在波动。
报告每个 case 的 solve consistency，再报告 aggregate mean；best-of-N 必须单独标注，不能与
single-run pass@1 混在一起。

## 正确的三层 Benchmark 体系

### 第一层：PR 级确定性回归

Unit test 和小型 synthetic case，验证 context compaction、memory authority、HITL、resume、
tool policy、idempotency 和 fanout conflict。便宜、稳定，每次提交运行。

### 第二层：开发期 SWE-bench 回归

- `smoke-5`：当前五个 case，用于快速发现执行链退化。
- `dev-23` 或分层抽样 `dev-30`：用于阶段性判断 Runtime 改进。
- 至少 3 次重复，保留完整 per-case artifact。

当前五个 case 来自 test split，又被反复人工分析，已经不适合作为无偏 holdout。后续应优先
使用 Lite dev 做日常调试，并建立一组不看 gold patch、不针对性调参的 holdout case。

### 第三层：里程碑评测

在功能稳定后运行 Lite 300 或 Verified 500，并使用官方 evaluator。只有这一层适合对外报告
可与其他系统比较的 resolved rate。个人项目无法频繁承担全量成本，可以按里程碑运行，
但不能用 smoke-5 的结果替代全量结果。

## NanoHarness 还需要补什么

### P0：把已有五个 Case 跑成可引用证据

已完成：`core` 改为 `smoke-5`；集合和单题契约已类型化；默认防泄漏；temperature 已进入
transport、artifact 和 identity gate。

仍需完成：

1. 同一模型、同一预算运行 3 次，共 15 个 official evaluation。
2. 发布 per-case scorecard、失败分布和 cost/latency，不只放一个 Astropy demo。
3. 先用 gold patch 做 evaluator/environment preflight，区分 Agent 失败和评测环境失败。
4. 补 dataset revision、runtime Git SHA、prompt/tool manifest identity。

### P1：增加可归因的实验设计

1. 对 tool routing、context compaction、Skill、Memory 分别做 single-factor paired ablation。
2. 增加 mean、median、P95、solve consistency、cost per resolved case。
3. 记录 dataset revision、runtime Git SHA、prompt/tool manifest SHA，以及 provider 支持时的随机种子；不支持 seed 时记录独立 repetition index。当前已经记录 temperature，不能把 temperature 当 seed。
4. 对不匹配的 official coverage 拒绝计算质量 delta。

### P2：补足通用 Agent Harness 边界

SWE-bench 不验证 HITL、长期记忆污染、恢复幂等、权限 stale、multi-agent conflict 和 research
citation quality。继续保留项目自己的 deterministic mini-case，但不要把它们称为 SWE-bench，
也不要把 mini-case pass rate 与 official resolved rate混合。

## 面试 90 秒回答

> 我选择 SWE-bench，是因为它把真实 GitHub issue、确定 base commit、真实仓库工具交互和
> 可执行测试串成了一个客观闭环，能验证 Harness 是否真的帮助模型完成工程任务，而不只是
> 生成看起来合理的代码。Full 有 2,294 个任务；我当前接的是 Lite test 的 300 个任务，并
> 固定了其中 5 个不同仓库的 case 做低成本 regression smoke。五个 case 分别覆盖算法组合、
> 类型边界、公共 API、AST rewrite 和继承对象布局，gold patch 从 2 行到 67 行不等。
>
> 我明确不把这 5 个样本当 leaderboard benchmark。它们的作用是每次 Runtime 修改后快速
> 检查 patch reachability、official correctness、tool failure、token、cost 和 failure class。
> 做 A/B 时，我会固定 case、模型、环境和预算，只允许声明的 Harness factor变化，并按 case
> 做 paired comparison。项目目前的不足是历史证据主要集中在 Astropy 单 case，下一步是把
> smoke-5 跑成 3 次重复的 official matrix，再建立 dev set 和 milestone Verified evaluation。
> SWE-bench 只验证 code repair，因此 HITL、Memory、安全和恢复能力由另一层确定性 regression
> suite 验收，两个分数不会混在一起。

现场先运行 `forge bench cases`，再运行 `forge bench case <id>`。这样回答不是背出来的，
而是由项目自己的评测契约支撑。

## 常见追问边界

**为什么不用 Full？**

个人项目需要高频迭代，Full 的执行和容器成本过高。Lite 是开发期折中，最终里程碑仍应跑
Lite 全量或 Verified。

**五个 case 为什么可信？**

它们适合做异质性 smoke test，但不具备统计代表性。可信的是 per-case 执行证据，不是由五个
样本外推的总体 resolved rate。

**你怎样证明是 Harness 改进，不是模型波动？**

固定输入身份和环境，单因素 paired ablation，多次重复，比较相同 case 的 outcome 与成本，
并报告波动和失败类别。

**SWE-bench 能证明 Multi-Agent 更好吗？**

只有在同一 case、同一模型预算下做 single/multi paired run，并获得 official outcome 后，
才能支持局部结论。Lite 多数是单文件任务，本身不适合证明 fanout 或冲突合并能力。
