# HISTORICAL INTEGRITY V2.2

All checks re-run fresh on 2026-09-09 with sha256. HISTORICAL_FILES_MODIFIED = 0.

| Artifact | Frozen value | Re-verified |
|---|---|---|
| Protocol V1 (`data/local-service-discovery-protocol-v1.json`) | `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca` | MATCH |
| Provider config V2 (`evaluation/local-discovery-provider-arch-v2/provider-config-v2.json`) | `d6890b5f97c8dd12eb915114c571a8ba930b75aa00fdd0c5a373965c5423cbc3` | MATCH |
| Candidate V2 manifest (`evaluation/local-discovery-provider-arch-v2/candidate-runtime-v2/manifest.json`) | `74329662e2df1e8bffb69165b3c39820af6313e7a3096fe6754d78f80977a678` | MATCH |
| V2.1 implementation snapshot (all 7 files listed in manifest) | manifest sha256 map | 7/7 MATCH |

Notes:

- The V2.1 snapshot manifest itself hashes to `666b7248a65fc90ba26508080394c80b2e87a756ed9f331ed6107233fefb7d2c`.
- V2.1 terminal status `LOCAL_DISCOVERY_PROVIDER_V2_1_ADAPTER_FIXED_BACKEND_NOT_READY` and all V2.1 report artifacts are preserved untouched.
- Brave HTML adapter stays the documented negative control (`BRAVE_HTML_BACKEND_DISQUALIFIED` for this runtime lineage). It was not re-probed, re-tuned, or reconsidered as a candidate, per task section 3.
- No file outside `evaluation/local-discovery-external-backend-v2-2/` was created or modified by this task.
