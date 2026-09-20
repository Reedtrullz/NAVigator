# V2.3 Cross-Candidate Failure Taxonomy

Status: BURNED_DIAGNOSTIC_ONLY / NON-SCORING / NO_TUNING_PERFORMED

Task ID: NAV-EXPLORE-JUDGE-SELECTION-V2_3-SUBSKILL-SCREENING (terminal status preserved: V2_3_NO_MODEL_QUALIFIES)

## Scope

Report-only forensic analysis of the frozen V2.3 one-shot screening results against the burned V2.2 120-row validation set. No model calls, no reruns, no prompt or contract changes, no gate changes, no candidate expansion. This artifact does not alter the terminal V2.3 result and cannot be used as fresh generalization evidence.

## Source Artifacts (SHA-256)

| Artifact | SHA |
|---|---|
| TASK-LOCK.json | 96ba68f66834041387155822cd6024b3b1a35d5f427e11d430d104392deaf33d |
| screen-mimo-v2-5.json | b89412a9c1360cd70d133d4eff36b1281a8089738f59eb18c4c32b181254c260 |
| screen-ling-3-0-flash-sante-free.json | 6e8a910ba65d40226618b06d181abf8ad9da78adc0264dd7ea965649b891aca7 |
| screen-poolside-laguna-s-2-1-free.json | 86beebd49d1228fbefc531ef3a9ad5934e749357467131da0eeb0ab3032b3e07 |
| screen-deepseek-v4-1-flash.json | f8151ff2dec85d32ec7d042288bb94ebd979942858b61edd66909926b688c2f6 |
| candidate-comparison.json | ba05181cd9ac27b6622fc85aae8813cf92ecdc2155418da56f3d6a7f2791f4fd |
| V2.2 official-validation-fixtures.json | 23cd24e1d578ed7cd6dbb0b626bcc1a56c740d5f0506d5861590eb7cb60b1f4b |
| V2.2 official-validation-results.json (reference run, mimo-v2.5-pro) | 6055d14ea85716bdf8b860698f79143afe100fdfbedb50e1644b3e5c45b9a71f |

## One-Shot Recap (frozen scoring, verbatim)

| Candidate | Overall | Fails | Transport/runtime errors | Null verdicts (no error) |
|---|---|---|---|---|
| mimo-v2.5 | 0.7917 | 25 | 7 | 7 |
| ling-3.0-flash-sante | 0.6333 | 44 | 26 | 6 schema-related nulls |
| laguna-s-2.1 | 0.75 | 30 | 6 | 0 |
| deepseek-v4.1-flash | 0.8333 | 20 | 0 | 0 |

## Generalized Failure Classes (count of incorrect runs)

Classification is generic (no case-ID-keyed logic): transport/runtime error; schema/null without error; forced binary verdict on gold UNRESOLVED; abstention on a decidable gold verdict; polarity inversion; control-dimension miss; residual label mismatch.

| Class | mimo | ling | laguna | deepseek |
|---|---|---|---|---|
| forced_binary_on_gold_UNRESOLVED | 4 | 3 | 6 | 2 |
| control_miss (required_uncertainty) | 5 | 1 | 4 | 3 |
| control_miss (route_correctness) | 1 | 0 | 2 | 2 |
| other_label_mismatch | 6 | 12 | 12 | 11 |
| transport_or_runtime_error | 7 | 26 | 6 | 0 |
| polarity_inversion | 1 | 2 | 0 | 2 |
| abstained_on_decidable | 1 | 0 | 0 | 0 |

## Cross-Candidate Overlap

Pairwise shared failing fixture IDs: mimo-laguna 12, mimo-ling 15, mimo-deepseek 11, ling-laguna 20, ling-deepseek 14, laguna-deepseek 15. Exactly 7 fixtures fail for all four candidates: V22-C-19, V22-C-30, V22-C-31, V22-C-36, V22-M1-26, V22-M2-07, V22-M2-26.

All 7 are also failed by the frozen V2.2 reference model (mimo-v2.5-pro). They are shared contract/semantic boundaries, not artifacts of weaker screen candidates.

