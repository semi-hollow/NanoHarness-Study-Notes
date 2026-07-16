# AI Agent 面试 Q&A 防守版

这份文档只服务一个目标：你在 3 年+ AI Agent 工程面试里，能把 Agent Forge 讲清楚，并且被追问时不慌。

阅读方式：

- 面试前 30 分钟：只看每题的“核心回答”。
- 面试前 2 小时：再看“项目映射”和“避坑”。
- 面试官深挖：打开对应代码或 artifact（产物）。

## 1. AgentLoop 的职责是什么？

核心回答：

> AgentLoop 是 运行时控制平面（runtime control plane）。模型负责提出动作，runtime 负责上下文构建、LLM 调用、工具路由、权限检查、工具执行、observation 回填、trace/usage 记录和停止条件。

项目映射：

- `agent_forge/runtime/agent_loop.py`
- `agent_forge/runtime/control.py`
- `agent_forge/observability/trace.py`
- UI: `Show Trace Timeline`

避坑：

- 不要说 AgentLoop 只是 简单 while 循环。
- 要强调停止条件不能靠模型自觉，必须由 runtime 兜底。

## 2. 为什么复杂 Agent 要把复杂度从 prompt 转移到 runtime？

核心回答：

> Prompt 是软约束，runtime 是硬边界。安全、预算、权限、审计、回放、幂等、超时、失败恢复这些不能靠一句“不要做危险事”。

项目映射：

- `WorkspaceSandbox`
- `CommandPolicy`
- `PermissionPolicy`
- `HookManager`
- `TraceRecorder`

避坑：

- 不要贬低 prompt。正确说法是：prompt 定义任务策略，runtime 执行治理边界。

## 3. 什么任务做 Chatbot、Workflow、Agent？

核心回答：

> Chatbot 适合低风险问答；Workflow 适合路径确定、规则明确的业务链路；Agent 适合目标明确但路径不确定、需要探索、工具调用和多步恢复的任务。

项目映射：

- SWE-bench code fix 需要读 repo、定位文件、改 patch、验证，所以是 Agent。
- `MultiAgentCoordinator` 是 工作流层（workflow layer） 包住多个 按角色配置的 AgentLoop（role-specific AgentLoop）。

避坑：

- 不要所有东西都说 Agent。能 workflow 固化的，就不要让模型自由探索。

## 4. 为什么要 Multi-Agent，单 Agent + Skills 不够吗？

核心回答：

> 单 Agent + Skills 是默认方案，成本低、上下文简单。Multi-agent 只有在需要角色隔离、独立审稿、验证和责任边界时才值得。

项目映射：

- `agent_forge/multi_agent/coordinator.py`
- `RoleSpec`
- `ArtifactStore`
- `coding_fix` profile

加分点：

- Agent Forge 不做 swarm（群体式协作），而是 由 Coordinator 驱动（coordinator-driven）。这样通信成本低、状态可复现、审计清楚。

## 5. 为什么 agents 不自由聊天，而是 artifact（产物） handoff（显式产物交接）？

核心回答：

> 自由聊天状态隐藏、难审计、难复现，也容易上下文污染。Artifact handoff（显式产物交接） 把每个角色输出落盘，Reviewer/Verifier 只基于明确候选产物做判断。

项目映射：

- `.agent_forge/runs/<run-id>/multi_agent/artifacts/`
- `multi_agent_summary.json`
- `multi_agent_report.md`
- UI: `Artifact Handoff Graph`

避坑：

- 不要把 multi-agent 描述成“多个模型互相讨论”。本项目强调显式 artifact（产物） 边界。

## 6. Reviewer 和 Verifier 为什么不能直接把结果给用户？

核心回答：

> 子角色输出是中间证据，不是最终答案。Coordinator 要合并角色结论、处理 修订预算（revision budget）、判断 PASS / NEEDS_REVISION / BLOCKED，再生成最终 summary。

项目映射：

- `MultiAgentCoordinator`
- `RoleRunResult`
- `MultiAgentRunSummary`

加分点：

