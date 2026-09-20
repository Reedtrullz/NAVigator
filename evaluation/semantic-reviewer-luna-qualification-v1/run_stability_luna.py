#!/usr/bin/env python3
"""Stage 3: stability rerun of frozen STABILITY partitions (LUNA-HIGH).

Identical frozen config; measures self-consistency of authoritative fields
against the frozen reference. Runs only if Stage 2 qualified the config.
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
import sys  # noqa: E402
sys.path.insert(0, V1)
import luna_transport as lt  # noqa: E402
from run_transport_calibration import build_prompts, load_frozen, validate  # noqa: E402

OUT = os.path.join(HERE, "stability-results.json")
CONFIGS = [("LUNA-HIGH", "HIGH")]


def main():
    contract, split, rows = load_frozen()
    state = {"stage": "STABILITY_LUNA_V1", "configs": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
    for cid, effort in CONFIGS:
        if cid not in state["configs"]:
            state["configs"][cid] = {}
        for lane in ("forbidden_claim", "critical_condition"):
            hashes = split["partitions"][lane].get("STABILITY", [])
            if lane in state["configs"][cid]:
                print("SKIP", cid, lane)
                continue
            print("STABILITY", cid, lane, "rows:", len(hashes), flush=True)
            results = []
            prog = os.path.join(HERE, "stability-progress-%s-%s.jsonl"
                                % (cid.lower(), lane))
            for chash in hashes:
                row = rows[chash]
                system_prompt, user_prompt = build_prompts(row, contract)
                rec = {"config_id": cid, "reasoning_effort": effort,
                       "lane": lane, "canonical_hash": chash,
                       "packet_id": row["packet_id"],
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
                results.append(rec)
                with open(prog, "a", encoding="utf-8") as pf:
                    pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print("  ", row["packet_id"], lane, rec["status"], flush=True)
                time.sleep(1)
            state["configs"][cid][lane] = results
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(" ->", cid, lane, "frozen", flush=True)
    print("STABILITY_DONE")


if __name__ == "__main__":
    main()
