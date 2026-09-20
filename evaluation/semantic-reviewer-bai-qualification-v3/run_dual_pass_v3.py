#!/usr/bin/env python3
"""V3 Stage 2: dual-pass for surviving lanes only.

V3 screening survivors: BAI-DEEPSEEK critical_condition (the only lane that
passed frozen screening gates). GLM failed both lanes and is not screened
further (no best-of-bad). Reuses V1 dual-pass harness via direct import of
the module functions with a V3 out path; candidate config is the frozen
V3 candidate-configs.json filtered to the surviving lane.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1DIR = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
V1 = os.path.join(V1DIR, "run_dual_pass.py")
sys.path.insert(0, V1DIR)

import importlib.util
spec = importlib.util.spec_from_file_location("v1_dual_pass", V1)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

from run_transport_calibration import build_prompts, call_model, load_frozen, validate  # noqa: E402
import urllib.error
import time

OUT = os.path.join(HERE, "full-qualification-results.json")
CAND = {"logical_id": "BAI-DEEPSEEK",
        "wire_id": "B.AI/deepseek-v4-flash-vision-exp"}


def run_one(cand, row, contract, json_mode):
    attempts = []
    raw = parsed = elapsed = usage = err = None
    for attempt in (1, 2):
        try:
            t0 = time.time()
            system_prompt, user_prompt = build_prompts(row, contract)
            raw, elapsed, usage = call_model(
                cand["wire_id"], system_prompt, user_prompt, json_mode)
            err = None
            break
        except Exception as exc:
            err = type(exc).__name__ + ": " + str(exc)[:300]
            attempts.append({"attempt": attempt, "error": err[:300]})
            if (isinstance(exc, urllib.error.HTTPError)
                    and exc.code in (400, 422) and json_mode):
                json_mode = False
    return raw, parsed, elapsed, usage, err, attempts, json_mode


def main():
    contract, split, rows = load_frozen()
    lane = "critical_condition"
    hashes = (split["partitions"][lane].get("CORE", [])
              + split["partitions"][lane].get("EDGE", []))
    state = {"candidates": {}}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8"))
        for lid in list(prev.get("candidates", {})):
            if lid == CAND["logical_id"]:
                state["candidates"][lid] = prev["candidates"][lid]
    lid = CAND["logical_id"]
    if lid not in state["candidates"]:
        state["candidates"][lid] = {}
    if lane in state["candidates"][lid]:
        print("SKIP", lid, lane)
        return
    print("DUAL_PASS", lid, lane, "rows:", len(hashes), flush=True)
    lane_results = {"A": [], "B": []}
    for tag in ("A", "B"):
        prog = os.path.join(HERE, "dual-pass-progress-v3-%s-%s.jsonl" % (tag, lane))
        json_mode = True
        for chash in hashes:
            row = rows[chash]
            rec = {"logical_id": lid, "pass": tag, "lane": lane,
                   "canonical_hash": chash}
            (raw, parsed, elapsed, usage, err,
             attempts, json_mode) = run_one(CAND, row, contract, json_mode)
            rec["attempts"] = attempts
            if err is not None:
                rec.update(status="TRANSPORT_ERROR", error=err[:300])
            else:
                try:
                    parsed = json.loads(raw)
                except Exception:
                    rec.update(status="INVALID_JSON", raw=raw[:300],
                               elapsed_s=elapsed)
                    parsed = None
                if parsed is not None:
                    sv, ev, evid = validate(parsed, row, contract)
                    rec.update(status="OK" if (sv and ev and evid)
                               else "INVALID_MODEL_REVIEW",
                               schema_valid=sv, enum_valid=ev,
                               evidence_valid=evid, elapsed_s=elapsed,
                               usage=usage, parsed=parsed)
            lane_results[tag].append(rec)
            with open(prog, "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + chr(10))
        state["candidates"][lid][lane] = {"A": lane_results["A"],
                                          "B": lane_results["B"]}
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print("  ->", tag, "frozen", flush=True)
    print("DUAL_PASS_DONE")


if __name__ == "__main__":
    main()
