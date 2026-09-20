# Stage 3 Final Report - NAV-EXPLORE-MEASUREMENT-V3-COMBINED-FREEZE

## Result

STATUS: MEASUREMENT_V3_COMBINED_FREEZE_READY

The combined measurement engine (combined-measurement-v3) integrates the three
frozen measurement components and passes all 9 integration gates on 150
synthetic mixed-workflow fixtures. Model calls in this stage: 0.

## Architecture

Single authoritative owner per item, chosen by frozen workflow:

1. DETERMINISTIC_SCORER_V1 - deterministic scorer criteria only.
2. M2_LANE_V2_6 - M2-workflow critical-condition decomposition with frozen
   derivation table, dual review, adjudication, duplicate rejection.
3. GENERIC_LANE_V2_15 - all four semantic dimensions (critical_condition,
   forbidden_claim, route_correctness, required_uncertainty), including items
   escalated from the deterministic scorer when its notes
   (SEMANTIC_JUDGE_STUB, PARAPHRASE_NOT_DETERMINISTICALLY_MATCHED,
   CRITICAL_CONDITION_UNMAPPED) require semantic judgment.

No automated semantic verdicts anywhere in the combined engine. Confidence is
not mixed across layers. Fail-closed: pending / invalid / disagreement states
carry no final label.

## Integration gates (150 fixtures: 40 scorer, 45 M2, 65 semantic)

| Gate | Result |
|---|---|
| routing_100 | PASS |
| no_authority_overlap_100 | PASS |
| fail_closed_100 | PASS |
| provenance_100 | PASS |
| leakage_0 | PASS |
| reporting_arithmetic_100 | PASS |
| deterministic_rerun_stable | PASS |
| expectations_100 | PASS |
| no_automated_semantic_verdicts | PASS |

## Bugs found and fixed during integration (harness + engine glue only)

1. Fixture: M2 disagreeing review used PRESENT with an empty evidence-span
   list, which the frozen lane correctly rejects; replaced with a valid
   sufficiency-conflict disagreement so adjudication is exercised.
2. Fixture: M2 NOT_TRIGGERED case lacked any non-trigger span in the SUT text,
   violating the frozen lane span rule; gave the case its own SUT text with a
   present non-trigger span.
3. Engine: M2 final was propagated as the raw derivation dict; normalized to
   the frozen final_label string.
4. Gate: provenance check rejected the lane's valid terminal tail
   DUPLICATE_REVIEW_REJECTED (accepted duplicate rejection carries no trailing
   STATUS event); corrected to the frozen lane contract, same class of fix as
   the V2.15 audit ALLOWED_TAILS correction.
5. Gate: routing check did not model the documented scorer-to-generic-lane
   escalation path; made escalation-aware.

No frozen upstream artifact was modified; all fixes are in the new Stage 3
lineage (fixtures, engine glue, test gates).

## Freeze

22 artifacts pinned in v3-manifest.json / hashes.txt, including the combined
engine, both fixture/result files, the deterministic scorer + contract, the
M2 lane + derivation table + schemas + contracts, the V2.12 uncertainty lane,
the V2.15 semantic fallback lane, judge cores (v2_13, v1_4), the V2.7E
uncertainty derivation, and the semantic-judge v1-4 contract + schema.

Note on determinism: the frozen V2.6/V2.15 lanes stamp real wall-clock utc
values into packet/provenance records (intended lane behavior, frozen
upstream). Therefore integration-results-v3.json is a point-in-time freeze;
re-verification means a 9-gate rerun plus the deterministic_rerun_stable gate
(semantic signature: item_id/status/final), not byte identity of the results
file. All 21 other pinned artifacts are byte-stable and SHA-reverified.

## Remaining gap

No full NAV Explore SUT exists (confirmed by dev-corpus-scorer-v1 TASK-LOCK:
FULL_NAV_EXPLORE_SUT_NOT_AVAILABLE). See full-sut-gap-report.md. Campaign
terminal status after Stage 4: MEASUREMENT-READY-SUT-MISSING.
