"""Arbitration tests (spec 8-9, 30): monotonic authority model."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
import arbitration as arb


def _atom(state, verdict="AUTO_SUPPORTED"):
    return {"proof_state": state, "final_verdict": verdict}


SRC = "Kommunen gir radgivning. Det er ikke krav om henvisning."


def _review(**kw):
    base = {
        "semantic_assessment": "likely supported",
        "evidence_sufficiency": "EVIDENCE_RELEVANT_BUT_UNRESOLVED",
        "proposed_relation": "SUPPORTED",
        "supporting_span_ids": [0],
        "counter_proof": None,
        "requires_human_review": False,
    }
    base.update(kw)
    return base


def test_confident_reviewer_cannot_flip_accepted_proof():
    # Reviewer says CONTRADICTED with max confidence: no auto flip.
    r = _review(proposed_relation="CONTRADICTED")
    out = arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), r, SRC)
    assert out == "AUTO_SUPPORTED", out


def test_counter_proof_routes_to_review():
    r = _review(counter_proof={
        "span_ids": [10], "target_claim": "contradicts qualification"})
    out = arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), r, SRC)
    assert out == "REVIEW_REQUIRED", out


def test_no_proof_never_upgrades_to_auto():
    for rel in ("SUPPORTED", "CONTRADICTED"):
        r = _review(proposed_relation=rel,
                    evidence_sufficiency="EVIDENCE_SUFFICIENT_FOR_PROOF")
        out = arb.arbitrate(_atom("ENGINE_NO_PROOF"), r, SRC)
        assert out in ("REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"), (rel, out)


def test_unsafe_and_conflict_always_review():
    for state in ("ENGINE_UNSAFE", "ENGINE_CONFLICT"):
        assert arb.arbitrate(_atom(state), _review(), SRC) \
            == "REVIEW_REQUIRED"


def test_unvalid_reviewer_output_ignored():
    bad = _review(supporting_span_ids=[999999])
    ok, errs = arb.validate_reviewer_output(bad, SRC)
    assert not ok and errs
    # Arbitration falls back to engine authority.
    out = arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), bad, SRC)
    assert out == "AUTO_SUPPORTED"


def test_confirm_only_when_no_counter():
    r = _review(requires_human_review=False)
    out = arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), r, SRC)
    assert out == "AUTO_SUPPORTED"


def test_downgrade_to_review_allowed():
    # Reviewer may downgrade an accepted proof to review (spec 8),
    # but still never flip polarity.
    r = _review(requires_human_review=True)
    assert arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), r, SRC) \
        == "REVIEW_REQUIRED"
    r2 = _review(proposed_relation="CONTRADICTED")
    assert arb.arbitrate(_atom("ENGINE_PROOF_ACCEPTED"), r2, SRC) \
        == "AUTO_SUPPORTED"


if __name__ == "__main__":
    test_confident_reviewer_cannot_flip_accepted_proof()
    test_counter_proof_routes_to_review()
    test_no_proof_never_upgrades_to_auto()
    test_unsafe_and_conflict_always_review()
    test_unvalid_reviewer_output_ignored()
    test_confirm_only_when_no_counter()
    test_downgrade_to_review_allowed()
    print("arbitration tests: 6/6 PASS")
