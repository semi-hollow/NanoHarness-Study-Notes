# 从命令到 Evidence：macOS 全链路实操

> 层级：[返回总入口](../README.md) → A1 主学习链 → 全链路实操；顺序只以总入口为准。

本页只负责执行顺序、断点、观察项和通过条件。调用关系查[系统地图](01-系统地图与代码入口.md)，
控制语义查[核心机制](02-核心机制与设计边界.md)，artifact/Evidence 查[证据闭环](03-Benchmark与证据闭环.md)。

规则：只在 macOS 执行；首轮只跑 Single Agent 和一个 Astropy Case；路径用变量；key 只放环境变量；失败保留 evidence。

## 0. 一次性安装与每日恢复

新 Mac 整块复制。固定目录后，本文不再要求替换路径：

```bash
mkdir -p "$HOME/Developer"
cd "$HOME/Developer"
test -d NanoHarness/.git || git clone https://github.com/semi-hollow/NanoHarness.git
test -d NanoHarness-Study-Notes/.git || git clone https://github.com/semi-hollow/NanoHarness-Study-Notes.git
export NH_ROOT="$HOME/Developer/NanoHarness"
export NH_NOTES="$HOME/Developer/NanoHarness-Study-Notes"
git -C "$NH_ROOT" switch master
git -C "$NH_ROOT" pull --ff-only
git -C "$NH_NOTES" switch main
git -C "$NH_NOTES" pull --ff-only
unset DEEPSEEK_API_KEY
cd "$NH_ROOT"
test -x .venv/bin/forge || ./scripts/setup_macos_local.sh
source .venv/bin/activate
python -c 'import pytest' 2>/dev/null || python -m pip install pytest
mkdir -p .agent_forge/learning
which python
which forge
forge doctor
```

`setup_macos_local.sh` 只在全新环境运行，它会做一次本地健康检查；日常不要重复。新 Terminal 只恢复：

```bash
export NH_ROOT="$HOME/Developer/NanoHarness"
export NH_NOTES="$HOME/Developer/NanoHarness-Study-Notes"
source "$NH_ROOT/.venv/bin/activate"
```

过关：`python` 和 `forge` 都指向 `$NH_ROOT/.venv/bin/`。此时 key/Docker 未就绪可以如实显示。

## 1. 看清公开命令面

```bash
cd "$NH_ROOT"
forge --help
forge run --help
forge inspect --help
forge demo --help
forge resume --help
forge bench --help
forge ui --help
forge skills list
```

只记六个公开动作：`run` 执行，`inspect` 只读，`demo` 离线展示，`resume` 继续 checkpoint，`bench` 评测，`ui` 展示 evidence。

## 2. inspect 源码并准备断点

```bash
forge inspect Harness.run
forge inspect AgentLoop.run
forge inspect ToolExecutionPipeline.execute_calls
forge inspect LocalCaseExecutor.run
```

必须画成两条链，不能伪装成一条：

```text
repository CLI -> Harness.run -> AgentLoop.run -> single-run artifacts
bench CLI -> RunSwebench -> LocalCaseExecutor -> build_agent_loop -> AgentLoop -> local/official evidence
```

Benchmark 不经过 `Harness.run`；DI 可能让 caller/flow 未登记，此时看类 docstring 与 `bench.wiring.build_swebench_runner`。

PyCharm 打开 `$NH_ROOT`，Interpreter 选 `.venv/bin/python`。Python Debug Configuration 使用 Module
name `agent_forge`、Working directory `$ProjectFileDir$`、Parameters `demo --scenario approval`。首轮断点：

1. `cli.dispatch.main`
2. `showcase.control_plane._run_phase`
3. `harness.Harness.run`
4. `runtime.application.agent_loop.AgentLoop.run`
5. `AgentLoop._run_turn`
6. `runtime.application.tool_execution.ToolExecutionPipeline._run_tool`

