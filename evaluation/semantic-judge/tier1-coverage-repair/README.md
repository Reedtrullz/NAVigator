# Tier-1 coverage repair (SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR)

Final runtime repair round before blind re-sertifisering. Audited all 7
SHOULD_ALREADY_AUTO_DECIDE cases, repaired general lexer/lexicon/
actor/eligibility bugs in one implementation pass, verified zero safety
regression, and froze the runtime as NAV-EXPLORE-EVALUATOR-RC1.

| File | Content |
|---|---|
| TASK-LOCK.json | Task lock (COMPLETED, all forbidden tasks confirmed not performed) |
| known-coverage-gaps.json | The exactly-7 gaps with claims, evidence, labels, expected path, review reason |
| bug-taxonomy.md | Root-cause classification per case + fix mapping |
| coverage-fix-spec.md | The 9 general fixes (F1-F9) with near-miss design and deliberate non-fixes |
| implementation-report.md | Files/lines changed, single-pass compliance |
| before-after-metrics.json | Spec 17 metric pairs (auto/review/necessary/unnecessary/invalid/unsafe) |
| regression-results.json | Full QA battery results + canary states |
| final-report.md | All 58 SLUTTRAPPORT points |

## Outcome

- 3 x FIXED_SAFE_AUTO: CAL011, CAL014 (DIRECT_ASSERTION), CAL034
  (NUMERIC_CONFLICT on exclusion thresholds).
- 4 x REMAINS_REVIEW_BY_DESIGN: HOL006, HOL014, LOC-13, MOD-14 (fixes
  would require new inference doctrine or trade away load-bearing
  safety guards).
- Auto decisions 121 -> 122; review finals 27 -> 27; invalid accepted
  proofs 3 -> 0; unsafe auto 0 before and after.
- RC1 frozen in ../release-candidate/ (17 hashed files); verdict
  READY_TO_BUILD_BLIND_RECERTIFICATION_SET.

Rerun the gate with: python3 tier1-proof/run_gate.py (from
evaluation/semantic-judge/).
