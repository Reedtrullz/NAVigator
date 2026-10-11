# NAVigator runtime repairs - 2026-10-11

Plan: docs/superpowers/plans/2026-10-08-navigator-runtime-plan.md
Base: a09cb28864bbc45ef48cbdb0afa92f6b12ac1a79
Worktree: /Users/reidar/.codex/worktrees/navigator-contact-pilot/NAVigator

## Pre-flight interfaces

| Producer / consumer | Check and decision |
|---|---|
| R1 access profile / R3 S4 result | Explicit general permission precedes file opening; R3 will retain failures and bounded coverage through S4. |
| R2 normalization / R1-R3 retrieval | Matching changes only derived match text, never source excerpts or byte hashes. |
| R3 records / R4 claims and provenance | Historical and gap records cannot become VERIFIED facts; source dates are source-specific. |
| R4 route evidence / R5 finalizer | Dimensions require matching service evidence; finalization may never restore rejected answer text. |
| R6 V2.5 / R7 phase-3 | Separate lineages remain separate. Fake discovery injection exercises phase-3 without adopting live V2.5. |

Initial ruling (before the later explicit commit request): keep repairs as reviewable local changes and retain this ledger; do not use commit-dependent skill scripts or delete their evidence. Cost at that point: no new commit identity until the user requests one.

Ruling: Frozen output v1 requires a string verified_at. Missing dates will use an empty string in that adapter and explicit null/unknown in an additive versioned evidence receipt; frozen schema files remain unchanged. Cost: legacy clients must consult the revision receipt to distinguish unknown dates.

## Tasks

- R1 complete: unauthorized-open failure observed before repair; 5 synthetic tests PASS. Explicit ID/path/class/hash permission, no-follow directory descriptors, and redacted failures. S4 forwards the same profile and root. Fresh LSP diagnostics distinguish stale hook output from current errors; touched pipeline imports made relative and heterogeneous JSON entry annotated.
- R2 complete: 9 failing assertions observed; 5 semantic test methods PASS after shared match normalization and overlapping signal negation. Together R1/R2: 10 PASS. Original excerpts and frozen vocabulary unchanged; no-signal remains unknown in the additive receipt.
- R3 complete: 6 source-admission tests PASS; observed VERIFIED gaps/historical records, dropped failures, and constant dates before repair. RetrievalResult now carries bounded coverage and failures; S4 retains per-track receipt, provenance dates are source-specific, and emission uses additive source-admission/v2 evidence.
- R4 complete: 9 synthetic methods PASS. Six original failures plus adapter metadata loss observed before repair. Independent track states, actual age bounds, per-service/per-dimension evidence and unique IDs; adapter forwards explicit evidence and national reasoning consumes admitted context only.

Ruling: National heading/table extraction now consumes already-admitted source lines, never reopens an indexed path. Cost: callers without admitted context cannot use heading/table rescue.

Ruling: Legacy discovery rows without service identity, source hash, dimension, locator and excerpt cannot positively verify a dimension. Universal/group wording without numeric age criteria remains unresolved. Cost: historical routes can be downgraded until explicit evidence is supplied; no old scores are recomputed.
- R5 complete: 3 synthetic rejection tests PASS after observing rejected answer text restored and schema errors exposing rejected values. Rejection emits a fixed safe answer, no routes/claims and output_emission TERMINAL. Combined R1-R5: 29 PASS.
- R6 complete: synthetic query/fetch accounting, actual age extraction and final-URL provenance gate; hostname boundaries, public DNS, pinned IP/TLS, every redirect and response-size limit. Default browser rendering is blocked. Final combined receipt will supersede intermediate counts.
- R7 complete: combined guarded suite 58/58, zero failures/errors/skips or real DNS/connection/subprocess/browser attempts. Eleven end-to-end methods through phase-3; legacy inventory and protected-file receipts in runtime-candidate-2026-10-11.md. Source manifest and static diagnostics recorded there; no integration approval.

## Boundaries

Ruling: The approval profile also pins domains, freshness and verified_date. Observed an index-only metadata change promoting an unchanged historical source; the source is now rejected. Cost: profiles lacking these metadata pins cannot confer positive current-source evidence.

Ruling: Browser rendering defaults to failure until redirects and subresources can enforce the pinned boundary. Injected render callbacks are fixture seams only. Cost: JavaScript-only sites cannot supply live rendered content through this candidate.

Ruling: V2.5 claims protocol completion only when all declared levels are implemented, all query families return honest SUCCESS/NO_RESULTS, and all selected sources fit the fetch budget and succeed. Levels beyond 1/2 are explicitly unsupported here; a frozen full protocol therefore remains incomplete. Cost: fewer COMPLETE runs; no implicit claim that sitemap/link traversal is finished.

Ruling: presented_as_complete requires FULLY_VERIFIED for every track in the candidate; partial access or unknown suitability cannot pass this stronger presentation gate. Cost: historical presentation expectations may differ; frozen contracts/scores are not rewritten.

Test isolation correction: the first R6 RED transport test patched a not-yet-used shared function and let legacy curl attempt the reserved public.example test name. Later tests block subprocess/network entrypoints and mock DNS/transport. No production/provider or private case endpoints were used.

Final review: self-review after fresh native reviewer dispatch was blocked by the registered-role hook. Matching installed reviewer roles could not be used under the current acceptance/routing constraints. No generic/routed substitution; ocx sync returned omitted IDs/HTTP 405 and catalog stayed stale. Ruling: use author review to finish the local repair/test artifact; retain independent review as a later activation gate. Cost: the author may miss defects a fresh reviewer would catch.

