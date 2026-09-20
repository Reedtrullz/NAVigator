# Measurement V3 Human Review Batch 2 - AFK Prep V1

Task: `NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1`

Terminal status: `HUMAN_REVIEW_BATCH_2_AFK_PREP_READY` (see `final-report.md`).

This lineage contains ONLY mechanical preparation for the owner's batch-2 review
session. It holds no semantic judgments. The authoritative packets live in
`../measurement-v3-human-review-batch-2-repaired/` (74 packets, SHA-pinned, immutable).

## Files

- `TASK-LOCK.json` - task lock and terminal status
- `authoritative-integrity.json` - integrity gate + 12 SHA pins (PASS, re-verified unchanged at close)
- `prep_integrity.py` - integrity gate script
- `prep_lib.py` - shared validation/derive helpers (frozen lane `review_lane_semantic_v2_15`)
- `prep_tests.py` - 18 negative cases + synthetic E2E (`negative-test-matrix.json`)
- `packet-mechanical-qc.json` - 9 presentation-layer QC findings
- `review-burden-report.json` - answer volume/burden stats
- `session-chunks.json` - frozen 9-chunk review plan (74 packets)
- `cockpit_server.py` + `review-cockpit.html` - localhost owner review cockpit
- `run_review_batch_2.py` - validate | ingest | freeze runner (freeze needs 74/74)
- `post-review-runbook.md` - exact post-review sequence
- `report-templates.md` - downstream report templates (semantic fields empty)
- `leakage_audit.py` + `leakage-audit.json` - leakage audit (all required zeros PASS)
- `frozen_output_anomalies.py` + `frozen-output-mechanical-anomalies.json` - read-only mechanical diagnostics on frozen Phase 3 outputs
- `final-report.md` - full close-out report

## Owner Session

```bash
cd "$(dirname "$0")" 2>/dev/null || true
python3 cockpit_server.py 8765
# then follow post-review-runbook.md
```

## Hard Invariants

- `REAL_OWNER_REVIEWS_WRITTEN = 0` at prep close (reviews happen in the owner session).
- No AI semantic reviews. No gold/verdict leakage. No packet or corpus mutations.
- `--allow-partial` never freezes. Freeze requires complete 74/74 valid OWNER-01 rows.
- Combined V3 aggregation is a separate owner-authorized task.

