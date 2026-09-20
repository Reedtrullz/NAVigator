#!/usr/bin/env python3
"""Parallel variant of run_diagnostic.py (same contract, same budgets, 4 in flight per route).

Resume rule: any row already present in the results file (any status) is never re-called.
OK rows are reused; non-OK rows remain logged as final outcomes (no semantic retries).
"""
import json, hashlib, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

import run_diagnostic as base

HERE = base.HERE
WORKERS = 4

LOCK = threading.Lock()
STATE = {"tech_extra": 0, "json_mode": {}}
TECH_EXTRA_MAX = 15


def existing_rows(route_name):
    path = os.path.join(HERE, "results-%s.jsonl" % route_name.lower())
    present = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    rec = json.loads(l)
                    present.setdefault(rec["row_id"], rec)
    return present, path


def call_once(route, rname, system_prompt, user_prompt):
    with LOCK:
        jm = STATE["json_mode"].setdefault(rname, route["json_mode"])
    out = base.call(route, system_prompt, user_prompt, jm)
    return out, jm


def process_row(route, rname, row, sysp, up):
    rid = row["row_id"]
    attempt = 1
    while True:
        out, jm = call_once(route, rname, sysp, up)
        if "error" in out:
            code = out["code"]
            with LOCK:
                with open(os.path.join(HERE, "transport-events.jsonl"), "a", encoding="utf-8") as ef:
                    ef.write(json.dumps({"event": "TRANSPORT_ERROR", "route": rname, "row_id": rid,
                                         "attempt": attempt, "code": code, "error": out["error"],
                                         "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, ensure_ascii=False) + chr(10))
            if code in (402, 403):
                return {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                        "status": "ACCESS_FAILURE", "attempt": attempt, "error": out["error"]}
            if code == 400 and jm:
                with LOCK:
                    STATE["json_mode"][rname] = False
                    STATE["tech_extra"] += 1
                with open(os.path.join(HERE, "transport-events.jsonl"), "a", encoding="utf-8") as ef:
                    ef.write(json.dumps({"event": "JSON_MODE_DISABLED", "route": rname, "row_id": rid,
                                         "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, ensure_ascii=False) + chr(10))
                attempt += 1
                continue
            retry_ok = False
            with LOCK:
                if code in base.TECH_RETRIABLE and attempt == 1 and STATE["tech_extra"] < TECH_EXTRA_MAX:
                    STATE["tech_extra"] += 1
                    retry_ok = True
            if retry_ok:
                with open(os.path.join(HERE, "transport-events.jsonl"), "a", encoding="utf-8") as ef:
                    ef.write(json.dumps({"event": "TECHNICAL_RETRY", "route": rname, "row_id": rid,
                                         "code": code, "sleep_s": 30,
                                         "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, ensure_ascii=False) + chr(10))
                attempt += 1
                time.sleep(30)
                continue
            return {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                    "status": "TRANSPORT_ERROR", "attempt": attempt, "error": out["error"],
                    "elapsed_s": out["elapsed_s"], "request_fingerprint": out["request_fingerprint"]}
        raw = out.get("raw")
        finish = out.get("finish_reason")
        rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
               "attempt": attempt, "elapsed_s": out["elapsed_s"],
               "usage": out.get("usage", {}), "model_reported": out.get("model_reported"),
               "finish_reason": finish, "json_mode_effective": jm,
               "request_fingerprint": out["request_fingerprint"],
               "semantic_input_hash": base_sha["semantic_input_hash"],
               "dataset_sha256": base_sha["dataset_sha256"],
               "contract_view_sha256": base_sha["contract_view_sha256"]}
        if finish == "length":
            rec.update(status="TRANSPORT_CAPACITY_FAILURE", raw=(raw or "")[:2000])
        elif raw is None:
            rec["status"] = "EMPTY_RESPONSE"
        else:
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = None
            if parsed is None:
                rec.update(status="INVALID_JSON", raw=raw[:2000])
            else:
                ok, why = base.validate(row, parsed)
                rec["result"] = parsed
                rec["raw"] = raw
                if ok:
                    rec.update(status="OK", evidence_spans_valid=True)
                else:
                    rec.update(status="INVALID_MODEL_REVIEW", invalid_reason=why)
        return rec


base_sha = {}


def run_route(rname, rows, row_order, sysp, intro, labels):
    route = base.ROUTES[rname]
    present, path = existing_rows(rname)
    todo = [rid for rid in row_order if rid not in present]
    print(rname, "already present:", len(present), "todo:", len(todo), flush=True)
    done_count = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {}
        for rid in todo:
            row = rows[rid]
            up = base.build_user_prompt(row, intro, labels)
            futs[ex.submit(process_row, route, rname, row, sysp, up)] = rid
        for fut in as_completed(futs):
            rec = fut.result()
            with LOCK:
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + chr(10))
                done_count += 1
                if done_count % 10 == 0 or rec["status"] not in ("OK",):
                    print(rname, "progress:", done_count, "/", len(todo),
                          "last:", rec["row_id"], rec["status"], flush=True)
    return len(todo)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    rows = {}
    for l in open(os.path.join(base.LANE, "dataset-frozen.jsonl"), encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r["row_id"].startswith("FB1-SCR-"):
                rows[r["row_id"]] = r
    order = json.load(open(os.path.join(base.LANE, "lane-h-presentation-order.json"), encoding="utf-8"))
    row_order = [rid for k in sorted(order["blocks"]) for rid in order["blocks"][k]]
    intro, labels = base.load_contract_parts()
    sysp = json.load(open(os.path.join(base.ROOT,
        "evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json"),
        encoding="utf-8"))["semantic_instructions"]["system_prompt"]
    base_sha["semantic_input_hash"] = base.sha({"system": sysp, "intro": intro, "labels": labels,
        "dataset_sha": base.sha_file(os.path.join(base.LANE, "dataset-frozen.jsonl"))})
    base_sha["dataset_sha256"] = base.sha_file(os.path.join(base.LANE, "dataset-frozen.jsonl"))
    base_sha["contract_view_sha256"] = base.sha_file(os.path.join(base.LANE, "lane-h-diagnostic-contract-view-v1.md"))
    if mode == "verify":
        print("verify: nothing called; semantic_input_hash:", base_sha["semantic_input_hash"])
        return
    for rname in ("MIMO", "DEEPSEEK"):
        t0 = time.time()
        n = run_route(rname, rows, row_order, sysp, intro, labels)
        print(rname, "route done:", n, "rows in", round(time.time() - t0, 1), "s", flush=True)
    print("parallel run finished", flush=True)


if __name__ == "__main__":
    main()
