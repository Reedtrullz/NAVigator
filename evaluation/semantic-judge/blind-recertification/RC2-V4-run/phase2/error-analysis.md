# Error Analysis (post-freeze)

Produced only after official-score freeze (e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2).

146/160 cases fail at least one exact metric (14 fully correct). Per-case
detail: error-analysis.json. Severity uses the frozen general policy:

## Severity

* CRITICAL: 3 (false auto-SUPPORTED: RC2B-0058, RC2B-0136, RC2B-0030)
* HIGH: 0 (no false auto-CONTRADICTED)
* MEDIUM: 63 (unnecessary REVIEW_REQUIRED on cases expecting an auto decision)
* LOW: 80 (semantic/proof miss without unsafe auto decision)

## Root-cause categories (mechanical)

* compound_decomposition 38 (atom coverage/verdict mismatches on compound cases)
* compound_top_level 25 (compound top-level product/semantic miss)
* review_vs_abstain 26 (expected ABSTAIN_INSUFFICIENT, predicted REVIEW_REQUIRED - frozen policy keeps these separate; 25 of these are the dominant MEDIUM mass)
* reviewer 26 (reviewer output disagrees with sealed target after engine was already correct/neutral)
* reviewer_route 16 (route gating below threshold / not-entailing / insufficient)
* engine_parser 14 (engine-only path wrong; includes 3 known negation/skal-kan misses)
* fusion_or_difficulty 9

## Dominant failure mass

Over-review: RC2 never reached an auto decision on 63 of the 95 cases the
frozen key expects to be auto-actionable (39 AUTO_SUPPORTED + 40
AUTO_CONTRADICTED + 26 ABSTAIN - the 26 abstains are review-vs-abstain
by architecture). The 17 accepted auto decisions are 82.35% precise
(14/17); the three misses are all false SUPPORTED on contradiction-bearing
claims (negation / deontic flip).

Compound atom accuracy is 25.53% (36/141) mostly because RC2 emits fewer
atoms than the sealed canonical decomposition (35 of 62 compound cases
have missing expected atoms; extra unmatched predicted atoms: 0).

## RC3_BUG_CANDIDATE (scorer view defect, not RC2)

Frozen scorer semantic confusion matrix drops the 103 predicted-REVIEW
cells due to a counter-key mismatch (REVIEW_REQUIRED_PREDICTED_ONLY vs
REVIEW_REQUIRED). Metrics/gates unaffected. Fix scorer view in RC3, do
not retro-edit official-score.json.
