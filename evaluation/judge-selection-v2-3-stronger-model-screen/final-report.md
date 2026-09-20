# V2.3 Stronger-Model Screening - Final Report

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN
Date: 2026-09-13
Frozen spec: evaluation/judge-selection-v2-3-draft/TASK-SPEC-DRAFT.md (SHA 8b0be315b3ce0d39a4687482642e13e9f867831541f305dff2667ffd95c25152, verified unchanged)

## Outcome

STATUS: V2_3_NO_MODEL_QUALIFIES
SELECTED: null (no best-of-bad selection, per frozen section 6)

## Execution summary (frozen section 8 order)

1. V2.2 baseline re-verified: contract, prompt source (judge_core_v2_2.py), schema, derivation tables, fixture/gold hashes, manifest artifacts all match frozen SHAs; TASK-LOCK terminal V2_2_REFERENCE_MODEL_NOT_READY preserved; 0 historical writes.
2. TASK-LOCK frozen with explicit owner authorization; candidate list frozen before execution (no expansion afterward).
3. Burned V2.2 120-row benchmark reference frozen (screening-benchmark-reference.json).
4. deepseek-v4.1-flash transport verification: PASS via existing commandcode local proxy, 2 bounded non-benchmark probes; TRANSPORT_VERIFIED recorded in transport-verification.json. No provider/auth repair.
5. One-shot screens (120 calls each, frozen scoring verbatim from run_official_v2_2.py, 429/5xx single-retry policy unchanged):

| Priority | Candidate | Overall | M1 | M2 | Controls | Valid-structured | Deriv. consistency | Invalid rows |
|---|---|---|---|---|---|---|---|---|
| 1 | mimo-v2.5 (command-code/xiaomi/mimo-v2.5) | 0.7917 | 0.80 | 0.75 | 0.825 | 0.9417 | 1.0 | 7 |
| 2 | ling-3.0-flash-sante (command-code/inclusionai/ling-3.0-flash-sante:free) | 0.6333 | 0.85 | 0.65 | 0.40 | 0.7833 | 1.0 | 26 |
| 3 | laguna-s-2.1 (command-code/poolside/laguna-s-2.1-free) | 0.75 | 0.875 | 0.625 | 0.75 | 0.95 | 1.0 | 6 |
| 4 | deepseek-v4.1-flash (opencode-go/deepseek-v4.1-flash) | 0.8333 | 0.925 | 0.725 | 0.85 | 1.0 | 1.0 | 0 |

6. Gate extraction (mechanical, frozen V2.2 sections 35-38 semantics; gate-extraction-*.json):
   - mimo-v2.5: 10/14 gates fail (overall, valid-structured, evidence-span validity, M1, M2 gold-UNRESOLVED, M2 forced-NOT_TRIGGERED, M2 clear-critical, critical FN, controls). Passes: M1 hedged zero-gates, derivation consistency, forced-TRIGGERED zero, no safety regression.
   - ling-3.0-flash-sante: 10/14 gates fail. Invalid rows: 20 quota HTTP 429 + 6 schema. Even among completed rows, M1 0.85 / M2 clear 0.7692 / controls 0.40 fail capability gates regardless of quota.
   - laguna-s-2.1: 10/14 gates fail (adds forced-TRIGGERED violations).
   - deepseek-v4.1-flash: 6/14 gates fail (overall 0.8333, M1 0.925, M2 gold-UNRESOLVED 0.2143, M2 forced-TRIGGERED 1, M2 forced-NOT_TRIGGERED 6, controls 0.85). Passes: valid-structured 1.0, evidence-span validity 1.0, derivation consistency 1.0, M2 clear-critical 1.0, critical FN 0, M1 hedged zero-gates, no safety regression.
7. Stability stage: not run for any candidate (eligibility requires passing ALL one-shot gates; no candidate did).
8. Comparison frozen before selection (candidate-comparison.json). Selection rule applied: 0 qualifiers.

## Model-capability reading (diagnostic only; no tuning performed)

- The frozen V2.2 contract measures semantic misalignment between gold criterion and SUT output (M1), critical-condition evidence ambiguity (M2), and control dimensions. The dominant cross-candidate failure is M2 ambiguity handling: every model collapses AMBIGUOUS_OR_CONFLICTING evidence toward a forced binary (deepseek: 1 forced TRIGGERED + 6 forced NOT_TRIGGERED; gold-UNRESOLVED correct rate 0.2143).
- deepseek-v4.1-flash is materially stronger on structure and safety-critical recall: only candidate with 100% structured-output validity, 100% evidence-span validity, 100% clear-critical accuracy, 0 critical FN. It failed no safety regression check. Its failures are calibration-type (forcing binary verdicts on ambiguous evidence) plus residual M1/controls accuracy.
- No safety-critical false accepts (forbidden PRESENT -> ABSENT or critical TRIGGERED -> NOT_TRIGGERED) occurred for any candidate.

## Boundaries preserved

- Burned V2.2 benchmark used for candidate comparison only; no tuning, no threshold changes, no prompt changes, no fixture reuse for anything fresh.
- LongCat: 0 calls, 0 probes, 0 aliases. GPT-5.5: not used. No OpenRouter candidates added.
- Historical lineages unchanged; V2_2_REFERENCE_MODEL_NOT_READY stands.
- Stability stage correctly skipped for non-qualifiers; no majority-vote repair anywhere.

## Terminal status

V2_3_NO_MODEL_QUALIFIES

Per the frozen spec, no next stage starts automatically: fresh judge validation on a new official set, model re-screening, prompt tuning, product integration, and product holdouts all require a separate explicit owner-authorized task.
