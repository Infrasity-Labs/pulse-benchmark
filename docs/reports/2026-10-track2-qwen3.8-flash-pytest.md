# Okto Pulse Track 2: Qwen 3.8 Flash on 10 pytest tasks

Prepared for OktoLabs, October 2026. Model: `qwen/qwen3.8-flash`. Pulse: `okto-pulse 0.3.2`.

## Summary

- Flash ran the full Pulse lifecycle on 10 SWE-bench Lite pytest tasks with no hints and no approvals: task creation, architecture and mockup, refinement, spec, card, baseline, reproduction test, fix, validation, submit.
- All 10 tasks reached a submitted patch and a reproduction test that failed before the fix and passed after it.
- The official SWE-bench check resolved **4 of 10** (5227, 5692, 7373, 7432). Without 5227, which carries a caveat (section 5), the result is 3 of 10.
- All 6 unresolved tasks share one cause: the patch follows a different reading of the issue than the hidden tests. No environment, harness or Pulse cause was found.
- Flash got through task creation on all 10 tasks, so this run does not support the idea that agents fail at task creation. It lost on interpreting the issue.
- Pulse had 627 tool calls and 56 failures (40 model mistakes, 2 board settings, 14 Pulse tool bugs).
- Track 1 for the same model: 10 of 10 resolved (staged), 9 of 10 (direct).

## 1. How the test was run

- **Tasks:** pytest-5221, 5227, 5413, 5495, 5692, 6116, 7220, 7373, 7432, 8365.
- **Setup:** one fresh checkout per task at its base commit, a Python 3.9 environment per task, the issue text as a file. The model did everything from task creation onward.
- **Runs:** run 1 covered 5227 and 6116; run 2 covered the other 8.
- **Grading:** the official SWE-bench harness on source-only patches, with the dataset's hidden tests.
- **Board:** `reviewer_separation_mode` was set to `warn`. With the default (`enforce`) a single agent cannot pass task validation, so every card here is self-attested.

## 2. Results for each task

| Task | Resolved | FAIL_TO_PASS | PASS_TO_PASS |
|:--|:--:|:--:|:--:|
| 5221 | no | 0/2 | 163/170 |
| 5227 | yes | 3/3 | 34/34 |
| 5413 | no | 0/1 | 92/92 |
| 5495 | no | 0/2 | 86/86 |
| 5692 | yes | 2/2 | 68/68 |
| 6116 | no | 0/2 | 69/69 |
| 7220 | no | 0/1 | 11/11 |
| 7373 | yes | 1/1 | 81/81 |
| 7432 | yes | 1/1 | 77/77 |
| 8365 | no | 0/1 | 32/32 |

Harness totals: 10 submitted, 10 completed, 4 resolved, 6 unresolved, 0 errors, 0 empty patches.

## 3. How far the tasks got in Pulse

| Step | Tasks |
|:--|:--:|
| Ideation, architecture and mockup, refinement, implementation card done | 10 of 10 |
| Reproduction test failed before and passed after | 10 of 10 |
| Patch submitted | 10 of 10 |
| Spec done and test card done | 4 of 10 (5227, 6116, 5221, 5413) |
| Resolved by the official check | 4 of 10 |

The other 6 specs were left in progress and the 6 test cards not started, all in run 2. The model recorded its scenario results on the implementation card instead. No task stopped at a Pulse step.

## 4. Why the 6 tasks were not resolved

- **5221 (fixture scope):** the hidden tests expect `[session scope]` and a bare line for function scope. The patch prints `[<scope>]` for every fixture and broke 7 existing tests. The model had edited 7 existing assertions so its own run stayed green; the harness ran the originals.
- **5413 (raises string form):** expected `<ExceptionInfo ValueError tblen=4>`. The patch returns location plus full message.
- **5495 (byte strings):** expected the index line to stay, shown as bytes. The patch removes it.
- **6116 (short option):** expected `--co`. The patch adds `-co`.
- **7220 (paths after a directory change):** expected an absolute path. The patch keeps it relative.
- **8365 (illegal user name):** expected `pytest-of-unknown`. The patch substitutes `_` for each bad character.

The model's reproduction tests passed in every case because they encode its own reading of the issue. A test written by the same model gives no independent check on that reading.

## 5. Conditions we disclose

- **Earlier board titles in run 1.** Two global knowledge-graph queries returned titles from an earlier attempt's board. For 5227 they named the one constant the fix changes. For 6116 they named `-c` and `-g`, both different from the model's `-co` and the tests' `--co`. Only titles were seen. This is the caveat on 5227.
- **Shared session.** Run 2 ran in run 1's session with its full context, so it started with Pulse know-how already learned.
- **Temporary folders.** Run 2 had no fresh temp folder; the model made its own.
- **Operator notes.** Run 2's first message carried operator notes (board setting, launch command). None touched an answer, patch or test.
- **Retries.** One retry per run after provider rate limits.
- **Recall.** The model reasoned from memory about upstream fixes in both runs. No web, dataset, gold patch or hidden test was used, and no Pulse object was deleted.

## 6. What Pulse did

| Cause of failed call | Run 1 | Run 2 | Both |
|:--|:--:|:--:|:--:|
| Model mistake | 32 | 8 | 40 |
| Board setting | 2 | 0 | 2 |
| Pulse tool bug | 12 | 2 | 14 |
| **Total failed** | 46 | 10 | 56 |
| Total Pulse calls | 252 | 375 | 627 |

- **Tool bug 1:** 6 server-capacity refusals (`mcp_admission_saturated`).
- **Tool bug 2:** 8 calls failed because optional nested parameters reached the server as strings. This blocked code-investigation receipts, code evidence, lint findings and validation pinpoints through the tool.
- **Lint gate:** all 8 run 2 lint records were accepted with score 0 and no findings. A pass here is no evidence the lint found nothing.
- **Friction:** 5227 took 171 calls and 44 failures; the other 9 tasks took 456 calls and 12 failures. Part of the drop is the model reusing what it learned in run 1.

## 7. Earlier attempt for reference

An earlier attempt on the same tasks did not use a prepared setup: worktrees held earlier edits (complete diffs for 5221 and 5227 matched what the model later submitted) and upstream history was in the clone. It also resolved 4 of 10, but 5495 resolved there and not officially, and 5692 the other way round. The two agree on 8 tasks. It is not the official result.

## 8. Limits

- 10 tasks, one repository, one run per task, one model.
- A gap of one or two tasks is a hint, not proof.
- Every card is self-attested (`reviewer_separation_mode` warn).
- Failure counts come from transcripts, sorted by error text; REST calls from a shell are not counted.
- This report covers `qwen/qwen3.8-flash` only.
