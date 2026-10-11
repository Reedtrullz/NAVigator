# Independent runtime review - 2026-10-11

Status: INDEPENDENTLY_REVIEWED / FINDINGS_REPAIRED / SYNTHETIC_VERIFIED / PILOT_DISCONNECTED. The owner subsequently authorized one local commit containing this report and the verified candidate.

## Work ledger

- [x] Independent review of the exact runtime candidate and synthetic tests.
- [x] Reproduce and repair confirmed findings, or record the evidence rejecting them.
- [x] Run the guarded synthetic suite and verify protected pilot bytes.
- [x] Record final evidence in this receipt and Obsidian.

## Review request

Review the current bytes in this isolated worktree, including the untracked runtime Python files. Base/HEAD is a09cb28864bbc45ef48cbdb0afa92f6b12ac1a79; the 28-file runtime source manifest before review is cb0155b66ba02a8e6787f152e27a0a6f65bfadb977b6fea06a0b7f68d90099b7. Inspect the entire supplied source, including callers and tests; report concrete defects with file, function/line, severity, a triggering synthetic example and expected behavior. Distinguish actual defects from optional changes. Return explicit scope/coverage limitations and an assessment of the candidate.

Requirements:

1. General knowledge admission must fail closed before source reads unless an explicit profile pins permitted document identity, path, class, content hash, domains, freshness and source date. Private/case/derived content cannot enter general answers. Reuse admitted context without reopening indexed paths.
2. Norwegian normalization must preserve signal/negation behavior. Absence of a lexical signal does not establish medical safety. No real clinical or legal advice is in scope.
3. Gaps, historical sources, missing dates and incomplete retrieval must not establish present-day verified facts or a complete answer. Keep uncertainty and source-specific evidence through serialization.
4. A verified route dimension requires evidence for the same service, source URL/hash, dimension and actual supporting span. Compare the actual user's age with actual bounds; do not treat the presence of an age as eligibility. No route-wide fallback references for unsupported dimensions.
5. Failed output validation or terminal stage failures must emit a fixed safe answer without the rejected recommendation, and truthful status/trace. Recoverable retrieval/discovery failure must preserve unaffected tracks and report incomplete coverage.
6. Source and sitemap HTTP must reject nonpublic DNS/IPs, pin checked numeric destinations, preserve HTTPS host verification, and recheck redirects with bounded time/bytes. Source authority is separate from network permission. The default browser renderer stays disabled; injected renderer callbacks are synthetic fixture seams, not an approved live renderer.
7. V2.5 accounting distinguishes attempts, successful pages, detected services and completed protocol work. Empty pages and unimplemented/capped protocol steps cannot fabricate service evidence or full completion.
8. The pilot remains disconnected. No pilot/evaluation/schema changes, private-corpus reads, live runtime/provider calls, commits, pushes, deployment or activation are authorized by this review. The external reviewer is advisory; native Codex reproduces and fixes findings locally.

The intentional candidate contracts include RetrievalResult instead of a raw record list, default-deny knowledge admission, unknown age/proof staying unresolved, fixed safe rejected output and disabled live browser rendering. Do not classify these requirements as defects merely because older frozen callers/assertions expect the previous behavior; identify any remaining candidate caller that is actually inconsistent.

Only explicitly selected runtime code, synthetic tests and this request may be submitted. Personal/case records, evaluation packets, knowledge source documents, credentials and pilot packages are excluded.

The review request above is historical: it did not authorize commits. The owner's subsequent explicit commit request authorizes local packaging of the repaired candidate and these receipts. Review scope and all pilot/privacy/frozen-evaluation restrictions still apply. Fresh commit-stage evidence is in [runtime-commit-evidence-2026-10-11.json](runtime-commit-evidence-2026-10-11.json). The reviewed/repaired manifest below is 3446d0b081e4feddce7829891b34a53438dc2498b447539d7efa50faa966dd37; commit packaging only removed one redundant final blank line in test_fetch_accounting.py, producing 71448516b85feff55ad19aefa584940c9eca29e877c298cd19b14e73157fcbef. The full guarded suite and static check were rerun on these final bytes; no behavior changed or further external review was claimed.

## Evidence

