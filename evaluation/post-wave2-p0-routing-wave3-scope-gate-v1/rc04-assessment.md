# RC-04 Assessment (Uncertainty, Wave 2)

## Status: STILL_REQUIRED (sequenced after route semantics)

## Facts
- required_uncertainty verdicts (Wave 2): NOT_REQUIRED 83, PARTIAL 36, VIOLATED 1 (ROUT-091; classified as measurement lexical sensitivity, not product defect).
- The 36 PARTIAL criteria are criteria where the product expresses some but not all required uncertainty. This is the SEMANTIC_JUDGE_STUB layer boundary: deterministic matching cannot grade partial epistemic coverage.

## Downstream vs independent
- A subset of PARTIALs is co-located with R0/R1 route failure (outputs without structured routes lean on boilerplate "ikke verifisert" phrasing), so fixing route propositions may change some PARTIAL outcomes.
- But the uncertainty layer itself (what must be expressed, and how partial coverage is graded) is an independent measurement/product gap that routing repair does not close.

## Recommendation
Keep RC-04 open. Do NOT pull it ahead of route semantics: re-scoring uncertainty depth before route construction exists would measure against unstable product shape. Reassess the independent residual after Wave-3 route repair lands.
