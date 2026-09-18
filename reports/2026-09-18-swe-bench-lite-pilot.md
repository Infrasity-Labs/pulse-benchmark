# SWE-bench Lite pilot — Okto Pulse staged vs direct (pytest slice, n=10)

**Date:** 2026-09-18
**Scope:** SWE-bench Lite, `pytest-dev/pytest` instances only (10 of 300)
**Agent model:** `qwen3.8-flash`
**Status:** pilot, not conclusive — see caveats

---

## TL;DR

- **Staged never did worse than direct** on this slice.
- Staged improved on direct: **9/10 → 10/10**, resolving the one instance
  (`pytest-dev__pytest-6116`, `missing_module` ambiguous failure) direct left
  unresolved.
- A gold-patch sanity run (the real upstream fixes, not model output) went
  10/10 through the identical harness, so the direct-arm miss is not a
  broken container setup.

## What was run

| arm | model | instances | resolved |
|---|---|--:|--:|
| direct | qwen3.8-flash | 10 | 9 |
| staged | qwen3.8-flash | 10 | 10 |
| gold (sanity) | n/a | 10 | 10 |

Both arms ran the **same 10 instances**, so the gap is paired.

## Results detail

Direct resolved 9/10; the sole miss was `pytest-dev__pytest-6116`, flagged
`ambiguous_failure` with reason `missing_module`. Staged resolved that same
instance and everything else: 10/10, zero ambiguous failures, zero empty
patches, zero errors.

One process note: the staged run's `task-4` needed a retry
(`qwen-staged/task-4-rerun` in the raw work tree) before it resolved. The
final 10/10 is what the harness graded, but it wasn't a clean first pass on
every task.

## Why no significance test is reported

At n=10 with a paired binary outcome, this result's shape (1 discordant
pair: staged resolved an instance direct didn't, no case of the reverse) is
the best case achievable at this sample size and still does not clear a
conventional significance threshold under an exact McNemar test. Reporting
a p-value here would overstate the precision of a 10-task pilot. The honest
read is "directional signal, worth scaling," not "proven."

## Caveats

- **One repo only.** All 10 instances are `pytest-dev/pytest`. Lite has 12
  repos; nothing here says anything about the other 11.
- **Small n.** 10 of 300 Lite instances. A wider run is the actual next step,
  not more analysis of this one.
- **One model only.** Only `qwen3.8-flash` has been run so far; whether the
  staged advantage holds on other agent models is untested.
- **Gold sanity check is clean** (`results/gold.validate-gold-all-10.json`,
  10/10), which rules out a broken harness/container as the explanation for
  the direct-arm miss.

## Next steps, in priority order

1. Scale the instance set: more `pytest` instances first (cheap, harness
   already proven on this repo), then expand to Lite's other 11 repos.
2. Once n supports it, add a paired significance test (bootstrap CI / exact
   McNemar) before any number from this suite is quoted externally.
3. Run additional agent models on the same instance set to see whether the
   staged advantage generalizes.
