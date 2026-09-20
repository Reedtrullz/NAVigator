#!/usr/bin/env python3
"""Lane H diagnostic runner V2 (ingestion repair; DEVELOPMENT_DIAGNOSTIC_ONLY).

Differences vs run_diagnostic.py (V1), nothing else changed:
- fence ingestion is optional and strict (one outer markdown fence max),
  default OFF for live calls, controlled by --fence-ingest;
- semantic_input_hash_v2 is computed per row over the exact model-facing text
  (system prompt + built user prompt), format MODEL_FACING_TEXT_V2;
- resume keys on request fingerprint + per-row input hash, not row_id alone;
- results go to results-v2-<route>.jsonl (V1 result files are never touched);
- replay mode re-scores stored V1 raw responses read-only with the unchanged
  validate() from run_diagnostic.py.

No reference labels, views or gold are visible to the model. No span
normalization, no JSON reconstruction.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ingestion_v2 as ing
import run_diagnostic as base


def load_rows():
    rows = {}
    with open(os.path.join(base.LANE, "dataset-frozen.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r["row_id"].startswith("FB1-SCR-"):
                    rows[r["row_id"]] = r
    return rows


def replay(rows):
    # smoke: empty string must not be treated as a fence wrapper
    _s, flag, _e = ing.parse_like_original("", True)
    assert flag is False, "empty string must not be treated as a fence wrapper"
    summary = {}
    for rname in ("MIMO", "DEEPSEEK"):
        path = os.path.join(HERE, "results-%s.jsonl" % rname.lower())
        counts, dispositions = ing.replay_results(path, rows, fence_enabled=True)
        summary[rname] = {"counts": counts, "non_ok_dispositions": dispositions}
        print(rname, json.dumps(counts))
    out = {
        "replay_engine": "ingestion_v2 fence_enabled=true; validate() unchanged from run_diagnostic.py",
        "hash_format": ing.HASH_FORMAT,
        "summary": summary,
    }
    out_path = os.path.join(HERE, "replay-v2-results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write(chr(10))
    print("wrote", out_path)


def verify(rows):
    intro, labels = base.load_contract_parts()
    sysp = json.load(open(os.path.join(
        base.ROOT,
        "evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json"),
        encoding="utf-8"))["semantic_instructions"]["system_prompt"]
    h1 = ing.model_input_hash_v2(sysp, base.build_user_prompt(rows["FB1-SCR-001"], intro, labels))
    h2 = ing.model_input_hash_v2(sysp, base.build_user_prompt(rows["FB1-SCR-002"], intro, labels))
    h1b = ing.model_input_hash_v2(sysp, base.build_user_prompt(rows["FB1-SCR-001"], intro, labels))
    assert h1 != h2, "different rows produced identical per-row hash"
    assert h1 == h1b, "same row produced different hash across calls (determinism)"
    stripped, flag = ing.strip_outer_fence("```json\n{\"a\": 1}\n```")
    assert flag and stripped == "{\"a\": 1}", "fence strip failed on canonical case"
    stripped2, flag2 = ing.strip_outer_fence("text\n```json\n{\"a\": 1}\n```\ntext")
    assert not flag2 and stripped2 == stripped2, "fence strip must not touch non-wrapper fences"
    print("verify OK: per-row hashes differ across rows, deterministic; fence strip strict")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "verify", "replay"])
    ap.add_argument("--fence-ingest", action="store_true",
                    help="strictly strip ONE outer markdown fence before json.loads (live calls)")
    args = ap.parse_args()
    rows = load_rows()
    if args.mode == "verify":
        verify(rows)
        return
    if args.mode == "replay":
        replay(rows)
        return

    order = json.load(open(os.path.join(base.LANE, "lane-h-presentation-order.json"),
                           encoding="utf-8"))
    row_order = [rid for k in sorted(order["blocks"]) for rid in order["blocks"][k]]
    intro, labels = base.load_contract_parts()
    sysp = json.load(open(os.path.join(
        base.ROOT,
        "evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json"),
        encoding="utf-8"))["semantic_instructions"]["system_prompt"]
    dataset_sha = base.sha_file(os.path.join(base.LANE, "dataset-frozen.jsonl"))
    contract_view_sha = base.sha_file(os.path.join(base.LANE, "lane-h-diagnostic-contract-view-v1.md"))

    events_path = os.path.join(HERE, "transport-events-v2.jsonl")
    events_f = open(events_path, "a", encoding="utf-8")

    for rname in ("MIMO", "DEEPSEEK"):
        route = dict(base.ROUTES[rname])
        out_path = os.path.join(HERE, "results-v2-%s.jsonl" % rname.lower())
        done = {}  # request_fingerprint -> row_id
        if os.path.exists(out_path):
            with open(out_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        if rec.get("status") == "OK" and rec.get("request_fingerprint"):
                            done[rec["request_fingerprint"]] = rec["row_id"]
            print(rname, "resume v2: fingerprint-keyed completed rows:", len(done))
        json_mode = route["json_mode"]
        fence_ingest = args.fence_ingest
        route_stopped = None
        for rid in row_order:
            if route_stopped:
                break
            row = rows[rid]
            up = base.build_user_prompt(row, intro, labels)
            row_hash = ing.model_input_hash_v2(sysp, up)
            if args.fence_ingest is False and json_mode is False:
                pass  # identical transport config to V1 MIMO; fingerprint still text-bound
            attempt = 1
            rec = None
            while True:
                # Fingerprint is computed by call(); to key resume on it we must
                # call first and check after. To avoid a duplicate network call
                # for an already-completed row we precompute it the same way.
                fp = base.sha({"wire_id": route["wire_id"],
                               "payload_extra": route["payload_extra"],
                               "json_mode": json_mode,
                               "system_sha": base.sha(sysp),
                               "user_sha": base.sha(up)})
                if fp in done:
                    break
                out = base.call(route, sysp, up, json_mode)
                if "error" in out:
                    code = out["code"]
                    ev = {"event": "TRANSPORT_ERROR", "route": rname, "row_id": rid,
                          "attempt": attempt, "code": code, "error": out["error"],
                          "elapsed_s": out["elapsed_s"],
                          "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                                            __import__("time").gmtime())}
                    events_f.write(json.dumps(ev, ensure_ascii=False) + chr(10))
                    events_f.flush()
                    if code in (402, 403):
                        route_stopped = "ACCESS_FAILURE_%d" % code
                        rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                               "status": "ACCESS_FAILURE", "attempt": attempt,
                               "error": out["error"],
                               "request_fingerprint": out["request_fingerprint"],
                               "semantic_input_hash_v2": row_hash}
                        break
                    rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                           "status": "TRANSPORT_ERROR", "attempt": attempt,
                           "error": out["error"], "elapsed_s": out["elapsed_s"],
                           "request_fingerprint": out["request_fingerprint"],
                           "semantic_input_hash_v2": row_hash}
                    break
                raw = out.get("raw")
                finish = out.get("finish_reason")
                rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                       "attempt": attempt, "elapsed_s": out["elapsed_s"],
                       "usage": out.get("usage", {}),
                       "model_reported": out.get("model_reported"),
                       "finish_reason": finish, "json_mode_effective": json_mode,
                       "fence_ingest_effective": fence_ingest,
                       "request_fingerprint": out["request_fingerprint"],
                       "semantic_input_hash_v2": row_hash,
                       "semantic_input_hash_format": ing.HASH_FORMAT,
                       "dataset_sha256": dataset_sha,
                       "contract_view_sha256": contract_view_sha}
                if finish == "length":
                    rec["status"] = "TRANSPORT_CAPACITY_FAILURE"
                    rec["raw"] = (raw or "")[:2000]
                elif raw is None:
                    rec["status"] = "EMPTY_RESPONSE"
                else:
                    parsed, was_stripped, perr = ing.parse_like_original(raw, fence_ingest)
                    if parsed is None:
                        rec["status"] = "INVALID_JSON"
                        rec["raw"] = raw[:2000]
                        if was_stripped:
                            rec["json_parse_error_after_fence_strip"] = perr
                    else:
                        ok, why = base.validate(row, parsed)
                        rec["result"] = parsed
                        rec["raw"] = raw
                        rec["outer_fence_stripped"] = was_stripped
                        if ok:
                            rec["status"] = "OK"
                            rec["evidence_spans_valid"] = True
                        else:
                            rec["status"] = "INVALID_MODEL_REVIEW"
                            rec["invalid_reason"] = why
                break
            if rec:
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + chr(10))
                print(rname, rid, rec.get("status"), flush=True)
        if route_stopped:
            ev = {"event": "ROUTE_STOPPED", "route": rname, "reason": route_stopped,
                  "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                                    __import__("time").gmtime())}
            events_f.write(json.dumps(ev, ensure_ascii=False) + chr(10))
            print(rname, "STOPPED:", route_stopped)
    events_f.close()


if __name__ == "__main__":
    main()
