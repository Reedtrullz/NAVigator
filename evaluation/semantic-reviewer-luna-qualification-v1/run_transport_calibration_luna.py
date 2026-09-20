#!/usr/bin/env python3
"""Stage 0: transport calibration for LUNA-HIGH and LUNA-MAX.

Runs the frozen V1 TRANSPORT partitions (13 forbidden + 6 critical rows per
candidate) through each frozen Luna config. May fix ONLY transport issues
(json mode, parsing, enum serialization). Semantic performance on this
partition does NOT qualify any candidate.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)  # V1 harness first; local dir would shadow its module name
import luna_transport as lt  # noqa: E402
from run_transport_calibration import build_prompts, load_frozen, validate  # noqa: E402  (frozen V1 harness)

OUT = os.path.join(HERE, "transport-calibration.json")
CONFIGS = [("LUNA-HIGH", "HIGH"), ("LUNA-MAX", "MAX")]


def classify(rec, parsed, row, contract):
    if parsed is None:
        rec.update(status="INVALID_JSON")
        return
    sv, ev, evid = validate(parsed, row, contract)
    rec.update(status="OK" if (sv and ev and evid) else "INVALID_MODEL_REVIEW",
               schema_valid=sv, enum_valid=ev, evidence_valid=evid,
               parsed=parsed)


def main():
    contract, split, rows = lt.load_frozen() if hasattr(lt, "load_frozen") else load_frozen()
    hashes = (split["partitions"]["forbidden_claim"].get("TRANSPORT", [])
              + split["partitions"]["critical_condition"].get("TRANSPORT", []))
    state = {"stage": "TRANSPORT_CALIBRATION", "rows_total": len(hashes),
             "configs": {}}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8"))
        state["configs"] = prev.get("configs", {})
    for cid, effort in CONFIGS:
        results = state["configs"].get(cid, {}).get("results", [])
        done = {r["canonical_hash"] for r in results}
        if len(done) >= len(hashes):
            print("SKIP (calibrated):", cid, flush=True)
            continue
        print("calibrating", cid, "remaining:", len(hashes) - len(done), flush=True)
        for chash in hashes:
            if chash in done:
                continue
            row = rows[chash]
            system_prompt, user_prompt = build_prompts(row, contract)
            rec = {"config_id": cid, "reasoning_effort": effort,
                   "canonical_hash": chash, "lane": row["lane"],
                   "packet_id": row["packet_id"],
                   "request_config_hash": lt.request_config_hash(effort)}
            r = lt.call_with_policy(effort, system_prompt, user_prompt)
            rec["attempts"] = r["attempts"]
            rec["json_mode_final"] = r["json_mode_final"]
            rec["elapsed_s"] = r["elapsed_s"]
            rec["usage"] = r["usage"]
            if r["error"] is not None:
                rec.update(status="TRANSPORT_ERROR", error=r["error"][:300])
            else:
                rec["raw_full"] = r["raw"]
                parsed = None
                try:
                    parsed = json.loads(r["raw"])
                except Exception:
                    try:
                        parsed = json.loads(lt.strip_fences(r["raw"]))
                        rec["parse_fix"] = "FENCE_STRIP"
                    except Exception:
                        parsed = None
                classify(rec, parsed, row, contract)
            results.append(rec)
            counts = {}
            for x in results:
                counts[x["status"]] = counts.get(x["status"], 0) + 1
            state["configs"][cid] = {"rows": len(results),
                                     "status_counts": counts,
                                     "results": results}
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            with open(os.path.join(HERE, "transport-progress-%s.jsonl" % cid.lower()),
                      "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + chr(10))
            print("  ", row["packet_id"], row["lane"], rec["status"], flush=True)
            time.sleep(1)
        print(" ->", cid, counts, flush=True)
    print("CALIBRATION_DONE")


if __name__ == "__main__":
    main()
