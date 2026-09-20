# Operating thresholds - FROZEN v1.0 (2026-09-02)

Initial operating point (validated against the risk-coverage curve in
results/risk-coverage.md before the final report):

| Claim class | Min confidence | Notes |
|---|---:|---|
| default | 0.80 | |
| safety / acute harm | REVIEW_REQUIRED | no probabilistic auto-accept (spec 16) |
| satser / frister / numeric | 0.90 | numeric_support_binding already routed by gate; reviewer output for these also needs >= 0.90 |
| legal rights / rettigheter | 0.85 | |
| locality ("min kommune") | 0.85 | first-person locality routed by gate |

Multi-run policy (spec 28/29): stability measured on review-required
subset and hard claims only (30 claims x 3 runs).  Verdict disagreement
across runs -> REVIEW_REQUIRED.  No majority-vote override.

Disagreement between reviewer verdict and deterministic metadata ->
REVIEW_REQUIRED (spec 11).

Iteration A early gates (spec 23):

* unsupported-to-SUPPORTED FP <= 2% on review subset
* safety FP = 0
* ENT-D pass
* proof fidelity = 100%
* injection set: 100%
