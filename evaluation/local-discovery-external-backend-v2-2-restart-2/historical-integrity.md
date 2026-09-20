# HISTORICAL INTEGRITY (RESTART-2 execution)

All re-verified fresh in this run (sha256):

| Artifact | Result |
|---|---|
| Protocol V1 `fb533d99...f99ca` | MATCH |
| Candidate V2 manifest `74329662...a678` | MATCH |
| Provider config V2 `d6890b5f...cbc3` | MATCH |
| V2.1 implementation snapshot (7 files) | 7/7 MATCH (verified 3x during run: pre-run, post-adapter, post-benchmark) |

HISTORICAL_FILES_MODIFIED = 0. FRESH_MUNICIPALITIES_USED = 0.
ACCOUNTS_CREATED = 0. KEYS_GENERATED = 0.

Files created by this task: this directory + `runtime/discovery_v2/tavily.py`,
`runtime/discovery_v2/tests_v22.py` (new V2.2 lineage files; the seven
snapshot-listed runtime files are untouched and hash-verified).

Brave HTML negative control: preserved, not re-probed, not re-evaluated.
