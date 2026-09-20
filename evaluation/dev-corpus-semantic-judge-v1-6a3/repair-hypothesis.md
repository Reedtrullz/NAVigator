# Repair Hypothesis (V1.6A.3)

Pre-implementation, frozen. Generic-gate hypothesis for the V1.6A.2 official-80 precision failure (0.7027 < 0.99).

## Hypothesis

The 11 false deterministics reduce to four abstain-able structural ambiguity families plus one deterministic polarity-scope defect, all addressable by generic gates without touching V1.6A.1 out-of-inventory or V1.6A.2 clause-locality invariants:

1. Quote spans co-occurring with out-of-quote commitment signals (3 non-dispute cases) -> ABSTAIN.
2. Parenthetical-only commitment (1 case) -> ABSTAIN.
3. Single-candidate multi-polarity without retraction resolution (2 cases) -> ABSTAIN.
4. Competing hedges across candidates (1 case) -> ABSTAIN.
5. Conditional-antecedent negation mis-scoped to the route proposition (1 case, deterministic fix) -> HYPOTHETICAL_ONLY.

The remaining 4 failures are gold/contract boundary disputes (OFF-SAME-17, OFF-SCOPE-08, OFF-SCOPE-09, OFF-SCOPE-16) and are explicitly not repair targets; they are disclosed, not tuned, and cap the achievable burned official-80 score.

## Prediction

After the gates: burned-120, targeted-60 and official-80 pass precision >= 0.99 with zero false deterministics among non-disputed cases; disputed cases remain disclosed failures; coverage may fall. New TDD fixtures (>=30) reproduce families 1-5 as RED on the A.2 engine before the fix.

## Falsification

If any burned cascade run shows a new false deterministic, or the new TDD suite cannot reproduce at least one family as RED, the hypothesis fails -> stop per contract sections 23/28.
