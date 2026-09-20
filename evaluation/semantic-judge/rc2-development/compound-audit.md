# RC2 Compound Audit (BURNED_BLIND_V1_DEVELOPMENT_ONLY)

Scope: all 41 semantic failures in the 120-core burned set, classified
by comparing the sealed answer key's atom_labels (80 of 120 cases carry
atom labels) with the RC2 engine's atom_results. Method: classes from
the task spec (BAD_DECOMPOSITION, MISSING_ATOM, WRONG_ATOM_BOUNDARY,
EVIDENCE_ROUTING, ATOM_VERDICT_ERROR, AGGREGATION_ERROR,
PARTIAL_DOCTRINE, FUSION_THRESHOLD, TRUE_AMBIGUITY). Full per-case
detail: compound-audit.json.

## Classification (41 failures)

| Class | n | Note |
|---|---|---|
| BAD_DECOMPOSITION | 24 | engine merges label atoms (e.g. RC1B-0122: 5 label atoms -> 1 engine atom) |
| WRONG_ATOM_BOUNDARY | 12 | engine splits into more atoms than labeled |
| ATOM_VERDICT_ERROR | 4 | atom count matches, verdicts differ |
| AGGREGATION_OR_FUSION | 1 | atoms fully correct, overall wrong |

## Oracle decomposition test

Question: if the engine judged the annotators' exact label atoms, would
the annotation's aggregation rule fix these failures? Procedure: judge
each labeled atom separately against the same sources, aggregate with
the rule recovered from the 80 labeled cases (all-SUPPORTED ->
SUPPORTED; all-CONTRA -> CONTRADICTED; CONTRA+SUPPORT -> PARTIAL;
SUPPORT+INSUFFICIENT -> PARTIAL; 77/80 label-consistent).

Result: only **6 of 30 atom-labeled failures** are fixed. The dominant
residual is the engine returning INSUFFICIENT_EVIDENCE on fine-grained
atoms the annotators marked SUPPORTED (support recall on narrow atoms),
plus one contradiction-direction case (RC1B-0116, a known label-audit
sensitivity).

## Consequence

Decomposition granularity is NOT the binding constraint - atom-level
support recall is. Rewriting the segmenter is a core-engine project with
regression risk across the whole surface, not a bounded repair. The
spec permits exactly one bounded fix in Phase B; the measured-yield
comparison (fusion: 32 label-correct autos recovered on the 41-battery
vs oracle-decomposition: 6) selects the fusion repair as Iteration B.
Compound repair is documented as deferred with this evidence base.
RC1B-0169 (CONTRA overcall on mixed atoms) is covered by the fusion
policy's asymmetric no-CONTRA-accept rule.
