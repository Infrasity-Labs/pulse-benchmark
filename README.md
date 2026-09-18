# okto-pulse-benchmarks

**Does Okto Pulse's staged, plan-then-edit workflow actually produce better
patches than a single-shot direct edit?** This repo answers that with paired
runs of [SWE-bench Lite](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite)
against a direct-edit baseline, graded by the official `swebench` harness
(`FAIL_TO_PASS` / `PASS_TO_PASS`, nothing judged by an LLM).

**Short answer: promising, not proven yet.** On a 10-task pilot, staged
matched or beat direct on both models tested, with one model going from 9/10
to a clean 10/10. Read the caveats before quoting either number — this is a
pilot on 10 tasks from **one** of Lite's twelve repos, not the full 300-task
set, and at this sample size no comparison here clears statistical
significance.

## Results

### The one number

Tasks resolved out of 10, on the `pytest-dev/pytest` slice of SWE-bench Lite.
Higher is better.

| | `claude-opus-5` | `qwen3.8-flash` |
|:--|:--:|:--:|
| **Staged (Okto Pulse)** | 4 / 10 | **10 / 10** |
| Direct (single-shot) | 4 / 10 | 9 / 10 |
| **Staged advantage** | +0 | +1 |

**Staged never did worse than direct. At `qwen3.8-flash` it closed the one
gap direct had left, going 9/10 → 10/10.** At `claude-opus-5` the two modes
landed on the *exact same* 4 resolved instances — see caveats below before
reading that as "no effect."

### How to read this

New here? Three sentences of context.

- Every comparison is **paired**: staged and direct run the same 10 task
  instances, so a gap (or lack of one) isn't explained by one arm getting
  easier work.
- **Resolved** means the harness applied the model's patch to the repo at the
  issue commit and every `FAIL_TO_PASS` test now passes while every
  `PASS_TO_PASS` test still passes. Nothing here is graded by an LLM.
- At n=10, a raw count is a lead, not a finding. This repo does not claim
  significance anywhere — see Caveats.

### Per-model results

| Agent model | Staged | Direct | Staged advantage | Verdict |
|---|--:|--:|--:|---|
| `qwen3.8-flash` | **10/10** | 9/10 | +1 | directional, not significance-tested |
| `claude-opus-5` | 4/10 | 4/10 | +0 (identical instance set) | no observed effect at this n |

<details>
<summary><b>Per-instance breakdown</b> (resolved / unresolved / ambiguous, both models)</summary>

**`claude-opus-5`, direct** — 4 resolved, 6 unresolved (4 of those flagged
`ambiguous_failure` / `no_tests_collected`):

| Instance | Resolved? |
|---|:--:|
| pytest-dev__pytest-5227 | ✅ |
| pytest-dev__pytest-6116 | ✅ |
| pytest-dev__pytest-7373 | ✅ |
| pytest-dev__pytest-7432 | ✅ |
| pytest-dev__pytest-5221 | ❌ (no_tests_collected) |
| pytest-dev__pytest-5413 | ❌ |
| pytest-dev__pytest-5495 | ❌ (no_tests_collected) |
| pytest-dev__pytest-5692 | ❌ (no_tests_collected) |
| pytest-dev__pytest-7220 | ❌ (no_tests_collected) |
| pytest-dev__pytest-8365 | ❌ |

**`claude-opus-5`, staged** — same 4 resolved, same 6 unresolved, **identical
instance-for-instance to direct** (see Caveats — this is on its own not
strong evidence of "no effect").

**`qwen3.8-flash`, direct** — 9 resolved, 1 unresolved:

| Instance | Resolved? |
|---|:--:|
| all except pytest-dev__pytest-6116 | ✅ |
| pytest-dev__pytest-6116 | ❌ (ambiguous_failure: missing_module) |

**`qwen3.8-flash`, staged** — 10/10, no unresolved, no ambiguous failures,
no empty patches.

</details>

### Caveats, read before quoting any number

**This is a 10-task pilot on one repo, not the 300-task Lite set.** All ten
instances are from `pytest-dev/pytest`; none of the other eleven repos in
Lite (Django, Flask, scikit-learn, sympy, matplotlib, requests, astropy,
sphinx, xarray, pylint, …) have been run yet. Nothing here should be read as
a Lite-wide number.

**No significance test is reported, on purpose.** At n=10 with a paired
binary outcome, the smallest resolvable McNemar p-value on a 1-discordant-pair
result (the `qwen3.8-flash` case) is not below conventional significance
thresholds. Reporting a p-value here would imply a precision the sample
doesn't support. Treat every number above as directional.

