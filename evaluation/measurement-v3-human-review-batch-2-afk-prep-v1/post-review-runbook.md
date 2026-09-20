# Post-Review Runbook - Human Review Batch 2

Mechanical runbook for the owner review session. No semantic decisions are made
by any tool in this lineage. All judgments come from OWNER-01 via the cockpit.

## Preconditions

- Frozen packets: `evaluation/measurement-v3-human-review-batch-2-repaired/human-review-packets.jsonl` (74 packets, SHA-pinned).
- Draft file location: `owner-reviews-draft.jsonl` in THIS prep lineage (not the batch directory).
- Frozen review lane: `review_lane_semantic_v2_15` (validate_review + derive_final only).

## Step 1 - Owner review session

```bash
cd evaluation/measurement-v3-human-review-batch-2-afk-prep-v1
python3 cockpit_server.py 8765
# open http://127.0.0.1:8765
```

Complete all 74 packets in the frozen order (10 critical, then 64 forbidden).
Draft rows are saved atomically per packet and can be resumed at any time.
Mechanical span checks run in the cockpit before each save; unmappable spans are rejected.

## Step 2 - Validate drafts

```bash
python3 run_review_batch_2.py validate
```

Requires 74/74 valid rows before ingest. Missing/invalid rows are reported by packet_id.

## Step 3 - Ingest and derive

```bash
python3 run_review_batch_2.py ingest
```

Runs the frozen lane validation per row, then derives final verdicts mechanically
via `LANE.derive_final(dimension, judgment)`. No semantic override occurs.
`--allow-partial` is a bounded checkpoint only and NEVER freezes.

## Step 4 - Freeze

```bash
python3 run_review_batch_2.py freeze
```

Refuses unless all 74 reviews are present and valid. Produces:
- completed measurement results (526 deterministic + 74 owner-reviewed = 600 criteria)
- freeze manifest with packet SHA pins
- `hashes.txt`

## Step 5 - Verify hashes

```bash
shasum -a 256 -c hashes.txt
```

All pins must verify. Any mismatch is terminal: stop and report, never re-derive.

## Step 6 - Hard stop

Freeze is terminal for this lineage. Combined V3 aggregation belongs to a SEPARATE
owner-authorized task (`evaluation/measurement-v3-combined-freeze/combined_measurement_v3.py`
is the existing engine; `run_integration_v3.py` consumes it). Do not run it from here.

## Downstream sequence (separate owner-authorized task only)

For traceability, the full post-review contract from the owner authorization maps
to this runbook as follows:

1. validate - Step 2 above
2. audit - lane re-validation inside Step 3 ingest (frozen lane validate_review)
3. ingest - Step 3
4. derive - Step 3 (frozen lane derive_final)
5. combine 526 + 74 - separate authorized task (combined_measurement_v3.py)
6. verify 600 authoritative criteria - separate authorized task
7. aggregate - separate authorized task
8. freeze - Step 4
9. verify hashes - Step 5
10. terminal report - separate authorized task

Steps 5-7 and 10 MUST NOT run inside this prep lineage.

## Invariants

- Packets are immutable; packet body SHAs must match the batch-2 repaired frozen set.
- Superseded criterion packets PKT-ESC-ROUT-061/070/073 must never bind derived rows to old packet SHAs.
- `REAL_OWNER_REVIEWS_WRITTEN` remains 0 until the owner session itself writes them.
- No model call, no semantic suggestion, no gold or verdict leakage into the cockpit or drafts.
