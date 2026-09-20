# Wave-1 Residual LLM Adjudication - Final Report

Task: NAV-EXPLORE-MEASUREMENT-V3-WAVE1-RESIDUAL-LLM-ADJUDICATION-V1
Date: 2026-09-16
Upstream terminal: MEASUREMENT_V3_REMEASURE_WAVE_1_RESIDUAL_ADJUDICATION_REQUIRED
Final terminal: MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING

## 1. Scope

Blind dual-pass adjudication (gpt-5.6-sol, LOW only) of exactly 4 frozen residual packets
(DIS-118, ROUT-026, ROUT-031, ROUT-037; all forbidden_claim), mechanical derivation via
frozen judge_core_v2_13, freeze of the complete 600/600 wave-1 remeasurement, and
recomputed aggregates. No SUT rerun, no gold change, no measurement-contract change,
no packet change, no Astra calls, no GPT-5.5, no third pass, no majority vote.

## 2. Accounting Checks

Check A (526 -> 508 DETERMINISTIC): exactly 18 criterion rows moved
DETERMINISTIC -> LLM_REVIEWED across 17 cases; mechanism is the frozen scorer's
CRITICAL_CONDITION_UNMAPPED and PARAPHRASE_NOT_DETERMINISTICALLY_MATCHED + SEMANTIC_JUDGE_STUB
escalations routed to GENERIC_LANE_V2_15. No measurement source or config changed; 508 is valid.
Full transition matrix and moved-row list: accounting-audit.json.

Check B (failure-rate definitions): distinct canonical names now registered.
- OLD_HARD_FAIL_RATE = 45.07% (265/588, frozen scorer semantics)
- WAVE1_HARD_FAIL_RATE_AUTHORITATIVE = 41.61% (243/584)
- OLD_NON_PASS_RATE = 51.70% (1 - 284/588)
- WAVE1_NON_PASS_RATE_AUTHORITATIVE = 50.86% (1 - 287/584)
- The failure-analysis headline 38.61% was a legacy triage counting that treated the 38
  evidence_completeness=0.0 rows as DEGRADED; the frozen scorer calls them FAIL.

Open item resolution: old LLM_ADJUDICATED=10 rows split 9 -> LLM_REVIEWED and
1 -> PENDING (DIS-118) in wave1; the handoff cross-tab 8 was a miscount. The
wave1-effect-analysis state_delta had two arithmetic defects (stale UNRESOLVED=5 instead
of 18, and denominator 588 instead of 584) explaining the 17-row gap. All aggregates in
this lineage are recomputed from raw rows via the frozen semantic_state mapping.

## 3. Sol Availability and Execution

- Presence probe: AVAILABLE via existing local proxy; corrected probe after diagnosing that
  json_object mode requires the word json in messages (identical behavior for Sol and the
  Astra control; control was a transport diagnostic only, no packet content).
- 8 adjudication calls (SOL-A/SOL-B x 4 packets): 8x OK, 0 transport retries.
- All records independently valid: JSON schema fields, packet SHA binding, verbatim
  evidence spans, conditional span-presence rule.
- Constraint compliance: ASTRA_CALLS=0, GPT_5_5_CALLS=0, SOL effort LOW only, no spend.

## 4. Consensus Outcome

Frozen rule: A==B on the entire result object. Outcome: 0 adjudicated, 4 pending.

Disagreement analysis: on all 4 packets, criterion_semantic_match and speaker_commitment
are identical across SOL-A and SOL-B; only free-text rationale (and evidence-span wording)
differed. Routing-relevant primitives fully agree; the whole-object equality rule is
strictly stronger than primitive-level agreement. Per the frozen TASK-LOCK no third pass
and no majority vote were permitted, so all 4 remain PENDING_HUMAN_ADJUDICATION.

This is recorded as a frozen observation for the owner: the contract tension between
whole-object equality and primitive-level agreement is the exact boundary a future
owner-authorized amendment would need to address. No such change was made here.

## 5. Completed Lineage Artifact

wave1-remeasurement-complete-after-secondary-residual.json:
- deep copy of wave1-combined-measurement-results.json; exactly 4 rows changed (provenance only)
- pending rows: observation_source SECONDARY_SOL_RESIDUAL_DUAL_PASS_NO_CONSENSUS,
  model gpt-5.6-sol, per-pass record SHAs, packet_sha256 restored to frozen packet body hashes
- verdicts unchanged (None), authority unchanged (PENDING_HUMAN_ADJUDICATION)
- coverage: 508 DETERMINISTIC / 88 LLM_REVIEWED / 0 LLM_ADJUDICATED / 0 HUMAN_REVIEWED /
  4 PENDING / 600 total; authoritative 596 (99.33%)
- states (frozen semantic_state mapping, raw-row recount): PASS 287, FAIL 243, DEGRADED 36,
  UNRESOLVED 18, ABSENT_OR_NOT_APPLICABLE 12, PENDING 4; applicable 584
- rates: HARD_FAIL_RATE_AUTHORITATIVE 41.61%, NON_PASS_RATE_AUTHORITATIVE 50.86%

## 6. Result Facts (old provenance-corrected baseline vs wave1 remeasurement)

- RC-01 critical_condition CRITICAL_ERROR: 110 -> 91 (FAIL-state 111 -> 92)
- RC-02 required_uncertainty VIOLATED: 2 -> 0 (SAF-009/019 VIOLATED -> PARTIAL)
- RC-03 forbidden CLAIM_ABSENT_TAKEN (premature absence): 53 -> 48; safety block
  PRESENT/CLAIM_PRESENT: 6 -> 5; route_correctness rows with verdicts: 120/120 before and
  after. RC-03 is a structural mechanism repair, not a semantic product outcome improvement.
- No fresh product holdout was authorized; no generalization claim is made.

## 7. Integrity

- Upstream artifact SHA verified before use.
- Frozen derivation core judge_core_v2_13 SHA verified; derive_final not invoked because
  zero packets reached consensus; derivation LLM calls 0.
- All lineage and task artifacts pinned in measurement-manifest.json and hashes.txt.

## 8. Terminal Status

MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING

Hard stop. Next step requires a separate owner authorization. The only forward path
within this lineage would be an owner decision on one of:
1. Human adjudication of the 4 pending packets (still legitimate; observations frozen).
2. A new owner-authorized amendment defining primitive-level consensus semantics for the
   secondary lane, then a fresh dual pass on new transport observations.
Neither is started here.
