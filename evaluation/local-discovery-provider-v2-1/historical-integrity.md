# HISTORICAL INTEGRITY V2.1

- Candidate V2 manifest `74329662e2df1e8b...a678`: NOT rewritten. The V2.1 edits change `runtime/discovery_v2/brave.py` and `providers.py`, so runtime files no longer match that manifest byte-for-byte; this is expected and documented. V2.1 is a new implementation lineage; V2 remains immutable history.
- Protocol V1 SHA re-verified: `fb533d99d473a3382e2d2c52dfe72d117ceae6f07b4c1736243d3a533fff99ca` (unchanged).
- Provider config V2 SHA re-verified: `d6890b5f97c8dd12eb915114c571a8ba930b75aa00fdd0c5a373965c5423cbc3` (unchanged).
- Prior terminal status `RUNTIME_FRESH_EVAL_V2_BLOCKED_BY_PROVIDER` preserved in its own artifacts; not rewritten.
- HISTORICAL_FILES_MODIFIED = 0 (no file under `evaluation/local-discovery-runtime-fresh-eval-v2/`, `evaluation/local-discovery-provider-arch-v2/`, or any earlier candidate was touched).
- FRESH_MUNICIPALITIES_USED = 0 (E1 re-run used exactly the five burned municipalities and the same five burned technical queries).
- Baseline implementation SHA (pre-fix) captured in `source-integrity.json` (Gate 0).
