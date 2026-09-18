# okto-pulse-benchmarks — persistent state

This file exists so status survives across sessions and machines, same
convention as `caura-ai`'s sibling benchmark repo this project was modeled
on. Keep it current; the README is the summary, this is the detail.

## Current status (2026-09-18)

One suite populated: `suites/swe_bench_lite`. 10 of SWE-bench Lite's 300
instances run, all `pytest-dev/pytest`, one model (`qwen3.8-flash`), two
arms (`direct`, `staged`). Full numbers and caveats:
`reports/2026-09-18-swe-bench-lite-pilot.md`.

Headline, restated: staged (Okto Pulse's plan-then-edit lifecycle) never
did worse than direct at this n, and closed the one gap direct left —
9/10 → 10/10.

## Source of the raw run

The original run lived in a scratch workspace
(`~/Infrasity/bench-workspace`) before being promoted into this repo. That
scratch tree also has the per-task work directories (`qwen-direct/`,
`qwen-staged/`, `wt/`) and full container logs
(`logs/run_evaluation/<run_id>/`) that were **not** copied here — too large
to commit, and reproducible from `results/predictions_*.jsonl` via the
commands in `suites/swe_bench_lite/README.md`.

A companion scratch dir (`~/Infrasity/swe-bench-workspace`) holds a
single-instance gold-patch validation (`pytest-dev__pytest-5221`) that
predates the 10-instance sanity run now in
`results/gold.validate-gold-all-10.json`; superseded, not copied here.

## Open items, in priority order

1. **Scale past 10 instances / past one repo.** Cheapest next step is more
   `pytest` instances (harness already proven here); after that, Lite's
   other 11 repos (Django, Flask, scikit-learn, sympy, matplotlib, requests,
   astropy, sphinx, pydata/xarray, pylint, and more).
2. **Add paired significance testing** once n supports it — bootstrap CI /
   exact McNemar, not a raw count. At n=10 the best-case McNemar result
   (this pilot's 1 discordant pair) still doesn't clear significance, so
   this repo makes no significance claim yet; don't let a future update
   assert one without the math actually supporting it.
3. **Run additional agent models** on the same instance set to check
   whether the staged advantage generalizes beyond `qwen3.8-flash`.

## Conventions carried over from the reference repo this was modeled on

- Every comparison is **paired**: same instances, both arms, same harness
  run.
- A raw delta is a lead, not a finding, until a sample size supports a
  significance test.
- Caveats go **before** the numbers they qualify, not as a footnote after.
