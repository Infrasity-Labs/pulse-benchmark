<p align="center">
  <img src="assets/pulse-benchmark-banner-v2.png" alt="pulse-benchmark: benchmarking agents inside Okto Pulse's plan-then-edit workflow" width="100%" />
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3ddc97.svg" /></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776ab.svg" />
  <img alt="Benchmark: SWE-bench Lite" src="https://img.shields.io/badge/benchmark-SWE--bench%20Lite-6d8bd6.svg" />
  <img alt="Status: pilot" src="https://img.shields.io/badge/status-pilot%20(n%3D10)-orange.svg" />
</p>

# Pulse Benchmark

**How well do agents work inside [Okto Pulse](https://github.com/OktoLabsAI/okto-pulse)'s plan-then-edit workflow?** This repository benchmarks it on [SWE-bench Lite](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite) using **two different methodologies**, one per track. Every result is graded by the official [`swebench`](https://github.com/SWE-bench/SWE-bench) harness (`FAIL_TO_PASS` / `PASS_TO_PASS`). No LLM judges any result.

| | **Track 1: Current benchmark** | **Track 2: End-to-end agent benchmark** |
|:--|:--|:--|
| **Methodology** | Prepared task and plan, scripted Pulse cycle, paired staged vs. direct comparison | Agent runs the whole Pulse cycle itself, from issue to validated patch |
| **Question** | Does a staged, plan-then-edit workflow beat a single-shot edit? | How well do agents handle the entire process without external assistance? |
| **Task creation and planning** | Prepared in advance, outside the model | Done by the agent, with no hints and no approvals |
| **What is measured** | Quality of the edit | Quality of the whole workflow, including task creation and planning |
| **Models** | qwen3.8-flash, Qwen3.5-27B, Qwen3.5-9B | Qwen 3.8 Flash, Qwen 3.8 27B, Qwen3.5-9B, Qwen3.5-2B |
| **Status** | Complete | In progress (1 of 4 models) |

> [!IMPORTANT]
> The two methodologies measure different things. All runs published before Track 2 belong to **Track 1**, and their numbers are not comparable with Track 2 results.

## Contents

- [Track 1: Current benchmark](#track-1-current-benchmark)
  - [How tasks are created and run through Pulse](#how-tasks-are-created-and-run-through-pulse)
  - [Results](#results) · [Scope](#scope) · [Per-instance breakdown](#per-instance-breakdown) · [Quick start](#quick-start)
- [Track 2: End-to-end agent benchmark](#track-2-end-to-end-agent-benchmark)
- [Repository layout](#repository-layout)
- [Contributing](#contributing) · [License](#license)

## Track 1: Current benchmark

**Methodology 1: prepared plan, staged vs. direct.** Paired runs on 10 `pytest-dev/pytest` tasks. Each task is run through a *direct* baseline (one-shot edit) and a *staged* arm (Okto Pulse's plan-then-edit lifecycle), then graded by the harness. Methodology and results below are unchanged from the original runs.

### How tasks are created and run through Pulse

> [!NOTE]
> **Exact methodology of Track 1.** The agent is graded on the edit; it does not create the task or the plan.
>
> 1. **Task definitions are prepared in advance.** For each SWE-bench instance, the problem statement, approach, code analysis, in-scope and out-of-scope lists, decisions, and the FR/TR/AC (functional requirements, technical requirements, acceptance criteria) are written ahead of time in [`scripts/gen_staged.py`](scripts/gen_staged.py). The model does not write them at run time.
> 2. **A script drives the task through Pulse over REST.** [`runners/staged_driver.py`](runners/staged_driver.py) pushes each task through the real board stages, with every gate evaluated server-side: **Ideation** (architecture and mockup attached, `review -> approved -> evaluating -> done`), then **Refinement** (`review -> approved -> done`), then **Spec** (derived from the refinement, FR/TR/AC filled, `review -> approved`), then **Task** (implementation card created off the approved spec).
> 3. **The edit is applied and a diff is emitted.** Once the card exists, [`runners/apply_staged.py`](runners/apply_staged.py) applies the edit in the instance worktree and writes a `git diff`. The direct arm uses the same diff-emission mechanics, so the variable under test is the process that led to the edit.
> 4. **Both arms are graded by the same harness run** on the same instances.
>
> **Not exercised:** Pulse's Validation stage (after Task). Every Track 1 task stopped at spec-approved plus card-created.
>
> Step-by-step instructions: [docs/reproducing.md](docs/reproducing.md).

### Results

All runs use the same 10 `pytest-dev/pytest` instances from SWE-bench Lite.

| Agent model | Metric | Staged (Okto Pulse) | Direct | Report |
|:--|:--|:--:|:--:|:--|
| `qwen3.8-flash` | Resolved (harness-graded) | **10 / 10** | 9 / 10 | [report](docs/reports/2026-09-18-swe-bench-lite-pilot.md) |
| `Qwen3.5-27B` | Resolved (harness-graded) | 10 / 10 | 10 / 10 | [report](docs/reports/2026-10-05-qwen3.5-27b-pytest-pilot.md) |
| `Qwen3.5-9B` | Code change applied (**not** harness-graded) | 10 / 10 | 10 / 10 | [report](docs/reports/2026-09-23-qwen3.5-9b-pytest-pilot.md) |

**Takeaway: promising, not proven.** Staged never did worse than direct on any model.

#### qwen3.8-flash: resolved rate, harness-graded

| Arm | Resolved |
|:--|:--:|
| **Staged (Okto Pulse)** | **10 / 10** |
| Direct (single-shot) | 9 / 10 |
| **Staged advantage** | +1 |

Staged resolved the one task direct missed, `pytest-6116`. Per-instance detail is [below](#per-instance-breakdown).

#### Qwen3.5-27B: resolved rate, harness-graded

| Arm | Resolved |
|:--|:--:|
| **Staged (Okto Pulse)** | **10 / 10** |
| Direct (single-shot) | 10 / 10 |

Both arms resolved all 10 instances with no regressions (100% of `FAIL_TO_PASS` and `PASS_TO_PASS`). With no discordant pair, this shows staged did not cost anything, not that it helped. Raw evidence: [`results/qwen3.5-27b/harness-reports-raw.txt`](results/qwen3.5-27b/harness-reports-raw.txt). Details in the [report](docs/reports/2026-10-05-qwen3.5-27b-pytest-pilot.md).

#### Qwen3.5-9B: code-change completion, not harness-graded

| Arm | Code changes applied | Staged lifecycle completed |
|:--|:--:|:--:|
| **Staged (Okto Pulse)** | **10 / 10** | Spec + Task: 10 / 10 |
| Direct (single-shot) | 10 / 10 | n/a |

Both arms produced a code change for all 10 tasks. These patches were not run through the `FAIL_TO_PASS` / `PASS_TO_PASS` harness, so this is implementation coverage rather than a resolved rate and is not blended into the figures above. Evidence: [board export](results/qwen3.5-9b/pulse-board-export.json) and [10 staged diffs](results/qwen3.5-9b/diffs-staged/).

### Scope

- 10 tasks from `pytest-dev/pytest`, not the full 300-task Lite set.
- Counts are directional. No significance test is reported at this sample size.
- The harness is validated: upstream gold patches resolve 10/10 ([`results/gold.validate-gold-all-10.json`](results/gold.validate-gold-all-10.json)).
- Per-run caveats are in the [reports](docs/reports/).

### Per-instance breakdown

`qwen3.8-flash`, all 10 instances. `F2P` is passing/total `FAIL_TO_PASS` tests. Every instance in both arms kept 100% of `PASS_TO_PASS`. A check mark means the harness marked the instance `resolved`.

| Instance | Issue | Direct | Staged | F2P (direct) | F2P (staged) | Patch size (direct → staged) |
|---|---|:--:|:--:|:--:|:--:|:--|
| pytest-5221 | Display fixture scope with `pytest --fixtures` | ✅ | ✅ | 2/2 | 2/2 | 1 file / 28 lines → 1 file / 28 lines |
| pytest-5227 | Improve default logging format | ✅ | ✅ | 3/3 | 3/3 | 2 files / 25 lines → 2 files / 25 lines |
| pytest-5413 | `str()` on the `pytest.raises` context variable doesn't match a normal `except` | ✅ | ✅ | 1/1 | 1/1 | 1 file / 18 lines → 1 file / 18 lines |
| pytest-5495 | Confusing assertion-rewrite message for byte strings | ✅ | ✅ | 2/2 | 2/2 | 2 files / 68 lines → 2 files / 68 lines |
| pytest-5692 | Hostname and timestamp in generated JUnit XML | ✅ | ✅ | 2/2 | 2/2 | 2 files / 32 lines → 2 files / 32 lines |
| **pytest-6116** | `--collect-only` needs a one-char shortcut | ❌ | ✅ | **0/2** | **2/2** | 1 file / 18 lines → **2 files / 19 lines** |
| pytest-7220 | Wrong path to test file when a fixture changes directory | ✅ | ✅ | 1/1 | 1/1 | 2 files / 37 lines → 2 files / 37 lines |
| pytest-7373 | Incorrect caching of skipif/xfail string condition evaluation | ✅ | ✅ | 1/1 | 1/1 | 2 files / 65 lines → 2 files / 64 lines |
| pytest-7432 | `--runxfail` breaks skip-location reporting | ✅ | ✅ | 1/1 | 1/1 | 2 files / 21 lines → 2 files / 21 lines |
| pytest-8365 | `tmpdir` creation fails for usernames with illegal directory characters | ✅ | ✅ | 1/1 | 1/1 | 2 files / 25 lines → 2 files / 25 lines |

On the 9 instances both arms resolved, the two patches were near-identical. Staging changed the outcome only where direct's approach was wrong.

<details>
<summary><b>Worked example: why staging fixed pytest-6116</b></summary>

The issue asks for `--co` as a shortcut for `--collect-only`. Both runs found the right area and diverged on how to wire it in.

**Direct** rewrote `-co` to `--collect-only` in the raw argument list before option parsing. That never registers `--co` as a real option, and it targets `-co` rather than the requested `--co`. Both `FAIL_TO_PASS` tests failed.

```diff
--- a/src/_pytest/config/__init__.py
+++ b/src/_pytest/config/__init__.py
+    args = ["--collect-only" if arg == "-co" else arg for arg in args]
     config = get_config(args, plugins)
```

**Staged** registered `--co` as a real alias next to the existing `--collect-only` option, plus a changelog entry per the project's conventions. Both tests passed.

```diff
--- a/src/_pytest/main.py
+++ b/src/_pytest/main.py
         "--collect-only",
+        "--co",
         action="store_true",
```

Full diffs: [direct](results/examples/pytest-6116-direct.diff), [staged](results/examples/pytest-6116-staged.diff).

</details>

### Quick start

```bash
git clone https://github.com/Infrasity-Labs/pulse-benchmark.git
cd pulse-benchmark
pip install -r requirements.txt   # installs swebench; Docker must be running
```

Re-grade the committed predictions with the official harness:

```bash
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --predictions_path results/predictions_staged.jsonl \
  --run_id staged --max_workers 4
```

To run the staged arm yourself, you need a running Okto Pulse server and these environment variables:

| Variable | Purpose |
|:--|:--|
| `PULSE_API_KEY` | API key for the benchmark agent (required) |
| `PULSE_BOARD_ID` | Board the staged chain runs on (required) |
| `PULSE_BASE_URL` | REST root, default `http://127.0.0.1:8100/api/v1` |
| `BENCH_WORKSPACE` | Directory holding the pytest checkout and per-task worktrees, default `~/bench-workspace` |

The full end-to-end procedure is in [docs/reproducing.md](docs/reproducing.md).
## Track 2: End-to-end agent benchmark

**Methodology 2: agent-driven, end to end.** Track 1 tests the edit. Track 2 tests the whole job. The agent picks up an issue and carries it through the complete Pulse cycle with no external help, ending in final validation. Early task creation and planning is where agents tend to struggle more than at code generation, and this track measures that directly.

**What the agent does on its own:** task creation and ideation, architecture and mockup, refinement, spec, implementation card, baseline, reproduction test, fix, validation, and submission.

**Rules:** no hints, no approvals, no web, dataset, gold patch or hidden tests. Each task starts from a fresh checkout at its base commit with the issue text supplied as a file. Patches are graded by the official harness with the dataset's hidden tests.

| Model | Status |
|:--|:--|
| Qwen 3.8 Flash | **Done** (10 pytest tasks, below) |
| Qwen 3.8 27B | Planned |
| Qwen3.5-9B | Planned |
| Qwen3.5-2B | Planned |

### Qwen 3.8 Flash: 10 pytest tasks

| Outcome | Result |
|:--|:--:|
| Task creation through a submitted patch | 10 / 10 |
| Reproduction test failed before the fix and passed after | 10 / 10 |
| **Resolved by the official SWE-bench check** | **4 / 10** |

Resolved: `5227`, `5692`, `7373`, `7432`. Flash completed task creation on all 10 tasks. The 6 unresolved tasks follow a different reading of the issue than the hidden tests.

Per-task results, failure analysis, Pulse tooling breakdown and run conditions: [full report](docs/reports/2026-10-track2-qwen3.8-flash-pytest.md).

## Repository layout

```text
.
├── assets/       banner image
├── docs/
│   ├── reproducing.md   end-to-end run guide
│   └── reports/         dated write-ups for both tracks
├── results/      harness summaries, predictions, gold-patch check, example diffs,
│                 and per-model artifacts (qwen3.5-9b/, qwen3.5-27b/)
├── runners/      staged lifecycle driver, Pulse REST helper, diff emission
├── scripts/      task-definition generator and banner renderer
└── suites/       benchmark definitions (swe_bench_lite/)
```

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository (code, scripts, results and documentation) is released under the [MIT License](LICENSE).

[Okto Pulse](https://github.com/OktoLabsAI/okto-pulse), the software being benchmarked, is **not** covered by this license. It is distributed under the [Elastic License 2.0](https://github.com/OktoLabsAI/okto-pulse/blob/main/LICENSE). SWE-bench and its Lite subset are separate projects with their own licenses.
