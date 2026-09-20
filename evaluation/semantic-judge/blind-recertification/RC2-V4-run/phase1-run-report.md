# RC2-V4 Phase 1 run report

Task: NAV-EXPLORE-RC2-BLIND-V4-PHASE1. Fresh keyless session (new
thread; no blind-key conversation history carried in). No subagents.

## Pre-run verification

### RC2 integrity

- candidate = NAV-EXPLORE-EVALUATOR-RC2, status =
  FROZEN_DEVELOPMENT_CANDIDATE (RC2-manifest.json)
- RC2 manifest SHA-256:
  1215f0d2978d80cf383f921155933f19f85f259279d04136ad00fd9f81d559cc
- hashes.txt SHA-256 (matches firewall manifest):
  034e2f91c8db78a379d3f4b4054a01907345fdc95a8a84b1b313daa556321294
- component count: 10 (9 runtime + fusion-calibration.json);
  matched: 10/10 via shasum -a 256 -c, pre-run

### V4 integrity (public surface only; sealed payloads never read)

- set_version = NAV-EXPLORE-RC2-BLIND-V4
- firewall_status = SEALED_AND_FIREWALLED (public manifest; the
  requested "READY" string does not exist in any public manifest; the
  Phase-1 firewall manifest hashes, counts, and statuses below are the
  authoritative checks actually run)
- CORE = 160, reserve = 122 (pool 282)
- blind-cases.json SHA-256:
  ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d
- answer-key.sealed SHA-256:
  65f72b170cb200b804cf817c32aaf42e9166a20ed002777a5d9f5e71b99fd80d
- construction-audit.sealed SHA-256:
  5be70e666493d3a6e000b89418a8064099f03ee797ece3365840acb7a7646ff3
- rc2_executed_on_blind_set = false; seal decrypt re-verification
  dated 2026-09-04 recorded in manifest; hashes above match the
  firewall manifest exactly

### Firewall allowlist check

Files used in Phase 1: RC2 manifest + hashes.txt + README (frozen
RC2 runtime category), all ten frozen components, blind-cases.json,
blind-cases.schema.json, blind-manifest.json, phase1-firewall-manifest
.json, and the prediction harness (RC1-run/run_blind_phase1.py read as
the established harness reference; RC2-V4 driver written fresh in the
run dir). Sealed files were touched ONLY via shasum -a 256. No
construction-v4/, V3 construction/pilot, or label-bearing file was
opened. The firewall manifest lists "prediction harness" as a required
category without naming a file; this was treated as a manifest gap and
resolved as described; no other access was widened.

### Snapshot

validation/pre-run-hashes.json: SHA-256 over 19 files (RC2 manifest,
hashes.txt, README, 10 frozen components, blind-cases, schema,
blind manifest, both sealed files, firewall manifest) taken before
evaluator execution. Status ACTIVE.

## Run

- driver: run_blind_phase1_v4.py (frozen composition, documented in
  its docstring; no component modified; py_compile clean; import
  smoke test passed before run)
- reviewer configuration (frozen, logged): openai/gpt-5.6-luna,
  temperature 0, max_tokens 300, local OpenCodex proxy
  127.0.0.1:10100/v1/chat/completions, key read at runtime from
  /Users/reidar/.opencodex/config.json by frozen reviewer.py
- retries: 0 (frozen policy has no retry; none applied)
- console log: validation/run-console.log

## Post-run QA

- exactly 160 CORE IDs; missing 0; extra 0; duplicates 0; input order
  preserved
- per-case required fields present on all 160 rows (case_id,
  semantic_verdict, proof_safe_verdict, product_action, auto_or_review,
  proof_object, proof_valid, reviewer_used, reviewer_output,
  runtime_status)
- raw intermediates retained: engine atom_results on all rows (202
  atoms), gate reasons, reviewer outputs (127), fusion routes; raw
  intermediates are embedded in RC2-V4-predictions.json, so no separate
  raw file exists and the prediction SHA is also the raw SHA
- QA read schema/completeness/ID matching only; no semantic review of
  predictions; no comparison with aggregate class distributions

## Integrity after run

- RC2: shasum -c ALL OK (10/10)
- V4: all five public/surface hashes unchanged (blind-cases, both
  sealed files, blind manifest, RC2 manifest + hashes.txt)
- snapshot recheck: 19/19 files byte-identical (POST_RUN_ALL_MATCH:
  True)
- PREDICTION_HASH_STABLE = TRUE (rehash identical to freeze manifest)

## Freeze

See prediction-freeze.json. RC2-V4-predictions.json and
prediction-freeze.json set read-only (444).
