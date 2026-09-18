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

### Per-instance table

All patch sizes are files-changed / total-diff-lines. `F2P` is the count of
`FAIL_TO_PASS` tests that passed out of the instance's total. Every instance
in both arms kept 100% of its `PASS_TO_PASS` set — no regressions anywhere.

| Instance | Issue | Direct | Staged | F2P direct | F2P staged | Patch (direct) | Patch (staged) |
|---|---|:--:|:--:|:--:|:--:|---|---|
| pytest-5221 | Display fixture scope with `pytest --fixtures` | ✅ | ✅ | 2/2 | 2/2 | 1f/28L | 1f/28L |
| pytest-5227 | Improve default logging format | ✅ | ✅ | 3/3 | 3/3 | 2f/25L | 2f/25L |
| pytest-5413 | `str()` on the `pytest.raises` context variable | ✅ | ✅ | 1/1 | 1/1 | 1f/18L | 1f/18L |
| pytest-5495 | Confusing assertion-rewrite message for bytes | ✅ | ✅ | 2/2 | 2/2 | 2f/68L | 2f/68L |
| pytest-5692 | Hostname and timestamp in JUnit XML | ✅ | ✅ | 2/2 | 2/2 | 2f/32L | 2f/32L |
| **pytest-6116** | `--collect-only` needs a one-char shortcut | ❌ | ✅ | **0/2** | **2/2** | 1f/18L | 2f/19L |
| pytest-7220 | Wrong path when a fixture changes directory | ✅ | ✅ | 1/1 | 1/1 | 2f/37L | 2f/37L |
| pytest-7373 | Incorrect caching of skipif/xfail conditions | ✅ | ✅ | 1/1 | 1/1 | 2f/65L | 2f/64L |
| pytest-7432 | `--runxfail` breaks skip-location reporting | ✅ | ✅ | 1/1 | 1/1 | 2f/21L | 2f/21L |
| pytest-8365 | `tmpdir` creation fails for illegal usernames | ✅ | ✅ | 1/1 | 1/1 | 2f/25L | 2f/25L |

On every instance both arms resolved, the two patches are near-identical in
shape (same file count, same or near-same line count). The staged advantage
here is entirely concentrated in the one instance where direct chose a
different, wrong approach — not a general "staged writes bigger/more
careful diffs" effect.

### Worked example: pytest-6116, direct vs staged

The issue asks for `--co` as a shortcut for `--collect-only`.

**Direct** rewrote the raw CLI arg list before argparse ever sees it
(`src/_pytest/config/__init__.py`, `_prepareconfig`): `-co` (short form,
not what was asked) silently becomes `--collect-only` before parsing.
`--co` is never registered as a real option — doesn't show up in `--help`,
isn't inspectable by anything that reads the parser. Both `FAIL_TO_PASS`
tests failed; full diff at `results/examples/pytest-6116-direct.diff`.

**Staged** added `--co` as a real alias on the existing `addoption` call in
`src/_pytest/main.py`, next to `--collectonly`/`--collect-only`, plus a
changelog entry — the project's actual contribution convention. Both
`FAIL_TO_PASS` tests passed; full diff at
`results/examples/pytest-6116-staged.diff`.

The staged lifecycle's spec/FR/TR/AC step appears to have pushed the model
toward "register a real option" instead of "patch the arg list" — a
workaround vs. the fix the maintainers actually shipped, not a difference in
raw capability.

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
