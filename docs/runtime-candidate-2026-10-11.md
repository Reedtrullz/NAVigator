# NAVigator runtime candidate - 2026-10-11

Status: SYNTHETIC_VERIFIED / PILOT_DISCONNECTED. Candidate for an explicitly authorized local commit, not an activation approval.

Worktree: /Users/reidar/.codex/worktrees/navigator-contact-pilot/NAVigator
Branch: codex/navigator-contact-pilot
Runtime change base: a09cb28864bbc45ef48cbdb0afa92f6b12ac1a79
The owner explicitly authorized one local commit of the verified runtime candidate, review report and test evidence on 2026-10-11. The commit containing this receipt identifies that candidate. The primary checkout is preserved; push, PR, deployment and pilot rebuild remain outside this authorization.

Plan: [R1-R7](superpowers/plans/2026-10-08-navigator-runtime-plan.md).
Execution decisions, failures before repair and review: [ledger](runtime-implementation-2026-10-11.md).
Independent reviewer findings, repairs and scope: [review receipt](runtime-independent-review-2026-10-11.md).
Fresh commit-stage test results, explicit source hashes and preservation baseline: [machine-readable evidence](runtime-commit-evidence-2026-10-11.json).

## Observed verification

- Eight explicitly named synthetic modules: 63 tests, zero failures/errors/skips. Includes 12 phase-3 end-to-end methods through the real S1-S11 entry and stages and four additional cross-phase failure methods, with only discovery/transport/failure boundaries replaced by fixtures.
- Guarded combined execution recorded zero real DNS, socket connection, subprocess and browser attempts. The initial R6 RED isolation mistake is recorded in the ledger; it is not included in this zero-attempt claim.
- Scenarios include unauthorized private opens, missing/hash-rejected sources, arbitrary GAP_REGISTRY IDs, Unicode/negation pairs, actual age mismatch, other-service and unsupported excerpts, source evidence surviving serialization, safe rejected answers, stage crashes and truthful terminal traces.
- V2.5 checks distinguish attempts, successful fetches, empty pages, provider failures, capped/unimplemented protocol work and redirected source authority. A service-looking URL cannot establish a service on an empty page.
- DNS checks reject any nonpublic member of a resolution, connect to the checked numeric address, retain the original TLS hostname and check every redirect. Authority uses exact/dot-bounded hosts separately from public network permission. The default browser renderer is blocked.
- Syntax parsed for all 28 changed/new runtime Python files. Independent basedpyright 1.39.3: zero errors, 2,526 warnings, exit 1 because warnings remain. Mostly untyped/unknown Python interfaces; no warning suppression. This is not a clean strict-type gate. Previous native LSP checks were on the pre-review candidate; the current CLI check covers the repaired bytes.
- git diff --check: PASS. Synthetic temporary directories remaining: zero. Disk preflight for the independent-review work: 43Gi free; no matching Vifty temporary directories.

Runtime source manifest SHA256:

`71448516b85feff55ad19aefa584940c9eca29e877c298cd19b14e73157fcbef`

