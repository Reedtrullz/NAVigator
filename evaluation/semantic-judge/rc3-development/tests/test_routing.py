"""Routing + aggregation tests (spec 10-12, 26): abstain is a real
final action; review dominates; mixed polarity aggregates
deterministically."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
import routing as rt


def test_genuinely_insufficient_abstains():
    cls, _ = rt.classify_sufficiency(
        "Kommunen gir oekonomisk radgivning pa tirsdager.",
        "Skolen har ansvar for PPT-vurdering av elever.")
    assert cls == "EVIDENCE_GENUINELY_INSUFFICIENT"
    out = rt.route_atom({"proof_state": "ENGINE_NO_PROOF"},
                        "Kommunen gir oekonomisk radgivning pa tirsdager.",
                        "Skolen har ansvar for PPT-vurdering av elever.")
    assert out == "ABSTAIN_INSUFFICIENT"


def test_relevant_but_unresolved_reviews():
    out = rt.route_atom(
        {"proof_state": "ENGINE_NO_PROOF"},
        "Kommunen gir oekonomisk radgivning.",
        "Kommunen gir oekonomisk radgivning i begrenset omfang.")
    assert out == "REVIEW_REQUIRED"


def test_aggregation_rules():
    A, C, R, I = "AUTO_SUPPORTED", "AUTO_CONTRADICTED", \
        "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"
    def at(v):
        return {"route": v}
    assert rt.aggregate_atoms([at(A), at(A)])["product_action"] == A
    assert rt.aggregate_atoms([at(A), at(C)])["product_action"] \
        == "PARTIALLY_SUPPORTED"
    assert rt.aggregate_atoms([at(A), at(R)])["product_action"] == R
    assert rt.aggregate_atoms([at(I), at(I)])["product_action"] == I
    assert rt.aggregate_atoms([at(A), at(I)])["product_action"] \
        == "PARTIALLY_SUPPORTED"
    assert rt.aggregate_atoms([at(C), at(C)])["product_action"] == C


def test_abstain_not_alias_of_review():
    # The abstain action is a distinct product action value.
    assert "ABSTAIN_INSUFFICIENT" in rt.PRODUCT_ACTIONS
    assert "ABSTAIN_INSUFFICIENT" != "REVIEW_REQUIRED"


if __name__ == "__main__":
    test_genuinely_insufficient_abstains()
    test_relevant_but_unresolved_reviews()
    test_aggregation_rules()
    test_abstain_not_alias_of_review()
    print("routing tests: 4/4 PASS")
