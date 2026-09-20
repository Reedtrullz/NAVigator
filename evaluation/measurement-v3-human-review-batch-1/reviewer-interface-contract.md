# REVIEWER INTERFACE CONTRACT - HUMAN REVIEW BATCH 1 (V2 PRESENTATION LAYER)

Task: NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1 | Reviewer: OWNER-01 | Policy: SINGLE_HUMAN_REVIEW

## 1. Role boundary

The human reviewer performs SEMANTIC COMPARISON AGAINST AN EXPLICIT CRITERION only.

- The reviewer is NOT performing domain-expert fact checking. NAV-, barneverns-, helse- og jusekspertise er ikke nodvendig og er ikke tillatt som beslutningsgrunnlag.
- A review is decidable exclusively from: (1) the self-contained review packet surface, (2) the frozen contract definitions shown verbatim in the workbook header (from judge_core_v2_13 via the frozen V2.15 lane), and (3) the SUT text under review.
- The paastandens sannhet er irrelevant: forbidden_claim maaler om svaret FREMSETTER paastanden; critical_condition maaler evidensgrunnlaget for den frosne betingelsen.
- AI/agents never make or influence semantic review content. The AI mechanically presents packets, validates schemas, maps evidence-span encoding, and derives final labels via frozen code.

## 2. Presentation layout (workbook v2)

Each packet section presents exactly:

- A. Case: the original user context.
- B. Criterion: the criterion verbatim from the packet, plus its frozen corpus source line (dev-corpus-v1 case file + field) and the allowed frozen criterion context (required_evidence_fields for critical_condition). This is the tested criterion itself, not gold verdict data.
- C. SUT answer: the actual user-facing answer field, primary review surface.
- D. Structured claims: compact mechanical extraction of the SUT structured claims + compact structured fields (safety, routes, uncertainty, failures, tracks). Mechanically extracted, no semantic filtering.
- E. Reviewer question: the exact question with the frozen label enums.
- F. Evidence span: empty fields for the reviewer.
- Technical appendix (collapsed): full raw packet SUT output, preserved byte-equivalent with the authoritative packet. Never needed for a normal review.

## 3. Evidence span rule

- Reviewer copies evidence spans exactly from block C or D (or the appendix).
- The lane validator (semantic-human-review-lane-v2_15) requires spans to be verbatim substrings of the RAW sut_output JSON string. Spans copied from the decoded display text may differ in JSON escaping.
- span_tool.py maps display spans to raw JSON encoding mechanically (prepare IN.jsonl OUT.jsonl produces ingest-ready human-reviews.jsonl). It exits non-zero on any unmappable span and never alters semantics.
- Ufullstendig span avvises teknisk (fail-closed).

## 4. Gold boundary

Allowed on reviewer surface: the criterion/proposition under test, frozen label definitions, review instructions, frozen criterion context (required_evidence_fields).

Forbidden and absent: expected verdicts, final gold labels, scorer answers, historical model verdicts, safety_priority/acceptable_routes/required_uncertainty gold fields from the corpus (only critical_error_if / forbidden_claims / required_evidence_fields are exposed, and only when they are the packet criterion itself).

Note on text hits: "Gold-kriteriet" appears only inside the verbatim frozen contract definitions block quoting judge_core_v2_13; "critical_error_if" appears only as frozen corpus field provenance for the criterion itself. Neither is verdict leakage.

## 5. Usability hard gate

Gate: for each of the 74 packets, "Kan en intelligent norsklesende reviewer uten NAV-/helse-/jusekspertise utfore denne semantic reviewen kun fra det som vises?"

Result: 74/74 = YES (reviewability-audit.json). The gate therefore holds and the batch may proceed to human review after this repair task closes.

## 6. Frozen invariants

- REVIEW_PACKETS_EDITED = false
- REVIEW_PACKET_HASHES_CHANGED = false (74/74 re-verified at v2 build time)
- HUMAN_REVIEWS_COMPLETED = 0 / OWNER_01_REVIEWS_COMPLETED = 0
- v1 workbook (human-review-workbook.md), v1 form (human-review-form.jsonl) and the authoritative packet JSONL are preserved unchanged.
- human-review-form-v2.jsonl contains 74 empty entries in frozen order; fill it and save as human-reviews.jsonl (or run span_tool.prepare) for ingestion.

## 7. Ingest path

span_tool.prepare output feeds run_review_batch_1.py ingest unchanged. No runtime, scoring, or packet changes were made for this repair.
