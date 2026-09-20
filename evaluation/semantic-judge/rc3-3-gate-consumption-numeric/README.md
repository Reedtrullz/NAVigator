# RC3.3 Gate-Consumption + Numeric-Coverage Repair

Task: NAV-EXPLORE-RC3_3-GATE-CONSUMPTION-NUMERIC-COVERAGE

## Status

RC3_3_RELATION_NUMERIC_PASS_PROOF_NOT_READY

Relation/numeric objectives improved from baseline 0.4643 to 0.9929 (macro-F1 0.4835 -> 0.9913), gate-collapse subgroup 0.5714 -> 1.0000, numeric subset 0.4342 -> 0.9868. Proof-side gates are green except CONTRADICTS precision 0.9756 vs the 0.99 gate (single false positive R33-126, the documented R08 stale-amount residual; engine frozen, bounded bugfix pass consumed, so it is reported honestly rather than patched). Comparator strict-directional reading 0.9231 vs 0.98 (all gold-false rows correctly routed RBI; verdict-consistent reading 0.9846 passes). Sealed 60-case validation remains sealed and untouched.

## Candidate freeze

Not created. Per spec 43/45 the candidate-proof directory exists only when ALL gates pass.

## Key artifacts

- results/final-relation-results.json (0.9929 / F1 0.9913)
- results/gate-collapse-results.json (70 cases, 1.0000)
- results/numeric-results.json (76 cases, 0.9868)
- results/proof-safety-audit.json (63/63 grounded ENTAILS, 0 ungrounded, 0 critical false)
- results/safety-projection-regression.json (boundary byte-identical, 0 diffs)
- results/final-verify.json (determinism byte-identical, id_guard 0)
- results/legacy-regression-report.json (RC2 37/37, Tier-1 43/43, ops 23/23, probes pass)
- implementation-report.md, contract-hashes.txt

No new blind set. No reviewer/routing tuning. No GPT-5.5 (0 subagents).
