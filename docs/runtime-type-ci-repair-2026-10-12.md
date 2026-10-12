# Runtime type CI dependency repair (2026-10-12)

PR #68's first GitHub run, [38191205243](https://github.com/Reedtrullz/NAVigator/actions/runs/38191205243), tested exact head `2ef52a1a1c791bc7a1980aafc17123c0b5b999a7` against main `08d51d4feadfe03695ca2af87370949b44cafa6b`. Both Python matrix jobs completed the guarded synthetic suite and both protected-diff checks successfully, then failed the type-check step with exactly one error and zero warnings:

```text
runtime/type_support.py:7:10 - error: Import "typing_extensions" could not be resolved from source (reportMissingModuleSource)
```

The workflow installed basedpyright but omitted the existing type-check dependency used by `runtime/type_support.py`. Local verification had `typing_extensions 4.16.0` installed; its package metadata requires Python >=3.9, compatible with the 3.10/3.14 matrix. The dependency is imported under `TYPE_CHECKING`; the synthetic runtime does not require it at execution time.

The repair adds only `typing_extensions==4.16.0` beside `basedpyright==1.39.3` in the CI install command. No warning suppression, type-severity change, runtime source change, test change, provider activation or checker-scope reduction. Existing action SHA pins, exact-head/base checks, 68-test guard and protected paths remain intact.

The 42-file runtime source manifest remains `1db6cfd0bf67e4753a6ca14a09c6ed39a8d73d071121d451898b7c4fb0b34419`. Prior source/review/test receipts retain their original immutable snapshot descriptions. The independent review covers identical runtime bytes; this workflow dependency delta is a native repair requiring a fresh GitHub run, not a new independent reviewer approval.

The failed run and its uploaded synthetic receipts are retained as failure evidence. A successful run on the repaired PR head is required before reporting CI green. Pilot packages, frozen evaluation, actual phase-1 context/schema implementations and the primary checkout's existing WIP remain preserved; runtime remains disconnected.

Only this document and the workflow install line change in the repair commit.
