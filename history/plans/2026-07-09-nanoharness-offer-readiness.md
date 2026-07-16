# NanoHarness Offer Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make NanoHarness a hard, compact AI Agent engineering project by strengthening failure taxonomy, baseline comparison, report quality, safety evidence, and a small regression suite without broad rewrites.

**Architecture:** Keep the core spine as Task -> Context -> AgentLoop -> Tool Governance -> Trace -> Diagnosis -> Evaluation. Add small focused data models and report builders around existing `bench`, `evaluation`, `observability`, `tools`, and `safety` modules. Avoid deleting extensions; classify them as optional capabilities that hang from the core spine.

**Tech Stack:** Python 3.11, stdlib `dataclasses`/`json`/`pathlib`, existing unittest/pytest test style, existing `forge` CLI, no new runtime dependencies.

## Global Constraints

- Keep changes high-signal and concise; do not introduce duplicate frameworks.
- Do not claim official SWE-bench resolved unless official evaluation data exists.
- Preserve existing CLI compatibility unless a step explicitly adds a backwards-compatible flag.
- Prefer small focused modules over growing already-large files.
- Multi-agent, MCP, UI, and Skills remain as extensions; do not remove them.
- Every report claim about success, patch generation, validation, or failure class must point to trace, usage, patch, or evaluation evidence.

---

## File Structure

- Create `agent_forge/bench/failure_taxonomy.py`: canonical failure classes, diagnosis dataclass, and reusable rule helpers.
- Modify `agent_forge/bench/diagnostics.py`: delegate classification to the canonical taxonomy while preserving `diagnose_case_result()` and `attach_failure_diagnosis()` public behavior.
- Modify `agent_forge/bench/types.py`: ensure case results can carry structured diagnosis fields and before/after evidence links.
- Modify `agent_forge/evaluation/types.py`: add fields for direct baseline, single agent, governed agent comparison metrics if missing.
- Modify `agent_forge/evaluation/comparison.py`: support `direct_baseline`, `single_agent`, and `governed_agent` variants, not only single-vs-multi.
- Modify `agent_forge/bench/report.py`: render a professional result card with headline, evidence levels, baseline comparison, failure taxonomy, and conservative next actions.
- Modify `agent_forge/observability/evidence.py`: add step-level citation fields without changing existing citation output.
- Create `agent_forge/bench/case_study.py`: render one markdown case study per case from result, diagnosis, patch, trace, and usage artifacts.
- Modify `agent_forge/bench/swebench.py`: write `failure_diagnosis.json` and `case_study.md` where case artifacts are already written.
- Modify `agent_forge/tools/tool_router.py`: expose routing decisions in a report-friendly structure if not already present.
- Modify `agent_forge/safety/sandbox.py` and/or `agent_forge/safety/command_policy.py`: expose concise safety policy summaries for reports.
- Create `docs/evaluation/failure-taxonomy.md`: human explanation of failure classes.
- Create `docs/evaluation/regression-set.md`: five-case regression suite design.
- Create `docs/case-studies/astropy-12907.md`: first manually curated case study.
- Create/update tests: `tests/test_failure_taxonomy.py`, `tests/test_evaluation_comparison.py`, `tests/test_bench_report.py`, `tests/test_case_study.py`, `tests/test_workspace_sandbox.py`.

---

### Task 1: Canonical Failure Taxonomy

**Files:**
- Create: `agent_forge/bench/failure_taxonomy.py`
- Modify: `agent_forge/bench/diagnostics.py`
- Test: `tests/test_failure_taxonomy.py`
- Existing reference tests: `tests/test_bench_diagnostics.py`

**Interfaces:**
- Consumes: `BenchCaseResult` from `agent_forge.bench.types`.
- Produces: `FailureDiagnosis` dataclass with fields `failure_class: str`, `summary: str`, `evidence: list[str]`, `next_actions: list[str]`, `severity: str`, `impact: str`, `interview_lesson: str`.
- Produces: `classify_case_result(result: BenchCaseResult, usage: dict, trace: dict) -> FailureDiagnosis`.

- [ ] **Step 1: Write the failing taxonomy tests**

