# Report Templates - AFK Prep V1

All semantic result fields below are PLACEHOLDERS. They are filled only by the
future owner review session and downstream authorized tasks. This prep lineage
must not prefill, predict, or suggest any semantic value.

## T1 - Review Progress (filled during owner session)

```json
{
  "task": "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1",
  "packets_total": 74,
  "packets_drafted": null,
  "packets_remaining": null,
  "critical_block": {"total": 10, "done": null},
  "forbidden_block": {"total": 64, "done": null},
  "REAL_OWNER_REVIEWS_WRITTEN": null,
  "AI_ASSISTANCE_FIELDS_IN_COCKPIT": 0
}
```

## T2 - Validation Report (after Step 2 of runbook)

```json
{
  "rows_total": null,
  "valid": null,
  "invalid": null,
  "invalid_details": [],
  "missing_packet_ids": [],
  "span_reencode_failures": null,
  "lane": "review_lane_semantic_v2_15"
}
```

## T3 - Derived Verdict Summary (after Step 3 of runbook)

```json
{
  "critical_rows": null,
  "forbidden_rows": null,
  "critical_final_verdicts": {},
  "forbidden_final_verdicts": {},
  "deterministic_override_count": 0,
  "model_semantic_calls": 0
}
```

## T4 - Final Combined Metrics (separate authorized task, NOT this lineage)

```json
{
  "criteria_total": 600,
  "deterministic_criteria": 526,
  "owner_reviewed_criteria": 74,
  "critical_dimension": null,
  "forbidden_dimension": null,
  "route_dimension": null,
  "uncertainty_dimension": null,
  "STATUS": null
}
```

## T5 - Product Findings (reserved, out of scope here)

```json
{
  "finding_count": null,
  "findings": [],
  "note": "Filled only after combined V3 aggregation in a separate authorized task."
}
```

## T6 - Terminal Report (end of full batch-2 review task)

```json
{
  "TASK_ID": null,
  "packets_frozen": 74,
  "reviews_completed": 74,
  "reviews_valid": 74,
  "hash_verification": "PASS/FAIL",
  "AUTHORITATIVE_PACKET_MUTATIONS": 0,
  "CORPUS_MUTATIONS": 0,
  "AI_AS_HUMAN_REVIEWER": false,
  "deterministic_criteria": 526,
  "owner_reviewed_criteria": 74,
  "total_criteria": 600,
  "combined_aggregation_task": "separate owner-authorized lineage",
  "STATUS": null
}
```
