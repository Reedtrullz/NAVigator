#!/usr/bin/env python3
"""V2 Stage 0 recovery: bounded, per frozen retry policy.

- 502 rows: one retry each (transient transport).
- INVALID_JSON rows: fence-stripping parse fix only, no new model calls.
- 429-chronic and 403 candidates get no recovery.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)

from run_transport_calibration import build_prompts, call_model, load_frozen, validate  # noqa: E402

OUT = os.path.join(HERE, "transport-recovery-results.json")
FENCE = chr(96) * 3


def strip_fences(raw):
    s = raw.strip()
    if s.startswith(FENCE):
        first_nl = s.find(chr(10))
        if first_nl != -1:
            s = s[first_nl + 1:]
        if s.endswith(FENCE):
            s = s[:-3]
    return s.strip()


def main():
    contract, split, rows = load_frozen()
    tsr = json.load(open(os.path.join(HERE, "transport-screen-results.json"), encoding="utf-8"))
    recovery = {"event": "V2_TRANSPORT_RECOVERY", "recovered": {}}
    for lid, cand in tsr["candidates"].items():
        stats = {"retried_502": 0, "recovered_from_502": 0, "fence_stripped": 0,
                 "recovered_from_fence": 0, "still_failed": 0}
        for rec in cand["results"]:
            if rec["status"] == "TRANSPORT_ERROR" and (rec.get("error") or "").startswith("HTTP_502"):
                stats["retried_502"] += 1
                row = rows[rec["canonical_hash"]]
                system_prompt, user_prompt = build_prompts(row, contract)
                try:
                    raw, elapsed, usage = call_model(cand["wire_id"], system_prompt, user_prompt, True)
                except Exception as exc:
                    rec["recovery"] = {"result": "STILL_TRANSPORT_ERROR", "error": str(exc)[:200]}
                    stats["still_failed"] += 1
                    continue
                try:
                    parsed = json.loads(raw)
                except Exception:
                    rec["recovery"] = {"result": "INVALID_JSON_AFTER_RETRY", "raw": raw[:200]}
                    stats["still_failed"] += 1
                    continue
                sv, ev, vv = validate(parsed, row, contract)
                rec.update(status="OK" if (sv and ev and vv) else "INVALID_MODEL_REVIEW",
                           schema_valid=sv, enum_valid=ev, evidence_valid=vv,
                           elapsed_s=elapsed, usage=usage, parsed=parsed)
                rec["recovery"] = {"result": "RECOVERED_RETRY"}
                stats["recovered_from_502"] += 1
            elif rec["status"] == "INVALID_JSON":
                row = rows[rec["canonical_hash"]]
                stripped = strip_fences(rec.get("raw", ""))
                try:
                    parsed = json.loads(stripped)
                except Exception:
                    rec["recovery"] = {"result": "STILL_INVALID_JSON"}
                    stats["still_failed"] += 1
                    continue
                sv, ev, vv = validate(parsed, row, contract)
                rec.update(status="OK" if (sv and ev and vv) else "INVALID_MODEL_REVIEW",
                           schema_valid=sv, enum_valid=ev, evidence_valid=vv,
                           parsed=parsed, raw_original=rec.get("raw"))
                rec.pop("raw", None)
                rec["recovery"] = {"result": "RECOVERED_FENCE_STRIP"}
                stats["fence_stripped"] += 1
                if sv and ev and vv:
                    stats["recovered_from_fence"] += 1
        c = cand
        c["ok_original"] = c["ok"]
        c["ok"] = sum(1 for r in c["results"] if r["status"] == "OK")
        c["transport_errors"] = sum(1 for r in c["results"] if r["status"] == "TRANSPORT_ERROR")
        c["invalid_json"] = sum(1 for r in c["results"] if r["status"] == "INVALID_JSON")
        c["invalid_model_reviews"] = sum(1 for r in c["results"] if r["status"] == "INVALID_MODEL_REVIEW")
        c["recovery_stats"] = stats
        recovery["recovered"][lid] = stats
        print(lid, "->", json.dumps(stats), "ok:", c["ok_original"], "->", c["ok"], flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(recovery, f, ensure_ascii=False, indent=2)
    with open(os.path.join(HERE, "transport-screen-results.json"), "w", encoding="utf-8") as f:
        json.dump(tsr, f, ensure_ascii=False, indent=2)
    print("V2 TRANSPORT RECOVERY DONE")


if __name__ == "__main__":
    main()