每次只回答“谁创建输入、下一层是谁、状态由谁持有”，不进 argparse/JSON/renderer。

## 3. 离线跑 approval 与 HITL

Demo 使用确定性 ModelPort，经过正式 Runtime，但不证明模型质量或测试通过。

```bash
cd "$NH_ROOT"
run_demo_labs() {
local before candidate
before="$(tr -d '\r\n' < .agent_forge/latest/run.txt 2>/dev/null || true)"
forge demo --scenario approval || return 1
candidate="$(tr -d '\r\n' < .agent_forge/latest/run.txt)"
test -n "$candidate" && test "$candidate" != "$before" || return 1
APPROVAL_PHASE="$candidate"
APPROVAL_ROOT="$(cd "$APPROVAL_PHASE/../.." && pwd -P)"
forge inspect "$APPROVAL_PHASE"
find "$APPROVAL_ROOT" -type f | sort
sed -n '1,220p' "$APPROVAL_ROOT/demo.md"
python -m json.tool "$APPROVAL_ROOT/showcase.json"

before="$APPROVAL_PHASE"
forge demo --scenario hitl --answer 'Python 3.11' || return 1
candidate="$(tr -d '\r\n' < .agent_forge/latest/run.txt)"
test -n "$candidate" && test "$candidate" != "$before" || return 1
HITL_PHASE="$candidate"
HITL_ROOT="$(cd "$HITL_PHASE/../.." && pwd -P)"
forge inspect "$HITL_PHASE"
sed -n '1,220p' "$HITL_ROOT/demo.md"
}
run_demo_labs || echo 'STOP：Demo 失败或 latest pointer 未更新。'
```

必须找到两个 phase、`approvals/`、`task_state/`、`operation_ledger/` 和 `human_input/`；机制解释回 `learning/02`。

## 4. 跑一次最小 Public API

CLI 是薄入口，`Harness` 是单一 Public API。这个例子离线运行两轮模型和一个自定义 Tool：

```bash
cd "$NH_ROOT"
API_OUTPUT="$(python examples/embed_harness.py)" || API_OUTPUT=""
printf '%s\n' "$API_OUTPUT" | tee .agent_forge/learning/embed_harness_output.txt
API_RUN="$(tail -n 1 .agent_forge/learning/embed_harness_output.txt | tr -d '\r\n')"
if test -d "$API_RUN"; then forge inspect "$API_RUN"; find "$API_RUN" -type f | sort
else echo 'STOP：Public API 示例失败或没有返回 artifact directory。'; fi
```

打开 `examples/embed_harness.py`，只找 `Harness.run`、`Tool.schema/execute` 和 Event listener；不背示例细节。

## 5. 创建隔离练习仓库

安全输入 key；输入不回显，也不进入 shell history：

```bash
export DEEPSEEK_API_KEY="$(python -c 'import getpass; print(getpass.getpass("DeepSeek API Key: "))')"
python -c 'import os; assert os.getenv("DEEPSEEK_API_KEY"); print("DeepSeek key is set")'
```

创建绝不污染 NanoHarness 的小仓库，并把路径保存给后续步骤：

```bash
LAB="$HOME/NanoHarness-learning-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LAB" "$NH_ROOT/.agent_forge/learning"
printf '%s\n' "$LAB" > "$NH_ROOT/.agent_forge/learning_lab.txt"
cd "$LAB"
printf 'def add(a, b):\n    return a - b\n' > calculator.py
printf 'from calculator import add\n\ndef test_add():\n    assert add(2, 3) == 5\n' > test_calculator.py
printf 'def normalize_name(name):\n    return name\n' > formatter.py
printf 'from formatter import normalize_name\n\ndef test_normalize_name():\n    assert normalize_name("  Ada  ") == "Ada"\n' > test_formatter.py
printf '.agent_forge/\n.pytest_cache/\n__pycache__/\n*.py[cod]\n' > .gitignore
git init
git add calculator.py test_calculator.py formatter.py test_formatter.py .gitignore
git -c user.name='NanoHarness Learner' -c user.email='learner@local.invalid' \
  commit -m 'create learning fixture'
python -m pytest test_calculator.py
git status --porcelain
```

