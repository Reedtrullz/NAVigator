# Phase 2A.1 - Pre-Key Denominator / Membership Sanity Audit

Task: `NAV-EXPLORE-RC2-BLIND-V4-PHASE2A1-DENOMINATOR-AUDIT` (keyless;
no answer-key or construction-audit decryption; no scoring; no
correctness analysis; prediction artifact untouched).

## Root cause of the "40/120" report

Classification: **REPORT_ONLY_TYPO** (spec 8 case A).

The Phase-2A SLUTTRAPPORT point 16 wrote `criticality ... 40/120`.
The preregistered source phrase - repeated in certification-metrics.md
line 23 and in the public blind manifest criticality block - is
`40 critical / 120 standard`, a partition of the 160 CORE cases
(40 + 120 = 160). The report compressed that phrase into an ambiguous
fraction that reads as a wrong denominator. The correct expression is:

```text
critical_cases = 40
total_core = 160
40/160 CORE cases are critical
```

## Occurrence classification of "120" (spec 7)

Every occurrence in the frozen Phase-2A artifacts and the preregistered
certification spec was inspected individually. No global replace was
performed and none was needed.

- `scoring-policy.json:16` - source_of_authority quote of the
  preregistered manifest counts (`40 critical/120 standard`):
  legitimate historical/reference.
- `scoring-policy.json:102` - criticality_membership source quote of
  the same preregistered rule/counts: legitimate reference.
- `scoring-policy.md:119` - identical prose quote of the preregistered
  counts: legitimate reference (harmless prose).
- `RC2-V4-set/certification-metrics.md:23` - the preregistration
  itself: legitimate preregistered text.
- `score_frozen_predictions.py` - zero occurrences.
- `scoring-policy-freeze.json`, `TASK-LOCK.json` - zero occurrences.

No stale V1/RC1 denominator exists anywhere in the scoring path.

## Mechanical denominator verification (spec 2, 4)

Verified from public/frozen artifacts only:

- V4 CORE count = 160 (`blind-cases.json`: 160 cases, all CORE,
  160 unique ids).
- Prediction rows = 160, unique = 160; prediction id set equals the
  CORE id set exactly. Prediction SHA unchanged:
  `49ab4e0d890cd3e9c15b44646c0235db3413647b971ba5b736888e651aa861a2`.
- All overall exact metrics use denominator 160
  (`n = len(rows)` after the 160-row guard).
- Critical product: the scorer derives the denominator from
  `key.criticality == "CRITICAL"` rows (`len(critical_ids)`), never
  from a constant. With the preregistered 40 critical cases the
  denominator is 40. It is not /120, not /160, not /predicted critical,
  not /successful critical. Gate: `crit_prod_ok == len(critical_ids)`.

## Critical and subgroup membership (spec 3, 5)

Membership source is preregistered public/sealed metadata; no expected
label was opened. Preregistered membership counts (public
`blind-manifest.json`, `core_flag_counts` / `criticality` /
semantic distribution):

```text
critical        40   source: key.criticality (rule: flags intersect {safety, age_legal}); denominator: the 40 critical CORE cases
safety          20   source: key.final_flags[safety]
legal           89   source: key.final_flags[legal]
numeric         92   source: key.final_flags[numeric]
temporal        82   source: key.final_flags[temporal]
locality        38   source: key.final_flags[locality]
modality       132   source: key.final_flags[modality]
actor           99   source: key.final_flags[actor]
condition/exception  42   source: key.final_flags[cond_exc]
compound        62   source: key.final_flags[compound]
multi-span      31   source: key.final_flags[multi_span]
age/legal adversarial  20   source: key.final_flags[age_legal]
insufficiency   40   source: label-derived (key.semantic_truth == INSUFFICIENT_EVIDENCE), preregistered in public manifest
```

Every subgroup denominator is its own membership N inside the 160 CORE
rows, independent of the overall N and independent of any other
subgroup. The scorer computes each subgroup denominator from key flags
per row; no hardcoded membership counts exist in scorer or policy
logic (counts appear only as quoted preregistration references). No
hardcoded 120 exists in any subgroup path.

## Compound denominator (spec 6)

- Compound CORE cases = 62 (preregistered; scorer derives compound
  membership from `key.final_flags` per case).
- Expected atom denominator = 141 (preregistered; scorer derives
  `atom_den` by summing `len(key atom_labels)` over compound cases -
  i.e. all expected atom targets when the key opens, not a constant).
- Phase-1 predicted atom intermediates = 202 total across 160 rows.
  This is NOT a denominator for compound atom accuracy and is never
  used as one.
- Extra/missing atoms are recorded as mismatch errors per the frozen
  policy; only expected targets enter the denominator.

## Frozen artifact integrity

Per spec 8, the frozen Phase-2A artifacts were NOT modified:

- `scoring-policy.json` SHA-256:
  `92fe6aa6cd8bb55a0539da30967f8e8249fe5d7745bbdc7a8d5e84d745e1cd35`
  (unchanged, re-verified).
- `score_frozen_predictions.py` SHA-256:
  `77b3e9f1ae3c6270757ccc8c5490e461a32feb3bee59e762658cccabf51a07b5`
  (unchanged, re-verified).
- `scoring-policy-freeze.json` unchanged (no v2 supersession needed).
- Thresholds unchanged (all 12 preregistered hard gates as frozen).

## Firewall confirmation (spec 12)

- `BLIND_RC2_V4_KEY`: unavailable, never requested.
- `answer-key.sealed`: never decrypted or opened (SHA-256 check only:
  `65f72b170cb200b804cf817c32aaf42e9166a20ed002777a5d9f5e71b99fd80d`,
  unchanged).
- `construction-audit.sealed`: never decrypted or opened (SHA-256
  check only: `5be70e666493d3a6e000b89418a8064099f03ee797ece3365840acb7a7646ff3`,
  unchanged).
- No scoring performed; no per-case correctness computed; prediction
  SHA unchanged.

## Status

`SCORING_POLICY_CONFIRMED_BEFORE_KEY`

The Phase-2A freeze stands unchanged. Phase 2B may receive
`BLIND_RC2_V4_KEY` in a separate continuation.
