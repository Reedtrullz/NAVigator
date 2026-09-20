#!/usr/bin/env python3
"""V2 stability screen (frozen contract: only for the top qualifying candidate).

Subset: first 8 fixtures per family in frozen ID order (24 total), 5 runs
each. Fail-closed eligibility: refuses to run unless the candidate passed
ALL one-shot gates in screening-results-{candidate}.json. Modal stability:
a fixture is stable iff all 5 runs produced the same verdict; overall and
per-family rates must both be >= 0.95. No majority-vote repair.
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

CONTRACT_SHA = "d4469ecea0ffaeef04bbbf8d5aaf32a920aa2b27ec5aa9402b7903fd531c7bcd"
GOLD_SHA = "2b348e9f12603d9890e6ccb642fc245db24fc850e62db1ab91554cfc5ee2c30d"
A3_SHA = "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b"
FAMILIES = [("a", "family-a-fixtures.json"),
            ("b", "family-b-fixtures.json"),
            ("c", "family-c-fixtures.json")]
EXPL_ROWS = {"EXPLICIT_LIMITATION": "SATISFIED", "PARTIAL_LIMITATION": "PARTIAL",
             "HEDGE": "PARTIAL", "CONTRADICTORY_LIMITATION": "PARTIAL",
             "OVERCONFIDENT_ASSERTION": "VIOLATED", "NONE": "UNRESOLVED",
             "UNRESOLVED": "UNRESOLVED"}
RUNS = 5
SUBSET_PER_FAMILY = 8
STABILITY_MIN = 0.95


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def save(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True,
                    choices=["longcat-2-0-free", "mimo-v2-5-pro"])
    args = ap.parse_args()
    model = {"longcat-2-0-free": "command-code/meituan/LongCat-2.0:free",
             "mimo-v2-5-pro": "command-code/xiaomi/mimo-v2.5-pro"}[args.candidate]

    one_shot = json.load(open(os.path.join(
        HERE, "screening-results-" + args.candidate + ".json")))
    if not one_shot.get("gates_all_pass"):
        sys.exit("ELIGIBILITY_FAIL: " + args.candidate
                 + " did not pass all one-shot gates; stability not permitted")

    assert sha(os.path.join(HERE, "screening-contract-v2.json")) == CONTRACT_SHA
    gdoc = json.load(open(os.path.join(HERE, "judge-selection-gold.json")))
    gold_canon = json.dumps({k: v for k, v in gdoc.items() if k != "gold_sha256"},
                            sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False).encode("utf-8")
    assert hashlib.sha256(gold_canon).hexdigest() == GOLD_SHA
    assert sha(os.path.join(A3, "boundary_preclassifier.py")) == A3_SHA
    gold = {g["fixture_id"]: g for g in gdoc["gold"]}
    fxh = json.load(open(os.path.join(HERE, "fixture-hashes.json")))["fixture_hashes"]

    subset = []
    for fam, fname in FAMILIES:
        rows = json.load(open(os.path.join(HERE, fname)))["fixtures"]
        for f in rows:
            canon = json.dumps(f, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False).encode("utf-8")
            assert fxh.get(f["id"]) == hashlib.sha256(canon).hexdigest(), f["id"]
        subset.extend(rows[:SUBSET_PER_FAMILY])
    assert len(subset) == 24

    ck_path = os.path.join(HERE, "stability-checkpoint-" + args.candidate + ".json")
    done = {}
    if os.path.exists(ck_path):
        ck = json.load(open(ck_path))
        if ck.get("model") != model:
            raise RuntimeError("checkpoint/model mismatch")
        done = ck.get("completed", {})
        print("RESUME stability " + args.candidate + ": "
              + str(len(done)) + " cells", flush=True)

    J.MODEL = model
    for fx in subset:
        g = gold[fx["id"]]
        for run in range(1, RUNS + 1):
            key = fx["id"] + "#" + str(run)
            if key in done:
                continue
            row = pipeline_row(fx, g)
            done[key] = {"id": fx["id"], "family": g["family"],
                         "dimension": g["dimension"], "run": run, **row}
            print(key + " [" + row["stage"] + "] " + str(row.get("verdict",
                  row.get("status"))), flush=True)
            save(ck_path, {"candidate_key": args.candidate, "model": model,
                           "subset_ids": [f["id"] for f in subset],
                           "completed": done})
    save(ck_path, {"candidate_key": args.candidate, "model": model,
                   "subset_ids": [f["id"] for f in subset], "completed": done})

    per_fx = {}
    for key, cell in done.items():
        per_fx.setdefault(cell["id"], []).append(cell.get("verdict"))
    fam_of = {g["fixture_id"]: g["family"] for g in gdoc["gold"]}
    stable = {fid: (len(set(v)) == 1 and None not in v and len(v) == RUNS)
              for fid, v in per_fx.items()}
    overall = sum(1 for v in stable.values() if v) / len(stable)
    per_family = {}
    for fam, _ in FAMILIES:
        ids = [fid for fid in stable if fam_of[fid] == fam]
        per_family[fam] = sum(1 for fid in ids if stable[fid]) / len(ids)
    results = {"artifact": "JUDGE SELECTION V2 STABILITY RESULTS",
               "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2-SUBSKILL-SCREENING",
               "candidate_key": args.candidate, "model": model,
               "runs_per_fixture": RUNS, "n_fixtures": len(subset),
               "stability_definition": "fixture stable iff all 5 runs identical verdict",
               "overall_modal_stability": overall,
               "per_family_modal_stability": per_family,
               "stability_min": STABILITY_MIN,
               "stability_pass": overall >= STABILITY_MIN
               and all(v >= STABILITY_MIN for v in per_family.values()),
               "fixture_stability": stable}
    save(os.path.join(HERE, "stability-results-" + args.candidate + ".json"),
         results)
    print("STABILITY DONE overall=" + str(round(overall, 4))
          + " per_family=" + json.dumps(per_family), flush=True)


def pipeline_row(fx, g):
    if g["family"] in ("a", "c"):
        tj = J.call_judge(g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
        return judge_stage(tj, fx)
    mode = fx["mode"]
    cs = fx.get("criterion_struct") or {}
    if (mode == "EXPLICIT_LIMITATION" and bool(cs.get("required_limitations"))
            and not bool(cs.get("prohibited_conclusions"))):
        out = classify(fx["sut"], cs)
        unc = out["uncertainty_behavior"]
        if not unc["abstained"] and unc.get("label") != "ABSTAIN":
            return {"stage": "A3_DERIVED", "verdict": EXPL_ROWS[unc["label"]]}
    tj = J.call_judge(g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
    return judge_stage(tj, fx)


def judge_stage(t, fx):
    if t.get("status") != "OK":
        return {"stage": "JUDGE", "status": t.get("status"),
                "error": t.get("error")}
    res = t["result"]
    ev_ok = all(J.norm(s) in J.norm(fx["sut"])
                for s in res.get("evidence_spans", []))
    return {"stage": "JUDGE", "status": "OK", "verdict": res.get("verdict"),
            "evidence_valid": ev_ok}


if __name__ == "__main__":
    main()
