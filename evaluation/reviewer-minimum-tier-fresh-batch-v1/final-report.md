# FINAL REPORT - NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1

Stage: PREPARATION ONLY. Terminal status: PREPARATION_COMPLETE_AWAITING_HUMAN_GOLD_AND_RUN_AUTHORIZATION.

MODEL_CALLS_THIS_STAGE = 0. ASTRA_CALLS = 0 (absolute, per TASK-SPEC-V1.1 R4). GPT-5.5 used = NO. Subagents used = 0.

## 1. Integrity chain

| Artifact | SHA-256 |
|---|---|
| Original draft (fresh-batch-spec-draft.md) | 96cbf4fe980941405c450f449d8984dccaaaa9b59e0a7cb8215e941d5d28cd2f |
| TASK-SPEC-V1.1.md (owner revisions R1-R12) | 3ecfc12d64b3fd8dfd3b20b6ff53163eb75cacaba60eb47b2c3ea33282de5fa2 |
| source-manifest.json | 436ffc70b1565d554cc3d3efea56ac4e51621b516ac9f6abd4fa5479d44d54b5 |
| construction-builder.py | 6a2dc3633d4c120626eca26904057d12aff244d1c06f185919b8465172a681f4 |
| dataset-frozen.jsonl | f3e11e83f03b7ddd9203ffc82be8844dfa32238c39205e08d736c344b6e807a2 |
| qualification-contract.json (semantic_instructions source) | a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f |
| minimum-sufficient-reviewer-burned.jsonl (predecessor label set) | 4cd87708c79c44ce8a424b1feee491727096dbfd4edc55e0985a3a26fc64902e |

All SHAs re-verified this session before dependent work.

## 2. Dataset

- 350 rows / 100 scenario groups (dataset-frozen.jsonl, deterministic builder output).
- Family targets exact: 50 ASM / 150 SCR / 30 ARD / 30 NGP / 20 IAC / 30 EXC / 20 CMP / 20 CTL.
- 150 safety rows across 30 safety groups.
- Dimensions: 200 forbidden_claim / 150 critical_condition.
- No gold anywhere in the dataset. No family/source/model metadata in workbook row sections (blindness).

## 3. Overlap / lineage check

Result: PASS.

- canonical_hash / packet_sha256 exact hits: 0
- exact triple hits: 0
- normalized-text duplicates: 0
- masked-text duplicates: 0
- near-dup candidate pairs (sim >= 0.55, >= 2 shared decision terms): 14, all generic KB-domain phrase overlap (e.g. "bup", "fastlege"); none decision-equivalent (sim >= 0.85 AND >= 3 shared terms).
- decision-equivalent candidates: 0 => builder revision NOT required.

Sources compared: reference-corpus.jsonl (387 rows, text pool) + 25 historical fixture files under evaluation/dev-corpus-semantic-judge-v1*/.

Artifacts: overlap-lineage-check.py, overlap-lineage-summary.json, overlap-lineage-report.md.

## 4. Blind human adjudication package

- human-review-workbook.md (SHA 63d3727a71d65258ad47ad1f777522eb8c8ed64cf3d499922a6dc67f15245be5): 350 sections, frozen contract definitions verbatim, per-row Case / Criterion / Candidate text + empty verdict / evidence_spans / rationale_unclear fields. Single-human policy (Reidar or designated human; AI never fills verdicts).
- scenario-group-manifest.json (SHA 6e6db9aa300a3713b1cff96aed5cedec75a8baaef91377215b1bf421446059be): 100 groups with family, safety flag, row_ids.

## 5. Call / cost plan (offline)

call-cost-plan.json (planning only; no calls made):

- Ladder: T1 (mimo-v2.5-pro -> laguna-s-2.1 -> ling-3.0-flash-sante) -> T2 (deepseek-v4-flash -> nex-n2.5-pro) -> T3 (luna-high -> luna-max). Stop at first tier with >= 1 SUFFICIENT cell.
- Planning cap: 2450 primary calls (350 x 7 worst case).
- Retry: max 1 technical (30s); no substantive retries; finish_reason length = TRANSPORT_CAPACITY_FAILURE.
- Lane C consensus: costed, NOT called; model identity to be authorized at run time; luna/T3 overlap flagged.
- Pricing: all T1/T2 routes free/local-proxy; Luna paid, price unknown => cost unknown, flagged.
- T4/Astra: 0 calls, forbidden.

## 6. Terminal state

TASK-LOCK.json: status PREPARATION_COMPLETE_AWAITING_HUMAN_GOLD_AND_RUN_AUTHORIZATION, stage COMPLETE (SHA recorded in lock-verification block below after closure).

Next stage requires explicit owner authorization: (1) human gold labeling from the frozen workbook, then (2) frozen run authorization for tier ladder execution. HARD STOP at this terminal status.

