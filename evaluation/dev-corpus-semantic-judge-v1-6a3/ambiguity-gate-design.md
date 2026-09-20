# Ambiguity Gate Design (V1.6A.3)

Status: FROZEN before implementation. Strategy: PRECISION_FIRST + CONSERVATIVE_ABSTENTION.

## Placement

Generic ambiguity gates run inside _route_rules AFTER clause-locality (BC_ROUTE_CLAUSE_LOCALITY_01), same-clause competition (BC_ROUTE_AMBIGUOUS_02), and BEFORE the polarity label firing block. Each gate is a generic Norwegian linguistic rule; no fixture IDs, no exact sentence matching.

## Gates

### G1 QUOTE GUARD (BC_ROUTE_QUOTE_SCOPE_04)
Fires ABSTAIN when the output contains a quote span AND at least one out-of-quote commitment-relevant signal (assertion, hedge, negation, retraction, conditional marker) that the quote scope does not mechanically resolve. Exceptions preserved: (a) quote adoption conflict (CMT-AB-01 / TDD-QUOTE-02) already handled by existing higher-priority rules; (b) plain QUOTED_ONLY outputs with no out-of-quote signals (CMT-Q-*, VR-Q-*, TDD-QUOTE-01) stay QUOTED_ONLY. Disputed quote boundaries (attributed bare quote, single bare guillemet output) are gold/contract boundary cases and intentionally NOT patched.

### G2 PARENTHETICAL GUARD (BC_ROUTE_PAREN_SCOPE_05)
Fires ABSTAIN when ALL route candidates and ALL commitment operators sit inside parentheses. A parenthetical aside with out-of-parenthesis grounding stays deterministic.

### G3 SINGLE-CANDIDATE MIXED POLARITY GUARD (BC_ROUTE_MIXED_POLARITY_04)
Fires ABSTAIN when exactly one route candidate collects 2 or more distinct labels from {ASSERTED, NEGATED, HEDGED_ASSERTION, HYPOTHETICAL_ONLY} and no retraction rule resolves the output to SELF_RETRACTED. Retraction binding (VR-R-*/CMT-R-* pattern) has priority and keeps SELF_RETRACTED. OFF-SCOPE-05 and OFF-SCOPE-17 land here.

### G4 HEDGE COMPETITION GUARD (BC_ROUTE_HEDGE_COMPETITION_06)
Fires ABSTAIN when 2 or more candidates are hedge-licensed and hedge/candidate pairing is not uniquely resolvable (hedge markers bind to 2 or more different candidates, or 2 or more hedged clauses carry different candidates). Replaces the single HEDGED_ASSERTION collapse seen on OFF-SCOPE-19. Clean single-candidate hedge (CMT-H-*) unaffected.

### G5 CONDITIONAL-ANTECEDENT NEGATION REFINEMENT (deterministic, family A)
NEGATED (BC_ROUTE_NEGATED_01) must not fire when the negation occurrence is preceded, within the same clause, by a conditional marker (hvis/dersom). In that frame the negation scopes the antecedent condition, not the route proposition; HYPOTHETICAL_ONLY from the conditional marker stands. Fixes OFF-ADV-12 without touching clean negations (CMT-N-*, VR-N-*).

## Non-goals

- No retraction-definition change (OFF-SAME-17 stays a contract boundary).
- No trailing-qualifier rule (OFF-SCOPE-09 stays a contract boundary).
- No attributed-bare-quote rule (OFF-SCOPE-08) and no bare-quote-output rule (OFF-SCOPE-16).
- No coverage tuning; precision first, abstain is desired behavior for structural ambiguity.
