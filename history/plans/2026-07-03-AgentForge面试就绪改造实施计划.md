# Interview-Ready Agent Forge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Agent Forge into an interview-ready AI Agent project with trustworthy single-vs-multi comparisons, strong visual evidence, concise code, and high-density learning material.

**Architecture:** Keep `AgentLoop` as the canonical runtime. Keep `MultiAgentCoordinator` deterministic/sequential for reproducibility, then document and visualize how the same artifact/coordinator contract evolves to real parallel agents in production. Build extraction/reporting around existing `trace.json`, `usage.json`, `multi_agent_summary.json`, and SWE-bench result artifacts instead of duplicating runtime logic.

**Tech Stack:** Python 3.11 standard library, existing Agent Forge runtime, `unittest`, Markdown/Mermaid reports, and dependency-free static HTML/CSS/JS dashboards.

## Global Constraints

- Do not implement Claude / Anthropic provider compatibility.
- Do not implement Raft, Swarm, blockchain, quorum, P2P, or distributed consensus.
- Do not delete unrelated user files, including `Modified_resume_Eng.pdf`.
- Do not commit unless explicitly asked.
- Keep implementation concise and DRY.
- Optimize for interview value, learning speed, explainability, and non-toy engineering signals.
- Official SWE-bench evaluation must be honest: missing Docker/SWE-bench means skipped/unavailable, never pass.
- Multi-agent concurrency claims must be truthful: current runtime is deterministic sequential; docs may explain real parallel deployment evolution.

---

## File Structure

### Modify

- `agent_forge/bench/swebench.py` — implement `single|multi|compare`, isolated workspace variants, comparison artifact writing, and honest eval skipped status.
- `agent_forge/bench/types.py` — add optional comparison paths and multi-agent status metadata if needed.
- `agent_forge/bench/report.py` — link comparison dashboard/report in benchmark card.
- `agent_forge/evaluation/types.py` — add compact metric/value objects if needed.
- `agent_forge/evaluation/comparison.py` — extract real metrics from nested usage/trace/multi-agent summaries; fix recommendation logic.
- `agent_forge/evaluation/report.py` — render Markdown plus static visual HTML dashboard.
- `agent_forge/multi_agent/coordinator.py` — preserve coordinator status for benchmark classification, avoid trace grouping collisions, advertise only actual registered tools, and avoid false pass for coding profile with no diff signal.
- `agent_forge/multi_agent/profiles.py` — remove side-effecting diagnostics from read-only reviewer allowlist; tune research criteria; centralize profile registry.
- `agent_forge/tools/apply_patch.py` — detect overlapping anchor ambiguity.
- `agent_forge/forge_cli.py` — fix TUI namespace drift.
- `评测目录说明与SWE-bench使用入口.md`, `docs/多Agent协作机制与对比评测说明.md`, `docs/evaluation/评测目录说明与SWE-bench使用入口.md` — update usage and interpretation.
- `.agent_forge/codex_handoff.md` — final handoff.

### Create

- `tests/test_swebench_compare.py` — compare mode with isolated local workspaces and skipped official eval behavior.
- `tests/test_evaluation_extraction.py` — metric extraction from real artifact shapes.
- `tests/test_interview_visual_reports.py` — static dashboard/report smoke tests.
- `docs/interview/agent-forge-defense-zh.md` — high-density interview defense notes.
- Optional: `docs/interview/multi-agent-concurrency-evolution-zh.md` — truthful sequential-to-parallel deployment story.

---

## Task 1: Correctness fixes before feature work

**Files:**
- Modify: `agent_forge/tools/apply_patch.py`
- Modify: `agent_forge/multi_agent/profiles.py`
- Modify: `agent_forge/multi_agent/coordinator.py`
- Modify: `agent_forge/forge_cli.py`
- Test: `tests/test_write_apply_patch_tools.py`
- Test: `tests/test_multi_agent_coordinator.py`

**Interfaces:**
- Produces: safer `ApplyPatchTool.execute()`; reviewer tools without side-effecting diagnostics; role display tools based on actual registered tools; unique trace agent names per round; TUI args with new defaults.

