# Lane H Diagnostic Ingestion V2 — Implementation Report

Task: NAV-EXPLORE-LANE-H-DIAGNOSTIC-INGESTION-V2

## Scope

Exactly the two owner-authorized items, in the diagnostic tool only:

1. Correct per-row input hashing (MODEL_FACING_TEXT_V2).
2. Strict, optional outer-JSON-fence ingestion (fence-only, default OFF for live calls).

No reference/semantic/contract changes. No span normalization, no JSON
reconstruction, no repair of model content. Original run_diagnostic.py,
results-*.jsonl, dataset, contract and diagnostic-report.md are byte-unchanged
(SHAs re-verified at the end of this task).

## Root cause (hashing)

run_diagnostic.py line ~130:

semantic_input_hash = sha({"system": sysp, "intro": intro, "labels": labels, "dataset_sha": dataset_sha})

The field hashed only contract parts + the whole-dataset SHA, so it was one
constant value across all 150 rows x 2 routes (300 records). It could not
identify a row's model-facing input. Resume logic (V1) keyed on row_id +
status=="OK", not on the hash; the unique request_fingerprint already bound
system_sha+user_sha+route config, but was not used for resume.

## Changes

- ingestion_v2.py (new):
  - strip_outer_fence(): matches at most ONE outer markdown fence anchored at
    both ends; interior fences and non-wrapper text fail closed unchanged.
  - parse_like_original(): optional strip, then json.loads exactly like V1.
    No other transformation.
  - model_input_hash_v2(): sha256 over JSON {"format": "MODEL_FACING_TEXT_V2",
    "system": <exact system prompt>, "user": <exact built user prompt>}.
    Changing case context, criterion or SUT output changes the hash; changing
    row_id alone does not.
  - replay_results(): read-only replay of stored raw responses with the
    unchanged validate() imported from run_diagnostic.py.
- run_diagnostic_v2.py (new runner; V1 runner untouched):
  - modes: run (live, no calls made in this task), verify, replay.
  - --fence-ingest flag (default OFF; same as V1 behavior for live calls).
  - per-row semantic_input_hash_v2 + semantic_input_hash_format written per
    record; V1 field name semantic_input_hash is not reused for the new format.
  - resume keys on request fingerprint (which binds system_sha+user_sha+route
    config) + status OK, so identical model-facing text is recognized as the
    same input regardless of row_id.
  - results go to results-v2-<route>.jsonl; V1 files never touched.

## Hash format: MODEL_FACING_TEXT_V2

Hash input: sha256 over canonical JSON (sort_keys, ensure_ascii=False) of:

{"format": "MODEL_FACING_TEXT_V2", "system": <system_prompt>, "user": <exact user prompt>}

Properties verified by tests:

- different rows (different case/criterion/SUT text) -> different hashes;
- same row -> same hash across calls (determinism);
- row_id is NOT part of the hash: identical model-facing text under a
  different row_id hashes identically (by design, per owner requirement).

Historical V1 semantic_input_hash values remain unchanged in historical
records. Recomputed hashes are stored only under new field names
(semantic_input_hash_v2 + format tag) or in this report, and are NOT
represented as evidence of what was sent in past requests.

## Fence rule

Regex requires the wrapper to start at the first non-whitespace byte and end
at the last non-whitespace byte, opening fence with optional language tag,
closing fence at end. At most one wrapper is removed. Content containing its
own fences, prose-wrapped JSON, or any other decoration is NOT touched and
fails closed exactly as in V1. No typo/quotation/grammar fixes, no missing-JSON
completion, no object-fishing in prose.

## Regression replay (read-only, stored raw responses)

Engine: ingestion_v2.parse_like_original(fence_enabled=True) + unchanged
run_diagnostic.validate(). Per-row dispositions in replay-v2-results.json.

| Route | OK | INVALID_JSON | INVALID_MODEL_REVIEW | changed_vs_original_OK_rows |
|---|---|---|---|---|
| MIMO | 137/150 | 1 | 12 | 0 |
| DeepSeek | 150/150 | 0 | 0 | 0 |

This matches the preregistered targets (137/150, 150/150, 13 remaining
rejections, 0 OK rows flipped) exactly. The 13 remaining Mimo rejections are:
FB1-SCR-040 (span_not_verbatim after parse) + 11 span_not_verbatim
INVALID_MODEL_REVIEW + FB1-SCR-103 (malformed JSON; stray quote before
"rationale"; no truncation evidence). None were repaired, normalized or
reconstructed.

Note: fence-only replay count (137) is a hypothetical ingestion counter, not a
new official score; identical numbers to the earlier fence-only-replay.jsonl
analysis, now produced by the actual reusable engine.

## Tests (run in this task)

python3 run_diagnostic_v2.py verify

PASS: per-row hashes differ across rows; deterministic across calls; strict
fence strip (canonical wrapper stripped, prose-wrapped JSON untouched).

## Non-claims

- No new inference calls; zero tokens spent.
- No new benchmark, no new gold, no runtime/routing change.
- json_mode difference (MIMO false / DeepSeek true) remains a configuration
  constraint of the comparison; models are NOT tested under identical format
  conditions.
- Fence-enabled live results would still be a NEW measurement lineage (would
  require a separate owner-authorized run); this task only repairs the tool.
- Historical records keep original values; recomputed hashes never presented
  as evidence of past request payloads.

## Terminal

Ingestion repair complete and regression-matched. Status:
INGESTION_V2_IMPLEMENTED_REGRESSION_MATCHED
