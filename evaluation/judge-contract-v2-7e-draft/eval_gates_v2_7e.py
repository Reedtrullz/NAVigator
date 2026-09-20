#!/usr/bin/env python3
"""V2.7E two-pass agreement + preregistered gate evaluation.

Usage:
  eval_gates_v2_7e.py <set.json> <pass1.json> <pass2.json> <out.json>
  eval_gates_v2_7e.py --selfcheck

Gates (TASK-SPEC-DRAFT.md, pre-adjudication):
  overall >= 0.95
  zero disagreements on contradictory_limitation / unclear_prose /
  self_retracted_limitation rows
"""
import json
import sys

ZERO_GATE_TAGS = {
    "contradictory_limitation",
    "unclear_prose",
    "self_retracted_limitation",
}
OVERALL_GATE = 0.95


def evaluate(set_path, pass1_path, pass2_path, out_path):
    fixtures = {f["id"]: f for f in json.load(open(set_path))["fixtures"]}
    p1 = json.load(open(pass1_path))
    p2 = json.load(open(pass2_path))
    l1 = {r["id"]: r["verdict"] for r in p1["labels"]}
    l2 = {r["id"]: r["verdict"] for r in p2["labels"]}
    if set(l1) != set(fixtures) or set(l2) != set(fixtures):
        missing = set(fixtures) - (set(l1) & set(l2))
        sys.exit(f"PASS_COVERAGE_ERROR: labels missing for {sorted(missing)}")

    disagreements = []
    per_tag = {}
    for fid, fx in fixtures.items():
        agree = l1[fid] == l2[fid]
        tag = fx["tag"]
        row = per_tag.setdefault(tag, {"n": 0, "agree": 0})
        row["n"] += 1
        if agree:
            row["agree"] += 1
        else:
            disagreements.append(
                {"id": fid, "tag": tag,
                 "pass1_verdict": l1[fid], "pass2_verdict": l2[fid]}
            )

    n = len(fixtures)
    a = n - len(disagreements)
    overall = a / n
    zero_gate_disagreements = [
        d for d in disagreements if d["tag"] in ZERO_GATE_TAGS
    ]
    gates = {
        "overall_ge_0_95": overall >= OVERALL_GATE,
        "zero_gate_boundary_rows": len(zero_gate_disagreements) == 0,
    }
    result = {
        "task_id": p1["task_id"],
        "stage": "raw_agreement_pre_adjudication",
        "pass1_file": pass1_path,
        "pass2_file": pass2_path,
        "total": n,
        "agreements": a,
        "overall_agreement": overall,
        "per_tag": {
            t: {**r, "rate": r["agree"] / r["n"]}
            for t, r in sorted(per_tag.items())
        },
        "disagreements": disagreements,
        "zero_gate_disagreements": zero_gate_disagreements,
        "gates": gates,
        "gates_passed": all(gates.values()),
    }
    json.dump(result, open(out_path, "w"), indent=2, ensure_ascii=True)
    print(("GATES_PASSED" if result["gates_passed"] else "GATES_FAILED"),
          f"{a}/{n} = {overall:.4f}")
    return result


def selfcheck():
    import tempfile, os
    mk = tempfile.mkdtemp()
    ids = [f"V27E-SETA-{i:02d}" for i in range(1, 33)]
    tags = (["clear_limitation"] * 8 + ["absent_limitation"] * 8
            + ["no_requirement"] * 7 + ["partial_limitation"] * 3
            + ["non_assertion_ok"] * 3)
    tags += ["contradictory_limitation", "unclear_prose",
             "self_retracted_limitation"]  # -> 32
    set_d = {"fixtures": [{"id": i, "tag": t} for i, t in zip(ids, tags)]}
    def dump(name, obj):
        p = os.path.join(mk, name)
        json.dump(obj, open(p, "w"))
        return p
    sp = dump("set.json", set_d)

    # PASS case: identical passes
    labs = [{"id": i, "verdict": "SATISFIED"} for i in ids]
    r = evaluate(sp, dump("p1a.json", {"task_id": "T", "labels": labs}),
                 dump("p2a.json", {"task_id": "T", "labels": labs}),
                 os.path.join(mk, "out-a.json"))
    assert r["gates_passed"] and r["overall_agreement"] == 1.0

    # FAIL case: PARTIAL<->UNRESOLVED on the contradictory boundary row
    labs1 = [{"id": i, "verdict": "PARTIAL" if i == "V27E-SETA-30"
              else "SATISFIED"} for i in ids]
    labs2 = [{"id": i, "verdict": "SATISFIED" if i == "V27E-SETA-29"
              else ("UNRESOLVED" if i == "V27E-SETA-30" else "SATISFIED")}
             for i in ids]
    r = evaluate(sp, dump("p1b.json", {"task_id": "T", "labels": labs1}),
                 dump("p2b.json", {"task_id": "T", "labels": labs2}),
                 os.path.join(mk, "out-b.json"))
    assert not r["gates_passed"]
    assert r["zero_gate_disagreements"][0]["tag"] == "contradictory_limitation"
    print("selfcheck OK")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selfcheck":
        selfcheck()
    elif len(sys.argv) == 5:
        evaluate(*sys.argv[1:])
    else:
        sys.exit(__doc__)