pytest 应失败，但最后 `git status` 必须无输出；否则 cache/pyc 会污染 candidate patch。新 Terminal 恢复：

```bash
export NH_ROOT="$HOME/Developer/NanoHarness"
source "$NH_ROOT/.venv/bin/activate"
LAB="$(tr -d '\r\n' < "$NH_ROOT/.agent_forge/learning_lab.txt")"
test ! -f "$LAB/.agent_forge/learning_run.txt" || \
  RUN_DIR="$(tr -d '\r\n' < "$LAB/.agent_forge/learning_run.txt")"
```

## 6. 跑真实 DeepSeek run 并读 artifact

```bash
cd "$LAB"
unset RUN_DIR
BEFORE_RUN="$(tr -d '\r\n' < "$LAB/.agent_forge/latest/run.txt" 2>/dev/null || true)"
if forge run '修复 calculator.py 的 add：2 + 3 必须等于 5。不要修改测试；修改后必须调用 diagnostics，kind=pytest，target=test_calculator.py。' \
    --workspace "$LAB" --output-root "$LAB/.agent_forge/runs" \
    --provider deepseek --model deepseek-chat --max-steps 8; then
  CANDIDATE_RUN="$(tr -d '\r\n' < "$LAB/.agent_forge/latest/run.txt")"
  test -n "$CANDIDATE_RUN" && test "$CANDIDATE_RUN" != "$BEFORE_RUN" && RUN_DIR="$CANDIDATE_RUN"
fi
if test -n "${RUN_DIR:-}"; then
printf '%s\n' "$RUN_DIR" > "$LAB/.agent_forge/learning_run.txt"
forge inspect "$RUN_DIR"
forge inspect "$RUN_DIR/patch.diff"
git -C "$LAB" diff
python -m pytest "$LAB/test_calculator.py"
find "$RUN_DIR" -type f | sort
sed -n '1,220p' "$RUN_DIR/patch.diff"
python -m json.tool "$RUN_DIR/resolved_config.json" | sed -n '1,220p'
python -m json.tool "$RUN_DIR/run_manifest.json" | sed -n '1,260p'
else
  echo 'STOP：forge run 失败或 latest pointer 未更新。'
fi
```

把大 trace 压成时间线：

```bash
if test -n "${RUN_DIR:-}"; then
python - "$RUN_DIR/trace.json" <<'PY'
import json, sys
for event in json.load(open(sys.argv[1], encoding="utf-8")).get("events", []):
    print(f"step={event.get('step')} agent={event.get('agent_name') or event.get('agent')} event={event.get('event_type')}")
PY
open "$RUN_DIR"
fi
```

若没修好，保留 run，最多重跑一次并刷新 pointer。Debug 时把 `_run_phase` 换成 `cli.repository._run_single_repository_task`。

## 7. 亲手制造 approval 并 resume

```bash
cd "$LAB"
git add calculator.py
git diff --cached --quiet || git -c user.name='NanoHarness Learner' \
  -c user.email='learner@local.invalid' commit -m 'accept first exercise'
WORKTREE_STATUS="$(git status --porcelain)"
printf '%s\n' "$WORKTREE_STATUS"
unset WAIT_RUN
BEFORE_WAIT="$(tr -d '\r\n' < "$LAB/.agent_forge/latest/run.txt" 2>/dev/null || true)"
if test -z "$WORKTREE_STATUS" && forge run '修复 formatter.py：normalize_name("  Ada  ") 必须返回 "Ada"。不要修改测试；修改后运行 test_formatter.py。' \
    --workspace "$LAB" --output-root "$LAB/.agent_forge/runs" \
    --provider deepseek --model deepseek-chat --max-steps 8 \
    --approval-mode on-write --no-auto-approve-writes; then
  CANDIDATE_WAIT="$(tr -d '\r\n' < "$LAB/.agent_forge/latest/run.txt")"
  test -n "$CANDIDATE_WAIT" && test "$CANDIDATE_WAIT" != "$BEFORE_WAIT" && WAIT_RUN="$CANDIDATE_WAIT"
fi
if test -n "${WAIT_RUN:-}"; then
  forge inspect "$WAIT_RUN"
else
  echo 'STOP：approval run 失败或 latest pointer 未更新。'
fi
```

