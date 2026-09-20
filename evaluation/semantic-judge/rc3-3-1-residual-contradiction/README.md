# RC3.3.1 Residual Contradiction + Comparator Contract

Task: NAV-EXPLORE-RC3_3_1-RESIDUAL-CONTRADICTION-COMPARATOR

Status: **RC3_3_1_RESIDUAL_REPAIR_NOT_READY** (engine work is green; the hidden
micro-validation one-shot was spent before the candidate freeze, which voids it
as a section-32 validation; the task therefore ends NOT READY by protocol).

Contents:

- comparator-metric-contract-v2.{md,json}, residual-repair-metrics.json - frozen metric contracts
- temporal-numeric-contract.md - TEMPORAL_NUMERIC_APPLICABILITY_V1 design
- fresh-targeted-cases.json - 90 cases (60 development / 30 hidden; hidden labels burned)
- implementation-report.md - main pass + the single bounded bugfix
- development-results.json (dev-60, all 1.0) / rc3-3-global-regression.json (global-140, all 1.0)
- proof-safety-audit.json, boundary-regression.json, results/legacy-regression-report.json
- results/micro-validation-premature-void.json + micro-validation-results.json - burned hidden run
- candidate-prevalidation/ - frozen pre-validation candidate (manifest SHA c66c14a6...)
- final-report.md - 68-point SLUTTRAPPORT + protocol deviation record

Subagent policy: GPT-5.6-Luna default for any subagent; GPT-5.5 forbidden; none used.
