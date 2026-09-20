# Review annotation + Tier-2 value assessment

Task: SEMANTIC-JUDGE-REVIEW-ANNOTATION-TIER2-ASSESSMENT (additive metadata only; no implementation).

## Files

- TASK-LOCK.json - task lock; ACTIVE during work, COMPLETED at end (spec 35 checklist)
- README.md - this inventory
- review-final-manifest.json - the 21 remaining review finals derived from frozen tier1-proof/results/gate-results.json (30 review finals total; 9 already dual-labelled in Tier-1)
- annotation-pass1.json - codex-first-hand dual-target annotations, 21/21, contract-driven, span-strict
- annotation-pass2.json - gpt-5.6-luna x3 independent second pass (neutral case numbers 1-21, no pass-1 access); thread IDs in pass2-thread-ids.txt
- annotation-disagreements.md - per-case adjudication log (statuses per spec 7; 0 unresolved disputes)
- review-final-dual-labels.json - final adjudicated labels (the triple contract: semantic truth, proof-safe verdict, product expected action)
- tier2-case-mapping.json - mapped cases with premises/preconditions/risk + unmapped operator needs (report-only)
- tier2-value-analysis.md - audit of all 9 SAFE_WITH_PRECONDITIONS operators, pool-of-28 audit, dedup, safety weighting, canaries
- tier2-headroom.json - current metrics, theoretical vs realistic headroom, per-100 rates, threshold check
- decision.md - GO/NO-GO: SKIP_TIER2_AND_PREPARE_BLIND_RECERTIFICATION
- final-report.md - 62-point report (spec SLUTTRAPPORT)

## Provenance

- Gate data: ../tier1-proof/results/gate-results.json (frozen, unmodified; 389 rows, 4 duplicated IDs across sets)
- Claims/evidence: ../tier1-proof/results/claims-map.json (frozen, unmodified)
- Operator catalog: ../evaluation-contract/operator-classification.json (9 SAFE_WITH_PRECONDITIONS; none implemented)
