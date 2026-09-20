# Release candidate NAV-EXPLORE-EVALUATOR-RC1

Frozen evaluator runtime after the SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR
single implementation pass. RC1 is the exact artifact that the upcoming
blind recertification set must test (spec 31): same hashes, no
modifications.

| File | Content |
|---|---|
| RC1-manifest.json | Component versions, contract reference, SHA-256 hashes of all runtime + contract files |
| hashes.txt | Plain sha256sum-format list mirroring the manifest |
| readiness-report.md | Spec 27 readiness verdict with per-gate evidence |

Freeze rules (spec 26): no tuning of any hashed component before blind
recertification results exist. If certification fails, RC1 results are
preserved and the next runtime is RC2 - never edit RC1 in place.
