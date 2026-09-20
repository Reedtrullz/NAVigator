#!/usr/bin/env python3
"""V2 Stage 0: transport calibration for reserve-pool candidates.

Reuses V1's frozen corpus/split/contract via the V1 harness functions
(build_prompts, call_model, validate, load_frozen) with V2 candidate routes.
Only transport fixes apply (JSON-mode disable on 400/422).
Semantic performance here does NOT qualify any candidate.
"""
import json
import os
import sys
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)

from run_transport_calibration import (  # noqa: E402
    build_prompts, call_model, load_frozen, validate,
)

OUT = os.path.join(HERE, "transport-screen-results.json")

CANDIDATES = [
    {"logical_id": "R2-laguna-s-2.1", "wire_id": "command-code/poolside/laguna-s-2.1-free"},
    {"logical_id": "R3-ling-3.0-flash-sante", "wire_id": "command-code/inclusionai/ling-3.0-flash-sante:free"},
    {"logical_id": "R4-gemma-4-26b-a4b-it", "wire_id": "openrouter/google/gemma-4-26b-a4b-it:free"},
    {"logical_id": "R5-inkling-small", "wire_id": "openrouter/thinkingmachines/inkling-small:free"},
]


def main():
    contract, split, rows = load_frozen()
    hashes = (split["partitions"]["forbidden_claim"].get("TRANSPORT", [])
              + split["partitions"]["critical_condition"].get("TRANSPORT", []))
    state = {"stage": "TRANSPORT_CALIBRATION_V2", "candidates": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
    for cand in CANDIDATES:
        lid = cand["logical_id"]
        if lid in state["candidates"]:
            print("SKIP (already calibrated):", lid)
            continue
        results = []
        json_mode = True
        f403 = f402 = f429 = 0
        for chash in hashes:
            row = rows[chash]
            system_prompt, user_prompt = build_prompts(row, contract)
            rec = {"logical_id": lid, "canonical_hash": chash, "lane": row["lane"]}
            attempts = []
            raw, elapsed, usage, err = None, None, None, None
            for attempt in (1, 2):
                try:
                    raw, elapsed, usage = call_model(cand["wire_id"], system_prompt, user_prompt, json_mode)
                    err = None
                    break
                except urllib.error.HTTPError as exc:
                    body = ""
                    try:
                        body = exc.read().decode(errors="replace")[:300]
                    except Exception:
                        pass
                    err = "HTTP_%d: %s" % (exc.code, body)
                    if exc.code == 403:
                        f403 += 1
                    elif exc.code == 402:
                        f402 += 1
                    elif exc.code == 429:
                        f429 += 1
                    if exc.code in (400, 422) and json_mode:
                        json_mode = False  # provider-specific structured-output fix
                        continue  # retry same row once without JSON mode
                    if exc.code in (402, 403):
                        break  # never retried per frozen retry policy
                except Exception as exc:
                    err = type(exc).__name__ + ": " + str(exc)[:300]
                attempts.append({"attempt": attempt, "error": (err or "")[:300]})
            rec["attempts"] = attempts
            if err is not None:
                rec.update(status="TRANSPORT_ERROR", error=err[:300])
                results.append(rec)
                with open(os.path.join(HERE, "transport-progress-v2-%s.jsonl" % lid), "a", encoding="utf-8") as pf:
                    pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue
            try:
                parsed = json.loads(raw)
            except Exception:
                rec.update(status="INVALID_JSON", raw=raw[:300], elapsed_s=elapsed)
                results.append(rec)
                with open(os.path.join(HERE, "transport-progress-v2-%s.jsonl" % lid), "a", encoding="utf-8") as pf:
                    pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue
            sv, ev, vv = validate(parsed, row, contract)
            rec.update(status="OK" if (sv and ev and vv) else "INVALID_MODEL_REVIEW",
                       schema_valid=sv, enum_valid=ev, evidence_valid=vv,
                       elapsed_s=elapsed, usage=usage, parsed=parsed)
            results.append(rec)
            with open(os.path.join(HERE, "transport-progress-v2-%s.jsonl" % lid), "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ok = sum(1 for r in results if r["status"] == "OK")
        terr = sum(1 for r in results if r["status"] == "TRANSPORT_ERROR")
        inv = sum(1 for r in results if r["status"] == "INVALID_MODEL_REVIEW")
        ij = sum(1 for r in results if r["status"] == "INVALID_JSON")
        state["candidates"][lid] = {
            "wire_id": cand["wire_id"], "rows": len(results), "ok": ok,
            "transport_errors": terr, "invalid_model_reviews": inv,
            "invalid_json": ij,
            "http_403_events": f403, "http_402_events": f402, "http_429_events": f429,
            "results": results,
        }
        print("  ->", lid, "ok:", ok, "terr:", terr, "inv:", inv, "ij:", ij,
              "403:", f403, "402:", f402, "429:", f429, flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    print("V2 TRANSPORT CALIBRATION DONE")


if __name__ == "__main__":
    main()
