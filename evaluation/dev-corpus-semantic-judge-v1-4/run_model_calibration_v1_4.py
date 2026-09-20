#!/usr/bin/env python3
"""V1.4 model calibration: 24 burned fixtures, preregistered <=3 prompt iterations."""
import json
import os
import sys
import time

import judge_core_v1_4 as J

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "model-calibration.json")


def matches(result, intent):
    return all(result.get(k) == v for k, v in intent.items())


def main():
    doc = json.load(open(os.path.join(HERE, "model-calibration-fixtures.json")))
    fixtures = doc["fixtures"]
    rows = []
    for i, fx in enumerate(fixtures):
        if i:
            time.sleep(2.0)
        t = J.call_judge(fx["dimension"], fx["case_context"],
                         fx["gold_criterion"], fx["sut_answer"])
        row = {"id": fx["id"], "dimension": fx["dimension"],
               "status": t.get("status"), "telemetry": {
                   k: t.get(k) for k in
                   ("finish_reason", "usage", "latency_seconds", "retries", "error")}}
        if t.get("status") == "OK":
            row["result"] = t["result"]
            row["correct"] = matches(t["result"], fx["designer_intent"])
            row["designer_intent"] = fx["designer_intent"]
        rows.append(row)
        tag = row["correct"] if "correct" in row else row["status"]
        print(f"{i + 1}/{len(fixtures)} {fx['id']}: {tag}", flush=True)

    ok_rows = [r for r in rows if r.get("status") == "OK"]
    per_dim = {}
    for dim in sorted({r["dimension"] for r in rows}):
        sub = [r for r in rows if r["dimension"] == dim]
        ok_sub = [r for r in sub if r.get("status") == "OK"]
        per_dim[dim] = {"n": len(sub), "ok": len(ok_sub),
                        "correct": sum(1 for r in ok_sub if r.get("correct")),
                        "accuracy_on_ok": round(
                            sum(1 for r in ok_sub if r.get("correct")) / len(ok_sub), 4)
                        if ok_sub else None}
    summary = {
        "artifact": "V1.4 model calibration (BURNED_MODEL_DEVELOPMENT_DATA)",
        "n": len(rows),
        "status_ok": len(ok_rows),
        "transport_failures": sum(1 for r in rows if r.get("status") == "TRANSPORT_FAILURE"),
        "transport_capacity_failures": sum(1 for r in rows if r.get("status") == "TRANSPORT_CAPACITY_FAILURE"),
        "schema_failures": sum(1 for r in rows if r.get("status") == "SCHEMA_FAILURE"),
        "per_dimension": per_dim,
        "overall_correct_on_ok": round(
            sum(1 for r in ok_rows if r.get("correct")) / len(ok_rows), 4) if ok_rows else None,
        "rows": rows,
    }
    with open(OUT, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in
                      ("n", "status_ok", "transport_failures",
                       "transport_capacity_failures", "schema_failures",
                       "per_dimension", "overall_correct_on_ok")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
