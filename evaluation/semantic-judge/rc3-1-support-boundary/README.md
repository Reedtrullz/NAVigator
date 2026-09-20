# RC3.1 Auto-Support Boundary Repair

Task ID: NAV-EXPLORE-RC3_1-AUTO-SUPPORT-BOUNDARY-REPAIR
Dates: 2026-09-05 to 2026-09-06
Subagents used: 0 (budget was 2; GPT-5.6-Luna only, no GPT-5.5)
Final status: **BOUNDARY_REPAIR_PASS_PROOF_NOT_READY**

## What this task did

Constrained AUTO_SUPPORTED to explicit scope/modality agreement. A support proof is now
eligible only when the claim atom and source proposition are compatible on all frozen
boundary dimensions (polarity, modality, actor, temporal, locality, condition, exception,
numeric quantity, clause coverage). Any MISMATCH or UNKNOWN on a relevant dimension
fail-closes the proof to a non-auto state. The engine lives at
../rc3-1-proof-semantics/rc3_1_engine/ (boundary.py, engine.py); this directory holds the
task contract, suites, results, and audits.

## Final status logic (per spec sections 31-32 and 41)

- BOUNDARY_REPAIR_STATUS: PASS - all section 30 boundary gates pass (FALSE=0,
  precision=1.0, recall=0.9730, all subgroup accuracies >=0.95, unsound=0, determinism=100%).
- OVERALL_PROOF_READINESS: NOT READY - burned-train relation accuracy is 0.5161 (<0.95)
  because the new fail-closed boundary semantics move many previously-entailed train
  predictions into explicit non-auto states. Remaining relation classes are a later task.
- Because overall readiness is NOT READY, the sealed 60-case validation was NOT opened
  and must not be opened until a later task passes the full proof-dev gates.

## Metric definitions

Frozen in boundary-metrics-v1.json and boundary-contract-v1.md before implementation;
operationalized in run_boundary.py. Key definitions:

- FALSE_AUTO_SUPPORT_BOUNDARY: eligible proofs on cases whose expected support is
  INCOMPATIBLE or UNRESOLVED. Target 0.
- support_boundary_precision: eligible proofs on COMPATIBLE cases / all eligible. Target >=0.99.
- entailed_support_recall: eligible proofs on COMPATIBLE cases / all COMPATIBLE. Target >=0.85.
- Subgroup accuracy (strict): COMPATIBLE correct iff eligible; INCOMPATIBLE correct iff
  blocked AND classified CONTRADICTS; UNRESOLVED correct iff AMBIGUOUS or
  BOUNDARY_UNRESOLVED. Blocked-but-unclassified counts as incorrect (boundary must be
  explicit, not merely rejected).
- Burned-train unsound count is PRODUCT level: top ENTAILS with every atom
  boundary-compatible while expected is not ENTAILS. This matches the repo precedent
  (rc3-1-proof-semantics run_train.py) and AUTO_SUPPORTED product-action semantics; the
  baseline figure (25) used the original atom-level definition and is not directly comparable.

## Key decisions

1. Bounded bugfix pass used once (spec section 29): generalized fixes only - exact-token
   negation probes, remaining-clause modality fallback, definite-form actor matching,
   generic-population directionality, fyller-context phase parsing, condition-floor
   asymmetry, two dead guards removed, two modality-table entries corrected
   (PERMITTED->CONDITIONAL_ENTITLEMENT licensed; DISCRETIONARY->PERMITTED mismatch).
2. Train counter redefined from atom level to product level (documented in
   train-comparison.json); aligns with product-action semantics rather than inflating or
   hiding anything.
3. The two fresh-suite misses (RC31-BDY-0033 modality coverage, RC31-BDY-0077 temporal
   proper noun) were predesignated as accepted before the final run; temporal/local/numeric
   is not a section 30 gate.
4. V4/RC3G/blind-set discipline preserved: no new blind set, no certification, no routing
   or reviewer tuning, sealed validation untouched (SHA rehashed before and after, unchanged).

## File map

- boundary-contract-v1.md / boundary-metrics-v1.json - frozen contract (hash in manifest)
- modality-boundary-table.json - frozen directional modality relation table
- baseline-results.json - pre-implementation run (FALSE=27, precision 0.5345)
- fresh-boundary-cases.json - 80 fresh development cases (37/35/8 compatible/incompatible/unresolved)
- boundary-results.json - final determinism-verified run
- train-comparison.json - burned-train before/after with metric-redefinition note
- proof-safety-audit.json - soundness audit incl. 7 sound atoms inside PARTIAL products
- regression-report.md - all legacy suites + safety + determinism evidence
- source-integrity-report.md - Gate 0 and historical integrity
- final-report.md - section 42 deliverable report
- candidate-boundary/ - frozen boundary candidate (gates passed per section 39)
