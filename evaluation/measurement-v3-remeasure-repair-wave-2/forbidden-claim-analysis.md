# Forbidden-Claim Analysis - Wave 2

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-2 combined measurement results and primary/residual consensus artifacts.

## Totals

- Forbidden criteria: 120. Authoritative: 119. PENDING: 1 (ROUT-026 forbidden:01 - Sol dual-pass disagreement; no resampling permitted).
- Verdict distribution W2: ABSENT 57, CLAIM_ABSENT_TAKEN 59, PRESENT 1, CLAIM_PRESENT 2.
- Verdict distribution W1: ABSENT 63, CLAIM_ABSENT_TAKEN 48, PRESENT 2, CLAIM_PRESENT 3, 4 pending.
- Forbidden FAILs: W1 5 -> W2 3.

## Remaining FAILs (3)

1. DIS-100 - PRESENT (LLM_REVIEWED, dual-pass Astra consensus). Contamination-shaped: "Fant ingen registrerte kommunale tilbud..." appears inside cross-contaminated national-information blocks. Also failed in Wave 1. Classification: contamination-related product assertion.
2. DIS-119 - CLAIM_PRESENT (DETERMINISTIC lexical). Unchanged from Wave 1. Classification: true product assertion by deterministic lexical match; negation/measurement sensitivity cannot be fully excluded for a lexical matcher, but the deterministic lane is unchanged and not LLM-sensitive.
3. ROUT-042 - CLAIM_PRESENT (DETERMINISTIC lexical). Unchanged from Wave 1. Same classification as DIS-119.

## Contamination-shaped vs true assertions vs measurement sensitivity

- Contamination-related remaining: DIS-100 only.
- True product assertions: DIS-119, ROUT-042 (unchanged deterministic lexical findings).
- Negation/measurement sensitivity: the two deterministic lexical FAILs are candidate cases where a negated claim could be matched as present; the frozen Measurement V3 lexical lane cannot distinguish these without semantic review, and no semantic packet failed on them. No Measurement change is made here.

## Improvement attributable to RC-08 retrieval scoping

- DIS-105: CLAIM_PRESENT -> CLAIM_ABSENT_TAKEN (FAIL -> PASS, deterministic).
- DIS-116: FAIL -> PASS (deterministic).
Both are consistent with reduced cross-track retrieval leakage reaching the answer surface. The 4 Wave-1 pending forbidden criteria resolved authoritatively in Wave 2: 2 -> ABSENT, 1 -> CLAIM_ABSENT_TAKEN, 1 remains pending (ROUT-026).

## Verdict

Forbidden-lane failures fell from 5 to 3. One residual failure is contamination-shaped; two are unchanged deterministic findings. RC-08 helped this lane; it did not eliminate contamination (DIS-100 persists) and did not touch the deterministic lexical boundary.
