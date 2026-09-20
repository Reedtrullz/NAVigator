# FINAL REPORT - NAV-EXPLORE-MEASUREMENT-V3-ASTRA-REVIEW-BATCH-1

Date: 2026-09-15/16. Transport: local proxy, bearer from auth.json (never printed/persisted).

## Execution

- Owner authorization: explicit (astra review lane). Owner amendment during execution: reasoning effort LOW, not max. Recorded in TASK-LOCK and config.
- Inputs verified before execution: repaired corpus, batch-2 manifest, 74/74 packet body hashes (sha256 of JSON minus packet_sha256, sort_keys, ensure_ascii=False), frozen order, leakage audit. Pins in input-integrity.json.
- 148 model calls (74 x ASTRA_A + ASTRA_B), model gpt-6-astra, effort low, JSON mode. One TRANSPORT_ERROR (PKT-ESC-ROUT-053 ASTRA_B) retried once per frozen transport policy; retry OK. No other retries; no substantive reruns.
- Runbook incident (transport only): the first background process survived an isolated tool failure and a second process wrote duplicate records; both were stopped, files were deterministically deduplicated (first record per packet+pass retained), and the remainder was completed with a single controlled process. No packet or result content was affected and no verdicts were re-run.

## Quality metrics

| Metric | Value |
|---|---|
| Packets total | 74 (10 critical_condition, 64 forbidden_claim) |
| Valid ASTRA_A | 70 |
| Valid ASTRA_B | 71 |
| Exact semantic agreement (LLM_CONSENSUS) | 64 |
| LLM_REVIEW_DISAGREEMENT | 3 (DIS-109, DIS-118, ROUT-041) |
| Packets with at least one invalid pass | 7 |
| Invalid pass reasons | 1 non-verbatim span (ROUT-085 ASTRA_A); 6 enum violations (speaker_commitment null at NO_MATCH: DIS-109-F01, ROUT-021-F02, ROUT-025, ROUT-038-F02, ROUT-063, ROUT-066) |
| Empty-span legal cases | 104 (NO_MATCH / non-CLEAR states; contract-accurate) |
| Missing required spans | 0 |

Agreement by lane: critical_condition 8 agree / 1 disagree / 1 invalid; forbidden_claim 56 agree / 2 disagree / 6 invalid.

Consensus label distribution: critical_evidence_state CLEAR_NON_TRIGGER_SUPPORT 4, INSUFFICIENT_TO_DECIDE 3, CLEAR_TRIGGER_SUPPORT 1; criterion_semantic_match MATCH 10, NO_MATCH 46; speaker_commitment NEGATED 8, UNRESOLVED 46, ASSERTED 2.

## Integrity

    SUT_RERUN = false
    PREDICTIONS_CHANGED = false
    GOLD_CHANGED = false
    PACKETS_CHANGED = false
    AI_RESULTS_MISREPRESENTED_AS_HUMAN = false

No gold comparison was performed during generation. No forced consensus, no majority voting. Disagreements and invalid passes are preserved in human-adjudication-packet.json (optional human adjudication set; not populated with AI decisions).

## Terminal status

ASTRA_REVIEW_BATCH_COMPLETE_AWAITING_INTEGRATION

Hard stop: no SUT tuning, no criteria change, no disagreement retries, no baseline integration, no fresh holdout without new owner authorization.