- [ ] Add a failing test for overlapping `apply_patch` anchors: file content `aaa`, old `aa` must return ambiguous and leave file unchanged.
- [ ] Implement overlapping occurrence detection with a helper that finds more than one start offset, including overlaps.
- [ ] Add/adjust coordinator tests so reviewer role does not expose `diagnostics`.
- [ ] Change `CODING_READ_TOOLS` or reviewer role tools so read-only reviewer cannot run diagnostics/commands.
- [ ] Add test for actual-vs-profile tool prompt: if registry lacks `forge.web_search`, role prompt must not claim it is available as an executable tool.
- [ ] Implement `_available_tools_for_role()` and use it for both registry and prompt text.
- [ ] Add test for revision round trace separation.
- [ ] Run roles with trace agent names like `Implementer[r0]`, `Reviewer[r0]`, `Implementer[r1]` while keeping artifact role names stable.
- [ ] Fix TUI SWE-bench Namespace to include `agent_mode='single'`, `profile='coding_fix'`, `max_revision_rounds=2`.
- [ ] Run focused tests:
  `source .venv/bin/activate && python -m unittest tests.test_write_apply_patch_tools tests.test_multi_agent_coordinator -v`

---

## Task 2: Evaluation metric extraction foundation

**Files:**
- Modify: `agent_forge/evaluation/types.py`
- Modify: `agent_forge/evaluation/comparison.py`
- Modify: `agent_forge/evaluation/report.py`
- Test: `tests/test_evaluation_extraction.py`

**Interfaces:**
- Produces: `extract_run_metrics(...)` or equivalent helper that accepts result/usage/trace/multi-agent dictionaries and returns a flat metric dict compatible with `compare_runs()`.

- [ ] Write tests using realistic `usage.json` shape: metrics under `usage['summary']`.
- [ ] Write tests for `multi_agent_summary.json`: revision rounds, reviewer decisions, verifier status, needs_revision/blocked/passed.
- [ ] Fix `compare_runs()` so it reads nested usage summary and does not report zero metrics for real usage artifacts.
- [ ] Fix `_recommend()` so multi-agent is recommended only when multi produced a quality signal that single did not: patch generated, official eval better, fewer blocking failures, or reviewer/verifier caught and resolved a defect.
- [ ] Add failure taxonomy extraction from `failure_class`, `stop_reason`, and multi-agent status.
- [ ] Run focused tests:
  `source .venv/bin/activate && python -m unittest tests.test_evaluation_comparison tests.test_evaluation_extraction -v`

---

## Task 3: SWE-bench compare mode with isolated workspaces

**Files:**
- Modify: `agent_forge/bench/swebench.py`
- Modify: `agent_forge/bench/types.py`
- Modify: `agent_forge/bench/report.py`
- Modify: `agent_forge/evaluation/report.py`
- Test: `tests/test_swebench_compare.py`

**Interfaces:**
- Consumes: metric extraction from Task 2.
- Produces: `comparison.json`, `evaluation_report.md`, and visual dashboard under the benchmark output directory.

- [ ] Add test with a local git repo case showing compare creates separate `single` and `multi` workspaces.
- [ ] Extend `SwebenchWorkspaceManager.prepare(case, variant='')` so variant suffix changes workspace path.
- [ ] Implement compare flow: for each case run `_run_case(..., agent_mode='single', variant='single')` and `_run_case(..., agent_mode='multi', variant='multi')`.
- [ ] Write separate predictions files for single and multi or clearly label combined predictions; keep official eval honest.
- [ ] Generate comparison artifacts using evaluation helpers.
- [ ] Ensure multi-agent coordinator status influences `BenchCaseResult.status`: `needs_revision`, `blocked`, `patch_generated`, `no_patch` must not be collapsed incorrectly.
- [ ] If `--evaluate` and `swebench` is missing, mark official eval unavailable/skipped in both runs and report, not pass.
- [ ] Run focused tests:
  `source .venv/bin/activate && python -m unittest tests.test_swebench_compare -v`

---

## Task 4: Static visual evidence dashboard

**Files:**
- Modify: `agent_forge/evaluation/report.py`
- Modify: `agent_forge/multi_agent/report.py`
- Test: `tests/test_interview_visual_reports.py`

