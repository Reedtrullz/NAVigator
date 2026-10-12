# Runtime type cleanup: independent review and fresh proof (2026-10-12)

The independent Gemini Pro review found no concrete defects, regressions, security vulnerabilities, API breaks or test failures in the type-cleanup increment. No code repair was required. The reviewed candidate remains uncommitted on `codex/runtime-type-cleanup`, based on main `08d51d4feadfe03695ca2af87370949b44cafa6b`. Runtime remains disconnected from the pilot.

## Review identity and exact scope

[Anti skill](/Users/reidar/.codex/skills/anti/SKILL.md), explicit `gemini-3.1-pro` / actual `gemini-3.1-pro`, provider `google-antigravity`; run `20261012T003458Z-0a12fd3e`. One helper generation attempt, no retry or fallback, complete successful response. Full-retention artifact:
`/Users/reidar/.codex/anti-runs/20261012T003458Z-0a12fd3e/revisions/e5425bb4a82a4012a002962c7c4447d5/result.json`
SHA-256: `306b04194c41535050ecafbb98d280f1b1df6127c4c371554c8b2da1c93236e6`.

The request supplied 53 complete public code/configuration/proof files plus the review request containing the complete tracked diff: 54/54 input items, zero excluded/omitted files or chunks. All 54 captured SHA-256 hashes and the tracked diff were checked again after the response and match. The selected files include every type-check manifest entry, all seven implementations corresponding to the new stubs, CI, prior author report and raw proof. Coverage proves supplied bytes, not a guarantee that an AI found every possible defect. No private knowledge/index records, pilot package contents or frozen evaluation records were sent.

Prompt SHA-256: `3d4f48ccff0f9320e05bcc487a7451b0701e4577b7714589383c3ef6c03cc6a7`; 522925 assembled characters. Data policy `docs/runtime-type-review-submission-policy-2026-10-12.json` permits only the named Gemini primary destination and excludes private/protected data paths. Its credential-pattern scan matched a substring of a public Norwegian service URL slug. The owner explicitly approved this exact prompt hash before submission; no code or scanner was changed to bypass it. Helper/package tree parity matched. Context preflight remained explicitly unknown despite the advertised window; a completed response and source coverage do not independently verify that limit.

Anti's complete verdict is retained in the evidence JSON. It reports no actionable findings. The two caveats have these dispositions:

1. Seven `.pyi` interfaces are in the checked scope; their underlying older implementations are not directly checked for diagnostics. Public implementations were supplied for comparison. Zero warnings applies to the 42 explicit checked files, not the whole runtime/repository.
2. Synthetic/replay verification does not clear live-provider, legal/clinical, human, release or pilot gates. Phase-3 discovery uses replay; separate experimental live-capable V2.5 paths remain unactivated.

A planned native Luna dispatch never started: the hook rejected the unregistered `worker` role. The registered review role uses Sol, prohibited by this parent's gate; manual routed alternatives were unavailable because OCX reported its proxy was not running. No proxy/configuration/login/role setup was changed, no child was spawned, and those failures are not review evidence. The successful independent evidence is the separate, owner-approved Anti generation.

## Fresh local verification

- basedpyright 1.39.3, all 42 explicit candidate paths: **0 errors, 0 warnings, 0 informational diagnostics; exit 0**. No suppression or severity change.
- CI-equivalent module command on Python 3.10.4: **68/68 PASS**, elapsed 0.376s.
- Same command on Python 3.14.6: **68/68 PASS**, elapsed 0.349s.
- Both runs: zero failures, errors, skips, expected failures, unexpected successes and guarded DNS/socket/subprocess/browser attempts.
- All original 63 methods plus five boundary methods remain; no test/source/workflow edits were necessary in this review turn.
- Current source hashes match the existing 42-file type-cleanup receipt and manifest `1db6cfd0bf67e4753a6ca14a09c6ed39a8d73d071121d451898b7c4fb0b34419`.
- All 42 selected type-check source/stub files parse; `git diff --check` passes; no synthetic fixture leftovers.

Commands from the worktree root:

```sh
PYTHONPATH=runtime /usr/local/bin/python3.10 -m tools.runtime_synthetic
PYTHONPATH=runtime /opt/homebrew/bin/python3.14 -m tools.runtime_synthetic
python3 -c 'import json, subprocess; from pathlib import Path; paths = json.loads(Path("docs/runtime-type-evidence-2026-10-12.json").read_text())["runtime_source_hashes"]; raise SystemExit(subprocess.call(["basedpyright", *paths]))'
```

Direct file invocation without the documented import path fails with `ModuleNotFoundError: No module named runtime`; it is not the CI invocation. The module commands above match the workflow and pass. No environment workaround was added to product code.

Tests ran against the same uncommitted source bytes supplied to the reviewer. No runtime/test/workflow source changed afterwards, so a second identical run is unnecessary. Existing source/type/test receipts remain immutable historical evidence; this report and `runtime-type-review-evidence-2026-10-12.json` add independent review and fresh proof.

## Preservation

The final readback passes all existing preservation checks: original candidate runtime hashes, 36 protected original files, both pilot HTML/ZIP hashes, `runtime_enabled=false`, primary checkout HEAD/status/README, frozen evaluation Git tree and metadata, and historical package metadata. Active diff for pilot/evaluation/data/phase-1/schema implementations is empty.

Frozen evaluation tree: `dbb2c7ad8d0ddb4f9d0ae77b9d52714d532deb55`. Evaluation metadata: 11433 entries across two roots, SHA-256 `9d3888d7fe24e6ec3027c6e3e4612069b0fced78382f23da0b94c5cf01a9625d`. Historical pilot metadata: 8473 entries across 18 roots, SHA-256 `affaa1195f76a1b11203fbf7f5b559ac96a4e1e573efd482ac2f011403ea8f06`. These metadata fingerprints are not a semantic or full-byte audit of private archives.

No pilot rebuild/activation, private-record demonstration, frozen evaluation execution/rescore, source-authority revalidation, remote CI for this increment, commit/push/PR/merge or deployment occurred. Disk space was briefly 29.97GiB; no long build/test loop ran, and the bounded synthetic suites each took less than one second.

Machine-readable evidence: [runtime-type-review-evidence-2026-10-12.json](runtime-type-review-evidence-2026-10-12.json).
