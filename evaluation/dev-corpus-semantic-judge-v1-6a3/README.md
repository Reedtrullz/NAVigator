# V1.6A.3 - Boundary Pre-Classifier (Ambiguity-Abstention Hardening)

Lineage: V1.6A -> V1.6A.1 -> V1.6A.2 -> **V1.6A.3** (this task).

**Terminal status**: `V1_6A3_BOUNDARY_PRECLASSIFIER_READY`

Frozen candidate: `boundary-preclassifier-v1-6a3`
Engine SHA: `21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b`
Manifest SHA: `0fedd38b5aa680a891dd9e16307e5de200cd3e06464789b8393580d4d71bcd00`

## What this is

A model-free, deterministic, precision-first boundary pre-classifier for the
dev-corpus semantic judge pipeline. It resolves unambiguous route-commitment
outputs mechanically and ABSTAINs conservatively on five generic ambiguity
families (quote scope, parenthetical scope, mixed polarity, hedge competition,
multiple candidates). It is a gate layer, not a judge replacement.

## Headline results (official one-shot, 120 fresh fixtures)

- Overall non-ABSTAIN precision 1.0 (gate >=0.99)
- REQUIRED_ABSTAIN: 40/40 correct abstains, 0 unsafe non-abstains (hard zero-gate)
- CLEAN_DETERMINISTIC: coverage 1.0 (gate >=0.80), precision 1.0
- ADVERSARIAL_MIXED: precision 1.0 (gate >=0.98)
- Evidence-span validity 1.0

## Key files

- `final-report.md` - full 68-item contract report with deviations
- `ambiguity-gate-design.md` - frozen G1-G5 gate design
- `boundary_preclassifier.py` - frozen engine
- `official-validation-results.json` - one-shot run (frozen)
- `burned-v1-4-diagnostic-replay.json` - diagnostic-only V1.4 replay (includes A3 amendment)
- `preclassifier-manifest-v1-6a3.json` - freeze manifest with all file hashes

## Provenance cautions

- Gold provenance is INTRA_ANNOTATOR_REPEATABILITY (same annotator, two passes), not inter-annotator.
- 273 generic template-frame 4-gram overlaps with historical corpora are disclosed in `disputed-fixture-registry.json` (0 exact/normalized reuse).
- TDD RED was reconstructed post-patch (A1 deviation, disclosed in final-report.md).
- V1.4 replay is diagnostic only; 3 route-deterministic-on-miss rows (R-12, R-16, R-18) remain unresolved diagnostic risk.

## Out of scope (do not do here)

No semantic judge calls, no V1.6B rescreen, no product runtime changes, no
fresh product holdout. Next stage is a separate task:
`NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6B-RESCREEN`.
