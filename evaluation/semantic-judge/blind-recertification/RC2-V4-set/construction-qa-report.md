# Construction QA Report (V4)

## Live gate

- `python3 v4_qa.py`: live plaintext-label gate PASS, exit 0 (full-project scan;
  8 incidental allowlisted files; 0 true leaks).

## Regressions

`qa-tests/test_v4_qa.py`: 7/7 PASS, exit 0:

- test_plaintext_labels_fail
- test_missing_compound_atom_target_fails
- test_missing_criticality_fails
- test_missing_subgroup_metadata_fails
- test_incomplete_two_pass_fails
- test_aggregation_inconsistency_fails
- test_reused_old_key_fails

## Sealed-content verification (2026-09-04, in-memory, aggregates only)

- `answer-key.sealed`: decrypts with AAD = blind-cases SHA-256 hex; 160 cases;
  final labels, criticality, flags, rationale, and annotation_status complete on
  all (150 two_pass_agreed + 10 adjudicated); 62/62 compound cases with complete
  atoms (atom_id, claim_text, semantic_truth, proof_safe, supporting_span_ids,
  required_inference); 1 top-level relabel recorded (identity sealed).
- `construction-audit.sealed`: decrypts with AAD `construction-audit:v1`.
- Key persistence scan: no key material found in repo, memories, or Obsidian.

## Notes

- `test_reused_old_key_fails` verifies the mechanism: a registered fingerprint
  flags a matching key while any fresh key passes; no key material is embedded.
- The retired V3 key was checked by SHA-256 fingerprint only; the key itself was
  never written to disk.