Add `tests/test_failure_taxonomy.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from agent_forge.bench.diagnostics import diagnose_case_result
from agent_forge.bench.types import BenchCaseResult


class FailureTaxonomyTest(unittest.TestCase):
    def _result(self, root: Path, *, status="blocked", final_answer="", error="", patch_chars=0):
        trace_path = root / "trace.json"
        trace_path.write_text(json.dumps({"stop_reason": status}), encoding="utf-8")
        usage_json = root / "usage.json"
        usage_json.write_text(
            json.dumps(
                {
                    "summary": {
                        "llm_calls": 3,
                        "tool_calls": 5,
                        "failed_tool_calls": 0,
                        "total_tokens": 1000,
                    },
                    "steps": [{"context": {"selected_files_count": 0}}],
                }
            ),
            encoding="utf-8",
        )
        usage_report = root / "usage_report.md"
        usage_report.write_text("usage", encoding="utf-8")
        patch_path = root / "patch.diff"
        patch_path.write_text("x" * patch_chars, encoding="utf-8")
        return BenchCaseResult(
            instance_id="case-1",
            repo="local/repo",
            workspace=root,
            trace_path=trace_path,
            usage_report_path=usage_report,
            patch_path=patch_path,
            status=status,
            final_answer=final_answer,
            patch_chars=patch_chars,
            error=error,
        )

    def test_patch_generated_is_not_called_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            diagnosis = diagnose_case_result(self._result(Path(tmp), status="patch_generated", patch_chars=12))
        self.assertEqual(diagnosis.failure_class, "patch_generated_but_unverified")
        self.assertIn("official", " ".join(diagnosis.next_actions).lower())
        self.assertIn("candidate", diagnosis.summary.lower())

    def test_validation_environment_unavailable_beats_tool_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._result(Path(tmp), final_answer="diagnostics: missing dependency erfa; validation_blocked")
            diagnosis = diagnose_case_result(result)
        self.assertEqual(diagnosis.failure_class, "validation_environment_unavailable")
        self.assertIn("environment", diagnosis.impact.lower())

    def test_tool_schema_mismatch_has_interview_lesson(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._result(Path(tmp), final_answer="read_file ignored offset limit; wrong line window")
            diagnosis = diagnose_case_result(result)
        self.assertEqual(diagnosis.failure_class, "tool_schema_mismatch")
        self.assertIn("schema", diagnosis.interview_lesson.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_failure_taxonomy.py -q
```

Expected: FAIL because `failure_taxonomy.py` does not exist and current classes use old names like `candidate_patch_generated`.

- [ ] **Step 3: Implement canonical taxonomy module**

