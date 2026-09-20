# Decision: Tier-2 GO/NO-GO (specs 26/27/28)

## Threshold (defined first, spec 27)

Tier-2 should not be prototyped if realistic expectation is only 1-2 additional auto decisions in the 389-row development corpus, or less than 2 percentage points of review-rate reduction, unless the operator is extremely simple and low-risk.

## Measured result against threshold

- Realistic headroom: 1 additional auto decision (CAL015), 0.26 pp review-final-rate reduction (7.71 -> 7.46%).
- Theoretical headroom: 3 additional auto decisions, 0.77 pp.
- Only one operator qualifies as simple and low-risk (RULE_PLUS_CONDITION on CAL015). Its payoff is exactly the case that triggered the threshold's escape hatch, and one case does not clear the 'meaningful number of reviews' condition.

## Verdict

SKIP_TIER2_AND_PREPARE_BLIND_RECERTIFICATION

## Justification

1. 20 of 21 newly annotated review finals are necessary under the contract (evidence missing, genuine semantic reasoning, injection posture, or no safe automation path).
2. The 7 cases that look automatable are Tier-1 implementation-bug candidates (lexicon, lexer, actor equality), not Tier-2 work; they are registered, not fixed (spec 25).
3. The contradiction-side Tier-2 family (7 pool rows) is already emitting auto-CONTRADICTED on the pool rows and carries the highest legal risk; its review-final value is zero.
4. Review-final rate is already 7.71% of the corpus with zero unsafe auto decisions after Tier-1 retractions; the marginal economics of Tier-2 do not clear the bar.
5. Annotation agreement is high on the necessary-review side and the single Tier-2 candidate is clean, but one clean case is headroom, not a mandate.

## Not done here (spec 28)

Blind recertification is NOT started. Holdout-v3 is NOT built. Next step is a separate, explicitly scoped preparation task. Future blind contract confirmed (spec 29): holdout labels must be triple (semantic truth, proof-safe verdict, product expected action) - the dual-label schema in review-final-dual-labels.json is the template.
