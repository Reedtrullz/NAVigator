# Lane H Cheap Model Diagnostic V1 - Report

Task: NAV-EXPLORE-LANE-H-CHEAP-MODEL-DIAGNOSTIC-V1
Classification: DEVELOPMENT_DIAGNOSTIC_ONLY. Reference = AI_PROPOSED_REFERENCE (Reading B). Disagreement with the reference is not by itself a model error, and nothing here is gold, certification, or production readiness.

## Frozen setup (verified before first call)

- Run manifest SHA-256: fad27195b04c9131a46e3bbb4561a8a2e421f349824912217fbfac0ef47aa69e (frozen before first call; created 2026-09-19T22:55:49Z).
- Dataset pin f3e11e83..., AI proposals pin 8b1dad2c..., decision note e2e0a126..., contract view 11965d72..., reference manifest b033aae9... all re-verified this session.
- Wire IDs: command-code/xiaomi/mimo-v2.5-pro and B.AI/deepseek-v4-flash-vision-exp. Gateway model_reported matched the requested wire ID on every row (no reroute).
- Prompt: frozen semantic_instructions.system_prompt + contract-view label definitions; schema critical_evidence_state / evidence_spans / rationale. The model never saw reference labels, alternatives, flags, or view assignment.
- Views: A = 109, B = 41 (B = rows where the AI reference flagged label_clarification_required; alternative labels reported separately, not counted as extra correct).
- Reference distribution: CLEAR_TRIGGER_SUPPORT 30, CLEAR_NON_TRIGGER_SUPPORT 79, AMBIGUOUS_OR_CONFLICTING 30, INSUFFICIENT_TO_DECIDE 11.

## Execution

- MIMO: 150/150 rows attempted, 150 registered. Statuses: 115 OK, 24 INVALID_JSON, 11 INVALID_MODEL_REVIEW. Invalid outcomes are final and were logged as observed, not repaired or re-prompted.
- DeepSeek: 150/150 attempted, 150 registered, all 150 OK (json_mode on; the preregistered 400/422 fallback was never needed).
- Transport events: 0. Technical retries used: 0. Budget respected: <=150 primary calls per route, <=15 retries total (0 used).
- Auth via local proxy Bearer; no secret values printed or persisted. No Astra / Sol / Luna / GPT-5.5 / Jev / consensus calls; 0 subagents; no paid calls.

## Results vs AI reference (exact label match)

| Route | Planned N | Valid | Match | Match/planned | Match/valid |
|---|---|---|---|---|---|
| MIMO full | 150 | 115 | 76 | 50.7% | 66.1% |
| MIMO view A | 109 | 81 | 62 | 56.9% | 76.5% |
| MIMO view B | 41 | 34 | 14 | 34.1% | 41.2% |
| DeepSeek full | 150 | 150 | 104 | 69.3% | 69.3% |
| DeepSeek view A | 109 | 109 | 99 | 90.8% | 90.8% |
| DeepSeek view B | 41 | 41 | 5 | 12.2% | 12.2% |

The B-view gap is dominated by disagreement between the AI reference and its own flagged alternative labels, not by one model behavior. Paired over B (34 rows both valid): MIMO proposed-label hits 14, alternative hits 16, other 4; DeepSeek proposed-label hits 4, alternative hits 29, other 1.

## Paired comparison (115 rows both valid)

- Both match reference: 62 (53.9%)
- Only MIMO matches: 14
- Only DeepSeek matches: 16
- Both deviate with the same label: 16
- Both deviate with different labels: 7
- Missing/invalid on at least one side: 35 rows (24 MIMO INVALID_JSON + 11 MIMO INVALID_MODEL_REVIEW)

## Main deviation patterns (reference x model)

- MIMO: spreads verdicts across CLEAR_TRIGGER_SUPPORT / CLEAR_NON_TRIGGER_SUPPORT / AMBIGUOUS_OR_CONFLICTING, and 12 of 30 AMBIGUOUS-reference rows are labeled CLEAR_TRIGGER_SUPPORT. Its invalid-JSON rate (24/150) is a real reliability cost.
- DeepSeek: close on view A (99/109), but 26 of 30 AMBIGUOUS-reference rows are labeled CLEAR_TRIGGER_SUPPORT, and 9 of 11 INSUFFICIENT_TO_DECIDE rows become CLEAR_NON_TRIGGER_SUPPORT. Structurally it commits to a concrete label far more often than the reference.
- Both models find the AMBIGUOUS_OR_CONFLICTING reference rows hardest (3/30 exact each). That boundary is the strongest candidate for a future clarification pass if the owner authorizes one.

## Latency and usage (valid rows)

| Route | Median | p95 | Max | Tokens (prompt/completion/total) |
|---|---|---|---|---|
| MIMO | 26.5 s | 48.8 s | 60.4 s | 66,821 / 188,043 / 254,864 |
| DeepSeek | 16.1 s | 22.6 s | 54.9 s | 98,104 / 108,826 / 206,930 |

Cost basis: included local-proxy access; observed billing UNKNOWN (not $0).

## Limits and non-claims

- 150 rows are not 150 independent scenarios (scenario grouping exists upstream); percentages are diagnostic, not generalization claims.
- The reference is an AI proposal, not human gold; agreement is not accuracy.
- No gold freeze, no tier-ladder decision, no router training, no prompt tuning, no runtime changes, and no third-model adjudication were performed. per-row-comparison.jsonl and disagreements-vs-ai-reference.jsonl preserve every disagreement for later human review.

## Terminal status

DIAGNOSTIC_COMPLETE
