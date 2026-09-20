#!/usr/bin/env python3
"""ASTRA review lane for Measurement V3 Batch 1 (owner-authorized, effort LOW)."""
import json, hashlib, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACKETS_REL = "evaluation/measurement-v3-human-review-batch-2-repaired/human-review-packets.jsonl"
MANIFEST_REL = "evaluation/measurement-v3-human-review-batch-2-repaired/human-review-batch-manifest.json"
ORDER_REL = "evaluation/measurement-v3-human-review-batch-2-repaired/review-order.json"
AUTH = os.path.expanduser("~/.codex/auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-6-astra"
EFFORT = "low"

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
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def packet_body_sha(p):
    body = dict(p); body.pop("packet_sha256", None)
    return sha(body)

def verify_inputs():
    packets = [json.loads(l) for l in open(os.path.join(ROOT, PACKETS_REL)) if l.strip()]
    manifest = json.load(open(os.path.join(ROOT, MANIFEST_REL)))
    order = json.load(open(os.path.join(ROOT, ORDER_REL)))
    exp = {h["packet_id"]: h["sha256"] for h in manifest["packet_hashes"]}
    ids = [p["packet_id"] for p in packets]
    assert len(packets) == 74 == len(exp) == len(order["packet_ids"]), "count mismatch"
    assert sorted(ids) == sorted(exp.keys()) == sorted(order["packet_ids"]), "id mismatch"
    for p in packets:
        if packet_body_sha(p) != p["packet_sha256"] or packet_body_sha(p) != exp[p["packet_id"]]:
            raise SystemExit("INTEGRITY_FAILURE " + p["packet_id"])
    return packets, order

def system_prompt():
    return ("Du er en semantisk review-dommer. Du ser KUN packet-innholdet (case context, criterion, SUT-output). "
            "Ingen gold, ingen modellresultater, ingen ekstern research. Svar KUN med det paaeldte JSON-objektet.")

def user_prompt(p):
    dim = p["dimension"]
    contract = CRIT_CONTRACT if dim == "critical_condition" else FORB_CONTRACT
    schema = ('{"critical_evidence_state":"...","evidence_spans":["..."],"rationale":"kort"}'
              if dim == "critical_condition" else
              '{"criterion_semantic_match":"...","speaker_commitment":"...","evidence_spans":["..."],"rationale":"kort"}')
    return (f"### FROZEN CONTRACT\n{contract}\n\n"
            f"### SVARFORMAT (strict JSON)\n{schema}\n\n"
            f"### CASE CONTEXT\n{p['case_context']}\n\n"
            f"### CRITERION (verbatim)\n{p['criterion']}\n\n"
            f"### SUT OUTPUT\n<<<SUT\n{p['sut_output']}\nSUT>>>\n\n"
            "Klassifiser naa ifoelge kontrakten. evidence_spans MAA vaere ordrett kopiert fra SUT OUTPUT.")

def call_model(pass_name, p):
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
                "error": type(e).__name__ + ": " + str(e)[:200], "elapsed_s": round(time.time()-t0, 1)}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {"packet_id": p["packet_id"], "pass": pass_name, "status": "INVALID_JSON",
                "raw": raw[:2000]}
    rec = {"packet_id": p["packet_id"], "pass": pass_name, "model": MODEL,
           "reasoning_effort": EFFORT, "packet_sha256": p["packet_sha256"],
           "request_config_hash": sha({"model": MODEL, "effort": EFFORT, "schema": payload["response_format"]}),
           "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "status": "OK", "result": parsed, "raw": raw}
    spans = parsed.get("evidence_spans", [])
    spans_verbatim = isinstance(spans, list) and all(isinstance(s, str) and s in p["sut_output"] for s in spans)
    # Contract: spans required only when the claim/condition is asserted (MATCH with
    # commitment, or a CLEAR_* critical state). Empty spans are otherwise legal.
    if "critical_evidence_state" in parsed:
        need = parsed.get("critical_evidence_state") in ("CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")
    elif "criterion_semantic_match" in parsed:
        need = (parsed.get("criterion_semantic_match") == "MATCH"
                and parsed.get("speaker_commitment") != "UNRESOLVED")
    else:
        need = True
    rec["evidence_spans_valid"] = (bool(spans) == need) and spans_verbatim
    rec["spans_required_by_contract"] = need
    if not rec["evidence_spans_valid"]:
        rec["status"] = "INVALID_MODEL_REVIEW"
    return rec

def main():
    if "--resume" in sys.argv:
        fa, fb = os.path.join(HERE, "astra-pass-a.jsonl"), os.path.join(HERE, "astra-pass-b.jsonl")
        done_a = {json.loads(l)["packet_id"] for l in open(fa)} if os.path.exists(fa) else set()
        done_b = {json.loads(l)["packet_id"] for l in open(fb)} if os.path.exists(fb) else set()
    else:
        done_a, done_b = set(), set()
    packets, order = verify_inputs()
    by_id = {p["packet_id"]: p for p in packets}
    for pid in order["packet_ids"]:
        p = by_id[pid]
        for fname, done, pass_name in (("astra-pass-a.jsonl", done_a, "ASTRA_A"), ("astra-pass-b.jsonl", done_b, "ASTRA_B")):
            if pid in done:
                continue
            rec = call_model(pass_name, p)
            with open(os.path.join(HERE, fname), "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(rec["packet_id"], pass_name, rec["status"], flush=True)
            time.sleep(1)
    print("EXECUTION_DONE")

if __name__ == "__main__":
    main()
