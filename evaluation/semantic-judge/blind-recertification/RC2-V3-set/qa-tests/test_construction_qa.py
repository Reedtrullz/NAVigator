#!/usr/bin/env python3
"""Regression tests for the V2 construction bug (spec 43).

Each scenario builds a pool that PASSES pool-wide but must FAIL on a CORE-only
gate. The runner asserts construction_qa returns failures and that the CLI
exits non-zero. Run: python3 test_construction_qa.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.join(HERE, "..", "construction_qa.py")
sys.path.insert(0, os.path.dirname(QA))
import construction_qa as cqa  # noqa: E402


def mk(cid, sem, proof, prod, flags=(), adjudicated=False):
    c = {
        "case_id": cid, "claim": "x", "sources": [], "flags": list(flags),
        "pass1": {"semantic_truth": sem, "proof_safe": proof, "product_action": prod},
        "pass2": {"semantic_truth": sem, "proof_safe": proof, "product_action": prod},
    }
    if adjudicated:
        c["final"] = {"semantic_truth": sem, "proof_safe": proof, "product_action": prod}
    return c


def core_data(core_cases, reserve_cases=()):
    return {
        "candidates": list(core_cases) + list(reserve_cases),
        "selection": {"core": [c["case_id"] for c in core_cases],
                      "reserve": [c["case_id"] for c in reserve_cases]},
        "fidelity": {"failures": 0},
        "novelty": {"pass": True},
    }


def balanced_core(n=160, flags_fn=None, zero_insufficiency=False):
    classes = ["SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
    products = ["AUTO_SUPPORTED", "AUTO_CONTRADICTED", "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"]
    cases = []
    for i in range(n):
        sem = "SUPPORTED" if zero_insufficiency else classes[i % 4]
        prod = "AUTO_SUPPORTED" if zero_insufficiency else products[i % 4]
        flags = flags_fn(i) if flags_fn else []
        proof = sem if sem != "PARTIALLY_SUPPORTED" else "SUPPORTED"
        cases.append(mk(f"T{i:04d}", sem, proof, prod, flags))
    return cases


def flags_meeting_minima(i):
    """Deterministic assignment meeting every CORE flag minimum at n=160."""
    fs = []
    if i % 3 == 0:
        fs.append("compound")          # 54 >= 50
    if i % 5 == 0:
        fs.append("multi_span")        # 32 >= 30
    if i % 5 == 1:
        fs.append("numeric")           # 32 >= 30
    if i % 5 == 2:
        fs.append("temporal")          # 32 >= 30
    if i % 5 == 3:
        fs.append("actor")             # 32 >= 30
    if i % 4 == 1:
        fs.append("modality")          # 40 >= 30
    if i % 5 == 4:
        fs.append("cond_exc")          # 32 >= 30
    if i % 8 == 0:
        fs.append("safety")            # 20 >= 20
    if i % 5 in (0, 1):
        fs.append("legal")             # 64 >= 30
    if i % 8 == 2:
        fs.append("locality")          # 20 >= 20
    if i % 8 == 3:
        fs.append("age_legal")         # 20 >= 20
    return fs


def flip_pass2(c):
    """Guaranteed-different, vocabulary-valid pass2; final stays pass1."""
    p2 = c["pass2"]
    p2["semantic_truth"] = "SUPPORTED" if c["pass1"]["semantic_truth"] != "SUPPORTED" else "CONTRADICTED"
    p2["proof_safe"] = "SUPPORTED" if c["pass1"]["proof_safe"] != "SUPPORTED" else "CONTRADICTED"
    p2["product_action"] = "AUTO_SUPPORTED" if c["pass1"]["product_action"] != "AUTO_SUPPORTED" else "AUTO_CONTRADICTED"
    c["final"] = dict(c["pass1"])


def scenario_pool_quota_cannot_satisfy_core():
    """Pool has 40 insufficiency; CORE has 0 -> FAIL (V2 bug)."""
    core = balanced_core(160, flags_meeting_minima, zero_insufficiency=True)
    reserve = [mk(f"R{i:04d}", "INSUFFICIENT_EVIDENCE", "INSUFFICIENT_EVIDENCE",
                  "ABSTAIN_INSUFFICIENT") for i in range(40)]
    pool_sem = sum(1 for c in core + reserve
                   if c["pass1"]["semantic_truth"] == "INSUFFICIENT_EVIDENCE")
    assert pool_sem == 40, "test setup: pool should contain 40 insufficiency"
    fails, _ = cqa.run_qa(core_data(core, reserve))
    assert any("genuine insufficiency" in f for f in fails), fails


def scenario_zero_abstain_product():
    """CORE has no ABSTAIN_INSUFFICIENT -> product gate FAIL."""
    core = balanced_core(160, flags_meeting_minima)
    for c in core:
        c["pass1"]["product_action"] = c["pass2"]["product_action"] = "AUTO_SUPPORTED"
    fails, _ = cqa.run_qa(core_data(core))
    assert any("ABSTAIN_INSUFFICIENT" in f for f in fails), fails


def scenario_multi_span_18():
    """CORE multi-span 18 (pool 44) < 30 -> FAIL."""
    def few_flags(i):
        fs = flags_meeting_minima(i)
        return [f for f in fs if f != "multi_span"] if i >= 18 else fs
    core = balanced_core(160, few_flags)
    reserve = [mk(f"R{i:04d}", "SUPPORTED", "SUPPORTED", "AUTO_SUPPORTED", ["multi_span"])
               for i in range(26)]
    fails, _ = cqa.run_qa(core_data(core, reserve))
    assert any("multi_span" in f for f in fails), fails


def scenario_agreement_078():
    """CORE agreement 0.78 on all three slots -> FAIL."""
    core = balanced_core(160, flags_meeting_minima)
    n_flip = int(0.22 * 160)
    for c in core[:n_flip]:
        flip_pass2(c)
    fails, _ = cqa.run_qa(core_data(core))
    for slot in ("semantic_truth", "proof_safe", "product_action"):
        assert any(f"agreement {slot}" in f for f in fails), (slot, fails)


def scenario_single_pass():
    """A candidate lacking pass2 fails completeness."""
    core = balanced_core(160, flags_meeting_minima)
    del core[0]["pass2"]
    fails, _ = cqa.run_qa(core_data(core))
    assert any("single-pass" in f for f in fails), fails


def scenario_adjudication_over_35():
    """CORE adjudication rate 0.40 > 0.35 -> FAIL."""
    core = balanced_core(160, flags_meeting_minima)
    for c in core[:64]:
        flip_pass2(c)
    fails, _ = cqa.run_qa(core_data(core))
    assert any("adjudication rate" in f for f in fails), fails


def scenario_unresolved_dispute():
    """Disagreement without final labels -> unresolved dispute FAIL."""
    core = balanced_core(160, flags_meeting_minima)
    core[0]["pass2"]["semantic_truth"] = "CONTRADICTED"
    fails, _ = cqa.run_qa(core_data(core))
    assert any("unresolved dispute" in f for f in fails), fails


def cli_exits_nonzero_on_failure():
    """End-to-end: failing construction.json must exit non-zero from CLI."""
    core = balanced_core(160, flags_meeting_minima, zero_insufficiency=True)
    path = os.path.join(HERE, ".tmp-fail.json")
    with open(path, "w") as f:
        json.dump(core_data(core), f)
    try:
        r = subprocess.run([sys.executable, QA, path], capture_output=True, text=True)
        assert r.returncode != 0, "CLI must exit non-zero when a hard CORE gate fails"
        assert "QA_FAILED" in r.stdout
    finally:
        os.unlink(path)


def cli_exits_zero_when_all_pass():
    """Happy path: fully compliant CORE passes (guards against always-fail)."""
    core = balanced_core(160, flags_meeting_minima)
    fails, _ = cqa.run_qa(core_data(core))
    assert fails == [], fails


SCENARIOS = [
    ("pool-quota-cannot-satisfy-core", scenario_pool_quota_cannot_satisfy_core),
    ("zero-abstain-product", scenario_zero_abstain_product),
    ("multi-span-18-of-30", scenario_multi_span_18),
    ("agreement-0.78", scenario_agreement_078),
    ("single-pass-completeness", scenario_single_pass),
    ("adjudication-over-35", scenario_adjudication_over_35),
    ("unresolved-dispute", scenario_unresolved_dispute),
    ("cli-nonzero-on-failure", cli_exits_nonzero_on_failure),
    ("cli-zero-when-clean", cli_exits_zero_when_all_pass),
]


def main():
    failures = 0
    for name, fn in SCENARIOS:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {name}: {e}")
    if failures:
        print(f"{failures} scenario(s) failed")
        return 1
    print("ALL CONSTRUCTION-QA REGRESSION SCENARIOS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
