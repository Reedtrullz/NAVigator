# RC2 Numeric-Binding Audit

## Root cause (live-reproduced)

_numeric_contra (v0.2 wrapper in polarity_engine_v02.py) fired on
ANY same-unit bound pair with disjoint intervals inside the aligned
atom span:

- RC1B-0005: claim "full sats 2 572 kr/mnd" collided with "1 286 kr"
  (the halved rate) from the same source row -> hard CONTRA on a
  SUPPORTED claim.
- RC1B-0086: same-pair logic on a conjunction (3-month deadline +
  6-month total) -> CONTRA on an internally consistent claim.

## Fix (Iteration A)

1. Qualifier-set equality (_same_predicate_phrase): full/hel/halv/
   halvert/delt/dobbelt/total markers must match on both sides, else
   the pair is a different quantity -> no CONTRA.
2. Claim-value attestation skip (_attests_same_subject): if the exact
   claimed value is attested in the source under the same subject
   vocabulary, the mismatched number is a different quantity, not a
   contradiction. Cross-subject citations (the ordinaer rate cited
   inside an utvidet claim, RC1B-0003) do NOT count; phrase
   extraction treats newlines as boundaries so section headers cannot
   leak into an attestation phrase.
3. Line-474 family: _UNIT_EQ/_unit_eq unit normalization in
   polarity_engine.py; diff-claims require the claimed difference to
   be attested elsewhere (fail-closed).

## Regression evidence

- numeric_conjunction + agg_component + full_divided groups: all pass
  (37/37), including the new cross-subject-citation pin.
- Post-fix burned outcomes: 0005 SUPPORTED (correct), 0086
  INSUFFICIENT_EVIDENCE (fail-closed, correct), 0003 CONTRADICTED
  (correct).

