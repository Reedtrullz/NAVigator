# Review vs Abstain Contract

ABSTAIN_INSUFFICIENT (final product action, real runtime route):
  The evidence packet gives no proof for the claim or its negation, and there
  is no specific conflict needing human adjudication. Deterministic signals:
  engine NO_PROOF on all atoms AND no context conflict AND no relevant
  contrary sentence with subject overlap. Reviewer must not be able to move
  this to REVIEW by low confidence alone; only NEW evidence or a conflict
  signal re-routes it.

REVIEW_REQUIRED:
  Relevant evidence exists but the case needs bounded inference, ambiguity
  resolution, competing spans, compound adjudication, scope/actor
  interpretation, or another non-auto-safe judgment. Deterministic signals:
  engine review flag, context-guard UNSAFE, valid counter-proof conflict,
  or compound atom requiring review while others are decided.

Classifier (deterministic, reviewer-assisted): rc3_engine/routing.py
classify_route(). Default on ambiguity between the two: REVIEW_REQUIRED
(never silently abstain when evidence is relevant).

Absence doctrine preserved: no-support != contradiction (spec 13).

