# Quota resume runbook (do not execute now)

When Astra quota is available:

1. verify this partial freeze (manifest + hashes.txt)
2. verify quota-resume-manifest.json and packet hashes
3. run Astra A/B ONLY on quota-resume-semantic-packets.jsonl
4. Astra LOW only (ASTRA_MEDIUM/HIGH/MAX forbidden)
5. validate structured observations
6. derive semantic-field consensus
7. run Sol A/B ONLY on residuals if Sol quota is available
8. no third pass
9. freeze semantic observations
10. mechanically derive with frozen judge_core_v2_13.derive_final
11. replace PENDING rows with authoritative rows
12. freeze complete Wave-4 measurement
13. run complete bridge-to-Wave-4 comparison

Estimated minimum: 220 Astra calls (110 packets x 2). Residual Sol usage
cannot be known until Astra consensus is observed. No fallback models.
