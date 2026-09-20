#!/usr/bin/env python3
"""Stage 2: frozen dual blind passes over CORE+EDGE for LUNA-MAX only.

Byte-identical frozen inheritance: same contract, prompts, validation,
transport policy, retry/parse-fix classes, and config as the predecessor
lineage. Pass A never sees pass B; no third pass; invalid stays invalid.
Resumable: completed rows in the spec-named progress JSONLs are skipped.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(os.path.dirname(HERE), "semantic-reviewer-luna-qualification-v1")
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)   # frozen harness first
sys.path.insert(1, PRE)  # predecessor frozen transport (no name collision)
import luna_transport as lt  # noqa: E402
from run_transport_calibration import build_prompts, load_frozen, validate  # noqa: E402

OUT = os.path.join(HERE, "max-dual-pass-results.json")
CONFIGS = [("LUNA-MAX", "MAX")]
EXPECTED_CONTRACT_SHA = "a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f"
EXPECTED_MAX_CONFIG_SHA = "89e12976b6f134daecb55d68f41536b1e5eee0b9b0dbe2242e067799f5bf754b"


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def integrity_gate():
    checks = {
        os.path.join(HERE, "inherited-contract.json"): EXPECTED_CONTRACT_SHA,
        os.path.join(HERE, "inherited-max-config.json"): EXPECTED_MAX_CONFIG_SHA,
        os.path.join(PRE, "luna-max-config.json"): EXPECTED_MAX_CONFIG_SHA,
    }
    for path, expected in checks.items():
        actual = sha_file(path)
        if actual != expected:
            print("LUNA_MAX_COMPLETION_INPUT_INTEGRITY_FAILURE:", path,
                  actual, "!=", expected, flush=True)
            sys.exit(2)
    print("INTEGRITY_GATE PASS", flush=True)


def load_progress(prog):
    done = {}
    if os.path.exists(prog):
        with open(prog, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    done[(rec["pass"], rec["canonical_hash"])] = rec
    return done


def main():
    integrity_gate()
    contract, split, rows = load_frozen()
    state = {"stage": "DUAL_PASS_LUNA_MAX_COMPLETION_V1", "configs": {}}
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
            lane_slug = "forbidden" if lane == "forbidden_claim" else "critical"
            for tag in ("A", "B"):
                prog = os.path.join(HERE, "max-%s-pass-%s.jsonl"
                                    % (lane_slug, tag.lower()))
                done = load_progress(prog)
                for chash in hashes:
                    if (tag, chash) in done:
                        lane_results[tag].append(done[(tag, chash)])
                        continue
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
