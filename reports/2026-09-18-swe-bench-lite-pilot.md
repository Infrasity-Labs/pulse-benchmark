# SWE-bench Lite pilot — Okto Pulse staged vs direct (pytest slice, n=10)

**Date:** 2026-09-18
**Scope:** SWE-bench Lite, `pytest-dev/pytest` instances only (10 of 300)
**Agent models:** `claude-opus-5`, `qwen3.8-flash`
**Status:** pilot, not conclusive — see caveats

---

## TL;DR

- **Staged never did worse than direct** on this slice, at either model.
- `qwen3.8-flash` improved from 9/10 (direct) to **10/10 (staged)** —
  resolved the one instance (`pytest-dev__pytest-6116`, `missing_module`
  ambiguous failure) direct left unresolved.
- `claude-opus-5` resolved the **exact same 4/10 instances** in both arms —
  including the same 4 `no_tests_collected` ambiguous failures in both. This
  looks more like a shared harness/collection issue than an editing-quality
  result and is not yet root-caused.
- A gold-patch sanity run (the real upstream fixes, not model output) went
  10/10 through the identical harness, so the failures above are not a
  broken container setup.

## What was run

| arm | model | instances | resolved |
|---|---|--:|--:|
| direct | claude-opus-5 | 10 | 4 |
| staged | claude-opus-5 | 10 | 4 |
| direct | qwen3.8-flash | 10 | 9 |
| staged | qwen3.8-flash | 10 | 10 |
| gold (sanity) | n/a | 10 | 10 |

All arms within a model ran the **same 10 instances**, so any gap is paired.

## Results detail

### `qwen3.8-flash`

Direct resolved 9/10; the sole miss was `pytest-dev__pytest-6116`, flagged
`ambiguous_failure` with reason `missing_module`. Staged resolved that same
instance and everything else: 10/10, zero ambiguous failures, zero empty
patches, zero errors.

One process note: the staged run's `task-4` needed a retry
(`qwen-staged/task-4-rerun` in the raw work tree) before it resolved. The
final 10/10 is what the harness graded, but it wasn't a clean first pass on
every task.

### `claude-opus-5`

Both direct and staged resolved:
`pytest-dev__pytest-5227`, `pytest-dev__pytest-6116`, `pytest-dev__pytest-7373`,
`pytest-dev__pytest-7432`.

Both left unresolved:
`pytest-dev__pytest-5221`, `pytest-dev__pytest-5413`, `pytest-dev__pytest-5495`,
`pytest-dev__pytest-5692`, `pytest-dev__pytest-7220`, `pytest-dev__pytest-8365`.

Four of those six were `ambiguous_failure` with reason `no_tests_collected`
in **both** arms: `5221`, `5495`, `5692`, `7220`. `no_tests_collected` means
the harness could not even collect the `FAIL_TO_PASS` tests for the instance
after applying the patch — that's upstream of whether the patch itself was
good, and identical failure in both arms suggests a shared cause (container,
test collection config, or a systematic patch-application issue) rather than
two independently-bad edits landing on the same four tasks by chance. Not
root-caused yet; flagged as the top follow-up.

## Why no significance test is reported

At n=10 with a paired binary outcome, the `qwen3.8-flash` result (1
discordant pair: staged resolved an instance direct didn't, no case of the
reverse) is the best-case shape for that sample size and still does not
clear a conventional significance threshold under an exact McNemar test.
Reporting a p-value here would overstate the precision of a 10-task pilot.
The honest read is "directional signal, worth scaling," not "proven."

## Caveats

- **One repo only.** All 10 instances are `pytest-dev/pytest`. Lite has 12
  repos; nothing here says anything about the other 11.
- **Small n.** 10 of 300 Lite instances. A wider run is the actual next step,
  not more analysis of this one.
- **The Opus tie is unexplained.** Identical resolved-set and identical
  ambiguous-failure-set across both arms is the single most suspicious
  result in this pilot and should be root-caused before either "+0" or
  "staging doesn't matter at this model" gets repeated anywhere.
- **Gold sanity check is clean** (`results/gold.validate-gold-all-10.json`,
  10/10), which rules out a broken harness/container as the explanation for
  the above.

## Next steps, in priority order

1. Root-cause the four shared `no_tests_collected` failures in the
   `claude-opus-5` arms — check whether it's patch non-application, a
   container/collection config issue, or something in how those four
   instances' tests are discovered.
2. Scale the instance set: more `pytest` instances first (cheap, harness
   already proven on this repo), then expand to Lite's other 11 repos.
3. Once n supports it, add a paired significance test (bootstrap CI / exact
   McNemar) before any number from this suite is quoted externally.
