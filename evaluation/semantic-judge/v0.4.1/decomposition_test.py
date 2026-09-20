#!/usr/bin/env python3
"""Run the v0.4 decompose prompt over decomposition-tests.json (44 cases)
and grade atom counts. Resumable: writes v0.4/results/decomposition-run.json
after each case. Judge A via the frozen v0.2/v0.3 transport."""
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
V03 = os.path.join(os.path.dirname(HERE), "v0.3")
V02 = os.path.dirname(V03)
sys.path.insert(0, V02)
sys.path.insert(0, HERE)
import run_semantic_judge as base
import semantic_judge_v041 as sj


def main():
    timeout = 180
    with open(os.path.join(V03, "decomposition-tests.json"),
              encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    out_path = os.path.join(HERE, "results", "decomposition-run.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results = {"meta": {"version": "decomposition-test-v0.4",
                        "prompt_sha256": base.sha256_of(sj.DECOMPOSE_PROMPT),
                        "generated": datetime.now(timezone.utc).isoformat()},
               "results": []}
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            results = json.load(f)
    done_ids = {r["id"] for r in results["results"]}
    home = base.build_home()
    model = base.JUDGES["A"]["model"]
    n_pass = 0
    for case in cases:
        if case["id"] in done_ids:
            n_pass += 1 if next(r for r in results["results"]
                                if r["id"] == case["id"])["pass"] else 0
            continue
        t0 = time.time()
        decomp, status, rc = sj.run_decompose(home, model, case["claim"],
                                              timeout)
        n_atoms = len(decomp["atoms"])
        ok = n_atoms == case["expected_atoms"]
        row = {"id": case["id"], "expected_atoms": case["expected_atoms"],
               "got_atoms": n_atoms, "pass": ok,
               "forbid": case.get("forbid", []),
               "atom_texts": [a["text"] for a in decomp["atoms"]],
               "status": status, "elapsed_s": round(time.time() - t0, 1)}
        results["results"].append(row)
        n_pass += 1 if ok else 0
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        mark = "PASS" if ok else "FAIL"
        print(f"[{row['id']}] {mark} expected={case['expected_atoms']} got={n_atoms} ({status})", flush=True)
    print(f"DECOMPOSITION: {n_pass}/{len(cases)} pass -> {out_path}")
    sys.exit(0 if n_pass == len(cases) else 1)


if __name__ == "__main__":
    main()
