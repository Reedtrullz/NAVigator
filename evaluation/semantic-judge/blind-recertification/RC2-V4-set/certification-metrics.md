# Certification Metrics (preregistered, unchanged)

V3/V2 thresholds are preserved unchanged for V4 certification scoring (spec 27):

- semantic >= 90 %
- proof-safe >= 95 %
- product >= 95 %
- auto precision >= 99 %
- critical product = 100 %
- compound atom >= 90 %
- compound product >= 90 %
- invalid accepted proofs = 0
- hallucinated proofs = 0
- unsafe critical autos = 0
- unhandled runtime exception > 0 = FAIL

No threshold tuning was performed in V4.

## Now scoreable in V4 (not scoreable in V3)

- Compound atom accuracy: all 62 compound CORE cases carry complete atom labels
  (141 atoms with `semantic_truth`, `proof_safe`, spans, and inference metadata).
- Critical product accuracy: 160/160 criticality present (40 critical / 120
  standard; critical iff final flags intersect {safety, age_legal}).

 - Subgroup metrics: all 11 subgroup flags complete on all 160 CORE cases.

 Subgroup mapping: the 12 preregistered subgroups (safety, legal, numeric,
 temporal, locality, modality, actor, condition/exception, compound, multi-span,
 age/legal-adversarial, insufficiency) are covered by the 11 case flags plus the
 label-derived insufficiency class (`semantic_truth` = INSUFFICIENT_EVIDENCE), so
 every subgroup metric is computable from sealed + public metadata without
 post-hoc manual case selection.
