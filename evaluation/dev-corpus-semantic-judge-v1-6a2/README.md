# V1.6A.2 - Route-Grounding Repair

Terminal status: V1_6A2_FRESH_CONFIRMATION_NOT_READY

Clause-level route grounding repair for the boundary pre-classifier. New
lineage; V1.6A and V1.6A.1 are immutable.

## What was built
- Clause segmentation + per-clause operator/noun association (BC_ROUTE_CLAUSE_LOCALITY_01)
- Ambiguous grounding guard (BC_ROUTE_AMBIGUOUS_02)
- Correction binding for retractions across adjacent clauses
- Mixed-polarity guard extended to HYPOTHETICAL_ONLY (DEV-02 bounded bugfix)
- Quote-span suppression of assertion markers inside guillemets

## Verification
- TDD: 17/17 (genuine RED on TDD-CROSS-07 before fix)
- Unit: 72/72
- Burned-120: precision 1.0, 0 false deterministics, all gates PASS
- Burned-60: precision 1.0, ADV-11 now abstains (root cause repaired)
- Official 80-fixture one-shot: FAILED (precision 0.7027 < 0.99 gate)

## Why it stopped
11 false deterministics on the fresh official set. 7 genuine engine gaps
(quote scope, parenthetical, single-candidate mixed polarity, hedge
competition, negation-in-antecedent) + 4 gold-curation boundary disagreements.
Per contract section 49: no post-execution patch, candidate not frozen,
V1.6B remains blocked.

## Key artifacts
- final-report.md (all 66 contract items)
- official-validation-results.json (per-fixture results)
- official-fixture-hashes.json (frozen fixture + engine SHAs)
- process-deviations.md (V1.6A.1 permanent record + DEV-02)
- root-cause-trace.json, repair-hypothesis.md

## Next bounded stage
Contract-derived repair of the 7 gaps, then fresh official 80 -> one-shot ->
gate evaluation. See final-report.md item 66.

