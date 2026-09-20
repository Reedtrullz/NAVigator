#!/usr/bin/env python3
"""V1.6B stability screen (contract pipeline-contract-v1-6b.json).

Eligibility is fail-closed: refuses to run unless the candidate passed ALL
one-shot floors. Subset = first 30 EXPECTED_SEMANTIC_RESIDUAL fixtures by
frozen fixture ID order, 3 runs each. No majority-vote repair: the one-shot
screening result remains authoritative.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3"))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
sys.path.insert(0, A3)
sys.path.insert(0, V14)

from boundary_preclassifier import classify  # noqa: E402
import judge_core_v1_4 as J  # noqa: E402

NON_EVALUABLE = {"QUOTED_ONLY", "HYPOTHETICAL_ONLY", "NEGATED", "SELF_RETRACTED"}
RUNS = 3


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def save(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def pipeline_row(fx, g):
    """One pipeline pass for a fixture; returns (stage, verdict, extra)."""
    cs = fx.get("criterion_struct") or {}
    req = bool(cs.get("required_limitations"))
    prohib = bool(cs.get("prohibited_conclusions"))
    if fx["dimension"] == "required_uncertainty":
        if not req and not prohib:
            return "DETERMINISTIC_PRE_A3", g["verdict"], {}
        if req and not prohib:
            out = classify(fx["sut"], cs)
            unc = out["uncertainty_behavior"]
            if not unc["abstained"] and unc.get("label") != "ABSTAIN":
                verdict = {"EXPLICIT_LIMITATION": "SATISFIED",
                           "PARTIAL_LIMITATION": "PARTIAL", "HEDGE": "PARTIAL",
                           "CONTRADICTORY_LIMITATION": "PARTIAL",
                           "OVERCONFIDENT_ASSERTION": "VIOLATED",
                           "NONE": "UNRESOLVED",
                           "UNRESOLVED": "UNRESOLVED"}[unc["label"]]
                return "A3_DERIVED", verdict, {}
            tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
            return judge_stage(tj, fx)
    elif fx["dimension"] == "route_correctness":
        out = classify(fx["sut"], None)
        rc = out["route_commitment"]
        if not (rc["abstained"] or rc.get("label") == "ABSTAIN"):
            label = rc["label"]
            if label in NON_EVALUABLE:
                return "A3_DERIVED", "UNRESOLVED", {}
            if label not in ("ASSERTED", "HEDGED_ASSERTION"):
                return "A3_DERIVED", "UNRESOLVED", {}
    tj = J.call_judge(fx["dimension"], fx["ctx"], fx["crit"], fx["sut"])
    return judge_stage(tj, fx)


def judge_stage(t, fx):
    if t.get("status") != "OK":
        return "JUDGE", None, {"status": t.get("status"),
                               "finish_reason": t.get("finish_reason"),
                               "error": t.get("error")}
    res = t["result"]
    ev_ok = all(J.norm(s) in J.norm(fx["sut"])
                for s in res.get("evidence_spans", []))
    return "JUDGE", res.get("verdict"), {"status": "OK",
                                         "verdict": res.get("verdict"),
                                         "evidence_valid": ev_ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True,
                    choices=["longcat-2-0-free", "mimo-v2-5-pro"])
    args = ap.parse_args()
    model = {"longcat-2-0-free": "command-code/meituan/LongCat-2.0:free",
             "mimo-v2-5-pro": "command-code/xiaomi/mimo-v2.5-pro"}[args.candidate]

    one_shot = json.load(open(os.path.join(
        HERE, f"screening-results-{args.candidate}.json")))
    if not one_shot.get("gates_all_pass"):
        sys.exit(f"ELIGIBILITY_FAIL: {args.candidate} did not pass all "
                 "one-shot floors; stability screen not permitted")

    fixtures = json.load(open(os.path.join(
        HERE, "screening-fixtures.json")))["fixtures"]
    gdoc = json.load(open(os.path.join(HERE, "screening-gold.json")))
    gold = {g["fixture_id"]: g["pass1"] for g in gdoc["gold"]}
    fixture_sha = sha(os.path.join(HERE, "screening-fixtures.json"))
    fxh = json.load(open(os.path.join(HERE, "screening-fixture-hashes.json")))
    canonical = lambda o: json.dumps(o, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")
    for f in fixtures:
        assert fxh["fixture_hashes"].get(f["id"]) == \
            hashlib.sha256(canonical(f)).hexdigest(), f"drift {f['id']}"
    engine_sha = sha(os.path.join(A3, "boundary_preclassifier.py"))
    assert engine_sha == \
        "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b"

    residual = sorted((f for f in fixtures
                       if f.get("stratum", "EXPECTED_SEMANTIC_RESIDUAL")
                       == "EXPECTED_SEMANTIC_RESIDUAL"),
                      key=lambda f: f["id"])
    subset = residual[:30]
    ck_path = os.path.join(HERE, f"stability-checkpoint-{args.candidate}.json")
    done = {}
    if os.path.exists(ck_path):
        ck = json.load(open(ck_path))
        assert ck.get("model") == model and ck.get("fixtures_sha256") == fixture_sha
        done = ck.get("completed", {})

    J.MODEL = model
    for fx in subset:
        g = gold[fx["id"]]
        for run in range(1, RUNS + 1):
            key = f"{fx['id']}#{run}"
            if key in done:
                continue
            stage, verdict, extra = pipeline_row(fx, g)
            done[key] = {"id": fx["id"], "run": run, "dimension": fx["dimension"],
                         "stage": stage, "verdict": verdict,
                         "verdict_correct": verdict == g["verdict"], **extra}
            print(f"{key} [{stage}] {verdict}", flush=True)
            save(ck_path, {"candidate_key": args.candidate, "model": model,
                           "fixtures_sha256": fixture_sha,
                           "subset_ids": [f["id"] for f in subset],
                           "completed": done})
    save(ck_path, {"candidate_key": args.candidate, "model": model,
                   "fixtures_sha256": fixture_sha,
                   "subset_ids": [f["id"] for f in subset],
                   "completed": done})
    print(f"STABILITY RUNS DONE n={len(subset)}x{RUNS}", flush=True)


if __name__ == "__main__":
    main()
