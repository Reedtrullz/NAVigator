# Stage A — Burned Minimum-Sufficient-Reviewer Labels & Router Development

Task: NAV-EXPLORE-MINIMUM-SUFFICIENT-REVIEWER-ROUTING-V1
Status: STAGE_A_COMPLETE (burned development only; no fresh validation claims)
Date: 2026-09-19

## 1. Scope and authority

Stage A produced burned development labels and a burned Jev difficulty-router
development run. Nothing here is fresh validation evidence. V3 terminal status
JEV_NATIVE_FRESH_NOT_QUALIFIED remains immutable; Jev is used only as a
difficulty/routing model, never as a PASS/FAIL correctness authority.

## 2. Frozen tier mapping (A.1)

| Tier | Models | Historical evidence |
|---|---|---|
| T1_BASIC | mimo-v2.5-pro, laguna-s-2.1, ling-3.0-flash-sante | full |
| T2_INTERMEDIATE | bai-deepseek, nex-n2.5-pro | full |
| T3_STRONG | luna-high, luna-max | full |
| T4_FRONTIER_RESERVE | Astra LOW | no historical per-row evidence |

Sufficiency (A.2): a cell is CORRECT only if ALL valid runs match frozen gold.
Ladder (A.3/A.4): cheapest SUFFICIENT tier with all cheaper tiers definitively
FAILED; any UNRESOLVED/no-evidence cheaper tier blocks supervision ->
MINIMUM_UNKNOWN. Tier FAILED requires every tier model tested (complete
coverage); existence semantics: a tier is sufficient if one route works, so an
in-tier cascade must order known-good routes first (tested in Stage B).

## 3. Label set (frozen)

minimum-sufficient-reviewer-burned.jsonl, SHA256
4cd87708c79c44ce8a424b1feee491727096dbfd4edc55e0985a3a26fc64902e:

- total gold rows: 375 (of 387 inventory rows; 7 gold=None excluded, plus
  inventory gaps)
- supervised: 72 (T1=64, T2=8)
- MINIMUM_UNKNOWN: 205
- EVIDENCE_GAP_NO_TIER_CORRECT: 59
- NO_EVIDENCE_ANY_TIER: 39
- safety-critical rows: 13, of which supervised 2 (1xT1, 1xT2)

## 4. T4 supervision investigation (negative result, documented)

The 26 rows with T3_STRONG=FAILED were audited for supervised-T4 candidacy
(T1+T2+T3 all definitively FAILED). Result: 0 candidates. Breakdown of
(T1,T2,T3) states on those 26 rows:

- (SUFFICIENT, SUFFICIENT, FAILED): 8  -> ladder stops at T1/T2, correct
- (SUFFICIENT, UNRESOLVED, FAILED): 4  -> T2 untested models remain
- (FAILED, SUFFICIENT, FAILED): 2      -> ladder stops at T2
- (UNRESOLVED, SUFFICIENT, FAILED): 3  -> ladder stops at T2
- (UNRESOLVED, UNRESOLVED, FAILED): 8  -> cheaper tiers unresolved
- (FAILED, UNRESOLVED, FAILED): 1      -> T2 untested models remain

Conclusion: the burned corpus cannot supervise T4 from the frozen ladder rule.
The earlier development hypothesis that 26 rows were mislabeled
EVIDENCE_GAP_NO_TIER_CORRECT is falsified; the label set is correct as frozen.
T4 remains a defined reserve tier with zero historical per-row evidence; Stage
B must treat Astra fresh calls as targeted (target 0 calls) and may not derive
T4 supervision from absence of evidence.

## 5. Router schema and dev run

- router_schema.py + router-schema-frozen.json (frozen): Jev Score question
  (reasoning_complexity 0-4), Choice question (predicted_starting_tier
  T1/T2/T3/T4/UNCERTAIN), 8 NOUL signals.
- router-dev-raw-jev.jsonl: 72/72 supervised rows called, transport OK 72/72.
- Key handling: TYPESAFE_API_KEY / project .env.local, never printed.

## 6. Router dev performance (burned only)

- exact tier: 5/72 (6.9%)
- under-routing: 0/72 (0) - the safety direction is clean on this burned set
- over-routing: 67/72 (93.1%) - cost inefficiency, not safety
- confusion: T1->T1 4, T1->T2 3, T1->T3 57, T2->T2 1, T2->T3 7
- safety-critical supervised rows: both over-routed to T3 (no under-route)
- predicted Astra/frontier share: 0 (Jev never predicted T4)

Feature separation is weak: mean reasoning_complexity T1=2.07 vs T2=2.23;
mean NOUL signal T1=0.48 vs T2=0.55. Jev has almost no signal toward the
cheaper tiers and default-routes to T3_STRONG (64/72).

## 7. Interpretation and Stage B implications

- Jev V1 difficulty routing over-routes massively on burned dev data. Under
  the task asymmetric cost model this is a cost problem, not a safety problem:
  0 under-routes and both safety-critical rows over-routed.
- The ladder existence semantics plus the T3 default means a naive cascade
  would start at Luna for ~89% of rows. A starting-tier override (e.g. start
  at T1 unless Jev is confident) is the obvious candidate mechanism, but it
  must be precommitted and tested on fresh data, not tuned here.
- EVIDENCE_GAP rate on the full gold set: 59/375 (15.7%); NO_EVIDENCE 39
  (10.4%). Router claims are restricted to rows with sufficient tier evidence.
- Stage B gate: 0 safety-critical under-routes remains a hard disqualifier;
  report the Wilson upper bound for the under-route rate on fresh rows.

## 8. Limitations

- Burned development only; no fresh generalization claim.
- 72 supervised rows is small and lane-skewed (routing/escalation families).
- T1 tier-sufficiency inherits in-tier route ordering assumptions.
- T4 cannot be evaluated on historical data at all.
