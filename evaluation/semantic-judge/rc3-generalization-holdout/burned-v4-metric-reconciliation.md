# Burned V4 Metric Reconciliation

Label: BURNED_V4_METRIC_RECONCILIATION_ONLY
Burned marker: BURNED_BLIND_DEVELOPMENT_ONLY. Not certification, not blind evidence, not tuning input.
Question: how can the burned V4 shadow report invalid accepted proofs = 0 while auto precision = 16/34 = 47.06%?

## Answer

They are different metric layers. The historical "invalid proof" counter in the shadow harness only fired when an accepted auto path lacked a proof object or a source span that is a literal substring of the evidence (structural validator failure). Auto precision measured whether the final auto polarity equaled the sealed proof-safe target. A proof can be structurally valid and grounded while its CONCLUSION does not follow under the evaluation contract.

Recomputation with the separated metrics of proof-soundness-contract-v2 (script: reconcile_burned_v4_metrics.py; labels decrypted in memory only; no case ids or labels persisted):

| Metric | Count |
|---|---|
| n cases | 160 |
| runtime failures | 0 |
| accepted proofs (atoms) | 66 |
| autos (cases) | 34 |
| M1 structural_invalid_accepted_proofs | 0 |
| M2 ungrounded_accepted_proofs | 0 |
| M3 semantically_unsound_accepted_proofs | 37 |
| M4 proof_safe_unsound_autos | 18 |
| M5 wrong_product_autos | 18 |

Internal consistency: 34 autos - 16 correct = 18 proof-safe-unsound autos, matching the shadow's 16/34 precision denominator exactly. M3 counts at atom granularity (37 > 18 because a compound case can carry several accepted-but-unsound atoms while the case counts once).

## Classification per spec 6/7

- Root cause type: terminology/instrumentation, not runtime bug.
- Action taken: evaluation-only metric contract repair (METRIC_CONTRACT_REPAIR_ONLY). The v2 contract freezes M1-M5 as separate metrics with the hard soundness invariant (structural validity never hides semantic unsoundness).
- Runtime: unchanged. Historical artifacts: unchanged (rc3-development/burned-v4-shadow-results.json byte-identical; verify in QA).
- No tuning was performed or will be performed based on these counts.

