# Final report - NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_2-UNCERTAINTY-CONTRACT-REPAIR

## Terminal status

**SEMANTIC_JUDGE_V1_2_ANNOTATION_CONTRACT_NOT_READY**

Human uncertainty contract PASSED (Set B 20/20), but the fresh official
80-fixture dual blind annotation failed the hard agreement gates (overall
70/80 = 87.5% < 95%; route 16/20 = 80% < 95%; uncertainty 16/20 = 80% < 95%).
Per spec section 28: official model validation was NOT started. No frozen
gold exists; the auto-generated gold file is preserved as
judge-validation-gold-v1-2.UNFROZEN.json.

## What was completed

1. Historical baselines intact: 17/17 artifacts MATCH at start and at close
   (V1 corpus/scorer/judge, V1.1 lineage, adapter/integration).
2. V1.1 80-set marked BURNED_CONTRACT_DEVELOPMENT_DATA
   (burned-data-registry.json); no reused text in any V1.2 set.
3. Human uncertainty contract repair: Set A 18/20 (gate fail) ->
   one bounded clarification (4 points) -> Set B 20/20 = 100%,
   SAT<->NR = 0, PARTIAL<->UNRESOLVED = 0, 0 schema failures. All section 20
   Set B gates PASS.
4. Contract frozen: semantic-judge-contract-v1-2.json
   (SHA 5747d8d1b70b1f5879235dadf1b746efc86dac9029dbb541534718da07bd815b),
   result schema, fixture-design rules, annotation instructions.
5. V1.2 judge implemented with applicability-first uncertainty schema,
   invalid-combination guards, evidence-span validation, frozen retry/fail-
   closed policy.
6. Model calibration (section 23, separate synthetic 16-fixture set):
   13/16 = 81.25%. All 3 misses were diagnostic-gold issues, not prompt
   deficiencies; uncertainty dimension 4/4 correct. Prompt frozen UNCHANGED
   before official fixtures were built
   (prompt-freeze-v1-2.json, bf7cc31bc8e0e164156832e84608474a80ee040e2485282ff10247881db9b610;
   prompt_hash 08c57c44c57507f29e8336997b44cc87fd5a1e3d18997c0d0cb42a43b055a785).
7. Fresh official 80 fixtures built (judge-validation-fixtures-v1-2.json,
   SHA 51bcc8e21138f840d5a451bc4fcfd9328f025aabb40b9c897add91b1ac777918):
   Critical 20 (10/10 TRIGGERED/NOT), Forbidden 20 (10/10),
   Route 20 (5 per label incl. rule-1 UNRESOLVED),
   Uncertainty 20 (5 per label incl. negative-requirement NOT_REQUIRED).
8. Dual blind labeling completed (160 calls): 70/80 overall.
   Per dimension: critical 20/20 = 100%, forbidden 18/20 = 90%,
   route 16/20 = 80%, uncertainty 16/20 = 80%. 0 schema failures.

## Gates

| Gate (section 28) | Required | Result | Status |
|---|---|---|---|
| Overall agreement | >=95% | 87.5% | FAIL |
| Critical agreement | >=90% | 100% | PASS |
| Forbidden agreement | >=90% | 90% | PASS (at boundary) |
| Route agreement | >=95% | 80% | FAIL |
| Uncertainty agreement | >=95% | 80% | FAIL |

## Root causes of the 10 disagreements

Pattern 1 (route, 4 cases OJ-RT-16/17/19/20): pass 1 resolves vague or
contradictory offers to a definite NO_ACCEPTABLE_ROUTE or PARTIAL, pass 2
answers UNRESOLVED. All 5 designer-UNRESOLVED route fixtures split exactly
on this boundary. This is a residual contract-level vagueness boundary that
the V1.1 route rule did not fully close for "negated or contradicted
offer" fixtures.

Pattern 2 (uncertainty, 4 cases OJ-UN-09/10/13/19): pass 1 assigns
applicability NO / NOT_REQUIRED where pass 2 assigns YES and a verdict.
UN-19 is the sharpest: the criterion phrase "krever at svaret ikke
konkluderer at tilbudet mangler" sits exactly on the avklaring-1 boundary
(is "no missing-offer conclusion" a negative requirement = NO, or a
limitation that must be expressed = YES?). This is a genuine residual
ambiguity in the frozen contract's applicability test.

Pattern 3 (forbidden, 2 cases OJ-FB-09/17): PRESENT vs ABSENT and
PRESENT vs UNRESOLVED on implicit universal claims ("du slipper all
dokumentasjon", "gratis for en hver person"). Pass-level phrasing
sensitivity, lower severity.

## Non-claims

- No official model validation was run (one-shot, stability, scorer freeze
  all skipped per the gate failure).
- No frozen gold exists for V1.2.
- No historical artifact was modified (17/17 baseline SHAs verified MATCH
  at close).
- V1.1 route collapse stands; V1/V1.1 statuses preserved unchanged.

## Recommended next bounded stage

A V1.3 contract clarification task (single bounded clarification, same
protocol as V1.2) should resolve exactly two boundary questions, with
calibration fixtures designed for them:

1. Applicability vs negative-requirement boundary for criteria that
   require the SUT NOT to draw a conclusion ("ikke konkluder at X"):
   is the required non-conclusion an uncertainty limitation that must be
   expressed (applicability YES) or a negative exposure requirement (NO)?
2. The vagueness/contradiction boundary for offered routes: when an
   identifiable offer is followed by self-negation or is otherwise
   undermined, is the label decided by the expressed offer (NO_ACCEPTABLE_
   ROUTE) or by the undecidability of what was offered (UNRESOLVED)?

After Set-B-style PASS, re-run the same official 80-fixture flow (fresh
fixtures not required if SHAs are re-verified, but a fresh uncertainty
subset replacing the applicability-boundary fixtures is recommended).
