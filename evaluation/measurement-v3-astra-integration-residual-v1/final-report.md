# FINAL REPORT - NAV-EXPLORE-MEASUREMENT-V3-ASTRA-INTEGRATION-AND-RESIDUAL-ADJUDICATION-V1

Date: 2026-09-16. Transport: local proxy (127.0.0.1:10100), bearer token from auth.json - never printed, persisted, or hashed.

## 1. Task ID
NAV-EXPLORE-MEASUREMENT-V3-ASTRA-INTEGRATION-AND-RESIDUAL-ADJUDICATION-V1

## 2-9. Inputs and models

| # | Item | Value |
|---|---|---|
| 2 | Starting burned baseline manifest | evaluation/measurement-v3-burned-baseline-v1, freeze manifest sha256 554e7d4a3c91f3cf928eb17e147046434c20ec71dbacd818616a99c9f23c03c9 (16/16 pins verified this task) |
| 3 | Repaired corpus manifest | evaluation/dev-corpus-v1-1-repair, manifest sha256 0df5c956e8a5d340b90df91d6c0ccb689dccc9a6700b252b7c602c3047cfca17 (3/3 owner-approved repair pins) |
| 4 | Batch 2 manifest | evaluation/measurement-v3-human-review-batch-2-repaired, manifest sha256 46cd54501f66000c5b26cf38eef0d326effba4b65f1d8d80b6b9bd37dd33641d; packet file sha256 edd48c70d0d9ed6a707a97c75ba4bb5f4d5c483ec5b8425a5375b316720d6d91; review order sha256 5cf86ece226afcd2aa43da18781a6798ae6659e91974aea722b413f10ddf9952; leakage audit sha256 c160c24b6debdf2b2acaa6b0794067e90f774bdf7721e161b9afea8a609a925b; 74/74 packet body hashes verified |
| 5 | Astra Batch 1 manifest | evaluation/measurement-v3-astra-review-batch-1; TASK-LOCK sha256 00c198690b19370ac71214f1cffb71f91c69d76881b9f1e64c4d3dc80cab4814 (status ASTRA_REVIEW_BATCH_COMPLETE_AWAITING_INTEGRATION); consensus-results.json sha256 25fae89224cd8c4397b2911d034c9f789b972c390b2e7f5ebfd8d6f3ea32fea6; hashes.txt verified 14/14 |
| 6 | Original Astra model | gpt-6-astra |
| 7 | Original Astra reasoning effort | low |
| 8 | Residual adjudicator model | gpt-6-astra |
| 9 | Residual adjudicator reasoning effort | LOW (verified across all 20 jsonl records; no other effort value present) |

## 10-18. Original Astra Batch 1 reconstruction

| # | Item | Value |
|---|---|---|
| 10 | Original packet count | 74 (10 critical_condition, 64 forbidden_claim) |
| 11 | Original A records | 74 records; 70 valid per frozen validator |
| 12 | Original B records | 74 records; 71 valid per frozen validator |
| 13 | Duplicate-process incident reconstructed | YES - documented in batch1-record-provenance.json; deterministic dedup retained first record per packet+pass; content unaffected |
| 14 | ROUT-053 transport retry verified | YES - ASTRA_B transport error retried once per frozen policy; retained record timestamp 2026-09-15T22:18:24Z |
| 15 | Original valid-pass counts | ASTRA_A 70/74, ASTRA_B 71/74 |
| 16 | Original exact consensus count | 64 (independently recomputed with frozen build_consensus.validate() logic and reproduced exactly; stored status fields used a stricter in-run span rule and are documented as non-authoritative in batch1-revalidation.json) |
| 17 | Original disagreement count | 3 (PKT-ESC-DIS-109 critical, PKT-ESC-DIS-118 forbidden, PKT-ESC-ROUT-041 forbidden) |
| 18 | Original invalid-pass count | 7 packets with at least one invalid pass: 1 non-verbatim span (ROUT-085 ASTRA_A), 6 enum violations (speaker_commitment null at NO_MATCH: DIS-109-F01, ROUT-021-F02, ROUT-025, ROUT-038-F02, ROUT-063, ROUT-066) |

## 19-29. Residual adjudication

| # | Item | Value |
|---|---|---|
| 19 | Residual packet count | 10 (2 critical_condition, 8 forbidden_claim) |
| 20 | Residual IDs | PKT-ESC-DIS-109, PKT-ESC-DIS-109-F01, PKT-ESC-DIS-118, PKT-ESC-ROUT-021-F02, PKT-ESC-ROUT-025, PKT-ESC-ROUT-038-F02, PKT-ESC-ROUT-041, PKT-ESC-ROUT-063, PKT-ESC-ROUT-066, PKT-ESC-ROUT-085 |
| 21 | ADJ-A calls | 10 (all status OK) |
| 22 | ADJ-B calls | 10 (all status OK) |
| 23 | Technical retries | 0 |
| 24 | ADJ-A valid | 8 (invalid: PKT-ESC-ROUT-025, PKT-ESC-ROUT-066 - enum speaker_commitment) |
| 25 | ADJ-B valid | 9 (invalid: PKT-ESC-ROUT-066) |
| 26 | Residual exact consensus count | 8 (ADJ-A/ADJ-B identical structured fields on all 8) |
| 27 | Residual disagreement count | 0 |
| 28 | Residual invalid count | 2 packets (ROUT-025: ADJ-A invalid; ROUT-066: ADJ-A and ADJ-B invalid) - preserved, not repaired |
| 29 | Human adjudication required count | 2 criteria: ROUT-025::forbidden:01, ROUT-066::forbidden:01 |