Manifest algorithm: initially select the union of git diff --name-only and git ls-files --others --exclude-standard, restricted to runtime/*.py recursively; sort paths, hash each file, serialize the path-to-SHA256 mapping with sorted keys and compact JSON separators, then SHA256. After commit, use the explicit 28-path runtime_source_hashes mapping in the machine-readable evidence to reproduce the same manifest from committed blobs. Documentation and the pre-existing untracked AGENTS.md are excluded from the runtime manifest; AGENTS.md is also excluded from the commit.

Fresh commit-stage execution on the same runtime bytes: 63/63 tests, zero failures/errors/skips and zero guarded DNS/connection/subprocess/browser attempts; all 28 files parse, git diff --check passes and synthetic fixture directories remaining are zero. The evidence records the actual timestamps, Python version, per-module counts and reproduction invocation. The 36 protected tracked files and both pilot package content hashes match the base/prior receipts; frozen evaluation and ignored historical package snapshots use metadata only, without reading private records.

Commit packaging removed one redundant final blank line from the new test_fetch_accounting.py after the first cached diff check detected it; the earlier working-tree check did not include untracked files. This is the only byte change from the reviewed manifest 3446d0b081e4feddce7829891b34a53438dc2498b447539d7efa50faa966dd37. The complete guarded suite and basedpyright were rerun on the final manifest above: 63 tests pass; zero static errors and 2526 unsuppressed warnings, exit 1.

## Reproduce only the candidate suite

Run from the worktree, with PYTHONPATH=runtime. Do not use unrestricted unittest discovery.

```python
import unittest
from unittest.mock import patch

modules = [
    "sut.phase2.test_privacy_scope", "sut.phase2.test_semantic_normalization",
    "sut.phase2.test_source_admission", "sut.phase2.test_evidence_integrity",
    "sut.phase3.test_rejection_synthetic", "sut.phase3.test_runtime_synthetic",
    "runtime.discovery_v2.test_fetch_accounting", "runtime.discovery.test_host_policy",
]
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
with patch("socket.getaddrinfo", side_effect=AssertionError("NO_REAL_DNS")) as dns, \
     patch("socket.create_connection", side_effect=AssertionError("NO_REAL_CONNECTION")) as connect, \
     patch("subprocess.run", side_effect=AssertionError("NO_REAL_SUBPROCESS")) as child, \
     patch("subprocess.Popen", side_effect=AssertionError("NO_REAL_BROWSER")) as browser:
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    attempted = any(g.call_count for g in (dns, connect, child, browser))
raise SystemExit(0 if result.wasSuccessful() and not attempted else 1)
```

## Internal contract changes

| Previous behavior | Candidate behavior | Compatibility cost |
|---|---|---|
| Default knowledge index admitted by hash/class after opening | Explicit knowledge-access/v1 profile precedes document open; permission, ID, path, class, hash, domains, freshness and date are pinned | Default configuration admits no knowledge corpus; real curated permissions have not been granted by these tests |
| retrieve returned a list | RetrievalResult(records, failures, coverage); S4 records per-track coverage/failures | Direct historical callers must migrate to .records; their expectations are not silently adapted |
| GAP/historical/undated records could support current facts | Nonfactual records are unresolved and labelled in user text; source-specific dates survive | Fewer positive verification claims; no historical score comparison |
| Discovery IDs alone could bind a route dimension | Service ID, URL, hash, dimension, locator, identity and the matching age/access/scenario excerpt required; dimension_sources retains the admitted proofs in output | Legacy rows without this proof remain unresolved; unsupported access markers cannot positively verify |
| Heading/table rescue reopened an indexed path | Already-admitted source_lines only | No rescue without admitted context |
| Fixed provenance verification date | Actual approved source date; null in source-admission/v2, empty string where frozen output v1 requires a string | Frozen clients must consult the additive receipt to distinguish unknown dates |
| Accepted partial tracks could be presented as complete | Every track must be FULLY_VERIFIED and knowledge/discovery complete | Stronger candidate presentation gate; frozen contracts/scores untouched |
| Rejected render copied back into answer | Fixed safe answer, empty routes/claims, TERMINAL output_emission in both output and trace | Rejected recommendation text is unavailable in normal output |
| Phase-2 crashes marked RECOVERABLE, late emission raises KeyError | Shared stage handling with phase 3, explicit incomplete retrieval/discovery receipts, other failures TERMINAL; discard partial output and emit a validated safe answer | Both candidate entries use the stronger failure contract; phase 1 remains frozen |
| Fetch attempt implied success/COMPLETE | discovery-execution/v1 carries attempted_fetches, successful_fetches, protocol_completed, services_found, unsupported_levels and unfetched_candidates | Declared levels beyond 1/2 remain incomplete in V2.5; full frozen protocol completion is not claimed |
| HTTP/render followed unchecked destinations | Shared pinned public HTTP for source/sitemap fetch; browser default fails closed | JS-only live rendering unavailable; injected render callbacks are fixture seams only |

Frozen input/output/context schema files remain byte-identical. The additive evidence maps use existing output extensibility; they are explicit candidate revisions, not rewritten frozen schemas. Phase 1, the original V1/V2 orchestrators, evaluation locks, source registers and historical scores were not edited or executed. V2.5 remains separate from the phase-3 replay adapter and the pilot. Older Brave/Tavily external-search lineages were not activated or qualified by this task.

## Legacy test inventory

Source inspection only: 29 existing modules classified below, none executed in this task. "Public fixture" describes the inspected dependency, not present-day source/legal approval. Several assertions encode older contracts; do not relax them to make this candidate look compatible. Migrate under a separate, scoped decision.

| Class | Modules |
|---|---|
| Synthetic component/source-structure tests | runtime/sut/test_context.py, test_schemas.py, test_separation.py; runtime/sut/phase2/test_aggregate.py, test_decompose.py, test_route_targets.py; runtime/sut/phase3/test_phase3.py, test_planner_scoping.py; runtime/discovery_v2/tests_v24.py, tests_v25.py |
| General rule/protocol or public replay/challenge fixture dependencies | runtime/discovery/tests.py; runtime/discovery_v2/tests.py, tests_v21.py, tests_v23.py; runtime/sut/phase2/test_discovery_adapter.py, test_routes.py, test_safety.py; runtime/sut/test_pipeline.py, test_safety_granularity.py, test_safety_output.py |
| Implicit repository knowledge access or direct source reads needing curated replacement/permission review | runtime/sut/phase2/test_knowledge.py, test_knowledge_scoping.py, test_pipeline_ids.py, test_route_propositions.py; runtime/sut/phase3/test_route_binding_wave4.py; runtime/sut/test_evidence_attachment.py, test_national_routes.py, test_input_normalization.py |
| Actual credential lookup / external provider boundary | runtime/discovery_v2/tests_v22.py includes load_tavily_api_key; excluded even though most requests in it use fake transports |

## Preservation and later integration

- 36 tracked pilot source/data/build/package, runtime schema, phase-1 context/schema/pipeline and knowledge/rule register files byte-match the base; zero mismatches. No evaluation/data/pilot/schema Git changes.
- Pilot HTML SHA256: 056c87a636b91d4cfd3502ae89d44faa4ecf5d0b01333c43b48c28250f5eb00c.
- Pilot ZIP SHA256: ab2f842cea4ce827407097a45e3620518c4116e23187ea382e763d152fe4a8bb.
- Both packaged hashes match the before-work values. pilot/data/input-policy.json still has runtime_enabled=false. The existing UTKAST/BLOCKED pilot posture is not promoted by these tests.
- The original self-review has been followed by an independent Anti/Opus review of all 28 candidate files and selected supporting context, then a completed targeted closure review. Confirmed findings were reproduced and repaired; scope, the discarded truncated attempt and individual dispositions are in the review receipt. The native OmO role gate remains pending and was not bypassed by changing routing.
- Before integration: grant/review a bounded general access profile; adapt consumers to the explicit receipts; prove any enabled discovery protocol/transport and source-specific evidence; complete legal/clinical, privacy and human acceptance as appropriate. Additional host authorities and Windows/other runtime platforms remain unqualified. Synthetic success alone authorizes none of these transitions.

Not measured: current law/medical guidance, real source accuracy/recall, live provider capability, browser networking, owner/device trials, CI or deployed behavior. No private-record demonstration or frozen evaluation rescore was performed.
