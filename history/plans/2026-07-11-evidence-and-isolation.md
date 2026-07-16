# Evidence and Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development for each behavior change.

**Goal:** Add reproducible benchmark scorecards, paired runtime ablations,
official per-case SWE-bench parsing, and OCI-backed command execution without
introducing unsupported quality claims.

**Architecture:** Existing benchmark and runtime paths remain canonical. New
evaluation modules consume their artifacts; `ExecutionEnvironment` gains one
adapter mode and command tools delegate through it.

**Tech Stack:** Python 3.11 standard library, unittest, git, Docker-compatible
OCI CLI, Tectonic for the one-page CV.

## Global Constraints

- No benchmark percentage may be hard-coded into code, docs, README, or CV.
- Candidate patch, local validation, and official resolution remain separate.
- Public docs describe product/runtime behavior, not preparation process.
- The fixed regression suite contains five public SWE-bench Lite case ids.
- Container mode must fail closed when the OCI runtime or image is unavailable.

### Task 1: Official Per-Case Evaluation

**Files:**
- Create: `agent_forge/bench/official_results.py`
- Modify: `agent_forge/bench/swebench.py`, `agent_forge/bench/types.py`
- Test: `tests/test_official_results.py`, `tests/test_failure_taxonomy.py`

- [ ] Write fixtures for run-level and per-case official reports.
- [ ] Run the focused tests and confirm failures for the missing parser.
- [ ] Implement explicit resolved/failed/error/incomplete mappings.
- [ ] Run focused tests and the failure-taxonomy suite.

### Task 2: Scorecard and Paired Ablation

**Files:**
- Create: `agent_forge/evaluation/scorecard.py`, `agent_forge/evaluation/experiment.py`
- Modify: `agent_forge/evaluation/comparison.py`, `agent_forge/evaluation/__init__.py`, `agent_forge/bench/report.py`, `agent_forge/forge_cli.py`
- Test: `tests/test_evaluation_scorecard.py`, `tests/test_evaluation_experiment.py`, `tests/test_public_cli.py`

- [ ] Write tests for honest denominators, usage aggregation, and variant rows.
- [ ] Confirm the tests fail before implementation.
- [ ] Implement scorecard JSON/Markdown generation from run artifacts.
- [ ] Write mismatched-run and paired-delta ablation tests.
- [ ] Implement `forge eval ablation` and conservative conclusions.
- [ ] Run all evaluation/report tests.

### Task 3: Observable Tool-Routing Factor

**Files:**
- Modify: `agent_forge/runtime/config.py`, `agent_forge/runtime/agent_loop.py`, `agent_forge/bench/swebench.py`, `agent_forge/forge_cli.py`
- Test: `tests/test_agent_loop_policy.py`, `tests/test_public_cli.py`

- [ ] Write tests showing `task-aware` hides irrelevant schemas while `all`
      exposes them without disabling runtime policy.
- [ ] Confirm tests fail because no routing-mode control exists.
- [ ] Add the config/CLI factor and trace metadata.
- [ ] Run focused loop and CLI tests.

### Task 4: OCI Execution Environment

**Files:**
- Modify: `agent_forge/runtime/execution_environment.py`, `agent_forge/runtime/wiring.py`, `agent_forge/tools/run_command.py`, `agent_forge/tools/diagnostics.py`, `agent_forge/forge_cli.py`
- Test: `tests/test_container_execution_environment.py`, `tests/test_execution_environment_cli.py`, `tests/test_run_command_tool.py`, `tests/test_diagnostics_tool.py`

- [ ] Write a fake OCI-runner test asserting image inspection, constrained
      container start, bind mount, delegated command, manifest, and cleanup.
- [ ] Confirm the focused test fails before container mode exists.
- [ ] Implement fail-closed OCI preparation and command delegation.
- [ ] Route run-command and unittest diagnostics through the environment.
- [ ] Run focused safety/runtime tests.

### Task 5: Public Documentation and CV

**Files:**
- Modify: `README.md`, `docs/CAPABILITY_REALITY_MATRIX.md`, `docs/ROADMAP.md`, `docs/evaluation/regression-set.md`, `docs/architecture/runtime-capability-guide.md`
- Modify outside repo: `/Users/chenjiahui/Documents/GitHub/cv/sources/claude/resume_cn_claude.tex`

- [ ] Document exact control/treatment commands and claim boundaries.
- [ ] Replace the three-case set with five verified SWE-bench Lite ids.
- [ ] Archive the current CV and change `个人开源重构` to `个人独立开源实现`.
- [ ] Mention only implemented five-case scorecards, paired ablation, and OCI
      controls; do not invent outcome percentages.
- [ ] Compile and render the one-page PDF, inspect it visually, and run the full
      repository verification suite plus `git diff --check`.
