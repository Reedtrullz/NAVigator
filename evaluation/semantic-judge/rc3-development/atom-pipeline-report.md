# Atom Pipeline Report (Phase B)

DECOMPOSITION_V1 canonical decomposition runs before any evidence
judgment (spec 20): a pure function of claim text. Evidence
availability never changes the atom count.

## Pipeline

1. decompose_claim(claim) -> ordered atoms with stable atom_id A1..An
   and relation_to_parent CONJUNCT (spec 19).
2. Each atom judged independently through PROOF_ENGINE_RC3
   (engine_rc3.judge_atom): aligner -> deterministic proof ->
   structural validation -> guards -> proof state.
3. Per-atom arbitration (ARBITRATION_V2) with optional reviewer
   proposal (REVIEWER_V2).
4. Deterministic top-level aggregation (routing.aggregate_atoms):
   any REVIEW -> REVIEW_REQUIRED; all-abstain -> ABSTAIN_INSUFFICIENT;
   auto+abstain mix -> PARTIALLY_SUPPORTED; sup+contra mix ->
   PARTIALLY_SUPPORTED; else the uniform auto verdict (spec 26).

## Development results (decomposition-results.json)

- 66 claim-logical cases: 63/66 atom-count exact = 95.45%
  (gate >= 95%: PASS).
  Known boundary misses: "gratis men henvisning kreves" (men without
  explicit subject repetition), one "og" with locational complement,
  "men" inside a valuation clause. All three under-split to 1 atom.
- Deterministic stability: 100% (repeated calls byte-identical).
- Stable atom IDs: 100% (A1..An sequential).
- Aggregation unit checks: 4/4 correct.
- Atomicity doctrine: noun coordination ("inntekt og formue",
  "legehjelp og psykologhjelp") is ONE atom; only independent
  propositions split (claim-logical, spec 21).

## Compound development gates (spec 39)

- decomposition atom count exact: 95.45% (>= 95% PASS)
- atom semantic accuracy: not separately measurable on synthetic
  count suite; engine-layer semantic exact on the 45-case dev corpus
  is 48.89% (DEVELOPMENT_SANITY_ONLY, see final report).
- compound product accuracy: 60% on the 15 compound dev rows
  (DEVELOPMENT_SANITY_ONLY; RC2 label doctrine mismatch documented).
- critical compound failures: 0 (no critical synthetic case failed
  unsafely; no unsafe auto produced anywhere).

Phase B gate verdict: decomposition gates PASS; atom pipeline works
independently; aggregation tests PASS (spec 47).
