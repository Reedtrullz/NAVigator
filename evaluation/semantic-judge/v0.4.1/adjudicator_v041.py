#!/usr/bin/env python3
"""Deterministic adjudicator for semantic judge v0.4.1 (Iteration A).

The extraction LLM returns concrete observation primitives (no abstract
relation_type classification). This module computes the relation:
modality normalization (modality.py), modality matrix, numeric /
negation / temporal conflicts, scope and locality relations, enumeration
and the contradiction proof obligation. No model calls, no I/O, no
claim-id lookups (spec section 30 id_guard).
"""
import re

from modality import normalize_modality, modality_relation

STRONG_MODALITIES = {"MUST", "REQUIRED", "ALWAYS", "ENTITLED"}
HEDGE_MODALITIES = {"MAY", "USUALLY", "SHOULD", "RECOMMENDED",
                    "MAY_BE_ENTITLED"}

def _as_bool(v):
    return v is True


def _text(v):
    return str(v).strip() if v is not None else ""


def _norm_number(s):
    """Extract digits of a monetary/numeric value for strict comparison."""
    if s is None:
        return None
    digits = re.sub(r"[^0-9]", "", str(s))
    return digits or None


def adjudicate_atom(rel, atom=None):
    """Decide one atom verdict from primitive observations."""
    rel = dict(rel or {})
    atom = atom or {}

    def _result(verdict, confidence, rule, reasons=None, rtype=None):
        near_miss = verdict == "CONTRADICTED" and bool(
            atom.get("numbers") or atom.get("dates") or atom.get("modality"))
        s_mod = rel.get("_source_modality") or normalize_modality(
            rel.get("source_modality_trigger"))
        c_mod = rel.get("_claim_modality") or normalize_modality(
            rel.get("claim_modality_trigger"))
        return {
            "verdict": verdict,
            "confidence": round(max(0.0, min(1.0, confidence)), 2),
            "near_miss": near_miss,
            "reason": rel.get("reason") or rule,
            "relation": {
                "relation": rel.get("_relation") or ("injection" if rule == "injection_unverifiable" else None),
                "relation_type": rtype,
                "source_modality": s_mod,
                "claim_modality": c_mod,
                "modality_relation": rel.get("_modality_relation"),
                "numeric_relation": rel.get("_numeric_relation"),
                "negation_relation": rel.get("_negation_relation"),
                "locality_relation": rel.get("locality_relation"),
                "scope_relation": rel.get("claim_scope_relation"),
                "enumeration": rel.get("enumeration"),
                "same_subject": rel.get("same_subject"),
                "same_predicate": rel.get("same_predicate"),
                "source_explicitly_affirms": rel.get("source_explicitly_affirms"),
                "source_explicitly_negates": rel.get("source_explicitly_negates"),
                "temporal_closure": rel.get("temporal_closure"),
            },
            "evidence": {
                "support": rel.get("support_evidence") or "",
                "contradiction": rel.get("contradiction_evidence") or "",
            },
            "adjudication": {"rule": rule},
            "review_reasons": reasons or [],
        }

    def _insuff(rule, reasons=None):
        return _result("INSUFFICIENT_EVIDENCE",
                       min(float(rel.get("confidence") or 0.5), 0.9),
                       rule, reasons)

    # Injection contract: loud failure, never soft insufficiency.
    if rel.get("relation") == "injection":
        rel["_relation"] = "injection"
        return _result("CONTRADICTED", float(rel.get("confidence") or 0.9),
                       "injection_unverifiable")

    same_subject = rel.get("same_subject") is True
    same_predicate = rel.get("same_predicate") is not False
    affirms = rel.get("source_explicitly_affirms") is True
    negates = rel.get("source_explicitly_negates") is True
    silent = rel.get("source_silent_on_subject") is True
    evidence = _text(rel.get("contradiction_evidence"))
    support = _text(rel.get("support_evidence"))

    s_mod = normalize_modality(rel.get("source_modality_trigger"))
    c_mod = normalize_modality(rel.get("claim_modality_trigger"))
    rel["_source_modality"] = s_mod
    rel["_claim_modality"] = c_mod
    m_rel = modality_relation(
        s_mod, c_mod,
        discretion_explicit=_as_bool(rel.get("discretion_explicit")),
        source_trigger_text=_text(rel.get("source_modality_trigger")),
        claim_text=_text(atom.get("text")))
    rel["_modality_relation"] = m_rel

    claim_val = rel.get("claim_numeric_value")
    source_val = rel.get("source_numeric_value")
    comparable = rel.get("numeric_comparable") is True
    numeric_conflict = False
    if (comparable and claim_val is not None and source_val is not None):
        cv, sv = _norm_number(claim_val), _norm_number(source_val)
        numeric_conflict = bool(cv and sv and cv != sv)
    rel["_numeric_relation"] = ("conflict" if numeric_conflict
                                else "same" if (claim_val is not None and
                                                source_val is not None and
                                                _norm_number(claim_val) ==
                                                _norm_number(source_val))
                                else "n/a")

    claim_neg = rel.get("claim_negates") is True
    both_negate = claim_neg and negates
    targets_differ = (both_negate and _text(rel.get("claim_negates_target"))
                      and _text(rel.get("source_negates_target"))
                      and _text(rel.get("claim_negates_target")).lower()
                      != _text(rel.get("source_negates_target")).lower())
    # A negated claim atom ("X er ikke skattepliktig") usually asserts a
    # positive rule about a negative property; affirm + claim_negates is
    # therefore polarity-ambiguous by itself. A conflict needs explicit
    # source negation of this atom or complementary negated targets.
    affirm_negated_atom = affirms and claim_neg and not negates
    neg_conflict = (targets_differ or (negates and not claim_neg)
                    or (negates and claim_neg and not _text(rel.get("claim_negates_target"))
                        and not _text(rel.get("source_negates_target"))))
    rel["_negation_relation"] = ("conflict" if neg_conflict
                                 else "same" if (claim_neg == negates)
                                 else "n/a")

    atom_text_pre = _text(atom.get("text")).lower()
    existence_scope = any(m in atom_text_pre for m in
                          ("enkelte kommuner", "varierer",
                           "mellom kommunene",
                           "fra kommune til kommune"))
    if (existence_scope and neg_conflict
            and (negates or str(rel.get("locality_relation") or "")
                 .upper() == "BROADER")):
        existence_scope = True
    elif (str(rel.get("locality_relation") or "").upper() == "BROADER"
            and negates and neg_conflict):
        # BROADER + source-side negation is the primitive signature of
        # a variation statement ("varierer mellom kommunene") that the
        # claim universalizes; not refutable by polarity alone.
        existence_scope = True
    if existence_scope and neg_conflict:
        # An existence/variation claim over the municipal domain
        # ("koster i enkelte kommuner", "varierer mellom kommunene")
        # is not refuted by one source's universal statement; refuting
        # an existence claim needs exhaustive enumeration, which this
        # protocol never extracts.
        neg_conflict = False
        rel["_negation_relation"] = "n/a"

    same_date = rel.get("same_date")
    temporal_conflict = same_date is False and bool(
        _text(rel.get("claim_date")) and _text(rel.get("source_date")))

    exhaustive_exclusion = (str(rel.get("enumeration") or "").upper()
                            == "EXHAUSTIVE"
                            and rel.get("claim_actor_outside_enumeration") is True)

    contradiction_reasons = []
    rtype = None
    if (rel.get("predicate_complement_conflict") is True and same_subject
            and claim_neg and negates and evidence
            and _text(rel.get("claim_negates_target"))
            and _text(rel.get("source_negates_target"))
            and _text(rel.get("claim_negates_target")).lower()
            != _text(rel.get("source_negates_target")).lower()):
        contradiction_reasons.append("complementary_predicate_conflict")
        rtype = "COMPLEMENTARY_PREDICATE_CONFLICT"
    if numeric_conflict and (same_subject or comparable):
        contradiction_reasons.append("numeric_conflict")
        rtype = rtype or "MUTUALLY_EXCLUSIVE_VALUE"
    if neg_conflict and same_subject and not affirm_negated_atom:
        contradiction_reasons.append("polarity_conflict")
        rtype = rtype or "EXPLICIT_NEGATION"
    if temporal_conflict and same_subject:
        contradiction_reasons.append("temporal_conflict")
        rtype = rtype or "TEMPORAL_CONFLICT"
    if m_rel == "CONFLICT" and same_subject:
        contradiction_reasons.append("modality_conflict")
        rtype = rtype or "EXPLICIT_NEGATION"
    if exhaustive_exclusion and same_subject:
        contradiction_reasons.append("exhaustive_exclusion")
        rtype = rtype or "EXHAUSTIVE_SET_EXCLUSION"
    atom_text_pre = _text(atom.get("text")).lower()
    if (same_subject and same_predicate
            and any(w in atom_text_pre for w in
                    ("kun ", "bare ", "alene ", "eneste "))
            and _text(support)
            and (" og " in support.lower())
            and not any(m in support.lower() for m in
                        ("blant annet", "bl.a.", "for eksempel",
                         "eksempelvis", "også", "eller"))):
        # Claim asserts exclusivity; the affirming source sentence
        # enumerates an additional coordinated element. An exhaustive
        # claim is refuted by a second factor.
        contradiction_reasons.append("exclusivity_conflict")
        rtype = rtype or "EXCLUSIVE_CLAIM_ADDITIONAL_ELEMENT"
    if (m_rel == "CONFLICT" and s_mod == "MAY" and c_mod in STRONG_MODALITIES
            and _as_bool(rel.get("discretion_explicit")) and same_subject):
        contradiction_reasons.append("discretion_conflict")
        rtype = "EXPLICIT_DISCRETION_CONFLICT"
    if (rel.get("conjunctive_binding") is True
            and rel.get("source_restriction_present") is True and evidence):
        contradiction_reasons.append("conjunctive_restriction_conflict")
        rtype = rtype or "EXPLICIT_NEGATION"

    if contradiction_reasons:
        if (exhaustive_exclusion and not evidence
                and _text(support)
                and contradiction_reasons == ["exhaustive_exclusion"]):
            # The extractor documented the exclusion in its reason but
            # filed the verbatim span under support_evidence. The
            # exclusion sentence itself is the contradiction evidence.
            evidence = support
        if not evidence:
            return _insuff("contradiction_without_evidence",
                           contradiction_reasons)
        rel["_relation"] = "contradicts"
        return _result("CONTRADICTED", float(rel.get("confidence") or 0.9),
                       "contradiction_with_evidence",
                       contradiction_reasons, rtype)

    if (affirm_negated_atom and same_subject and same_predicate
            and _text(support)):
        atom_text = _text(atom.get("text")).lower()
        composite_negated = (" og " in atom_text and bool(atom.get("negations")))
        if composite_negated and not any(
                marker in support.lower()
                for marker in ("ikke", "ingen", "aldri", "uten", "nei")):
            # Composite atom with a negated conjunct: the support span
            # must itself carry the negation, otherwise the source only
            # establishes the non-negated conjunct.
            return _insuff("conjunctive_negation_not_in_support_span")
        # The source affirms the atom's assertion, which itself describes
        # a negative property; treat the affirming span as support.
        rel["_relation"] = "supports"
        return _result("SUPPORTED", float(rel.get("confidence") or 0.9),
                       "support_from_affirmed_negation")

    both_negate_same = both_negate and not targets_differ
    if both_negate_same:
        # Negation agreement: source denies the same assertion the claim
        # denies. That is positive support, not source silence.
        if not support:
            return _insuff("negation_agreement_without_support_span")
        if not same_subject or not same_predicate:
            return _insuff("subject_or_predicate_not_matched")
        rel["_relation"] = "supports"
        return _result("SUPPORTED", float(rel.get("confidence") or 0.9),
                       "support_from_negation_agreement")

    if negates and not affirms:
        return _insuff("source_explicit_negation_without_claim_polarity_conflict")

    if not affirms:
        return _insuff("no_explicit_affirmation")
    if not support:
        return _insuff("affirmation_without_support_span")
    if not same_subject:
        return _insuff("subject_not_matched")
    if not same_predicate:
        return _insuff("predicate_not_matched")

    enumeration = str(rel.get("enumeration") or "").upper()
    atom_text = _text(atom.get("text")).lower()
    exclusivity = any(w in atom_text for w in
                      ("kun ", "bare ", "alene ", "eneste "))
    if (enumeration == "NON_EXHAUSTIVE" and exclusivity
            and not _text(rel.get("support_evidence")).lower().startswith("kun")):
        # The claim asserts exclusivity ("kun X, Y og Z"), but the
        # matching source list is explicitly open-ended ("blant annet").
        # An open list cannot establish an exclusive rule.
        return _insuff("claim_exclusive_but_list_non_exhaustive")

    scope = str(rel.get("claim_scope_relation") or "UNKNOWN").upper()
    c_loc = str(rel.get("claim_locality") or "UNKNOWN").upper()
    s_loc = str(rel.get("source_locality") or "UNKNOWN").upper()
    loc_rel = rel.get("locality_relation")
    scope_blocked = []
    if scope == "BROADER" and c_mod not in HEDGE_MODALITIES:
        scope_blocked.append("claim_broader_than_source")
    if scope == "DIFFERENT":
        scope_blocked.append("different_scope")
    if loc_rel == "DIFFERENT":
        scope_blocked.append("locality_different")
    elif loc_rel == "UNKNOWN" and "NAMED" in c_loc and s_loc in (
            "NATIONAL", "MUNICIPAL_GENERAL", "UNKNOWN") and "NAMED" not in s_loc:
        scope_blocked.append("locality_unresolved")
    elif c_loc.startswith("NATIONAL") and s_loc.startswith("NAMED"):
        scope_blocked.append("local_generalization")
    if scope_blocked:
        return _insuff("scope_blocked:" + ";".join(scope_blocked))

    if evidence:
        # Verbatim contradiction-flavored span, but no positive conflict
        # primitive survived the scope gates: extraction disagreement.
        return _insuff("contradiction_evidence_without_computed_conflict")

    if m_rel == "CLAIM_STRONGER":
        return _insuff("claim_stronger_than_source")
    if m_rel == "UNKNOWN" and (s_mod != "UNKNOWN" or c_mod != "UNKNOWN"):
        # one side normalized to UNKNOWN while the other is specific:
        # tolerate only when the specific side is a hedge on the claim.
        if s_mod != "UNKNOWN" and c_mod in STRONG_MODALITIES:
            return _insuff("source_modality_unresolved_claim_strong")

    if temporal_conflict:
        return _insuff("temporal_dates_differ")
    if (str(rel.get("source_rule_type") or "").upper() == "VALID_FROM_CUTOFF"
            and rel.get("temporal_closure") is False):
        return _insuff("temporal_closure_refuted")

    if rel.get("source_conditional") is True and rel.get("claim_conditional") is not True:
        return _insuff("specific_to_universal")
    if (rel.get("conjunctive_binding") is True
            and rel.get("source_restriction_present") is not True):
        return _insuff("conjunctive_unit_does_not_establish_second_conjunct")
    if (rel.get("source_conditional") is True
            and rel.get("claim_conditional") is True
            and rel.get("condition_compatible") is False):
        return _insuff("condition_incompatible")

    rel["_relation"] = "supports"
    return _result("SUPPORTED", float(rel.get("confidence") or 0.9),
                   "support_from_primitives")
