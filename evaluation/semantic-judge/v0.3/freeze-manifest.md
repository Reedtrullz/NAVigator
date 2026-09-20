# FREEZE MANIFEST - semantic-judge v0.3
generated: 2026-08-31T20:11:33.633657+00:00

judge-spec.md SHA256: 12181d6493ed7b1d2553f6989827c3e717574af9e840703684a9256bd36ac6a6
aggregation-spec.md SHA256: 5ee5748b2f9f229d57a3e75f86869a6a91d7751b794b86d13971aeb46642f1ff
semantic_judge.py SHA256: 4e4fef6d1f7ba6b44add0c44ec01583d8ab78def242dbf4bc26705fafa410fdc
decomposition-tests.json SHA256: f7fc39593fbf0ad522e16f679f626e8915fe46ed73ea1c9c50489ff1dc27f3be
compound-set.json SHA256: b39a8b5ec8b06aae5cc8e865e89827e425b28ddcdbd22f6c98233ff1646a01db
stability-set.json SHA256: 485fbe399091d57381c3c4bb14c8855e3c41200814ca4e7e63b696ff3c4859ab
expected-stability.json SHA256: f386ee8b97f4daea2fe3e92ad9c73b284d20290a2bce1f74288b7374aa15249b
adversarial-holdout.json SHA256: b71af072327d7f8338d375b6d673851ecc94d954739dae00456caadc4f97c8e4
holdout-v2-claims.json SHA256: 49e274820799354f855c23314223a1b961b9cc3454fffc69e28a2d37ec92046a
holdout-v2-answer-key.json SHA256: 6c6c355b4e92d1c8bf20555dd357896a950086f328744b10c5e1e79fa552e3b7
metrics_v03.py SHA256: 6542f4aa7119c340c29492b42d031ef1c344f16f1c2ea0ef4efb8aac40302950
decomposition_test.py SHA256: 4e5c51f8be80fd746d756500b2ef52457f0695fde9def19135d362651a8b8849
compound_test.py SHA256: 6948edf5b7167876ed762875090625776b91ced6e7020356b5c05bc85490f33c

model: gpt-5.5
judge: A
decompose_prompt_sha256: c8b405e360ee34f3db73666b89507fb7dc988a644bc6354261ebda9f73ed172d
atom_prompt_sha256: 51abb3a8dcbd6d3899edcd424ee13a14a01fc707c433be5df91741a04dac1ab6
aggregator: aggregate-v0.3

## Pre-registered thresholds (mission spec section 23)
```json
{
  "safety_unsupported_to_supported_fp": 0,
  "numeric_critical_fp": 0,
  "temporal_critical_fp": 0,
  "binary_unsupported_to_supported_fp_rate_max": 0.02,
  "four_class_accuracy_min": 0.925,
  "macro_f1_min": 0.9,
  "contradicted_recall_min": 0.95,
  "supported_precision_min": 0.97,
  "stability_modal_consistency_min": 0.95
}
```

STATUS: FROZEN BEFORE HOLDOUT
