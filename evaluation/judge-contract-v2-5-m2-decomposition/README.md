# judge-contract-v2-5-m2-decomposition

Task: `NAV-EXPLORE-JUDGE-CONTRACT-V2_5-M2-EVIDENCE-STATE-DECOMPOSITION`

Owner-authorized R&D lineage (2026-09-13) decomposing the V2.2 M2 five-value
evidence-state intermediate field into independent sub-fields, with
deterministic derivation to the unchanged final semantic verdict.

Scope and hard locks: see `TASK-LOCK.json`. Baseline integrity Gate 1:
see `baseline-integrity.json` (PASS, 15/15 anchors matched; one handoff
transcription error on the V1.6B anchor documented in-place).

Frozen anchors from V2.2, V2.3, V2.4, and V1.6B are authoritative. The V2.4
12-model screening draft (`judge-selection-v2-4-draft/`, SHA `44c269c6...0ec1`)
remains NOT authorized and untouched.

## Terminal status (2026-09-13)

`V2_5_REFERENCE_MODEL_CANNOT_USE_DECOMPOSITION`

Human annotatability passed in full (60 fixtures, all agreement gates 1.0), but
DeepSeek-v4.1-flash failed calibration within the two allowed prompt iterations
(derived-final 0.500 -> 0.833; gate >= 0.95; critical FN 1; conflict field 0.765).
Per spec sections 23/40/43 this is a hard stop. Official validation, stability,
and evaluator freeze were not reached and no such artifacts exist.

Key artifacts: `final-report.md`, `error-attribution.json`,
`calibration-summary-v2-5-iter0.json`, `calibration-summary-v2-5-iter1.json`,
`calibration-artifact-shas.json`.
