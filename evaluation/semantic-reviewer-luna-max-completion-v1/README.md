# NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-MAX-COMPLETION-V1

Terminal status: **NO_LUNA_REVIEWER_CONFIG_QUALIFIES_CONFIRMED**

This lineage completed the previously unexecuted LUNA-MAX full-qualification
branch (Stage-2 dual pass + Stage-3 stability-if-passed) inherited byte-for-byte
from the frozen predecessor
`NAV-EXPLORE-SEMANTIC-REVIEWER-LUNA-QUALIFICATION-V1`.

Outcome summary:

- LUNA-MAX ran the exact frozen Stage-2 dual-pass protocol on both lanes:
  forbidden_claim (294 calls) and critical_condition (160 calls).
- forbidden_claim: FAIL. All 4 core gates exceeded; EDGE agreement 0.9333
  passed the 0.92 floor but 4 errors exceeded the <=2 gate.
- critical_condition: FAIL. 70/80 rows INVALID_MODEL_REVIEW, consensus
  coverage 30/80, 11 consensus errors, safety-subset agreement 23/23 rows with
  8 errors, 1 catastrophic false-trigger escape.
- No lane passed Stage 2, so Stage-3 stability was protocol-correctly not run
  (`max-stability.json` = NOT_RUN_NO_LANE_PASSED_STAGE_2).
- Router proposal: PRIMARY remains GPT_6_ASTRA_LOW for both lanes;
  activation_authorized = false.
- Tokens: MAX completion 544 calls / 2,013,177 total tokens including the
  frozen screening baseline vs frozen LUNA-HIGH 544 calls / 2,014,991
  (ratio 0.999). MAX reasoning did not reduce cost and did not qualify.
- 0 new HIGH calls, 0 Astra/Sol/GPT-5.5 calls, 0 fresh cases, no historical
  mutation, no gate/prompt/config changes.

Entry points: `final-report.md` (40-point report), `max-full-qualification.json`
(frozen scoring), `token-cost-comparison.json`, `proposed-review-router.json`,
`hashes.txt` (all artifacts except TASK-LOCK), `TASK-LOCK.json`.
