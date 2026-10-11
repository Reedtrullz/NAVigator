# PR 67 final independent review and redirect repair - 2026-10-12

Status: INDEPENDENT_REVIEW_APPROVE_WITH_INFORMATIONAL_FINDINGS / REDIRECT_REPAIR_SYNTHETICALLY_VERIFIED / FINAL_HEAD_GATES_REQUIRED / PILOT_DISCONNECTED.

## Independent review

Anti/Opus (`claude-opus-4-6-thinking`, Google Antigravity) independently reviewed commit 17766f03f5a27168df77d1f59357514c40e312e5 against canonical main 55eac73a54fbb05dac6e5ac9b1a70363fe9811ac. Run 20261011T221419Z-e960d385 completed successfully: all 36 changed PR files, six public supporting code files and a request containing the complete implementation/config diff were supplied in full. Coverage: 43/43 selected files, zero omitted/failed/truncated files, one Anti generation attempt, no retry/fallback. This is an advisory model review; native Codex reproduced the actionable observation.

Result: APPROVE with informational findings, no blocking defect reported. Result SHA256: 9384d8ce64b2b92f72e161dca37083a70c4391fd28fa628e37b6d98854939c90. Prompt identity: 224c67f02408ded732d325e07844283080635ae1b4b5153fe0bc53bfddfe6011. Provider-reported usage: 130376 input / 4891 output tokens. The helper's context-fit estimate remained unknown; successful execution and coverage do not independently prove a context-window limit.

## Findings and dispositions

| Finding | Native disposition |
|---|---|
| HTTPS redirects may silently downgrade to HTTP | Confirmed synthetically and repaired in the shared transport. An HTTPS hop now rejects a non-HTTPS target before any second DNS lookup/connection. |
| PR `edited` events also rerun CI after title/body changes | Kept deliberately: base-branch edits must rerun the protected-diff and exact-head checks. Removing `edited` would lose that event. Extra title/body runs are accepted overhead. |
| Knowledge reads use POSIX-only directory/no-follow flags | Existing documented platform limit, retained. CI supports Linux and local verification macOS; Windows support is not claimed. No weaker path-opening fallback was introduced. |
| FakeDiscovery exhausts its explicit status tuple if extra queries are added | Not a current defect: the synthetic protocol has exactly two queries and explicit per-query statuses. Fixture exhaustion exposes an unmodelled test change; no silent default status was added. |

## Repair and tests

Only shared `runtime/discovery/security.py`, its existing synthetic host-policy module and the runner's source-receipt path change. Initial HTTP sources remain allowed under the existing public-address policy. HTTPS-to-HTTPS, relative HTTPS redirects, HTTP-to-HTTPS and the original HTTP-to-HTTP behavior remain supported. URLs are still revalidated and resolved/pinned at each permitted hop.

Red proof before the transport fix: the existing redirect test, extended with lowercase and uppercase HTTP targets from an HTTPS origin, failed both new subtests. The old transport followed the downgrade until its redirect limit. After the fix, all eight host-policy tests pass, including the same downgrade cases and the permitted redirect variants. The tests use synthetic DNS/socket/HTTPConnection/TLS mocks, not live requests.

`PYTHONPATH=runtime python3 -m tools.runtime_synthetic` after repair: 63/63 test methods pass on Python 3.14.6, zero failures/errors/skips/expected failures/unexpected successes and zero guarded external attempts. New cases extend existing methods, so the eight-module count remains 63. This local run has Git parent 17766f0 and modified working bytes; it is source-manifest evidence, not exact-commit CI for 17766f0.

[New source receipt](runtime-final-review-evidence-2026-10-12.json) pins all 28 runtime files to manifest 9c79dc853f698d4765095b0ab1f4c3fedeb4ecca3c94fdc1c4370f3e71f858b8. The runner checks this receipt. Original [commit evidence](runtime-commit-evidence-2026-10-11.json) and previous reports keep their immutable earlier observation scope and are unchanged. Only the transport and its synthetic test bytes differ from that original runtime manifest.

A fresh independent delta review must cover the committed transport/test/runner/receipt/report change, and both CI matrix jobs plus downloaded receipts must pass for that exact final head before ordinary merge. Review outcomes and the final GitHub merge/main readback are retained in the Obsidian audit log with exact commits and native run artifacts.

Static check on the repaired 28-file runtime: basedpyright 1.39.3 reports zero errors and 2535 unsuppressed warnings (exit 1). The prior runtime had 2526 warnings. Strict type cleanliness is not claimed and the warnings were not suppressed.

## Preservation and limits

No changes to pilot, evaluation, data/registers, phase-1 context/pipeline or frozen schemas. The main-based worktree has no pilot directory or activation wiring. Original protected file/package hashes, frozen evaluation tree and evaluation/historical-package metadata are verified independently in the preserved original worktree and primary checkout. No pilot rebuild, frozen evaluation run/rescore, private-record demonstration, provider call or deployment occurs.

Review excludes unchanged extractor/DiscoveryPlanner source, classification_gate_v25.py, old V1 orchestrator, phase-1 pipeline, frozen schema JSON, registers and actual corpus/evaluation/pilot data. The two unchanged extractor/classification support files are outside external submission after credential-scanner false positives on Norwegian service slugs. The actual extractor is exercised by synthetic tests, which does not expand the model's source-reading scope. Existing package imports require the documented `PYTHONPATH=runtime` convention. Historical strict type warnings, authoritative content review, real-provider transport acceptance, source permissions, legacy migrations and human/pilot acceptance remain separate gates.

