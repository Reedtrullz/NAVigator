# Capability proof - assertion strength as a deterministic boundary feature

Classification: PRE-IMPLEMENTATION HYPOTHESIS FREEZE (auth section 4).
Written before any A4 code. If fresh validation later contradicts the
precision claims below, the layer fails closed via ABSTAIN, and the
terminal status must reflect NOT_READY, not a rule patch.

## Question

Can assertion strength / endorsement strength be separated deterministically,
with very high precision, from information the classifier already has
or can derive without a new semantic model?

## Answer: YES, as a bounded amplifier layer - with named residual risks

The A3 engine already derives the core signal. It detects
assertion/hedge/negation/retraction/conditional/quote markers, segments
clauses (_clauses), binds operators to candidates per clause
(_route_rules G-gates and clause-local grounding), and resolves quote
spans (_quote_spans). What A3 does NOT yet do is apply that machinery to
the forbidden-claim dimension, which the V1.6B diagnostic showed is
where assertion-strength failures concentrate (F-23/26/27: a forbidden
conclusion asserted via conditional consequent, epistemic hedge, or
belief-verb still counts as PRESENT; hedged/negated/quoted/hypothetical
forms do not).

A4 reuses the identical mechanism on the prohibited-claim dimension:
1. Detect the prohibited claim surface from the criterion (claim terms
   provided by the frozen criterion object - no invention).
2. Segment clauses with the frozen _clauses().
3. Find the strongest commitment operator in the claim's clause chain.
4. Map operator class to assertion strength.

## State enum and mechanism

- ASSERTED: claim clause has an assertive operator, no competing frame.
- HEDGED_ASSERTION: epistemic hedge over the assertive matrix.
- REPORTED_ATTRIBUTED: third-party attribution marker over the claim.
- QUOTED_ONLY: claim surface inside detected quote spans.
- HYPOTHETICAL_ONLY: explicit conditional frame, consequent not asserted.
- NEGATED: negation scopes the claim in the same clause.
- SELF_RETRACTED: claim asserted, then explicitly retracted; retraction
  resolves polarity (A3 retraction-binding pattern).
- VAGUE_NONCOMMITTAL: no claim surface, only vague helper vocabulary.
- ABSTAIN: 2+ distinct commitment frames, claim terms in quotation with
  out-of-quote operators, parenthetical-only scope, or no signal - all
  reusing the A3 G1/G2/G3/gate logic verbatim.

## New signal A4 adds (beyond A3 lexicons)

Belief-verb lexicon (tror, mener, antar, regner med, er overbevist om)
and first-person hedge lexicon (jeg tror, jeg mener, vi antar, jeg regner
med). Precision limits, documented before implementation:

1. First-person drop risk: "Jeg tror ikke ..." = negated belief. Mitigated
   by A4-N1: negation inside a first-person hedge clause flips to NEGATED
   (same-sentence negation binding, frozen pattern). Residual risk: an
   unusual negation spelling bypasses it; then the state is WRONG only if
   fresh validation contains that form. Accepted, monitored.
2.REPORTED-vs-ASSERTED contrast risk: "Jeg mener at X" is an assertion;
   "Han mener at X" is a report. Mitigated by A4-N2 first-person lexicon
   gating; cross-checked against third-party lexicon (disjoint matches
   required, else ABSTAIN). Residual risk: unknown first-person variants.
   Fail-closed: no first-person match + third-party match = REPORTED.
3. Bare belief-verb without subject ("Tror det finnes...") exists in
   colloquial Norwegian. Residual risk accepted: if the subject is absent,
   the form is rare and the fresh-set adversarial stratum will measure it;
   if it misfires, terminal status must reflect it. No subject-verb parser
   is added - that would be the semantic creep authorization section 1
   forbids.

All other signals reuse frozen lexicons only. No new parsing is introduced.

## Why this is not semantics-by-hand

The layer answers only: which commitment operator class binds to the
claim clause, and is the binding unambiguous? That is surface/structural
information, decidable from lexicons + clause segmentation + the already
frozen ambiguity gates. It does not judge whether the claim is true,
probable, or advisable - the semantic judge keeps that. The
abstention-first design (canonical uncertain -> ABSTAIN) keeps the
precision-first contract.

## Capability verdict

CAPABILITY_DETERMINISTIC: proceed to fresh-TDD phase (auth section 6).
Three residual risks are named; each is monitored by fresh validation
strata (CLEAN_RESOLVABLE / REQUIRED_ABSTAIN / ADVERSARIAL_MIXED) and
none is mitigated by a case-specific patch.
