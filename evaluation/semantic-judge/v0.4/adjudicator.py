#!/usr/bin/env python3
"""Deterministic adjudicator for semantic judge v0.4.

The relation judge (LLM) only extracts a structured evidence relation;
this module decides every atom verdict in pure code. No model calls,
no I/O, no claim-id lookups (spec section 34).

Core rule (spec sections 3-5, 12): absence_of_support is not
contradiction. CONTRADICTED requires ALL of:
  1. relation == "contradicts"
  2. non-empty contradiction_evidence span
  3. relation_type in the allowed contradiction set
Anything else falls back to INSUFFICIENT_EVIDENCE.

relation == "supports" requires matching subject/scope/time/actor and no
conflict fields; any mismatch or contradiction evidence downgrades to
INSUFFICIENT_EVIDENCE.

Modality matrix (spec section 6, the rules the relation judge applies;
the adjudicator enforces the resulting modality_relation field):
  source MAY,              claim MUST/REQUIRED -> insufficient
                             (WEAKER_MODALITY) unless the source also
                             establishes discretion/non-obligation for the
                             SAME decision -> EXPLICIT_DISCRETION_CONFLICT
  source NOT_REQUIRED,     claim REQUIRED      -> contradicted
  source MUST/REQUIRED,    claim MAY           -> compatible (claim weaker)
  source MAY_BE_ENTITLED,  claim ENTITLED      -> insufficient unless the
                             entitlement itself is established
  source USUALLY,          claim ALWAYS        -> insufficient
                             (universal not established)
  source USUALLY,          claim USUALLY       -> compatible
  source NEVER,            claim ALWAYS        -> contradicted
                             (EXPLICIT_NEGATION)
"""

CONTRA_RELATIONS = {
    "EXPLICIT_NEGATION",
    "MUTUALLY_EXCLUSIVE_VALUE",
    "TEMPORAL_CONFLICT",
    "EXHAUSTIVE_SET_EXCLUSION",
    "EXPLICIT_DISCRETION_CONFLICT",
}

INSUFF_RELATIONS = {
    "SOURCE_SILENCE",
    "SCOPE_MISMATCH",
    "ACTOR_NOT_MENTIONED",
    "LOCALITY_MISMATCH",
    "GENERAL_TO_SPECIFIC",
    "SPECIFIC_TO_UNIVERSAL",
    "NON_EXHAUSTIVE_ENUMERATION",
    "WEAKER_MODALITY",
    "TEMPORAL_SCOPE_UNRESOLVED",
    "MEMBER_ELIGIBILITY_UNKNOWN",
    "OTHER_INSUFFICIENT",
}

SUPPORT_RELATIONS = {
    "DIRECT_SUPPORT",
    "RESTATEMENT",
    "REFERENT_INHERITED",
    "CONDITIONAL_SUPPORT",
}

INJECTION_RELATION = "INJECTION_UNVERIFIABLE"


def _clip_conf(value):
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, conf))


def adjudicate_atom(relation_obj, atom=None):
    """Decide one atom verdict from a structured evidence relation.

    Returns a v0.3-aggregation-compatible atom result dict plus the full
    relation echo (used for structured stability metrics), the evidence
    spans and an adjudication trace.
    """
    atom = atom or {}
    rel = relation_obj or {}
    relation = rel.get("relation")
    rtype = rel.get("relation_type")
    evidence = (rel.get("contradiction_evidence") or "").strip()
    conf = _clip_conf(rel.get("confidence"))
    trace = {
        "relation": relation,
        "relation_type": rtype,
        "has_contradiction_evidence": bool(evidence),
        "atom_has_numbers": bool(atom.get("numbers")),
        "atom_has_dates": bool(atom.get("dates")),
    }
    review = []

    def _insuff(reason):
        trace["rule"] = "fallback_" + reason
        review.append(reason)
        return _result("INSUFFICIENT_EVIDENCE", min(conf, 0.9),
                       rel, atom, trace, review)

    # Injection contract: an instruction asserts nothing the source can
    # support. Loud failure (v0.3 semantics), never soft insufficiency.
    if relation == "injection" or rtype == INJECTION_RELATION:
        trace["rule"] = "injection_unverifiable"
        review.append("injection_unverifiable")
        return _result("CONTRADICTED", conf if conf else 0.9,
                       rel, atom, trace, review)

    if relation == "contradicts":
        if not evidence:
            return _insuff("missing_contradiction_evidence")
        if rtype not in CONTRA_RELATIONS:
            return _insuff("disallowed_contradiction_relation")
        trace["rule"] = "allowed_contradiction_with_evidence"
        return _result("CONTRADICTED", conf, rel, atom, trace, review)

    if relation == "supports":
        for field, label in (("subject_match", "subject"),
                             ("scope_match", "scope"),
                             ("time_match", "time"),
                             ("actor_match", "actor")):
            if rel.get(field) is False:
                return _insuff("supports_without_" + label + "_match")
        for field, label in (("numeric_relation", "numeric"),
                             ("negation_relation", "negation"),
                             ("modality_relation", "modality")):
            if rel.get(field) == "conflict":
                return _insuff("supports_with_" + label + "_conflict")
        if evidence:
            return _insuff("supports_with_contradiction_evidence")
        if rtype and rtype not in SUPPORT_RELATIONS:
            review.append("unrecognized_support_relation_type")
        trace["rule"] = "support_with_full_match"
        return _result("SUPPORTED", conf, rel, atom, trace, review)

    if relation == "insufficient":
        trace["rule"] = "insufficient_relation"
        return _result("INSUFFICIENT_EVIDENCE", min(conf, 0.9),
                       rel, atom, trace, review)

    return _insuff("invalid_relation")


def _result(verdict, confidence, rel, atom, trace, review):
    near_miss = verdict == "CONTRADICTED" and bool(
        atom.get("numbers") or atom.get("dates") or atom.get("modality"))
    return {
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "near_miss": near_miss,
        "reason": (rel.get("reason") or trace.get("rule") or ""),
        "relation": {
            "relation": rel.get("relation"),
            "relation_type": rel.get("relation_type"),
            "claim_modality": rel.get("claim_modality"),
            "source_modality": rel.get("source_modality"),
            "modality_relation": rel.get("modality_relation"),
            "numeric_relation": rel.get("numeric_relation"),
            "negation_relation": rel.get("negation_relation"),
            "enumeration": rel.get("enumeration"),
            "subject_match": rel.get("subject_match"),
            "scope_match": rel.get("scope_match"),
            "time_match": rel.get("time_match"),
            "actor_match": rel.get("actor_match"),
        },
        "evidence": {
            "support": rel.get("support_evidence") or "",
            "contradiction": rel.get("contradiction_evidence") or "",
        },
        "adjudication": trace,
        "review_reasons": review,
    }
