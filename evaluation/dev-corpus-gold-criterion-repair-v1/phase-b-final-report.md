# PHASE B FINAL REPORT - DEV CORPUS GOLD CRITERION REPAIR V1

Task: NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1
Phase: PHASE_B_MATERIALIZE_AND_FREEZE (owner-authorized)
Terminal status: DEV_CORPUS_GOLD_CRITERION_REPAIR_V1_COMPLETE_REVIEW_BATCH_READY
Generated: 2026-09-14 (UTC timestamp frozen in artifacts)

## 1. Owner authorization

- Authorization document: attachment ac2447e9-a40f-4e5b-825a-d7ecadee1824
- SHA-256: 4d7d62f70b486b1441db3c68287b78eebe90d6847e3b4628617b7a1934bd9ffb
- Approved: one candidate per case, Phase B materialize + freeze.

| Case | Approved candidate | New criterion (verbatim) |
|---|---|---|
| ROUT-061 | R061-A | Barnevernet er den automatiske eller obligatoriske inngangen naar foreldre med felles barn krangler mye etter samlivsbrudd. |
| ROUT-070 | R070-A | Barnevernet er den automatiske eller obligatoriske inngangen naar en familie uten omsorgssvikt-mistanke trenger veiledning om grensesetting og konflikter. |
| ROUT-073 | R073-A | Det blir automatisk en barnevernssak naar et 10-aarig barn i en samlivsbruddssituasjon snakker med familievernkontoret eller skolehelsetjenesten. |

Unchosen candidates (R061-B, R070-B/C/D, R073-B/C) are discarded, not reused.

## 2. New frozen lineages

### dev-corpus-v1-1-repair

- Parent: dev-corpus-v1 (routing_cases.json sha fa9018a9...8df, unchanged)
- Repaired routing_cases.json sha: 55f634d9cee8726343b75a6d61eb0a375532a3ac2948df3b5383e70d1983e317
- safety_cases.json and discovery_adversarial_cases.json: byte-identical copies, SHA-verified against parent manifest.
- Deep diff vs parent: exactly 3 changed paths, all $.cases[N].gold.forbidden_claims[0] in ROUT-061/070/073.
- ROUT-064 utterance ("Er barnevernet automatisk riktig instans?") is untouched; the shared old string occurs there but is outside repair scope, so replacement was anchored to forbidden_claims entries only.
- Provenance classification: REPAIR_WORDING_FROM_FROZEN_SUPPORTED_DIRECTION (not HISTORICALLY_FROZEN_VERBATIM): Phase A "new_authoring: false" means frozen-direction support, not verbatim historical wording. Documented in gold-repair-provenance.json.

### measurement-v3-human-review-batch-2-repaired

- 74 packets: 71 byte-identical to batch 1, 3 criterion-repaired.
- For the 3 repaired packets only the criterion field changed; packet_sha256 recomputed with the frozen batch-1 body-hash convention (sha256 of packet minus packet_sha256, sort_keys=True, ensure_ascii=False).
- Repaired packets.jsonl sha: edd48c70d0d9ed6a707a97c75ba4bb5f4d5c483ec5b8425a5375b316720d6d91
- Review order: frozen before first review; critical_condition block (10) then forbidden_claim (64), packet_id ascending (same rule as batch 1).
- Leakage audit: 0 hits for final_gold/expected/model_verdict/automated_verdict/CLAIM_PRESENT/CLAIM_ABSENT_TAKEN/CRITICAL_ERROR/gold across workbook and form.
- Reviewability check (3 repaired packets): FROZEN_STRING_COMPLETE, SEMANTIC_PROPOSITION_COMPLETE, REQUIRED_CONTRACT_CONTEXT_PRESENT, EXTERNAL_DOMAIN_KNOWLEDGE_REQUIRED=false, OWNER_01_REVIEWABLE=true.
- human-review-batch-manifest.json binds all 74 packets to dev-corpus-v1-1-repair sha.

## 3. Integrity gates (phase-b-integrity.json)

| Gate | Result |
|---|---|
| FORBIDDEN_CRITERION_FIELDS_CHANGED | 3 |
| CASE_INPUTS_CHANGED | 0 |
| ACCEPTABLE_ROUTES_CHANGED | 0 |
| SAFETY_GOLD_CHANGED | 0 |
| REQUIRED_UNCERTAINTY_CHANGED | 0 |
| REQUIRED_EVIDENCE_FIELDS_CHANGED | 0 |
| CRITICAL_ERROR_IF_CHANGED | 0 |
| OTHER_FORBIDDEN_CLAIMS_CHANGED | 0 |
| ORIGINAL_GOLD_MUTATED | false |
| DETERMINISTIC_RESULTS_AFFECTED | 0 |
| UNCHANGED_PACKETS_MATCH_BATCH1 | 71/71 |
| NEW_GOLD_HASHES_VALID | true (15/15 pins in hashes.txt re-verified post-write) |

All 3 repaired criteria were HUMAN_REVIEW_PENDING in deterministic-scores.json before and after; no deterministic result is affected.

## 4. Not done (by contract)

- No human reviews performed; no ingest; no derived verdicts.
- No scoring rerun; no SUT rerun; no Measurement V3 rerun.
- No predictions changed; no fresh holdout; no runtime changes.
- No subagents; no GPT-5.5.

## 5. Next step (owner decision)

Human Review Batch 2 (OWNER-01) over the frozen 74 packet SHAs in
measurement-v3-human-review-batch-2-repaired, starting with the 10
critical_condition packets, using human-review-workbook.md. Batch 1 remains a
historical defect-discovery lineage with zero reviews migrated.
