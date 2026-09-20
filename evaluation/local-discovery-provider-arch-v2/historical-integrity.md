# HISTORICAL INTEGRITY REPORT

Task: NAV-EXPLORE-LOCAL-DISCOVERY-PROVIDER-ARCH-V2. Date: 2026-09-09.

## Baselines (frozen in TASK-LOCK.json at task start)

| Artifact | SHA-256 | Status |
|---|---|---|
| Candidate V1 manifest (evaluation/local-discovery-runtime-fresh-eval-v1/candidate-runtime/manifest.json) | 573f77348a75a750542e05a5f5c18a2b033643773b24df73a2fa827716f15af7 | UNCHANGED - file SHA re-verified post-task, matches baseline |
| Protocol V1 (data/local-service-discovery-protocol-v1.json) | fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca | UNCHANGED - re-verified post-task, matches baseline and ProtocolLoader frozen SHA |

## V1 candidate file integrity

All 14 files in the frozen V1 candidate manifest were re-hashed after all V2
work: 14/14 match recorded SHA-256 values, 0 missing, 0 modified. The full
file list is recorded in replay-regression.json
(candidate_manifest_integrity).

## Historical artifacts preserved

- evaluation/local-discovery-runtime-v1/ (replay results, live smoke,
  access regression, determinism, task lock, reports): read-only access
- evaluation/local-discovery-runtime-fresh-eval-v1/ including the blocked
  fresh-eval final report with terminal status
  RUNTIME_FRESH_EVAL_BLOCKED_BY_PROVIDER: read-only access; status NOT
  rewritten to PASS/FAIL
- data/local-service-discovery-protocol-v1.json: never written
- runtime/discovery/ (V1 runtime): never written

## Fresh municipality usage

0. All live/benchmark work used the 13 burned municipalities frozen in
benchmark-corpus.json (Municipal Sample V1, 18-23 deep dive, access
verification, generalization V1 material).

## HISTORICAL_FILES_MODIFIED

0.
