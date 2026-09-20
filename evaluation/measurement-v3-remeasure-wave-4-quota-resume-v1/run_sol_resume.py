#!/usr/bin/env python3
"""Wave-4 quota-resume SOL residual adjudication (gpt-5.6-sol, LOW only).

Imports the frozen Wave-3 residual-adjudication module so prompts, schema
validation, span checks, and single-transport-retry policy are identical.
Outputs live in THIS resume lineage; frozen lineages are never written."""
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"

_spec = importlib.util.spec_from_file_location(
    "frozen_residual_adjudication",
    os.path.join(REPO, "evaluation", "measurement-v3-remeasure-repair-wave-3",
                 "run_residual_adjudication.py"))
_resid = importlib.util.module_from_spec(_spec)
sys.modules["frozen_residual_adjudication"] = _resid
_spec.loader.exec_module(_resid)


def main():
    inp = json.load(open(os.path.join(HERE, "residual-inputs.json"), encoding="utf-8"))
    pkts = inp["packets"]
    transport = {"artifact": "sol-adjudication-transport-log", "task_id": TASK_ID,
                 "model": _resid.MODEL, "reasoning_effort": _resid.EFFORT,
                 "policy": "at most ONE technical retry per transport failure",
                 "events": []}
    fa = os.path.join(HERE, "sol-pass-a.jsonl")
    fb = os.path.join(HERE, "sol-pass-b.jsonl")
    done_a = {json.loads(l)["packet_id"] for l in open(fa) if l.strip()} if os.path.exists(fa) else set()
    done_b = {json.loads(l)["packet_id"] for l in open(fb) if l.strip()} if os.path.exists(fb) else set()
    for p in pkts:
        for fname, done, name in ((fa, done_a, "SOL_A"), (fb, done_b, "SOL_B")):
            if p["packet_id"] in done:
                continue
            rec = _resid.call_model(name, p)
            if rec["status"] == "TRANSPORT_ERROR":
                transport["events"].append({"packet_id": p["packet_id"],
                                            "pass": name, "attempt": 1,
                                            "outcome": "TRANSPORT_ERROR",
                                            "error": rec.get("error")})
                time.sleep(2)
                retry = _resid.call_model(name, p)
                transport["events"].append({"packet_id": p["packet_id"],
                                            "pass": name, "attempt": 2,
                                            "outcome": retry["status"],
                                            "retry_reason": "single permitted technical transport retry"})
                rec = retry
            with open(fname, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(p["packet_id"], name, rec["status"], flush=True)
            time.sleep(1)
    with open(os.path.join(HERE, "sol-transport-log.json"), "w", encoding="utf-8") as f:
        json.dump(transport, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("EXECUTION_DONE")


if __name__ == "__main__":
    main()
