# Judge Contract V2.2 — Two-Mechanism Operationalization

Task: NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION
Prior status: V2_1_NO_JUDGE_QUALIFIES. Owner-authorized 2026-09-12.

## What this task changes

After V2.1 showed all authorized candidates failing the same seven rows, this
task operationalizes the two shared failure mechanisms as explicit intermediate
model decisions with deterministic code-derived final verdicts:

- M1: hedged positive assertion remains an evaluable assertion
  (criterion_semantic_match + speaker_commitment -> PRESENT by code).
- M2: critical ambiguity abstains to UNRESOLVED by code
  (critical_evidence_state -> UNRESOLVED when not safely decidable).

No semantic meaning, label set, or gold changes. Frozen V1.4 semantics are
preserved exactly; only the decision procedure, output schema, and derivation
authority change.

## Pipeline

1. Baseline integrity (done): 17 frozen artifacts SHA-verified, 0 historical
   writes. See baseline-integrity.json.
2. Frozen semantics trace (done): both mechanisms proven from frozen V1.4.
3. Mechanism analysis (done): seven burned rows classified as diagnostic data.
4. Intermediate contracts + deterministic derivation tables (drafted; frozen
   after calibration).
5. 48 fresh calibration fixtures (24 M1 / 24 M2), max 2 prompt/schema
   clarification iterations, reference model command-code/xiaomi/mimo-v2.5-pro
   only. LongCat excluded (0 calls/probes/aliases).
6. 120 fresh official fixtures (40 M1 / 40 M2 / 40 controls), collision audit,
   dual curation passes, gold freeze, one-shot reference validation.
7. Gates per spec; terminal status; burned-seven retrospective (non-scoring,
   after score freeze).

## Hard rules

- No LongCat. No stronger-model screening inside this task.
- No case-ID logic in runtime. Burned rows used for diagnosis only.
- AMBIGUOUS_CRITICAL_FORCED_BINARY = 0. UNRESOLVED is first-class.
- Evidence spans mechanically validated (100%).
- Deterministic derivation consistency 1.0; model free-choice final verdict
  has no authority.

## Terminal outcome (2026-09-12)

Official one-shot validation completed 120/120: overall 0.7917 (95/120),
M1 0.90, M2 0.675, controls 0.80, valid-structured 0.975, derivation
consistency 1.0. Human/curation verdict agreement was 1.0 in all families,
so gold quality is not the confound: the residual failure profile is model
capability against a mechanically enforced contract.

Hard-zero breaches: 8 ambiguous-critical cases forced NOT_TRIGGERED,
1 forced TRIGGERED, 1 critical false negative (schema-failure run),
2 fabricated evidence spans caught by the validator, 1 non-retried HTTP 400.
The M1 hedge hard-zeros held (0 false ABSENT / 0 false UNRESOLVED, N=7).

Burned-seven retrospective (non-scoring, post-freeze): 4/7 historical
mechanisms repaired; A-13/A-18/A-23 still forced-binary.

STATUS: V2_2_REFERENCE_MODEL_NOT_READY.

STOP per spec section 45: no stronger-model screening, no contract or prompt
changes, no fresh fixtures, no Phase B, no product runtime work. The next
direction (V2_3 stronger-model screen) requires owner authorization.
