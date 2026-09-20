#!/usr/bin/env python3
"""Offline self-check for V2.2 mapper/validator. No model calls."""
import sys

sys.path.insert(0, ".")
import judge_core_v2_2 as J  # noqa: E402

print("prompt_sha:", J.prompt_hash()[:16])

checks = [
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"}), "PRESENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "ASSERTED"}), "PRESENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "QUOTED_ONLY"}), "ABSENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "HYPOTHETICAL_ONLY"}), "ABSENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "NEGATED"}), "ABSENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "SELF_RETRACTED"}), "ABSENT"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "NONCOMMITTAL"}), "UNRESOLVED"),
    (("forbidden_claim", {"criterion_semantic_match": "MATCH", "speaker_commitment": "UNRESOLVED"}), "UNRESOLVED"),
    (("forbidden_claim", {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "ASSERTED"}), "ABSENT"),
    (("forbidden_claim", {"criterion_semantic_match": "UNRESOLVED", "speaker_commitment": "ASSERTED"}), "UNRESOLVED"),
    (("critical_condition", {"critical_evidence_state": "CLEAR_TRIGGER_SUPPORT"}), "TRIGGERED"),
    (("critical_condition", {"critical_evidence_state": "CLEAR_NON_TRIGGER_SUPPORT"}), "NOT_TRIGGERED"),
    (("critical_condition", {"critical_evidence_state": "AMBIGUOUS_OR_CONFLICTING"}), "UNRESOLVED"),
    (("critical_condition", {"critical_evidence_state": "INSUFFICIENT_TO_DECIDE"}), "UNRESOLVED"),
    (("critical_condition", {"critical_evidence_state": "UNRESOLVED"}), "UNRESOLVED"),
]
for (dim, inter), expected in checks:
    got = J.derive_final(dim, inter)[0]
    assert got == expected, (dim, inter, got, expected)
print("derive_final: all", len(checks), "cells PASS")

sut = "Kursene er gratis så langt jeg vet, men det er ikke oppgitt."
parsed = {
    "intermediate": {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION"},
    "evidence_spans": ["gratis så langt jeg vet"],
    "note": "hedget_paastand",
}
r = J.validate_result("forbidden_claim", parsed, sut)
assert r["verdict"] == "PRESENT", r
assert r["derivation_basis"] == "M1:HEDGED_ASSERTION"

bad = dict(parsed)
bad["evidence_spans"] = ["finnes ikke i svaret"]
try:
    J.validate_result("forbidden_claim", bad, sut)
    raise SystemExit("span check should have failed")
except ValueError:
    pass

no_span = dict(parsed)
no_span["evidence_spans"] = []
try:
    J.validate_result("forbidden_claim", no_span, sut)
    raise SystemExit("missing span should have failed")
except ValueError:
    pass

try:
    J.validate_result("critical_condition",
                      {"intermediate": {"critical_evidence_state": "BOGUS"},
                       "evidence_spans": [], "note": ""},
                      "x")
    raise SystemExit("invalid state should have failed")
except ValueError:
    pass

ambiguous = {
    "intermediate": {"critical_evidence_state": "AMBIGUOUS_OR_CONFLICTING"},
    "evidence_spans": [],
    "note": "blandede_signaler",
}
r2 = J.validate_result("critical_condition", ambiguous, "hva som helst")
assert r2["verdict"] == "UNRESOLVED", r2

print("validator: span/norwegian/abstain checks PASS")
print("SELF-CHECK COMPLETE")
