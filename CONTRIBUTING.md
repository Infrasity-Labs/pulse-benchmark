# Contributing

Thanks for helping improve Pulse Benchmark.

## Ground rules

- **Keep comparisons paired.** Both arms must run the same instances through the same harness invocation.
- **Grade mechanically.** Report harness results (`FAIL_TO_PASS` / `PASS_TO_PASS`), never LLM-judged outcomes.
- **Caveats come before numbers.** Do not claim statistical significance unless a test on the sample supports it.
- **Run the gold-patch sanity check** before trusting a new instance set.
- **Keep raw evidence unedited** (harness reports, predictions, board exports).

## Adding a run

1. Add predictions and harness summaries under `results/`.
2. Add a dated write-up in `docs/reports/` named `YYYY-MM-DD-<model>-<slice>.md`.
3. Add a row to the results table in `README.md` and update its caveats.

## Pull requests

- Open an issue first for larger changes.
- Keep one logical change per PR, with a clear description.
- Do not commit secrets, API keys, or machine-specific paths. Use the environment variables documented in the README.