**Interfaces:**
- Consumes: `EvaluationComparison` and `MultiAgentRunSummary`.
- Produces: dependency-free HTML dashboard and Markdown/Mermaid sections.

- [ ] Render a single-vs-multi metric table with delta columns.
- [ ] Render status cards for patch, official eval, verifier, revision rounds, cost, calls, and failures.
- [ ] Render Mermaid role swimlane / artifact chain in Markdown reports.
- [ ] Render dependency-free HTML with sections: executive summary, role timeline, artifact handoff, comparison metrics, failure taxonomy, tool safety matrix, and interview talking points.
- [ ] Keep colors accessible and status colors labeled with text/icons, not color alone.
- [ ] Add smoke tests that dashboard HTML contains the major sections and no external CDN/framework references.

---

## Task 5: Coding showcase and research profile tuning

**Files:**
- Modify: `agent_forge/multi_agent/profiles.py`
- Modify: `tests/test_multi_agent_coordinator.py`
- Create/Modify: `tests/test_swebench_compare.py` as needed
- Docs: `docs/evaluation/评测目录说明与SWE-bench使用入口.md`, `docs/多Agent协作机制与对比评测说明.md`

**Interfaces:**
- Produces: reproducible local showcase path and stable research pass/needs-revision semantics.

- [ ] Add fake-LLM test that forces Implementer r0 -> Reviewer NEEDS_REVISION -> Implementer r1 -> Verifier PASS.
- [ ] Ensure artifacts show the full revision loop.
- [ ] Tune `research_report` reviewer/verifier instructions: honest source limitation can PASS; only concrete unsupported/contradictory/high-impact missing caveats require revision.
- [ ] Add test that offline limitation + caveated draft can pass reviewer/verifier.
- [ ] Document real provider showcase commands and clearly state provider/API/Docker unavailable cases are skipped.

---

## Task 6: Interview learning material and concurrency story

**Files:**
- Create: `docs/interview/agent-forge-defense-zh.md`
- Create: `docs/interview/multi-agent-concurrency-evolution-zh.md`
- Modify: `评测目录说明与SWE-bench使用入口.md`
- Modify: `docs/多Agent协作机制与对比评测说明.md`
- Modify: `docs/evaluation/评测目录说明与SWE-bench使用入口.md`

**Interfaces:**
- Produces: high-density material the user can study and use in interviews.

- [ ] Write a concise Chinese defense doc covering: runtime control plane, tool governance, artifact handoff, workspace isolation, trace/usage, evaluation, failure taxonomy, and non-goals.
- [ ] Write a truthful concurrency evolution doc: current sequential coordinator, why chosen for reproducibility, how production could parallelize independent reviewers/verifiers over isolated workspaces/artifacts, what changes in conflict resolution/cost/cancellation.
- [ ] Include interview-safe wording: do not claim current code is true parallel; say the architecture intentionally keeps a deterministic MVP and documents the production path.
- [ ] Update README with interview-ready project positioning and visual artifact outputs.

---

## Task 7: Final handoff and verification

**Files:**
- Modify: `.agent_forge/codex_handoff.md`

**Interfaces:**
- Produces: truthful final handoff with completed work, skipped work, test commands, and known limitations.

- [ ] Run: `source .venv/bin/activate && python -m compileall -q agent_forge tests`
- [ ] Run: `source .venv/bin/activate && python -m unittest discover tests`
- [ ] Run: `bash scripts/verify.sh`
- [ ] Run: `git diff --check`
- [ ] If real DeepSeek/SWE-bench/Docker showcase cannot run, record skipped reason precisely.
- [ ] Update `.agent_forge/codex_handoff.md` with new files, changed files, verification output, and remaining TODOs.

---

## Self-Review

- Spec coverage: compare isolation, evaluation extraction, visual reports, coding showcase, research tuning, stale/safety fixes, docs, and handoff are covered.
- No false concurrency claim: docs must distinguish deterministic MVP from production parallel evolution.
- No provider scope violation: no Claude/Anthropic provider work.
- No heavy frontend framework: visual dashboard is static generated HTML.
- Placeholder scan: no task contains TBD/TODO placeholders.