Final: fixed arbitrary GAP_REGISTRY ID promoted to VERIFIED - test_gap_class_not_dependent_on_known_document_id RED to GREEN, suite 58/58.
Final: fixed identity/marker/age mismatch in purported source excerpt - test_identity_or_marker_mismatch_in_excerpt_cannot_verify_dimension and test_age_metadata_must_match_actual_excerpt RED to GREEN, suite 58/58.
Final: fixed dimension excerpts missing from final serialized evidence - test_actual_dimension_evidence_survives_serialization RED to GREEN; source proof records retained and claim references validated, suite 58/58.
Final: fixed unqualified gap rendering - test_gap_information_is_qualified_in_user_answer RED to GREEN, suite 58/58.
Final: fixed rejected output reported SUCCESS in stage trace - test_rejection_is_terminal_in_stage_trace_as_well_as_output RED to GREEN, suite 58/58.
Final: fixed service-looking URL falsely establishing service on an empty page - test_empty_success_is_complete_without_claiming_service additional assertion RED to GREEN, suite 58/58.

Static gate limitation: independent basedpyright gives zero errors but 2,531 unsuppressed warnings and exit 1; this is not a clean strict-type claim. Fresh native error diagnostics for the critical security/routes/phase3 entry files are empty. No style/minor findings were deferred as repairs; historical contract migration and nontechnical acceptance remain distinct work.

Runtime stays disconnected from the pilot. No live providers, private-record retrieval, frozen evaluation execution, schema rewriting, model-generated advice, deployment or GitHub writes are authorized by this task. Technical checks do not confer clinical/legal/product approval.

## Independent review follow-up - 2026-10-11

The user explicitly requested the missing independent review and repairs. Anti/Opus reviewed all 28 candidate Python files and seven supporting modules plus the review request in one bounded call, run 20261011T210304Z-1917ba01. Scope, model identity, excluded context and all nine dispositions are in [the review receipt](runtime-independent-review-2026-10-11.md); the earlier blocked-review paragraph above is historical.

Confirmed Phase-2 crash/emission defects were reproduced with four new synthetic methods: 11 failed subtest assertions and six errors before repair. Shared existing Phase-3 handling with Phase 2; added safe emission fallback/input rejection and terminal precedence over earlier recoverable markers, and removed unused helper arguments. Phase 1 remains byte-identical. No frozen test was rewritten, relaxed or executed.

Current guarded suite: 62/62 methods, zero failures/errors/skips and zero real DNS/connection/subprocess/browser attempts. Current basedpyright: zero errors, 2534 unsuppressed warnings, exit 1. 36 protected tracked pilot/contract/register/phase-1 files byte-match base; HTML/ZIP hashes unchanged; runtime_enabled=false. Runtime manifest 3bc2b3b6f04282fa51e9fd4a4e1f3fc85f0f8cc0f535691361908ca5a4821f9f. Targeted independent closure review remains pending at this ledger update.

Closure completed: run 20261011T211557Z-24967c32 confirms the repaired failure boundary without new leakage. Previous run 20261011T211149Z-a195fa4b was truncated/failed and supplies no gate. Repaired the additional safety_class=null shape gap after three RED rejection tests; removed unused finalizer arguments and unreachable code. Norwegian source-fact behavior was already correct under the established renderer mapping and is now exercised end to end. Optional provenance caching was not introduced.

Final superseding receipt: 63/63 guarded methods, zero failures/errors/skips or real DNS/connection/subprocess/browser attempts; 28 parsed Python files; basedpyright zero errors, 2526 unsuppressed warnings, exit 1. All 36 protected files and both pilot hashes remain unchanged, runtime_enabled=false; diff check PASS and synthetic leftovers zero. Source manifest 3446d0b081e4feddce7829891b34a53438dc2498b447539d7efa50faa966dd37. All confirmed findings handled; external review scope and nontechnical/live/platform limits remain documented. Logged in the existing Obsidian runtime note, project index and daily Log.

## Owner-authorized commit packaging - 2026-10-11

The owner now explicitly requests a local commit of the verified runtime candidate with its independent review report and test evidence. This supersedes the earlier no-commit state only for those files. Use the existing candidate branch, leave the primary checkout and pre-existing untracked AGENTS.md untouched, and stage only the 28 runtime Python files and five candidate/review/evidence documents. Runtime remains disconnected; pilot/evaluation/data/schema files and packaged pilot evidence are excluded.

Fresh verification on the exact final runtime manifest: 63/63 guarded synthetic tests, zero failures/errors/skips or guarded external attempts; 28 files parse, diff check PASS, synthetic fixture leftovers zero. [The machine-readable receipt](runtime-commit-evidence-2026-10-11.json) records the source hashes, test invocation/counts/timestamps and pre-commit preservation baseline. The evaluation subtree remains dbb2c7ad8d0ddb4f9d0ae77b9d52714d532deb55. The commit containing these receipts is the candidate identity; final committed-tree readback and its SHA are recorded in Obsidian after commit. No push, pilot rebuild, frozen rescore, activation or deployment is included.

Packaging correction: the first cached diff check found a redundant final blank line in the new test_fetch_accounting.py; the earlier working-tree diff check did not cover untracked files. Remove that line only. Final source manifest is 71448516b85feff55ad19aefa584940c9eca29e877c298cd19b14e73157fcbef; the reviewed manifest above remains historical. Rerun the full guarded suite (63 PASS, zero external attempts) and basedpyright (zero errors, 2526 unsuppressed warnings, exit 1) on the final bytes. No test expectation or production logic changed.