- 子 Agent 幻觉不能直接透传给用户，必须经过上层 coordinator 汇总和验证。

## 7. Revision loop（修订循环） 如何避免无限循环？

核心回答：

> Reviewer/Verifier 可以触发 NEEDS_REVISION，但修订轮次（revision round）有上限；BLOCKED 会停止；runtime 还有最大步数（max steps）、timeout 和 budget 兜底。

项目映射：

- `--max-revision-rounds`
- `RuntimeConfig.max_steps`
- `evaluation_report.md`

避坑：

- 不要说“让模型自己判断什么时候停”。停止条件必须 runtime 化。

## 8. compare mode（对比模式） 为什么必须隔离 workspace（工作区）？

核心回答：

> single 和 multi 都会修改 repo。如果共用 workspace（工作区），第二个 run 会看到第一个 run 的 patch，结果被污染。

项目映射：

- `agent_forge/bench/swebench.py`
- `SwebenchWorkspaceManager.prepare(..., variant="single|multi")`
- `comparison.json`
- `evaluation_report.md`

## 9. 如何证明不是 玩具项目（toy project）？

核心回答：

> 我不用自己编的 calculator/webhook 用例证明效果，而是接 SWE-bench 风格的真实 repo issue。结果不只看最终回答（final answer），还保留 patch、trace、usage、失败分类（failure taxonomy）和对比报告（comparison report）。

证据：

- `forge bench swebench --showcase --agent-mode compare`
- `predictions.jsonl`
- `evaluation_report.md`
- `usage_report.md`
- UI: `Show Interview Evidence`

边界：

- `patch_generated` 只是 候选 patch（candidate patch）。
- 官方 resolved rate 必须跑 SWE-bench Docker harness。

## 10. patch_generated 和 官方 resolved rate 有什么区别？

核心回答：

> patch_generated 只说明 agent 产出了非空 diff；官方 resolved rate 需要官方 SWE-bench harness 在目标 repo 上跑测试并判定通过。

项目映射：

- `predictions.jsonl`
- `patch.diff`
- `official_eval_status`
- `docs/evaluation/评测目录说明与SWE-bench使用入口.md`

避坑：

- 不能把 候选 patch（candidate patch） 说成 solved。

## 11. 工具调用失败怎么处理？

核心回答：

> 先分类，再恢复。unknown tool、invalid args、permission denied、patch mismatch、command failed、repeated action 对应的恢复策略不同。

项目映射：

- `agent_forge/runtime/control.py`
- `agent_forge/tools/registry.py`
- `agent_forge/tools/apply_patch.py`
- `agent_forge/bench/diagnostics.py`

证据：

- `trace.json` 的 `tool_call` / `tool_observation`
- `usage.json` 的 `failed_tool_calls`

## 12. 如何防止 Agent 越权或高风险操作？

核心回答：

> 模型不能直接执行动作。所有动作都必须经过 ToolRouter、ToolRegistry、PermissionPolicy、WorkspaceSandbox、CommandPolicy 和 hooks。

项目映射：

- `agent_forge/safety/sandbox.py`
- `agent_forge/safety/permission.py`
- `agent_forge/safety/command_policy.py`
- `agent_forge/runtime/hooks.py`
- `docs/technical-defense/defense/Agent安全边界与权限防守说明.md`

例子：

- Reviewer 是 read-only role。
- `apply_patch` 要求 old text 唯一匹配。
- dangerous/network/delete command 会被 command policy 拦截。

## 13. System prompt 和 runtime 护栏（guardrail） 的边界？

核心回答：

> System prompt 管行为偏好和任务策略；runtime 护栏（guardrail） 管硬约束。凡是涉及安全、权限、预算、审计和外部副作用，都必须在 runtime。

项目映射：

- prompt/context: `agent_forge/context/context_builder.py`
- hard boundary: `hooks.py`, `permission.py`, `sandbox.py`, `command_policy.py`

## 14. tool 是怎么表示给模型的？

核心回答：

