#!/usr/bin/env python3
"""Lane H cheap-model diagnostic V1 (owner-authorized, DEVELOPMENT_DIAGNOSTIC_ONLY).

Both reviewer routes get the identical semantic contract (neutral diagnostic view).
No reference labels, views, flags or other reviewers' answers are visible to the model.
Raw outcomes are persisted incrementally and locked before any reference comparison.
"""
import json, hashlib, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LANE))

AUTH = os.path.expanduser("~/.codex/auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
ENUM = ["CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT",
        "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED"]
SPAN_REQUIRED = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}
TECH_RETRIABLE = (429, 500, 502, 503, 504)

ROUTES = {
    "MIMO": {
        "wire_id": "command-code/xiaomi/mimo-v2.5-pro",
        "payload_extra": {"temperature": 0, "max_tokens": 32768},
        "json_mode": False,
    },
    "DEEPSEEK": {
        "wire_id": "B.AI/deepseek-v4-flash-vision-exp",
        "payload_extra": {},
        "json_mode": True,
    },
}


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_contract_parts():
    txt = open(os.path.join(LANE, "lane-h-diagnostic-contract-view-v1.md"), encoding="utf-8").read()
    s1 = txt.split("## 1. Neutral introduction (operative for this view)", 1)[1]
    intro = s1.split("## 2.", 1)[0].strip()
    blk = txt.split("~~~", 1)[1]
    labels = blk.split("~~~", 1)[0].strip()
    return intro, labels


def build_user_prompt(row, intro, labels):
    p = row["packet"]
    schema = '{"critical_evidence_state":"...","evidence_spans":["..."],"rationale":"kort"}'
    nl = chr(10)
    return ("### DIAGNOSTISK INSTRUKS" + nl + intro + nl + nl
            + "### ETIKETTDEFINISJONER (frozen contract, ordrett)" + nl + labels + nl + nl
            + "### SVARFORMAT (strict JSON)" + nl + schema + nl + nl
            + "### CASE CONTEXT" + nl + p["case_context"] + nl + nl
            + "### CRITERION (verbatim)" + nl + p["criterion"] + nl + nl
            + "### SUT OUTPUT" + nl + "<<<SUT" + nl + p["sut_output"] + nl + "SUT>>>" + nl + nl
            + "Klassifiser naa ifoelge instruksen. evidence_spans MAA vaere ordrett kopiert fra SUT OUTPUT.")


def call(route, system_prompt, user_prompt, json_mode, timeout_s=300):
    tok = json.load(open(AUTH))["tokens"]["access_token"]
    payload = {"model": route["wire_id"],
               "messages": [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}]}
    payload.update(route["payload_extra"])
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    fingerprint = sha({"wire_id": route["wire_id"], "payload_extra": route["payload_extra"],
                       "json_mode": json_mode, "system_sha": sha(system_prompt),
                       "user_sha": sha(user_prompt)})
    req = urllib.request.Request(PROXY, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=timeout_s))
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode(errors="replace")[:300]
        except Exception:
            pass
        return {"error": "HTTP_%d: %s" % (exc.code, body), "code": exc.code,
                "elapsed_s": round(time.time() - t0, 1), "request_fingerprint": fingerprint}
    except Exception as exc:
        return {"error": type(exc).__name__ + ": " + str(exc)[:200], "code": None,
                "elapsed_s": round(time.time() - t0, 1), "request_fingerprint": fingerprint}
    ch = resp.get("choices", [{}])[0]
    msg = ch.get("message", {})
    return {"raw": msg.get("content"), "finish_reason": ch.get("finish_reason"),
            "model_reported": resp.get("model"), "usage": resp.get("usage", {}),
            "elapsed_s": round(time.time() - t0, 1), "request_fingerprint": fingerprint}


