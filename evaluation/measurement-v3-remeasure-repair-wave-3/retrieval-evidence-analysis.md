# Wave-3 Retrieval and Evidence Analysis

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-3 measurement, frozen Wave-2 measurement, product-diagnostics.json, routing-funnel.json.

## Claim and provenance (unchanged from Wave 2)

Claims total: 625 in both waves; every claim has a provenance entry. Provenance-linked claims: 369/625 (59.0 %) in both waves.

## Evidence completeness (unchanged)

Per-case evidence scores: 23 cases at 0.0, 97 cases at 1.0 (W2 identical). 100 % claim provenance coverage coexists with 0 route PASS, so evidence attachment alone does not make routes usable.

## Forbidden-claim lane (contamination proxy)

Forbidden FAILs: 3 -> 3. W3 failures: DIS-100 (PRESENT, LLM_REVIEWED; contamination-shaped "Fant ingen registrerte kommunale tilbud..." inside cross-contaminated national-information blocks), DIS-119 (CLAIM_PRESENT), ROUT-042 (CLAIM_PRESENT), both deterministic lexical, unchanged since Wave 1.

Verdict distribution W2 -> W3: ABSENT 57 -> 58, CLAIM_ABSENT_TAKEN 59 -> 59, PRESENT 1 -> 1, CLAIM_PRESENT 2 -> 2; ROUT-026::forbidden:01 moved PENDING -> ABSENT (LLM_ADJUDICATED), completing the 600/600 authoritative set.

## Presentation mechanisms (unchanged)

- Cases with 2+ "Nasjonal informasjon" blocks: 103/120 (W3), same as W2. Duplicate/repeated national-information noise persists mechanically.
- presented_as_complete with recoverable failures: 104/120; no_route_asserted: 92/120; epistemic: 104 EXISTENCE_ONLY, 16 UNVERIFIED.
- Runtime: 120/120 SUCCESS, 0 crashes, 0 terminal failures, 104 RECOVERABLE.

## Verdict

Retrieval and evidence state is materially unchanged from Wave 2. The W3 repair targeted route emission, not retrieval; no retrieval contamination reduction, evidence gain, or presentation-noise reduction was expected or observed. RC-04 (binding) and RC-06 (presentation) remain indicated.

