# Implementation Report (task sections 5-11)

## New lineage design

V2.4 is a minimal new-lineage override, per section 5 and YAGNI:

- runtime/discovery_v2/roots_v24.py - canonical_roots_v24(): delegates to the
  frozen V2.3 resolver and replaces exactly the platform-root construction
  .bedinnsats.no/ with the canonical .bedreinnsats.no/. The kommune.no
  variants are passed through untouched (tested).
- runtime/discovery_v2/cli_v24.py - thin V2.3 clone importing the V2.4
  resolver; SiteDirectProviderV23 is reused unchanged (budget stays 16).
- runtime/discovery_v2/tests_v24.py - 4 regression tests (sections 6 and 8):
  Raelingen canonical root present, forbidden bedinnsats root absent, a
  synthetic non-Raelingen slug proving generalization, and kommune.no
  pass-through invariance.

No historical file was modified; no full-runtime copy exists (V2.4 code is
three small new files).

## RED (section 7)

Sequence deviation disclosed in tdd-red-result.json: tests and fix landed in
the same patch, so the first run was green. RED was re-observed honestly by
temporarily removing the only new production artifact and re-running against
the pre-fix lineage:

- Module level: exit 1, FAILED (errors=4), ModuleNotFoundError roots_v24.
- Assertion level (historical resolver, no code change): expected root
  https://ralingen.bedreinnsats.no/ missing; forbidden
  https://ralingen.bedinnsats.no/ produced; actual_roots recorded in
  tdd-red-result.json.

## GREEN (section 10)

Focused suite runtime.discovery_v2.tests_v24: 4/4 OK, exit 0.

## Fix scope and prohibitions (sections 9, 8, 11)

- Canonical suffix defined once in roots_v24.py: .bedreinnsats.no/.
- No municipality-specific branching, no case IDs, no hardcoded Raelingen
  URL anywhere in V2.4 code (grep-verified in test-report.md).
- No other runtime behavior changed. OUT_OF_SCOPE_FINDING: none encountered.
