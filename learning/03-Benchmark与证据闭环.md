# Benchmark 与证据闭环

Benchmark 不是项目最后补的一张成绩表，而是决定 Runtime 改动是否成立的验收合同。

## 先回答评测问题

NanoHarness 要测的不是“模型会不会写代码”，而是：

> 固定模型、任务、预算和环境后，某个 Runtime preset 是否让真实仓库任务更稳定地完成，
> 失败模式、成本和恢复行为发生了什么变化？

因此评测必须同时保存 task identity、runtime identity、execution environment、trajectory 和
最终 correctness，不能只统计 token 或 patch 数量。

## 为什么使用 SWE-bench

SWE-bench case 提供真实 issue、repository、base commit 和可执行测试。Agent 需要理解现有
代码、定位、修改并验证；official evaluator 能将“看起来合理”变成 per-case
resolved/unresolved。

它适合验证 repository-level code repair，但不能覆盖 HITL、审批 stale、Memory 生命周期和
Fanout 冲突。这些由确定性 regression suite 验收。

## Smoke-5 是什么

- 候选全集：SWE-bench Lite test 的 300 个 case。
- 选择方法：人工分层，不是随机采样。
- 目标：低成本检查 Harness 机制回归，不估计总体解决率。
- 约束：五个不同仓库、五类问题；每题一个源码文件、最多三个参考 hunk；都有
  FAIL_TO_PASS 与 PASS_TO_PASS。
- 防泄漏：运行时只给 issue 与 base commit，不给 test patch 或 gold patch。

| Case | 问题族 | 主要观察点 |
| --- | --- | --- |
| `astropy__astropy-12907` | 算法语义与嵌套组合 | 跨调用链定位、最小 patch、测试验证 |
| `django__django-11133` | 类型边界与框架兼容 | 公共 API、bytes/string 行为、回归保护 |
| `matplotlib__matplotlib-18869` | 公共 API 与版本解析 | 多分支规则、边界输入、兼容性 |
| `pytest-dev__pytest-5103` | AST rewrite 与诊断 | AST 导航、多 hunk 编辑、错误报告 |
| `sympy__sympy-20590` | 继承语义与对象布局 | 大仓导航、非局部根因、对象布局 |

先看题，不运行 Agent：

```bash
forge bench cases --regression-set smoke-5
forge bench case astropy__astropy-12907
```

## 一个 Case 的证据链

```text
dataset issue + base commit
  -> clean checkout / execution manifest
  -> AgentLoop trace + usage
  -> candidate patch
  -> local validation evidence
  -> official FAIL_TO_PASS / PASS_TO_PASS result
  -> failure class + scorecard + case study
```

| 层级 | 分母 | 正确解释 |
| --- | --- | --- |
| Patch rate | 全部 case | 是否产生非空 candidate diff |
| Local verification rate | 有明确本地 test evidence 的 case | 记录的本地验证是否通过 |
| Official resolved rate | 有 parsed official outcome 的 case | 官方 evaluator 是否判定 resolved |

Official denominator 为空时结果是未知，不是 0%。Process exit code、Reviewer PASS、
`model_patch` 非空都不能代替 official outcome。

## Failure Taxonomy 的用途

失败分类必须有优先级，否则同一 case 可能同时符合多个标签。高层次分法是：

```text
environment unavailable
  -> official evaluation failed/unavailable
  -> no candidate patch
  -> local verification failed/unverified
  -> official unresolved
  -> resolved / incomplete evidence
```

分类目标不是给失败起漂亮名字，而是把下一次行动指向正确 owner：模型协议、context、tool、
safety、environment、evaluation adapter 或 task 本身。

## 怎样比较 Runtime 改动

### 单因素 Ablation

只改变一个因素，例如 tool routing；dataset、case、provider/model、temperature、预算和环境
必须匹配。Comparator 应拒绝未声明 drift。

一次 matched pair 只能形成 case study，不能估计随机方差。

### Repeated Campaign

当前 campaign 比较两个同核 preset：

- `minimal-control`：完整工具可见性、关闭 Skill。
- `governed-runtime`：task-aware routing、启用内置 Skill。

```bash
forge bench campaign \
  --regression-set smoke-5 \
  --repetitions 3 \
  --evaluate \
  --publish
```

五题、两个 preset、三次重复共 30 个 slot。运行顺序交错；每个 slot 原子 checkpoint；resume
跳过 completed，只重试 running/failed。Campaign 绑定 source revision、config digest 与
execution identity。

两个 preset 同时改变 routing 与 Skill，所以只能说“整体 preset 的 outcome 不同”，不能把
差异归因给某一个机制。需要因果结论时，再做单因素 matched ablation。

## 应该读哪些指标

优先级从高到低：

1. Official resolved / denominator。
2. Paired wins、losses、ties 与跨 repetition 稳定性。
3. Failure taxonomy 分布。
4. Candidate/local evidence，用于定位执行阶段。
5. Cost、token、latency、tool failure 与 repair。
6. Context compaction、Memory recall、Skill activation 等机制计数。

后四类指标帮助解释原因，但不能替代 correctness。

## 一个合格的实验结论

错误说法：

> Governed runtime patch rate 更高，所以解决率更高。

合格说法：

> 在相同 case、model、temperature、预算和执行环境下，两个 preset 完成了各 N 次 matched
> run。双方都有 official outcome 的 pair 中，treatment 为 X 胜/Y 负/Z 平；成本变化为 ...。
> 由于 preset 同时改变 routing 与 Skill，这个结果只支持整体 preset 差异。失败主要集中在
> 某 taxonomy，下一步将对该因素单独 ablate。

## 当前不能说什么

- Smoke-5 代表 SWE-bench Lite 300 题总体能力。
- Candidate patch 或 local test 通过等于 official solved。
- 一次 run 足以证明稳定提升。
- Direct model 无工具 baseline 是有竞争力的框架 baseline。
- Multi-Agent 更贵或更慢就一定更差；需要同时看 correctness 和任务类型。
- 没有公开 artifact 的数字可以写进 README 或 CV。

## 闭卷检查

1. 90 秒解释为什么选择 SWE-bench、为什么只选五题，以及五题不能证明什么。
2. 随机挑一个 Smoke-5 case，说出问题族、F2P/P2P 作用和 Harness 观察点。
3. 画出 candidate、local、official 三层分母。
4. 解释为什么 process exit code 不能判定 resolved。
5. 设计一个 tool-routing 单因素实验，列出必须冻结的变量。
6. 解释 repeated campaign 为什么仍不是单因素实验。
7. 给一份只有 patch、没有 official result 的 run 下结论，必须使用“未知”而不是“失败”。

答题后必须现场执行一次 `forge bench case`，并在 Workbench 中找到对应 run matrix 或
scorecard。只会背定义、不会检查 artifact，最多记 1 分。
