# Benchmark 与证据闭环

> 层级：[返回总入口](../README.md) → A4 主学习链 → Evidence；顺序只以总入口为准。

Evidence 不是项目最后补的一张成绩表，而是每个 Runtime claim 的验收合同。主演示只讲一个真实
Run Story；Benchmark 采样和 Campaign 细节降为追问。

## Canonical Run Story

```text
task identity + runtime identity + environment
  -> context/model/tool timeline
  -> policy gate + operation + checkpoint/resume
  -> candidate patch + validation
  -> local / official outcome
  -> failure diagnosis + claim boundary
```

`forge inspect <run-or-artifact>`、默认只读 Workbench 和静态报告必须读取同一份 canonical
Read Model，不能各自从文件名、exit code 或 JSON 字段重新猜状态。

Run Story 一屏只回答：

1. 这次 run 要解决什么，基于哪个 commit？
2. Context、模型和工具发生了什么关键决策？
3. 哪个 policy/HITL gate 改变了执行？
4. 产生了哪些 artifact，各自由谁发布？
5. candidate、local、official 分别支持什么结论？

确定性 Demo 可以复用同一视图，但只证明控制面；模型能力必须来自真实 provider run 和 evaluator
artifact。

## Artifact 血缘合同

每个 run artifact 的 manifest/catalog entry 至少包含：

| 字段 | 回答的问题 |
| --- | --- |
| `kind` / `relative_path` | 它是什么，稳定地址在哪里 |
| `producer_symbol` / `flow_stage` | 哪个 owner 在流程哪一步创建它 |
| `semantic_consumers` | inspect、resume、local/official evaluator 谁会读取 |
| `derived_from` / `source_event_refs` | 可追溯到哪个 artifact/event |
| `evidence_level` | 原始事实、派生投影还是 evaluator 判定 |
| `proves` / `does_not_prove` | 能支持和不能支持什么 claim |
| `rebuildable` / `deletion_impact` + hash/size | 能否重建、删除会失去什么 |

典型解释：

| Artifact | Producer | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| `run_request.json` | Single-run boundary | 输入与配置身份 | 实际执行完全符合预期 |
| `trace.json` | Trace recorder | 记录到的运行事件 | 未记录外部事实一定没发生 |
| checkpoint | `RunLifecycle` / state repository | durable continuation state | Python stack 或隐藏模型状态 |
| operation ledger | `OperationTracker` repository | 已批准/执行/拒绝的 operation | 副作用业务结果一定正确 |
| `patch.diff` | artifact publisher | 产生 candidate diff | 测试通过或 issue resolved |
| local validation | local executor/evaluator | 指定本地检查的结果 | official tests 全部通过 |
| official result | official evaluator adapter | evaluator 对该 case 的判定 | 对其他 case 的总体能力 |

能从 trace 重建的投影可以删除并再生成；不可重建的原始事实、checkpoint 或 evaluator result 必须
按保留策略保存。不要为了回答“为什么不能删”而假装每个文件都不可删除。

## 三层 Evidence 与分母

| 层级 | 分母 | 正确解释 |
| --- | --- | --- |
| Candidate patch rate | 全部目标 run/case | 是否产生非空 candidate diff |
| Local verification rate | 有明确本地 test evidence 的 run/case | 记录的本地验证是否通过 |
| Official resolved rate | 有 parsed official outcome 的 case | 官方 evaluator 是否判定 resolved |

Official denominator 为空时是 `Unknown`，不是 0%。Process exit code、Reviewer PASS、非空 patch、
模型自述“完成”都不能替代 official outcome。

## 一个真实 Case 的证据链

```text
dataset issue + base commit
  -> clean checkout / execution manifest
  -> AgentLoop trace + usage
  -> candidate patch
  -> local validation evidence
  -> official FAIL_TO_PASS / PASS_TO_PASS result
  -> failure class + scorecard / Run Story
```

