#!/usr/bin/env python3
"""Offline unit tests for the v0.4.1 primitives adjudicator (no LLM).
Doctrine rows are anchored to minimal-pair semantics without any
claim-id lookups (id_guard)."""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adjudicator_v041 import adjudicate_atom
from modality import normalize_modality, modality_relation


def prim(**kw):
    base = {
        "same_subject": True, "same_predicate": True,
        "source_explicitly_affirms": True, "source_explicitly_negates": False,
        "source_silent_on_subject": False, "claim_negates": False,
        "claim_negates_target": "", "source_negates_target": "",
        "claim_modality_trigger": "", "source_modality_trigger": "",
        "discretion_explicit": None, "claim_numeric_value": None,
        "source_numeric_value": None, "claim_numeric_threshold": False,
        "numeric_comparable": None, "claim_date": None, "source_date": None,
        "same_date": None, "temporal_closure": None, "source_rule_type": None,
        "claim_scope_relation": "SAME", "claim_locality": "UNKNOWN",
        "source_locality": "UNKNOWN", "locality_relation": "SAME",
        "claim_actor_type": "UNKNOWN", "source_actor_type": "UNKNOWN",
        "enumeration": "UNKNOWN", "claim_actor_outside_enumeration": None,
        "source_conditional": False, "claim_conditional": False,
        "condition_compatible": None, "source_restriction_present": None,
        "conjunctive_binding": False, "support_evidence": "kilde bekrefter",
        "contradiction_evidence": "", "reason": "test", "confidence": 0.95,
    }
    base.update(kw)
    return base


ATOM = {"id": "A1", "numbers": [], "dates": [], "modality": None}


