# Runtime type cleanup - 2026-10-12

The runtime candidate now passes basedpyright 1.39.3 with **0 errors and
0 warnings across 42 explicit source/interface/test/runner files**. All
68 guarded synthetic tests pass on Python 3.10.4 and 3.14.6. Runtime remains
disconnected; pilot packages and frozen evaluation are preserved.

Local branch: `codex/runtime-type-cleanup`, based on main merge
`08d51d4feadfe03695ca2af87370949b44cafa6b`. This increment is uncommitted.
The original runtime/pilot worktree and primary checkout are preserved.

## Changes

Continue the completed R1-R7 runtime plan with explicit typed records,
provider callbacks, stage contexts, source/admission evidence, output and
trace contracts. Input types match the frozen schema, including required
case/profile fields and nullable age. Seven stubs describe the unchanged
phase-1 and legacy provider APIs used by this candidate. The extractor's
implementation is checked directly; no stub hides its source.

JSON enters as object and is checked before becoming trusted fields.
Malformed source metadata is rejected before a document is opened;
safety arrays, signals and collapse values are checked. Replay payload
validation is inside the adapter's existing fail-closed handler, so malformed
services, age bounds, evidence and errors produce redacted
DISCOVERY_INCOMPLETE rather than an exception escaping the adapter.

Shared helpers have public names and retain legacy aliases. Synthetic
fixtures now carry concrete types; intentional malformed-state injection
remains a negative test. No original test was deleted, skipped or weakened.
Five boundary methods add malformed-profile/metadata/safety/replay cases
and a valid nullable replay case.

The synthetic runner verifies the new 42-file source receipt and all
68 methods. CI retains its protected-path and guarded Python 3.10/3.14
matrix and now checks these exact types with basedpyright pinned to 1.39.3.
No checker setting, severity, exclusion, Any annotation or ignore is added.

## Evidence

Baseline: default basedpyright, the original 28-file PR-67 scope:
0 errors, **2,535 warnings**, exit 1. Full baseline JSON remains outside
Git at `../types-baseline.json`.

Final: default basedpyright, all 42 listed candidate paths:
**0 errors, 0 warnings, exit 0**. Explicit Python 3.10 and 3.14 type targets
also return zero errors/warnings. Full final diagnostics remain outside
Git at `../types-current.json`; their hash is captured in the test proof.

The native edit hook intermittently retained stale line/import diagnostics
from another worktree view. Fresh full CLI checks against the actual
candidate files are clean; no diagnostic hook or checker was disabled.

Both Python versions run **68/68**, with zero failures, errors, skips,
expected failures, unexpected successes and guarded DNS, connection,
subprocess or browser attempts. The replay regression first produced four
failed subcases and zero errors; after moving parsing into the handler it
passes. The caught-DNS negative control still rejects an otherwise passing
68-test run, and an in-memory source mutation is rejected before testing.

Fresh source manifest:
`1db6cfd0bf67e4753a6ca14a09c6ed39a8d73d071121d451898b7c4fb0b34419`.

- `runtime-type-evidence-2026-10-12.json`: exact source hashes, scope and baseline.
- `runtime-type-test-proof-2026-10-12.json`: raw versioned test receipts, type
  results, negative controls and post-test preservation.
- `git diff --check`: PASS; 42 files parse; zero synthetic temporary leftovers.

## Preservation and review

After testing, the original runtime candidate's 28 hashes and all 36
protected original files still match. Both original pilot HTML/ZIP hashes
match, and its runtime_enabled remains false. Evaluation Git tree
`dbb2c7ad8d0ddb4f9d0ae77b9d52714d532deb55` is unchanged. Metadata-only
fingerprints retain 11,433 evaluation entries and 8,473 historical pilot
entries. These fingerprints do not claim a byte audit of private records.

The active worktree has no changes to pilot, evaluation, data, frozen
schemas or phase-1 implementation. Prior review/CI receipts are untouched.
Primary HEAD, status and README bytes remain unchanged.

Author review checked the typed boundaries, retained failure handling,
legacy helper aliases and stub/public API compatibility. The prior PR-67
independent approval is historical; no new independent review is claimed
for this increment.

## Reproduce and limits

From this worktree:

```sh
PYTHONPATH=runtime python3 -m tools.runtime_synthetic
python3 -c 'import json, subprocess; from pathlib import Path; paths = json.loads(Path("docs/runtime-type-evidence-2026-10-12.json").read_text())["runtime_source_hashes"]; raise SystemExit(subprocess.call(["basedpyright", *paths]))'
```

The type claim covers only the listed candidate paths, shared interfaces,
synthetic tests and runner. Legacy phase-1/provider implementations outside
that scope are not claimed warning-free. CI is updated but not run remotely.
No private-record demonstration, live-provider test, frozen evaluation
execution/rescore, pilot rebuild/integration, release, legal/clinical
acceptance or deployment occurred. JavaScript live rendering and missing
V2.5 protocol levels retain their existing unavailable/incomplete states.

All requested type-cleanup and synthetic-verification tasks are complete.
