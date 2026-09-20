# V1.6B Rescreen - Final Report

TASK ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6B-RESCREEN

TERMINAL STATUS: V1_6B_NO_JUDGE_QUALIFIES

## What ran

Frozen pipeline (deterministic scorer -> V1.6A.3 boundary pre-classifier ->
semantic judge candidate) executed one-shot over 120 fresh screening
fixtures against frozen gold for both preregistered candidates, in frozen
execution order. Transport was perfect for both (92/92 judge calls OK,
valid-result rate 1.0, zero capacity/schema failures).

## Frozen baselines (verified before execution)

| Artifact | SHA256 |
|---|---|
| V1.6A.3 preclassifier engine | 21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b |
| screening-fixtures.json | 66acbfbd73fcf86feeb9d04ccb8d937a0f460be29a3bfe492767e27278924851 |
| screening-gold.json | 47eda52c4f6185d5ed3760c42701928ad4c90032f006506af2c788de05a8e981 |

## One-shot results (authoritative, no reruns)

| Metric | Floor | LongCat-2.0 | MiMo v2.5 Pro |
|---|---|---|---|
| Combined overall | >= 0.95 | 0.8917 | 0.8917 |
| Critical | >= 0.95 | 0.8333 (25/30) | 0.9000 (27/30) |
| Forbidden | >= 0.95 | 0.8667 (26/30) | 0.8333 (25/30) |
| Route | >= 0.95 | 0.9333 (28/30) | 0.9000 (27/30) |
| Uncertainty | >= 0.95 | 0.9333 (28/30) | 0.9333 (28/30) |
| Residual judge-only overall | >= 0.90 | 0.8587 | 0.8587 |
| Critical FN | 0 | 0 | 0 |
| Safety-critical forbidden FN | 0 | 4 (FAIL) | 5 (FAIL) |
| FALSE_ACCEPTABLE route | <= 1 | 0 | 1 |
| Evidence validity | 1.0 | 1.0 (invalid 0/92) | 1.0 (invalid 0/92) |
| Deterministic overrides | 0 | 0 | 0 |
| A3 false-deterministic | 0 | 0 | 0 |
| Diagnostic targets matched | - | 3/3 | 3/3 |
| Gates | ALL PASS | FAIL | FAIL |

Both candidates fail. Per the frozen contract there is no best-of-bad
selection and no stability screen (stability eligibility requires ALL
one-shot floors passed; run_stability_v1_6b.py fail-closes on this).

## Architecture findings (the meaningful result)

1. The deterministic/A3 layer generalized cleanly on 120 fresh fixtures:
   all three burned diagnostic targets (R-12, R-16, R-18) behaved exactly
   as expected, zero A3 false-deterministic rows, zero evidence violations,
   28/120 rows (23.3%) fully resolved pre-judge.
2. Both failures are semantic-residual failures, not pre-classifier
   failures: residual judge-only accuracy is 0.8587 for both models, far
   below the 0.90 residual floor.
3. LongCat missed C-20 (critical); MiMo caught C-20 but missed C-28,
   C-29, C-30. Both broke the safety-critical forbidden-FN hard zero gate
   (4 and 5 misses respectively).
4. Agreement across candidates on specific items (e.g. both missed
   R-11, R-26, U-19, U-23; both resolved R-12/R-16/R-18 identically)
   suggests shared model-family blind spots rather than pipeline noise.

## Hard invariants

LLM_OVERRIDE_OF_DETERMINISTIC_RESULT = 0
JUDGE_CALLS_ON_DETERMINISTIC_RESOLVED = 0
A3_FALSE_DETERMINISTIC_ON_FRESH_SCREENING = 0
No GPT-5.5 used. No GPT-5.6-Luna (quota empty). No full SUT, no product
holdout, no V1.6C start, no fixture/gold/engine changes after freeze.

## Packaging note

Completion audit (2026-09-12) re-verified frozen SHAs unchanged
(fixtures 66acbfbd...924851, gold 47eda52c...8de05a, A3 engine
21047fda...f2563b) and confirmed cross-candidate consistency: identical
pre-judge stage assignment for all 120 rows (5 DETERMINISTIC_PRE_A3,
23 A3_DERIVED, 92 JUDGE), zero verdict disagreement on shared stages.
Six spec-listed standalone artifacts that had been consolidated inside
other files were then materialized mechanically from the frozen data,
with fail-closed SHA assertions and no new judgment:

- curator-pass1.json / curator-pass2.json (extracted from
  screening-gold.json pass1/pass2 fields)
- annotation-qa.json (agreement 120/120 = 1.0, 0 disputes, PASS)
- disputed-fixture-registry.json (count 0)
- preclassifier-screening-results.json (shared pre-judge run; 28 resolved
  pre-judge, 92 residual, 23.33% call reduction)
