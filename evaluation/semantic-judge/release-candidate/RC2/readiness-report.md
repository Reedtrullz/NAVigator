# RC2 Readiness Report

Verdict: RC2_READY_FOR_NEW_BLIND_SET

This is the maximum permitted claim. RC2 is NOT certified. No new blind evaluation has been run. RC1 remains NOT_CERTIFIED permanently.

## Gate Evidence (development set, 120 burned rows tagged BURNED_BLIND_V1_DEVELOPMENT_ONLY)

| Gate | Result | Source |
|---|---|---|
| RC2 regressions | 37/37 (run twice, identical output) | regressions/run_regression.py |
| Tier1 unit tests | 43/43 | phase-a-gates.json |
| Operator regression | 23/23 | phase-a-gates.json |
| KB baseline (score_baseline.py) | 48/48 BESTATT | phase-a-gates.json |
| id_guard (engine/ + fusion.py) | 0 case-ID references | grep audit |
| qa_check.sh | PASS | phase-a-gates.json |
| Engine-layer semantic fixes | 42 to 52 correct, 10 fixed, 0 regressed | before-after-results.json |
| Fusion auto precision | 13/13 on blind-shadow autos, 0 false autos, 0 critical false autos | burned-v1-shadow-results.json |
| Reproducibility | run_before_after_and_shadow.py run twice; byte-identical output | this report |
| RC1 parity check | RC1 column reproduces official 79/79/44 exactly | burned-v1-shadow-results.json |

## What Changed

- Engine: year-word age-range regex (law citations no longer parsed as ages), qualifier-set equality, same-subject attestation skip, newline phrase boundary, set-iteration fix.
- Fusion (RC2-FUSION-V1): auto-accept reviewer SUPPORT >= 0.90 only when no specific-defect gate reason is present. No CONTRA or PARTIAL auto-accept on any path.

## Known Trade-off

Strict-scorer fused shadow: 63 semantic / 24 product / 28 proof-safe vs RC1 official 79/79/44. This is the cost of the conservative no-false-autos policy: 13 autos instead of 75, 107 routed to review. RC1 achieved its 79/79 by accepting 5 critical false autos; RC2 development gates show 0.

## Deferred

- Compound atom-recall: decomposition repair alone recovered only 6/30; atom support-recall is the binding constraint (compound-audit.md).
- Label sensitivities on rows 0116/0165 (label side, not engine side).

## Constraints Honored

RC1 artifacts untouched. No new blind set. No live dialog. No KB tuning. No case-ID runtime code (id_guard 0). No GPT-5.5 subagents. Burned usage tagged BURNED_BLIND_V1_DEVELOPMENT_ONLY.

