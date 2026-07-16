# Clowder AI Agent 面经回答思路：NanoHarness 查漏补缺版

> 参考题目来自 `Clowder_AI_Agent_面经精练版.md`，参考项目为
> [Clowder AI](https://github.com/zts212653/clowder-ai)。本文不是把 NanoHarness 包装成
> Clowder，而是区分：哪些问题可以用项目实现回答，哪些只能讲设计判断，哪些不属于项目范围。

## 使用标记

| 标记 | 含义 | 面试表达 |
| --- | --- | --- |
| A 真实实现 | 已接入主 Runtime，有测试和 trace/usage 证据 | 可以沿调用链讲实现、取舍和 failure case |
| B 有限实现 | 有可运行 primitive，但范围刻意收敛 | 先讲解决的问题，再主动说边界 |
| C 非项目范围 | 企业平台、组织治理或产品运营问题 | 讲设计思路，不暗示 NanoHarness 已实现 |

## 先记住项目定位

### 30 秒版本

NanoHarness 是一个精简的 Agent Runtime Control Plane 与 Evaluation Harness。它不做完整
IDE 或企业协作平台，重点解决模型之外的工程问题：完整请求上下文治理、受约束工具执行、
HITL、checkpoint/resume、副作用幂等、隔离多 Agent、trace/usage、失败分类和 matched eval。

### 与 Clowder 的区别

Clowder 更接近位于 Claude Code、Codex、Gemini CLI 等 Agent CLI 之上的协作平台，强调
持久身份、A2A、共享记忆和 Skill。NanoHarness 研究的是更底层的单次任务执行控制面：
模型怎样看到上下文，工具怎样被限制，失败怎样恢复，候选 patch 怎样被验证，Runtime
改动怎样被证据化比较。

不要把二者说成竞品。更好的说法是：

> Clowder 主要回答“多个长期存在的 Agent 如何协作”，NanoHarness 主要回答“一个或多个
> Agent 在真实工程任务中如何被可靠执行、限制、恢复和评测”。

---

## 一、Memory 与上下文管理

### 1. Memory 为什么分层？【A】

先按“生命周期”和“权威性”拆，不按一个 `memory` 名字全部装进去：

| 层 | NanoHarness 结构 | 作用 |
| --- | --- | --- |
| 当前任务 | `Message(role="user")` | 本次 run 的原始目标 |
| Working Memory | `context.memory.Memory` | 当前 run 的 task、session 摘要和召回视图 |
| 原始会话 | `Message` + `Observation` | 当前 run 的原始模型/工具交互 |
| 压缩状态 | `SessionDigest` | 模型窗口的派生摘要和 continuation 线索 |
| 任务状态 | `TaskCheckpoint` | 当前步骤、状态、停止原因、恢复提示 |
| 长期记忆 | `LongTermMemoryRecord` | 跨 run 的证据化事实、决策、约束和失败模式 |

为什么这样分：会话历史追求完整，checkpoint 追求可恢复，长期记忆追求可验证与可失效。
如果混为一层，就会出现摘要覆盖原始事实、临时聊天污染长期知识、恢复状态被当成项目知识。

关键代码：

```text
agent_forge/context/domain/memory.py
agent_forge/context/memory.py
agent_forge/runtime/domain/task.py
```

### 2. 什么有资格成为长期记忆？【A】

NanoHarness 使用显式生命周期：

```text
candidate -> active -> superseded / retired
          -> rejected
```

- 模型或人提出的内容先是 candidate，不进入上下文。
- `promote` 必须附 evidence；本地文件记录 path 和 SHA-256。
- 同 key 的新 active 记录会 supersede 旧记录。
- TTL 到期、retired、rejected、candidate 均不可召回。
- 原始 trace 和 evidence 是事实源，长期记忆是经过治理的结论，不反过来覆盖原始证据。

设计原因：长期记忆最大的风险不是“没记住”，而是“把错的东西记得太牢”。

关键代码：

```text
LongTermMemoryService.propose
LongTermMemoryService.promote
LongTermMemoryService.retire/reject
JsonLongTermMemoryRepository
```

### 3. 如何隔离，避免记忆污染？【A/B】

当前真实范围：

- namespace：默认使用原始 workspace；benchmark 可使用稳定逻辑 namespace。
- scope：`workspace` 或 `agent_private`。
- agent private 还要求 agent_name 匹配。
- 状态与 TTL 在召回前过滤。
- Runtime 只读召回，不允许模型在运行中自动晋升长期真相。

没有实现 user、organization、tenant 四层隔离，也没有分布式并发写冲突。多 Agent 当前共享
workspace 级 active 记录，但运行中不自动写长期记忆，因此主动消除了最危险的写冲突面。

若追问多 Agent 写冲突的未来设计：使用 key/version、compare-and-swap、evidence merge 和
人工/Verifier 仲裁；冲突记录并存为 candidate，不能 last-write-wins 自动成为 active。

### 4. 长期记忆如何检索？【A，范围有限】

当前使用透明 lexical recall：英文词项、中文单字/双字词项，加上 confidence、importance
排序。只返回 active、未过期且 namespace/scope 可见的记录。

为什么暂时不用全量 embedding：

1. 记忆量小，lexical 结果容易解释和测试。
2. 约束、文件名、错误码、API 名称往往精确词项比向量更稳定。
3. 向量召回不能替代 authority、TTL 和 provenance。
4. 项目重点是 Harness 控制面，不是知识库平台。

未来量大后可做 hybrid：exact filter/BM25 负责实体与错误码，vector 负责语义召回，reranker
结合 scope、freshness、authority。知识图谱只在关系查询确实重要时引入。

### 5. 上下文满了怎样压缩？【A】

主要入口：`ContextWindowManager.prepare`。

预算对象是完整请求：

```text
system context + raw history + tool schemas + reserved output
```

在这之前，Context Builder 已按区段限制 policy、FORGE.md、Skill、长期记忆、文件 preview、
retrieval 和 working memory，避免第一轮静态 system message 本身超限；task 不在 system 和
user message 中重复注入。

接近 soft limit 时，旧历史被转换成结构化 `SessionDigest`。Assistant tool intent 与对应
tool result 是不可拆分事务；摘要保留 user updates、tool transactions、失败、assistant
updates 和 source hash。Raw session/trace 不删除。

Provider 仍报 context overflow 时，AgentLoop 强制做一次更激进压缩；只有估算 token 确实
下降才重试一次。压缩摘要不能替代原始证据，provider usage 才是调用后权威 token 数。

### 6. 一个任务持续多天如何恢复？【A/B】

`TaskCheckpoint` 保存步骤、状态、stop reason、resume hint 和最近 `SessionDigest`；
`forge resume` 创建一个新的 continuation run，并写 `resume_link.json` / `resume_chain.md`。
Operation ledger 防止副作用重复执行，目标 fingerprint 变化时拒绝盲 replay。

边界：不恢复 Python 调用栈、隐藏模型状态或 KV Cache。多天任务若需求发生变化，需要新的
task/Spec 作为事实源，不能只依赖旧摘要。

### 7. 单 Session 多主题如何防串扰？【B】

当前 Coding task 默认单主题，namespace 是 workspace，recall query 是当前 task。项目没有
专门 topic segmentation。若面试官问通用 Agent，应回答：先做 topic boundary 检测，再按
topic/session 分 digest，跨主题只注入显式 shared constraints；不要把整段聊天统一摘要。

---

## 二、Multi-Agent 路由与协作

### 1. 第一个 Agent 如何路由？【B，刻意不做动态路由】

NanoHarness 使用显式选择：single、sequential multi profile、validated fanout DAG。没有让
模型自由决定第一个 Agent，也没有自然语言社交路由。

设计原因：在代码修改任务中，动态角色选择不是当前最大变量；显式 profile 和 DAG 更容易
复现、评测和限制权限。未来若加入 router，应采用规则先过滤能力/权限/成本，再让模型在
候选中打分，低置信度由人决定，并保留 routing evidence。

同样不要声称 Single Agent 有独立 Planner。它是真实的受治理 ReAct loop；显式 task
decomposition 只存在于经过 schema、dependency、scope 和 budget 校验的 `FanoutPlan`。
项目曾有只写 trace 标签、不改变执行的 `SimplePlanner`，已作为装饰性能力删除。自动
model-driven decomposition 是清楚标注的未实现边界。

### 2. Single、主子 Agent、Team、Shared State 怎样区分？【A/B】

- Single：一个 `AgentLoop` 持有会话和工具状态，路径最短、成本最低。
- Sequential roles：Implementer -> Reviewer -> Verifier，共用控制内核但不共享隐藏会话。
- Live fanout：DAG 中独立 worker 并发运行，各自拥有 AgentLoop、LLM、tool view、trace 和
  worktree，最后确定性合并。
- Shared State：NanoHarness 只共享显式 artifact/checkpoint/patch，不实现任意共享黑板。

面试重点：多 Agent 的价值不是“多几次模型调用”，而是增加职责隔离、独立 review 和
verification 控制点。是否值得必须看质量、成本、延迟和失败证据。

### 3. 如何拆分和交接？【A】

Fanout plan 显式声明 task id、dependency、write scope、tool view、expected artifact 和
step budget。Worker 输出 artifact、candidate patch、touched files、trace 和 usage；
Coordinator 校验实际 touched files 是否越过声明 scope，按 DAG batch 合并。

Sequential roles 通过文件 artifact 交接，不把 Implementer 的隐藏上下文直接给 Reviewer。
这样 Reviewer 能看到可审计输入，也减少幻觉被无条件向上传播。

### 4. 如何解决代码冲突？【A】

调度前检查声明 write scope 重叠；worker 在 disposable worktree 执行；返回后再检查实际
touched files；集成阶段确定性 apply patch。冲突或越界不是让另一个 LLM 随意揉合，而是
阻断并生成 conflict evidence。最终 finalizer 在隔离视图中检查 candidate diff，Verifier
不能静默修改 patch。

### 5. 如何终止、防 ping-pong？【A】

NanoHarness 不允许 Agent 间自由对话。控制条件包括：max steps、revision rounds、task
terminal status、tool repeat、consecutive failures、timeout、累计 cost、HITL pause、
permission block 和 fanout DAG completion。工具失败由 `StepController` 生成 recovery decision。

这比单纯最大轮数更可靠：轮数是最后保险，主要终止依据应是状态、进展、副作用和预算。

### 6. 网络中断、额度耗尽、进程退出怎样接管？【A/B】

Single run：checkpoint + resume；副作用由 operation ledger 防重复。Fanout：checkpoint 保存
plan/base identity、accepted worker 和 patch hash，新 workspace 重放已完成 patch，只重跑
未完成 task。

边界：进程被强杀仍可能留下 orphan worktree；没有分布式 lease、worker heartbeat 或远程
队列。若扩展云端 worker，应增加 lease expiry、attempt id、幂等提交和 artifact object store。

---

## 三、Agent Harness 与模型适配

### 1. Harness 的核心职责是什么？【A】

模型负责产生推理结果和 tool intent；Harness 负责：

1. 构造和压缩上下文。
2. 约束模型可见工具。
3. 校验 Tool Schema 和参数。
4. 执行权限、Sandbox 和 command policy。
5. 管理 loop、预算、恢复和 HITL。
6. 收集 trace/usage/artifact。
7. 将 candidate、local validation、official result 分层。

NanoHarness 直接调用模型 API，是因为它本身就在研究 Harness 内核。如果目标是构建更上层
协作产品，可以复用 Claude Code/Codex 等成熟 CLI；如果目标是控制每个 tool transaction、
状态和评测变量，则直接拥有 Runtime 更容易做实验。

### 2. 模型与 Harness 如何解耦？【A】

Application 只依赖 `ModelPort`，`ModelGateway` 负责 provider usage、retry/fallback 和错误
分类，OpenAI-compatible client 负责协议。AgentLoop 只看统一 `AgentResponse`：content、
tool calls、error 和 normalization evidence。

不要说“完全模型无关”：不同模型仍会在 Tool Schema 遵循、reasoning 风格、上下文窗口、
成本和错误格式上不同。解耦的目标是让差异集中到边界，而不是假设差异不存在。

### 3. 弱模型 Tool Calling 不稳定怎样治理？【A】

`ToolCallNormalizer` 只做确定性修复：标准 JSON、Python dict literal、以及工具名属于本轮
可见集合的完整文本调用。无法确认时返回 `invalid_tool_call`，Gateway 使用 repair prompt
有界重试；不会猜未知工具或缺失业务参数。

Context overflow 不在 Gateway 重复同一请求，而由 AgentLoop 压缩后重试。单响应 tool call
过多时在执行前截断。所有 repair、failed invocation 和 burst 都进入 usage。

### 4. 不同模型怎样选？【B】

不要背“某模型一定最好”。按任务维度建立矩阵：correctness、tool success、context length、
latency、cost、retry rate、repair rate、reasoning token 和 official resolved。Thinking level
也应作为实验因子，同 case、同环境做 paired/multi-seed 比较。

项目当前提供统一 Gateway、usage 和 scorecard，但没有完成多 provider 大样本结果。面试时
可以讲评测方法，不能伪造模型排名。

### 5. 权限链有哪些盲点？【A】

真实链路：

```text
Model response
-> ToolRouter visible schema
-> ToolRegistry validation
-> repeat / burst gate
-> permission hook
-> ApprovalStore
-> CommandPolicy
-> WorkspaceSandbox
-> ExecutionEnvironment
-> tool observation / operation ledger
```

模型权限、工具权限、系统权限不能混为一层。ToolRouter 只是减少模型可见面，不能替代
执行时 policy；Sandbox 限制路径，不能替代 command 语义；container 比 local 强，但当前
也不是 hostile multi-tenant security boundary。

凭证管理属于 C：NanoHarness 没有 Vault、短期 token、per-tool credential broker。

---

## 四、Skill、自进化与事故驱动治理

### 1. Skill 如何发现、加载和复用？【A/B】

Skill manifest 包含名称、版本、触发条件、prompt card、tool names 和 entrypoint。Registry
根据 task 和显式配置选择 Skill，影响 context 和 tool visibility，并写 trace。自定义 manifest
内容哈希进入 benchmark，支持 matched Skill on/off 对比。

边界：没有 marketplace、签名安装、remote distribution、依赖解析和自动升级。

### 2. 如何证明十步变五步没有漏？【A，方法已具备，数据仍需跑】

不能只比较 step 数。至少同时比较 official resolved/local validation、tool failures、token、
cost、latency、human intervention 和 failure class。相同 case、模型、环境、Memory snapshot
下，只改变 Skill factor；多 seed 后再谈稳定收益。

### 3. “自进化”应该怎样理解？【B】

不要说 Agent 能自动进化。更准确的闭环是：

```text
failure trace -> taxonomy -> case study -> regression case
-> 选择沉淀位置 -> runtime/Skill/Memory/eval -> matched validation
```

沉淀判断：

- 临时事实：不持久化或只进 checkpoint。
- 有证据的项目事实/决策：Long-term Memory。
- 可复用操作流程：Skill。
- 安全或正确性不变量：代码硬约束、Schema、policy。
- 质量结论：Eval。
- 大量稳定行为模式：才考虑训练数据。

模型不能自动修改并发布自己的 Harness。自修改应生成 candidate patch，经过测试、review、
Verifier 和人工 merge gate。

### 4. 什么是事故驱动护栏？【A】

从具体 failure scenario 提炼不变量，而不是只加 prompt。例如：重复副作用形成 operation
ledger；审批后 target drift 形成 stale fingerprint；candidate patch 被说成 solved 形成 claim
ladder；失败模型调用漏计费形成“每次 chat 都记录 usage”的控制点。

公开记录：`docs/evaluation/failure-driven-improvements.md`。

Prompt 负责偏好，代码负责不可违反的边界，Eval 负责判断改动是否有效；三者不能互相替代。

---

## 五、Eval、Benchmark 与效果验证

### 1. Harness 修改后怎样证明变好？【A】

证据梯度：

```text
candidate patch
< local validation
< role verifier
< official per-case resolved/unresolved
< matched repeated experiment
```

Scorecard 分开计算 patch、local、official denominator，记录 token、cost、latency、tool failure、
compaction、memory recall、repair 和 failure taxonomy。`forge eval ablation` 拒绝未声明的模型、
数据、case、环境和 runtime config 漂移。

### 2. Memory、Skill、Tracing、A2A 分别怎样评测？【A/B】

- Memory：召回 precision/污染率、是否命中正确 scope、对 official outcome 和成本的增量。
  当前支持 frozen snapshot 的 recall on/off；还没有大规模 memory benchmark。
- Skill：manifest 固定后 on/off，比较正确性、步骤、失败、成本。
- Tracing：事件完整性、失败定位率、usage 与 raw trace 一致性，不以 trace 数量为价值。
- Multi-agent：同 case 比 single/multi 的质量、revision、cost、latency、冲突和 verifier evidence。
- A2A：NanoHarness 不实现开放 A2A，只能讲 message delivery、identity、loop prevention、
  idempotency 和 handoff completeness 指标。

### 3. 为什么不只看每日 Eval 曲线？【B】

每日曲线适合稳定任务集和模型版本监控，但必须固定 dataset version、runtime revision、model、
environment image 和 seed，否则曲线漂移不可归因。NanoHarness 当前更适合固定小集合的
failure-driven regression 和 matched experiment；样本少时不应做看似精确的趋势图。

### 4. 如何做真实环境评测？【A】

SWE-bench runner checkout base commit，在 local/worktree/OCI 环境运行真实工具，收集 candidate
patch，并可调用 official harness 解析 per-case outcome。Command policy、network、CPU、memory、
PID、read-only root 和 environment manifest 形成环境证据。

外部服务不可用时使用 deterministic fake 验证错误分支，但不能把 fake 成功当真实效果。

### 5. Agent RL 怎样评估？【C，知识准备】

将真实任务转成可重置环境，定义 observation/action、工具权限、终止条件和奖励。奖励应分层：
最终测试/official result 为主，过程奖励只辅助工具合法性、进展和成本；避免奖励 hack。训练与
评测 case、repo commit 和环境镜像隔离，保留失败轨迹供研究员分析。

### 6. 组织效果怎样评估？【C】

可讲指标框架：lead time、merge rate、返工率、escaped defects、人工检查时间、Agent task
acceptance、单位成功任务成本。知识库大小、调用数和生成代码量都是 vanity metric。

---

## 六、工程环境、Sandbox 与代码交付

### 1. 为什么用 Git Worktree？【A】

每个 worker 需要同一 base commit 的独立文件视图、独立 patch 和可删除生命周期。Worktree
比复制整个仓库轻，仍保留 Git identity 和 diff。Fanout 从 committed `base_head` 创建，
不会静默继承主 checkout 未提交文件。

### 2. Worktree、Sandbox、Container 分别解决什么？【A】

- Worktree：代码状态隔离和并发 patch。
- WorkspaceSandbox：路径必须解析在 workspace 内，阻断 `..` 和 symlink escape。
- CommandPolicy：限制 shell 命令语义和 network-sensitive action。
- OCI mode：进程、网络、资源、capability 和 root filesystem 边界。

它们是互补层，不应把 worktree 说成安全 sandbox，也不把当前 container 说成 hostile
multi-tenant isolation。

### 3. 大仓、多仓、跨语言如何做？【B/C】

当前真实能力是 repository map、lexical file ranking、grep 和有界 preview，适合单仓。
没有 AST/LSIF 级依赖图、多仓索引或 remote execution。未来应按语言接入 symbol/definition/
reference adapter，构建模块图和变更影响集，再把相关子图注入 context；跨仓任务需要统一
workspace manifest 和版本锁定。

### 4. 如何证明修复有效？【A】

生成 diff 只是 reachability。Diagnostics 产生 local validation evidence；official SWE-bench
结果才支持 resolved；Reviewer/Verifier 是 runtime 控制点但不冒充 official evaluator。
Report 用 claim ladder 强制区分这些层级。

### 5. Web、多模态自动验收？【C】

NanoHarness 不做。回答思路：浏览器任务需要 DOM assertion、network log、screenshot/video
artifact 和视觉 diff；多模态还需输入版本、模型版本和可重复 judge。LLM-as-judge 不能单独
作为最终正确性证据。

---

## 七、需求、长流程与人机协作

### 1. 用户需要一次讲完整吗？【A/B】

Run 前 `ClarificationPolicy` 判断缺失信息；需要时创建 durable `HumanInputRequest`，状态转为
`waiting_human`。`forge respond` 保存回答，`forge resume` 在 continuation 中加载。模型
`ask_human` 也会成为同 turn barrier，阻止其他副作用继续。

### 2. 需求变化怎样同步？【B】

当前通过新的 task/continuation 明确覆盖旧目标，checkpoint 提供 provenance。没有完整 SDD
系统。通用回答应强调 Spec 是事实源：需求变更先改 acceptance criteria 和 plan，再实现和
测试；不能只在聊天末尾追加一句而让旧计划继续执行。

### 3. 哪些必须人审批？【A】

- 信息缺失：human input，不代表授权。
- 写入/危险副作用：ApprovalStore，绑定 operation fingerprint。
- Approval 后 target 变化：标 stale，必须重新审批。
- Final merge、发布、敏感凭证和不可逆操作：应保留人 gate。

### 4. 中断后怎样避免重复执行？【A】

Checkpoint 解释进度，OperationRecord 解释副作用是否已执行。Operation key + pre/post
fingerprint 支持 replay skip；目标 drift 时拒绝把旧记录当安全成功。Fanout 用 worker patch
SHA-256 恢复 accepted task。

### 5. CI 失败后自动修复到什么程度？【B】

可以自动定位、生成 candidate、运行受限测试和提交 review artifact；不应在缺少 acceptance、
权限、official validation 或高风险变更时自动 merge。自动化边界应由 risk level 和 evidence
决定，不由“模型很强”决定。

---

## 八、架构定位与产品差异化

### 1. 整体架构为什么这样分层？【A】

项目采用 capability-first modular monolith，并在每个能力内使用 Domain/Application/Port/
Adapter/Presentation：

- Domain 定义稳定数据和规则。
- Application 表达用例顺序。
- Port 表达外部依赖协议。
- Adapter 负责文件、Git、HTTP、process。
- Wiring 是唯一认识具体实现的装配点。
- Public API 给 CLI、Bench、Multi-Agent 连接。

这样做不是为了套 DDD 名词，而是防止 AgentLoop 同时拥有流程、文件 IO、审批、报告和 Git，
让测试能替换外部依赖并用 AST test 阻止依赖反转。

### 2. 最突出的两个设计是什么？【A】

建议回答：

1. **Governed runtime control plane**：context、tool visibility、permission、sandbox、HITL、
   operation ledger、budget 和 recovery 全在 prompt 外执行。
2. **Evidence-driven evaluation loop**：raw trace -> usage projection -> failure taxonomy ->
   scorecard/ablation -> regression，严格区分 candidate、local、verifier 和 official evidence。

Memory、Multi-Agent 都是这两条主线上的能力，不要把项目讲成能力清单。

### 3. 为什么不用强状态机？【B】

Runtime 有显式 `TaskRunStatus` 和 terminal transition，但没有通用 workflow engine。主循环
状态少，Application service + checkpoint 足够；强状态机在角色/业务流程频繁定制时会增加
迁移成本。若未来出现几十种事件、异步 worker 和跨进程恢复，应升级为事件驱动状态机。

### 4. 为什么不直接用 LangChain/现成框架？【A】

不是“框架不好”，而是项目要研究控制面细节：tool transaction 原子性、approval fingerprint、
operation replay、official evidence boundary 和 matched ablation。手握这层可以精确插入策略和
观测。对 retrieval、协议或容器等成熟问题仍应复用库/外部工具，不主张全部自研。

### 5. 项目当前属于什么阶段？【A】

可运行的开源 engineering prototype / compact harness。核心链路真实，测试和本地 Evidence
Console 完整；没有生产多租户、托管服务、用户规模和 SLA。不要说 enterprise-ready。

---

## 九、企业治理与组织规模化

以下均为【C】，不要为了覆盖面经塞进 NanoHarness。

### 平台团队与业务团队怎样分工

平台统一模型网关、identity、权限、sandbox、trace schema、eval、Skill packaging 和基础
运行环境；业务团队拥有领域 Spec、工具 Adapter、知识权限、acceptance case 和 human gate。

### 组织知识是不是 Memory 上一层

是，但需要独立 authority：个人偏好、项目事实、组织规范的 owner、scope、TTL、审批和
冲突策略不同。组织知识不能简单把所有个人 Memory 合并。应保留 provenance、ACL、版本、
freshness 和退役流程。

### 凭证与敏感系统

使用短期凭证、per-tool scope、secret broker、审计日志和网络 egress policy；模型不直接看到
长期 secret。工具执行进程拿到最小权限 token，结果做脱敏。

### 多租户与云端

需要租户级 storage key、network namespace、compute quota、encrypted artifact、lease、
remote execution、data retention 和 deletion policy。NanoHarness 的本地 JSON store 不满足。

### Adoption

从高频、可评测、低风险流程切入；先 shadow mode，再人工 gate，再局部自动化。用 lead time、
返工和缺陷衡量，不用生成代码量。属于组织变革问题，不是多写一个 Agent 类能解决。

---

## 十、用户价值与产品运营

### 项目是否真的有人使用？【必须诚实】

当前主要是个人持续迭代和可复现实验项目，不要虚构用户数量。价值证据来自真实 SWE-bench
case、官方评测接口、failure log、runtime tests 和可审计 artifact；这证明工程完整性，不等于
市场验证。

### 如何描述收益

没有跑出稳定多 seed 数据前，不给百分比。可以说已经具备测量框架，并展示具体一次 run 的
token、cost、tool failure、patch、local/official status。量化结果应由固定 regression set 的
control/treatment 产生后再写简历。

### 本地优先和云端如何平衡【C】

代码、Memory、凭证默认本地；云端只上传最小必要 artifact 和脱敏 telemetry。远端执行需要
用户显式选择数据边界和 retention。NanoHarness 当前是 local-first，不是云产品。

---

## 十一、个人贡献与 Vibe Coding 问题

### “代码是不是主要由 AI 写的？”

不要回避。可以这样回答：

> 我高强度使用 Codex 和 Claude Code 做实现与审查，但我负责问题定义、架构边界、failure
> scenario、验收标准和最终代码 ownership。判断我是否掌握项目，不应看每一行是不是手敲，
> 而应看我能否从入口解释数据流、定位失败、修改控制策略并用测试和 benchmark 证明结果。

然后现场沿一条真实链讲：

```text
AgentLoop.run
-> TurnPreparation.execute
-> ContextWindowManager.prepare
-> ModelGateway.chat
-> ToolExecutionPipeline.execute_calls
-> RunLifecycle.stop
```

再挑一个 failure log 案例解释现象、根因、修复和验证。不要背类名清单。

### “你真正掌握了什么？”

建议聚焦：Agent loop 控制、Context/Memory 权威边界、Tool policy、HITL 与幂等恢复、
Multi-Agent artifact contract、trace/usage、failure taxonomy、SWE-bench evidence 和 paired eval。

---

## 本轮项目查漏补缺后的结论

### 已补到真实 Runtime 的核心缺口

1. 完整请求预算，不再只限制 repository context。
2. 不拆分 Tool Transaction 的结构化会话压缩。
3. Working/session/checkpoint/long-term Memory 分层。
4. Candidate -> evidence-backed active -> supersede/retire 生命周期。
5. Namespace、agent scope、TTL 和中英文透明召回。
6. 弱模型 Tool Calling 的确定性标准化与 repair retry。
7. Context overflow 由 Runtime 压缩后接管，不盲重试。
8. 单响应工具 burst 在执行前治理。
9. 失败模型调用与 retry 成本完整计入 usage 和累计 budget。
10. Memory、Skill、Context、tool burst 的 identity-gated paired ablation。
11. Evidence Console 直接展示 compaction、recall、repair、burst 和 active Skills。

### 现在最缺的不是继续加类，而是真实数据

1. 用固定五个 case 跑 Memory off/on、Skill off/on、Context budget 两档，多 seed。
2. 保存 provider/model、环境镜像、Memory/Skill hash 和 official per-case denominator。
3. 只将重复稳定结果写入 README/CV，失败结果同样保留 taxonomy 与 case study。

### 不应继续塞进项目的内容

- 企业多租户、组织知识平台、Vault、7x24 云调度。
- 社交式 A2A、动态首 Agent 路由、Agent Board。
- Skill marketplace、Agent 自动修改并发布自身 Harness。
- 向量数据库、知识图谱、多仓语义索引，除非出现真实规模需求。
- 图片/视频长任务体验、组织 Adoption、产品运营。

这些问题要懂，但实现它们会让 NanoHarness 从“精简 Harness”变成“功能很宽、证据很薄”。

## 面试时的统一回答模板

遇到任意项目问题，按五步回答：

1. **问题**：先说真实 failure scenario。
2. **边界**：说明 Runtime 哪一层应该负责，哪一层不负责。
3. **设计**：讲数据结构、状态和关键入口。
4. **取舍**：为什么没用更复杂方案，当前不能声称什么。
5. **证据**：测试、trace、usage、artifact、official eval 或 paired comparison。

这个模板比罗列 “Memory、MCP、Multi-Agent、Skill 都做了” 更像 3 年以上 Agent Harness
工程师的回答。
