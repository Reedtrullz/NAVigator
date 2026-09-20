# ROUT-030 Analysis

Task: NAV-EXPLORE-POST-WAVE3-P0-RC04-BINDING-WAVE4-SCOPE-GATE-V1
Classification: BURNED_DEV_BASELINE_ONLY

## Question

ROUT-030 was flagged as a lateral transition within FAIL, not one of the 5 regression-inventory P0 rows. Verify and classify.

## Frozen facts

| Field | Wave 2 | Wave 3 |
| --- | --- | --- |
| routes | ["Hensikt"] (pseudo-route) | [] |
| no_route_asserted | false | true |
| critical_condition authority | LLM_REVIEWED (Astra dual-pass consensus) | DETERMINISTIC |
| critical_condition verdict | TRIGGERED | CRITICAL_ERROR |
| derivation basis (W2) | M2:CLEAR_TRIGGER_SUPPORT | n/a (deterministic) |
| state | FAIL | FAIL |

Gold condition: "no coordination pathway" (free text; not present in CRITICAL_CONDITION_MAP).

## Why it was flagged

The transition matrix lists ROUT-030 among verdict changes (TRIGGERED -> CRITICAL_ERROR) with identical FAIL state on both sides. The regression-inventory definition ("strictly worse semantic state") excludes it; FAIL -> FAIL cannot be a regression regardless of verdict label.

## Did product behavior materially worsen?

No. Both waves score state FAIL. Wave 2 found clear trigger support (no coordination pathway asserted) via the semantic lane; Wave 3 fires generic R3 (PREMATURE_ABSENCE) deterministically. The verdict labels differ because the observation mechanism changed (LLM_REVIEWED -> DETERMINISTIC), not because the product became worse. The W3 output again reflects honest absence after pseudo-route suppression, the same mechanism as the five inventory P0s.

## Classification

\`NOT_A_REGRESSION\`. ROUT-030 must not inflate the P0 count. It is retained in the case registry of p0-regression-diagnosis.json for traceability only.

