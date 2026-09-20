# Certification Report - RC2 vs NAV-EXPLORE-RC2-BLIND-V4

Task: NAV-EXPLORE-RC2-BLIND-V4-PHASE2B-SCORING
Verdict: RC2_NOT_CERTIFIED (8 of 12 preregistered hard gates failed)

## Integrity chain

* Predictions 49ab4e0d...61a2 (160 CORE, frozen before key) - verified before and after.
* Scoring policy 92fe6aa6...cd35, scorer 77b3e9f1...07b5, certification
  metrics 8b8b88ee...1fbd - verified before and after.
* RC2 manifest components 10/10 before and after scoring.
* V4 blind-cases ad4fc100...a36d, sealed answer key 65f72b17...fd80d,
  sealed construction audit 5be70e66...46ff3 - verified before and after.
* AES-256-GCM authenticated decryption: OK (KEY_ACCEPTED = TRUE).
* Structural answer-key validation: PASS (160 rows, ID equality, 62
  compound / 141 atoms / 40 critical, annotation statuses valid).

## Hard gates

| Gate | Actual | Required | Result |
|---|---|---|---|
| Semantic exact | 33.12% (53/160) | >= 90% | FAIL |
| Proof-safe exact | 25.00% (40/160) | >= 95% | FAIL |
| Product exact | 42.50% (68/160) | >= 95% | FAIL |
| Combined auto precision | 82.35% (14/17) | >= 99% | FAIL |
| Critical product | 40.00% (16/40) | 100% | FAIL |
| Compound atom | 25.53% (36/141) | >= 90% | FAIL |
| Compound product | 74.19% (46/62) | >= 90% | FAIL |
| Invalid accepted proofs | 3 | 0 | FAIL |
| Hallucinated proofs | 0 | 0 | PASS |
| Critical unsafe AUTO_SUPPORTED | 0 | 0 | PASS |
| Critical unsafe AUTO_CONTRADICTED | 0 | 0 | PASS |
| Runtime failures | 0 | 0 | PASS |

Auto precision detail: AUTO_SUPPORTED 14/17 correct on proof-based
primary rule; AUTO_CONTRADICTED never predicted. Secondary
product-based rule identical (14/17).

Review metrics: predicted 143, TP 54, FP 89, FN 1; precision 37.76%,
recall 98.18%. Abstain: predicted 0, TP 0, FP 0, FN 26 (RC2 has no
abstain bucket; scored mechanically, not reinterpreted).

Official score frozen BEFORE error inspection: yes (freeze record
official-score-freeze.json, error_analysis_started=false at freeze).

## Key handling

KEY_ACCEPTED = TRUE. Key existed only in a memory shell variable, was
never written to repo/JSON/markdown/script/env/report, and the session
was terminated after scoring. Disk scans found no key material and no
full plaintext answer key. Plaintext lived in memory and passed through
an unlinked FIFO; FIFO removed. Reserve cases: 0 used. Reruns: 0.
Tuning: none. Runtime modified: no.
