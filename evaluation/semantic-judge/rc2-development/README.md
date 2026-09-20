# RC2 Development Directory (NAV-EXPLORE-RC2-ROOT-CAUSE-REPAIR)

Root-cause repair after RC1_NOT_CERTIFIED. Everything here is
development-only; the burned Blind V1 is marked
BURNED_BLIND_V1_DEVELOPMENT_ONLY everywhere it is used.

## Layout

- TASK-LOCK.json - task identity + constraints
- engine/ - RC2 candidate engine (RC1 copies + Iteration A fixes)
- fusion.py - frozen RC2 fusion policy (Iteration B)
- regressions/ - generalized regression suite (37 cases)
- run_phase_a_gates.py / phase-a-gates.json - engine-correctness gates
- run_phase_b_band_analysis.py / phase-b-band-results.json - band +
  labeled battery
- run_compound_audit.py / compound-audit.json - compound taxonomy
- run_before_after_and_shadow.py - before/after + RC2_BURNED_V1_SHADOW
- partial-band-analysis.md, fusion-calibration.json - fusion evidence
- compound-audit.md, age-parser-audit.md, numeric-binding-audit.md,
  runtime-bug-audit.md, proof-validity-vs-soundness.md,
  rc1-blind-postmortem.md - audits
- before-after-results.json, burned-v1-shadow-results.json - results
- final-report.md - SLUTTRAPPORT (items 1-66)

## Status

RC2_READY_FOR_NEW_BLIND_SET (development gates passed; no
certification claim; next step is a NEW blind set in a separate task).

