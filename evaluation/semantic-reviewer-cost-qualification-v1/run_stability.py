#!/usr/bin/env python3
"""Stage 3: stability rerun of the frozen STABILITY partitions.

Runs only candidates that passed Stage 2 (listed in stability-candidates.json).
Identical frozen config; measures self-consistency of authoritative fields.
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

OUT = os.path.join(HERE, "stability-results.json")


def main():
    contract, split, rows = load_frozen()
    cfg = json.load(open(os.path.join(HERE, "candidate-configs.json"),
                         encoding="utf-8"))
    by_id = {c["logical_id"]: c for c in cfg["candidates"]}
    targets = json.load(open(os.path.join(HERE, "stability-candidates.json"),
                             encoding="utf-8"))
    state = {"candidates": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
    for lane in ("forbidden_claim", "critical_condition"):
        hashes = split["partitions"][lane].get("STABILITY", [])
        for lid in targets.get(lane, []):
            if lid not in by_id:
                raise SystemExit("candidate not in frozen configs: " + lid)
            if lid in state["candidates"] and lane in state["candidates"][lid]:
                print("SKIP", lid, lane)
                continue
            print("STABILITY", lid, lane, "rows:", len(hashes), flush=True)
            results = []
            json_mode = True
            prog = os.path.join(HERE, "stability-progress-%s-%s.jsonl"
                                % (lid.replace("/", "_"), lane))
            for chash in hashes:
                row = rows[chash]
                rec = {"logical_id": lid, "lane": lane,
                       "canonical_hash": chash}
                attempts = []
                raw = parsed = elapsed = usage = err = None
                for attempt in (1, 2):
                    try:
                        t0 = time.time()
                        system_prompt, user_prompt = build_prompts(row, contract)
                        raw, elapsed, usage = call_model(
                            by_id[lid]["wire_id"], system_prompt,
                            user_prompt, json_mode)
                        err = None
                        break
                    except Exception as exc:
                        err = type(exc).__name__ + ": " + str(exc)[:300]
                        attempts.append({"attempt": attempt,
                                         "error": err[:300]})
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
                with open(prog, "a", encoding="utf-8") as pf:
                    pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if lid not in state["candidates"]:
                state["candidates"][lid] = {}
            state["candidates"][lid][lane] = results
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print("  ->", lid, lane, "frozen", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
