# V2.3 Stronger-Model Screening

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN
Terminal status: V2_3_NO_MODEL_QUALIFIES

One-shot screening of four owner-authorized candidates against the burned
V2.2 120-row benchmark under the frozen V2.2 contract scoring. No candidate
passed all section-5 gates; deepseek-v4.1-flash was closest (overall 0.8333,
all structure/safety gates passed) but failed overall/M1/M2-ambiguity/controls.
No stability stage was eligible to run. See final-report.md.

Key artifacts:

- TASK-LOCK.json - authorization, candidate freeze, terminal status
- screening-benchmark-reference.json - burned benchmark hashes
- transport-verification.json - deepseek conditional gate PASS
- screen-<candidate>.json - raw one-shot results
- gate-extraction-<candidate>.json - mechanical gate verdicts
- candidate-comparison.json - frozen comparison (before selection)
- security-secret-audit.json - PASS
- final-report.md - full outcome and boundaries