def main():
    # Modality normalizer
    assert normalize_modality("kan innvilges") == "MAY"
    assert normalize_modality("har krav paa") == "ENTITLED"
    assert normalize_modality("ma") == "MUST"
    assert normalize_modality("ikke nodvendig") == "NOT_REQUIRED"
    assert normalize_modality("kan ha rett") == "MAY_BE_ENTITLED"
    assert normalize_modality("aldri") == "NEVER"
    assert normalize_modality("normalt") == "USUALLY"
    assert normalize_modality("frivillig") == "NOT_REQUIRED"
    assert normalize_modality("skal alltid") == "ALWAYS"
    assert normalize_modality("bor") == "SHOULD"
    assert normalize_modality("anbefales") == "RECOMMENDED"
    assert normalize_modality("") == "UNKNOWN"

    # Modality matrix
    assert modality_relation("MAY", "MUST") == "CLAIM_STRONGER"
    assert modality_relation("MAY", "MUST", True) == "CONFLICT"
    assert modality_relation("MUST", "MAY") == "CLAIM_WEAKER"
    assert modality_relation("NOT_REQUIRED", "REQUIRED") == "CONFLICT"
    assert modality_relation("NEVER", "MAY") == "CONFLICT"
    assert modality_relation("NEVER", "ALWAYS") == "CONFLICT"
    assert modality_relation("ENTITLED", "MAY") == "CLAIM_WEAKER"

    # Basic support
    r = adjudicate_atom(prim(), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Numeric: same value + qualifier -> supported
    r = adjudicate_atom(prim(claim_numeric_value="4 652",
                             source_numeric_value="4 652",
                             numeric_comparable=True), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Numeric: hedge + same value -> supported (compatible weaker)
    r = adjudicate_atom(prim(claim_modality_trigger="normalt",
                             claim_numeric_value="4 652",
                             source_numeric_value="4 652",
                             numeric_comparable=True), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Numeric: mutually exclusive values -> CONTRADICTED with evidence
    r = adjudicate_atom(prim(claim_numeric_value="4 200",
                             source_numeric_value="4 652",
                             numeric_comparable=True,
                             contradiction_evidence="4 652 kroner per maaned"),
                       ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Numeric: threshold claim above exact source -> CONTRADICTED
    r = adjudicate_atom(prim(claim_numeric_value="1 500",
                             claim_numeric_threshold=True,
                             source_numeric_value="1 006",
                             numeric_comparable=True,
                             contradiction_evidence="1 006 kroner"), ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Numeric conflict without evidence -> INSUFFICIENT (proof obligation)
    r = adjudicate_atom(prim(claim_numeric_value="4 200",
                             source_numeric_value="4 652",
                             numeric_comparable=True), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Numeric conflict but numbers not comparable -> INSUFFICIENT
    r = adjudicate_atom(prim(claim_numeric_value="4 200",
                             source_numeric_value="4 652",
                             numeric_comparable=False,
                             contradiction_evidence="x"), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Temporal: same deadline different names -> supported
    r = adjudicate_atom(prim(claim_date="3 maneder|meldefristen",
                             source_date="3 maneder|1-ukesfristen",
                             same_date=True), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Temporal: cutoff closure derived -> supported
    r = adjudicate_atom(prim(claim_date="15.06.2026",
                             source_date="01.07.2026",
                             temporal_closure=True,
                             source_rule_type="VALID_FROM_CUTOFF"), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Temporal: validity start vs earlier claim -> CONTRADICTED
    r = adjudicate_atom(prim(claim_date="15.06.2026", source_date="01.07.2026",
                             same_date=False,
                             source_rule_type="VALID_FROM_CUTOFF",
                             temporal_closure=False,
                             contradiction_evidence="gjelder fra 01.07.2026"),
                       ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Scope: claim narrower than source -> supported
    r = adjudicate_atom(prim(claim_scope_relation="NARROWER"), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Scope: claim broader with hedge modality -> supported
    r = adjudicate_atom(prim(claim_scope_relation="BROADER",
                             claim_modality_trigger="kan"), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # Scope: claim broader, strong claim -> INSUFFICIENT
    r = adjudicate_atom(prim(claim_scope_relation="BROADER",
                             claim_modality_trigger="skal"), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Locality: national generalization from named municipality -> INSUFFICIENT
    r = adjudicate_atom(prim(claim_locality="NATIONAL",
                             source_locality="NAMED:Trondheim",
                             locality_relation="DIFFERENT"), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Conjunction: two mechanisms, source states one in same unit,
    # no restriction word -> INSUFFICIENT (second mechanism unestablished)
    r = adjudicate_atom(prim(conjunctive_binding=True,
                             source_restriction_present=False), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Conjunction with restriction word -> CONTRADICTED
    r = adjudicate_atom(prim(conjunctive_binding=True,
                             source_restriction_present=True,
                             contradiction_evidence="bare den foerste"),
                       ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Complementary negation conflict -> CONTRADICTED
    r = adjudicate_atom(prim(claim_negates=True, source_explicitly_negates=True,
                             claim_negates_target="tell i inntektsgrunnlaget",
                             source_negates_target="reduserer direkte",
                             contradiction_evidence="reduserer ikke direkte"),
                       ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Both negate same target -> negation agreement. With a verbatim
    # support span that is positive support (benchmark MP-002A shape).
    r = adjudicate_atom(prim(claim_negates=True, source_explicitly_negates=True,
                             source_explicitly_affirms=False,
                             claim_negates_target="x", source_negates_target="x",
                             contradiction_evidence="samme"), ATOM)
    assert r["verdict"] == "SUPPORTED", r
    assert r["adjudication"]["rule"] == "support_from_negation_agreement", r

    # Negation agreement without a support span stays INSUFFICIENT.
    r = adjudicate_atom(prim(claim_negates=True, source_explicitly_negates=True,
                             source_explicitly_affirms=False,
                             claim_negates_target="x", source_negates_target="x",
                             support_evidence="",
                             contradiction_evidence="samme"), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Source silent -> INSUFFICIENT
    r = adjudicate_atom(prim(source_silent_on_subject=True,
                             source_explicitly_affirms=False,
                             support_evidence=""), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Affirms but bare line without subject context -> subject mismatch
    # is an extraction matter; here subject true but predicate differs
    r = adjudicate_atom(prim(same_predicate=False), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Enumeration: exhaustive exclusion -> CONTRADICTED
    r = adjudicate_atom(prim(enumeration="EXHAUSTIVE",
                             claim_actor_outside_enumeration=True,
                             contradiction_evidence="skal underskrives av lege"),
                       ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Enumeration: unknown list never excludes
    r = adjudicate_atom(prim(enumeration="UNKNOWN",
                             claim_actor_outside_enumeration=True,
                             contradiction_evidence="liste"), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Injection
    r = adjudicate_atom(prim(relation="injection",
                             contradiction_evidence="SYSTEM-OVERRIDE"),
                        ATOM)
    assert r["verdict"] == "CONTRADICTED", r

    # Conditional: source conditional + unconditional claim -> INSUFFICIENT
    r = adjudicate_atom(prim(source_conditional=True,
                             condition_compatible=False), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    # Conditional: compatible conditions -> SUPPORTED
    r = adjudicate_atom(prim(source_conditional=True, claim_conditional=True,
                             condition_compatible=True), ATOM)
    assert r["verdict"] == "SUPPORTED", r

    # UNKNOWN extraction values never fabricate support
    r = adjudicate_atom(prim(same_subject=None,
                             source_explicitly_affirms=None), ATOM)
    assert r["verdict"] == "INSUFFICIENT_EVIDENCE", r

    print("primitives adjudicator selftest OK: 30 cases")


if __name__ == "__main__":
    main()