Create `agent_forge/bench/failure_taxonomy.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .types import BenchCaseResult


@dataclass(frozen=True)
class FailureDiagnosis:
    """Actionable diagnosis derived from benchmark artifacts."""

    failure_class: str
    summary: str
    evidence: list[str]
    next_actions: list[str]
    severity: str = "medium"
    impact: str = ""
    interview_lesson: str = ""


def classify_case_result(result: BenchCaseResult, usage: dict[str, Any], trace: dict[str, Any]) -> FailureDiagnosis:
    summary = usage.get("summary") or {}
    stop_reason = str(usage.get("stop_reason") or trace.get("stop_reason") or "")
    final_answer = str(result.final_answer or usage.get("final_answer") or trace.get("final_answer") or "")
    failed_tools = _int(summary.get("failed_tool_calls"))
    total_tokens = _int(summary.get("total_tokens"))
    tool_calls = _int(summary.get("tool_calls"))
    llm_calls = _int(summary.get("llm_calls"))
    selected_file_counts = [
        _int((step.get("context") or {}).get("selected_files_count"))
        for step in usage.get("steps", [])
        if isinstance(step, dict) and step.get("context")
    ]
    max_selected_files = max(selected_file_counts) if selected_file_counts else 0
    evidence = [
        f"status={result.status}",
        f"eval={result.evaluation_status}",
        f"stop_reason={stop_reason or 'unknown'}",
        f"patch_chars={result.patch_chars}",
        f"llm_calls={llm_calls}",
        f"tool_calls={tool_calls}",
        f"failed_tool_calls={failed_tools}",
        f"total_tokens={total_tokens}",
        f"max_selected_files={max_selected_files}",
    ]
    if result.error:
        evidence.append(f"runner_error={result.error[:240]}")

    lowered = " ".join([result.status, result.evaluation_status, stop_reason, final_answer, result.error]).lower()

    if result.error:
        return FailureDiagnosis(
            "runner_or_environment_error",
            "Runner, checkout, provider, or local environment failed before the agent could produce reliable evidence.",
            evidence,
            ["Fix the runner/provider/environment error first, then re-run the same case."],
            severity="high",
            impact="The run cannot isolate agent behavior until the harness environment is healthy.",
            interview_lesson="Separate harness failures from agent reasoning failures before tuning prompts or tools.",
        )
    if "validation_blocked" in lowered or "missing dependency" in lowered or "no module named" in lowered:
        return FailureDiagnosis(
            "validation_environment_unavailable",
            "Validation could not complete because the test environment or dependency set was unavailable.",
            evidence,
            ["Fix or document the validation environment, then re-run without changing the agent policy."],
            severity="medium",
            impact="A candidate patch may be correct, but the run cannot prove it locally.",
            interview_lesson="Evaluation must distinguish code failure from environment failure so optimization targets stay accurate.",
        )
    if result.evaluation_status == "official_eval_failed":
        return FailureDiagnosis(
            "official_eval_failed",
            "The official SWE-bench harness ran and rejected the candidate patch.",
            evidence,
            ["Read official eval output and patch.diff together; add this case to regression before tuning."],
            severity="high",
            impact="The generated patch did not satisfy benchmark correctness criteria.",
            interview_lesson="Patch generation, local validation, and official resolution are different evidence levels.",
        )
    if result.patch_chars > 0:
        return FailureDiagnosis(
            "patch_generated_but_unverified",
            "The agent produced a candidate patch, but it should not be called resolved without validation evidence.",
            evidence,
            ["Run local diagnostics or official SWE-bench evaluation before claiming solved."],
            severity="low",
            impact="The runtime reached edit capability, but correctness remains unproven.",
            interview_lesson="Conservative reporting prevents benchmark demos from becoming unsupported success claims.",
        )
    if "offset" in lowered and "limit" in lowered and ("ignored" in lowered or "line window" in lowered):
        return FailureDiagnosis(
            "tool_schema_mismatch",
            "The model attempted a natural tool-call shape that the runtime tool schema did not support correctly.",
            evidence,
            ["Align tool schema and coercion with common model invocation patterns, then replay the case."],
            severity="high",
            impact="The agent can waste steps or inspect the wrong code even when the right intent is visible.",
            interview_lesson="Agent tools are model-facing contracts; schema mismatch is an agent reliability bug, not just an API bug.",
        )
    if "pending_tool_call_at_stop" in lowered:
        return FailureDiagnosis(
            "pending_tool_call_at_stop",
            "The model still requested a tool on the final turn, so the runtime blocked an incomplete artifact.",
            evidence,
            ["Inspect the final model action and increase budget or force an earlier patch/no-patch decision."],
            severity="high",
            impact="The final answer is not trustworthy because the model had unfinished tool intent.",
            interview_lesson="Final answers need runtime validation; unfinished tool calls should not be treated as completed work.",
        )
    if "incompleteread" in lowered or "request_failed" in lowered:
        return FailureDiagnosis(
            "provider_transport_error",
            "The provider transport failed or returned an incomplete response before the agent finished.",
            evidence,
            ["Treat as provider instability; retry only after the client converts transport failures into structured observations."],
            severity="high",
            impact="The failure says little about coding ability until transport errors are isolated.",
            interview_lesson="Runtime observability should separate model/provider transport from agent logic failures.",
        )
    if "repeated" in lowered:
        return FailureDiagnosis(
            "repeated_action_loop",
            "The loop collapsed into repeated or near-repeated tool use before producing a patch.",
            evidence,
            ["Use trace timeline to find the first repeated action and add recovery that forces a different observation path."],
            severity="high",
            impact="The agent spent budget without gaining new information.",
            interview_lesson="Loop control needs risk-aware repetition policy: repeated reads and repeated writes should not be handled identically.",
        )
    if "command blocked" in lowered or "unsafe" in lowered or "permission" in lowered:
        return FailureDiagnosis(
            "unsafe_or_blocked_command",
            "Command or permission policy blocked an unsafe or unsupported action.",
            evidence,
            ["Replace free-form shell behavior with a narrower diagnostics tool or explicit approval path."],
            severity="medium",
            impact="The run preserved safety, but may need a better sanctioned validation path.",
            interview_lesson="Tool governance should narrow side effects while still giving agents a valid path to complete work.",
        )
    if failed_tools > 0:
        return FailureDiagnosis(
            "tool_not_available",
            "One or more requested tools failed or were unavailable, and the agent did not recover into a patch.",
            evidence,
            ["Classify the failed tool as retryable, hidden-by-policy, or schema-invalid."],
            severity="medium",
            impact="The agent's plan depended on an action that the runtime could not execute.",
            interview_lesson="Tool availability and recovery policy are part of the agent control plane.",
        )
    if max_selected_files == 0 and result.status in {"blocked", "no_patch"}:
        return FailureDiagnosis(
            "context_miss",
            "The agent did not surface concrete source files before stopping.",
            evidence,
            ["Tune file ranking, symbol search, or external context retrieval for this case."],
            severity="high",
            impact="The model likely lacked the code evidence needed to make a safe edit.",
            interview_lesson="Context engineering should be evaluated by whether expected files appear before the agent commits to an action.",
        )
    if result.status == "no_patch":
        return FailureDiagnosis(
            "no_patch_generated",
            "The loop ended without producing a diff even though it was not explicitly blocked.",
            evidence,
            ["Inspect the last two trace steps and require either a patch or a concrete blocker with evidence."],
            severity="medium",
            impact="The agent did not reach the edit phase.",
            interview_lesson="A useful harness explains no-patch outcomes instead of treating them as generic failure.",
        )
    return FailureDiagnosis(
        "unclassified",
        "No specific diagnosis matched. Keep the trace and usage artifacts for manual review.",
        evidence,
        ["Promote this pattern into a diagnosis rule if it repeats."],
        severity="low",
        impact="The current taxonomy does not yet cover this behavior.",
        interview_lesson="Failure taxonomies should evolve from repeated bad cases, not from abstract labels alone.",
    )


def _int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
```

