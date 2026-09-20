#!/usr/bin/env python3
"""Stage 1: blind semantic screening over frozen SCREEN partitions.

One pass per candidate over forbidden SCREEN (53) + critical SCREEN (37).
Outputs are frozen incrementally; scoring happens in a separate script only
after all candidate outputs are frozen (contract scoring_freeze rule).
Semantic retries are forbidden; only the transport JSON-mode fix applies.
"""
import json
import os
import time
import urllib.error

from run_transport_calibration import (
    CANDIDATES,
    HERE,
    build_prompts,
    call_model,
    load_frozen,
    validate,
)

OUT = os.path.join(HERE, "screening-results.json")


def main():
    contract, split, rows = load_frozen()
    cfg = json.load(open(os.path.join(HERE, "candidate-configs.json"),
                         encoding="utf-8"))
    wire_by_id = {c["logical_id"]: c["wire_id"] for c in CANDIDATES}
    todo = [c for c in cfg["candidates"]
            if c["transport_status"] != "TRANSPORT_NOT_VERIFIED_ROUTE_RESTRICTED"]
    state = {"candidates": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
        for lid in list(state["candidates"]):
            if lid not in todo:
                del state["candidates"][lid]
    for cand in todo:
        lid = cand["logical_id"]
        if lid in state["candidates"]:
            print("SKIP (already screened):", lid)
            continue
        hashes = (split["partitions"]["forbidden_claim"].get("SCREEN", [])
                  + split["partitions"]["critical_condition"].get("SCREEN", []))
        print("screening", lid, cand["wire_id"], "rows:", len(hashes),
              flush=True)
        results = []
        json_mode = True
        for chash in hashes:
            row = rows[chash]
            print("  row", row["packet_id"], row["lane"], flush=True)
            system_prompt, user_prompt = build_prompts(row, contract)
            rec = {"logical_id": lid, "canonical_hash": chash,
                   "lane": row["lane"]}
            attempts = []
            raw, parsed, elapsed, usage, err = None, None, None, None, None
            for attempt in (1, 2):
                try:
                    t0 = time.time()
                    raw, elapsed, usage = call_model(
                        cand.get("wire_id", wire_by_id[lid]), system_prompt,
                        user_prompt, json_mode)
                    err = None
                    break
                except Exception as exc:
                    err = type(exc).__name__ + ": " + str(exc)[:300]
                    attempts.append({"attempt": attempt, "error": err[:300]})
                    if (isinstance(exc, urllib.error.HTTPError)
                            and exc.code in (400, 422) and json_mode):
                        json_mode = False
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
            results.append(rec)
            with open(os.path.join(
                    HERE, "screening-progress-%s.jsonl"
                    % lid.replace("/", "_")), "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        counts = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        state["candidates"][lid] = {
            "wire_id": cand["wire_id"], "rows": len(results),
            "status_counts": counts, "results": results,
        }
        print("  ->", lid, counts, flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    print("DONE")


if __name__ == "__main__":
    main()
