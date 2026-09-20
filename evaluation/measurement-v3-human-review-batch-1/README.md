# NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1

Owner-authorized human review of the 74 frozen baseline review packets
(64 forbidden_claim + 10 critical_condition) from
measurement-v3-burned-baseline-v1 (authoritative manifest SHA
554e7d4a3c91...c03c9).

## State

REVIEWER_INTERFACE_REPAIR_COMPLETE_AWAITING_HUMAN_REVIEWS - the reviewer
usability repair is complete (HUMAN_REVIEW_BATCH_1_INTERFACE_READY, 74/74
usability gate = YES); no human review has been recorded yet. AI does not review.

## Reviewer usability repair (v2 presentation layer)

The v1 workbook forced the reviewer to reconstruct criteria from large raw
SUT JSON dumps. A bounded repair built a new presentation layer over the SAME
frozen packets: packets remain byte-identical, v1 artifacts are preserved.

- human-review-workbook-v2.md - compact per-packet surface: A. Case,
  B. Criterion (verbatim + frozen corpus source), C. SUT answer, D. compact
  structured claims, E. reviewer question + frozen enums, F. evidence span;
  full raw JSON only in a collapsed technical appendix. Frozen contract
  definitions (judge_core_v2_13, verbatim) shown at the top.
- human-review-form-v2.jsonl - 74 empty entries, frozen order, same schema.
- reviewability-audit.json - per-packet reviewability + surface stats.
- reviewability-issues.json - v1 issue classification (64 x CONTEXT_OVERLOAD,
  10 x REQUIRES_MISSING_CONTRACT_CONTEXT) and v2 resolution.
- reviewer-interface-contract.md - role boundary, layout, span rule, gold
  boundary, usability gate.
- pkt-esc-rout-070-diagnosis.md - section 13 diagnostic example.
- span_tool.py - mechanical mapping of display evidence spans to raw JSON
  encoding (fail-closed); `python3 span_tool.py prepare <filled-form> human-reviews.jsonl`
  produces the ingest-ready file.

## Reviewer workflow (OWNER-01)

1. Open human-review-workbook-v2.md (leakage-free; packets in frozen order:
   10 critical_condition first, then 64 forbidden_claim, packet_id ascending).
2. For each packet, record the required enum observations
   (forbidden_claim: criterion_semantic_match + speaker_commitment;
   critical_condition: critical_evidence_state) plus verbatim evidence spans.
   Do NOT provide a final verdict - it is derived mechanically.
3. Fill the matching entries in human-review-form-v2.jsonl
   (same packet_ids, same order) and save as human-reviews.jsonl
   in this directory (one JSON object per line), or run:
   python3 span_tool.py prepare human-review-form-v2.jsonl human-reviews.jsonl
4. Continue in any number of sessions; the packet order stays frozen.
   Partial progress can be ingested at any time.

## Machine steps (AI-executed, no semantic judgment)

- run_review_batch_1.py audit - re-run leakage audit
- run_review_batch_1.py ingest - validate reviews, derive final verdicts
  mechanically via frozen judge_core_v2_13.derive_final (through the frozen
  V2.15 lane), write validation/adjudication artifacts
- run_review_batch_1.py freeze - freeze completed reviews, derived labels,
  completed measurement results (526 + n of 600), manifest + hashes

## Integrity facts

- 74/74 packet hashes verified against the frozen baseline batch manifest.
- Frozen lane pins verified: V2.15 lane, V2.6 lane/schema/derivation table,
  V2.13 core (via V2.15 contract pins). M2 V2.6 lane has no applicable packets
  (baseline m2_items = 0); it is referenced, not bypassed.
- Leakage audit clean: workbook/form contain no gold, expected verdicts, or
  model verdicts.
- Packets, predictions, deterministic results, and both source trees are
  immutable in this task.