- [ ] **Step 4: Update diagnostics to delegate to taxonomy**

Modify `agent_forge/bench/diagnostics.py`:

```python
from .failure_taxonomy import FailureDiagnosis, classify_case_result
```

Replace the body of `diagnose_case_result()` after reading `usage` and `trace` with:

```python
    return classify_case_result(result, usage, trace)
```

Keep `_read_json()` and `_usage_json_path()` intact. Remove the old inline rule ladder only after tests pass.

- [ ] **Step 5: Run targeted diagnostics tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_failure_taxonomy.py tests/test_bench_diagnostics.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add agent_forge/bench/failure_taxonomy.py agent_forge/bench/diagnostics.py tests/test_failure_taxonomy.py tests/test_bench_diagnostics.py
git commit -m "feat: centralize coding agent failure taxonomy"
```

---

### Task 2: Baseline / Before-After Comparison Model

**Files:**
- Modify: `agent_forge/evaluation/types.py`
- Modify: `agent_forge/evaluation/comparison.py`
- Test: `tests/test_evaluation_comparison.py`

**Interfaces:**
- Consumes: dict summaries for variants named `direct_baseline`, `single_agent`, `governed_agent`, and optionally `multi_agent`.
- Produces: `compare_variants(task_id: str, variants: dict[str, dict]) -> dict`.
- Preserves: existing `compare_runs(task_id, single, multi)` behavior.

- [ ] **Step 1: Add failing tests for three-way comparison**

Append to `tests/test_evaluation_comparison.py`:

```python
from agent_forge.evaluation.comparison import compare_variants


def test_compare_variants_explains_agent_loop_value():
    result = compare_variants(
        "case-1",
        {
            "direct_baseline": {"patch_generated": False, "estimated_cost_usd": 0.01, "failure_class": "context_miss"},
            "single_agent": {"patch_generated": True, "tool_calls": 8, "estimated_cost_usd": 0.04, "failure_class": "patch_generated_but_unverified"},
            "governed_agent": {"patch_generated": True, "tool_calls": 6, "failed_tool_calls": 0, "estimated_cost_usd": 0.045, "failure_class": "patch_generated_but_unverified"},
        },
    )
    assert result["task_id"] == "case-1"
    assert result["variants"]["direct_baseline"]["patch_generated"] is False
    assert result["variants"]["single_agent"]["patch_generated"] is True
    assert "AgentLoop" in result["before_after_summary"]
    assert "governed" in result["recommendation"].lower()


def test_compare_variants_stays_conservative_when_cost_only_increases():
    result = compare_variants(
        "case-2",
        {
            "direct_baseline": {"patch_generated": True, "estimated_cost_usd": 0.01},
            "single_agent": {"patch_generated": True, "estimated_cost_usd": 0.05, "failed_tool_calls": 2},
            "governed_agent": {"patch_generated": True, "estimated_cost_usd": 0.07, "failed_tool_calls": 3},
        },
    )
    assert "global claim" in result["recommendation"].lower()
```

- [ ] **Step 2: Run comparison tests to verify failure**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_evaluation_comparison.py -q
```

Expected: FAIL because `compare_variants` is missing.

- [ ] **Step 3: Implement compare_variants**

Append to `agent_forge/evaluation/comparison.py`:

```python

def compare_variants(task_id: str, variants: dict[str, dict]) -> dict:
    """Compare direct baseline, single agent, and governed agent without hype."""

    normalized = {name: _normalize_variant(data) for name, data in variants.items()}
    direct = normalized.get("direct_baseline", {})
    single = normalized.get("single_agent", {})
    governed = normalized.get("governed_agent", {})
    before_after = _before_after_summary(direct, single, governed)
    return {
        "task_id": task_id,
        "variants": normalized,
        "before_after_summary": before_after,
        "recommendation": _recommend_variants(direct, single, governed),
    }


def _normalize_variant(data: dict) -> dict:
    return {
        "status": str(data.get("status") or data.get("stop_reason") or ""),
        "patch_generated": bool(data.get("patch_generated") or data.get("patch_chars", 0)),
        "verified": bool(data.get("verified") or data.get("local_verified") or data.get("official_resolved")),
        "failure_class": str(data.get("failure_class") or data.get("failure_taxonomy") or ""),
        "estimated_cost_usd": _float(data, "estimated_cost_usd"),
        "llm_calls": _int(data, "llm_calls"),
        "tool_calls": _int(data, "tool_calls"),
        "failed_tool_calls": _int(data, "failed_tool_calls"),
    }


def _before_after_summary(direct: dict, single: dict, governed: dict) -> str:
    if not direct:
        return "No direct baseline was recorded; compare agent variants only."
    if not direct.get("patch_generated") and single.get("patch_generated"):
        return "AgentLoop improved over one-shot baseline by reaching a candidate patch with tool-backed repository inspection."
    if single.get("failed_tool_calls", 0) > governed.get("failed_tool_calls", 0):
        return "Governed runtime reduced failed tool calls compared with the unguided single-agent loop."
    return "The comparison does not prove a quality improvement; read failure classes and cost before making a claim."


def _recommend_variants(direct: dict, single: dict, governed: dict) -> str:
    if not direct.get("patch_generated") and governed.get("patch_generated"):
        return "governed_agent is worth the added cost for this case because it produced a candidate patch where one-shot did not."
    if single and governed and governed.get("failed_tool_calls", 0) < single.get("failed_tool_calls", 0):
        return "governed_agent may be preferable because tool governance reduced failed tool calls."
    return "insufficient evidence for a global claim; compare success, observability, cost, and failure mode case by case."
```

