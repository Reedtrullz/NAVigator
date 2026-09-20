# Agreement Report

All agreement numbers come from two independent GPT-5.6-Luna passes
(temperature 0, fresh context, frozen contract, shared schema). Gold
labels were never used in any gate computation.

## Calibration round 1 (set 1, CC3-001..020, pre-repair)

calibration-results-1.json: semantic 95.0, quantity_identity 93.75 (FAIL),
temporal 100, comparator_applicable 95.0, comparator_relation 87.5 (FAIL),
arithmetic_duty 100. Triggered the single allowed contract repair.

## Calibration round 2 (set 2, CD3-001..020, post-repair)

calibration-results-2.json:

| Field | Agreement | Gate | Result |
|---|---|---|---|
| semantic_relation | 95.0 | >=90 | PASS |
| quantity_identity | 100.0 | >=95 | PASS |
| temporal_applicability | 100.0 | >=90 | PASS |
| comparator_applicable | 100.0 | >=95 | PASS |
| comparator_relation | 100.0 | >=95 | PASS |
| arithmetic_duty | 100.0 | >=95 | PASS |

One semantic dispute remained (CD3-010, PARTIAL vs RELATED_BUT_INSUFFICIENT),
which is within the 95% gate. Contract frozen after this round.

## Final 30-case pre-adjudication agreement

final-agreement.json (pass1-results.json vs pass2-results.json, cases
SHA c231979d... verified byte-identical):

| Field | Agreement | Gate | Result |
|---|---|---|---|
| semantic_relation | 96.67 | >=90 | PASS |
| quantity_identity | 94.74 | >=95 | FAIL |
| temporal_applicability | 100.0 | >=90 | PASS |
| comparator_applicable | 90.0 | >=95 | FAIL |
| comparator_relation | 66.67 | >=95 | FAIL |
| arithmetic_duty | 96.67 | >=95 | PASS |

Schema failures: 0 in all four final-relevant passes. Comparator_relation
denominator is the union of passes' comparator_applicable=true cases
(6 cases); restricting to both-applicable gives 8/9 = 88.9%, still below
the 95% gate.

## Terminal consequence

Spec 24 requires ALL gates to pass before adjudication. They do not, and
the one repair budget is spent. Status: ANNOTATION_CONTRACT_NOT_READY.
