#!/usr/bin/env python3
"""Run the frozen V1.2 judge over model-calibration.json (spec sec 23).
Prompt calibration only: not official validation, not part of any gate.
Writes model-calibration-run.json with per-fixture judge output, expected
labels, and a simple agreement summary.
"""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib_common import write_json
import v1_2_judge as judge

def main():
    with open(os.path.join(HERE, "model-calibration.json"), encoding="utf-8") as f:
        doc = json.load(f)
    rows = []
    ok = 0
    per_dim = {}
    for i, fxitem in enumerate(doc["fixtures"]):
        dim = fxitem["dimension"]
        res = judge.semantic_verdict(
            dim, fxitem["case_context"], fxitem["gold_criterion"],
            fxitem["sut_answer"])
        expected = fxitem["expected"]
        if dim == "uncertainty":
            got = {k: res[k] for k in ("requirement_applicable", "verdict")}
            match = (res["requirement_applicable"] == expected["requirement_applicable"]
                     and res["verdict"] == expected["verdict"])
            exp_disp = f'{expected["requirement_applicable"]}/{expected["verdict"]}'
        else:
            got = {"verdict": res["verdict"]}
            match = res["verdict"] == expected
            exp_disp = expected
        ok += match
        stat = per_dim.setdefault(dim, {"n": 0, "match": 0})
        stat["n"] += 1
        stat["match"] += match
        rows.append({
            "id": fxitem["id"],
            "dimension": dim,
            "expected": expected,
            "judge": got,
            "evidence_spans": res["evidence_spans"],
            "note": res["note"],
            "meta_ok": res["meta"]["ok"],
            "attempts": res["meta"]["attempts"],
            "match": match,
        })
        print(f'{i + 1}/{len(doc["fixtures"])} {fxitem["id"]}: '
              f'expected {exp_disp} vs got '
              f'{got.get("requirement_applicable", "")}/{got.get("verdict", "")}'
              + ("" if match else "  <-- MISMATCH"), flush=True)
    out = {
        "set": "MODEL_CALIBRATION_V1_2",
        "model": judge.MODEL,
        "prompt_sha256": judge.prompt_hash(),
        "fixture_count": len(rows),
        "agreement": f"{ok}/{len(rows)}",
        "agreement_rate": round(ok / len(rows), 4),
        "per_dimension": per_dim,
        "classification": "PROMPT_CALIBRATION_ONLY_NOT_VALIDATION",
        "rows": rows,
    }
    write_json("model-calibration-run.json", out)
    print(f"RESULT model calibration: {out['agreement']} = {out['agreement_rate']}")

if __name__ == "__main__":
    main()
