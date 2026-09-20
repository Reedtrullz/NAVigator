# Final Report: NAV-EXPLORE-JUDGE-DEEPSEEK-V2_4-M2-CALIBRATION-FRESH-VALIDATION

## Terminal status

V2_4_DEEPSEEK_CALIBRATION_NOT_READY

## What ran

- Candidate judge: opencode-go/deepseek-v4.1-flash (V2.3 transport-verified wire ID).
- Frozen V2.2 semantic contract, labels, scoring, evidence rules: unchanged.
- 60 frozen calibration fixtures (SHA 84e28f08...726c) and gold (SHA aed6d59f...0de1): unchanged through all iterations.
- Iteration 0 ran the frozen V2.2 prompt verbatim (prompt SHA 9a20e9b2...335e5 matches the V2.2 frozen prompt SHA).
- Two prompt-iteration passes (the maximum) were used; both failed the M2 gold-UNRESOLVED gates.
- No contract changes, no scoring changes, no runtime changes, no other models, no historical writes.

## Gate results by iteration

| Gate (section 13) | iter0 | iter1 | iter2 |
|---|---|---|---|
| M2 ambiguous UNRESOLVED >= 0.90 | 7/18 (0.389) | 11/18 (0.611) | 8/18 (0.444) |
| M2 insufficient UNRESOLVED (part of amb/insuf gate) | 0/6 (0.000) | 5/6 (0.833) | 6/6 (1.000) |
| M2 clear critical >= 0.95 | 12/12 | 11/12 | 12/12 |
| Critical false negatives = 0 | 0 | 0 | 0 |
| M1 hedged evaluability >= 0.90 | 12/12 | 12/12 | 12/12 |
| Controls >= 0.90 | 11/12 | 11/12 | 11/12 |
| Valid structured >= 0.99 | 58/60 (0.967) | 60/60 | 60/60 |
| Derivation consistency = 1.0 | 1.0 | 1.0 | 1.0 |

Overall verdict accuracy: iter0 0.700, iter1 0.833, iter2 0.817. Best iteration: 1.

## Root-cause finding (persistent)

The candidate model's dominant weakness is the same one V2.3 identified:
forced-binary collapse on gold-UNRESOLVED critical_condition evidence. When a
candidate answer mixes support with minimization, or never addresses the
criterion condition at all, DeepSeek-v4.1-flash tends to pick a CLEAR_* state
(most often CLEAR_NON_TRIGGER_SUPPORT) instead of INSUFFICIENT_TO_DECIDE or
AMBIGUOUS_OR_CONFLICTING.

Prompt-level mechanism clarification produced measurable but insufficient gains:
the combined gold-UNRESOLVED correct rate moved 7/24 -> 16/24 -> 14/24 across
the three runs, never reaching the 0.90 gate. The failure is a model capability
boundary under the frozen V2.2 contract, not a prompt-detail problem.

## What this means

Under the frozen V2.2 two-mechanism contract, DeepSeek-v4.1-flash does not
qualify as the semantic judge. The M2 forced-binary weakness is model-intrinsic
at the prompt level available in this task; the authorized calibration budget
is exhausted.

## Provenance

- prompt_deltas_v2_4.py SHA: 5e548ff8...b4b7
- run_calibration_v2_4.py SHA: 9f60a7e9...9f55
  (recreated after machine restart; imports frozen judge_core_v2_2.py and the
  frozen official score() verbatim; only model swap + prompt-delta globals)
- calibration-results-iter0.json SHA: a5ac262e...0377
- calibration-results-iter1.json SHA: b10ca411...63e3
- calibration-results-iter2.json SHA: ca307e61...64e30
- calibration-comparison.json SHA: 9054efbd...1b68
- TASK-LOCK.json (terminal state) SHA: 1164a6c5...10b2

## Next step (owner decision)

No new blind sets, no contract relaxation, and no further prompt tuning within
this task. The V2.2 judge-model search remains open with NO qualifying model:
either the contract's M2 evidence-state mechanism needs a bounded R&D revision
(separate task, owner authorization), or a different candidate model must be
screened in a separate authorized task.
