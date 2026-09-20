# Final Report — Wave-1 Semantic Consensus Comparator Repair V1

Task ID: `NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1`

## Summary

The Wave-1 Sol residual task left 4 of 600 criteria as
`PENDING_HUMAN_ADJUDICATION` because its task-local comparator required
whole-object A==B equality between two blind GPT-5.6-Sol passes. This task
traced the rule's provenance, classified it as a Branch A implementation
defect against the measurement contract's primitive-level consensus semantic,
replayed the corrected comparator over the frozen observations with zero new
model calls, and mechanically completed the Wave-1 result to 600/600
authoritative criteria.

| # | Item | Value |
|---|------|-------|
| 1 | Task ID | NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1 |
| 2 | Upstream terminal status | MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING |
| 3 | Upstream freeze SHA | 71a0b22441d69924226bf7835dc441df1b779e76dfbfff7fc867010c96c017fd (measurement-manifest.json) |
| 4 | Residual count | 4 |
| 5 | Residual IDs | DIS-118, ROUT-026, ROUT-031, ROUT-037 |
| 6 | Existing Sol observations verified | Yes (8/8 records; schema, packet binding, enums, evidence) |
| 7 | New LLM calls | 0 |
| 8 | Source of old whole-object rule | Task-local execution artifacts of the Wave-1 residual lineage (sol-adjudication-consensus.json, frozen-observations, lock terminal summary); no measurement contract or persisted comparator |
| 9 | Old rule implementation or contract | Implementation (ephemeral task-local comparator scope) |
| 10 | Branch | A — CONSENSUS_COMPARATOR_IMPLEMENTATION_DEFECT |
| 11 | Authoritative semantic fields | criterion_semantic_match, speaker_commitment |
| 12 | Non-authoritative fields | rationale (EXPLANATORY_NON_AUTHORITATIVE), transport metadata |
| 13 | Evidence fields | evidence_spans (REQUIRED_EVIDENCE; independently validated per pass) |
| 14 | A/B schema validity | 8/8 OK |
| 15 | A/B evidence validity | 8/8 valid (verbatim spans in SUT output; presence rules enforced) |
| 16 | Primitive agreement count | 4/4 |
| 17 | Whole-object agreement count | 0/4 (rationale-only differences) |
| 18 | Newly resolved count | 4 |
| 19 | Remaining pending count | 0 |
| 20 | Comparator frozen before derivation | Yes in-memory: comparator result validated before kernel invocation; see freeze_vs_derivation_ordering in comparator-repair-freeze-manifest.json (single-pass write, documented honestly) |
| 21 | Derivation kernel SHA | 66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682 (judge_core_v2_13.py, unmodified) |
| 22 | LLM calls during derivation | 0 |
| 23 | Semantic observations changed | No |
| 24 | Previous authoritative rows changed | No (596/596 rows byte-identical to upstream; proven by row diff) |
| 25 | Final DETERMINISTIC count | 508 |
| 26 | Final LLM_REVIEWED count | 88 |
| 27 | Final LLM_ADJUDICATED count | 4 |
| 28 | HUMAN_REVIEWED count | 0 |
| 29 | Pending count | 0 |
| 30 | Total authoritative | 600/600 |
| 31 | Criterion coverage | 100% (600/600) |
| 32 | Case coverage | 120/120 |
| 33 | Hard-fail rate | 244/588 = 0.4150 (HARD_FAIL_RATE_AUTHORITATIVE; 12 ABSENT_OR_NOT_APPLICABLE rows excluded) |
| 34 | Non-pass rate | 298/588 = 0.5068 (NON_PASS_RATE_AUTHORITATIVE = FAIL + UNRESOLVED + DEGRADED) |
| 35 | Improved criteria vs old baseline | 8 (ROUT-022, ROUT-026, ROUT-047, ROUT-052, ROUT-068, ROUT-088 critical_condition; SAF-009, SAF-019 required_uncertainty) |
| 36 | Regressed criteria vs old baseline | 0 |
| 37 | RC-01 summary | 3 ROUT rows re-bound to repaired comparator; verdicts unchanged (ABSENT confirmed); authority LLM_REVIEWED -> LLM_ADJUDICATED |
| 38 | RC-02 summary | DIS-118 re-derived via frozen kernel; verdict PRESENT confirmed; authority already LLM_ADJUDICATED |
| 39 | RC-03 structural summary | Prior remeasure: structural emission improved, 0 verdict-level route changes; unchanged by this repair |
| 40 | RC-03 semantic summary | Prior remeasure: 0 semantic routing verdict changes (108/108 NO_ACCEPTABLE_ROUTE); unchanged by this repair |
| 41 | SUT rerun | No |
| 42 | Source changed | No |
| 43 | Predictions changed | No |
| 44 | Gold changed | No |
| 45 | New semantic model calls | 0 |
| 46 | Burned classification retained | Yes (BURNED_DEV_BASELINE_ONLY) |
| 47 | Freeze manifest SHA | e3d651054fa473bcdf7168b57dc630fe61eb2f447e8228228a6b74d777b88479 |
| 48 | Hash verification | All pins in input-integrity.json (10 upstream/baseline/kernel pins) and comparator-repair-freeze-manifest.json (10 task-local pins) verified; hashes.txt covers all artifacts except itself and TASK-LOCK.json |
| 49 | STATUS | MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE |
| 50 | Recommended next bounded task | Owner decision on the complete frozen Wave-1 delta (repair-wave backlog, e.g. remaining FAIL families); no fresh holdout, no SUT changes, no certification claims without new owner authorization |

