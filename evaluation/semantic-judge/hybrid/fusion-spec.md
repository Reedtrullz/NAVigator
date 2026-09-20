# Fusion spec - FROZEN v1.0 (2026-09-02, before reviewer benchmarking)

Decision flow per claim:

    1. polarity_engine_v02.judge_claim (frozen deterministic engine)
    2. auto_gate.auto_gate(claim, source, result)  [hybrid/auto_gate.py v0.1]
         None            -> AUTO verdict (engine verdict is final)
         reason string   -> semantic review
    3. semantic review (reviewer.py, evidence packet, no browsing)
         verdict accepted only if ALL of:
           - proof fidelity passes (all span ids exist in packet)
           - SUPPORTED/CONTRADICTED require >=1 matching span id
           - confidence >= operating threshold (operating-thresholds.md)
           - verdict does not contradict a deterministic HARD finding
         else -> REVIEW_REQUIRED

## Frozen auto-accept gate list (generic, no claim IDs)

Routing to review when any of:

* compound_claim: >1 atom with any proof verdict
* engine_review_flag / not_a_proof (PARTIAL, INSUFFICIENT, ERROR)
* weak_support_rule: support_lexical_rescue
* weak_contra_rule: exhaustive_list_exclusion, incompatible_dates,
  neg_object_conflict, cost_axis_opposition,
  concept_opposition:free_of_charge
* compound_numeric_conflict: numeric_bound_conflict with >=2 numbers
* support_undercovered: >=2 uncovered content tokens vs best span
* support_weak_span: 1 uncovered token and span score < 0.6
* numeric_support_binding: SUPPORT claim contains numbers/dates/ages
* first_person_locality_unverified: "min/mitt/var kommun*" claim with
  no first-person marker in source
* causal_claim: "fordi" in SUPPORT claim

## Hard-fact priority (spec 8)

Engine CONTRADICTED via rules NOT in the weak list (numeric_conflict,
numeric_bound_conflict single-number, numeric_cap_conflict, polarity_conflict,
concept_opposition non-cost, modality_matrix_conflict, modifier_antonym,
universal_vs_exception family, staff_negation_contra, age_disjoint,
recipient_disjoint, requirement_opposition, option_vs_duty_opposition,
date_anchor_conflict, division_of_function, exclusivity_conflict) is FINAL.
The reviewer may never override these to SUPPORTED/PARTIAL.

## Reviewer precedence

The reviewer may refine AUTO_PENDING cases only.  It may upgrade
INSUFFICIENT/PARTIAL to SUPPORTED/CONTRADICTED only with valid span
evidence from the packet.  REVIEW_REQUIRED is a first-class outcome.
