# V2.9 Root-Cause Analysis (burned data)

Status marker: BURNED_DATA_ROOT_CAUSE_ANALYSIS. Source: V2.9 official one-shot
results and fixtures (screening-results-*.json, screening-fixtures.json in
evaluation/judge-selection-v2-9-non-m2-post-diagnostic/). Not generalization
evidence. No model calls were made for this analysis.

## Headline finding

16 of 19 substantive misses across both candidates (84%) are PARTIAL-collapse:
the judge output PARTIAL where the contract demands a definite pole in either
direction. PARTIAL acts as a gravitational middle label under uncertainty.

| Pattern | Gold | Model | Count |
|---|---|---|---|
| Overcommit on mandated UNRESOLVED | UNRESOLVED | PARTIAL | 12 |
| Undercommit on clear positives | ACCEPTABLE | PARTIAL | 4 |
| Other route | PARTIAL | NO_ACCEPTABLE_ROUTE | 1 |
| Forbidden detection miss | PRESENT | ABSENT | 1 |
| Overcommit to other definite | UNRESOLVED | SATISFIED | 1 |

(Counts cover DeepSeek 7 substantive misses + MiMo 12 substantive misses;
MiMo transport/schema rows V29-ROUTE-36 and V29-UNC-53 are excluded as
non-semantic per frozen policy.)

## Uncertainty taxonomy (12 UNC miss events across 9 distinct fixtures)

1. Self-contradictory limitation: SUT asserts a limitation, then retracts or
   contradicts it (V29-UNC-30, 44, 48). Contract: UNRESOLVED. Models credited
   the limitation language without processing the retraction.
2. Unclear prose: hedged/garbled text where the limitation status is genuinely
   unclear (V29-UNC-37, 38, 39, 42). Contract: UNRESOLVED. Models output
   PARTIAL, i.e. they treated "hedge detected" as "partial credit".
3. Compound with an unclear component (V29-UNC-43, 45 + overlaps above).
   Contract compound rule gives UNRESOLVED; models averaged components.

This is model behavior under the human-stable V2.7E contract (Set B agreement
20/20 on the same boundaries), not a contract defect.

## Route taxonomy (4 ACCEPTABLE-to-PARTIAL misses)

V29-ROUTE-26, 29, 30 are clear_acceptable fixtures: direct imperative
assertion of the criterion route. Both models demoted to PARTIAL. The frozen
iteration-2 route-granularity clarifications plausibly overcorrected: models
now require stricter route-identity matching than direct paraphrased
assertions satisfy. This is a symmetric failure to the overcommitment bias.

## Architecture consequence (hypothesis, preregistered for next task)

Both failure classes are mechanically detectable with high precision and
belong in the frozen deterministic/boundary layer per the measurement
architecture:

1. CONTRADICTORY_LIMITATION: limitation asserted then retracted/contradicted
   within the SUT. Detection is lexical/structural; ABSTAIN on doubt.
2. DIRECT_ROUTE_ASSERTION: criterion route asserted imperatively by its
   canonical name in the SUT. Detection is string-structural; ABSTAIN on
   paraphrase or hedge.

Extending the boundary layer with these two conservative classes shrinks the
judge residual to the genuinely semantic middle, and a symmetric
PARTIAL-discipline prompt rule (PARTIAL requires a grounded partial-satisfaction
finding; never a hedge fallback; never a demotion of a direct assertion)
addresses the residual judge behavior. Both are bounded, testable changes.
Neither is authorized yet.

## Prerequisite pin verification (2026-09-13, post-terminal, read-only)

All five frozen upstream pins from TASK-SPEC-DRAFT.md section 2 re-verified at
artifact level (SHA-256 over file bytes), independent of the draft:

- deterministic_scorer_v1 8d36606861bb... MATCH
- deterministic_scorer_contract 94d8146272e7... MATCH
- a3_boundary_preclassifier_v1_6a3 21047fdaaa4... MATCH
- v2_7e_uncertainty_contract 7648039ea57... MATCH
- v2_6_m2_human_review_manifest e2513c3dcee... MATCH

Result: measurement-architecture success criteria 1-3 (deterministic layer,
boundary layer, M2 human-review lane) have artifact-grade frozen evidence in
addition to the V2.9 behavioral evidence. Criterion 4 remains open pending
owner authorization of a rescreen task.
