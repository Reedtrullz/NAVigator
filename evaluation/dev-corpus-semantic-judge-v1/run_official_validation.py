#!/usr/bin/env python3
"""Official one-shot validation mot frozen contract og frosset gold."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantic_judge as sj


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "judge-validation-fixtures.json"), encoding="utf-8") as f:
        fixtures = json.load(f)["fixtures"]
    with open(os.path.join(here, "judge-validation-gold.json"), encoding="utf-8") as f:
        gold = json.load(f)
    with open(os.path.join(here, "semantic-judge-contract-v1.json"), encoding="utf-8") as f:
        contract = json.load(f)

    prompt_sha = sj.prompt_hash()
    if prompt_sha != contract["prompt_sha256"]:
        print(f"FATAL: prompt sha {prompt_sha} != frozen {contract['prompt_sha256']}")
        sys.exit(2)

    rows = []
    for i, fx in enumerate(fixtures):
        g = gold[fx["id"]]
        res = sj.semantic_verdict(
            fx["dimension"], fx["case_context"], fx["gold_criterion"], fx["sut_answer"])
        v = res["verdict"]
        rows.append({
            "id": fx["id"], "dimension": fx["dimension"],
            "gold": g["gold"], "actual": v, "correct": v == g["gold"],
            "evidence_spans": res.get("evidence_spans", []),
            "note": res.get("note"), "ok": res.get("meta", {}).get("ok"),
        })
        print(f"{i+1}/{len(fixtures)} {fx['id']}: {v} vs gold {g['gold']}"
              f" {'OK' if v == g['gold'] else 'MISS'}", flush=True)

    from collections import defaultdict
    dim = defaultdict(lambda: {"n": 0, "correct": 0})
    for r in rows:
        dim[r["dimension"]]["n"] += 1
        dim[r["dimension"]]["correct"] += r["correct"]
    total = len(rows)
    correct = sum(r["correct"] for r in rows)
    unresolved = sum(1 for r in rows if r["actual"] == "UNRESOLVED")

    # Safety: FN = gold says condition present / claim present but judge says otherwise
    critical_fn = sum(1 for r in rows if r["dimension"] == "critical_condition"
                      and r["gold"] == "TRIGGERED" and r["actual"] != "TRIGGERED")
    forbidden_fn = sum(1 for r in rows if r["dimension"] == "forbidden_claim"
                       and r["gold"] == "PRESENT" and r["actual"] != "PRESENT")

    injection_ids = {"FC-V14", "FC-V17", "RE-V15", "UN-V13"}
    inj_rows = [r for r in rows if r["id"] in injection_ids]
    inj_ok = all(r["correct"] for r in inj_rows)

    result = {
        "contract_sha256_prefix": contract["prompt_sha256"][:16],
        "fixture_set": "judge-validation-fixtures.json",
        "total": total, "correct": correct,
        "overall_accuracy": round(correct / total, 4),
        "per_dimension": {k: {"n": v["n"], "correct": v["correct"],
                              "accuracy": round(v["correct"] / v["n"], 4)}
                          for k, v in sorted(dim.items())},
        "unresolved": unresolved,
        "unresolved_rate": round(unresolved / total, 4),
        "critical_condition_FN": critical_fn,
        "forbidden_claim_FN": forbidden_fn,
        "injection_fixtures": len(inj_rows),
        "injection_all_correct": inj_ok,
        "rows": rows,
    }
    with open(os.path.join(here, "official-validation-results.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"overall: {correct}/{total} = {result['overall_accuracy']}")
    print(f"critical FN: {critical_fn} | forbidden FN: {forbidden_fn} | unresolved: {unresolved}/{total}")
    print(f"injection all correct: {inj_ok}")


if __name__ == "__main__":
    main()
