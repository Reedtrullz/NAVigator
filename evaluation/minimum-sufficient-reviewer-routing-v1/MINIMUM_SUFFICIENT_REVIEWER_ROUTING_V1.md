# NAV-EXPLORE-MINIMUM-SUFFICIENT-REVIEWER-ROUTING-V1 — Final Report

Terminal status: **ROUTER_V1_INSUFFICIENT_REVIEWER_EVIDENCE**
Date: 2026-09-19

## 1. Task status

The task closes with ROUTER_V1_INSUFFICIENT_REVIEWER_EVIDENCE. Stage 0 and
Stage A completed successfully; Stage B (fresh frozen router qualification)
cannot be executed because no fresh evaluation rows exist inside the task
authority. No Stage B precommit was created because no fresh slice exists to
precommit to; no downstream Stage B artifacts were fabricated.

## 2. Stage 0 (COMPLETE)

- Unique rows inventoried: 387 (reference-corpus canonical rows)
- Models inventoried: 10 across T1/T2/T3 (T4/Astra: no historical per-row evidence)
- Rows with frozen gold: 375
- Rows with sufficient evidence for a supervised minimum-tier label: 72 (19.2%)
- EVIDENCE_GAP_NO_TIER_CORRECT: 59 (15.7%); NO_EVIDENCE_ANY_TIER: 39 (10.4%)

## 3. Frozen tier mapping

- T1_BASIC: mimo-v2.5-pro, laguna-s-2.1, ling-3.0-flash-sante
- T2_INTERMEDIATE: bai-deepseek, nex-n2.5-pro
- T3_STRONG: luna-high, luna-max
- T4_FRONTIER_RESERVE: Astra LOW (reserve; target 0 fresh calls)

Ladder: cheapest SUFFICIENT tier with all cheaper tiers definitively FAILED;
any unresolved cheaper tier -> MINIMUM_UNKNOWN. Label set SHA256
4cd87708c79c44ce8a424b1feee491727096dbfd4edc55e0985a3a26fc64902e.

## 4. Stage A (COMPLETE) - burned router development

- Router N: 72 supervised rows, 72/72 Jev calls transport-OK
- Jev model: jev-latest (jev-1.13.0) via TypeSafe; 72 calls, mean latency 0.81 s
- Exact tier accuracy: 5/72 (6.9%)
- Within-one-tier accuracy: 15/72 (20.8%)
- UNDER_ROUTING: 0/72 (0)
- SAFETY-CRITICAL UNDER_ROUTING: 0/2 supervised safety rows
- OVER_ROUTING: 67/72 (93.1%) - cost inefficiency, not a safety failure
- Confusion: T1->T1 4, T1->T2 3, T1->T3 57, T2->T2 1, T2->T3 7
- Jev never predicted T4; predicted Astra share 0
- Feature separation weak: complexity T1 2.07 vs T2 2.23; NOUL signal 0.48 vs 0.55
- Routing stability: single development run; stability suite not run (burned dev only)

### T4 supervision investigation

All 26 rows with T3_STRONG=FAILED were audited for supervised-T4 candidacy.
None had T1+T2+T3 all definitively FAILED (every row had a cheaper tier
SUFFICIENT or UNRESOLVED). The frozen ladder rule is correct as frozen; the
hypothesis of 26 mislabeled rows is falsified. T4 cannot be supervised from
historical data.

## 5. Stage B - NOT EXECUTABLE

B.1 requires a fresh slice that did not participate in Jev V2, V3, Stage A,
or router tuning, with independent frozen gold. Exhaustive row-level check:

- Gold pool: 375 unique rows
- In V2 slice: 140 rows (40 cases, multiple packets per case)
- In V3 slice: 235 rows
- Overlap V2/V3: 0; remaining fresh rows: **0**
- The only unused rows are 12 gold=None rows, which cannot carry independent
  frozen gold and cannot be revealed as qualification data
- No sealed reserve pool exists ("Reserve candidates used: NONE" per cost-qual
  final report; no reserve was defined)

Constructing new fresh cases or burning the 12 unlabeled rows as gold would be
new dataset development outside this task authorization, and post-hoc gold
construction would itself violate the frozen-measurement discipline this
lineage is built on. Stage B therefore terminates with insufficient evidence
rather than being simulated on burned data.

## 6. Qualification gate assessment

Gate 7 (fresh evidence covers hard semantic families well enough for
qualification) cannot be evaluated: there is no fresh dataset. Gates 1-6 were
not tested on fresh data. Per the failure conditions, "sparse fresh evidence
so severe that the conclusion cannot be supported" applies; the canonical
terminal status is ROUTER_V1_INSUFFICIENT_REVIEWER_EVIDENCE.

## 7. Burned-only cost diagnostic (non-authoritative)

Simulated reviewer cascade on the 72 burned dev rows (calls only, no price
schedule frozen, so absolute cost is NOT EVALUABLE):

- P0 Jev-directed start: mean 1.46 model calls/row; 23/72 rows exhaust T1-T3
  without a sufficient tier (frontier/unresolved endpoint)
- P1 floor start at T1: mean 1.93 calls/row
- Jev-directed start saves ~24% calls on burned dev rows with 0 under-routes
  observed there - this is a development observation only, never a
  qualification claim

## 8. Primary evidence limitations

1. Zero fresh rows available; all 375 gold rows are burned in V2/V3/Stage A.
2. Frozen gold is LLM-consensus lineage, not human ground truth.
3. Supervised N=72 with lane skew; safety-critical supervised N=2.
4. Jev dev over-routing 93.1% means Jev V1 difficulty routing has near-zero
   value as-is; any future router must change the starting-tier policy, not
   Jev correctness semantics.
5. Single Jev run; no stability measurement.

## 9. Artifacts

- evaluation/minimum-sufficient-reviewer-routing-v1/TASK-LOCK.json
- evaluation/minimum-sufficient-reviewer-routing-v1/reviewer-evidence-inventory.json
- evaluation/minimum-sufficient-reviewer-routing-v1/reviewer-evidence-gaps.json
- evaluation/minimum-sufficient-reviewer-routing-v1/reviewer-evidence-coverage.md
- evaluation/minimum-sufficient-reviewer-routing-v1/minimum-sufficient-reviewer-burned.jsonl
- evaluation/minimum-sufficient-reviewer-routing-v1/stage-a-taxonomy-analysis.json
- evaluation/minimum-sufficient-reviewer-routing-v1/router-schema-frozen.json
- evaluation/minimum-sufficient-reviewer-routing-v1/router-dev-raw-jev.jsonl
- evaluation/minimum-sufficient-reviewer-routing-v1/router-dev-parsed.json
- evaluation/minimum-sufficient-reviewer-routing-v1/MINIMUM_SUFFICIENT_REVIEWER_STAGE_A.md
- evaluation/minimum-sufficient-reviewer-routing-v1/MINIMUM_SUFFICIENT_REVIEWER_ROUTING_V1.md (this file)

## 10. Recommended next step (requires new owner authorization)

The binding constraint is dataset supply, not router engineering. A future
task could: (a) authorize construction of a fresh labeled case batch with
precommitted gold (human-adjudicated where safety-critical), sized for the
Stage B gates, or (b) close this line and route reviewer effort through the
existing measurement pipeline without difficulty routing. No further work was
started in this task.
