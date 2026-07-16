# Agent Forge Multi-Agent 学习指南

> 目标：用最短路径学懂最新 multi-agent / single-vs-multi compare 实现，并能在 3 年以上 AI Agent 开发面试中讲清楚设计、取舍、证据和限制。

## 0. 先记住这条主线

不要把这个项目讲成“我做了多个 agent 互相聊天”。更准确的说法是：

> Agent Forge 的核心 runtime 是 `AgentLoop`。multi-agent 有两条外层路径：`MultiAgentCoordinator` 用显式 artifact handoff 做顺序 review workflow；`LiveFanoutCoordinator` 用 validated DAG、独立 worktree 和 scope gate 并发执行互不影响的 task。两者都复用同一个 AgentLoop，并留下可恢复、可审计、可评估的证据。

这句话对应 7 个关键词：

| 关键词 | 你要理解什么 | 对应代码/产物 |
| --- | --- | --- |
| `AgentLoop` | 单 agent 的 canonical runtime，不被 multi-agent 替代 | `agent_forge/runtime/agent_loop.py` |
| coordinator | multi-agent 是外层编排，不是 swarm | `agent_forge/multi_agent/coordinator.py` |
| live fanout | 本地真实并发 worker，不是 callback 原型 | `agent_forge/multi_agent/live_fanout.py` |
| ownership | depends_on + write_scope 决定并行、串行或 conflict gate | `agent_forge/multi_agent/fanout.py` |
| artifact handoff | agent 之间通过文件交接，不靠隐藏聊天状态 | `agent_forge/multi_agent/artifacts.py`, `.agent_forge/runs/.../multi_agent/` |
| review loop | reviewer/verifier 用 `PASS` / `NEEDS_REVISION` / `BLOCKED` 控制 revision | `agent_forge/multi_agent/profiles.py` |
| compare evidence | single 和 multi 在隔离 workspace 中对同一 case 做对比 | `agent_forge/bench/swebench.py`, `agent_forge/evaluation/` |

---

## 1. 推荐学习顺序

不要从文件树开始乱看。按这个顺序学：

1. **先跑命令**：看到真实输出目录。
2. **先看 artifacts**：理解系统留下了什么证据。
3. **再读 6 个核心文件**：建立调用链。
4. **再看 compare/evaluation**：理解为什么 multi-agent 不是口头概念。
5. **最后准备面试表达**：把代码设计转成工程语言。

---

## 2. 第 0 层：只跑，不看源码

### 2.1 环境检查

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
source .venv/bin/activate
forge doctor
```

看点：

- Python 是否来自 `.venv`。
- DeepSeek API key 是否存在。
- Docker / swebench 是否缺失。

Docker 或 `swebench` 缺失不影响你学习 multi-agent 主流程，只影响官方 SWE-bench evaluation。

### 2.2 不需要 API key 的测试

```bash
source .venv/bin/activate && python -m unittest tests.test_swebench_compare -v
source .venv/bin/activate && python -m unittest tests.test_evaluation_comparison -v
```

这两个测试是学习 compare 的入口：

- `tests/test_swebench_compare.py`：证明 compare mode 会跑 single 和 multi 两个隔离 variant，并写出 `comparison.json` / `evaluation_report.md`。
- `tests/test_evaluation_comparison.py`：证明 metrics extraction 和 report rendering 不是空壳。

### 2.3 跑 single-agent

需要 DeepSeek 或兼容 provider 的配置：

```bash
forge run "阅读这个项目结构并说明入口，不要修改文件" --provider deepseek
```

跑完看：

```bash
forge report latest
forge replay latest
```

### 2.4 跑 multi-agent 的 coding profile

```bash
forge run "fix the failing test in this repository" \
  --agent-mode multi \
  --profile coding_fix \
  --provider deepseek \
  --max-revision-rounds 2