SWE-bench 适合验证 repository-level code repair，因为它提供真实 issue、repository、base commit
和可执行测试；它不能覆盖 approval stale、Memory 生命周期或 Fanout 冲突，这些由确定性 regression
测试证明。

## 亲手走一次 astropy Case

从环境初始化、只读 Case、DeepSeek run、断点、手工 pytest 到 Official Harness 的唯一操作说明见
[从命令到 Evidence：macOS 全链路实操](05-从命令到Evidence全链路实操.md)。本页只保留证据语义：
默认先隐藏 gold/test patch；`schema()` 只公开 Tool 契约，`execute()` 才经 Execution Environment
启动 pytest；Local verified 必须能回到 trace 中明确的 kind、target/argv、exit code 和输出。依赖缺失、
未收集测试或手工命令未进入 trace，都不能伪装成 canonical Local PASS。

## Failure Taxonomy：把行动指回 owner

```text
environment unavailable
  -> official evaluation failed/unavailable
  -> no candidate patch
  -> local verification failed/unverified
  -> official unresolved
  -> resolved / incomplete evidence
```

分类要有稳定优先级和引用的 artifact。目标不是给失败命名，而是决定下一次该改模型协议、Context、
Tool/Safety、Environment、Evaluation Adapter，还是 task 本身。

## 随机 Artifact 定位训练

每轮任选一个 run 目录中的文件，不靠文件名猜答案：

```bash
forge inspect latest
forge inspect <run-or-artifact>
```

限时两分钟回答：

1. artifact type、producer 和 lifecycle phase 是什么？
2. 它来源于哪个 run/event，谁消费？
3. 它是原始事实、派生投影还是 evaluator authority？
4. 它能证明什么、不能证明什么？
5. 删除后能否重建；不能时会破坏 recovery、audit 还是 evaluation？

任一答案来自猜测而非 manifest/trace/owner code，训练不通过。

## 追问层：实验与 Campaign

### Smoke-5

候选全集是 SWE-bench Lite test 的 300 个 case；Smoke-5 是五仓库、五问题族、都有
FAIL_TO_PASS/PASS_TO_PASS 的人工分层机制回归集。运行时隐藏 test/gold patch。它不估计 Lite
总体解决率，也不要求背五题细节。

```bash
forge bench cases --regression-set smoke-5
forge bench case astropy__astropy-12907
```

### Matched Ablation

验证单因素改动时，dataset/case、provider/model、temperature、预算和环境必须匹配；Comparator
应拒绝未声明 drift。一次 matched pair 只能形成 case study，不能估计随机方差。

### Repeated Campaign

当前 `minimal-control` 与 `governed-runtime` 同时改变 routing 和 Skill，因此只能比较整体 preset，
不能单因素归因。Smoke-5、两个 preset、三次重复是 30 个 slot；顺序交错、每 slot 原子 checkpoint，
resume 跳过 completed。优先读取 official paired wins/losses/ties、跨 repetition 稳定性，再看 failure、
cost、token 和机制计数。

真实 official repeated campaign 仍是最高价值缺口。入口和文档整改不能长期阻塞 10-run pilot 与
后续公开 sanitized evidence。

## 当前不能说什么

- Smoke-5 代表 SWE-bench Lite 总体能力。
- Candidate patch 或 local PASS 等于 official solved。
- 一次 run 足以证明稳定提升。
- 两个 multi-factor preset 的差异来自单一机制。
- Deterministic Demo 证明模型推理质量。
- 没有公开 artifact 的数字可以写进 README/CV。

## 闭卷检查

1. 用一个 Run Story 串起 task、tool gate、checkpoint、patch 与三层 evidence。
2. 随机定位一个 artifact，回答 producer、consumer、authority、claim 和可重建性。
3. 画出 candidate、local、official 三层分母，解释 `Unknown`。
4. 给一份有 patch、无 official result 的 run 下结论。
5. 解释 repeated campaign 为什么仍不等于单因素实验。

只会读最终数字、不能从结论返回 artifact 和 owner，最多记 1 分。
