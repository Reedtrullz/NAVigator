#!/usr/bin/env python3
"""One bounded technical recapture per INVALID_JSON row.

The calibration pass stored raw[:300], which truncated fenced JSON payloads
before the fence-strip parse could run. This recapture stores the FULL raw,
applies fence-strip parsing only (no prompt change, json_mode unchanged).
This is the single technical transport retry allowed per row.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)

from run_transport_calibration import build_prompts, call_model, load_frozen, validate  # noqa: E402

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
    path = os.path.join(HERE, "transport-screen-results.json")
    tsr = json.load(open(path, encoding="utf-8"))
    summary = {}
    for lid, cand in tsr["candidates"].items():
        stats = {"recapture_attempts": 0, "recovered": 0, "still_invalid_json": 0}
        for rec in cand["results"]:
            if rec["status"] != "INVALID_JSON":
                continue
            stats["recapture_attempts"] += 1
            row = rows[rec["canonical_hash"]]
            system_prompt, user_prompt = build_prompts(row, contract)
            try:
                raw, elapsed, usage = call_model(cand["wire_id"], system_prompt, user_prompt, True)
            except Exception as exc:
                rec["recovery"] = {"result": "RECAPTURE_TRANSPORT_ERROR", "error": str(exc)[:200]}
                stats["still_invalid_json"] += 1
                continue
            rec["raw_full"] = raw
            try:
                parsed = json.loads(strip_fences(raw))
            except Exception:
                rec["recovery"] = {"result": "RECAPTURE_STILL_UNPARSEABLE", "raw_full": raw[:400]}
                stats["still_invalid_json"] += 1
                continue
            sv, ev, vv = validate(parsed, row, contract)
            rec.update(status="OK" if (sv and ev and vv) else "INVALID_MODEL_REVIEW",
                       schema_valid=sv, enum_valid=ev, evidence_valid=vv,
                       elapsed_s=elapsed, usage=usage, parsed=parsed)
            rec["recovery"] = {"result": "RECOVERED_RECAPTURE_FENCE_STRIP"}
            stats["recovered"] += 1
        cand["ok"] = sum(1 for r in cand["results"] if r["status"] == "OK")
        cand["transport_errors"] = sum(1 for r in cand["results"] if r["status"] == "TRANSPORT_ERROR")
        cand["invalid_json"] = sum(1 for r in cand["results"] if r["status"] == "INVALID_JSON")
        cand["invalid_model_reviews"] = sum(1 for r in cand["results"] if r["status"] == "INVALID_MODEL_REVIEW")
        if stats["recapture_attempts"]:
            cand["recapture_stats"] = stats
            summary[lid] = stats
            print(lid, "->", json.dumps(stats), "ok:", cand["ok"], flush=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tsr, f, ensure_ascii=False, indent=2)
    rec_path = os.path.join(HERE, "transport-recovery-results.json")
    rec = json.load(open(rec_path, encoding="utf-8"))
    rec["recapture_invalid_json"] = summary
    with open(rec_path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print("RECAPTURE DONE")


if __name__ == "__main__":
    main()
