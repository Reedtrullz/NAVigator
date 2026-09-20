# Atom Annotation Summary (V4)

Two independent blind annotation passes covered all 62 compound CORE cases
(pass 1 produced 141 atoms; pass 2 did not see pass 1 output before writing).
Claim-text matching produced 125 atom pairs.

## Agreement (pre-adjudication, matched pairs)

- `semantic_truth`: 120/125 = 0.96 (gate >= 0.90: PASS)
- `proof_safe`: 117/125 = 0.936

## Divergence and adjudication

- 9 cases had structural split/merge divergence (different atom counts); resolved
  to canonical atom sets.
- 5 semantic disputes and 8 `proof_safe` disputes were adjudicated directly from
  case sources; pass 1 was correct on all 5 semantic disputes.
- Canonical atom statuses across 141 atoms: 43 agreed, 10 adjudicated,
  9 adjudicated_structural.
- Unresolved atom disputes: 0.
- Source-mandated atom overrides were applied where the sources forced a verdict;
  per-case identities, verdicts, and rationales are sealed in
  `construction-audit.sealed` (spec 26: no expected verdicts in public metadata).

Full pass outputs and adjudication records live in `construction-audit.sealed`;
plaintext originals were deleted after a roundtrip-verified seal.
