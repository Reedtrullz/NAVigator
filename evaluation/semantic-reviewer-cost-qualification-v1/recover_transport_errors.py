#!/usr/bin/env python3
"""Bounded transport-recovery pass for rows marked TRANSPORT_ERROR.

Allowed ONLY for rows whose original error is transient (timeout, 502, 429).
Permanent route restrictions (403 route-restricted) are NOT recovered.
Each recovered row is validated identically and recorded with its attempt
history; original failed rows are preserved in the attempt record.
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

OUT = os.path.join(HERE, "transport-screen-results.json")
RECOVERY_OUT = os.path.join(HERE, "transport-recovery-results.json")


def transient(err):
    return ("TimeoutError" in err or "HTTP_502" in err
            or "HTTP_429" in err)


def main():
    contract, split, rows = load_frozen()
    state = json.load(open(OUT, encoding="utf-8"))
    recovery = {"note": ("single bounded recovery pass for transient transport "
                          "errors only (timeout/502/429); 403 route-restricted "
                          "candidates not recovered"),
                "candidates": {}}
    by_id = {c["logical_id"]: c for c in CANDIDATES}
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
                        by_id[lid]["wire_id"], system_prompt, user_prompt,
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
                    attempts.append({"attempt": "recovery-%d" % attempt,
                                     "error": err[:300]})
                    if (isinstance(exc, urllib.error.HTTPError)
                            and exc.code in (400, 422) and json_mode):
                        json_mode = False
            rec["attempts"] = attempts
            (fixed if ok else still_bad).append(rec)
            time.sleep(5)
        recovery["candidates"][lid] = {
            "attempted": len(bad), "recovered": len(fixed),
            "still_transport_error": len(still_bad),
            "rows": fixed + still_bad,
        }
        for r in fixed:
            for i, orig in enumerate(block["results"]):
                if orig["canonical_hash"] == r["canonical_hash"]:
                    block["results"][i] = r
                    break
        ok = sum(1 for r in block["results"] if r["status"] == "OK")
        terr = sum(1 for r in block["results"]
                   if r["status"] == "TRANSPORT_ERROR")
        inv = sum(1 for r in block["results"]
                  if r["status"] == "INVALID_MODEL_REVIEW")
        ij = sum(1 for r in block["results"]
                 if r["status"] == "INVALID_JSON")
        block.update(ok=ok, transport_errors=terr, invalid_model_reviews=inv,
                     invalid_json=ij)
        print("  ->", lid, "ok:", ok, "terr:", terr, "inv:", inv, "ij:", ij)
    with open(RECOVERY_OUT, "w", encoding="utf-8") as f:
        json.dump(recovery, f, ensure_ascii=False, indent=2)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print("RECOVERY_DONE")


if __name__ == "__main__":
    main()
