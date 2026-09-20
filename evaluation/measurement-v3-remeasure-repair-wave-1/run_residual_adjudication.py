#!/usr/bin/env python3
"""Blind residual ADJ-A/ADJ-B for Wave-1 remeasure (gpt-6-astra, LOW only).

Prompts use the exact frozen primary contract wording and the canonical
residual-lane blind-input structure. No primary results or gold visible."""
import hashlib
import importlib.util
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AUTH = os.path.expanduser("~/.codex/auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-6-astra"
EFFORT = "low"
REQ_CRIT = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}
_spec = importlib.util.spec_from_file_location(
    "frozen_astra_review",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "run_astra_review.py"))
_review = importlib.util.module_from_spec(_spec)
import sys as _sys
_sys.modules["frozen_astra_review"] = _review
_spec.loader.exec_module(_review)
CONTRACTS = {"critical_condition": _review.CRIT_CONTRACT,
             "forbidden_claim": _review.FORB_CONTRACT}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def system_prompt():
    return ("Du er en semantisk review-dommer. Du ser KUN packet-innholdet "
            "(case context, criterion, SUT-output). Ingen gold, ingen "
            "modellresultater, ingen ekstern research. Svar KUN med det "
            "paalagte JSON-objektet.")


def user_prompt(p):
    schema = ('{"critical_evidence_state":"...","evidence_spans":["..."],'
              '"rationale":"kort"}'
              if p["dimension"] == "critical_condition" else
              '{"criterion_semantic_match":"...","speaker_commitment":"...",'
              '"evidence_spans":["..."],"rationale":"kort"}')
    return ("### FROZEN CONTRACT\n%s\n\n### SVARFORMAT (strict JSON)\n%s\n\n"
            "### CASE CONTEXT\n%s\n\n### CRITERION (verbatim)\n%s\n\n"
            "### SUT OUTPUT\n<<<SUT\n%s\nSUT>>>\n\n"
            "Klassifiser naa ifoelge kontrakten. evidence_spans MAA vaere "
            "ordrett kopiert fra SUT OUTPUT."
            % (CONTRACTS[p["dimension"]], schema, p["case_context"],
               p["criterion"], p["sut_output"]))


def spans_needed(p, res):
    if p["dimension"] == "critical_condition":
        return res.get("critical_evidence_state") in REQ_CRIT
    return (res.get("criterion_semantic_match") == "MATCH"
            and res.get("speaker_commitment") != "UNRESOLVED")


def call_model(pass_name, p):
    tok = json.load(open(AUTH))["tokens"]["access_token"]
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_prompt()},
                     {"role": "user", "content": user_prompt(p)}],
        "reasoning_effort": EFFORT,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        PROXY, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"})
    t0 = time.time()
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=600))
        raw = resp["choices"][0]["message"]["content"]
    except Exception as exc:
        return {"packet_id": p["packet_id"], "pass": pass_name,
                "status": "TRANSPORT_ERROR",
                "error": type(exc).__name__ + ": " + str(exc)[:200],
                "elapsed_s": round(time.time() - t0, 1),
                "packet_sha256": p["packet_sha256"]}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {"packet_id": p["packet_id"], "pass": pass_name,
                "status": "INVALID_JSON", "raw": raw[:2000],
                "packet_sha256": p["packet_sha256"]}
    spans = parsed.get("evidence_spans", [])
    verbatim = isinstance(spans, list) and all(
        isinstance(s, str) and s in p["sut_output"] for s in spans)
    need = spans_needed(p, parsed)
    valid = verbatim and (bool(spans) == need)
    rec = {"packet_id": p["packet_id"], "pass": pass_name, "model": MODEL,
           "reasoning_effort": EFFORT, "packet_sha256": p["packet_sha256"],
           "request_config_hash": sha({"model": MODEL, "effort": EFFORT,
                                       "response_format": {"type": "json_object"}}),
           "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "status": "OK", "result": parsed, "raw": raw,
           "spans_required_by_contract": need, "evidence_spans_valid": valid}
    if not valid:
        rec["status"] = "INVALID_MODEL_REVIEW"
    return rec


def main():
    inp = json.load(open(os.path.join(HERE, "residual-inputs.json"), encoding="utf-8"))
    pkts = inp["packets"]
    transport = {"artifact": "adjudication-transport-log",
                 "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1",
                 "model": MODEL, "reasoning_effort": EFFORT,
                 "policy": "at most ONE technical retry per transport failure",
                 "events": []}
    fa = os.path.join(HERE, "adjudication-pass-a.jsonl")
    fb = os.path.join(HERE, "adjudication-pass-b.jsonl")
    done_a = {json.loads(l)["packet_id"] for l in open(fa)} if os.path.exists(fa) else set()
    done_b = {json.loads(l)["packet_id"] for l in open(fb)} if os.path.exists(fb) else set()
    for p in pkts:
        for fname, done, name in ((fa, done_a, "ADJ_A"), (fb, done_b, "ADJ_B")):
            if p["packet_id"] in done:
                continue
            rec = call_model(name, p)
            if rec["status"] == "TRANSPORT_ERROR":
                transport["events"].append({"packet_id": p["packet_id"],
                                            "pass": name, "attempt": 1,
                                            "outcome": "TRANSPORT_ERROR",
                                            "error": rec.get("error")})
                time.sleep(2)
                retry = call_model(name, p)
                transport["events"].append({"packet_id": p["packet_id"],
                                            "pass": name, "attempt": 2,
                                            "outcome": retry["status"],
                                            "retry_reason": "single permitted technical transport retry"})
                rec = retry
            with open(fname, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(p["packet_id"], name, rec["status"], flush=True)
            time.sleep(1)
    with open(os.path.join(HERE, "adjudication-transport-log.json"), "w",
              encoding="utf-8") as f:
        json.dump(transport, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("EXECUTION_DONE")


if __name__ == "__main__":
    main()
