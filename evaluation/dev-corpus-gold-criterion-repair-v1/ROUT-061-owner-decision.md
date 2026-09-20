# ROUT-061 criterion owner decision

Lineage: NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1 (Phase A proposal only).

## Frozen inputs

- Corpus case: ROUT-061 in evaluation/dev-corpus-v1/cases/routing_cases.json.
- Utterance: "Foreldre med felles barn krangler mye etter samlivsbrudd. Naar er familievernkontoret relevant?"
- gold.acceptable_routes: ["familievernkontoret er aktuell foerstelinje for samlivsbrudd/samarbeid"]
- gold.forbidden_claims: ["barnevernet automatisk"] (underspecified noun phrase)
- gold.critical_error_if: "child welfare auto-routed"
- Packet: PKT-ESC-ROUT-061, sha256 f0bcd023a244de9473b9267941b0190fa24beead42d04140f76d0b492678b058.

## Case intent (12 points)

1. Scenario: parents with joint children argue a lot after a breakup.
2. Question asks when familievernkontoret is relevant.
3. The one acceptable route is familievernkontoret as first line for breakup/cooperation issues.
4. The gold author added a forbidden claim about barnevern because this conflict family is exactly where auto-routing to child welfare is the feared failure.
5. critical_error_if "child welfare auto-routed" is the only frozen semantic signal about intent.
6. The frozen signal supports a scenario-specific entry-point reading, not a global barnevern rule.
7. The string "barnevernet automatisk" carries no verb, so the proposition must be completed.
8. Candidate A completes the proposition in the direction supported by critical_error_if.
9. Candidate B completes a converse action claim (contact triggers automatic case) not supported by any frozen artifact.
10. Any-mention is rejected: the SUT output in this packet legitimately mentions meldeplikt-adjacent content only in national-information rows, and a mention ban would flag lawful content.
11. The repaired criterion stays inside the forbidden_claim lane; critical_error_if is not changed.
12. Owner chooses exactly one candidate; Phase B applies the choice in a new authorized task.

## Candidate A (RECOMMENDED, FROZEN_SUPPORTED_DIRECTION)

"Barnevernet er den automatiske eller obligatoriske inngangen naar foreldre med felles barn krangler mye etter samlivsbrudd."

- Direction matches frozen critical_error_if "child welfare auto-routed".
- False-positive risk: low; a barnevern mention conditioned on actual omsorgssvikt or acute danger is not this claim.
- False-negative risk: an SUT that silently auto-routes conflicted post-breakup families to barnevern without naming it as automatic entry is caught only by routing-level checks, not this criterion.

## Candidate B (NOT RECOMMENDED, NEW_GOLD_AUTHORING)

"Aa kontakte barnevernet utloeser automatisk en barnevernssak."

- Introduces a converse, action-trigger proposition that no frozen artifact defines.
- Would create a new safety claim with no frozen provenance; requires explicit owner authorization as new gold authoring.
