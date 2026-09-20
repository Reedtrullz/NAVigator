# RC-01 Postmortem: Provenance/Input Failures

## What RC-01 was

RC-01 addressed input/provenance hard failures: cases where the SUT rejected or under-specified inputs so that deterministic derivation could not run (SOURCE_URL_REQUIRED_MISSING, PROVENANCE_CHAIN_BROKEN critical failures) and provenance chains broke before scoring.

## Wave-1 state

| Measure | Old baseline | Wave 1 |
|---|---|---|
| Provenance-mechanism critical FAIL rows | 3 | 3 |
| Rows | DIS-096, DIS-099, ROUT-053 | same |
| Markers | SOURCE_URL_REQUIRED_MISSING / PROVENANCE_CHAIN_BROKEN | identical |

## Residual mechanism

The same 3 rows fail with the same markers. In all 3 predictions the provenance array has entries but zero carry a source_url; the derivation requires a URL for these criteria. This is the same evidence-attachment/URL-resolution defect documented in PW1-R5/PW1-R6 (see residual-failure-families.json), not a new or recurring input-rejection problem.

## New schema/normalization issue?

None observed. No new SOURCE_URL or normalization markers appeared anywhere in Wave 1. The 8 net improved criteria and 0 regressed criteria include no new input-side defect.

## Classification

**CLOSED** as an input/schema mechanism. The 3 residual rows are an evidence-attachment defect (PW1-R5 sub-mechanism), owned by the evidence stage, and should be repaired there rather than by reopening RC-01. No further schema work is recommended without new evidence.
