"""Monotonic proof arbitration (ARBITRATION_V2, spec 8-9, 30).

The engine's accepted proof is authoritative. The reviewer result is a
new evidence/proof proposal, never an authoritative final verdict.
Reversal requires a valid COUNTER_PROOF; upgrade from NO_PROOF to auto
requires an accepted proof object, never confidence alone.
"""
import re

REVIEWER_SCHEMA_FIELDS = (
    "semantic_assessment", "evidence_sufficiency",
    "proposed_relation", "supporting_span_ids", "counter_proof",
    "requires_human_review",
)

SUFFICIENCY = ("EVIDENCE_SUFFICIENT_FOR_PROOF",
               "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
               "EVIDENCE_GENUINELY_INSUFFICIENT")

_RELATIONS = ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE")


def _span_grounded(span_id, source_text):
    """span ids are integer character offsets into the source; a span
    is grounded when it points inside the source text."""
    if not isinstance(span_id, int):
        return False
    return 0 <= span_id < max(len(source_text), 1)


def validate_reviewer_output(review, source_text):
    """Structural validation (spec 32-33). Returns (ok, errors)."""
    errors = []
    if not isinstance(review, dict):
        return False, ["not_an_object"]
    for f in REVIEWER_SCHEMA_FIELDS:
        if f not in review:
            errors.append("missing_field:" + f)
    if errors:
        return False, errors
    if review["evidence_sufficiency"] not in SUFFICIENCY:
        errors.append("bad_evidence_sufficiency")
    if review["proposed_relation"] not in _RELATIONS:
        errors.append("bad_proposed_relation")
    if not isinstance(review["supporting_span_ids"], list):
        errors.append("bad_supporting_span_ids")
    else:
        for s in review["supporting_span_ids"]:
            if not _span_grounded(s, source_text):
                errors.append("ungrounded_span:%s" % s)
    cp = review["counter_proof"]
    if cp is not None and not (
            isinstance(cp, dict) and
            cp.get("span_ids") and
            all(_span_grounded(s, source_text) for s in cp["span_ids"])
            and cp.get("target_claim")):
        errors.append("bad_counter_proof")
    return (not errors), errors


def arbitrate(atom_result, review=None, source_text=""):
    """Monotonic arbitration for one atom. Returns product action.

    Rules (frozen, spec 8-9):
      R1 ENGINE_PROOF_ACCEPTED + no valid counter-proof
         -> keep engine auto (reviewer may confirm or add metadata).
      R2 ENGINE_PROOF_ACCEPTED + valid counter-proof pointing at
         concrete spans -> REVIEW_REQUIRED (adjudication, not auto
         flip).
      R3 ENGINE_UNSAFE / ENGINE_CONFLICT -> REVIEW_REQUIRED always.
      R4 ENGINE_NO_PROOF -> reviewer can never upgrade to auto.
         Sufficiency classifier decides abstain vs review.
      R5 Reviewer confidence is metadata only; never routed on.
    """
    state = atom_result.get("proof_state")
    if review is not None:
        ok, _ = validate_reviewer_output(review, source_text)
        if not ok:
            # Unvalid reviewer output cannot influence routing at all.
            review = None
    if state == "ENGINE_PROOF_ACCEPTED":
        has_counter = bool(review and review.get("counter_proof"))
        if has_counter:
            return "REVIEW_REQUIRED"
        # Downgrade authority (spec 8) is bounded: a bare
        # requires_human_review flag without grounded reviewer spans
        # is metadata only and must not overturn a valid proof. The
        # objection must at least be anchored in the evidence packet.
        if review and review.get("requires_human_review") \
                and review.get("supporting_span_ids"):
            return "REVIEW_REQUIRED"
        return atom_result["final_verdict"]
    if state in ("ENGINE_UNSAFE", "ENGINE_CONFLICT"):
        return "REVIEW_REQUIRED"
    if state == "ENGINE_NO_PROOF":
        # Upgrade to auto is structurally impossible here: this branch
        # returns only review/abstain actions (spec 9).
        if review is not None:
            # Reviewer relevant-but-unresolved keeps review; genuine
            # insufficiency abstains regardless of reviewer confidence.
            if review.get("evidence_sufficiency") == \
                    "EVIDENCE_GENUINELY_INSUFFICIENT":
                return "ABSTAIN_INSUFFICIENT"
            return "REVIEW_REQUIRED"
        return "PENDING_ROUTE"
    return "REVIEW_REQUIRED"