- [ ] **Step 4: Run comparison tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_evaluation_comparison.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agent_forge/evaluation/comparison.py tests/test_evaluation_comparison.py
git commit -m "feat: compare baseline single and governed agent variants"
```

---

### Task 3: Professional Benchmark Report Quality

**Files:**
- Modify: `agent_forge/bench/report.py`
- Test: `tests/test_bench_report.py`

**Interfaces:**
- Consumes: `BenchRunSummary` with case results and diagnosis fields.
- Produces: `render_bench_report(summary: BenchRunSummary) -> str` with evidence-level sections.

- [ ] **Step 1: Add failing report tests**

Create `tests/test_bench_report.py`:

```python
import tempfile
from pathlib import Path

from agent_forge.bench.report import render_bench_report
from agent_forge.bench.types import BenchCaseResult, BenchRunSummary


def test_report_separates_candidate_patch_from_official_resolution():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        trace = root / "trace.json"
        usage = root / "usage_report.md"
        patch = root / "patch.diff"
        trace.write_text("{}", encoding="utf-8")
        usage.write_text("usage", encoding="utf-8")
        patch.write_text("diff", encoding="utf-8")
        case = BenchCaseResult(
            instance_id="case-1",
            repo="local/repo",
            workspace=root,
            trace_path=trace,
            usage_report_path=usage,
            patch_path=patch,
            status="patch_generated",
            evaluation_status="not_evaluated",
            patch_chars=4,
            failure_class="patch_generated_but_unverified",
            diagnosis="candidate patch only",
            diagnosis_evidence=["patch_chars=4", "eval=not_evaluated"],
            next_actions=["run official evaluation"],
        )
        summary = BenchRunSummary(
            run_id="run-1",
            dataset_name="local",
            split="test",
            provider="deepseek",
            model="default",
            output_dir=root,
            predictions_path=root / "predictions.jsonl",
            case_results=[case],
        )
        report = render_bench_report(summary)
    assert "Evidence Levels" in report
    assert "candidate patch" in report.lower()
    assert "official" in report.lower()
    assert "patch_generated_but_unverified" in report
    assert "run official evaluation" in report
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_bench_report.py -q
```

Expected: FAIL if report lacks `Evidence Levels`.

- [ ] **Step 3: Add evidence-level section to report**

In `agent_forge/bench/report.py`, after the `## Summary` block, insert:

```python
    lines.extend(
        [
            "",
            "## Evidence Levels",
            "",
            "- `patch_generated`: the workspace contains a non-empty candidate diff. This is not a solved claim.",
            "- `local_verified`: project diagnostics or tests passed in the prepared workspace.",
            "- `official_resolved`: the official SWE-bench harness accepted the patch.",
            "- `not_evaluated`: no correctness claim should be made beyond the available trace and patch evidence.",
        ]
    )
```

Then add a headline after summary counts:

```python
    if patch_generated and not any(result.evaluation_status == "official_resolved" for result in summary.case_results):
        lines.extend(
            [
                "",
                "> Candidate patches were generated, but no official resolved claim is made in this report.",
            ]
        )
```

- [ ] **Step 4: Run report tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_bench_report.py -q
```

Expected: PASS.

- [ ] **Step 5: Run existing report-related tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_swebench_compare.py tests/test_evaluation_comparison.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add agent_forge/bench/report.py tests/test_bench_report.py
git commit -m "feat: clarify benchmark report evidence levels"
```

---

### Task 4: Case Study Artifact Renderer

**Files:**
- Create: `agent_forge/bench/case_study.py`
- Modify: `agent_forge/bench/swebench.py`
- Test: `tests/test_case_study.py`

**Interfaces:**
- Produces: `render_case_study(result: BenchCaseResult) -> str`.
- Produces: `write_case_study(result: BenchCaseResult) -> Path` writing `case_study.md` next to `patch.diff`.

