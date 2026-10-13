# Reproducing the benchmark

Both arms start from the same SWE-bench Lite instances and end with a `predictions_<arm>.jsonl` file that the official harness can grade. They differ only in how the patch is produced.

## Prerequisites

- Python 3.10+ and `pip install -r requirements.txt`
- Docker (the harness builds one container per instance)
- A model endpoint (OpenAI-compatible) for the agent
- **Staged arm only:** a running Okto Pulse server with a board, and these variables set:
  `PULSE_API_KEY`, `PULSE_BOARD_ID`, optionally `PULSE_BASE_URL`, `BENCH_WORKSPACE`

## 1. Direct arm

Prompt the model once with the issue text and repo checkout, and take its diff as-is. Write `results/predictions_direct.jsonl` in the `swebench` format (`instance_id`, `model_name_or_path`, `model_patch`).

## 2. Staged arm

1. **Generate task definitions.** [`scripts/gen_staged.py`](../scripts/gen_staged.py) turns each instance into the fields Pulse's lifecycle needs and writes `tasks_rest.json`.
2. **Drive the lifecycle.** [`runners/staged_driver.py`](../runners/staged_driver.py) pushes each task through Pulse's board stages over REST (via [`pulse_rest.py`](../runners/pulse_rest.py)). Every gate is evaluated server-side:
   - **Ideation:** create the card, attach the architecture and mockup, move `review -> approved -> evaluating -> done`.
   - **Refinement:** create the brownfield refinement, move `review -> approved -> done`.
   - **Spec:** derive the spec, fill FR/TR/AC, move `review -> approved`.
   - **Task:** create the implementation card off the approved spec.

   [`results/qwen3.5-9b/pulse-board-export.json`](../results/qwen3.5-9b/pulse-board-export.json) is a real export of a board that went through this chain.
3. **Emit the diff.** [`runners/apply_staged.py`](../runners/apply_staged.py) applies the edit in the instance worktree and writes `results/predictions_staged.jsonl`, using the same mechanism as the direct arm.

> **Not exercised:** Pulse's Validation stage (after Task) was not reached in the qwen3.8-flash and Qwen3.5-9B runs. Reproducing as-is reproduces that gap.

## 3. Grade with the harness

```bash
for arm in staged direct; do
  python -m swebench.harness.run_evaluation \
    --dataset_name SWE-bench/SWE-bench_Lite \
    --predictions_path results/predictions_${arm}.jsonl \
    --run_id ${arm} --max_workers 4
done
```

Each run writes a `<run_id>.json` summary and a `logs/run_evaluation/<run_id>/` tree with per-instance container logs (git-ignored). Before trusting any result, run the gold patches through the same command; [`results/gold.validate-gold-all-10.json`](../results/gold.validate-gold-all-10.json) is that check for this instance set.

See also [`suites/swe_bench_lite/README.md`](../suites/swe_bench_lite/README.md) for the suite definition and instance list.
