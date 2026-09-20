"""Reviewer V2 contract (REVIEWER_V2, spec 32-34).

Structured-output schema, fidelity validation, and primitive-stability
comparison. The reviewer transport (gpt-5.6-luna via local proxy) is
reused unchanged from RC2; this module only defines the contract RC3
accepts. No free-text final verdicts.
"""
import json

SCHEMA = {
    "semantic_assessment": str,
    "evidence_sufficiency": str,
    "proposed_relation": str,
    "supporting_span_ids": list,
    "counter_proof": (dict, type(None)),
    "requires_human_review": bool,
}

VALID_SUFFICIENCY = {
    "EVIDENCE_SUFFICIENT_FOR_PROOF",
    "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
    "EVIDENCE_GENUINELY_INSUFFICIENT",
}

VALID_RELATIONS = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"}


def parse_reviewer_json(raw_text):
    """Parse strict JSON reviewer output; return dict or None."""
    try:
        obj = json.loads(raw_text)
    except (ValueError, TypeError):
        return None
    return obj if isinstance(obj, dict) else None


def validate_schema(review):
    """Structural schema check. Returns list of error strings."""
    errors = []
    if not isinstance(review, dict):
        return ["not_an_object"]
    for field, typ in SCHEMA.items():
        if field not in review:
            errors.append("missing_field:" + field)
        elif not isinstance(review[field], typ):
            errors.append("bad_type:" + field)
    if review.get("evidence_sufficiency") not in VALID_SUFFICIENCY:
        errors.append("bad_evidence_sufficiency")
    if review.get("proposed_relation") not in VALID_RELATIONS:
        errors.append("bad_proposed_relation")
    return errors


def validate_fidelity(review, source_text):
    """Every span ref must ground into the source text (spec 33).
    Ungrounded spans disqualify the output from routing use."""
    errors = validate_schema(review)
    if errors:
        return errors
    for s in review["supporting_span_ids"]:
        if not (isinstance(s, int) and 0 <= s < max(len(source_text), 1)):
            errors.append("ungrounded_span:%s" % s)
    cp = review.get("counter_proof")
    if cp is not None:
        if not isinstance(cp, dict) or not cp.get("span_ids") or \
                not cp.get("target_claim"):
            errors.append("bad_counter_proof")
        else:
            for s in cp["span_ids"]:
                if not (isinstance(s, int) and
                        0 <= s < max(len(source_text), 1)):
                    errors.append("ungrounded_counter_span:%s" % s)
    return errors


def routing_fields(review):
    """The primitive fields that control routing (stability targets
    apply to these, spec 34)."""
    return {
        "evidence_sufficiency": review.get("evidence_sufficiency"),
        "proposed_relation": review.get("proposed_relation"),
        "requires_human_review": review.get("requires_human_review"),
        "has_counter_proof": review.get("counter_proof") is not None,
    }


def primitive_stability(outputs):
    """Fraction of routing-field primitives that agree across runs."""
    if len(outputs) < 2:
        return 1.0
    fields = [routing_fields(o) for o in outputs]
    total, agree = 0, 0
    for key in fields[0]:
        vals = [f[key] for f in fields]
        total += 1
        agree += 1 if all(v == vals[0] for v in vals) else 0
    return agree / total if total else 1.0

