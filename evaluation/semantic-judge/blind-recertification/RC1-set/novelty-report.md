# Novelty report - RC1 blind set construction

Mechanical checker (validation/novelty-checker.py) compared every candidate against prior benchmark claims (calibration, holdout-v2, minimal-pair, diagnostic-20, novel-40, oracle, reviewer, operator-regression). The checker returned similarity scores, conflicting IDs and reasons only; candidate authors never saw old claim text.

Pre-registered thresholds: token Jaccard 0.55, char-3-gram 0.80, skeleton entity overlap 0.5, exact 1.0.

| Metric | Count |
|---|---|
| Candidates generated | 193 |
| Exact duplicates rejected | 0 |
| Near duplicates rejected | 2 (RC1B-0076, RC1B-0146) |
| Source-skeleton duplicates rejected | 4 (RC1B-0091, RC1B-0095, RC1B-0100, RC1B-0123) |
| Retained for annotation | 187 |
| Maximum similarity among retained | 0.5385 (below 0.55 gate) |
| Annotation disputes rejected | 0 (7 disputes adjudicated to confirmed labels per spec 29-30; none left as ANNOTATION_DISPUTE) |
| Source-fidelity failures rejected | 0 (193 checks, all verbatim) |
| Final core | 120 |
| Final reserve | 67 |

Wave 4 (genuine insufficiency / partial-support / near-miss supplementation): 26 candidates (RC1B-0168..0193), 0 rejected, 26 retained, maximum similarity 0.2941.

Conflicting references for rejects: CAL012, CAL028, DEC-008, DEC-012 (x2), N-L5. Per-case labels for retained cases are not disclosed in this report.