## Metric-name discipline

Distinct names preserved: HARD_FAIL_RATE_AUTHORITATIVE (0.4150) and
NON_PASS_RATE_AUTHORITATIVE (0.5068) are computed live from the frozen
semantic_state mapping. The legacy pre-Wave-1 38.61% triage headline was not
resurrected and is not comparable to these denominators (588 applicable rows).

## Verdict delta vs upstream Wave-1 state

- ABSENT 63 -> 66 (+3: ROUT-026, ROUT-031, ROUT-037)
- PRESENT 2 -> 3 (+1: DIS-118)
- PENDING (None) 4 -> 0 (-4)
- Semantic states: PASS 287 -> 290, FAIL 243 -> 244, UNRESOLVED 18,
  DEGRADED 36, ABSENT_OR_NOT_APPLICABLE 12; applicable denominator 584 -> 588.

## Anti-consensus-hunting provenance (spec §16)

Free-text rationale is stochastic explanatory material and is not part of the
semantic observation. The semantic primitives (criterion_semantic_match,
speaker_commitment) are the authoritative observation. Both Sol passes were
independently validated (schema, enum, packet binding, evidence verbatim)
before any consensus question was asked. No additional model calls were used
after observing the mismatch: the comparator was repaired mechanically and
replayed over the already-frozen observations. The repair is justified by the
semantic authority structure of the measurement contract, not by a preference
for the resulting numbers.

## Integrity

- Upstream lineage (measurement-v3-wave1-residual-llm-adjudication-v1) untouched: 10-file hashes.txt re-verified byte-identical.
- Pre-Wave-1 burned baseline (e73bbb86...8861cf) untouched and used only read-only for the transition matrix.
- No historical artifact rewritten; old rule strings preserved verbatim in consensus-rule-provenance.json.

## Terminal lock

TASK-LOCK.json is CLOSED with terminal status
`MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE`. Its
`terminal_manifest_sha256` pins
`complete-wave1-measurement-results.json` (the terminal authoritative
artifact). The lock file's own SHA-256 is recorded in the session report
(owner chat log and Obsidian), not inside the lock itself, to avoid a
self-referential unverifiable hash.
