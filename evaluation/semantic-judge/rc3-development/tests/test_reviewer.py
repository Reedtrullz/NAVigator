"""Reviewer V2 schema + fidelity + stability tests (spec 32-34)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
import reviewer_v2 as rv
import arbitration as arb

SRC = "Kommunen gir radgivning. Det er ikke krav om henvisning."


def _valid():
    return {
        "semantic_assessment": "supported",
        "evidence_sufficiency": "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
        "proposed_relation": "SUPPORTED",
        "supporting_span_ids": [0],
        "counter_proof": None,
        "requires_human_review": False,
    }


def test_schema_valid():
    assert rv.validate_schema(_valid()) == []


def test_schema_missing_field_rejected():
    r = _valid()
    del r["counter_proof"]
    errs = rv.validate_schema(r)
    assert "missing_field:counter_proof" in errs


def test_fabricated_span_rejected():
    r = _valid()
    r["supporting_span_ids"] = [424242]
    errs = rv.validate_fidelity(r, SRC)
    assert any("ungrounded_span" in e for e in errs)


def test_ungrounded_reviewer_cannot_route():
    r = _valid()
    r["supporting_span_ids"] = [424242]
    ok, errs = arb.validate_reviewer_output(r, SRC)
    assert not ok
    atom = {"proof_state": "ENGINE_NO_PROOF"}
    out = arb.arbitrate(atom, r, SRC)
    assert out in ("REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT", "PENDING_ROUTE")


def test_stability_metric():
    outs = [_valid(), _valid(), _valid()]
    assert rv.primitive_stability(outs) == 1.0
    divergent = _valid()
    divergent["proposed_relation"] = "CONTRADICTED"
    assert rv.primitive_stability([_valid(), divergent]) == 0.75


if __name__ == "__main__":
    test_schema_valid()
    test_schema_missing_field_rejected()
    test_fabricated_span_rejected()
    test_ungrounded_reviewer_cannot_route()
    test_stability_metric()
    print("reviewer tests: 5/5 PASS")

