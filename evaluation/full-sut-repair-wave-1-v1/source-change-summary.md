# Source change summary (Wave 1, candidate v2)

All changes are deterministic, generalized, and free of case IDs and
expected verdicts. The test file runtime/sut/test_input_normalization.py
is not part of the 24-component SUT manifest.

## RC-01 - input/schema compatibility

runtime/sut/context.py (normalize_input), sha256
078bcf3fb566e3f02a05a23e69835d88e863b1ef4a3c69a6df240537835fa0a3:

- Candidate v1: profile.age null dropped; nested profile.context merged
  into top-level context (caller top-level wins); profile.household_children
  boolean true to 1, false to 0, int kept; malformed values retained so the
  strict post-normalization schema rejects them fail-closed.
- Candidate v2 (this freeze): scalar (str/int/float) profile.context
  wrapped into top-level context.situational_context (existing top-level
  key wins); list/null values and non-object top-level context retained in
  profile so strict validation fails closed. Idempotent, no case IDs.
- runtime/sut/schemas/sut-input.schema.json: profile.age nullable
  (integer or null, 0-120); optional profile.household_children
  (integer or boolean, min 0); unknown profile keys still rejected.

## RC-02 - safety/triage granularity

- data/safety-triage-rules-v2.json (frozen rules file, 12 classes):
  class collapse table reduced; classification logic unchanged.
- runtime/sut/phase2/safety.py: no longer collapses every classified
  class to ACUTE_RISK_NOW; the classified 12-class name is carried to
  emission when classification succeeded (same signal matching and
  negation guard as before).
- runtime/sut/schemas/sut-output.schema.json: safety.priority and
  top-level safety_priority accept the frozen 12-class vocabulary plus
  the two collapse priorities URGENT_NOT_ACUTE / NOT_ACUTE (bookkeeping
  values for failed/unknown triage, not class names). Unknown/failed
  states still coerce fail-closed to ACUTE_RISK_NOW at emission.

## RC-03 - structured routes and provenance

- runtime/sut/phase2/routes.py: build_national_route_candidates() emits
  deterministic national route candidates from PROJECT_RESEARCH records,
  with route_state and provenance_refs continuing the P-K numbering of
  _provenance_records; appended to _s6_routes after discovery routes in
  both pipelines.
- runtime/sut/phase2/pipeline.py: route reasoning wires national
  candidates into the route stage (no discovery dependency).
- runtime/sut/phase3/finalize.py: route label consistency check uses
  the same ASCII transliteration as the renderer (ascii_text), so
  ae/oe/aa variants cannot spuriously fail the answer-substring check.

## Test deltas

- RC-01: 4 normalization tests added in candidate v2 (1 malformed-context
  test replaced by a split fail-closed pair); 1 end-to-end scalar-context
  test with a generic fixture (not a burned case).
- RC-02: acute invariant matrix over collapsed and uncollapsed classes.
- RC-03: route/provenance/consistency matrix.
- Full suite: 167 (v1) then 170 (v2) passed, 0 failed.