def validate(row, parsed):
    if not isinstance(parsed, dict):
        return False, "not_object"
    st = parsed.get("critical_evidence_state")
    if st not in ENUM:
        return False, "label_not_in_enum"
    spans = parsed.get("evidence_spans")
    if not isinstance(spans, list) or not all(isinstance(s, str) for s in spans):
        return False, "spans_not_list"
    sut = row["packet"]["sut_output"]
    if not all(s in sut for s in spans):
        return False, "span_not_verbatim"
    if st in SPAN_REQUIRED and not spans:
        return False, "spans_required_missing"
    return True, ""


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    rows = {}
    for l in open(os.path.join(LANE, "dataset-frozen.jsonl"), encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r["row_id"].startswith("FB1-SCR-"):
                rows[r["row_id"]] = r
    order = json.load(open(os.path.join(LANE, "lane-h-presentation-order.json"), encoding="utf-8"))
    row_order = [rid for k in sorted(order["blocks"]) for rid in order["blocks"][k]]
    intro, labels = load_contract_parts()
    sysp = json.load(open(os.path.join(ROOT, "evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json"), encoding="utf-8"))["semantic_instructions"]["system_prompt"]
    dataset_sha = sha_file(os.path.join(LANE, "dataset-frozen.jsonl"))
    contract_view_sha = sha_file(os.path.join(LANE, "lane-h-diagnostic-contract-view-v1.md"))
    semantic_input_hash = sha({"system": sysp, "intro": intro, "labels": labels, "dataset_sha": dataset_sha})
    print("semantic_input_hash:", semantic_input_hash)

    events_path = os.path.join(HERE, "transport-events.jsonl")
    tech_extra_total = 0
    TECH_EXTRA_MAX = 15
    if os.path.exists(events_path):
        with open(events_path, encoding="utf-8") as ef:
            tech_extra_total = sum(1 for l in ef if l.strip() and json.loads(l).get("event") == "TECHNICAL_RETRY")
    print("technical retries already used:", tech_extra_total)

    if mode == "verify":
        print("verify mode: nothing called")
        return

    events_f = open(events_path, "a", encoding="utf-8")
    for rname in ("MIMO", "DEEPSEEK"):
        route = ROUTES[rname]
        out_path = os.path.join(HERE, "results-%s.jsonl" % rname.lower())
        done = set()
        if os.path.exists(out_path):
            with open(out_path, encoding="utf-8") as f:
                for l in f:
                    if l.strip():
                        rec = json.loads(l)
                        if rec.get("status") == "OK":
                            done.add(rec["row_id"])
            print(rname, "resume: completed rows found:", len(done))
        json_mode = route["json_mode"]
        route_stopped = None
        for rid in row_order:
            if route_stopped:
                break
            if rid in done:
                continue
            row = rows[rid]
            up = build_user_prompt(row, intro, labels)
            attempt = 1
            rec = None
            while True:
                out = call(route, sysp, up, json_mode)
                if "error" in out:
                    code = out["code"]
                    ev = {"event": "TRANSPORT_ERROR", "route": rname, "row_id": rid,
                          "attempt": attempt, "code": code, "error": out["error"],
                          "elapsed_s": out["elapsed_s"], "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    events_f.write(json.dumps(ev, ensure_ascii=False) + chr(10))
                    events_f.flush()
                    if code in (402, 403):
                        route_stopped = "ACCESS_FAILURE_%d" % code
                        rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                               "status": "ACCESS_FAILURE", "attempt": attempt,
                               "error": out["error"], "request_fingerprint": out["request_fingerprint"]}
                        break
                    if code == 400 and json_mode:
                        json_mode = False
                        ev2 = {"event": "JSON_MODE_DISABLED", "route": rname, "row_id": rid,
                               "reason": "HTTP 400 with response_format (preregistered transport fix)",
                               "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                        events_f.write(json.dumps(ev2, ensure_ascii=False) + chr(10))
                        events_f.flush()
                        attempt += 1
                        tech_extra_total += 1
                        continue
                    if code in TECH_RETRIABLE and attempt == 1 and tech_extra_total < TECH_EXTRA_MAX:
                        ev2 = {"event": "TECHNICAL_RETRY", "route": rname, "row_id": rid,
                               "code": code, "sleep_s": 30,
                               "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                        events_f.write(json.dumps(ev2, ensure_ascii=False) + chr(10))
                        events_f.flush()
                        tech_extra_total += 1
                        attempt += 1
                        time.sleep(30)
                        continue
                    rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                           "status": "TRANSPORT_ERROR", "attempt": attempt,
                           "error": out["error"], "elapsed_s": out["elapsed_s"],
                           "request_fingerprint": out["request_fingerprint"]}
                    break
                raw = out.get("raw")
                finish = out.get("finish_reason")
                rec = {"row_id": rid, "route": rname, "wire_id": route["wire_id"],
                       "attempt": attempt, "elapsed_s": out["elapsed_s"],
                       "usage": out.get("usage", {}), "model_reported": out.get("model_reported"),
                       "finish_reason": finish, "json_mode_effective": json_mode,
                       "request_fingerprint": out["request_fingerprint"],
                       "semantic_input_hash": semantic_input_hash,
                       "dataset_sha256": dataset_sha,
                       "contract_view_sha256": contract_view_sha}
                if finish == "length":
                    rec["status"] = "TRANSPORT_CAPACITY_FAILURE"
                    rec["raw"] = (raw or "")[:2000]
                elif raw is None:
                    rec["status"] = "EMPTY_RESPONSE"
                else:
                    try:
                        parsed = json.loads(raw)
                    except Exception:
                        parsed = None
                    if parsed is None:
                        rec["status"] = "INVALID_JSON"
                        rec["raw"] = raw[:2000]
                    else:
                        ok, why = validate(row, parsed)
                        rec["result"] = parsed
                        rec["raw"] = raw
                        if ok:
                            rec["status"] = "OK"
                            rec["evidence_spans_valid"] = True
                        else:
                            rec["status"] = "INVALID_MODEL_REVIEW"
                            rec["invalid_reason"] = why
                break
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + chr(10))
            print(rname, rid, rec.get("status"), flush=True)
        if route_stopped:
            ev = {"event": "ROUTE_STOPPED", "route": rname, "reason": route_stopped,
                  "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            events_f.write(json.dumps(ev, ensure_ascii=False) + chr(10))
            print(rname, "STOPPED:", route_stopped)
    events_f.close()
    print("run finished; technical retries total:", tech_extra_total)


if __name__ == "__main__":
    main()