- [ ] **Step 1: Write failing case study test**

Create `tests/test_case_study.py`:

```python
import tempfile
from pathlib import Path

from agent_forge.bench.case_study import render_case_study, write_case_study
from agent_forge.bench.types import BenchCaseResult


def test_case_study_renders_runtime_lesson_and_evidence():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        trace = root / "trace.json"
        usage = root / "usage_report.md"
        patch = root / "patch.diff"
        trace.write_text('{"events": []}', encoding="utf-8")
        usage.write_text("usage", encoding="utf-8")
        patch.write_text("diff --git a/x b/x", encoding="utf-8")
        result = BenchCaseResult(
            instance_id="astropy__astropy-12907",
            repo="astropy/astropy",
            workspace=root,
            trace_path=trace,
            usage_report_path=usage,
            patch_path=patch,
            status="patch_generated",
            evaluation_status="not_evaluated",
            patch_chars=20,
            failure_class="patch_generated_but_unverified",
            diagnosis="candidate patch only",
            diagnosis_evidence=["patch_chars=20", "eval=not_evaluated"],
            next_actions=["run official evaluation"],
        )
        text = render_case_study(result)
        path = write_case_study(result)
    assert "# Case Study: astropy__astropy-12907" in text
    assert "Runtime Lesson" in text
    assert "patch_generated_but_unverified" in text
    assert path.name == "case_study.md"
    assert path.exists()
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_case_study.py -q
```

Expected: FAIL because module is missing.

- [ ] **Step 3: Implement case study renderer**

Create `agent_forge/bench/case_study.py`:

```python
from __future__ import annotations

from pathlib import Path

from .types import BenchCaseResult


def render_case_study(result: BenchCaseResult) -> str:
    evidence = result.diagnosis_evidence or []
    next_actions = result.next_actions or []
    lines = [
        f"# Case Study: {result.instance_id}",
        "",
        "## Why this case matters",
        "",
        f"This case exercises `{result.failure_class or 'unclassified'}` in a real repository task.",
        "",
        "## Runtime Outcome",
        "",
        f"- repo: `{result.repo}`",
        f"- status: `{result.status}`",
        f"- evaluation_status: `{result.evaluation_status}`",
        f"- patch_chars: `{result.patch_chars}`",
        f"- trace: `{result.trace_path}`",
        f"- usage: `{result.usage_report_path or '-'}`",
        f"- patch: `{result.patch_path}`",
        "",
        "## Failure Classification",
        "",
        f"- class: `{result.failure_class or 'unclassified'}`",
        f"- diagnosis: {result.diagnosis or 'No diagnosis recorded.'}",
        "",
        "## Evidence",
        "",
    ]
    lines.extend(f"- {item}" for item in evidence[:8])
    if not evidence:
        lines.append("- No structured evidence recorded.")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in next_actions[:5])
    if not next_actions:
        lines.append("- Inspect trace and promote repeated patterns into taxonomy rules.")
    lines.extend(
        [
            "",
            "## Runtime Lesson",
            "",
            "Use this case to decide whether the next improvement belongs in context selection, tool governance, sandbox policy, diagnostics, or model prompting. Do not treat a candidate patch as official resolution without evaluation evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def write_case_study(result: BenchCaseResult) -> Path:
    path = Path(result.patch_path).parent / "case_study.md"
    path.write_text(render_case_study(result), encoding="utf-8")
    return path
```

- [ ] **Step 4: Wire case study writing into benchmark flow**

In `agent_forge/bench/swebench.py`, import:

```python
from .case_study import write_case_study
```

After `attach_failure_diagnosis(result)` is called for a case result, add:

```python
write_case_study(result)
```

If there are multiple result creation paths, add the call in the common post-processing section where `patch_path`, `trace_path`, and `usage_report_path` are already known.

- [ ] **Step 5: Run targeted tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_case_study.py tests/test_swebench_compare.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add agent_forge/bench/case_study.py agent_forge/bench/swebench.py tests/test_case_study.py
git commit -m "feat: write case study artifacts for benchmark cases"
```

---

### Task 5: Safety and Tool Governance Evidence

**Files:**
- Modify: `agent_forge/tools/tool_router.py`
- Modify: `agent_forge/safety/command_policy.py`
- Modify: `agent_forge/safety/sandbox.py`
- Test: `tests/test_workspace_sandbox.py`
- Add if needed: `tests/test_tool_router.py`

**Interfaces:**
- Produces: `policy_summary() -> dict[str, object]` on safety/router components or module-level helpers if classes are not stateful.
- Reports should be able to show allowed tools, hidden tools, sandbox root, and command restrictions.

- [ ] **Step 1: Add tests for report-friendly safety summaries**

If `tests/test_tool_router.py` does not exist, create it with the smallest constructor pattern used by existing tests. If constructor setup is unclear, add module-level pure helper tests instead.

Expected helper shape:

```python
from agent_forge.safety.command_policy import command_policy_summary


