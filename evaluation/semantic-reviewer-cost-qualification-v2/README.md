# Semantic Reviewer Cost Qualification V2

Task: NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V2
Terminal status: **NO_LOW_COST_MODEL_QUALIFIES_V2**

Second bounded qualification attempt over the frozen V1 benchmark lineage
(contract a27523ea...cd073f, unchanged gates, unchanged reference corpus).
Owner authorization: attachment d5ea8aa6-32bd-4bd5-a01f-1fcabd210265.

## Outcome

| Candidate | Route | Transport | Screening forbidden | Screening critical | Verdict |
|---|---|---|---|---|---|
| R1 nemotron-3-super | none | NOT_TESTABLE_NO_ROUTE | not screened | not screened | eliminated (no route) |
| R2 laguna-s-2.1 | command-code/poolside/laguna-s-2.1-free | provisional (27 x 5xx, recovered) | schema 0.8302 < 1.0 | schema 0.8919 < 1.0, 4 escapes | ELIMINATED |
| R3 ling-3.0-flash-sante | command-code/inclusionai/ling-3.0-flash-sante:free | 48 x 429 during screening | schema 0.9623 < 1.0 | schema 0.3514 < 1.0 | ELIMINATED |
| R4 gemma-4-26b-a4b-it | openrouter/google/gemma-4-26b-a4b-it:free | chronic 429 (38 events) | not screened | not screened | operationally disqualified |
| R5 inkling-small | openrouter/thinkingmachines/inkling-small:free | hard 403 (19/19) | not screened | not screened | operationally disqualified |

Zero survivors. Stage 2 (dual pass), stability, cascade simulation and
router proposal were never started; those stages are reserved for
screening survivors by the frozen spec.

## Key files

- final-report.md — full 39-point terminal report
- screening-scored-v2.json — frozen gate scoring
- semantic-screen-results.json — frozen blind screening outputs (90 rows x 2 candidates, full raw)
- disagreement-analysis.json — invalid-reason and field-level disagreement patterns
- cost-analysis.json — token, latency, retry and HTTP-error accounting
- transport-screen-results.json + transport-freeze-manifest.json — frozen transport calibration
- nex-v1-invalid-analysis.json — why the V1 near-miss was NOT retested
- input-integrity.json — 9/9 V1 pins verified (re-verified after screening)
- hashes.txt — SHA-256 inventory of all V2 artifacts

## Non-claims

This result is a qualification screening outcome, not a claim about the
models' general capability. The V1 reference is the frozen authoritative
semantic reference, not human ground truth. No SUT, gold, runtime or
router changes were made. No fresh cases were consumed.
