# Historical Integrity — V2.3 Site-Direct-Only

Verified 2026-09-09 before implementation. All checks are fresh SHA-256
re-verifications, not memory-derived.

## Verified frozen state

| Artifact | Verification |
|---|---|
| Protocol V1 | data/local-service-discovery-protocol-v1.json SHA-256 fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca |
| Candidate Runtime V2 manifest | evaluation/local-discovery-provider-arch-v2/candidate-runtime-v2/manifest.json SHA-256 74329662e2df1e8bffb69165b3c39820af6313e7a3096fe6754d78f80977a678 |
| provider config V2 | SHA-256 d6890b5f97c8dd12eb915114c571a8ba930b75aa00fdd0c5a373965c5423cbc3 |
| V2.1 correctness snapshot | 7/7 declared files byte-match manifest sha256 values (brave.py, providers.py, tests_v21.py, tests.py, orchestrator.py, cli.py, sitemap_fetch.py) |
| V2.2 backend-selection artifacts | evaluation/local-discovery-external-backend-v2-2{,-restart,-restart-2}/ untouched; TASK-LOCK CLOSED_TERMINAL NO_EXTERNAL_BACKEND_MEETS_V2_2_GATES preserved |
| Previous benchmark/replay datasets | evaluation/local-discovery-provider-arch-v2/ (benchmark-corpus.json 117 queries, site-direct-results.json, replay-regression.json 21/22 Askoy FIXTURE_INCOMPLETE) and evaluation/local-discovery-runtime-v1/ (fixtures, replay-results.json, access-regression-results.json) reused byte-for-byte |
| Blocked V1/V2 fresh-evals | not touched; no fresh municipalities used |

## Policy

HISTORICAL_FILES_MODIFIED = 0. V2.3 adds new files only:

- runtime/discovery_v2/render.py (new render fetch layer)
- runtime/discovery_v2/tests_v23.py (new tests)
- evaluation/local-discovery-site-direct-only-v2-3/ (all task artifacts)
- evaluation/local-discovery-site-direct-only-v2-3/ official runners

No existing file is edited. At final audit, all files listed in the V2.1
snapshot manifest and the candidate-runtime-v2 manifest are re-verified
byte-identical. Historical provider modules (including tavily.py/brave.py and
their tests) are preserved as historical components; they are not runtime
dependencies of V2.3.