`git status` 必须无输出；否则先保留并检查第一题 evidence，不让脏 diff 进入第二题。模型也不保证一定
发出写 ToolCall。继续校验 checkpoint 和待批操作；assert 失败就最多重跑一次，不执行 decision：

```bash
APPROVAL_READY=0
if test -n "${WAIT_RUN:-}" && python - "$WAIT_RUN" "$LAB/.agent_forge/approvals" <<'PY'
import sys
from agent_forge.runtime.api import latest_checkpoint_path, list_pending_approvals, load_task_checkpoint
checkpoint = load_task_checkpoint(latest_checkpoint_path(sys.argv[1]))
pending = [item for item in list_pending_approvals(sys.argv[2]) if item.run_id == checkpoint.run_id]
assert checkpoint.status == "waiting_approval", checkpoint.status
assert len(pending) == 1, f"pending approvals={len(pending)}"
item = pending[0]
assert item.tool_name in {"apply_patch", "write_file"}, item.tool_name
assert item.action == "apply_patch", item.action
print(f"APPROVAL_READY=1 tool={item.tool_name} action={item.action} key={item.operation_key}")
PY
then
  APPROVAL_READY=1
else
  echo 'STOP：没有可批准的当前写操作。'
fi
```

只有看到 `APPROVAL_READY=1` 才继续：

```bash
unset RESUME_RUN
if test "${APPROVAL_READY:-0}" = 1 && forge resume "$WAIT_RUN" --decision approved; then
  CANDIDATE_RESUME="$(tr -d '\r\n' < "$LAB/.agent_forge/latest/run.txt")"
  test -n "$CANDIDATE_RESUME" && test "$CANDIDATE_RESUME" != "$WAIT_RUN" && RESUME_RUN="$CANDIDATE_RESUME"
fi
if test -n "${RESUME_RUN:-}"; then
forge inspect "$RESUME_RUN"
python -m pytest "$LAB/test_formatter.py"
python -m json.tool "$RESUME_RUN/resume_link.json"
sed -n '1,160p' "$RESUME_RUN/resume_chain.md"
python - "$WAIT_RUN/resolved_config.json" "$RESUME_RUN/resolved_config.json" <<'PY'
import json, sys
keys = ["provider", "model", "max_steps", "auto_approve_writes", "output_root", "execution_mode", "tool_routing"]
for label, path in [("source", sys.argv[1]), ("resume", sys.argv[2])]:
    values = json.load(open(path, encoding="utf-8"))["values"]
    print(label, {key: values.get(key) for key in keys})
PY
else
  echo 'STOP：resume 失败或 latest pointer 未更新。'
fi
```

断点换成 `cli.resume.resume_repository_task`、`_inherit_resolved_config`、
`runtime.wiring.prepare_continuation`。过关：配置一致，并能从 continuation 返回 source run。

## 8. 用 UI 对照同一份 Evidence

```bash
cd "$LAB"
forge ui --no-open --port 8765 > "$LAB/.agent_forge/ui.log" 2>&1 &
UI_PID=$!
open http://127.0.0.1:8765
```

对照 `forge inspect "$RESUME_RUN"` 查看 Run Story、Timeline、Artifacts、Claim Ladder。看完关闭：

```bash
kill "$UI_PID"
wait "$UI_PID" 2>/dev/null || true
```

