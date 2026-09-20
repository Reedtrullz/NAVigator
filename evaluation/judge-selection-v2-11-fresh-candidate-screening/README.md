# V2.11 - Fresh candidate screening (execution lineage)

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_11-FRESH-CANDIDATE-SCREENING

Authorized by the 2026-09-14 AFK measurement-system campaign (Stage 1).
Candidates: ling-3.0-flash-sante, laguna-s-2.1. No LongCat, no GPT-5.5.

Frozen spec: evaluation/judge-selection-v2-11-draft/TASK-SPEC-DRAFT.md
(sha256 b04e96219095f6ed7cb6525a7789adf9486d5633d026cede50ee193d5580df23).

Process repairs vs V2.10 (from frozen spec):
1. dual-pass annotated calibration gold, machine-checked via frozen derive_final,
2. preregistered prompt-sensitivity probe before burning iterations,
3. honest separate reporting of automated judge accuracy vs human-reviewed coverage.

Screening set: frozen V2.10 official 180-row set reused (zero prior model
exposure = freshness provenance). Calibration set: 25 new burned fixtures.

Hard stop at terminal status.
