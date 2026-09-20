# DEV CORPUS GOLD CRITERION REPAIR V1 (complete)

Lineage: NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1

Terminal status: DEV_CORPUS_GOLD_CRITERION_REPAIR_V1_COMPLETE_REVIEW_BATCH_READY

## Purpose

The frozen human-review criterion audit (HUMAN_REVIEW_CRITERION_REPAIR_REQUIRED) found 3 forbidden_claim criteria that are semantically underspecified noun phrases ("barnevernet automatisk" / "barnevern automatisk"). This lineage proposes full-proposition repair candidates for owner selection. Phase A does not rewrite any frozen artifact.

## Scope

| Packet | Corpus case | Frozen criterion | Status |
|---|---|---|---|
| PKT-ESC-ROUT-061 | ROUT-061 | barnevernet automatisk | candidate proposed |
| PKT-ESC-ROUT-070 | ROUT-070 | barnevernet automatisk | candidate proposed |
| PKT-ESC-ROUT-073 | ROUT-073 | barnevern automatisk | candidate proposed |

## Files

- TASK-LOCK.json - task authorization and invariants
- repair-input-manifest.json - 17 SHA-pinned inputs + 74 packet hashes
- ROUT-061-owner-decision.md - case intent and candidates A/B
- ROUT-070-owner-decision.md - 4 audit interpretations and candidates A-D
- ROUT-073-owner-decision.md - case intent and candidates A-C
- criterion-repair-candidates.json - 9 candidates with classification and FP/FN boundaries
- cross-case-consistency.json - cross-case structure and sibling comparison
- repair-proposal-report.md - terminal proposal report
- README.md - this file

## Phase B (owner-authorized, complete)

Owner approved one candidate per case (R061-A, R070-A, R073-A). Phase B
materialized and froze two new lineages without touching any historical
artifact:

- ../dev-corpus-v1-1-repair/ - repaired corpus (3 forbidden_claims fields); routing sha 55f634d9cee8726343b75a6d61eb0a375532a3ac2948df3b5383e70d1983e317
- ../measurement-v3-human-review-batch-2-repaired/ - 74 packets (71 byte-identical, 3 criterion-repaired), frozen review order, workbook, form, leakage audit, reviewability check, batch manifest

Phase B artifacts: approved-owner-decisions.json, gold-repair-diff.json,
gold-repair-provenance.json, phase-b-integrity.json (all gates pass),
hashes.txt (15/15 verified), phase-b-final-report.md, and the deterministic
stdlib-only builders build_phase_b.py + build_phase_b_lib.py + build_batch2.py.

## Status

Phase A + Phase B complete. Next owner decision: Human Review Batch 2 over
the frozen packet SHAs. No reviews, ingest, scoring, or SUT reruns were
performed in this task.
