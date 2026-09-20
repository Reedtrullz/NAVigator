# dev-corpus-semantic-judge-v1-6a1

Task: `NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A1-ABSTAIN-REPAIR`

Terminal status: **`V1_6A1_TARGETED_CONFIRMATION_NOT_READY`**

New-lineage generalized repair of the V1.6A out-of-inventory service-noun
abstain gap (`VR-H-08` class). The repair itself is sound on all development
data (72/72 unit, burned-120 precision 1.0, 0 false deterministics) but failed
the fresh 60-fixture targeted confirmation gate on one adversarial fixture
(`ADV-11`, cross-noun sentence resolution). Candidate NOT frozen; no manifest.

Entry points:

- `final-report.md` — 52-item closure report
- `TASK-LOCK.json` — scope, prohibitions, terminal status
- `repair-hypothesis.md` — frozen pre-implementation hypothesis
- `targeted-validation-results.json` + `precision-coverage-report.json` — official one-shot evidence

V1.6A history (`../dev-corpus-semantic-judge-v1-6a/`) is immutable and remains
`V1_6A_BOUNDARY_PRECLASSIFIER_NOT_READY`.
