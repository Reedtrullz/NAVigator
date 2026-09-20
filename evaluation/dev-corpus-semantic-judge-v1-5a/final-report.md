# V1.5A Final Report - Judge Model Selection

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_5A-MODEL-SELECTION

TERMINAL STATUS: V1_5A_NO_MODEL_MEETS_SELECTION_FLOOR

## 1. Context and integrity

Prior status: DEV_CORPUS_SEMANTIC_JUDGE_V1_4_NOT_READY.
V1.4 gold SHA c859a851e84957a5a30a296315080ef88ba4f8e39c60a8c5e83669760f7194dc (verified, unchanged).
All 18 files in semantic-judge-manifest-v1-4.json hash-verified (baseline-integrity.json).
Historical writes: 0. Semantic contract unchanged. Prompt unchanged. Gold unchanged.
Fixture count: 100 (frozen order SHA 948fc016...f74fad).
Data classification: BURNED_JUDGE_MODEL_SELECTION_DATA.

## 2. Authorization

Original authorization (display names) and second authorization (wire ids) recorded in
authorization-amendment.json. Ling 3.0 Flash Sante and Laguna S 2.1 became testable
after the user made them available on the router; both wire ids were live-verified
(presence only). GPT-5.5 never used. No silent escalation.

## 3. One-shot benchmark results (100 fixtures each, burned data)

| Metric | LongCat 2.0 | MiMo v2.5 Pro | Ling 3.0 Flash Sante | Laguna S 2.1 |
|---|---|---|---|---|
| Valid structured results | 97/100 (0.97) | 100/100 (1.00) | 80/100 (0.80) | 15/100 (0.15) |
| Overall accuracy | 0.866 | 0.840 | 0.8375 | 0.800 |
| Critical | 0.92 | 0.92 | 0.84 | 1.00 (n=1) |
| Critical FN | 0 | 0 | 0 | 0 |
| Forbidden | 0.92 | 0.92 | 0.92 | 1.00 (n=2) |
| Safety forbidden FN | 0 | 0 | 0 | 0 |
| Route | 0.84 | 0.80 | 0.76 | 0.667 (n=6) |
| Uncertainty | 0.773 | 0.72 | 0.80 (n=5) | 0.833 (n=6) |
| Invalid evidence spans | 1 (R-19) | 0 | 0 | 0 |
| Transport failures (HTTP 429) | 3 | 0 | 13 | 81 |
| Schema failures | 0 | 0 | 7 | 4 |

Frozen baseline (not rerun): mimo-v2.5 overall 0.8265, valid 98/100.

## 4. Selection floor adjudication

Floors: overall/critical/forbidden/route/uncertainty >= 0.95, critical FN 0,
safety FN 0, valid rate >= 0.99, evidence validity 1.0.

All four candidates pass the hard safety filter (0 critical FN, 0 safety FN).
NO candidate passes the full floor set. Closest: mimo-v2.5-pro
(overall 0.84, uncertainty 0.72; also fails route 0.80).
Best-of-bad selection is forbidden (contract section 22).

## 5. Stability screen

Not triggered: preregistration allows it only for candidates passing ALL one-shot
floors. 0 of 4 qualified. No stability data generated; no majority-vote repair.

## 6. Failure clusters (frozen taxonomy, applied uniformly)

- critical_false_positive: C-04 (LongCat, Ling, MiMo Pro), C-09 (all 4), C-15 (all 4), C-19 (Ling). Hedged or second-hand critical content is read as asserted.
- forbidden_claim_state_error: F-10, F-20 misclassified by every candidate, in different directions.
- vague_route_error: R-12 hit all four candidates.
- hedged_route_error: R-18 (all but Laguna), R-17/R-24 (Ling, LongCat).
- hypothetical_route_error: R-16 (LongCat, Ling, MiMo Pro).
- quoted_route_error: R-03 (Laguna only).
- route_semantic_equivalence_error: R-10 (LongCat, Ling, MiMo Pro).
- limitation_confusion_hedge_explicit_partial: U-10, U-12, U-14, U-22 across candidates.
- compound_uncertainty_error: U-16, U-20, U-24.
- non_assertion_ambiguity_error: U-13 (LongCat, MiMo Pro).
- self_retracted_error, critical_false_negative, forbidden_false_negative, evidence_span_paraphrase_failure: 0 for all candidates.
- Transport: LongCat 3x429 (U-23..U-25), Ling 13x429 tail (U-13..U-25) plus 7 schema failures (U-01..U-10), Laguna 81x429 (rate-limited almost the entire run).
- Shared root causes: (1) hedge vs assertion boundary on critical/forbidden content; (2) absence of positive route commitment misread as NO_ACCEPTABLE_ROUTE; (3) PARTIAL vs SATISFIED on limitation requirements.

## 7. Token / latency telemetry

- LongCat: completion median 864, p95 2011, max 3610; latency median 17.0s, p95 36.2s; completion total 96,288.
- MiMo Pro: completion median 1034, p95 2841, max 4378; latency median 18.1s, p95 44.9s; completion total 127,553.
- Ling: completion median 417, p95 1541, max 3407; latency median 2.4s, p95 6.9s; completion total 50,015.
- Laguna: completion median 77, p95 99, max 135; latency median 2.3s, p95 2.8s; completion total 1,175 (15 valid rows only).
No finish_reason=length anywhere; max budget fraction observed 0.134 (MiMo Pro).

## 8. Transport adjudication

Frozen retry policy was applied once per row; no substantive reruns were performed.
LongCat fails floors mathematically on 97 valid rows (0.866 overall), so its 429 tail
does not change the outcome. Ling and Laguna fail the valid-rate floor outright
(0.80 / 0.15 vs 0.99); their incomplete coverage is itself disqualifying. No model
was rescued or rerun.

## 9. Decision

Selected model: NONE. V1.5B eligibility: none.
No fresh validation, no prompt tuning, no contract repair, no full SUT, no product holdout.

## 10. Remaining limitations and next bounded stage

- MiMo v2.5 Pro remains the strongest measured judge but is far from the 0.95 floors; uncertainty (0.72) and route (0.80) are the weak dimensions.
- The hedge-vs-assertion and vague-route boundaries are contract/model interaction problems, not transport problems; V1.3 contract semantics already define these cases, so candidate models systematically violate them.
- Recommended next bounded stage: separate model-strategy decision (stronger candidates, or contract-preserving deterministic pre-classification for the boundary cases), THEN a new V1.5A-style burned screen, THEN V1.5B fresh validation only when a candidate clears floors.
