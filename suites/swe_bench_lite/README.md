# SWE-bench Lite

**Dataset:** [`SWE-bench/SWE-bench_Lite`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite),
test split, via the official [`swebench`](https://github.com/SWE-bench/SWE-bench)
package/harness. 300 tasks across 12 Python repos (Django, Flask,
scikit-learn, sympy, matplotlib, requests, pytest, astropy, sphinx,
pydata/xarray, pylint, and others), each a real closed GitHub issue paired
with the repo checkout at the moment it was filed.

**Grading:** entirely mechanical. The harness applies the model's patch to
the issue-commit checkout in a Docker container, then runs the instance's
`FAIL_TO_PASS` tests (must now pass) and `PASS_TO_PASS` tests (must keep
passing). Resolved or not is decided by test exit codes, not by an LLM.

**Status in this repo:** **10 of 300 instances run**, all from
`pytest-dev/pytest`, agent model `qwen3.8-flash`. Not a claim about Lite as
a whole — see the caveats in the top-level `README.md`.

## Arms

- **`direct`** — the model gets the issue text and repo checkout, produces
  one patch in a single pass.
- **`staged`** — the same task is driven through Okto Pulse's full
  plan-then-edit lifecycle (ideation → architecture/mockup → review/approve →
  spec derivation → FR/TR/AC fill-in → review/approve → implementation card)
  before a patch is taken. See `../../runners/staged_driver.py`.

Both arms run the same instances and the same diff-emission mechanics
(`../../runners/apply_staged.py`); the variable under test is the process
that produced the edit, not how the edit is turned into a diff.

## Instance list (this run)

```
pytest-dev__pytest-5221
pytest-dev__pytest-5227
pytest-dev__pytest-5413
pytest-dev__pytest-5495
pytest-dev__pytest-5692
pytest-dev__pytest-6116
pytest-dev__pytest-7220
pytest-dev__pytest-7373
pytest-dev__pytest-7432
pytest-dev__pytest-8365
```

## Reproducing

```bash
pip install swebench

python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --predictions_path ../../results/predictions_staged.jsonl \
  --run_id staged \
  --max_workers 4

python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --predictions_path ../../results/predictions_direct.jsonl \
  --run_id direct \
  --max_workers 4
```

Sanity-check the harness itself before trusting a result: run the dataset's
own gold patches through the same command with `--predictions_path` pointing
at a gold-patch predictions file. `../../results/gold.validate-gold-all-10.json`
is that check for this instance set (10/10 resolved).