> tool 通过 schema 暴露给模型，模型只产生结构化 tool call（工具调用）。runtime 再校验工具名、参数、权限和执行结果。

项目映射：

- `agent_forge/tools/base.py`
- `ToolRegistry`
- `ToolRouter`

避坑：

- 不要说模型“直接调用函数”。模型只是输出调用意图，真正执行在 runtime。

## 15. 工具很多时如何让模型选对？

核心回答：

> 不应该把所有工具无脑塞给模型。要按 task、role、skill、permission（权限） 过滤工具，并让 tool schema（工具协议） 清晰、参数少、失败可恢复。

项目映射：

- role-level 工具白名单（tool allowlist）
- `skills`
- `ToolRouter`

加分点：

- 工具路由既是效果问题，也是安全和成本问题。

## 16. apply_patch 为什么要求 old text 唯一匹配？

核心回答：

> patch 是有副作用的写操作。如果 old text 不存在或出现多次，直接替换会造成误改。必须返回 recoverable observation，让 agent 重新读文件并选择唯一 anchor。

项目映射：

- `agent_forge/tools/apply_patch.py`

面试关键词：

- precondition
- ambiguity
- idempotency
- recoverable failure

## 17. token/cost/latency 怎么量化？

核心回答：

> trace 是事实来源（source of truth），usage report 是读取视图（read model）。每次 LLM call、context chars、tool calls、failed tools、latency、estimated cost 都从 trace/usage 派生。

项目映射：

- `agent_forge/observability/usage_report.py`
- UI: `Show Usage Dashboard`
- `usage.json`

## 18. 为什么 Agent 评测 不能只看最终成功率？

核心回答：

> 最终成功率只能告诉你结果，不能告诉你怎么改。Agent 还要看 执行轨迹（trajectory）、工具失败（tool failure）、cost、latency、上下文命中（context hit）、修订轮次（revision rounds）、安全拦截（safety block） 和 失败分类（failure taxonomy）。

项目映射：

- `evaluation_report.md`
- `Failure Lens`
- `comparison.json`

## 19. Failure Taxonomy 怎么设计？

核心回答：

> 失败要归因到正确层：provider/config、context retrieval、model output format、tool/runtime、permission/sandbox、patch application、validation、official eval、multi-agent decision。

项目映射：

- `docs/technical-defense/defense/失败分类体系与排查话术.md`
- `agent_forge/bench/diagnostics.py`
- `evaluation_report.md`

避坑：

- 不要所有失败都说“模型能力不够”。这不是工程回答。

## 20. 长链路任务为什么可以接受几分钟甚至十几分钟？

核心回答：

> Coding fix / DeepResearch 这类任务本来就是高价值长链路，用户关注的是质量和可恢复性，不是每轮秒回。系统要展示进度、保留状态、支持 replay 和失败恢复。

项目映射：

- `.agent_forge/runs/<run-id>/`
- trace / usage / report

## 21. AgentLoop 什么时候停止？

核心回答：

> 模型可以表达最终回答（final answer），但真正停止由 runtime 判定：final answer、最大步数（max steps）、timeout、budget、permission block、repeated action、blocked 状态。

项目映射：

- `RuntimeConfig`
- `StepController`
- `TraceRecorder.stop_reason`

## 22. 如何处理上下文过长？

核心回答：

> 先保留 attention sink（注意力锚点） / system instruction（系统指令） / 当前任务（current task），再按相关性选择文件、历史、memory 和 检索到的文档（retrieved docs）。超限时压缩或丢弃低价值上下文，而不是简单截断前文。

项目映射：

- `agent_forge/context/context_builder.py`
- `agent_forge/context/context_strategy.py`
- `agent_forge/context/token_budget.py`
- `usage.json` 的 context breakdown

## 23. 记忆和上下文有什么区别？

核心回答：

> 上下文是本轮放进模型窗口的信息；记忆是跨轮或跨任务保留的信息。记忆不应该自动全量进入上下文，而要按任务相关性和优先级加载。

项目映射：

- `agent_forge/context/memory.py`
- `ContextBuilder`