def test_command_policy_summary_names_restricted_shell_behavior():
    summary = command_policy_summary()
    assert summary["free_form_shell"] is False
    assert "diagnostics" in " ".join(summary["preferred_validation_tools"])
```

Append to `tests/test_workspace_sandbox.py`:

```python
from agent_forge.safety.sandbox import sandbox_policy_summary


def test_sandbox_policy_summary_explains_path_boundary():
    summary = sandbox_policy_summary("/repo")
    assert summary["workspace_root"] == "/repo"
    assert summary["path_escape_allowed"] is False
```

- [ ] **Step 2: Run safety tests to verify failure**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_workspace_sandbox.py tests/test_tool_router.py -q
```

Expected: FAIL if helpers are missing. If `tests/test_tool_router.py` does not exist and cannot be created from existing constructors, run only the sandbox test first.

- [ ] **Step 3: Implement command policy summary**

Add to `agent_forge/safety/command_policy.py`:

```python

def command_policy_summary() -> dict[str, object]:
    """Return report-friendly command safety policy facts."""

    return {
        "free_form_shell": False,
        "path_escape_allowed": False,
        "preferred_validation_tools": ["diagnostics", "git_diff", "git_status"],
        "blocked_patterns": ["pipes", "redirects", "temporary script workarounds", "destructive commands"],
    }
```

- [ ] **Step 4: Implement sandbox policy summary**

Add to `agent_forge/safety/sandbox.py`:

```python

def sandbox_policy_summary(workspace_root: str) -> dict[str, object]:
    """Return report-friendly workspace boundary facts."""

    return {
        "workspace_root": workspace_root,
        "path_escape_allowed": False,
        "side_effect_scope": "workspace-only",
    }
```

- [ ] **Step 5: Run safety tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest tests/test_workspace_sandbox.py tests/test_tool_router.py -q
```

Expected: PASS, or run only existing tests if no router test file exists.

- [ ] **Step 6: Commit**

```bash
git add agent_forge/safety/command_policy.py agent_forge/safety/sandbox.py tests/test_workspace_sandbox.py tests/test_tool_router.py
git commit -m "feat: expose safety policy summaries for reports"
```

---

### Task 6: Small Regression Suite Documentation

**Files:**
- Create: `docs/evaluation/failure-taxonomy.md`
- Create: `docs/evaluation/regression-set.md`
- Create: `docs/case-studies/astropy-12907.md`
- Modify: `README.md`

**Interfaces:**
- Documentation must describe core spine plus extensions.
- Documentation must not overclaim official benchmark success.

- [ ] **Step 1: Write failure taxonomy documentation**

Create `docs/evaluation/failure-taxonomy.md` with this content:

```markdown
# Failure Taxonomy

NanoHarness classifies coding-agent failures so a bad run becomes an engineering target instead of a raw log.

## Evidence Levels

- `patch_generated`: non-empty diff exists; this is a candidate patch only.
- `local_verified`: project diagnostics or tests passed in the prepared workspace.
- `official_resolved`: official SWE-bench harness accepted the patch.
- `not_evaluated`: no correctness claim beyond trace and patch evidence.

## Failure Classes

| Class | Meaning | Typical next action |
| --- | --- | --- |
| `context_miss` | The agent did not surface concrete source files. | Tune file ranking, symbol search, or external context retrieval. |
| `tool_not_available` | The requested tool failed or was unavailable. | Classify as retryable, hidden-by-policy, or schema-invalid. |
| `tool_schema_mismatch` | The model called a natural shape that the tool contract did not support. | Align tool schema/coercion with observed model behavior. |
| `unsafe_or_blocked_command` | Command or permission policy blocked an unsafe action. | Replace free shell with diagnostics or approval. |
| `repeated_action_loop` | The agent repeated actions without new information. | Add recovery that forces a different observation path. |
| `pending_tool_call_at_stop` | The model still wanted a tool when the run ended. | Increase budget or force earlier patch/no-patch decision. |
| `provider_transport_error` | Provider transport failed. | Treat separately from agent logic. |
| `validation_environment_unavailable` | Tests could not run due to environment/dependencies. | Fix environment before tuning the agent. |
| `patch_generated_but_unverified` | A candidate patch exists but correctness is unproven. | Run local or official evaluation. |
| `official_eval_failed` | Official harness rejected the patch. | Analyze patch and add case to regression. |

## Interview framing

The point is not to label failures after the fact. The point is to decide whether the next improvement belongs in context selection, tool governance, sandbox policy, diagnostics, provider handling, or prompt procedure.
```

- [ ] **Step 2: Write regression set documentation**

Create `docs/evaluation/regression-set.md`:

```markdown
# Small Regression Set

