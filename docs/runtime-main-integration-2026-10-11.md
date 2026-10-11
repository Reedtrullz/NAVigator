# Runtime main integration preparation - 2026-10-11

Status: MAIN_BASE_PREPARED / SYNTHETIC_LOCALLY_VERIFIED / CI_CONFIGURED / PILOT_DISCONNECTED. The pull request remains draft.

## Base and dependencies

The original reviewed commit is 3a1ea78a1291e1a44bfbfecce7731eebae01ea26, whose parent a09cb28864bbc45ef48cbdb0afa92f6b12ac1a79 includes three earlier pilot commits. Those pilot commits are not required by the runtime. The runtime commit was cherry-picked with its original identity recorded onto current main, 55eac73a54fbb05dac6e5ac9b1a70363fe9811ac. Replayed commit: 226e55c3ba256f5ee5b85733abeff195ba7641ac.

PR #67 is prepared to target main directly. The old a09cb28 review-base branch remains preserved. Before replacing the PR head, preserve the original 3a1ea78 commit on codex/navigator-runtime-reviewed-3a1ea78; use a force-with-lease bound to that exact old remote head. The original candidate worktree and primary WIP are untouched. No dependent pilot PR or pilot merge is needed.

| Dependency | Main integration disposition |
|---|---|
| Phase-1 context, canonical schemas, general rule registers and frozen V1 replay | Already present on main; no changes in this PR |
| Phase-2/3 and V2.5 runtime repairs | The same 28 reviewed runtime files; manifest unchanged |
| Eight synthetic modules | Standard library only, explicit module list, temporary synthetic corpus and fake transports; no pilot or real corpus dependency |
| Original R1-R7 plan | Preserve the original immutable a09cb28 plan link; do not import the older pilot/product commits |
| Original pilot source/packages | Retain in the original candidate and archived lineage; absent from the main-based runtime tree and PR diff |

Runtime source manifest remains 71448516b85feff55ad19aefa584940c9eca29e877c298cd19b14e73157fcbef. The independent [review report](runtime-independent-review-2026-10-11.md) and [original test/preservation receipt](runtime-commit-evidence-2026-10-11.json) retain their original candidate/base observation scope. Changing commit ancestry does not imply a new model review.

## Synthetic CI

[Workflow](../.github/workflows/runtime-synthetic.yml) runs on pull requests targeting main, including base edits. It checks out the exact PR head, verifies that head and the protected diff against the PR base, then runs [the explicit runner](../tools/runtime_synthetic.py) on Ubuntu 24.04 with Python 3.10 and 3.14. No package installation is needed.

The runner verifies all 28 runtime file hashes against the review receipt before loading only the eight named modules. It requires exactly 63 executed tests, zero failures/errors/skips/expected failures, and zero guarded DNS/connection/subprocess/browser attempts. A caught network-guard exception still fails CI. Each matrix job uploads a JSON receipt with the actual checked-out commit, source manifest, Python version, module counts, timestamps and attempt counters. Protected tracked files are checked again after tests.

Actions are pinned to verified official release commits:
- checkout v7.0.1: 3d3c42e5aac5ba805825da76410c181273ba90b1
- setup-python v7.0.0: 5fda3b95a4ea91299a34e894583c3862153e4b97
- upload-artifact v7.0.2: cf430e030ddbb5b0abf93d22962f4752f3646cd9

Local command from the main-based worktree:

`PYTHONPATH=runtime python3 -m tools.runtime_synthetic`

Local verification before publication: 63/63 pass on Python 3.10.4 and 3.14.6, no skips or guarded external attempts. A negative runner control supplied 63 passing synthetic stubs with one caught DNS-guard attempt; runner exit 1 and passed=false prove that ordinary test success cannot override the isolation gate. YAML event/matrix validation passes. Exact-head GitHub job conclusions and uploaded receipt readback are separate publication evidence, recorded in the PR checks and Obsidian.

## Preservation and remaining gates

No pilot, evaluation, data/register, phase-1 context/pipeline or frozen schema paths are changed against main. The frozen evaluation tree is dbb2c7ad8d0ddb4f9d0ae77b9d52714d532deb55. Original pilot HTML/ZIP hashes, all 36 protected original files and original evaluation/historical-package metadata fingerprints remain unchanged; pilot/data/input-policy.json in that preserved original candidate retains runtime_enabled=false. The main-based tree has no pilot source or activation wiring.

CI is a synthetic engineering check. It does not execute frozen evaluation or old corpus/provider tests, grant actual source permissions, qualify live providers/browser networking, migrate all historical callers, approve clinical/legal content, or authorize pilot integration/deployment. The reviewed runtime still has 2526 unsuppressed basedpyright warnings and zero errors (exit 1). Adding a passing CI check does not make it a required branch-protection rule or clear human/domain acceptance. No merge or activation is authorized by this preparation.