Independent Anti sidecar review completed with claude-opus-4-6-thinking through Google Antigravity. Requested and actual model agree; one attempt, no retry or fallback. Run 20261011T210304Z-1917ba01, result: /Users/reidar/.codex/anti-runs/20261011T210304Z-1917ba01/revisions/3fbd6add35974501b34d57c01b1c9c42/result.json. Selected-source coverage is complete: 36 files, all 28 candidate Python files plus seven supporting modules and this request, no omitted/truncated selected bytes. Prompt: 221484 characters; input/output tokens 65030/7651. This is an independent advisory model review, not a professional approval or model consensus. Native Codex owns the reproduction and repairs.

The unchanged discovery/engine.py context file was excluded after the credential scanner matched a Norwegian service URL keyword. No credential acknowledgement or policy override was used. Direct inspection of the unchanged extractor, frozen V1 orchestrator, classification_gate_v25.py, schema contents and data documents is outside the external review scope. They are not silently counted as reviewed. Canonical imports, protected schema hashes and injected source/discovery behavior are checked locally.

The OmO route remains unavailable for ordinary reviewer dispatch: fixed roles/receipt agree, but toolAcceptance is pending and its receipt names a different chat. The independently ready Anti sidecar provided the requested review without changing routing configuration.

## Finding dispositions

| Reviewer item | Verdict and evidence |
|---|---|
| 1. context.py absolute import | Not a candidate regression under the documented PYTHONPATH=runtime / sut.phase2 and sut.phase3 entrypoints. Both imports succeed and the guarded suite runs through them. The shared phase-1 context stays frozen. Root-only runtime.sut imports remain unsupported; no additional packaging contract was introduced. |
| 2. Phase-2 emission crash leads to KeyError | Confirmed and repaired. Emission failure discards partial output and returns a schema-valid fixed safe answer with no routes/claims. |
| 3. Every Phase-2 crash marked RECOVERABLE | Confirmed and repaired. Share the existing phase-3 stage handler with phase 2; only retrieval/discovery crashes are recoverable, with explicit incomplete receipts. Other crashes are TERMINAL and prevent recommendation emission. Error messages expose exception types only. |
| 4. Ignored municipality argument / other official domains | Removed the unused argument and updated both callers and the synthetic test. Recognition remains deliberately bounded to approved host patterns. Municipality text cannot authorize a partner/other domain. Supporting additional official hosts requires an approved authority registry before live activation; this review does not invent one. |
| 5. _dimension_claims ignores route | Minor signature issue repaired: remove the unused argument at both callers. Keep the frozen five-dimensional claim vocabulary. |
| 6. Unix file flags unavailable on Windows | Recorded platform qualification limit. No Windows target or permission to weaken no-follow admission was supplied. macOS execution is verified; Windows access admission remains unqualified and must not be enabled from this receipt. No fallback that follows links was added. |
| 7. Documentation IP public on Python <3.11 | Rejected by direct local check: Python 3.10.4 reports 192.0.2.1.is_global=False; Python 3.14 synthetic host-policy tests also reject it. This does not qualify every Python version. |
| 8. Missing Phase-2 crash test | Repaired with four new synthetic methods covering all nine non-retrieval stages, incomplete recovery, invalid inputs and trace precedence across phases. No frozen test was weakened or executed. |
| 9. cached_property leaks corpus mutations across tests | Rejected: unittest constructs separate TestCase instances for each method; the original 11-method suite has 11 unique instance identities. cached_property belongs to an instance, not the class. SyntheticCorpus registers cleanup on that same instance. |

Additional findings reproduced while exercising the same failure boundary: partial output can survive an emission crash; a previous RECOVERABLE marker can hide a later TERMINAL state in the trace; Phase-2 nonobject input raises AttributeError rather than returning a safe rejection. Fixed in the shared handler/trace and Phase-2 input guard. Invalid schema messages are also redacted to INPUT_REJECTED.

Ruling: Stage failure semantics and trace precedence now live once in phase2/pipeline.py and are reused by phase 3. Cost: the internal Phase-2 entrypoint now uses the same stronger failure contract as the candidate's Phase-3 entrypoint; phase 1 and frozen contracts remain unchanged.

## Reproduction and verification