## 30-37. Authority and coverage

| # | Item | Value |
|---|---|---|
| 30 | Deterministic authority count | 526 (copied byte-untouched from frozen baseline) |
| 31 | LLM_REVIEWED count | 64 (original Astra consensus; all 74 original packet criteria map bijectively to corpus criteria; disagreements and invalid passes routed to adjudication) |
| 32 | LLM_ADJUDICATED count | 8 |
| 33 | Human-reviewed count | 0 |
| 34 | Pending count | 2 (PENDING_HUMAN_ADJUDICATION) |
| 35 | Total authoritative criteria | 598/600 = 99.67% |
| 36 | Criterion-level coverage | 598/600; by dimension: critical_condition 120/120, forbidden_claim 120/120, route_correctness 120/120 (108 scored, 12 NOT_APPLICABLE), required_uncertainty 120/120, evidence_completeness 120/120 |
| 37 | Case-level coverage | 118/120 = 98.33% fully authoritative (pending cases: ROUT-025, ROUT-066) |

## 38-40. Validation

| # | Item | Value |
|---|---|---|
| 38 | Evidence validation result | PASS - all LLM observations validated per frozen contract span rule; verbatim-span validation for provided spans; empty spans legal where contract permits; 0 span-rule violations in accepted observations |
| 39 | Gold leakage result | PASS - residual-input-leakage-audit.json with explicit artifact-class scope (model-visible packet fields only); occurrences of contract vocabulary inside frozen contract definitions are ALLOWED_FROZEN_CONTRACT_VOCABULARY; no gold values in any model-visible artifact |
| 40 | Prior-model leakage result | PASS - blind residual packets contained no A/B records, verdicts, or agreement metadata; adjudicator config records model_outputs_visible_to_adjudicator=false for both passes |

## 41-49. Integrity invariants

| # | Item | Value |
|---|---|---|
| 41 | SUT rerun | NO |
| 42 | Predictions changed | NO |
| 43 | Gold changed | NO |
| 44 | Packets changed | NO |
| 45 | Measurement contract changed | NO |
| 46 | Astra MEDIUM calls | 0 |
| 47 | Astra HIGH calls | 0 |
| 48 | Astra MAX calls | 0 |
| 49 | Burned-development classification preserved | YES - BURNED_DEV_BASELINE_ONLY |

## 50. Freeze manifest SHA

review-freeze-manifest.json sha256:
108fef5664311432f8b8a1232e734097653bd7730f7baf0c1f9faf0139e071e4

Frozen BEFORE derivation (spec section 21). Pins: accepted-original-consensus.json, residual-input-set.json,
adjudicator-config.json, adjudication-pass-a.jsonl, adjudication-pass-b.jsonl, adjudication-transport-log.json,
adjudication-validation.json, residual-consensus.json, authority-map.json - all re-verified OK after build.
Derivation core pinned: judge_selection-v2-13 judge_core_v2_13.py, unmodified, used mechanically for all 72 derived verdicts.

## Derived verdict summary (mechanical, mixed authority)

LLM_REVIEWED (64): critical_condition NOT_TRIGGERED 4, UNRESOLVED 3, TRIGGERED 1 (ROUT-050);
forbidden_claim ABSENT 54, PRESENT 2.
LLM_ADJUDICATED (8): critical_condition UNRESOLVED 2 (DIS-109, ROUT-085);
forbidden_claim ABSENT 5 (DIS-109-F01, ROUT-021-F02, ROUT-038-F02, ROUT-041, ROUT-063), PRESENT 1 (DIS-118).
Combined with the untouched 526 deterministic rows, full distributions are in combined-aggregate-metrics.json.
Dual-pass agreement is MODEL CONSISTENCY EVIDENCE only; results remain burned development baseline.

## 51. Final terminal status

MEASUREMENT_V3_BURNED_BASELINE_RESIDUAL_HUMAN_ADJUDICATION_REQUIRED

## 52. Exact next bounded task (do not start automatically)

Human adjudication of ROUT-025::forbidden:01 and ROUT-066::forbidden:01 using
human-residual-adjudication-packets.json (reviewer-permitted fields only, packet SHAs bound to
frozen Batch-2 packets), followed by mechanical derivation of those 2 criteria with the same
frozen judge_core_v2_13.derive_final and a combined-results v2 update. No SUT rerun, no
re-scoring of resolved criteria, no packet repair, no third automated pass, no fresh holdout.
