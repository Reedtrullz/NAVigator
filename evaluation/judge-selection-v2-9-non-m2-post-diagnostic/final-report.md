# Final Report - NAV-EXPLORE-JUDGE-SELECTION-V2_9-NON-M2-POST-DIAGNOSTIC-SCREENING

Terminal status: V2_9_NO_NON_M2_JUDGE_QUALIFIES

## 1. Task and authorization

- Task ID: NAV-EXPLORE-JUDGE-SELECTION-V2_9-NON-M2-POST-DIAGNOSTIC-SCREENING
- Authoritative spec: evaluation/judge-selection-v2-9-draft/TASK-SPEC-DRAFT.md,
  SHA a5819c8c8c64f34c0591e49ca85df2f1288c6cffb2d318557e153e31b98851fc (re-verified post-run).
- Owner authorization: explicit V2.9 authorization (2026-09-13).
- Candidates (only these two): opencode-go/deepseek-v4.1-flash, command-code/xiaomi/mimo-v2.5-pro.
- LongCat 2.0: 0 calls. GPT-5.5: not used. Subagents: 0 used.

## 2. Baseline integrity

All frozen pins verified before and after the run (see baseline-integrity.json):
draft spec, gate evaluator baedee48..., frozen prompt
a36cb9efc794b850c59a41780ed13fc3a144fbe08bf4b1bf1ffb920cbed7ded6 (iteration 2 of 3),
gold embedded SHA 613aea2a... and prepass embedded SHA c36e5221... re-verified with
the exact canonicalization used by derive_labels_v2_9.py. Historical writes: 0.
Fresh 180-fixture set: 0 collisions vs 4340 historical texts; U7E gold consistency PASS.

## 3. Benchmark construction

- 180 fresh fixtures: 60 forbidden / 60 route / 60 uncertainty.
- Deterministic prepass: 80 DETERMINISTIC_RESOLVED (judge bypassed, 0 judge calls, 0
  deterministic overrides), 100 EXPECTED_SEMANTIC_RESIDUAL (1 judge call each).
- 12 safety fixtures, 24-fixture uncertainty repair subset (V29-UNC-25..48),
  20 preregistered overcommitment traps (report-only).

## 4. Prompt freeze

Iteration 1 (V2.8-verbatim): calibration 24/25 deepseek, 22/25 mimo, zero overcommit.
Iteration 2 (frozen): 24/25 both, zero overcommit/undercommit. Prompt iteration 2 frozen
with UNRESOLVED-forcing system principle and route-granularity clarifications. No
iteration 3 (calibration overfit risk). Runtime/arbitration byte-identical to V2.8.

## 5. Official one-shot results (frozen gate evaluator, no edits)

| Metric | DeepSeek | MiMo Pro |
|---|---|---|
| Overall accuracy | 96.11% (173/180) PASS | 92.22% (166/180) FAIL |
| Forbidden | 100% PASS | 98.33% PASS |
| Route | 96.67% PASS | 91.67% FAIL |
| Uncertainty | 91.67% FAIL | 86.67% FAIL |
| Structured valid | 100% PASS | 98.89% FAIL (V29-ROUTE-36 transport + V29-UNC-53 schema-invalid; no reruns) |
| Evidence validity | 100% PASS | 100% PASS |
| Deterministic overrides | 0 PASS | 0 PASS |
| Residual overall | 93% PASS | 86% FAIL |
| Residual uncertainty | 86.11% FAIL | 77.78% FAIL |
| Repair subset (24) | 79.17% FAIL | 70.83% FAIL |
| Repair confusion zero | FAIL (5 UNC-UNRESOLVED to PARTIAL) | FAIL (6 UNC-UNRESOLVED to PARTIAL, 1 to SATISFIED) |
| Safety forbidden FN | 0 PASS | 0 PASS |
| Transport failures | 0 | 1 (V29-ROUTE-36, no rerun per frozen policy) |

Miss detail: DeepSeek 7 misses = 2 route (ACCEPTABLE to PARTIAL) + 5 uncertainty
(gold UNRESOLVED to PARTIAL). MiMo 14 incorrect rows = 12 substantive misses
(1 forbidden PRESENT to ABSENT on a non-safety fixture, 4 route, 7 uncertainty) +
2 transport/schema-invalid rows (V29-ROUTE-36, V29-UNC-53) counted wrong per frozen
policy and excluded from the gate evaluator misses list.

## 6. Overcommitment (report-only)

DeepSeek: 5 gold-UNRESOLVED committed definite (4 of 20 traps). MiMo: 8 (6 of 20 traps).
Undercommitment: 0 both. The V2.8 directional overcommitment pattern persists in both
candidates despite UNRESOLVED-forcing prompt additions; capability did not separate them.
See overcommitment-report.json. Not a gate; no threshold or prompt change made after
observation.

## 7. Stability

Not run. Frozen spec restricts stability runs to qualifying candidates; none qualified.

## 8. Selection decision

No candidate passed all hard gates. Per frozen spec: no best-of-bad selection.
Terminal status: V2_9_NO_NON_M2_JUDGE_QUALIFIES.

## 9. Interpretation and limits

The dominant failure mode is exactly the V2.8 diagnosis: models treat contract-mandated
UNRESOLVED boundaries as PARTIAL. The frozen V2.9 prompt additions reduced but did not
eliminate this (calibration zero-overcommit did not transfer to the fresh benchmark for
the boundary-heavy UNC subset). This is model-behavior evidence under a human-stable
contract (V2.7E validated), not a contract failure. DeepSeek remains the stronger
candidate on raw accuracy but is not selectable under the frozen gates.

## 10. Compliance

- No reruns, no substantive retries; one transport failure counted invalid per frozen policy.
- No gate/threshold edits after results. No runtime or product changes.
- Historical lineages untouched. Burned sets registered in burned-data-registry.json.
- Secrets: never printed, persisted, or hashed; leak QA PASS.
- Deterministic overrides: 0. Automation coverage: deterministic + boundary + judge,
  M2 responsibility NONE (human-review path per V2.6).

## 11. STOP

Hard stop per spec. No fresh judge validation, new screening, prompt tuning, contract
change, V2.10, full SUT, product integration, or product holdout without new explicit
owner authorization.