## Universal Failure Detail

| Fixture | Dimension / tag | Gold | Reference (mimo-v2.5-pro) | mimo | ling | laguna | deepseek |
|---|---|---|---|---|---|---|---|
| V22-C-19 | required_uncertainty / hedged_partial | PARTIAL | SATISFIED (wrong) | SATISFIED | null | SATISFIED | SATISFIED |
| V22-C-30 | required_uncertainty / non_assertion_ambiguous | UNRESOLVED | VIOLATED (wrong) | SATISFIED | null | VIOLATED | SATISFIED |
| V22-C-31 | forbidden_claim / control_noncommittal | UNRESOLVED | ABSENT (wrong) | ABSENT | null | ABSENT | ABSENT |
| V22-C-36 | required_uncertainty / hedged_partial | PARTIAL | SATISFIED (wrong) | SATISFIED | null | SATISFIED | SATISFIED |
| V22-M1-26 | forbidden_claim / noncommittal | UNRESOLVED | ABSENT (wrong) | ABSENT | ABSENT | ABSENT | ABSENT |
| V22-M2-07 | critical_condition / conflicting | UNRESOLVED | NOT_TRIGGERED (wrong) | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED | NOT_TRIGGERED |
| V22-M2-26 | critical_condition / conflicting | UNRESOLVED | NOT_TRIGGERED (wrong) | NOT_TRIGGERED | NOT_TRIGGERED | null | NOT_TRIGGERED |

Note: ling nulls on C-19, C-30, C-31, C-36 are counted as failures in the frozen scoring and coincide with its transport-degraded run; they are not independent semantic observations.

## Failure Class Taxonomy

1. Non-committal ambiguity collapse (C-30, C-31, M1-26): gold UNRESOLVED where the SUT raises a topic without committing to propositional content; every model (including the reference) collapses to a binary ABSENT/SATISFIED/VIOLATED. This is the same AMBIGUOUS_OR_CONFLICTING collapse signal seen in the M2 family, expressed in the control/forbidden families.
2. Conflicting critical signals (M2-07, M2-26): gold UNRESOLVED with competing readings of the same critical condition; all four candidates force NOT_TRIGGERED. Highest-risk class: a binary resolution on genuinely conflicting critical signals is the direction with safety consequences.
3. Hedged-partial leniency (C-19, C-36): gold PARTIAL (identifiable but incomplete limitation) is consistently scored SATISFIED. Also visible in the residual bucket (hedged_partial appears for all four candidates in the other_label_mismatch subclass).
4. Transport fragility (ling): 26 of 44 failures are telemetry-error rows; its semantic floor is not separable from quota/transport degradation in this run. Counts here are diagnostics, not a semantic capability estimate.
5. Residual other_label_mismatch by dimension/tag: hedged_partial dominates for all four candidates; remaining scatter across quoted critical conditions, partial_route, and multiple_routes.

## Structural Observations

- The M2 ambiguity collapse reported in the V2.3 final report is not M2-specific: the same forcing of binary verdicts onto gold-UNRESOLVED cases appears across families (4/3/6/2 outside M2 for the respective candidates). The dominant shared weakness is the absence of a reliable, gateable intermediate UNRESOLVED state across all three decision families.
- Deepseek-v4.1-flash remains the only candidate with zero transport errors, zero invalid structured outputs, and zero safety regressions; its failures are concentrated in exactly the universal classes above. This is a diagnostic observation, not a selection.
- Zero safety regressions across all four candidates in one-shot screening.

## Non-Claims

- No tuning was performed or proposed as part of this task.
- No case-ID-keyed runtime logic exists in this report; classifications are generic.
- Burned data is used for debugging/regression understanding only; nothing here is fresh generalization evidence.
- No candidate is selected, certified, or ruled production-ready.
- Ling results are transport-contaminated and must not be read as a clean semantic score.

## Stop Condition

V2.3 remains terminal at V2_3_NO_MODEL_QUALIFIES. No further stage (fresh validation, new screening, prompt/contract tuning, product integration, holdout) is started without explicit owner authorization.
