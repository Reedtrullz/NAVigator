#!/usr/bin/env python3
"""V2 Stage 1: blind semantic screening over the frozen V1 SCREEN partitions.

One pass per surviving-transport candidate (R2 laguna-s-2.1,
R3 ling-3.0-flash-sante) over forbidden SCREEN (53) + critical SCREEN (37).
Outputs are frozen incrementally; scoring happens only after all outputs are
frozen (contract scoring_freeze rule). No semantic retries; invalid stays
invalid. Only transport-class fixes apply: JSON-mode disable on 400/422 and
code-fence stripping on parse failure. Full raw payloads are persisted.
"""
import json
import os
import sys
import time
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)

from run_transport_calibration import (  # noqa: E402
    build_prompts, call_model, load_frozen, validate,
)

OUT = os.path.join(HERE, "semantic-screen-results.json")

CANDIDATES = [
    {"logical_id": "R2-laguna-s-2.1",
     "wire_id": "command-code/poolside/laguna-s-2.1-free"},
    {"logical_id": "R3-ling-3.0-flash-sante",
     "wire_id": "command-code/inclusionai/ling-3.0-flash-sante:free"},
]


def strip_fences(raw):
    """Transport-only parse fix: strip a single surrounding code fence."""
    s = raw.strip()
    fence = chr(96) * 3
    if s.startswith(fence):
        first_nl = s.find(chr(10))
        s = s[first_nl + 1:] if first_nl != -1 else s
        if s.rstrip().endswith(fence):
            s = s.rstrip()[:-3]
    return s.strip()


def main():
    contract, split, rows = load_frozen()
    hashes = (split["partitions"]["forbidden_claim"].get("SCREEN", [])
              + split["partitions"]["critical_condition"].get("SCREEN", []))
    state = {"stage": "SEMANTIC_SCREENING_V2", "rows_total": len(hashes),
             "candidates": {}}
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding="utf-8"))
        for lid in list(prev.get("candidates", {})):
            if lid in {c["logical_id"] for c in CANDIDATES}:
                state["candidates"][lid] = prev["candidates"][lid]
    for cand in CANDIDATES:
        lid = cand["logical_id"]
        results = state["candidates"].get(lid, {}).get("results", [])
        done = {r["canonical_hash"] for r in results}
        if len(done) >= len(hashes):
            print("SKIP (already screened):", lid, flush=True)
            continue
        print("screening", lid, cand["wire_id"],
              "remaining:", len(hashes) - len(done), flush=True)
        json_mode = True
        for chash in hashes:
            if chash in done:
                continue
            row = rows[chash]
            print("  row", row["packet_id"], row["lane"], flush=True)
            system_prompt, user_prompt = build_prompts(row, contract)
            rec = {"logical_id": lid, "canonical_hash": chash,
                   "lane": row["lane"]}
            attempts = []
            raw = elapsed = usage = err = None
            for attempt in (1, 2):
                try:
                    t0 = time.time()
                    raw, elapsed, usage = call_model(
                        cand["wire_id"], system_prompt, user_prompt, json_mode)
                    err = None
                    break
                except urllib.error.HTTPError as exc:
                    body = ""
                    try:
                        body = exc.read().decode(errors="replace")[:300]
                    except Exception:
                        pass
                    err = "HTTP_%d: %s" % (exc.code, body)
                    attempts.append({"attempt": attempt, "error": err[:300]})
                    if exc.code in (400, 422) and json_mode:
                        json_mode = False
                except Exception as exc:
                    err = type(exc).__name__ + ": " + str(exc)[:300]
                    attempts.append({"attempt": attempt, "error": err[:300]})
            rec["attempts"] = attempts
            if err is not None:
                rec.update(status="TRANSPORT_ERROR", error=err[:300])
            else:
                rec["raw_full"] = raw
                parsed = None
                try:
                    parsed = json.loads(raw)
                except Exception:
                    try:
                        parsed = json.loads(strip_fences(raw))
                        rec["parse_fix"] = "FENCE_STRIP"
                    except Exception:
                        parsed = None
                if parsed is None:
                    rec.update(status="INVALID_JSON", elapsed_s=elapsed,
                               usage=usage)
                else:
                    sv, ev, evid = validate(parsed, row, contract)
                    rec.update(
                        status="OK" if (sv and ev and evid)
                        else "INVALID_MODEL_REVIEW",
                        schema_valid=sv, enum_valid=ev, evidence_valid=evid,
                        elapsed_s=elapsed, usage=usage, parsed=parsed)
            results.append(rec)
            counts = {}
            for r in results:
                counts[r["status"]] = counts.get(r["status"], 0) + 1
            state["candidates"][lid] = {"wire_id": cand["wire_id"],
                                        "rows": len(results),
                                        "status_counts": counts,
                                        "results": results}
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            with open(os.path.join(
                    HERE, "semantic-screen-progress-%s.jsonl" % lid.replace("/", "_")),
                    "a", encoding="utf-8") as pf:
                pf.write(json.dumps(rec, ensure_ascii=False) + chr(10))
        print("  ->", lid, counts, flush=True)
    print("SCREENING_DONE")


if __name__ == "__main__":
    main()
