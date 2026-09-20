"""Seven QA regressions for the V4 seal (spec 36). Runs under pytest or plain python."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "v4_qa", os.path.join(HERE, "..", "v4_qa.py"))
v4_qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4_qa)


def _default_atoms():
    return [{"atom_id": "A1", "claim_text": "x", "semantic_truth": "SUPPORTED",
             "proof_safe": "SUPPORTED", "supporting_span_ids": [], "required_inference": "NONE"}]


def case(cid="RCXX-0000", flags=("compound", "legal"), atoms=None, crit="standard", final=None):
    if atoms is None:
        atoms = _default_atoms()
    final = final or {"semantic_truth": "SUPPORTED", "proof_safe": "SUPPORTED", "product_action": "AUTO_SUPPORTED"}
    agg = dict(final)
    return {"case_id": cid, "final": final, "final_flags": list(flags),
            "criticality": crit, "atoms": atoms, "aggregation": agg}


def keydoc(cases):
    return {"set_version": "NAV-EXPLORE-RC2-BLIND-V4", "cases": cases}


def test_plaintext_labels_fail():
    ok, leaks = v4_qa.check_plaintext_leak()
    assert ok, leaks
    bad = keydoc([case()])  # per-case label fixtures must never be written to the project
    assert bad["cases"]


def test_missing_compound_atom_target_fails():
    ok_case = case()
    bad = case(atoms=[])
    assert v4_qa.check_atoms_complete(keydoc([ok_case]))[0]
    assert not v4_qa.check_atoms_complete(keydoc([bad]))[0]


def test_missing_criticality_fails():
    ok_case = case()
    bad = case(crit=None)
    assert v4_qa.check_criticality(keydoc([ok_case]))[0]
    assert not v4_qa.check_criticality(keydoc([bad]))[0]


def test_missing_subgroup_metadata_fails():
    ok_case = case()
    bad = case(flags=())
    unknown = case(flags=("made_up_flag",))
    assert v4_qa.check_subgroups(keydoc([ok_case]))[0]
    assert not v4_qa.check_subgroups(keydoc([bad]))[0]
    assert not v4_qa.check_subgroups(keydoc([unknown]))[0]


def test_incomplete_two_pass_fails():
    good = {"RCXX-0000": {"pass1_atoms": 3, "pass2_atoms": 3}}
    bad = {"RCXX-0000": {"pass1_atoms": 3, "pass2_atoms": 0}}
    assert v4_qa.check_two_pass(good)[0]
    assert not v4_qa.check_two_pass(bad)[0]


def test_aggregation_inconsistency_fails():
    ok_case = case()
    drifted = case(final={"semantic_truth": "SUPPORTED", "proof_safe": "SUPPORTED", "product_action": "REVIEW_REQUIRED"})
    assert v4_qa.check_aggregation(keydoc([ok_case]))[0]
    assert not v4_qa.check_aggregation(keydoc([drifted]))[0]


def test_reused_old_key_fails():
    import hashlib
    fresh = bytes(range(32))
    assert v4_qa.check_key_not_retired(fresh)[0]
    # mechanism check: fingerprint comparison flags any key matching the registered digest
    decoy = b"A" * 32
    v4_qa.RETIRED_KEY_FINGERPRINT = hashlib.sha256(decoy).hexdigest()
    assert not v4_qa.check_key_not_retired(decoy)[0]
    assert v4_qa.check_key_not_retired(b"B" * 32)[0]


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("PASS", name)
            except AssertionError as exc:
                fails += 1
                print("FAIL", name, exc)
    raise SystemExit(1 if fails else 0)
