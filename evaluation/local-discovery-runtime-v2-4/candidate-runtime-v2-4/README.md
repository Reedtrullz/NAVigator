# LOCAL-DISCOVERY-RUNTIME-V2.4 (frozen development candidate)

New lineage over the frozen V2.3 site-direct runtime that repairs the platform-root defect: canonical_roots_v24 rewrites the frozen resolver's .bedinnsats.no output to .bedreinnsats.no for platform roots only (kommune.no pass-through untouched).

- Status: LOCAL_DISCOVERY_RUNTIME_V2_4_CANDIDATE_FROZEN
- Entry point: runtime/discovery_v2/cli_v24.py (or evaluation/local-discovery-runtime-v2-4/run_v24_harness.py)
- Config: evaluation/local-discovery-runtime-v2-4/provider-config-v2-4.json
- SHA-256 of this manifest: (see readiness-report line in final-report.md; hashes.txt covers all pinned components)

All official burned-run artifacts live in evaluation/local-discovery-runtime-v2-4/. Known limitations and the two documented V2.3 source-drift pairs are listed in manifest.json.