## 24. 用户中途改需求怎么办？

核心回答：

> runtime 要把新用户意图作为当前任务约束，旧 plan 不能盲目继续。需要重新组装 context、标记过时子任务，必要时中止未执行的高风险动作。

项目映射：

- session/任务状态（task state）
- trace event
- 最终回答（final answer） / blocked 状态

## 25. 如何避免重复执行非幂等操作？

核心回答：

> 对有副作用的工具要有权限层、dry-run/approval、执行记录和幂等 key。对于 patch/write，至少要有 precondition，防止重复替换或误写。

项目映射：

- `PermissionPolicy`
- `ApplyPatchTool`
- `TraceRecorder`

## 26. 为什么需要 observability？

核心回答：

> Agent 失败通常不是单点 bug，而是 context、LLM、tool、policy、环境共同作用。没有 trace/usage，就无法归因、复盘、计费和做 badcase 回流。

项目映射：

- `trace.json`
- `usage.json`
- `usage_report.md`
- UI evidence cards

## 27. 如何做 badcase 回流？

核心回答：

> 每次失败先归因，再把可复现输入、trace excerpt、expected behavior、failure class 写成 regression case。不能只把失败 prompt 丢回去重试。

项目映射：

- `failure_taxonomy`
- `regression-set core`
- `evaluation_report.md`

## 28. 为什么要 direct baseline（直接基线）？

核心回答：

> direct baseline（直接基线） 回答“为什么不直接问模型一次”。它是无工具、无 仓库检查（repo inspection） 的对照组；AgentLoop 代价更高，但能读文件、调用工具、恢复失败、产出可审计轨迹。

项目映射：

- `--direct-baseline`
- `direct_baseline_predictions.jsonl`

## 29. Multi-agent 的成本如何控制？

核心回答：

> 控制角色数量、每个 role 的 最大步数（max steps）、工具白名单（tool allowlist）、修订轮次（revision rounds），并让 Reviewer/Verifier 尽量基于 artifact（产物），而不是重新全仓库探索。

项目映射：

- `RoleSpec.max_steps`
- `--max-revision-rounds`
- 只基于 artifact（产物） 的修订（artifact（产物）-only revision）

## 30. 多 Agent 如何避免互相抢状态或重复执行？

核心回答：

> 本项目不让 agent 直接共享可写状态。Coordinator 串行调度，角色通过 artifact（产物） 交接；真正写 repo 的角色受 工具白名单（tool allowlist） 和 workspace（工作区） sandbox 控制。

项目映射：

- `ArtifactStore`
- `RoleSpec.allowed_tools`
- `WorkspaceSandbox`

## 31. 如果模型输出非法 JSON / tool call（工具调用） 怎么办？

核心回答：

> 解析失败不应该崩溃或盲目执行，要变成 observation，让模型修复；多次失败后 runtime 按 repeated failure / 最大步数（max steps） 截停。

项目映射：

- tool parser
- `StepController`
- `trace.json`

## 32. 如何看待 MCP / Skills / Tools 的区别？

核心回答：

> Tool 是一次可调用能力；Skill 是一组操作规程、工具权限和上下文策略；MCP 是外部工具发现和调用协议。工程上要把三者接到同一个 registry/router/policy 边界。

项目映射：

- `agent_forge/skills`
- `agent_forge/mcp`
- `ToolRegistry`

## 33. 已经有 live fanout，为什么仍不做 swarm / quorum / Raft？

核心回答：

> Live fanout 解决的是显式 DAG 中独立任务的本地并发，不是分布式共识。每个 worker 有独立 worktree、LLM 和 AgentLoop，scope 冲突由 coordinator 决定。Swarm/quorum/Raft 解决的是 peer communication、投票或容错复制，不是当前最主要的上下文、工具、安全和评测问题。

避坑：

- 不要为了“高级”堆不相关系统设计。

## 34. 如何控制模型调用成本？

核心回答：

> 从四层控制：减少无效上下文、限制 tool 暴露、设置 最大步数（max steps）/修订预算（revision budget）、用 usage report 找高成本步骤。

