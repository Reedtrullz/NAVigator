#!/usr/bin/env python3
"""Stage 2: independent dual blind passes over CORE+EDGE partitions.

Reads the frozen candidate-configs.json (written after transport calibration).
Pass A and pass B are independent calls; B never sees A. No third pass,
no best-of-N, no semantic retries.
"""
import json
import os
import time
import urllib.error

from run_transport_calibration import (
    HERE,
    build_prompts,
    call_model,
    load_frozen,
    validate,
)

OUT = os.path.join(HERE, "dual-pass-results.json")


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
    cfg = json.load(open(os.path.join(HERE, "candidate-configs.json"),
                         encoding="utf-8"))
    state = {"candidates": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
    for lane in ("forbidden_claim", "critical_condition"):
        hashes = (split["partitions"][lane].get("CORE", [])
                  + split["partitions"][lane].get("EDGE", []))
        for c in cfg["candidates"]:
            lid = c["logical_id"]
            if lid not in state["candidates"]:
                state["candidates"][lid] = {}
            if lane in state["candidates"][lid]:
                print("SKIP", lid, lane)
                continue
            print("DUAL_PASS", lid, lane, "rows:", len(hashes), flush=True)
            lane_results = {"A": [], "B": []}
            for tag in ("A", "B"):
                prog = os.path.join(HERE, "dual-pass-progress-%s-%s-%s.jsonl"
                                    % (lid.replace("/", "_"), tag, lane))
                json_mode = True
                for chash in hashes:
                    row = rows[chash]
                    rec = {"logical_id": lid, "pass": tag, "lane": lane,
                           "canonical_hash": chash}
                    (raw, parsed, elapsed, usage, err,
                     attempts, json_mode) = run_one(c, row, contract, json_mode)
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
                        pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            state["candidates"][lid][lane] = {"A": lane_results["A"],
                                              "B": lane_results["B"]}
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print("  ->", lid, lane, "frozen", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
