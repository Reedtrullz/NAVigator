# G2 - RC3 GENERALIZATION HOLDOUT SCORING

Task: NAV-EXPLORE-RC3-GENERALIZATION-G2

Frozen inputs (verified by SHA-256 before scoring):

- Predictions: run/RC3G-predictions.json, sha 6923c66c8abafde0bd0e3e58a282e2b40a3da4adefd3a364b25cddcd3a88a361 (159 outcomes, 0 runtime failures)
- Scoring policy: scoring-policy.json, sha 89abe4c2097ea97352e1133c600b4c70cf6a83afbb351744f27764cc5fff9e99
- Frozen scorer: score_generalization_frozen.py, sha 866f83786e8a9de7528e7c88f9d0d3e5951f47466f819a747e6913c610a53c2b
- Holdout cases: generalization-cases.json, sha 3f22c19b9f48e748ed5b5aadd0f715430e914225fc2923edd0e953cf09e720d4
- Sealed answer key: answer-key.sealed, sha e25b3ab813274662e354d4502192c2639df765bb3e5c5e67e616cba1fa32498a
- Sealed construction audit: construction-audit.sealed, sha 2b26675d51bd1cd0e39d2a5e93014ab03fa3de6ca60303f606efdc4ef43863b1
- Runtime snapshot: NAV-EXPLORE-RC3-GEN-SNAPSHOT-A, 14/14 components verified

Process:

1. TASK-LOCK-G2.json registered before scoring.
2. Authenticated decryption of the sealed key in memory only (AES-256-GCM, AAD = cases SHA).
3. Structural key validation: 159 IDs equal to prediction IDs, no unresolved disputes, 119 expected atoms.
4. Frozen scorer executed byte-for-byte; official score written BEFORE any error inspection.
5. Official score frozen: official-generalization-score-freeze.json.
6. Post-freeze error inspection only (g2_error_analysis.py; aggregate-only output).

Readiness verdict: GENERALIZATION_FAIL (11 of 16 preregistered hard gates failed).

Official score SHA-256: 384e1a21798001041d961ab06b0f5111f3b3077d6e3b519f56fff7aa739a61bb

Key handling: key used from environment only, never persisted to disk, shell history, or reports. Post-run scans (repo, shell history, /tmp) found zero key material. No plaintext labels were written; analysis artifacts contain aggregates and case-ID lists only.

Known scorer defect (registered, not patched, official score preserved):

The four zero-tolerance proof gates in the frozen scorer pass denominator 0 to gate_results, which short-circuits actual to 0.0, making structural-invalid, ungrounded, semantically-unsound, and proof-safe-unsound-autos gates structurally unable to fail. Recomputed directly from proof_gates counts: structural invalid 0 (pass), ungrounded 0 (pass), semantically unsound accepted proofs 53 (would FAIL), proof-safe unsound autos 14 (would FAIL). This does not change the verdict (already GENERALIZATION_FAIL on 11 other gates) but is mandatory input for the next scorer version.