项目映射：

- `max_context_chars`
- `max_steps`
- `usage.json`
- UI: `Usage Dashboard`

## 35. 模型效果提升但成本上升，怎么判断是否值得？

核心回答：

> 要看任务价值和指标 取舍（tradeoff）：resolved rate / patch 质量 / Reviewer 通过率 是否显著提升，成本、延迟、失败率是否可接受。不能只看单次成功。

项目映射：

- `comparison.json`
- `evaluation_report.md`
- regression set

## 36. 面试官问“你最突出的两个设计”怎么答？

核心回答：

> 第一是 runtime control plane：把工具、安全、HITL、恢复、预算和 trace 从 prompt 移到代码。第二是 evidence-based orchestration：顺序 role workflow 用 artifact handoff，live fanout 用 DAG、worktree、scope gate、hash-verified merge 和 checkpoint recovery，而不是自由聊天。

证据：

- UI: `Show Interview Evidence`
- `agent_forge/runtime/agent_loop.py`
- `agent_forge/multi_agent/coordinator.py`

## 37. 这个项目离生产系统还差什么？

核心回答：

> 当前是本地 harness，不是 SaaS。生产化还需要 remote queue/worker、hostile multi-tenant sandbox、数据库状态与 CAS、多用户审批服务、artifact object store、灰度与监控、更多重复 benchmark。fanout 还缺跨 ephemeral worktree 的稳定 write-approval identity 和 orphan worktree 自动回收。

加分表达：

> 我没有把这些强行塞进 repo，因为目标是清楚展示 CodingAgent runtime 的核心闭环，而不是做一个臃肿平台。

## 38. 如果现场 API / Docker 不可用怎么办？

核心回答：

> 不现场假跑。直接打开已生成 artifacts（产物）和 demo evidence：trace 表示执行链路，usage 表示成本，comparison 表示 single/multi 对比，failure taxonomy 表示失败归因。

项目映射：

- `docs/technical-defense/demo/evidence/评测目录说明与SWE-bench使用入口.md`
- `.agent_forge/runs/...`
- UI: `Show Interview Evidence`

## 39. 如何用一句话收尾？

核心回答：

> Agent Forge 的目标不是做一个聊天壳子，而是把 CodingAgent 真正落地时最核心的 runtime、工具治理（tool governance）、multi-agent review、observability 和 benchmark evaluation 做成可复现的 harness。

## 40. 你的 multi-agent 现在是否真的并发？

核心回答：

> 两条路径要分开。`MultiAgentCoordinator` 是顺序 Implementer/Reviewer/Verifier，
> 适合有反馈依赖的 review loop；`LiveFanoutCoordinator` 对显式 DAG 中 scope
> 不冲突的 task 创建独立 worktree、fresh ModelGateway/registry 和真实 AgentLoop
> 并发执行。它不是共享一个模型对象的线程包装。

证据：

- `agent_forge/multi_agent/live_fanout.py`
- `test_real_agentloop_workers_use_isolated_worktrees_and_merge_disjoint_patches`
- 每个 `workers/<id>/trace.json` 和 `execution_environment.json`

## 41. 多个 worker 发生冲突怎么办？

核心回答：

> declared scope overlap 在调度前串行化；worker 完成后再检查 actual touched
> files。scope escape、同 batch 未声明 overlap 或 `git apply --check` 失败都会
> 停在 `conflict_resolution_required`。当前不让一个模型自动扩权合并，而是要求
> operator 重新划 ownership 或增加 depends_on。

## 42. Partial execution recovery 做到什么程度？

核心回答：

> 普通 run 用 TaskState checkpoint、resume chain 和 OperationLedger 防重复副作用。
> fanout 每批原子写 checkpoint，记录 plan digest、base commit、accepted task 和
> patch SHA；新 run 在 fresh workspace 校验重放，只重跑 incomplete worker。
> 正在执行的 batch 可能重跑，隐藏模型状态和 KV cache 不恢复。

## 43. `ask_human` 还是模拟工具吗？

