# Risk-coverage curve (iteration B)

Review-layer confidence floor sweep. Auto layer always accepted
(100% precision by construction). Labels normalized
(INSUFFICIENT_EVIDENCE = INSUFFICIENT, PARTIALLY_SUPPORTED = PARTIAL).

| floor | decided | coverage | selective accuracy |
|-------|---------|----------|--------------------|
| 0.50  | 362/389 | 93.1%    | 87.57%             |
| 0.60  | 362/389 | 93.1%    | 87.57%             |
| 0.70  | 362/389 | 93.1%    | 87.57%             |
| 0.75  | 362/389 | 93.1%    | 87.57%             |
| 0.80  | 362/389 | 93.1%    | 87.57%             |
| 0.85  | 360/389 | 92.5%    | 87.78%             |
| 0.90  | 359/389 | 92.3%    | 88.02%             |
| 0.95  | 352/389 | 90.5%    | 88.35%             |

Reading: the curve is nearly flat. Raising the global floor to 0.95
trades 10 decisions for +0.8 points accuracy, because the residual
errors are not confidence-miscalibration but evidence-comprehension
gaps (reviewer returns high-confidence 0.95-0.99 on the wrong side of
the INSUFFICIENT/CONTRADICTED boundary in 12 cases, all in the
conservative direction, never toward SUPPORTED).

Operating point: keep the class-based thresholds of
operating-thresholds.md (safety 0.95, numeric 0.90, legal 0.85,
default 0.80) plus the hard locks. That is the 93.1% / 87.57% row.
INSUFFICIENT stays a first-class outcome and is not confidence-gated.