NanoHarness uses a small high-signal regression set instead of chasing broad benchmark coverage during development.

## Target cases

| Case | Purpose | Primary failure mode |
| --- | --- | --- |
| `astropy__astropy-12907` | Real SWE-bench patch path and line-window tool behavior. | `tool_schema_mismatch` / `patch_generated_but_unverified` |
| `validation-env-unavailable` | Distinguish code failure from missing test dependencies. | `validation_environment_unavailable` |
| `tool-governance-blocked-command` | Show why free-form shell/write tools should be narrowed. | `unsafe_or_blocked_command` |
| `context-miss-file-selection` | Verify expected source files appear before edit decisions. | `context_miss` |
| `repeated-action-loop` | Verify repeated read/search is recoverable but repeated writes are blocked. | `repeated_action_loop` |

## Metrics

- patch generated
- local verified
- official resolved, when available
- failure class
- tool calls
- failed tool calls
- repeated actions
- context files selected
- estimated cost
- latency

## Rule

A runtime change is useful only if it improves success, observability, failure localization, cost, or safety boundary on at least one case without hiding regressions on the others.
```

- [ ] **Step 3: Write first curated case study doc**

Create `docs/case-studies/astropy-12907.md`:

```markdown
# Case Study: astropy__astropy-12907

## Why this case matters

This case is a compact real-repository example for studying Coding Agent tool contracts, candidate patch evidence, and conservative evaluation claims.

## Runtime lesson

The agent needs to inspect a narrow code window around the separability logic. If `read_file` ignores natural `offset` / `limit` arguments, the model may repeatedly inspect the wrong part of the file. This is a tool schema mismatch, not just a prompt issue.

## Evidence to collect

- `trace.json`: file inspection steps and tool arguments.
- `patch.diff`: candidate change.
- `usage.json`: tool calls, failed tools, and cost.
- `report.md`: failure class and next action.

## Boundary

A candidate patch is not an official SWE-bench resolution. Only claim `official_resolved` after official harness evaluation accepts the patch.
```

- [ ] **Step 4: Update README with core spine plus extensions**

Add a short section near the top of `README.md`:

```markdown
## Project Spine and Extensions

Core spine:

```text
Task -> Context -> AgentLoop -> Tool Governance -> Trace -> Failure Diagnosis -> Regression
```

NanoHarness keeps optional extensions such as MCP tools, multi-agent comparison, runtime Skills, and the browser workbench, but they hang from the core spine. The main engineering claim is not that every extension is always better; it is that coding-agent behavior becomes observable, comparable, and improvable.
```

- [ ] **Step 5: Commit docs**

```bash
git add README.md docs/evaluation/failure-taxonomy.md docs/evaluation/regression-set.md docs/case-studies/astropy-12907.md
git commit -m "docs: frame NanoHarness around agent evaluation evidence"
```

---

### Task 7: Final Targeted Verification

**Files:**
- No new files.

**Interfaces:**
- Confirms all prior tasks work together.

- [ ] **Step 1: Run focused unit tests**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m pytest \
  tests/test_failure_taxonomy.py \
  tests/test_bench_diagnostics.py \
  tests/test_evaluation_comparison.py \
  tests/test_bench_report.py \
  tests/test_case_study.py \
  tests/test_workspace_sandbox.py \
  tests/test_swebench_compare.py \
  -q
```

Expected: PASS.

- [ ] **Step 2: Run CLI smoke that does not require live model**

Run:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
python -m agent_forge.forge_cli --help >/tmp/nanoharness-help.txt
head -40 /tmp/nanoharness-help.txt
```

Expected: command exits 0 and prints available `forge` commands.

- [ ] **Step 3: If API key is available, run one reference case**

Run only if `DEEPSEEK_API_KEY` is set:

```bash
cd /Users/chenjiahui/Documents/GitHub/NanoHarness
forge bench swebench --showcase --agent-mode compare --provider deepseek --max-revision-rounds 2
forge report latest
```

Expected: run writes `report.md`, per-case `case_study.md`, and diagnosis fields. Do not require official resolved.

- [ ] **Step 4: Commit verification-only adjustments if needed**

Only commit if the verification revealed small fixes directly related to this plan:

```bash
git status --short
git add <fixed-files>
git commit -m "test: verify NanoHarness offer readiness flow"
```

---

## Self-Review

- Spec coverage: The plan covers failure taxonomy/case studies, baseline comparison, report quality, safety/sandbox story, and small regression suite.
- Placeholder scan: No `TBD`, `TODO`, or undefined implementation steps remain.
- Type consistency: `FailureDiagnosis`, `classify_case_result`, `compare_variants`, `render_case_study`, and `write_case_study` are defined before later tasks consume them.
- Scope check: The work is split into independently testable tasks. UI polish and MCP/context-platform integration are intentionally left for later plans because they are separate subsystems.