核心回答：

> 不是。工具本身 direct execute 会 fail closed，AgentLoop 拦截 control signal，
> HumanInputStore 原子持久化 request，run 转 waiting_human。`forge respond` 后，
> resume 才把回答注入上下文。cancelled 是 terminal，choices 变化产生新 request。

## 44. 为什么 HumanInput 和 Approval 不能合并？

核心回答：

> HumanInput 是信息，Approval 是授权。授权必须绑定 operation arguments 和 target
> fingerprint，并处理 stale target；普通回答没有这些权限语义。合并成一个
> approved bool 会把“选择 API 版本”误解释成“允许写文件”。

## 45. 为什么 fanout 不支持逐操作手工写审批？

核心回答：

> 当前 operation identity 包含 ephemeral worktree。跨 run 直接复用 approval，
> 可能把旧中间状态的批准套到重新生成的新 patch 上。因此 write fanout 遇到
> `--no-auto-approve-writes` 明确 fail-fast；需要该边界时使用 single/sequential。
> 下一步是版本化、workspace-independent operation identity，而不是共享目录。

## 46. 为什么要单独实现 `git_workspace.py`？

核心回答：

> 普通 `git diff` 看不到 untracked new files，导致 worker scope、下游基线、
> SWE-bench prediction 和 UI 可能给出不同事实。共享 collector 统一 tracked 与
> untracked text/binary patch，同时只排除未跟踪的 runtime-owned `.agent_forge`。

## 47. 本轮最值得讲的真实 bug 是什么？

建议选一个：

> 我会讲 untracked patch 丢失。表面是 fanout `no_patch`，根因却是全系统对
> candidate patch 的定义不一致。我先写新文件/binary patch 在 clean clone 上
> 可应用的回归，再抽出共享 Git evidence layer，接到 run、benchmark、tool、
> sequential coordinator 和 fanout。随后又发现默认 `.agent_forge` 产物会让
> clean gate 自污染，所以只排除未跟踪的 runtime root，不隐藏 tracked change。
> 这个案例比“调了 prompt”更能体现 harness 工程判断。

## 48. 模型一次返回 `write_file` 和 `ask_human` 时怎么保证不先写？

核心回答：

> `ask_human` 不是普通工具，而是同一 assistant turn 的 control-plane
> barrier。AgentLoop 只处理第一个 human call，其他工具记为 deferred 且不执行；
> 回答注入后模型必须重新提出副作用。我还在落盘前验证 question/choices，
> 避免特殊拦截绕过 ToolRegistry 契约。

证据：`test_human_control_signal_defers_same_turn_side_effects`。

## 49. Finalizer 既要看 candidate diff，又不能修改 candidate，怎么做？

核心回答：

> 我在 disposable worktree 中应用 integration patch 但不提交，因此治理后的
> `git_diff` 能看到真实 candidate。finalizer 运行前保存完整 binary patch snapshot，
> 运行后重新采集；只要不一致就降为 BLOCKED 并丢弃 worktree。这比
> “先提交成 baseline”更好，后者会把 verifier 要看的 diff 一起消掉。

## 50. Fanout worker 为什么看不到主工作区的未提交文件？

核心回答：

> worker 消费记录在 manifest/checkpoint 中的 committed `base_head`，Git worktree
> 不会隐式复制另一 checkout 的 dirty state。这是 snapshot provenance 边界，不是
> 丢文件。write fanout 对 dirty integration fail closed；未来若要支持 draft，我会把
> dirty diff 做成显式、可 hash 的 seed artifact，而不是复制环境偶然状态。

## 51. Resume 之后怎样避免成本和并发指标失真？

核心回答：

> 恢复后 denominator 已经变了。原名 metrics 只记本次 worker + finalizer，
> `resumed_*` 记复用的历史用量，`evidence_chain_*` 记完整证据链。
> `worker_time_to_wall_ratio` 只用本次真正执行的 worker；没有 matched serial
> baseline 和重复样本时，我仍不把该 ratio 叫 speedup。
