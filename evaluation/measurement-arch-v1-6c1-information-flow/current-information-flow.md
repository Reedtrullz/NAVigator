# V1.6B Current Information Flow (end-to-end)

Task: NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR
Status: MEASUREMENT DOCUMENT (no runtime change)

## Pipeline

case/output -> deterministic scorer -> A3 -> residual judge request -> semantic judge -> parser -> score

Source artifacts (frozen, SHA-verified in baseline-integrity.json):

- pipeline-contract-v1-6b.json (frozen 2026-09-11T18:58:52Z)
- run_screening_v1_6b.py (V1.6B screening runner)
- boundary_preclassifier.py (A3, sha 21047fda...)
- judge_core_v1_4.py (frozen judge core, sha ad7f0fda...)

## Boundary 1: case/output -> deterministic scorer

Fields available: id, ctx (case context), crit (criterion text), sut (candidate
answer), dimension, stratum, criterion_struct (required_limitations,
prohibited_conclusions; present for 25/30 uncertainty rows).

Retained downstream: ctx, crit, sut, dimension, stratum.
Forkastet: nothing (scorer is the origin of the split).

## Boundary 2: deterministic scorer -> A3

The runner calls A3 classify() on the SUT text (route dimension: always;
uncertainty dimension: only when criterion_struct indicates
EXPLICIT_LIMITATION-mode, i.e. req and not prohib).

Fields produced by A3 per dimension:

- label (e.g. ASSERTED, HEDGED_ASSERTION, HYPOTHETICAL_ONLY, QUOTED_ONLY,
  NEGATED, SELF_RETRACTED, HEDGE, EXPLICIT_LIMITATION, NONE, ABSTAIN)
- rule_id (which fired rule)
- evidence_span (verbatim substring located by the rule, or null)
- abstained (bool) + reason (e.g. MIXED_POLARITY_CONFLICT,
  UNGROUNDED_ROUTE_CANDIDATE, NO_HIGH_PRECISION_RULE,
  HEDGE_COMPETITION, QUOTE_SCOPE_AMBIGUITY, PARENTHETICAL_SCOPE_AMBIGUITY)
- conflict (structured: competing labels/nouns/clause indices)
- deterministic: true
- confidence: DETERMINISTIC_HIGH (when not abstaining)

## Boundary 3: A3 -> residual judge request

THIS IS THE INFORMATION BOUNDARY.

The judge request is built by judge_core_v1_4.build_user_prompt() and contains
exactly four payload fields:

    dimension, labels, required_output_keys, case_context (ctx),
    gold_criterion (crit), candidate_answer (sut)

Of the A3 structure, only the routing DECISION survives:

- route dimension: A3 abstain -> row sent to judge; A3 non-abstain
  non-evaluable label -> row resolved deterministically (never reaches judge);
  A3 ASSERTED/HEDGED_ASSERTION -> row sent to judge.
- uncertainty dimension: A3 non-abstain EXPLICIT-mode behavior -> resolved by
  frozen derive table (never reaches judge); A3 abstain -> row sent to judge.

Fields DROPPED at this boundary (present before, gone after):

1. a3_route_label / a3_unc_label (mechanical read of what the rule saw)
2. a3_route_reason / abstain reason (WHY the deterministic layer stepped aside)
3. a3 conflict structure (competing labels, clause indices, grounded nouns)
4. a3 evidence_span (the exact substring the rule bound its label to)
5. rule_id (which of the ~30 high-precision rules fired)
6. assertion_scope dimension (always computed, never forwarded)
7. criterion_struct (the deterministic decomposition of the criterion; judge
   receives only the raw crit text)

Fields the judge must RECONSTRUCT from raw prose:

- clause boundaries (A3 _clauses() already computed them)
- quote/negation/retraction/hedge spans (A3 marker hits already located them)
- route candidates and their inventory grounding (A3 ROUTE_TERMS + inventory
  check already resolved them)
- which route proposition carries the commitment

## Boundary 4: judge -> parser -> score

Parser validates schema, derives verdicts mechanically from judge primitives
(EXPL_ROWS / NONASSERT_ROWS), checks evidence spans verbatim. Fields parsed:
verdict, route_proposition_present, route_speaker_commitment,
uncertainty_requirement_mode, uncertainty_output_behavior / compound_components,
evidence_spans, note. Deterministic derivation cannot be overridden by the
model (LLM_OVERRIDE_OF_DETERMINISTIC_RESULT = 0, hard invariant).

## Measured loss (V1.6B one-shot, 120 rows)

- 92/120 rows reached the judge (28 resolved deterministically pre-A3).
- For every one of those 92 rows, the full A3 output (label, rule_id, span,
  reason, conflict) was discarded; judge saw only raw ctx/crit/sut.
- Judge had to re-derive clause structure, scope, and commitment from raw
  Norwegian prose with no mechanical hints.

## Key implication

The deterministic layer already KNOWS (mechanically, no semantics added) the
answer to most structure questions the judge struggles with: where clauses
end, where the hedge/negation/quote markers sit, which noun is a route
candidate, why it abstained. The current flow throws that away and forces the
model to redo the work probabilistically. This is the candidate information
loss this task tests via the A/B experiment.
