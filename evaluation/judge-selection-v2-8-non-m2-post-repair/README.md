# Judge Selection V2.8 - Non-M2 Post-Repair Screening

Terminal status: **V2_8_NO_NON_M2_JUDGE_QUALIFIES**

Both authorized candidates (DeepSeek-v4.1-flash, MiMo-v2.5-Pro) were screened
one-shot against the frozen 180-fixture benchmark after the V2.7E uncertainty
contract repair. Neither passed all frozen hard gates. Per contract, no
least-bad selection was made. The benchmark is marked BURNED for model
development.

Key results:

| Metric | DeepSeek | MiMo Pro |
|---|---|---|
| Combined overall | 0.9333 | 0.9056 |
| Forbidden | 0.9833 | 0.95 |
| Route | 0.95 | 0.95 |
| Uncertainty | 0.8667 | 0.8167 |
| Repair subset (24) | 0.6667 | 0.5833 |
| Safety-critical forbidden FN | 0 | 1 |

No V2.9 fresh validation, product runtime, or holdout was started.

Successor: a preregistered, NOT-AUTHORIZED draft for the next screening stage
exists at evaluation/judge-selection-v2-9-draft/ (TASK-SPEC-DRAFT.md sha
a5819c8c8c64f34c0591e49ca85df2f1288c6cffb2d318557e153e31b98851fc, amended to
pin a frozen pre-registered gate evaluator). It
incorporates this task's post-terminal burned-data diagnostic as design basis
and requires explicit owner authorization with a named candidate set before
anything executes.
