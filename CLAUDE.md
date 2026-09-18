# okto-pulse-benchmarks — persistent state

This file exists so status survives across sessions and machines, same
convention as `caura-ai`'s sibling benchmark repo this project was modeled
on. Keep it current; the README is the summary, this is the detail.

## Current status (2026-09-18)

One suite populated: `suites/swe_bench_lite`. 10 of SWE-bench Lite's 300
instances run, all `pytest-dev/pytest`, two models (`claude-opus-5`,
`qwen3.8-flash`), two arms each (`direct`, `staged`). Full numbers and
caveats: `reports/2026-09-18-swe-bench-lite-pilot.md`.

Headline, restated: staged (Okto Pulse's plan-then-edit lifecycle) never
did worse than direct at this n. `qwen3.8-flash` went 9/10 → 10/10 staged.
`claude-opus-5` was flat 4/10 in both arms, resolving the *same* 4 instances
and failing the *same* 6 — that tie is unexplained, not yet root-caused, and
is the top open item.

## Source of the raw run

The original run lived in a scratch workspace
(`~/Infrasity/bench-workspace`) before being promoted into this repo. That
scratch tree also has the per-task work directories (`qwen-direct/`,
`qwen-staged/`, `wt/`) and full container logs
(`logs/run_evaluation/<run_id>/`) that were **not** copied here — too large
to commit, and reproducible from `results/predictions_*.jsonl` via the
commands in `suites/swe_bench_lite/README.md`. If those logs are needed for
debugging the `claude-opus-5` `no_tests_collected` failures (see Next steps
below), they're still on that machine as of this writing.

A companion scratch dir (`~/Infrasity/swe-bench-workspace`) holds a
single-instance gold-patch validation (`pytest-dev__pytest-5221`) that
predates the 10-instance sanity run now in
`results/gold.validate-gold-all-10.json`; superseded, not copied here.

## Open items, in priority order

1. **Root-cause the `claude-opus-5` identical-failure-set tie.** Both arms
   hit `no_tests_collected` on the exact same 4 instances
   (`pytest-dev__pytest-5221`, `-5495`, `-5692`, `-7220`). Gold patches pass
   clean on this harness (10/10), so it isn't a broken container setup —
   check patch application and test-discovery config for those 4 instances
   specifically before assuming it's an editing-quality result.
2. **Scale past 10 instances / past one repo.** Cheapest next step is more
   `pytest` instances (harness already proven here); after that, Lite's
   other 11 repos (Django, Flask, scikit-learn, sympy, matplotlib, requests,
   astropy, sphinx, pydata/xarray, pylint, and more).
3. **Add paired significance testing** once n supports it — bootstrap CI /
   exact McNemar, not a raw count. At n=10 the best-case McNemar result
   (qwen's 1 discordant pair) still doesn't clear significance, so this repo
   makes no significance claim yet; don't let a future update assert one
   without the math actually supporting it.

## Conventions carried over from the reference repo this was modeled on

- Every comparison is **paired**: same instances, both arms, same harness
  run.
- A raw delta is a lead, not a finding, until a sample size supports a
  significance test.
- Negative / inconclusive results (the Opus tie) get reported, not dropped.
- Caveats go **before** the numbers they qualify, not as a footnote after.
