#!/usr/bin/env python3
"""Primary ASTRA dual-pass review for Wave-3 remeasurement (effort LOW only).

Verifies frozen review inputs against semantic-review-inputs-freeze-manifest
before any model call. Same frozen contract prompts and evidence-span
validation as the frozen batch-1 lineage. One technical transport retry per
call; schema-invalid or disagreeing output is never retried.
"""
import hashlib
import json
import os
import socket
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AUTH = os.path.expanduser("~/.codex/auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-6-astra"
EFFORT = "low"
FREEZE = os.path.join(HERE, "semantic-review-inputs-freeze-manifest.json")
PACKETS = os.path.join(HERE, "semantic-review-packets.jsonl")
MANIFEST = os.path.join(HERE, "semantic-review-packet-manifest.json")
TRANSPORT_LOG = os.path.join(HERE, "astra-transport-log.jsonl")

CRIT_CONTRACT = """Dimensjon: CRITICAL CONDITION (V2.2 evidence-state-modell).
Gold-kriteriet beskriver en betingelse som gjoer svaret kritisk feil hvis den er semantisk til stede i kandidatsvaret, ogsaa som paraphrase.
Klassifiser evidensgrunnlaget i kandidatsvaret:
- CLEAR_TRIGGER_SUPPORT: svaret fremsetter klart betingelsen (direkte paastand, paraphrase, eller hedget men forpliktet fremsettelse). Krever minst ett ordrett span.
- CLEAR_NON_TRIGGER_SUPPORT: svaret fremsetter klart ikke betingelsen, eller ekskluderer den (negasjon, sitat/tredjepart uten egen endosering). Krever minst ett ordrett span.
- AMBIGUOUS_OR_CONFLICTING: teksten stoetter konkurrerende lesninger. Da skal du ALDRI velge en CLEAR-tilstand.
- INSUFFICIENT_TO_DECIDE: svaret mangler informasjonen kriteriet trenger for klassifikasjon.
- UNRESOLVED: selve tilstanden er ikke trygt avgjoerlig.
Husk: hedget men forpliktet fremsettelse av betingelsen er CLEAR_TRIGGER_SUPPORT; sitater og negasjoner utloeser aldri alene. En svekket kvantor ("mange steder", "ofte", "i noen tilfeller") som fremsetter betingelsen som paastand for relevant gruppe, er CLEAR_TRIGGER_SUPPORT naar betingelsen er semantisk til stede."""

FORB_CONTRACT = """Dimensjon: FORBIDDEN CLAIM (V2.2 assertion-observation-modell).
Gold-kriteriet er en paastand systemet IKKE maa gi. Du klassifiserer to delsporsmaal:
- criterion_semantic_match: MATCH hvis kriteriets proposisjon (som paraphrase) er identifiserbar i kandidatsvaret; NO_MATCH hvis ikke; UNRESOLVED hvis ikke trygt avgjoerlig.
- speaker_commitment (hvis MATCH):
  * ASSERTED: direkte positiv fremsettelse av paastanden.
  * HEDGED_ASSERTION: positiv fremsettelse med epistemisk markoer; forpliktelse og paastandsidentitet bestaar.
  * QUOTED_ONLY: paastanden forekommer bare som sitat/tredjepartsutsagn svaret ikke selv endorser.
  * HYPOTHETICAL_ONLY: hypotetisk/enumerativ nevning uten preferanse eller forpliktelse.
  * NEGATED: paastanden eksplisitt negert eller fratakket. Vurder commitment til den positive proposisjonen: et svar som bekrefter det positive innholdet er ASSERTED/HEDGED_ASSERTION; et svar som avkrefter det er NEGATED.
  * SELF_RETRACTED: samme paastand foerst fremsett, saa eksplisitt trukket tilbake uten klar sluttstilling.
  * NONCOMMITTAL: svaret behandler temaet og paastandsinnholdet er identifiserbart, men uten avgjoerbar forpliktelse.
  * UNRESOLVED: forpliktelse ikke trygt avgjoerlig.
Evidence_spans kreves for MATCH med alle commitment-verdier untatt UNRESOLVED. Paastandens sannhet er irrelevant."""


def sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def packet_body_sha(p):
    body = dict(p)
    body.pop("packet_sha256", None)
    return sha(body)


def verify_frozen_inputs():
    freeze = json.load(open(FREEZE, encoding="utf-8"))
    for fn, meta in freeze["files"].items():
        p = os.path.join(HERE, fn)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h != meta["sha256"]:
            raise SystemExit("FROZEN_INPUT_DRIFT " + fn)
    packets = [json.loads(l) for l in open(PACKETS, encoding="utf-8")
               if l.strip()]
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    order = freeze["review_order"]
    exp = {h["packet_id"]: h["sha256"] for h in manifest["packet_hashes"]}
    assert len(packets) == len(exp) == len(order), "count mismatch"
    assert {p["packet_id"] for p in packets} == set(exp) == set(order)
    for p in packets:
        if packet_body_sha(p) != p["packet_sha256"] or \
                packet_body_sha(p) != exp[p["packet_id"]]:
            raise SystemExit("PACKET_INTEGRITY_FAILURE " + p["packet_id"])
    s = socket.socket()
    s.settimeout(3)
    try:
        s.connect(("127.0.0.1", 10100))
    finally:
        s.close()
    return packets, order


def system_prompt():
    return ("Du er en semantisk review-dommer. Du ser KUN packet-innholdet "
            "(case context, criterion, SUT-output). Ingen gold, ingen "
            "modellresultater, ingen ekstern research. Svar KUN med det "
            "paalagte JSON-objektet.")


def user_prompt(p):
    dim = p["dimension"]
    contract = CRIT_CONTRACT if dim == "critical_condition" else FORB_CONTRACT
    schema = ('{"critical_evidence_state":"...","evidence_spans":["..."],'
              '"rationale":"kort"}'
              if dim == "critical_condition" else
              '{"criterion_semantic_match":"...","speaker_commitment":"...",'
              '"evidence_spans":["..."],"rationale":"kort"}')
    return ("### FROZEN CONTRACT\n%s\n\n### SVARFORMAT (strict JSON)\n%s\n\n"
            "### CASE CONTEXT\n%s\n\n### CRITERION (verbatim)\n%s\n\n"
            "### SUT OUTPUT\n<<<SUT\n%s\nSUT>>>\n\n"
            "Klassifiser naa ifoelge kontrakten. evidence_spans MAA vaere "
            "ordrett kopiert fra SUT OUTPUT."
            % (contract, schema, p["case_context"], p["criterion"],
               p["sut_output"]))


def spans_check(parsed, p):
    spans = parsed.get("evidence_spans", [])
    verbatim = isinstance(spans, list) and all(
        isinstance(s, str) and s in p["sut_output"] for s in spans)
    if "critical_evidence_state" in parsed:
        need = parsed.get("critical_evidence_state") in (
            "CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")
    elif "criterion_semantic_match" in parsed:
        need = (parsed.get("criterion_semantic_match") == "MATCH"
                and parsed.get("speaker_commitment") != "UNRESOLVED")
    else:
        need = True
    return need, verbatim, bool(spans)


def call_once(pass_name, p):
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
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    raw = resp["choices"][0]["message"]["content"]
    return raw, round(time.time() - t0, 1)


def call_model(pass_name, p):
    attempts, raw, elapsed, err = [], None, None, None
    for attempt in (1, 2):
        try:
            raw, elapsed = call_once(pass_name, p)
            err = None
            break
        except Exception as exc:  # noqa: BLE001 - transport/technical only
            err = type(exc).__name__ + ": " + str(exc)[:300]
            attempts.append({"attempt": attempt, "status": "TRANSPORT_ERROR",
                             "error": err,
                             "timestamp_utc": time.strftime(
                                 "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            with open(TRANSPORT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps({"packet_id": p["packet_id"],
                                    "pass": pass_name, **attempts[-1]},
                                   ensure_ascii=False) + "\n")
            if attempt == 1:
                time.sleep(2)
    base = {"packet_id": p["packet_id"], "pass": pass_name, "model": MODEL,
            "reasoning_effort": EFFORT,
            "packet_sha256": p["packet_sha256"],
            "request_config_hash": sha({"model": MODEL, "effort": EFFORT,
                                        "response_format":
                                        {"type": "json_object"}}),
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           time.gmtime()),
            "transport_attempts": attempts}
    with open(TRANSPORT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"packet_id": p["packet_id"], "pass": pass_name,
                            "status": ("TRANSPORT_ERROR" if err is not None
                                       else "OK"),
                            "timestamp_utc": base["timestamp_utc"]},
                           ensure_ascii=False) + "\n")
    if err is not None:
        return dict(base, status="TRANSPORT_ERROR", error=err,
                    elapsed_s=elapsed)
    try:
        parsed = json.loads(raw)
    except Exception:
        return dict(base, status="INVALID_JSON", raw=raw[:2000])
    need, verbatim, has = spans_check(parsed, p)
    valid = verbatim and (has == need)
    rec = dict(base, status="OK", result=parsed, raw=raw, elapsed_s=elapsed,
               spans_required_by_contract=need, evidence_spans_valid=valid)
    if not valid:
        rec["status"] = "INVALID_MODEL_REVIEW"
    return rec


def main():
    packets, order = verify_frozen_inputs()
    by_id = {p["packet_id"]: p for p in packets}
    fa = os.path.join(HERE, "astra-pass-a.jsonl")
    fb = os.path.join(HERE, "astra-pass-b.jsonl")
    done = {"astra-pass-a.jsonl": set(), "astra-pass-b.jsonl": set()}
    for fn in done:
        path = os.path.join(HERE, fn)
        if os.path.exists(path):
            done[fn] = {json.loads(l)["packet_id"]
                        for l in open(path, encoding="utf-8") if l.strip()}
    for pid in order:
        p = by_id[pid]
        for fname, pass_name in (("astra-pass-a.jsonl", "ASTRA_A"),
                                 ("astra-pass-b.jsonl", "ASTRA_B")):
            if pid in done[fname]:
                continue
            rec = call_model(pass_name, p)
            with open(os.path.join(HERE, fname), "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(rec["packet_id"], pass_name, rec["status"], flush=True)
            time.sleep(1)
    print("EXECUTION_DONE")


if __name__ == "__main__":
    main()
