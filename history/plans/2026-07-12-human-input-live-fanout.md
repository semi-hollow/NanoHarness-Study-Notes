# Durable Human Input and Live Fanout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace synthetic human clarification with a durable response/resume loop and connect fanout scheduling to real isolated AgentLoop workers with deterministic integration evidence.

**Architecture:** Human questions are persisted by a dedicated store and resolved through `forge respond`; AgentLoop owns WAITING_HUMAN transitions and resume injection. Live fanout consumes a validated JSON DAG, runs each worker in a detached worktree with a fresh LLM client and trace, checks actual writes against declared scopes, merges patches deterministically, and writes resumable evidence.

**Tech Stack:** Python 3.11, dataclasses, JSON, `ThreadPoolExecutor`, git worktrees, existing AgentLoop/TraceRecorder/usage artifacts, unittest.

## Global Constraints

- Keep the project compact: no distributed queue, peer chat, swarm, or new third-party runtime dependency.
- Never run concurrent write workers in one workspace.
- Human input must persist before the run stops; direct `AskHumanTool.execute` must fail closed.
- Fanout conflicts must fail closed; an LLM may summarize conflicts but may not silently merge outside declared scopes.
- Candidate patch, local validation, reviewer PASS, and official resolution remain separate evidence levels.
- Every new public capability needs behavior tests, report-visible evidence, capability-matrix wording, and a runnable learning exercise.

---

### Task 1: Durable Human Input Control Plane

**Files:**
- Create: `agent_forge/runtime/human_input.py`
- Modify: `agent_forge/runtime/task_state.py`
- Modify: `agent_forge/runtime/config.py`
- Modify: `agent_forge/tools/ask_human.py`
- Modify: `agent_forge/runtime/wiring.py`
- Modify: `agent_forge/runtime/agent_loop.py`
- Modify: `agent_forge/forge_cli.py`
- Test: `tests/test_human_input.py`
- Test: `tests/test_public_cli.py`

**Interfaces:**
- Produces: `HumanInputRequest`, `HumanInputStore.request`, `HumanInputStore.respond`, `HumanInputStore.cancel`, `human_response_for_checkpoint`.
- Produces: CLI `forge respond <request_id> --answer <text>` and runtime status `waiting_human`.

- [ ] Write failing store, AgentLoop stop, CLI response, stale/cancel, and resume-injection tests.
- [ ] Run `python -m unittest tests.test_human_input tests.test_public_cli -v` and confirm failures describe missing interfaces.
- [ ] Implement the store and fail-closed `AskHumanTool` schema.
- [ ] Intercept pre-loop clarification and tool-level `ask_human` in AgentLoop, persist request metadata, trace it, and stop with `WAITING_HUMAN`.
- [ ] Implement `forge respond` and append a responded answer to `forge resume` continuation context while preserving a stable human thread id.
- [ ] Run focused tests and `git diff --check`.

### Task 2: Real AgentLoop Fanout Workers

**Files:**
- Modify: `agent_forge/multi_agent/fanout.py`
- Create: `agent_forge/multi_agent/live_fanout.py`
- Modify: `agent_forge/multi_agent/types.py`
- Modify: `agent_forge/multi_agent/__init__.py`
- Test: `tests/test_live_fanout.py`
- Test: `tests/test_subagent_fanout.py`

**Interfaces:**
- Consumes: `SubagentTask`, `AgentLoop`, `ExecutionEnvironment`, registry/LLM factories.
- Produces: `FanoutPlan`, `LiveFanoutCoordinator.run()`, `LiveFanoutSummary`, per-worker artifacts and `integration.patch`.

- [ ] Write failing tests for JSON plan validation, real AgentLoop worker execution, independent worktrees, actual touched-file scope checks, dependency blocking, and deterministic patch merge.
- [ ] Run focused tests and confirm missing live coordinator failures.
- [ ] Implement strict plan parsing and conflict-free ready-batch partitioning.
- [ ] Implement one fresh worktree, registry, LLM client, trace, usage report, patch and manifest per worker.
- [ ] Implement actual scope validation, same-batch overlap checks, `git apply --check`, deterministic merge, and final read-only aggregation.
- [ ] Run focused tests and `git diff --check`.

### Task 3: Fanout CLI and Selective Recovery

**Files:**
- Modify: `agent_forge/forge_cli.py`
- Modify: `agent_forge/runtime/config.py`
- Modify: `agent_forge/multi_agent/live_fanout.py`
- Modify: `agent_forge/ui.py`
- Create: `examples/fanout-plan.sample.json`
- Test: `tests/test_live_fanout.py`
- Test: `tests/test_public_cli.py`

**Interfaces:**
- Produces: `forge run --agent-mode fanout --fanout-plan <json> [--fanout-resume <run-dir>] --max-workers <n>`.
- Produces: resume validation by plan digest/base commit and reapplication of prior merged patches.

- [ ] Write failing CLI and selective-resume tests.
- [ ] Add fanout arguments and route `run_repository_task` through `LiveFanoutCoordinator` with fresh registry/LLM factories.
- [ ] Persist plan digest, base commit, merged task ids and patch paths; resume only incomplete tasks after validation.
- [ ] Add bounded UI command fields without allowing arbitrary plan paths outside the project workspace.
- [ ] Run focused CLI/fanout tests.

### Task 4: Learning, Operations, and Interview Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/CAPABILITY_REALITY_MATRIX.md`
- Modify: `docs/architecture/runtime-capability-guide.md`
- Modify: `docs/architecture/human-input-and-live-fanout.md`
- Create: `docs/guides/learning-path.md`
- Create: `docs/guides/harness-interview-guide.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: actual CLI flags and artifact paths from Tasks 1-3.
- Produces: one start-to-artifact learning path, runnable HITL/fanout exercises, truthful capability boundaries, and evidence-grounded interview questions.

- [ ] Document the runtime relationships and exact commands for human response/resume and fanout.
- [ ] Add interview prompts covering design choices, failure scenarios, trade-offs, metrics, and explicit non-claims.
- [ ] Update capability status: durable clarification and live AgentLoop fanout become Green only when their behavior tests and artifacts exist.
- [ ] Search public files for stale synthetic/fake claims and correct them.

### Task 5: Verification and Publication

**Files:**
- Verify all files changed above.

**Interfaces:**
- Produces: clean master, passing CI, real-provider read-only fanout evidence, and GitHub commit.

- [ ] Run focused human-input, fanout, CLI, coordinator, approval, resume, scorecard, and safety tests.
- [ ] Run `DEEPSEEK_API_KEY= bash scripts/verify.sh` and `git diff --check`.
- [ ] Run a two-worker read-only fanout with the configured real provider and inspect report/trace/usage artifacts.
- [ ] Perform an independent correctness review focused on stale responses, concurrent git operations, scope escape, merge integrity, partial recovery, and overclaiming.
- [ ] Fix all important findings, rerun verification, commit with product language, push master, and verify GitHub Actions.
