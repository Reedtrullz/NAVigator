# Remaining RC-04 / RC-06 Assessment

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-2 measurement and frozen Candidate-2 structural diagnostics. Neither RC-04 (broad uncertainty repair) nor RC-06 (broad renderer cleanup) was implemented in Wave 2.

## RC-04 - uncertainty

Wave-2 required_uncertainty distribution: NOT_REQUIRED 83, PARTIAL 36, VIOLATED 1. Wave 1: NOT_REQUIRED 83, PARTIAL 36, SATISFIED 1.

- The single VIOLATED is ROUT-091 (SATISFIED -> VIOLATED, required_uncertainty PASS -> FAIL, regression severity P2, evidence CERTAINTY_MARKER_WITH_REQUIRED_UNCERTAINTY).
- PARTIAL is unchanged at 36: the uncertainty lane did not improve indirectly.
- Premature absence: W2 deterministic scorer rows carry PREMATURE_ABSENCE / SEMANTIC_JUDGE_STUB evidence in critical_condition rows where W1 carried LLM_REVIEWED NOT_TRIGGERED / UNRESOLVED observations. This is the same judgment-layer boundary RC-04 targets.
- Retrieval/routing/evidence improvements did not indirectly resolve uncertainty semantics: the uncertainty verdict distribution is identical except the one SATISFIED -> VIOLATED swap.

RC-04 remains independently necessary: YES.

## RC-06 - renderer / presentation

Frozen mechanical diagnostics (kept separate from semantic criteria):

- Cases with 2+ "Nasjonal informasjon" blocks: 103/120 (repeated national-information blocks persist after RC-08).
- presented_as_complete_with_failures: 104/120.
- no_route_asserted true: 100/120 (up from 97 in Wave 1).
- Epistemic state distribution: EXISTENCE_ONLY 104, UNVERIFIED 16.
- Duplicate answer blocks and repeated claims were the basis of RC-06's root-cause finding and remain mechanically observable.

RC-06 remains useful after RC-08: YES. RC-08 changed retrieval scoping, not rendering; presentation noise still dominates the answer surface and is a separate mechanism from the semantic failures measured above.

## Boundary statement

The diagnostics above are mechanical observations, not Measurement V3 criteria, except where a frozen dimension is quoted explicitly (required_uncertainty). No repair is implemented in this task.