```

学习时不要求它一定修好真实问题。你关注的是：

- 是否出现 multi-agent 目录；
- role artifact 是否写出；
- reviewer/verifier 是否产生 decision；
- revision_rounds 如何记录。

### 2.5 跑 single-vs-multi compare

最新本地 master 的 commit `8f6685b multi agent compare` 已实现 compare。某些旧文档可能还写着 compare 尚未完成，以最新代码为准。

```bash
forge bench swebench \
  --showcase \
  --agent-mode compare \
  --profile coding_fix \
  --provider deepseek \
  --max-steps 16 \
  --max-revision-rounds 2
```

依赖说明：

- 需要 provider 配置。
- 可能需要 git/network clone showcase repo。
- 不加 `--evaluate` 时不需要 Docker 官方评测。
- `patch_generated` 不是 solved，只是生成了 candidate patch。

---

## 3. 第 1 层：先看 artifacts，不看源码

一次 `forge run --agent-mode multi` 之后，重点看：

```text
.agent_forge/runs/<run-id>/
  trace.json
  usage.json
  usage_report.md
  final_answer.txt
  multi_agent/
    artifact_index.json
    multi_agent_summary.json
    multi_agent_report.md
    artifacts/*.md
```

### 3.1 `trace.json`

它回答：agent 每一步做了什么？

面试说法：

> 我不是只看最终回答，而是把 agent 的每次模型调用、工具调用、失败 observation、agent_name 都记录进 trace，所以可以 replay 和 debug。

### 3.2 `usage_report.md`

它回答：这次 run 花了多少 token/cost？上下文和工具效率如何？

面试说法：

> Agent 系统不能只看能不能跑，还要看成本、上下文预算和工具失败率。usage report 是我做成本治理和失败定位的入口。

### 3.3 `multi_agent/artifact_index.json`

它回答：每个 role 产出了哪些 artifact？

这是 artifact handoff 的目录索引。

### 3.4 `multi_agent/multi_agent_summary.json`

它回答：

- profile 是什么；
- overall status 是什么；
- revision_rounds 几轮；
- 每个 role 的 status/decision/artifact 是什么。

这是讲 multi-agent 的核心证据。

### 3.5 `multi_agent/artifacts/*.md`

这些是 agent 之间真正交接的信息。

你要理解这个设计：

```text
Implementer output -> markdown artifact
Reviewer reads artifacts -> review artifact
Verifier reads artifacts -> verification artifact
Coordinator reads decisions -> maybe revision
```

不是：

```text
Agent A 在聊天里随便告诉 Agent B
```

这点很重要，因为它体现可审计、可 replay、可控上下文。

---

## 4. 第 1.5 层：怎么看 compare artifacts

跑 compare 后看：

```text
.agent_forge/runs/<swebench-run-id>/
  cases/<case-id>/
    single/
      cases/<case-id>/
        trace.json
        patch.diff
        usage.json
        usage_report.md
    multi/
      cases/<case-id>/
        trace.json
        patch.diff
        usage.json
        usage_report.md
        multi_agent/
          multi_agent_summary.json
          multi_agent_report.md
    comparison.json
    evaluation_report.md
```

### 4.1 为什么要有 single 和 multi 两个目录？

因为公平比较必须隔离 workspace。

面试说法：

> Compare mode 不是在同一个 checkout 上连续跑两次，因为 single 的 patch 会污染 multi。它给同一个 case 准备 single/multi 两个隔离 variant，再统一抽指标。

### 4.2 `comparison.json`

机器可读的对比结果。重点字段：

- `single_status`
- `multi_status`
- `single_patch_generated`
- `multi_patch_generated`
- `single_cost_usd`
- `multi_cost_usd`
- `single_tool_calls`
- `multi_tool_calls`
- `revision_rounds`
- `verifier_status`
- `recommendation`

### 4.3 `evaluation_report.md`

这是人类可读的 evidence card。面试时优先打开这个文件。

它应该回答：

- single 和 multi 谁生成 patch；
- multi 多花了多少成本；
- reviewer/verifier 有没有提供额外质量信号；
- 是否能声称 resolved；
- 推荐用 single 还是 multi。

### 4.4 不要说错

不要说：

> compare 证明 multi-agent 一定更好。

要说：

> compare 证明这个 harness 能在同一 case 上公平比较 single 与 multi 的质量信号和成本。multi-agent 是否值得，需要按 case-by-case 阅读 report。

---

## 5. 第 2 层：只读 9 个核心文件

### 5.1 第一组：运行入口

#### 1. `agent_forge/forge_cli.py`

看：

- `build_parser()`：CLI 暴露哪些模式。
- `run_repository_task()`：普通 `forge run` 如何进入 single/multi。

你要能讲：

> CLI 只是入口，真正 runtime 是 AgentLoop；multi-agent 只是根据 `--agent-mode multi` 走 MultiAgentCoordinator。

#### 2. `agent_forge/bench/swebench.py`

看：

- `run_swebench()`：benchmark 主循环。
- `_run_case()`：单个 case 如何执行 single 或 multi。
- `_run_compare_case()`：compare 如何跑 single + multi，然后写 evaluation artifacts。

最重要的调用链：

```text
run_swebench(agent_mode="compare")
  -> _run_compare_case()
      -> _run_case(agent_mode="single")
      -> _run_case(agent_mode="multi")
      -> extract_run_metrics()
      -> compare_runs()
      -> write_evaluation_artifacts()
```

### 5.2 第二组：single-agent runtime

#### 3. `agent_forge/runtime/agent_loop.py`

看它如何循环：

```text
build context -> call model -> parse tool call -> route tool -> observe -> repeat -> final answer
```

你不用背所有细节，重点理解：

- `AgentLoop` 是 canonical runtime；
- trace 记录贯穿这里；
- tools 不是模型随便执行，而是经过 registry/router/safety；
- `agent_name` 能进入 trace，用来区分 multi-agent role。

### 5.3 第三组：multi-agent 核心

#### 4. `agent_forge/multi_agent/types.py`

理解这些概念：

- `RoleSpec`：一个 role 能做什么。
- `AgentProfile`：一组 roles，形成一个工作流。
- `Artifact`：role 输出的文件化结果。
- `RoleRunResult`：role 执行状态。
- `MultiAgentRunSummary`：整个 multi-agent run 的 summary。

#### 5. `agent_forge/multi_agent/profiles.py`

重点看 `coding_fix_profile()`：

- `Implementer` 可以写代码、跑命令；
- `Reviewer` 只读；
- `Verifier` 可以跑验证命令；
- decision marker 是 `PASS` / `NEEDS_REVISION` / `BLOCKED`。

面试说法：

> RoleSpec 的价值是把 agent 能力收窄：不同 role 有不同 tool allowlist 和 max_steps，reviewer 不应该能写代码。

#### 6. `agent_forge/multi_agent/coordinator.py`

这是 multi-agent 的主文件。

你要找到这些点：

- 它调用 `AgentLoop(...).run(..., agent_name=role.name)`；
- 每个 role 的输出写 artifact；
- reviewer/verifier 的 decision 决定是否 revision；
- revision 有上限；
- raw provider tool-call markup 会触发质量检查 gate。

核心讲法：

> Coordinator 只负责流程控制，不重新实现 agent runtime。这样避免两套 runtime 分叉，也让 single/multi 可以公平比较。

#### 7. `agent_forge/multi_agent/artifacts.py`

看：

- artifact 如何写入；
- index/summary/report 如何生成；
- handoff context 为什么 newest-first。

面试说法：

> artifact handoff 让每个 role 的输入输出都能被审计，也避免 multi-agent 变成不可观察的聊天链。

### 5.4 第四组：evaluation

#### 8. `agent_forge/evaluation/metrics.py`

看 `extract_run_metrics()`。

它把不同来源压平：

- case result dict；
- `usage.json`；
- `multi_agent_summary.json`。

输出给 `compare_runs()`。

#### 9. `agent_forge/evaluation/comparison.py` 和 `agent_forge/evaluation/report.py`

看：

- `compare_runs()` 如何生成保守 recommendation；
- `render_evaluation_report()` 如何输出面试可读 report。

重点：recommendation 很克制，不会说 multi 一定更好。

---

## 6. 完整流程图

### 6.1 `forge run --agent-mode multi`

```text
User task
  -> forge_cli.run_repository_task()
  -> build_registry(workspace)
  -> resolve_llm_config()
  -> build_llm()
  -> RuntimeConfig
  -> get_profile("coding_fix")
  -> MultiAgentCoordinator.run()
      -> build role prompt for Implementer
      -> AgentLoop.run(agent_name="Implementer")
      -> ArtifactStore writes implementer artifact
      -> build handoff context
      -> AgentLoop.run(agent_name="Reviewer")
      -> parse reviewer marker
      -> AgentLoop.run(agent_name="Verifier")
      -> parse verifier marker
      -> if NEEDS_REVISION and budget remains:
           run Implementer again with feedback
      -> write multi_agent_summary.json
      -> write multi_agent_report.md
  -> trace.write()
  -> write_usage_artifacts()
  -> final_answer.txt
```

### 6.2 `forge bench swebench --agent-mode compare`

```text
run_swebench()
  -> load_cases()
  -> for each case:
      -> _run_compare_case()
          -> _run_case(agent_mode="single")
              -> prepare single workspace
              -> AgentLoop
              -> patch.diff / trace / usage
          -> _run_case(agent_mode="multi")
              -> prepare multi workspace
              -> MultiAgentCoordinator
              -> patch.diff / trace / usage / multi_agent_summary
          -> extract_run_metrics(single)
          -> extract_run_metrics(multi)
          -> compare_runs()
          -> write_evaluation_artifacts()
  -> predictions.jsonl uses multi patch as candidate patch
  -> optional official SWE-bench eval
  -> report.md
```

---

## 7. 面试高频问题与回答

### Q1：你的 multi-agent 和 prompt chain 有什么区别？

答：

> 我没有做自由形式的 prompt chain，而是做 coordinator-driven workflow。每个 role 有 RoleSpec，包含职责、工具 allowlist、max steps 和输出 artifact 类型。role 之间通过 ArtifactStore 交接，coordinator 解析 reviewer/verifier 的 decision marker 来控制 bounded revision loop。所以它是可审计、可 replay、能限制权限的 multi-agent workflow。

对应代码：

- `agent_forge/multi_agent/types.py`
- `agent_forge/multi_agent/coordinator.py`
- `agent_forge/multi_agent/artifacts.py`

### Q2：你现在是否真的做了并发？为什么仍然不是 swarm？

答：

> 我保留了 deterministic sequential role workflow，同时新增了 live fanout。显式 DAG 中依赖满足、write scope 不冲突的 task 会在独立 worktree 中用 fresh LLM、registry 和真实 AgentLoop 并发执行；声明 overlap 串行，实际越界或 merge failure fail closed。它不是 swarm，因为没有 peer chat、动态扩散、共享可写状态或无界任务生成。

加分点：

> 我把 non-goal 写清楚了：不是 Raft、quorum、blockchain、remote worker queue，也不是 decentralized swarm。并发收益只记录 wall/worker time 和成本，未做 matched serial 重复实验前不声称 speedup。

### Q3：为什么复用 `AgentLoop`？

答：

> 因为 `AgentLoop` 已经包含上下文构建、模型调用、工具路由、安全控制、trace 和 usage。multi-agent 如果复制一套 runtime，会导致 single/multi 行为不可比，也增加维护成本。所以 coordinator 只做外层编排，每个 role 还是调用同一个 AgentLoop，只是传不同 role prompt、tool allowlist 和 `agent_name`。

对应代码：

- `agent_forge/runtime/agent_loop.py`
- `agent_forge/multi_agent/coordinator.py`

### Q4：Artifact handoff 解决什么问题？

答：

> 它解决 multi-agent 状态不可见的问题。如果 agent 之间只靠聊天传递状态，很难 replay、debug 或评估。ArtifactStore 把每个 role 的输出落盘，后续 role 通过 artifact path/context 读取。这样 reviewer 到底审了什么、verifier 到底验证了什么，都能在 run directory 里看到。

对应产物：

- `multi_agent/artifact_index.json`
- `multi_agent/artifacts/*.md`
- `multi_agent/multi_agent_summary.json`

### Q5：怎么避免 reviewer 乱改代码？

答：

> role-level tool allowlist。Implementer 有 patch/write/run_command，Reviewer 是 read-only，Verifier 可以 run focused validation。权限不是只靠 prompt 说“不要改”，而是在 ToolRegistry/ToolRouter 层收窄可用工具。

对应代码：

- `agent_forge/multi_agent/profiles.py`
- tool registry/router 相关代码

### Q6：`NEEDS_REVISION` 怎么处理？

答：

> Reviewer 或 Verifier 输出 `NEEDS_REVISION` 后，coordinator 会把反馈 artifact 注入下一轮 primary role subtask，但 revision 有 `--max-revision-rounds` 上限。这样可以让 agent 自修，但不会无限循环。

对应参数：

```bash
--max-revision-rounds 2
```

### Q7：为什么 compare mode 必须隔离 workspace？

答：

> 因为 single 和 multi 都会修改 repo。如果共用 checkout，第二个 run 会看到第一个 run 的 patch，比较就污染了。compare mode 为同一个 case 创建 single/multi 两个 variant，分别 checkout base_commit，再抽取统一指标。

对应代码：

- `agent_forge/bench/swebench.py::_run_compare_case`

### Q8：`patch_generated` 能不能说明 solved？

答：

> 不能。`patch_generated` 只说明产生了 candidate diff。真正 resolved signal 来自 official SWE-bench evaluation。这个项目刻意在 report 里保持诚实：没有跑官方 harness 时，不声称 resolved-rate。

面试加分：

> 我把 evaluation honesty 放在设计里，是为了避免 toy project 常见的“生成 patch 就算成功”。

### Q9：如果 multi-agent 成本更高，怎么判断值不值？

答：

> 看 comparison report。它比较 patch presence、cost delta、LLM calls、tool calls、failed tool calls、revision rounds、reviewer findings、verifier status。recommendation 是 conservative 的，不会全局宣称 multi 更好。

对应文件：

- `agent_forge/evaluation/metrics.py`
- `agent_forge/evaluation/comparison.py`
- `agent_forge/evaluation/report.py`

### Q10：当前系统最大的限制是什么？

答：

> 第一，官方 SWE-bench eval 依赖 Docker/swebench；第二，reviewer/verifier marker 仍依赖文本协议；第三，fanout 是本地 coordinator，不是分布式 worker service，也不做模型自动拆解；第四，跨 ephemeral worktree 的逐操作手工写审批尚无稳定 operation identity，所以当前 fail-fast；第五，并发还需要 matched serial 多次实验才能量化收益。

---

## 8. 你应该背熟的 90 秒项目介绍

中文版本：

> 我做的是 Agent Forge，一个面向真实工程任务的 Agent harness control plane。核心 AgentLoop 负责上下文、模型、工具、安全、HITL、恢复、trace 和 usage。我在外层做了两种 multi-agent：顺序 MultiAgentCoordinator 用 Implementer、Reviewer、Verifier 和 artifact handoff 控制 bounded revision；LiveFanoutCoordinator 消费显式 DAG，把 scope 不冲突的 task 放进独立 worktree，用真实 AgentLoop 并发执行，再做实际 touched-file 校验、deterministic patch merge、checkpoint recovery 和 isolated finalizer。评测层仍把 candidate patch、local verification 和 official resolved 分开。我不说 multi-agent 一定更强，而是用质量、成本、延迟、冲突和失败证据判断它什么时候值得。

英文面试时不要逐字背稿；直接把上面的中文版本压缩成英文即可。关键术语保留：`SWE-bench-oriented CodingAgent harness`、`runtime control plane`、`AgentLoop`、`MultiAgentCoordinator`、`artifact handoff`、`bounded revision loop`、`single-vs-multi compare mode`。

---

## 9. 7 天学习计划

### Day 1：跑通测试和普通 run

- 跑 `forge doctor`。
- 跑 `tests.test_swebench_compare` 和 `tests.test_evaluation_comparison`。
- 跑一个 read-only `forge run`。
- 看 `trace.json` 和 `usage_report.md`。

目标：知道单 agent run 产物在哪里。

### Day 2：读 `AgentLoop`

读：

- `agent_forge/forge_cli.py`
- `agent_forge/runtime/agent_loop.py`

目标：能画出 single-agent loop。

### Day 3：读 multi-agent 核心

读：

- `agent_forge/multi_agent/types.py`
- `agent_forge/multi_agent/profiles.py`
- `agent_forge/multi_agent/coordinator.py`
- `agent_forge/multi_agent/artifacts.py`

目标：能讲清楚 Implementer/Reviewer/Verifier 怎么交接。

### Day 4：跑 multi-agent 并看 artifacts

跑：

```bash
forge run "fix the failing test in this repository" \
  --agent-mode multi \
  --profile coding_fix \
  --provider deepseek \
  --max-revision-rounds 2
```

看：

- `multi_agent_summary.json`
- `multi_agent_report.md`
- `artifacts/*.md`

目标：能用 artifact 解释一次 run。

### Day 5：读 compare/evaluation

读：

- `agent_forge/bench/swebench.py`
- `agent_forge/evaluation/metrics.py`
- `agent_forge/evaluation/comparison.py`
- `agent_forge/evaluation/report.py`

目标：能讲清楚 single-vs-multi 公平比较。

### Day 6：跑 compare，准备 evidence card

跑：

```bash
forge bench swebench \
  --showcase \
  --agent-mode compare \
  --profile coding_fix \
  --provider deepseek \
  --max-steps 16 \
  --max-revision-rounds 2
```

看：

- `comparison.json`
- `evaluation_report.md`
- single/multi 各自的 `trace.json`

目标：能打开 report 讲项目价值。

### Day 7：练面试 Q&A

用第 7 节的问题练回答。重点练：

- sequential coordinator 和 live fanout 的区别，以及为什么仍不是 swarm；
- 为什么 artifact handoff；
- 为什么 compare 要隔离 workspace；
- 为什么 patch_generated 不等于 solved；
- 当前限制和下一步。

---

## 10. 学代码时不要陷入的坑

1. 不要从所有文件开始看。先跑，再看 artifact，再读核心文件。
2. 不要把 multi-agent 理解成模型能力提升技巧。这里重点是工程控制面。
3. 不要说项目有官方 resolved-rate，除非真的跑了 `--evaluate`。
4. 不要忽略失败 run。失败 taxonomy、trace、usage 才是 agent harness 的价值。
5. 不要为了面试讲太多 provider 细节。重点讲 runtime、tool governance、artifact handoff、evaluation。

---

## 11. 旧文档注意事项

如果你看到旧文档里写 compare mode 尚未完成，属于旧描述。

以最新本地 master commit `8f6685b multi agent compare` 为准。当前代码已经有 `_run_compare_case()`，并且 `tests/test_swebench_compare.py` 覆盖 compare artifact 写出。

后续可以再更新 `评测目录说明与SWE-bench使用入口.md`、`docs/多Agent协作机制与对比评测说明.md`、`docs/evaluation/评测目录说明与SWE-bench使用入口.md`，但学习这份文档时先按最新代码理解。
