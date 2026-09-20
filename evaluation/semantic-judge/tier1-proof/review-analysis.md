# Review analysis (spec 21/31) - SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS

Scope: dual-labelled rows (n=80), gate over 389 frozen rows. Baseline vs Tier-1 fused finals, post-fix rerun (qualifier/date/aggregate gates applied).

## Review finals (REVIEW_REQUIRED) trajectory

- Baseline: 27 total; 6 dual-labelled. All 6 necessary under the contract (semantic or proof truth = INSUFFICIENT/REVIEW_REQUIRED posture).
- After Tier-1: 30 total; 9 dual-labelled. All 9 necessary. 21 non-dual review finals unchanged (not contract-evaluated).
- Net review growth: +3, all retractions of unsafe baseline auto decisions (N-A4, N-R1, ENT-C): doctrine proof_safe=INSUFFICIENT and no Tier-1 operator produced a validator-passed proof; spec 14 sends them to REVIEW_REQUIRED. This is safety repair, not new review load.

## Reviews eliminated

- Review-path rows moved to auto: 1 (ACT-25, actor-scope). INSUFFICIENT baseline -> DIRECT_ASSERTION validator-passed SUPPORTED, correct against dual semantic truth (SUPPORTED). Precision 1/1 for Tier-1 SUPPORTED moves.
- Correctly eliminated: 1/1. Unsafe eliminated: 0.

## Remaining reviews

- Necessary remaining (dual): 9/9. Unnecessary remaining (dual): 0.
- Gate slice metric (remaining_necessary/unnecessary on baseline-review dual rows): necessary 1, unnecessary 5 - see final-report point 37 and Tier-2 pool note; these 5 are annotation-doctrine gaps (semantic decided, proof-safe INSUFFICIENT), not reviewer error.

## Safety bought vs coverage bought

- Invalid accepted proofs after: 0. Critical auto errors after: 0 (baseline criticals N-R1 and ENT-C retracted).
- Coverage bought: 1 row. No safety-for-coverage trade was made: retractions bought safety (invalid 3 -> 0, critical 2 -> 0) at +3 review finals.
- Semantic accuracy on dual rows: 45/80 before and after (stable; retraction rows went to REVIEW, which is contract-appropriate).

## Verdict

Review-reduction value is not yet meaningful (1 row). Safety gates all pass. Conservative retraction-heavy posture is contract-correct but must be an explicit product decision before Tier-2 (spec 60).