**The `claude-opus-5` tie is not yet diagnosed.** Direct and staged resolved
the *identical* 4 instances and failed the identical 6 — including all four
`no_tests_collected` ambiguous failures showing up in both arms. That
specific failure mode (the harness not being able to collect the
`FAIL_TO_PASS` tests at all) smells like a harness/container issue shared by
both runs rather than an editing-quality result, and hasn't been
root-caused. Don't read the "+0" as "staging doesn't help at this model" —
read it as "unexplained, worth rerunning."

**Gold-patch sanity check passed.** Before trusting either run, the actual
upstream fix for all 10 instances was applied and evaluated through the same
harness: `results/gold.validate-gold-all-10.json` shows 10/10 resolved, 0
unresolved, 0 errors. The harness and container setup are not the source of
the failures above.

**`qwen3.8-flash-staged` needed a retry on one task** (`task-4`, see
`qwen-staged/task-4-rerun` in the raw run tree) before it resolved — the
10/10 is real per the harness, but wasn't first-attempt-clean throughout.

## Setup

```bash
pip install swebench
export ANTHROPIC_API_KEY=...       # for claude-opus-5 runs
# qwen3.8-flash runs go through whatever OpenAI-compatible endpoint you route it to
```

Docker is required — `swebench` builds and runs a per-instance container to
apply the patch and execute `FAIL_TO_PASS` / `PASS_TO_PASS`.

## Running

**Direct** patches are produced by prompting the model once with the issue
text and repo checkout and taking its diff as-is.

**Staged** patches are produced by driving the same task through Okto
Pulse's full lifecycle before any code is written — ideation → architecture +
mockup → review/approve → spec derivation → FR/TR/AC fill-in → review/approve
→ implementation card — then applying the resulting edit. See
`runners/staged_driver.py` (drives the lifecycle over Pulse's REST API,
since the MCP bridge stringifies array params that some gates require as
real arrays) and `runners/apply_staged.py` (turns the approved staged edit
into a real `git diff`, identical in mechanism to how the direct arm's diff
is produced — the variable under test is the process, not the edit
mechanics).

```bash
# grade a predictions file with the official harness
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --predictions_path results/predictions_staged.jsonl \
  --run_id staged \
  --max_workers 4

python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --predictions_path results/predictions_direct.jsonl \
  --run_id direct \
  --max_workers 4
```

Each run writes a `<run_id>.json` summary (the files under `results/` were
produced this way) plus a `logs/run_evaluation/<run_id>/` tree with
per-instance container logs.

## Methodology

A raw resolved-count delta is not, on its own, treated as evidence of
anything beyond "worth a bigger run":

- staged and direct run the **same instances**, so a gap isn't explained by
  one arm getting easier tasks;
- grading is entirely mechanical — the harness's `FAIL_TO_PASS`/`PASS_TO_PASS`
  test execution decides resolved or not, nothing is judged by an LLM;
- every result was checked against the **gold-patch sanity run**
  (`results/gold.validate-gold-all-10.json`) so a harness/container problem
  can't be mistaken for an editing-quality result;
- no significance claim is made below the sample size that would support one
  — see Caveats.

## Next steps, in priority order

1. **Scale past 10 instances, and past one repo.** The current pilot can't
   distinguish "staging helps" from "staging happened to help on this
   slice." Widening to more of Lite's 300 tasks and its other 11 repos is
   the only way to get a number worth quoting externally.
2. **Root-cause the `claude-opus-5` identical-failure-set tie**, especially
   the four `no_tests_collected` ambiguous failures — confirm whether it's a
   container/collection issue shared by both arms (most likely, given the
   gold run is clean) before it's cited either way.
3. **Add a paired significance test** (bootstrap CI / exact McNemar, same
   family used for Okto Pulse's other benchmark work) once the sample is
   large enough for it to be meaningful.

## Repo layout

```
results/    per-run harness summaries (*.json), raw predictions (*.jsonl),
            and the gold-patch sanity check
runners/    Okto Pulse staged-lifecycle driver (staged_driver.py), the REST
            helper it runs over (pulse_rest.py), and the diff-emission step
            shared by both arms (apply_staged.py)
scripts/    per-task problem statements / spec fields fed into the staged
            lifecycle (gen_staged.py)
suites/     benchmark definition and how to reproduce a run
reports/    dated write-ups with full numbers and caveats
```
