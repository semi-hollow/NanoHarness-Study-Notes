# Agent 安全边界讲解

目标：回答“Agent 能读写文件、执行命令，怎么防止它乱来？”

## 1. 一句话

> 模型只提出动作，runtime 决定动作是否允许。所有副作用都必须经过工具路由、参数校验、权限策略、workspace（工作区） sandbox、command policy 和 trace 审计。

## 2. 安全链路

```text
LLM tool call
  -> ToolRouter: 本轮暴露哪些工具
  -> ToolRegistry: 工具是否存在、参数是否符合 schema
  -> HookManager: permission + environment + redaction
  -> WorkspaceSandbox: path 是否在 workspace 内，是否敏感
  -> CommandPolicy: shell 命令是否允许
  -> Tool executes
  -> Observation + Trace

Informational question
  -> HumanInputStore -> WAITING_HUMAN -> forge respond -> resume

Concrete side effect
  -> ApprovalStore + fingerprint -> forge approve -> stale recheck
```

对应代码：

- `agent_forge/tools/tool_router.py`
- `agent_forge/tools/registry.py`
- `agent_forge/runtime/hooks.py`
- `agent_forge/safety/sandbox.py`
- `agent_forge/safety/permission.py`
- `agent_forge/safety/command_policy.py`
- `agent_forge/runtime/agent_loop.py`

## 3. 具体边界

| 风险 | 项目实现 | 面试讲法 |
| --- | --- | --- |
| 读写越界 | `WorkspaceSandbox` resolve path | Agent 不能凭模型输出读 workspace（工作区） 外文件。 |
| 危险命令 | `CommandPolicy` | `rm -rf`、网络命令、外部路径命令被拦截。 |
| 写文件副作用 | `PermissionPolicy` / hooks | 写和 patch 不是裸执行，可要求 approval。 |
| 信息不足仍继续 | `HumanInputStore` + `WAITING_HUMAN` | Agent 必须先持久化问题并停止，不能模拟人类回答。 |
| 批量并发写冲突 | fanout worktree + declared/actual scope gate | 每个 worker 隔离，越界或 overlap 不合并。 |
| 运行环境污染 | worktree / OCI `ExecutionEnvironment` | local path policy、git-state isolation 和进程隔离分层表达。 |
| Reviewer 误改代码 | role read-only + 工具白名单（tool allowlist） | Reviewer 只能审，不允许 patch。 |
| Patch 锚点误替换 | `apply_patch` 要求 old text 唯一匹配 | 多处匹配不做“猜测替换”。 |
| 死循环 | 最大步数（max steps） + repeated tool call（工具调用） | runtime 检测重复动作并停止。 |
| 幻觉“测试通过” | 输出护栏（output guardrail） + evidence | 最终回答（final answer）要基于实际 tool evidence。 |
| secret 泄露 | redaction hook + sensitive path | trace/observation 不应暴露敏感信息。 |

## 4. 为什么不能只靠 prompt？

Prompt 可以写：

```text
不要删除文件，不要读 secrets，不要执行危险命令。
```

但生产系统必须用代码保证：

- 模型可能误解；
- provider 可能输出非标准 tool call（工具调用）；
- prompt injection 可能诱导越权；
- 工具执行有真实副作用；
- 事故后需要审计证据。

所以项目把安全下沉到 runtime，而不是让模型自觉。

## 5. 面试回答模板

> 我把 Agent 安全拆成三层。第一层是路由层，每一轮只暴露任务相关工具。第二层是执行层，ToolRegistry 做 schema 校验，WorkspaceSandbox 和 CommandPolicy 做硬边界。第三层是审计层，TraceRecorder 记录每个 action、permission（权限） decision 和 observation。这样即使模型输出危险或错误动作，runtime 也能拦截、记录并给出可恢复的 failure signal。

## 6. 当前边界

已覆盖：

- 本地 workspace（工作区） sandbox。
- command allow/deny policy。
- permission（权限） hook。
- role-specific 工具白名单（tool allowlist）。
- read-only reviewer。
- patch anchor uniqueness。
- trace/usage audit。
- durable informational HITL 和 stale write approval。
- detached worktree 与 constrained OCI execution evidence。
- fanout worker scope、patch hash、deterministic merge 和 isolated finalizer。

未覆盖到生产级：

- 多租户权限隔离。
- 远程 sandbox service 和 hostile multi-tenant isolation。
- 任意外部 API 的通用幂等/补偿协议。
- 企业级 secret vault。
- 多用户人工审批 UI/服务化工作流。
- 跨 ephemeral fanout worktree 的逐操作手工写审批；当前明确 fail-fast。

## 7. Fanout 安全追问

### 为什么有 worktree 还需要 write scope？

worktree 只隔离 worker 与 integration workspace，不能判断 worker 是否修改了本
任务不拥有的文件。scope 是所有权契约，执行后还要用 actual touched files
复核。

### 为什么不让一个 conflict-resolver agent 自动合并？

它需要同时拥有冲突双方的写权限，会绕过原 scope。当前设计让 declared overlap
串行，undeclared overlap fail closed，由 operator 重新划分 ownership 或创建依赖。

### HumanInput 为什么不等于 Approval？

HumanInput 提供信息；Approval 授权具体动作并绑定 target fingerprint。将两者合并
会让一句普通回答被错误解释为副作用授权。

### 模型同时返回写工具和 `ask_human` 怎么办？

human call 是 control-plane barrier，优先级高于同轮所有其他工具。runtime 只
保留第一个问题，其他调用记为 deferred，不执行。人工回答被注入后，
模型必须按新上下文重新提出副作用，避免“先写后问”。
