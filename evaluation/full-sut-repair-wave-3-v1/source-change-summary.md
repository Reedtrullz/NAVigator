# Source Change Summary (candidate 1)

Files changed vs. Wave-2 candidate:

- runtime/sut/phase2/routes.py (only runtime change): W3-RC-A
  structured route-target extraction + self-referral hint; shared
  label gate now rejects metadata labels on the lexical path too.

Files added (non-runtime):

- runtime/sut/phase2/test_route_propositions.py (26 tests)
- lineage docs in evaluation/full-sut-repair-wave-3-v1/

No other runtime file was modified. Wave-2 test files pass unmodified.