- Before repair: four new methods produced 11 failed subtest assertions and six errors, including two KeyError cases, a partial output schema failure, nonobject AttributeError and false SUCCESS/RECOVERABLE traces. No real network or subprocess calls were permitted.
- Final repair verification: combined guarded suite 63 tests, zero failures/errors/skips and zero real DNS/connection/subprocess/browser attempts. Includes 12 phase-3 end-to-end methods (the original 11 plus a Norwegian source-fact case) and four cross-phase failure methods. The earlier 62-test run preceded the closure-review repairs.
- 28 candidate Python files parse; final basedpyright reports zero errors and 2526 unsuppressed warnings, exit 1. Strict type qualification remains incomplete.
- After edits: 36 protected tracked pilot/contract/register/phase-1 files byte-match the base, pilot HTML/ZIP hashes match the prior receipt, and runtime_enabled=false. git diff --check passes; synthetic temporary directories and matching Vifty scratch directories: zero.
- Final tested runtime source manifest: 3446d0b081e4feddce7829891b34a53438dc2498b447539d7efa50faa966dd37, using the same 28-file algorithm as the candidate receipt. The preceding 62-test revision was 3bc2b3b6f04282fa51e9fd4a4e1f3fc85f0f8cc0f535691361908ca5a4821f9f.

## Targeted closure review request

Review only the supplied phase2/pipeline.py, phase3/pipeline.py, phase3/finalize.py and phase3/test_runtime_synthetic.py against the failure-boundary requirements above. The prior broad review covered all candidate files; unused-argument removals are checked locally by the full suite and are not resubmitted in this narrower closure. Check that the confirmed crash/emission/trace defects are closed and that sharing existing stage handling introduces no new failure path or output leak. Do not reopen optional platform, authority-registry or packaging scope as an implemented requirement. Return remaining concrete defects and limitations in at most 500 words; if no remaining actionable findings, say so. No patches or commands to execute. The same read-only, synthetic-only and pilot-disconnected requirements remain binding.

The first eight-file closure attempt, 20261011T211149Z-a195fa4b, hit its 6000-output-token limit. It is FAILED / PARTIAL, with no usable retained findings or closure verdict; it is not a successful review gate. A new narrower request with a 12000-token output allowance follows the same exact model and data policy, without fallback or credential override.

## Completed closure review and final dispositions

Run 20261011T211557Z-24967c32 completed successfully on all five selected files, no omissions or truncated selected bytes. Requested/actual claude-opus-4-6-thinking agree, one attempt, no fallback; 61167 prompt characters and 17433/4400 input/output tokens. Result: /Users/reidar/.codex/anti-runs/20261011T211557Z-24967c32/revisions/2fd08f7fd5c64124b673fa3260ce17b8/result.json. The reviewer confirms the original crash/emission/trace repairs and finds no new output-leak path from the shared handling.

| Closure item | Final disposition |
|---|---|
| 1. Claim helper ignores claims argument | Repaired: compare the caller's actual filtered claim strings; remove the redundant context parameter. Full guarded suite verifies the same finalization paths. |
| 2. Consistency helper ignores uncertainty argument | Remove the unused argument at its only caller. Existing plan-reference resolution and required incomplete-discovery wording checks remain active; no broader uncertainty validation is claimed. |
| 3. Route-label helper ignores ctx | Remove the unused argument at its only caller. |
| 4. Unreachable terminal-status branch | Remove it; the earlier terminal guard still emits fixed safe output before rendering, covered by failure/rejection tests. |
| 5. Norwegian facts spuriously rejected | Rejected by an actual end-to-end source/admission/planning/render/finalize test. The renderer applies the same established ascii_text mapping to INFO values and route labels. Original Unicode remains in structured claims. The test's first expectation incorrectly used o instead of the established oe mapping; corrected against the unchanged render.py table before any production repair. |
| 6. Failed output lacks safety_class | Confirmed shape inconsistency, repaired with explicit null. Three rejection tests failed on the missing field before the one-line fix and pass afterward. Both candidate entries reuse this safe output shape. |
| Repeated provenance construction | Optional performance observation, not a correctness defect. No cache/abstraction added without a measured need. |

No confirmed correctness finding is left deferred. Platform/authority/packaging qualification and the stated omitted unchanged context remain explicit limits. The closure reviewer inspected the shared-handler revision; the subsequent small shape/signature repairs were verified locally with the final guarded suite, not resubmitted for another broad review.

Ruling: Failed outputs explicitly carry safety_class=null. Cost: no diagnostic safety class is inferred after an aborted stage; frozen schemas stay unchanged. Historical evaluation and release gates are not promoted.

Obsidian: /Users/reidar/Obsidian/Hermes/Hermes/Personal/Projects/NAV Explore/NAVigator runtime repairs - 11-10-2026.md, section Independent review and repairs; linked from the project index and today's daily Log. No private records or secrets were logged.
