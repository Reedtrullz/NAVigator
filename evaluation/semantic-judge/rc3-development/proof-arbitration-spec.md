# Proof Arbitration Spec (ARBITRATION_V2)

## Inputs
- engine per-atom results with proof states (from PROOF_ENGINE_RC3)
- reviewer structured output (REVIEWER_V2 schema):
  {semantic_assessment, evidence_sufficiency, proposed_relation,
   supporting_span_ids, counter_proof, requires_human_review}
- evidence sufficiency class: EVIDENCE_SUFFICIENT_FOR_PROOF |
  EVIDENCE_RELEVANT_BUT_UNRESOLVED | EVIDENCE_GENUINELY_INSUFFICIENT

## Monotonic rules (frozen)

1. ENGINE_PROOF_ACCEPTED + reviewer agrees/no counter-proof:
   route by routing table from the proof (auto SUPPORT/CONTRA or review per
   safety classes). Reviewer may add uncertainty metadata only.
2. ENGINE_PROOF_ACCEPTED + reviewer disagrees WITHOUT valid counter-proof:
   proof stands; reviewer dissent recorded as uncertainty metadata; product
   route unchanged from proof state.
3. ENGINE_PROOF_ACCEPTED + reviewer delivers COUNTER_PROOF: counter-proof
   must pass the same validation chain (grounded spans in packet, doctrine,
   structural validator, soundness). If valid, result = ENGINE_CONFLICT ->
   REVIEW_REQUIRED. If invalid, rule 2 applies.
4. ENGINE_NO_PROOF: auto impossible regardless of reviewer confidence.
   If evidence sufficiency = GENUINELY_INSUFFICIENT -> ABSTAIN_INSUFFICIENT;
   if RELEVANT_BUT_UNRESOLVED -> REVIEW_REQUIRED.
5. ENGINE_CONFLICT: always REVIEW_REQUIRED.
6. ENGINE_UNSAFE (context guard fired without positive contradiction proof):
   REVIEW_REQUIRED; reviewer cannot clear it; only a valid counter-proof
   path (rule 3) or new deterministic evidence can change it.
7. Semantic truth and product routing are separated: reviewer semantic
   assessment never directly produces product action (spec 29).

## Thresholds
No confidence threshold participates in arbitration. The RC2 0.90 auto-accept
gate is removed (it had no semantic meaning; spec 31). All routing is
proof-state + sufficiency driven.

