#!/usr/bin/env python3
"""Stage 2: dual blind passes over CORE+EDGE partitions for LUNA-HIGH.

Mirrors V1 run_dual_pass.py semantics: pass A and pass B are independent
calls (B never sees A), no third pass, no best-of-N, no semantic retries.
Same frozen prompts and validation as screening via the V1 harness.
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
import sys  # noqa: E402
sys.path.insert(0, V1)  # V1 harness first; local dir would shadow module name
import luna_transport as lt  # noqa: E402
from run_transport_calibration import build_prompts, load_frozen, validate  # noqa: E402

OUT = os.path.join(HERE, "dual-pass-results.json")
CONFIGS = [("LUNA-HIGH", "HIGH")]


def main():
    contract, split, rows = load_frozen()
    state = {"stage": "DUAL_PASS_LUNA_V1", "configs": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
    for cid, effort in CONFIGS:
        if cid not in state["configs"]:
            state["configs"][cid] = {}
        for lane in ("forbidden_claim", "critical_condition"):
            hashes = (split["partitions"][lane].get("CORE", [])
                      + split["partitions"][lane].get("EDGE", []))
            if lane in state["configs"][cid]:
                print("SKIP", cid, lane)
                continue
            print("DUAL_PASS", cid, lane, "rows:", len(hashes), flush=True)
            lane_results = {"A": [], "B": []}
            for tag in ("A", "B"):
                prog = os.path.join(
                    HERE, "dual-pass-progress-%s-%s-%s.jsonl"
                    % (cid.lower(), tag, lane))
                for chash in hashes:
                    row = rows[chash]
                    system_prompt, user_prompt = build_prompts(row, contract)
                    rec = {"config_id": cid, "reasoning_effort": effort,
                           "pass": tag, "canonical_hash": chash,
                           "lane": lane, "packet_id": row["packet_id"],
                           "request_config_hash": lt.request_config_hash(effort)}
                    r = lt.call_with_policy(effort, system_prompt, user_prompt)
                    rec["attempts"] = r["attempts"]
                    rec["json_mode_final"] = r["json_mode_final"]
                    rec["elapsed_s"] = r["elapsed_s"]
                    rec["usage"] = r["usage"]
                    if r["error"] is not None:
                        rec.update(status="TRANSPORT_ERROR",
                                   error=r["error"][:300])
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
                                schema_valid=sv, enum_valid=ev,
                                evidence_valid=evid, parsed=parsed)
                    lane_results[tag].append(rec)
                    with open(prog, "a", encoding="utf-8") as pf:
                        pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    print("  ", tag, row["packet_id"], lane,
                          rec["status"], flush=True)
                    time.sleep(1)
            state["configs"][cid][lane] = {"A": lane_results["A"],
                                           "B": lane_results["B"]}
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(" ->", cid, lane, "frozen", flush=True)
    print("DUAL_PASS_DONE")


if __name__ == "__main__":
    main()
