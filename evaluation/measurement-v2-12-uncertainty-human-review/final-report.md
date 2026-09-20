# V2.12 Final Report - Uncertainty Human-Review Lane

Task ID: NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE
Campaign: AFK MEASUREMENT-SYSTEM CAMPAIGN, Stage 2C (Branch B)
Date: 2026-09-14

## 1. Context and trigger

V2.11 (fresh non-M2 candidate screening) reached terminal status
V2_11_NO_NON_M2_JUDGE_QUALIFIES: both candidates failed preregistered
calibration gates (iter-2: ling 0.84, laguna 0.80, both < 0.90 required; zero
overcommit each). Per the frozen campaign contract, Branch B moved semantic
uncertainty judgment to a human-review lane built on the frozen V2.7E
uncertainty contract. No candidate was re-scored, no gate lowered, no new
candidate added.

## 2. Architecture

- Runtime: review_lane_uncertainty_v2_12.py (stdlib only, no network, no model)
- Derivation: uncertainty_derivation_v2_7e.py imported unmodified from the
  frozen V2.7E lineage via sys.path; never reimplemented or edited here
- Contract version: semantic-judge-contract-v2-7e (pins re-verified)
- States: HUMAN_REVIEW_REQUIRED -> HUMAN_REVIEW_PENDING ->
  RESOLVED | INVALID | DISAGREEMENT -> (adjudication) -> RESOLVED
- Fail-closed properties: no final verdict without a valid human review;
  duplicate reviewer rejection; adjudicator must not see model outputs;
  leakage fields rejected at packet creation; evidence spans verbatim in SUT
  output (live lane keeps strict verbatim validation)
- Dual-blind agreement signature: (mode, behavior, compound components)

## 3. Verification evidence

- Workflow tests: 40/40 PASS (derivation paths incl. UNC-A1/UNC-A2 and frozen
  V1.4 compound rule, invalid-review paths, state machine, routing/provenance/
  invariants)
- Burned replay: 92/92 PASS. V2.7E Set A 32/32 (both blind passes replayed);
  V2.8 uncertainty subset 60/60. Pre-registered normalized span rule used to
  map historical V2.8 gold spans to verbatim SUT substrings (documented in
  run_burned_replay_v2_12.py docstring); live lane unchanged (strict verbatim)
- Fresh workflow: 60 fixtures PASS on all hard gates: routing 100%, packet
  validity 100%, ingestion 100%, derivation 100%, provenance completeness
  100%, automated-verdict-before-review = 0, deterministic rerun stable,
  pending fail-closed probe PASS, leakage-rejection probe PASS
- Leakage audit: 0 findings; runtime guard rejects every forbidden case key
- Provenance audit: complete on all 179 resolved cases across the three suites
- Process audit: frozen replay inputs unchanged (SHA match); fresh workflow
  rerun idempotent; burned replay re-executed clean inside the audit

## 4. Harness deviations found and fixed (pre-freeze)

- FW12-056/057 fresh fixtures initially expected PARTIAL for a
  PARTIAL+VIOLATED compound; the frozen V1.4 compound rule yields UNRESOLVED
  there. Fixture expectations corrected; derivation module untouched.
- Pending fail-closed probe initially checked the wrong collection. Probe
  helper fixed.
No lane runtime change was driven by observed labels; all fixes were
harness-side and made before the first recorded PASS.

## 5. Terminal status

UNCERTAINTY_HUMAN_REVIEW_LANE_READY

All development gates for this stage pass. Uncertainty automated authoritative
verdicts are removed from the measurement system; the uncertainty dimension is
human-review only with mechanical derivation.

## 6. Campaign continuation

Stage 2D is pre-authorized by the AFK campaign contract:
NAV-EXPLORE-JUDGE-SELECTION-V2_13-FORBIDDEN-ROUTE-SPECIALIST (candidates:
deepseek-v4.1-flash, mimo-v2.5-pro; fresh fixtures forbidden 80 + route 80;
gates: combined >= 0.97, residual >= 0.93, safety forbidden FN = 0; stability
40x3 >= 0.95). No fresh product holdout and no full SUT in this stage.

## 7. Limitations

- The lane has no automated semantic judgment; throughput is bounded by human
  review capacity by design.
- The normalized span rule applies only to burned V2.8 replay provenance; live
  review ingestion requires strict verbatim spans.
- V2.7E Set A labels carry no evidence spans; span fidelity is validated on
  workflow fixtures, fresh fixtures, and the V2.8 subset.

