# Diagnostic Basis (burned-data only)

Source: evaluation/judge-selection-v2-8-non-m2-post-repair/final-report.md,
post-terminal addendum (2026-09-13). This file restates the finding for draft
self-containment; the V2.8 report remains authoritative.

Finding: both V2.8 candidates failed the frozen gates primarily through
overcommitment on contract-mandated UNRESOLVED boundaries.

- DeepSeek (opencode-go/deepseek-v4.1-flash): 12 misses, 9 gold-UNRESOLVED
  committed to definite verdicts, 1 undercommitment.
- MiMo Pro (command-code/xiaomi/mimo-v2.5-pro): 14 misses, 9
  gold-UNRESOLVED committed to definite verdicts, 0 undercommitment.

Hypothesis (not proven): shared directional calibration bias, not random
variance. Model capability did not separate the candidates on this axis.

Design consequence preregistered in TASK-SPEC-DRAFT.md section 5:
UNRESOLVED-forcing signals are first-class prompt/arbitration requirements,
and the fresh benchmark must include at least 20 overcommitment-trap
uncertainty fixtures. The overcommitment metric is report-only in V2.9; the
gate set is unchanged from frozen V2.8.

Status marker: BURNED_DATA_DIAGNOSTIC_ONLY. Not generalization evidence.
