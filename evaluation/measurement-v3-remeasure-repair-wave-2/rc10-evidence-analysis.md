# RC-10 Effect Analysis - Evidence Attachment

Task: NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2
Classification: BURNED_DEV_BASELINE_ONLY
Basis: frozen Wave-2 measurement, frozen Wave-1 measurement, frozen Candidate-2 structural diagnostics.

## Mechanical evidence facts

- Claim provenance: 673/673 claims with provenance (structural gate PASS; zero provenance-linkage-bad findings). Wave 1 had 645/645 claims with provenance entries, of which 308 were provenance-linked to answer content.
- Provenance-linked claims (claim text actually bound to provenance): 308/645 (47.8 %) Wave 1 -> 369/625 (59.0 %) Wave 2.
- Route provenance: 20/20 structured-route cases with provenance; 0 structured-route cases without provenance (Wave 1 was not gated on this).
- Evidence completeness criterion (frozen binary): 0.0 38 -> 23; 1.0 82 -> 97. Fifteen criteria moved 0.0 -> 1.0; none moved 1.0 -> 0.0.

## Semantic measurement effect

Evidence completeness is the frozen evidence criterion; it improved in 15 criteria and regressed in none, making it the only dimension with strictly non-negative movement in the primary matrix. However:

- Route correctness (the dimension most dependent on usable evidence) is unchanged at 0 PASS.
- Provenance existence is not semantic correctness: 100 % claim provenance coverage coexists with 23 criteria still at evidence 0.0 and 108 route FAILs.

## RC-10 verdict

The implemented dataflow change produced a measurable, strictly positive mechanical and semantic effect (claims bound to provenance up 11.2 percentage points; evidence_completeness 0.0 count down 15). Residual: 23/120 criteria still lack sufficient attached evidence, and label-to-evidence binding for routes remains unresolvable (see rc07-routing-analysis.md). RC-10 is materially effective but incomplete.