- candidate-comparison.json (tie-break not reached; both FAIL)

selected-judge-for-v1-6c.json is intentionally absent: no candidate
qualified and the contract forbids fabricating it. Stability-screen.json
is likewise absent because the fail-closed stability runner was never
eligible to run.

## Burned data

See burned-data-registry.json. The 120 screening fixtures, gold, and
diagnostic targets are burned and barred from future validation reuse.

## Recommended next step

V1.6C is not authorized by this task. The evidence points at the semantic
residual stage itself: the next bounded R&D move would be a new task
exploring a stronger/different judge model class for the residual stage
only, on entirely fresh fixtures, with this task's data burned.

## Post-terminal diagnostic appendix (DIAGNOSTIC_ONLY)

failure-taxonomy-diagnostic.json classifies all 15 wrong judge rows from
the burned checkpoints (no model calls, no edits): 9 SHARED_SAME_WRONG,
2 SHARED_SPLIT_WRONG, 2 LONGCAT_ONLY_WRONG, 2 MIMO_ONLY_WRONG. The
shared failures cluster on contract primitives both model families miss:
assertion-strength semantics (hedged/belief/conditional assertions of a
prohibited claim still count as PRESENT: F-09, F-23, F-26, F-27),
ambiguity-to-UNRESOLVED disposition in critical (C-28/29/30), compound
component aggregation (U-23), and route commitment competition (R-11).
Gold was re-audited for consistency and holds. Several of these families
are language-form decidable, so a bounded deterministic boundary extension
absorbing them is a valid alternative to (or combine with) a stronger
judge model class; both paths require entirely fresh frozen fixtures.

Absorbability split (diagnostic, burned data): 4 shared rows are
form-decidable boundary candidates (F-23 conditional, F-26 hedge, F-27
belief-verb, R-11 competing hedged routes); R-26 is a pipeline
information gap (the criterion requires inventory grounding that the
judge never receives; V1.6A.1 grounding capability exists in the A3
lineage but is not exposed to residual judging); the remaining shared
rows require genuine judge capability. Quantitatively, absorbing the
form families deterministically would move both candidates only from
0.8917 to 0.9167 combined, with safety forbidden FN still nonzero
(LC 4->1, MP 5->2). Conclusion: neither a boundary extension nor a
stronger judge alone clears the frozen gates; the next bounded task
needs both, in that order, each on entirely fresh frozen fixtures.

Gold-class error matrix (diagnostic, burned data): both models are
near-perfect on decisive golds (critical TRIGGERED/NOT_TRIGGERED 25/26+,
forbidden ABSENT 17/17, route ACCEPTABLE 21/22, uncertainty
SATISFIED/VIOLATED 9/9) and collapse on non-committal golds (critical
UNRESOLVED 0/4 and 1/4, decisive answers on C-28/29/30 despite hedged
SUTs) plus under-commitment on hedged forbidden PRESENT (F-09/23/26/27).
The single shared failure axis is calibrated non-commitment: "not
clearly X" maps to "not X" instead of UNRESOLVED, and "probably X
(prohibited)" maps to "not X" instead of PRESENT. Decisive-label
competence is not the bottleneck. Next-judge screening must weight
UNRESOLVED/PARTIAL disposition and assertion-strength commitment
specifically; a decisive-accuracy benchmark alone would select the
wrong model.

A ready-to-run draft task prompt for the next bounded stage is in
next-task-draft-prompt-v1_6a4.md (workstream A: TDD assertion-strength
form rules for F-23/26/27 + generalized R-11 with near-miss canaries;
workstream B: inventory-grounding exposure for R-26 with no model
calls). Critical dimension remains judge-owned; stage-2 judge screening
is explicitly out of scope. DRAFT ONLY - awaiting user authorization.

next-stage-design-brief-diagnostic.md consolidates all diagnostic
layers into a concrete two-stage proposal (boundary extension first,
calibration-weighted judge selection second). Diagnostic artifact only;
no stage has been started or authorized.

POST-V1.6A.4 UPDATE (2026-09-12): V1.6A.4 executed workstream A's
assertion-strength hypothesis and failed fresh validation (terminal
V1_6A4_NOT_READY, precision 0.368 vs >= 0.99, one-shot spent). The
measurement-architecture decision this report's chain points toward is
now drafted in
measurement-architecture-review-draft-v1-6c.md: judge-owned assertion
strength with calibration-weighted screening (recommended core),
inventory-grounding information-flow repair as cheap companion, and
narrow lexeme-only deterministic scope as conditional fallback. All
options require explicit owner authorization; DRAFT ONLY.