只学 UI 展示了什么，不学 HTML/CSS/JSON 拼接。

## 9. 先看 Astropy 输入，再做 Official 预检

```bash
cd "$NH_ROOT"
python -c 'import datasets' 2>/dev/null || python -m pip install -e '.[bench]'
forge bench cases --output .agent_forge/learning/smoke-5.md
forge bench case astropy__astropy-12907 \
  --output .agent_forge/learning/astropy-12907-before-run.md && \
  sed -n '1,260p' .agent_forge/learning/astropy-12907-before-run.md
```

此时只看 issue、repo、base commit 和测试名，不加 `--show-gold/--show-test-patch`。我们的代码在
`$NH_ROOT/agent_forge`；Case 自带代码稍后在 workspace；`patch.diff` 才是本次 Agent 生成。

上游当前建议至少 120GB 可用存储、16GB RAM、8 CPU，x86_64 优先；Apple Silicon/arm64 仍是
experimental。先检查 Docker Desktop Settings -> Resources，并对照
[SWE-bench Docker Setup](https://www.swebench.com/SWE-bench/guides/docker_setup/)。只有下块最后打印
`OFFICIAL_PREFLIGHT_OK` 才继续：

```bash
(
  set -e
  cd "$NH_ROOT"
  docker info >/dev/null
  docker info --format 'Docker CPUs={{.NCPU}} Memory={{.MemTotal}} bytes'
  docker system df
  df -h /
  mkdir -p .agent_forge/tools
  test -d .agent_forge/tools/SWE-bench/.git || \
    git clone https://github.com/SWE-bench/SWE-bench.git .agent_forge/tools/SWE-bench
  python -m pip install -e .agent_forge/tools/SWE-bench
  git -C .agent_forge/tools/SWE-bench rev-parse HEAD | \
    tee .agent_forge/learning/swebench_revision.txt
  python -c 'import swebench; print("swebench import:", swebench.__file__)'
  python -m swebench.harness.run_evaluation --help >/dev/null
  python -c 'import os; assert os.getenv("DEEPSEEK_API_KEY"), "请按第 5 关重新输入 key"'
  forge doctor
  echo 'OFFICIAL_PREFLIGHT_OK'
)
```

不要为腾磁盘直接执行破坏性 Docker prune。包缺失是 unavailable，Docker/process 失败通常是 error；
都不能改写成 unresolved/0 分。

## 10. 跑一个真实 Astropy Local + Official Case

```bash
cd "$NH_ROOT"
BEFORE_BENCH="$(tr -d '\r\n' < .agent_forge/latest/bench.txt 2>/dev/null || true)"
unset BENCH_DIR
if forge bench swebench \
    --instance-id astropy__astropy-12907 \
    --provider deepseek --model deepseek-chat --max-steps 8 \
    --timeout-seconds 900 --evaluate --max-workers 1; then
  CANDIDATE_BENCH="$(tr -d '\r\n' < .agent_forge/latest/bench.txt)"
  test -n "$CANDIDATE_BENCH" && test "$CANDIDATE_BENCH" != "$BEFORE_BENCH" && BENCH_DIR="$CANDIDATE_BENCH"
fi
test -n "${BENCH_DIR:-}" || echo 'STOP：Benchmark 失败或 latest pointer 未更新。'
```

若命令异常退出，停在本关，不读旧 pointer。成功后执行；任一 `test/assert` 失败也停止：

```bash
BENCH_READY=0
if test -n "${BENCH_DIR:-}" && test -f "$BENCH_DIR/results.json" && \
    python - "$BENCH_DIR/results.json" <<'PY'
import json, sys
ids = [x["instance_id"] for x in json.load(open(sys.argv[1], encoding="utf-8")).get("case_results", [])]
assert ids == ["astropy__astropy-12907"], ids
PY
then
CASE_DIR="$BENCH_DIR/cases/astropy__astropy-12907"
CASE_WORKSPACE="$BENCH_DIR/workspaces/astropy__astropy-12907__single"
printf '%s\n' "$BENCH_DIR" > .agent_forge/learning/astropy_bench_dir.txt
forge inspect "$BENCH_DIR"
open "$BENCH_DIR"
BENCH_READY=1
else
  unset BENCH_DIR CASE_DIR CASE_WORKSPACE
  echo 'STOP：results.json 不存在或 Case identity 不匹配。'
fi
```

抽取 Local/Official 结论和 candidate patch：

```bash
python - "$BENCH_DIR/results.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))["case_results"][0]
for key in ["status", "patch_chars", "local_validation_status", "local_validation_evidence",
            "official_evaluation_status", "official_evaluation_report_path",
            "official_evaluation_detail", "failure_class", "diagnosis"]:
    print(f"{key}: {r.get(key)}")
PY
sed -n '1,240p' "$CASE_DIR/patch.diff"
python - "$CASE_DIR/trace.json" <<'PY'
import json, sys
events = json.load(open(sys.argv[1], encoding="utf-8")).get("events", [])
items = [e.get("validation") for e in events if e.get("event_type") == "validation_evidence"]
print(json.dumps(items, ensure_ascii=False, indent=2))
PY
```

直接读 Official 原始 Oracle；没有 parsed report 时只信 `results.json` 的显式状态：

```bash
OFFICIAL_REPORT="$(python - "$BENCH_DIR/results.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["case_results"][0].get("official_evaluation_report_path", ""))
PY
)"
if test -n "$OFFICIAL_REPORT" && test -f "$OFFICIAL_REPORT"; then
  python -m json.tool "$OFFICIAL_REPORT" | sed -n '1,320p'
else
  echo 'No parsed raw Official report: do not claim resolved.'
fi
find "$BENCH_DIR/logs" -type f | sort
```

`--timeout-seconds 900` 只限制 NanoHarness AgentLoop，不覆盖上游 Official per-case timeout。第二轮断点
只打 `RunSwebench.execute`、`LocalCaseExecutor.run`、`SwebenchOfficialEvaluator.evaluate`；JSON、报告和
Docker 清理只看结果，不学实现。

## 11. 手工 pytest，最后才揭示答案

```bash
cd "$CASE_WORKSPACE"
grep -n 'def _cstack' astropy/modeling/separable.py
python -m pytest astropy/modeling/tests/test_separable.py
cd "$NH_ROOT"
forge bench case astropy__astropy-12907 \
  --show-test-patch --show-gold --all-tests \
  --output "$BENCH_DIR/case-contract-after-run.md" && \
  sed -n '1,320p' "$BENCH_DIR/case-contract-after-run.md"
```

手工 pytest 只用于理解；没进入 trace 就不是 canonical Local Evidence。依赖缺失如实记 unavailable。
过关：闭卷说清 Case 自带代码、Agent patch、可见本地测试、隐藏 test/gold 与独立 Official Oracle。

## 12. Advanced 止步线

```bash
forge bench campaign --help
forge eval --help
forge memory --help
```

到此停止，不跑 30-slot Campaign、ablation、Memory 生命周期或 Evaluation JSON 基础设施。

## 完成记录

| 日期 | 实验 | artifact 绝对路径 | 结果/失败类别 | 能否闭卷解释 |
| --- | --- | --- | --- | --- |
|  | approval + HITL Demo |  |  |  |
|  | Public API |  |  |  |
|  | DeepSeek run |  |  |  |
|  | approval + resume |  |  |  |
|  | Workbench |  |  |  |
|  | Astropy Local |  |  |  |
|  | Astropy Official |  |  |  |

最终通过：能闭卷画出两条链；随机 symbol 能说上/下游；随机 artifact 能说 producer、consumer、
能证明/不能证明什么；能现场复现一个 run、一次 resume 和一个真实 Case。
