# Certification Metrics - RC2 Blind V3

Pre-registered 2026-09-04, BEFORE the certification run and unchanged at seal (spec 39-40). Thresholds are the already-planned V2 thresholds, unmodified.

## Gates (Phase 2 scoring, spec 39)

| Metric | Threshold |
|---|---|
| Semantic accuracy | >= 90% |
| Proof-safe accuracy | >= 95% |
| Product accuracy | >= 95% |
| Auto precision | >= 99% |
| Critical product | 100% |
| Invalid accepted proofs | 0 |
| Hallucinated proofs | 0 |
| Critical unsafe autos | 0 |
| Runtime exceptions | any occurrence = FAIL |
| Compound atom | >= 90% |
| Compound product | >= 90% |

No threshold may change after seal (spec 40). A change would invalidate the certification, not repair it.

## Coverage disclosure (affects interpretation, not thresholds)

1. The sealed key carries full atom rows only for adjudicated cases (10 of 160 CORE; pass-agreed and single-atom cases carry the triple + flags only, per the key note). Compound-atom scoring is therefore computed over available atom rows, and compound cases without atom rows fall back to triple-level evaluation. Any protocol change needed for Phase 1 must be amended BEFORE that run, never after scoring.
2. Criticality is not a separately pre-registered field in the V3 key structure. Critical-product and critical-unsafe metrics must therefore derive from case content (safety/legal/age_legal flags and claim text) under the same pre-registered thresholds; if a criticality annotation pass is wanted, it must be added as a pre-Phase-1 amendment.
3. Operator (required-inference) agreement was not separately measured during construction (see final report item 38). Spec 28 makes this an audit trigger below 80%, not a hard gate; the gap is disclosed rather than backfilled.
