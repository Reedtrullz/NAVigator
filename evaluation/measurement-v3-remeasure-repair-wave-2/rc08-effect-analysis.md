# RC-08 Effect Analysis - Retrieval Scoping

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-2 measurement (wave2-measurement-freeze-manifest.json, 2026-09-16T15:50:42Z), frozen Wave-1 measurement, frozen Candidate-2 structural diagnostics (evaluation/full-sut-repair-wave-2-v1/structural-replay-diagnostics.json). No SUT rerun; no source, prediction, gold, or Measurement V3 change.

## Mechanical contamination reduction (observed)

- Claims total: 645 (Wave 1) -> 625 (Wave 2). Every claim in both waves has a provenance entry.
- Provenance-linked claims: 308/645 (47.8 %) -> 369/625 (59.0 %).
- Structured route cases with provenance: 20/20 (gate PASS); zero structured-route cases without provenance.
- Cross-track contamination proxy (Wave-1 metric definition retained): same-track INFO blocks are not counted; cases with 2+ "Nasjonal informasjon" blocks remain 103/120, so duplicate/repeated national-information noise persists mechanically.
- Mechanism gates overall: PASS (junk-route labels 0, structured-route-without-provenance 0, no-route consistency mismatches 0; fragment-like labels 2 recorded).

MECHANICAL_CONTAMINATION_REDUCTION: PARTIAL. Retrieval scoping improved claim-level provenance linkage and satisfied all frozen mechanism gates, but multi-block national-information noise and fragment-like route labels persist.

## Semantic measurement improvement (observed)

Forbidden-claim lane (the lane where contamination-shaped failures previously dominated):

- Verdict distribution Wave 1 -> Wave 2: ABSENT 63 -> 57, CLAIM_ABSENT_TAKEN 48 -> 59, PRESENT 2 -> 1, CLAIM_PRESENT 3 -> 2.
- Forbidden FAILs: 5 -> 3. Improvements: DIS-105 and DIS-116 (both FAIL -> PASS, deterministic lexical). DIS-105 moved CLAIM_PRESENT -> CLAIM_ABSENT_TAKEN.
- Remaining FAILs: DIS-100 (PRESENT, LLM_REVIEWED; contamination-shaped text "Fant ingen registrerte kommunale tilbud..." inside cross-contaminated national-information blocks; also failed in Wave 1), DIS-119 and ROUT-042 (both CLAIM_PRESENT, deterministic lexical, unchanged from Wave 1).

Critical-condition lane: CRITICAL_ERROR 91 -> 81, NOT_TRIGGERED 10 -> 21. The net semantic direction is positive but includes 2 true PASS -> FAIL under-triage candidates (see rc11-safety-analysis.md).

SEMANTIC_MEASUREMENT_IMPROVEMENT: CONCENTRATED_IN_FORBIDDEN_LANE. Two contamination/lexical forbidden failures resolved; the remaining forbidden failures are 1 contamination-shaped and 2 unchanged deterministic lexical findings. Aggregate canonical improvement is 31 improved vs 9 regressed criteria (primary Wave1 -> Wave2 matrix), with 8 of 9 regressions in critical_condition.

## Separation statement

The mechanical retrieval effects (provenance linkage, mechanism gates) and the semantic measurement effects (forbidden verdict shifts, aggregate transitions) are reported separately above. Provenance existence is not semantic correctness: route correctness remains 0 PASS and evidence completeness remains 23/120 at 0.0 despite 100 % claim provenance coverage.

## RC-08 verdict

Implemented as scoped. Effect is real but bounded: forbidden-lane semantic improvement plus mechanical provenance gains; route-lane and multi-block presentation mechanisms are untouched and remain the dominant residual mechanisms.
