# FINAL REPORT - HUMAN REVIEW CRITERION SEMANTIC COMPLETENESS AUDIT

Task: NAV-EXPLORE-HUMAN-REVIEW-CRITERION-SEMANTIC-COMPLETENESS-AUDIT (authorized continuation of NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1, same ACTIVE lineage).

## Scope compliance
- OWNER_01_REVIEWS_COMPLETED = 0; HUMAN_REVIEW_INGEST = 0; BASELINE_RESCORING = 0.
- Packet mutation: 0. Prediction rerun: 0. Gold rewrite: 0. Scoring rerun: 0.
- Packet hashes re-verified this task: 74/74 OK, 0 mismatches.
- Recovery: authoritative frozen artifacts only (criterion-recovery-sources.json, 11 sources SHA-pinned). No web research, no NAV-domain knowledge, no inferred intent treated as truth.

## Key distinction applied (task section 3)
FROZEN_CRITERION_STRING_COMPLETE (criterion field shown verbatim) is NOT the same as SEMANTIC_PROPOSITION_COMPLETE (an intelligent reviewer can unambiguously tell which proposition is tested). The prior v2 usability repair fixed presentation (CONTEXT_OVERLOAD) but could not manufacture missing criterion semantics.

## Classification results (74/74 audited)
| Classification | N | Meaning |
|---|---|---|
| PROPOSITION_COMPLETE | 66 | Self-bearing semantic condition, or fragment whose unique referent is supplied by the packet utterance and corroborated by frozen critical_error_if / required_evidence_fields shown on the reviewer surface. |
| SHORTHAND_BUT_AUTHORITATIVELY_EXPANDABLE | 5 | The five definitions-merged / levels-merged criteria; operational definitions exist in frozen required_evidence_fields and ARE displayed in workbook v2 block B. |
| SEMANTICALLY_UNDERSPECIFIED | 3 | Noun-phrase fragments with no predicate and no authoritative expansion anywhere in frozen artifacts. |

External domain knowledge required: 0 packets. (One owner decision rule: criterion composition, not NAV expertise.)

## SEMANTICALLY_UNDERSPECIFIED defects (honest N, not forced to 0)

1. PKT-ESC-ROUT-061 - criterion `barnevernet automatisk` (corpus ROUT-061)
2. PKT-ESC-ROUT-070 - criterion `barnevernet automatisk` (corpus ROUT-070; see pkt-esc-rout-070-readjudication.md)
3. PKT-ESC-ROUT-073 - criterion `barnevern automatisk` (corpus ROUT-073)

Common defect signature:
- Criterion is subject+adverb with no verb; the forbidden proposition is not stated.
- gold.critical_error_if = null for all three; required_evidence_fields = null.
- The utterances do not supply a unique predicate reading.
- Plausible interpretations diverge (assert-as-entry vs auto-referral vs any-mention vs escalation-without-assessment).
- No frozen artifact (gold-model, judge_core_v2_13, review lane v2-15, expected-routing S-keys, mutation records) defines these criteria boundaries. Expected-routing S16/S25/S43 and MUT020/021 use the phrase as an error-class label in other scenarios; that is usage context, not provenance for these cases.

Prior SELF_CONTAINED_REVIEWABLE status of ROUT-070 was wrong because it conflated frozen_string_complete with semantic_proposition_complete and asserted a reading ("must not assert barnevernet is the automatic entry point") that exists in no frozen artifact (task section 6 violation if kept).

## Borderline calls, decided conservatively but composable (documented per packet)
- ROUT-068 `fortielse uten grunnlag`: full verbal predicate in the string; utterance supplies the unique object (opplysningsplikt); critical_error_if corroborates. PROPOSITION_COMPLETE.
- ROUT-028, ROUT-030, ROUT-060, ROUT-080, ROUT-090, ROUT-093, ROUT-074, DIS-116/117/118, ROUT-051, ROUT-024: predicate fragments where the utterance supplies exactly one referent reading and frozen critical_error_if corroborates; classified PROPOSITION_COMPLETE with per-packet notes in the audit JSON. A stricter gate would flag some of these; the per-packet basis is recorded so the repair task can re-open any of them.

## Reviewability Gate V3 (task section 8)
- Rule: semantic_proposition_complete AND external_domain_knowledge_required=false AND required_contract_context_present=true.
- Result: 71/74 OWNER_01_REVIEWABLE (10/10 critical_condition, 61/64 forbidden_claim).
- Not reviewable: ROUT-061, ROUT-070, ROUT-073 packets.
- Hard target 74/74 was NOT forced (task section 9).

## ROUT-070 re-adjudication
See pkt-esc-rout-070-readjudication.md (6 questions answered).

## Terminal status

HUMAN_REVIEW_CRITERION_REPAIR_REQUIRED

Rationale: at least one packet criterion is semantically underspecified with no authoritative recovery path. Per task sections 11 and 16, this audit stops here; no gold repair in this task. Next task must be a separate DEV_CORPUS_GOLD_CRITERION_REPAIR lineage that freezes full propositions for ROUT-061/070/073 (and re-checks the borderline set), after which human review Batch 1 can resume on the frozen packets for the remaining 71 packets.

## Artifacts
- criterion-semantic-completeness-audit.json (74 records)
- criterion-quality-defects.json (3 defects, expansion_found=false)
- reviewability-v3-summary.json (gate v3 counts)
- pkt-esc-rout-070-readjudication.md
- criterion-recovery-sources.json (11 SHA-pinned frozen sources)
