#!/usr/bin/env python3
"""Bounded transport-recovery pass for frozen screening outputs.

Same policy as the frozen transport-stage recovery: only transient errors
(timeout, 502, 429) are retried once in a single bounded pass. HTTP 402
(provider credit exhaustion) and HTTP 503 are NOT in the frozen transient
enumeration and stay TRANSPORT_ERROR. INVALID_JSON / INVALID_MODEL_REVIEW
rows are never retried (invalid remains invalid).
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

OUT = os.path.join(HERE, "screening-results.json")
RECOVERY_OUT = os.path.join(HERE, "screening-recovery-results.json")


def transient(err):
    return ("TimeoutError" in err
            or "HTTP Error 502" in err
            or "HTTP Error 429" in err)


def main():
    contract, split, rows = load_frozen()
    state = json.load(open(OUT, encoding="utf-8"))
    cfg = json.load(open(os.path.join(HERE, "candidate-configs.json"),
                         encoding="utf-8"))
    wire_by_id = {c["logical_id"]: c["wire_id"] for c in cfg["candidates"]}
    recovery = {"note": ("single bounded recovery pass for transient transport "
                         "errors only (timeout/502/429); 402 credit exhaustion "
                         "and 503 not in frozen transient enumeration; "
                         "INVALID_JSON and INVALID_MODEL_REVIEW never retried"),
                "candidates": {}}
    for lid, block in state["candidates"].items():
        bad = [r for r in block["results"]
               if r["status"] == "TRANSPORT_ERROR"
               and transient(r.get("error", ""))]
        if not bad:
            continue
        print("recovering", lid, "rows:", len(bad), flush=True)
        fixed = []
        still_bad = []
        json_mode = True
        for rec in bad:
            row = rows[rec["canonical_hash"]]
            attempts = rec.get("attempts", [])
            ok = False
            for attempt in (1, 2):
                try:
                    t0 = time.time()
                    system_prompt, user_prompt = build_prompts(row, contract)
                    raw, elapsed, usage = call_model(
                        wire_by_id[lid], system_prompt, user_prompt,
                        json_mode)
                    parsed = json.loads(raw)
                    sv, ev, evid = validate(parsed, row, contract)
                    rec.update(status="OK" if (sv and ev and evid)
                               else "INVALID_MODEL_REVIEW",
                               schema_valid=sv, enum_valid=ev,
                               evidence_valid=evid, elapsed_s=elapsed,
                               usage=usage, parsed=parsed)
                    rec.pop("error", None)
                    ok = True
                    break
                except Exception as exc:
                    err = type(exc).__name__ + ": " + str(exc)[:300]
                    attempts.append({"attempt": "screening-recovery-%d" % attempt,
                                     "error": err[:300]})
                    if (isinstance(exc, urllib.error.HTTPError)
                            and exc.code in (400, 422) and json_mode):
                        json_mode = False
            rec["attempts"] = attempts
            (fixed if ok else still_bad).append(rec)
            time.sleep(3)
        recovery["candidates"][lid] = {
            "attempted": len(bad), "recovered": len(fixed),
            "still_transport_error": len(still_bad),
            "rows": fixed + still_bad,
        }
        for r in fixed + still_bad:
            for i, orig in enumerate(block["results"]):
                if orig["canonical_hash"] == r["canonical_hash"]:
                    block["results"][i] = r
                    break
        counts = {}
        for r in block["results"]:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        block["status_counts"] = counts
        print("  ->", lid, counts, flush=True)
    with open(RECOVERY_OUT, "w", encoding="utf-8") as f:
        json.dump(recovery, f, ensure_ascii=False, indent=2)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print("SCREENING_RECOVERY_DONE")


if __name__ == "__main__":
    main()
