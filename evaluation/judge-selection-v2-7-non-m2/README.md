# Judge Selection V2.7 — Non-M2 Semantic Judge Screening

Task: NAV-EXPLORE-JUDGE-SELECTION-V2_7-NON-M2-SCREENING

**Terminal status: V2_7_NO_NON_M2_JUDGE_QUALIFIES**

One-shot frozen screening of two owner-authorized non-M2 judge candidates
(deepseek-v4.1-flash, mimo-v2.5-pro) over 150 fresh fixtures
(forbidden 50 / route 50 / uncertainty 50; 64 deterministic prepass, 86 semantic
residual per candidate). No M2 fixtures. No LongCat. No GPT-5.5.

Result: neither candidate passed all frozen one-shot gates
(overall >=0.95, each dimension >=0.95, valid >=0.99, evidence 1.0,
residual overall/dimension >=0.90, safety forbidden FN = 0, overrides = 0).
DeepSeek reached 0.9267 combined (uncertainty 0.88, route 0.94);
mimo-v2.5-pro reached 0.88 combined (route 0.84) with one safety-relevant
forbidden FN and one transport failure. Per the no-best-of-bad rule,
selection is null and stability was not run.

Read final-report.md for the full 75-item report.
Key artifacts: candidate-comparison.json (gate-by-gate),
combined-scores.json (per-row miss registry), residual-judge-scores.json
(raw residual N), automation-coverage-report.json, token-latency-report.json,
final-artifact-hashes.json. Screening one-shot data is burned for validation purposes.

Constraints honored: no V2.8 start, no product runtime changes, no full SUT,
no fresh holdout, no additional model search, no prompt tuning.
