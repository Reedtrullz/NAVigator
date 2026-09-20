#!/usr/bin/env python3
"""Stage 1: blind semantic screening over frozen V1 SCREEN partitions.

One pass per frozen Luna config (LUNA-HIGH, LUNA-MAX) over forbidden SCREEN
(53) + critical SCREEN (37). Same packet ordering as V1/V2. Outputs are
frozen incrementally; scoring happens only in score_screening_luna.py after
all outputs are frozen (contract scoring_freeze rule). Candidates see only
reviewer-visible packet content.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)  # V1 harness first; local dir would shadow module name
import luna_transport as lt  # noqa: E402
from run_transport_calibration import build_prompts, load_frozen, validate  # noqa: E402

OUT = os.path.join(HERE, "screening-results.json")
CONFIGS = [("LUNA-HIGH", "HIGH"), ("LUNA-MAX", "MAX")]


def main():
    contract, split, rows = load_frozen()
    hashes = (split["partitions"]["forbidden_claim"].get("SCREEN", [])
              + split["partitions"]["critical_condition"].get("SCREEN", []))
    state = {"stage": "SEMANTIC_SCREENING_LUNA_V1", "rows_total": len(hashes),
             "configs": {}}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8"))
        state["configs"] = prev.get("configs", {})
    for cid, effort in CONFIGS:
        results = state["configs"].get(cid, {}).get("results", [])
        done = {r["canonical_hash"] for r in results}
        if len(done) >= len(hashes):
            print("SKIP (already screened):", cid, flush=True)
            continue
        print("screening", cid, "remaining:", len(hashes) - len(done), flush=True)
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
                if parsed is None:
                    rec.update(status="INVALID_JSON")
                else:
                    sv, ev, evid = validate(parsed, row, contract)
                    rec.update(
                        status="OK" if (sv and ev and evid)
                        else "INVALID_MODEL_REVIEW",
                        schema_valid=sv, enum_valid=ev, evidence_valid=evid,
                        parsed=parsed)
            results.append(rec)
            counts = {}
            for x in results:
                counts[x["status"]] = counts.get(x["status"], 0) + 1
            state["configs"][cid] = {"rows": len(results),
                                     "status_counts": counts,
                                     "results": results}
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            with open(os.path.join(HERE, "screen-progress-%s.jsonl" % cid.lower()),
                      "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + chr(10))
            print("  ", row["packet_id"], row["lane"], rec["status"], flush=True)
            time.sleep(1)
        print(" ->", cid, counts, flush=True)
    print("SCREENING_DONE")


if __name__ == "__main__":
    main()
