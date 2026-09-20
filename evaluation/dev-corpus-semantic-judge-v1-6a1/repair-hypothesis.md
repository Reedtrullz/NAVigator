# Frozen Repair Hypothesis (V1.6A.1)

Frozen before any code change (2026-09-11).

> The pre-classifier must not emit a deterministic route-commitment
> classification solely from a vague route construction when the purported
> service noun cannot be grounded in the classifier's recognized service/route
> inventory or another frozen high-precision grounding rule.

This is NOT a special case for VR-H-08.

## Generalized mechanism

In the frozen V1.6A rule set, `BC_ROUTE_VAGUE_01` is the only route rule that
can fire without an inventory route-term hit. Any out-of-inventory service
noun combined with generic help/support language therefore produces a
deterministic `VAGUE_NONCOMMITTAL` classification even though the classifier
cannot ground the noun in its route inventory. Deterministic precision
requires abstention in that state.

## Planned minimal repair (new lineage only)

1. New generic rule `BC_ROUTE_UNKNOWN_SERVICE_01` (priority 25):
   an unrecognized Norwegian service noun (stems `tjenest`, `kontor`,
   `senter`, `sentral`, `team` occurring in a word that no `ROUTE_TERMS`
   hit covers) with NO inventory route term in the text fires
   `ABSTAIN_CONFLICT` above hedge (20) / asserted (10) / vague (5) and below
   hypothetical (30) / retracted (50) / quoted (60) / quote-conflict (65).
   The rule is evaluated only when no inventory route term is present.
2. `BC_ROUTE_QUOTED_01` and `BC_ROUTE_HYPOTHETICAL_01` guards extend from
   `route` to `route or unknown_service`, so independent high-precision
   quote/hypothetical grounding of an unknown noun still resolves.
3. Hedged and asserted pathways remain inventory-grounded: an unknown noun
   with hedge/assertion wording abstains.
4. Uncertainty and assertion-scope dimensions are untouched.
5. Conflict policy is untouched: top-priority single `ABSTAIN_CONFLICT`
   resolves to `ABSTAIN`; no priority hack to recover coverage.

Pre-checked collision surface (mechanical scan over 67 unit + 120 burned
fixtures, before implementation): contains-based stem matching with
inventory-coverage exclusion touches only `VR-H-08` (the intended defect)
and `VR-AB-04` (already expected `ABSTAIN`; only the abstain reason field
changes, label unchanged). No unit-suite route fixture is touched.
