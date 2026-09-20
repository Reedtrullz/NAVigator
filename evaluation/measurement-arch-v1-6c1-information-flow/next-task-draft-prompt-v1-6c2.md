# NY OPPGAVE - JUDGE SELECTION V2 (M1/M2/M3 SUB-SKILLS)

## Calibrated non-commitment + compound uncertainty + paraphrase equivalence

DRAFT TASK PROMPT - NOT YET AUTHORIZED. Do not execute until Reidar
explicitly issues or approves this task.

## TASK ID

NAV-EXPLORE-JUDGE-SELECTION-V2-SUBSKILL-SCREENING

Arbeidsmappe: /Users/reidar/Projectos/NAV Explore
Output dir: evaluation/judge-selection-v2-subskill/

Subagenter: maks 2, kun from AGENTS.md allowed list (f.eks.
command-code/xiaomi-mimo-v2.5-pro), ingen GPT-5.5, ingen silent escalation.

## BAKGRUNN (IMMUTABLE TERMINAL STATES)

- V1_6B_NO_JUDGE_QUALIFIES (combined screening failed both candidates)
- V1_6A4_NOT_READY (assertion-strength boundary expansion falsified,
  0.368 fresh precision vs >=0.99; further boundary expansion banned
  without new authorization)
- V1_6C1_INFORMATION_FLOW_NOT_SUPPORTED (packet repair: NEW 78/92 vs
  OLD 79/92; uncertainty regression -7.1 pp; route-only positive signal)

Diagnose (failure-cluster-root-cause.md, burned data): residual failures
are judge-capacity failures - M1 critical abstention recall, M2 compound
uncertainty PARTIAL, M3 forbidden paraphrase equivalence. A3 abstains on
13/14 residual rows. Abstention precision is already high.

## SCOPE

### 1. Fresh fixture families (frozen before any model call)

Three families, minimum 24 fixtures each, authored fresh (no text reuse
from burned V1.6B, C1 A/B rows, V1.2 official, or calibration sets):

A. Critical UNRESOLVED-disposition: ambiguous safety-adjacent answers
   where neither TRIGGERED nor NOT_TRIGGERED is warranted; include hedged
   near-miss controls where TRIGGERED/NOT_TRIGGERED IS warranted
   (protects against abstain-everything cheating).
B. Compound uncertainty: EXPRESSION + NON_ASSERTION combos; gold spans
   SATISFIED / PARTIAL / VIOLATED / UNRESOLVED; include single-constraint
   controls.
C. Forbidden paraphrase equivalence: paraphrased/hedged/subject-shifted
   forbidden claims (gold PRESENT) plus non-equivalent claims (gold
   ABSENT).

Dual-pass human labeling with agreement gates (>=95% overall, per-family
>=90%) BEFORE model calls. Disputed fixtures before gold freeze: DISCARD
and replace with new fixtures; never repair in place. Freeze gold + SHA.

### 2. One-shot model screening (frozen prompt/config per candidate)

Same frozen V1.6B gate architecture. Candidates only from AGENTS.md
allowed list; identical prompts/config across candidates; no
threshold tuning; technical retry policy frozen up front.

Gates per family: accuracy >= 0.90, zero critical FN (family A),
zero safety-critical forbidden FN (family C), abstention precision
>= 0.95 on rows where the model abstains. No best-of-bad: if no
candidate qualifies, terminal status is
JUDGE_SELECTION_V2_NO_JUDGE_QUALIFIES.

### 3. Stability (only for the top qualifying candidate)

5 runs x 24 fixtures on all three families; modal stability >= 0.95
overall and per family; instability disqualifies, no majority-vote
repair.

### 4. Terminal statuses (exactly one)

- JUDGE_SELECTION_V2_QUALIFIED (all gates + stability pass; candidate
  frozen with manifest, ready for C2 design as a SEPARATE task)
- JUDGE_SELECTION_V2_NO_JUDGE_QUALIFIES
- JUDGE_SELECTION_V2_ANNOTATION_CONTRACT_NOT_READY
- JUDGE_SELECTION_V2_INVALID (protocol violation/contamination)

## DELIVERABLES

evaluation/judge-selection-v2-subskill/
  TASK-LOCK.json, README.md, baseline-integrity.json,
  fixture-families-a-b-c.json, human-label-pass1.json,
  human-label-pass2.json, annotation-agreement.json,
  judge-selection-gold.json (frozen, SHA),
  screening-results-<model>.json, screening-comparison.json,
  stability-results.json (if any qualify), final-report.md

## IKKE I DENNE TASKEN

Ingen boundary-utviding (A4-forbodet staar). Ingen lexical fallback.
Ingen packet-reintroduksjon for non-route-dimensjonar. Ingen C2 og ingen
combined scorer freeze (kjem som separat task berre etter QUALIFIED).
Ingen full SUT, ingen produktendringar, ingen fresh product holdout.
Ingen result-driven reruns.
