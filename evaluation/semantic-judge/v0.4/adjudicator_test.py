#!/usr/bin/env python3
"""Offline unit tests for the v0.4 deterministic adjudicator (no LLM)."""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adjudicator import (CONTRA_RELATIONS, INSUFF_RELATIONS,
                         SUPPORT_RELATIONS, adjudicate_atom)


def rel(**kw):
    base = {"relation": "supports", "relation_type": "DIRECT_SUPPORT",
            "subject_match": True, "scope_match": True, "time_match": True,
            "actor_match": True, "claim_modality": "MAY",
            "source_modality": "MAY", "modality_relation": "same",
            "numeric_relation": "same", "negation_relation": "same",
            "enumeration": "unknown", "support_evidence": "kilden sier regelen",
            "contradiction_evidence": "", "near_miss": False,
            "reason": "test", "confidence": 0.95}
    base.update(kw)
    return base


def contra(**kw):
    kw.setdefault("relation", "contradicts")
    kw.setdefault("relation_type", "EXPLICIT_NEGATION")
    kw.setdefault("contradiction_evidence", "kilden sier motsatt")
    return rel(**kw)


ATOM = {"id": "A1", "numbers": [], "dates": [], "modality": None}


def main():
    cases = [
        ("support", rel(), "SUPPORTED"),
        ("support missing actor match", rel(actor_match=False),
         "INSUFFICIENT_EVIDENCE"),
        ("support with scope mismatch", rel(scope_match=False),
         "INSUFFICIENT_EVIDENCE"),
        ("support with numeric conflict", rel(numeric_relation="conflict"),
         "INSUFFICIENT_EVIDENCE"),
        ("support with negation conflict", rel(negation_relation="conflict"),
         "INSUFFICIENT_EVIDENCE"),
        ("support with modality conflict", rel(modality_relation="conflict"),
         "INSUFFICIENT_EVIDENCE"),
        ("support with contradiction evidence",
         rel(contradiction_evidence="kilden sier noe annet"),
         "INSUFFICIENT_EVIDENCE"),
        ("explicit negation", contra(), "CONTRADICTED"),
        ("exhaustive set exclusion",
         contra(relation_type="EXHAUSTIVE_SET_EXCLUSION",
                enumeration="exhaustive"), "CONTRADICTED"),
        ("mutually exclusive value",
         contra(relation_type="MUTUALLY_EXCLUSIVE_VALUE"), "CONTRADICTED"),
        ("discretion conflict",
         contra(relation_type="EXPLICIT_DISCRETION_CONFLICT"), "CONTRADICTED"),
        ("contradicts without evidence", contra(contradiction_evidence="  "),
         "INSUFFICIENT_EVIDENCE"),
        ("contradicts with disallowed type",
         contra(relation_type="SOURCE_SILENCE"), "INSUFFICIENT_EVIDENCE"),
        ("contradicts with unknown type", contra(relation_type="GUESS"),
         "INSUFFICIENT_EVIDENCE"),
        ("insufficient relation",
         rel(relation="insufficient", relation_type="SCOPE_MISMATCH"),
         "INSUFFICIENT_EVIDENCE"),
        ("invalid relation", rel(relation="maybe"), "INSUFFICIENT_EVIDENCE"),
        ("no relation object", None, "INSUFFICIENT_EVIDENCE"),
        ("injection loud failure",
         rel(relation="contradicts", relation_type="INJECTION_UNVERIFIABLE",
             contradiction_evidence=""), "CONTRADICTED"),
    ]
    failures = []
    for name, obj, expected in cases:
        got = adjudicate_atom(obj, dict(ATOM))
        if got["verdict"] != expected:
            failures.append((name, expected, got["verdict"], got["adjudication"]))
        if got["verdict"] == "CONTRADICTED" and name != "injection loud failure":
            assert got["evidence"]["contradiction"], name
    near = adjudicate_atom(contra(), {**ATOM, "numbers": ["1 286 kr"]})
    assert near["near_miss"] is True
    assert CONTRA_RELATIONS and INSUFF_RELATIONS and SUPPORT_RELATIONS
    print("ADJUDICATOR SELFTEST:", len(cases) + 1, "cases,", len(failures), "failures")
    for f_ in failures:
        print("  FAIL:", f_)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
