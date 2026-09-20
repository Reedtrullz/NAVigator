#!/usr/bin/env python3
"""A/B-dommer-sammenligning + fusion-analyse pa kalibrering (run 1)."""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def rows_of(name):
    res = load(name)
    return {x["id"]: x for x in res["results"] if x.get("run", 1) == 1 and x["status"] == "ok"}


def main():
    A = {k: v["response"] for k, v in rows_of("judge-results-calibration-judge-a-gpt-5.5-v0.2.json").items()}
    B = {k: v["response"] for k, v in rows_of("judge-results-calibration-judge-b-deepseek-v4-flash-v0.2.json").items()}
    exp = load("expected-results.json")["expected"]
    both = sorted(set(A) & set(B))
    groups = Counter()
    disagreements = []
    abcd = Counter()
    for c in both:
        ea = A[c]["verdict"] == exp[c]["verdict"]
        eb = B[c]["verdict"] == exp[c]["verdict"]
        if ea and eb:
            abcd["A"] += 1
        elif ea and not eb:
            abcd["C"] += 1
        elif eb and not ea:
            abcd["B"] += 1
        else:
            abcd["D"] += 1
        if A[c]["verdict"] != B[c]["verdict"]:
            disagreements.append({
                "id": c, "expected": exp[c]["verdict"],
                "A": A[c]["verdict"], "B": B[c]["verdict"],
                "A_conf": A[c].get("confidence"), "B_conf": B[c].get("confidence"),
            })
            if ea and not eb:
                groups["A_right_B_wrong"] += 1
            elif eb and not ea:
                groups["B_right_A_wrong"] += 1
            else:
                groups["both_wrong"] += 1
    agree = len(both) - len(disagreements)
    # fusion proposal: hard binary gate — CONTRADICTED by either judge blocks SUPPORTED
    fusion_fp = 0
    unsup = 0
    for c in both:
        e = exp[c]["verdict"]
        if e == "SUPPORTED":
            continue
        unsup += 1
        # candidate accepted only if both judges say SUPPORTED
        if A[c]["verdict"] == "SUPPORTED" and B[c]["verdict"] == "SUPPORTED":
            fusion_fp += 1
    out = {
        "meta": {"set": "calibration", "version": "semantic-judge-v0.2",
                 "A_model": "gpt-5.5", "B_model": "deepseek/deepseek-v4-flash"},
        "n_both": len(both),
        "verdict_agreement": agree,
        "verdict_agreement_rate": round(agree / len(both), 4),
        "A_correct": sum(1 for c in both if A[c]["verdict"] == exp[c]["verdict"]),
        "B_correct": sum(1 for c in both if B[c]["verdict"] == exp[c]["verdict"]),
        "abcd_groups": dict(abcd),
        "disagreement_groups": dict(groups),
        "disagreements": disagreements,
        "fusion_both_must_support": {
            "description": "SUPPORTED krever at begge dommere sier SUPPORTED",
            "unsupported_total": unsup,
            "fusion_fp": fusion_fp,
            "fusion_fp_rate": round(fusion_fp / unsup, 4) if unsup else None,
        },
    }
    path = os.path.join(HERE, "comparison-calibration-v0.2.json")
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE", path)
    print(json.dumps({k: v for k, v in out.items() if k != "disagreements"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
