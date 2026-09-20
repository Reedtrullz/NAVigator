# Architecture Decision - Semantic Residual Packet V1 (V1.6C.1)

## Decision

**NOT_SUPPORTED.** The `semantic-residual-packet-v1` information-flow repair
does not pass the preregistered material-improvement gate and must not be
integrated into the judge lineage as-is.

## Evidence (paired A/B, 92 burned V1.6B judge rows)

| Metric | OLD flow | NEW flow (+packet) |
|---|---|---|
| Residual overall | 79/92 (85.87%) | 78/92 (84.78%) |
| Critical | 27/30 | 26/30 |
| Forbidden | 25/30 | 25/30 |
| Route | 15/18 | 16/18 |
| Uncertainty | 12/14 | 11/14 |
| Critical FN | 0 | 0 |
| Safety forbidden FN | 0 | 0 |
| Valid rate | 100% | 100% |
| Evidence validity | 100% | 100% |

Switches: 2 wrong->right (F-02, R-11), 3 right->wrong (C-27, F-08, U-14),
79 unchanged. Largest dimension regression: uncertainty -7.14 pp (gate -3.00).
Absolute improvement: -1.09 pp (gate +10.0). Relative error reduction: -7.69%
(gate +25%). Token overhead median +42.2% (+816.5 tokens); latency median
+18.6% (+3.99 s).

## Interpretation

- The information lost to the judge (13/13 wrong rows discarded A3 structure)
  was real, but re-injecting it as neutral context did not convert into
  materially better verdicts. The model already recovers most of the structure
  from RAW text; the packet mainly duplicated signal it can infer.
- Route correctness improved (+5.56 pp), consistent with route candidates and
  clause grouping being the most useful additions.
- Uncertainty regressed (-7.14 pp): extra structural context appears to have
  pushed hedging classification around rather than clarified it.
- Cost is strictly negative at these numbers: worse accuracy, +42% tokens.

## Consequences

1. Packet V1 is frozen as a measured negative result; do not tune or rerun it.
2. No C2 calibration-weighted screening is justified on this signal alone.
3. No A5, lexical fallback, or fresh validation in this task.
4. Next bounded stages must attack the residual failure clusters directly
   (16 rows unchanged-wrong/failing) rather than re-encoding structure the
   judge already sees.
