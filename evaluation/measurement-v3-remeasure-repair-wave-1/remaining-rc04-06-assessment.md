# Remaining RC-04 / RC-05 / RC-06 Assessment

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1. Read-only assessment based on frozen artifacts. None of RC-04/05/06 was implemented in this task (hard constraint).

## RC-04 - forbidden claims on failure-path outputs: DESCOPED, indirectly addressed

RC-04 targeted forbidden-claim violations that appeared only on EXECUTION_FAILED failure-path outputs. Its observed family was 2 VIOLATED verdicts in the old baseline. RC-01 removed the failure path entirely: 9 EXECUTION_FAILED cases in the old phase-3 run logs (SAF-007, SAF-009, SAF-011, SAF-013, SAF-019, ROUT-078, ROUT-087, ROUT-088, DIS-120) are all SUCCESS in the frozen Wave-1 replay, and forbidden-claim VIOLATED-type failures went to 0 in the new measurement.

Disposition: no direct RC-04 implementation is still indicated. The failure-path canary should be kept in future regression suites so a regression of the execution path would be caught before forbidden-claim behavior is measured again.

## RC-05 - evidence completeness: STILL INDICATED

Frozen scorer evidence rows are unchanged: 38 of 120 cases remain at evidence_completeness 0.0 and 82 at 1.0; mean 0.6833 is identical to the old baseline. Structured provenance exists on claims (308 of 645 provenance-linked in the new diagnostics vs 291 of 610 old), but the evidence-completeness criterion distribution did not move.

Disposition: a dedicated evidence/provenance repair wave remains justified. Expected blast radius: evidence scoring and provenance linkage, not route or safety semantics.

## RC-06 - repeated national information blocks: STILL INDICATED

Read-only product diagnostics on the frozen Wave-1 predictions:

- answers with >= 2 repeated "Nasjonal informasjon" blocks: 104 of 120 (old: 98 of 120)
- total repeated national-information occurrences: 645 (old: 610)
- provenance-linked claims: 308 of 645 (old: 291 of 610)
- no_route_asserted: 97 of 120 (old: 120)

The repeated-block problem slightly worsened in raw counts while route emission improved; the two are plausibly linked (more rendered source content per answer), but that linkage is a hypothesis, not a proven root cause. No frozen scoring criterion directly captures this defect; it remains a presentation-quality diagnostic.

Disposition: renderer/source-block deduplication remains a separate repair candidate for a future wave, with regression risk concentrated in answer rendering only.

## Summary table

| Candidate | Status after Wave-1 | Action |
|---|---|---|
| RC-01 execution failures | Repaired (9 -> 0 EXECUTION_FAILED) | Keep run-log canary |
| RC-02 safety priority | Structural mismatch unchanged (19/20 rows) | Future decision: align taxonomy or scoring |
| RC-03 route emission | Emission repaired; verdicts unchanged | Future: service-identity route labels |
| RC-04 failure-path forbidden claims | Descoped; indirectly resolved by RC-01 | Keep failure-path canary |
| RC-05 evidence completeness | Still indicated (38/120 at 0.0 unchanged) | Future repair wave |
| RC-06 repeated national blocks | Still indicated (98 -> 104 cases) | Future repair wave |

Interpretation boundary: BURNED_DEV_BASELINE_ONLY; no repair work was authorized or performed here.
