#!/usr/bin/env python3
"""Residual adjudication lane for Measurement V3 (owner-authorized, effort LOW).

Prompts are rebuilt from the frozen Batch-1 review prompt structure (no tuning).
Model-visible content comes only from residual-input-set.json (leakage-audited).
"""
import json, hashlib, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
INPUT_REL = "evaluation/measurement-v3-astra-integration-residual-v1/residual-input-set.json"
PACKETS_REL = "evaluation/measurement-v3-human-review-batch-2-repaired/human-review-packets.jsonl"
AUTH = os.path.expanduser("~/.codex/auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-6-astra"
EFFORT = "low"

REQ_CRIT = {"CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT"}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def system_prompt():
    return ("Du er en semantisk review-dommer. Du ser KUN packet-innholdet (case context, criterion, SUT-output). "
            "Ingen gold, ingen modellresultater, ingen ekstern research. Svar KUN med det paaeldte JSON-objektet.")


def user_prompt(p):
    schema = ('{"critical_evidence_state":"...","evidence_spans":["..."],"rationale":"kort"}'
              if p["dimension"] == "critical_condition" else
              '{"criterion_semantic_match":"...","speaker_commitment":"...","evidence_spans":["..."],"rationale":"kort"}')
    return ("### FROZEN CONTRACT\n" + p["contract_definitions"] + "\n\n"
            "### SVARFORMAT (strict JSON)\n" + schema + "\n\n"
            "### CASE CONTEXT\n" + p["case_context"] + "\n\n"
            "### CRITERION (verbatim)\n" + p["criterion"] + "\n\n"
            "### SUT OUTPUT\n<<<SUT\n" + p["sut_output"] + "\nSUT>>>\n\n"
            "Klassifiser naa ifoelge kontrakten. evidence_spans MAA vaere ordrett kopiert fra SUT OUTPUT.")


def spans_needed(p, res):
    if p["dimension"] == "critical_condition":
        return res.get("critical_evidence_state") in REQ_CRIT
    return res.get("criterion_semantic_match") == "MATCH" and res.get("speaker_commitment") != "UNRESOLVED"


def call_model(pass_name, p, packet_sha):
    tok = json.load(open(AUTH))["tokens"]["access_token"]
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_prompt()},
                     {"role": "user", "content": user_prompt(p)}],
        "reasoning_effort": EFFORT,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(PROXY, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    t0 = time.time()
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=600))
        raw = resp["choices"][0]["message"]["content"]
    except Exception as e:
        return {"packet_id": p["packet_id"], "pass": pass_name, "status": "TRANSPORT_ERROR",
                "error": type(e).__name__ + ": " + str(e)[:200], "elapsed_s": round(time.time() - t0, 1),
                "packet_sha256": packet_sha}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {"packet_id": p["packet_id"], "pass": pass_name, "status": "INVALID_JSON",
                "raw": raw[:2000], "packet_sha256": packet_sha}
    rec = {"packet_id": p["packet_id"], "pass": pass_name, "model": MODEL,
           "reasoning_effort": EFFORT, "packet_sha256": packet_sha,
           "request_config_hash": sha({"model": MODEL, "effort": EFFORT, "schema": payload["response_format"]}),
           "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "status": "OK", "result": parsed, "raw": raw}
    spans = parsed.get("evidence_spans", [])
    spans_verbatim = isinstance(spans, list) and all(isinstance(s, str) and s in p["sut_output"] for s in spans)
    need = spans_needed(p, parsed)
    rec["evidence_spans_valid"] = spans_verbatim and (bool(spans) if need else True)
    rec["spans_required_by_contract"] = need
    if not rec["evidence_spans_valid"]:
        rec["status"] = "INVALID_MODEL_REVIEW"
    return rec


def main():
    inp = json.load(open(os.path.join(ROOT, INPUT_REL)))
    pkts = inp["packets"]
    psha = {json.loads(l)["packet_id"]: json.loads(l)["packet_sha256"]
            for l in open(os.path.join(ROOT, PACKETS_REL)) if l.strip()}
    transport_log = {"artifact": "adjudication-transport-log",
                     "task_id": "NAV-EXPLORE-MEASUREMENT-V3-ASTRA-INTEGRATION-AND-RESIDUAL-ADJUDICATION-V1",
                     "input_set_sha256": sha_file(os.path.join(ROOT, INPUT_REL)),
                     "model": MODEL, "reasoning_effort": EFFORT,
                     "policy": "at most ONE technical retry per transport failure; no semantic retries",
                     "events": []}
    fa = os.path.join(HERE, "adjudication-pass-a.jsonl")
    fb = os.path.join(HERE, "adjudication-pass-b.jsonl")
    done_a = {json.loads(l)["packet_id"] for l in open(fa)} if os.path.exists(fa) else set()
    done_b = {json.loads(l)["packet_id"] for l in open(fb)} if os.path.exists(fb) else set()
    for p in pkts:
        pid = p["packet_id"]
        for fname, done, pass_name in ((fa, done_a, "ADJ_A"), (fb, done_b, "ADJ_B")):
            if pid in done:
                continue
            rec = call_model(pass_name, p, psha[pid])
            if rec["status"] == "TRANSPORT_ERROR":
                transport_log["events"].append({"packet_id": pid, "pass": pass_name,
                    "attempt": 1, "outcome": "TRANSPORT_ERROR", "error": rec.get("error"),
                    "timestamp_utc": rec.get("timestamp_utc") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                time.sleep(2)
                retry = call_model(pass_name, p, psha[pid])
                transport_log["events"].append({"packet_id": pid, "pass": pass_name,
                    "attempt": 2, "outcome": retry["status"], "retry_reason": "single permitted technical transport retry",
                    "timestamp_utc": retry.get("timestamp_utc") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                rec = retry
            with open(fname, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(pid, pass_name, rec["status"], flush=True)
            time.sleep(1)
    with open(os.path.join(HERE, "adjudication-transport-log.json"), "w") as f:
        json.dump(transport_log, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("EXECUTION_DONE")


if __name__ == "__main__":
    main()
