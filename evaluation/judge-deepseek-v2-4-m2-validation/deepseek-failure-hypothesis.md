# DeepSeek Failure Hypothesis (spec section 1)

Observed in frozen V2.3 burned screening (screen-deepseek-v4-1-flash.json,
gate-extraction-deepseek-v4-1-flash.json):

- structured validity 1.0, evidence-span validity 1.0, derivation consistency 1.0
- critical FN 0, invalid rows 0, strongest overall 0.8333
- failed 6/14 gates; dominant weakness: M2 gold-UNRESOLVED correct rate 0.2143
  (forced TRIGGERED 1, forced NOT_TRIGGERED 6 among 7 gold-ambiguous rows)

Hypothesis under test: DeepSeek-v4.1-flash treats AMBIGUOUS_OR_CONFLICTING /
INSUFFICIENT_TO_DECIDE evidence as a request to decide, collapsing deliberately
ambiguous critical evidence into binary verdicts, instead of honoring
UNRESOLVED as a correct terminal classification under the frozen V2.2
contract. The model otherwise follows structure, span grounding, and safety
recalls perfectly.

Calibration intent: make the decision order and the terminal status of
UNRESOLVED explicit for ambiguous/conflicting/insufficient evidence, without
creating a general "prefer UNRESOLVED" bias - clear cases must stay binary.

This document is diagnostic; no contract, label, or scoring change is allowed.
