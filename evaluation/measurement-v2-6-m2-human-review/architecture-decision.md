# Architecture Decision: M2 Human Review Lane (V2.6)

## Summary

V2.6 replaces automated authoritative M2 critical-condition judgement with an explicit human-review lane in the NAV Explore measurement system, while preserving automation for all non-M2 semantic dimensions and the deterministic scorer.

## Prior state

- V2.5 terminal: V2_5_REFERENCE_MODEL_CANNOT_USE_DECOMPOSITION (spec sections 23/43 hard stop).
- Root evidence: human decomposition contract sound (60/60, agreement 1.0); DeepSeek-v4.1-flash derived-final 0.500 then 0.833 vs gate >=0.95; critical FN 1 in both iterations; conflict under-reporting persisted; no derivation-table defects; no official 120 validation reached; no evaluator frozen.

## New evaluator flow

```
SUT OUTPUT
    |
existing deterministic scorer
    |
dimension?
    |-- M2 / critical_condition semantic judgement
    |       -> HUMAN_REVIEW_REQUIRED
    |       -> human review packet (blind: no gold, no model verdict)
    |       -> human intermediate labels
    |       -> deterministic final derivation (frozen table)
    |
    \-- non-M2 semantic dimension
            -> automated semantic judge lane (selected/validated separately)
```

## First-class measurement states

- HUMAN_REVIEW_REQUIRED: criterion intentionally outside automated evaluator boundary.
- HUMAN_REVIEW_PENDING: packet exists, no valid review yet. Fail-closed; never auto-pass.
- HUMAN_REVIEW_INVALID: review failed validation; criterion remains unadjudicated.
- HUMAN_REVIEW_DISAGREEMENT: dual reviews differ; requires adjudication; no majority vote.
- HUMAN_REVIEW_RESOLVED: final label mechanically derived from human intermediate labels.

## What did NOT change

- V2.5 semantic meaning, labels, and derivation table (SHA-pinned in m2-contract-pins.json).
- Non-M2 automated judge responsibilities and scoring.
- Product runtime, product safety behavior, emergency handling.
- The 12-model V2.4 draft remains NOT_OWNER_AUTHORIZED; LongCat remains excluded.

## Metrics consequences

- AUTOMATED_SCORING_COVERAGE is reported explicitly; M2 semantic coverage is 0% authoritative automated while this architecture holds (intended).
- Human-reviewed, automatically-scored, unresolved, and execution-failed buckets are always reported separately; blended single-accuracy reporting is forbidden.
- Critical-condition performance is reported as HUMAN_REVIEW_M2, never as model safety accuracy.

## Evidence for this decision

See ADR-M2-HUMAN-REVIEW.md and evaluation/judge-contract-v2-5-m2-decomposition/final-report.md (SHA dac98cbd prefix, recorded in V2.5 lineage).

## Status

ACTIVE; terminal status will be recorded in final-report.md per spec section 40.
