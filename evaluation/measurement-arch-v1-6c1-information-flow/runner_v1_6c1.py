#!/usr/bin/env python3
"""V1.6C.1 NEW-arm runner: one-shot NEW-flow judge calls on burned residuals.

OLD arm = frozen checkpoint replay (no calls). NEW arm = same frozen judge
core mechanics, same model/provider/config/schemas; the user prompt carries
the semantic residual packet. No tuning after first call (enforced by
contract; no packet or prompt edits permitted once execution starts).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
V14 = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-4"))
V6B = os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6b"))
sys.path.insert(0, HERE)
sys.path.insert(0, V14)
sys.path.insert(0, V6B)

from packet_builder import build_packet  # noqa: E402
import judge_core_v1_4 as J  # noqa: E402

MODEL = "command-code/xiaomi/mimo-v2.5-pro"
CKPT_SHA = "a5e9d87a18e649cf365d84ad3ee6e9358171c69340ff59357a06aaabfec6597e"
SET_SHA = None  # verified from ab-evaluation-set.json at runtime


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def structure_block(packet):
    keys = ["clause_spans", "route_candidates", "quote_spans", "negation_spans",
            "retraction_spans", "hedge_spans", "assertion_spans",
            "conditional_spans", "attribution_spans", "vague_spans",
            "deterministic_evidence", "a3"]
    return {k: packet[k] for k in keys if packet.get(k)}


def build_user_prompt_new(dimension, case_context, gold_criterion, sut_answer, packet):
    base = json.loads(J.build_user_prompt(dimension, case_context,
                                          gold_criterion, sut_answer))
    base["deterministic_structure"] = structure_block(packet)
    base["deterministic_structure_note"] = (
        "Strukturen under er mekanisk produsert av den deterministiske "
        "analysen (klauseinndeling, markoerfund, abstain-aarsak). Den er "
        "kontekst for din vurdering, ikke fasit. Kontroller strukturen mot "
        "originalteksten og vurder selv.")
    return json.dumps(base, ensure_ascii=False)


def call_judge_new(dimension, case_context, gold_criterion, sut_answer, packet):
    labels = {"critical_condition": J.CRITICAL_LABELS,
              "forbidden_claim": J.FORBIDDEN_LABELS,
              "route_correctness": J.ROUTE_LABELS,
              "required_uncertainty": J.UNC_LABELS}[dimension]
    body = json.dumps({
        "model": J.MODEL, "temperature": J.TEMPERATURE,
        "max_tokens": J.MAX_TOKENS,
        "messages": [
            {"role": "system", "content": J.SYSTEM_PROMPT},
            {"role": "system", "content": J.DIMENSION_INSTRUCTIONS[dimension]},
            {"role": "user", "content": build_user_prompt_new(
                dimension, case_context, gold_criterion, sut_answer, packet)},
        ],
    }).encode()
    telemetry = {"model": J.MODEL, "provider": J.PROVIDER,
                 "max_tokens": J.MAX_TOKENS, "temperature": J.TEMPERATURE,
                 "retries": 0}
    import urllib.request
    import urllib.error
    last_error = None
    for attempt in range(J.MAX_TECHNICAL_RETRIES + 1):
        if attempt:
            telemetry["retries"] += 1
            time.sleep(J.RETRY_SLEEP_SECONDS)
        start = time.time()
        try:
            req = urllib.request.Request(
                J.PROXY_URL, data=body,
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer " + J._api_key()})
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            content = choice["message"].get("content") or ""
            telemetry.update({
                "finish_reason": choice.get("finish_reason"),
                "usage": data.get("usage"),
                "latency_seconds": round(time.time() - start, 2)})
            if telemetry["finish_reason"] == "length":
                return {"status": "TRANSPORT_CAPACITY_FAILURE",
                        "telemetry": telemetry, "error": "finish_reason=length"}
            parsed = J._parse_json_loose(content)
            result = J.validate_result(dimension, parsed, sut_answer)
            return {"status": "OK", "result": result, "telemetry": telemetry}
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            err = str(exc)
            if "429" in err and attempt < J.MAX_TECHNICAL_RETRIES:
                continue
            if attempt < J.MAX_TECHNICAL_RETRIES and not (
                    isinstance(exc, ValueError) or "not" in err.lower() and "verbatim" in err.lower()):
                continue
    return {"status": "ERROR", "telemetry": telemetry,
            "error": str(last_error)[:300]}


def main():
    global SET_SHA
    set_doc = json.load(open(os.path.join(HERE, "ab-evaluation-set.json")))
    SET_SHA = set_doc["set_sha256"]
    ckpt_sha = sha(os.path.join(V6B, "screening-checkpoint-mimo-v2-5-pro.json"))
    assert ckpt_sha == CKPT_SHA, f"OLD-arm checkpoint drifted: {ckpt_sha}"
    out_path = os.path.join(HERE, "new-flow-results.json")
    rows = []
    if os.path.exists(out_path):
        rows = json.load(open(out_path))["rows"]
        assert json.load(open(out_path)).get("set_sha256") == SET_SHA
    done = {r["id"] for r in rows}
    for row in set_doc["rows"]:
        rid = row["id"]
        if rid in done:
            continue
        fx_doc_row = row
        fx = json.load(open(os.path.join(V6B, "screening-fixtures.json")))
        f = {x["id"]: x for x in fx["fixtures"]}[rid]
        packet = build_packet(f["dimension"], f["crit"], f["sut"], f.get("ctx", ""))
        t = call_judge_new(f["dimension"], f.get("ctx", ""), f["crit"], f["sut"], packet)
        out_row = {"id": rid, "dimension": row["dimension"],
                   "gold_verdict": row["gold_verdict"],
                   "old_verdict": row["old_verdict"],
                   "old_verdict_correct": row["old_verdict_correct"],
                   "status": t["status"], "telemetry": t.get("telemetry")}
        if t["status"] == "OK":
            res = t["result"]
            out_row["result"] = res
            out_row["verdict"] = res["verdict"]
            out_row["verdict_correct"] = res["verdict"] == row["gold_verdict"]
            ev_ok = all(J.norm(s) in J.norm(f["sut"])
                        for s in res.get("evidence_spans", []))
            out_row["evidence_valid"] = ev_ok
        else:
            out_row["error"] = t.get("error")
        rows.append(out_row)
        tag = out_row.get("verdict", t["status"])
        print(f"{len(rows)}/92 {rid} [{row['dimension']}] {tag} "
              f"{'OK' if out_row.get('verdict_correct') else 'WRONG/ERR'}", flush=True)
        doc = {"artifact": "V1.6C.1 NEW-FLOW RESULTS",
               "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
               "set_sha256": SET_SHA, "checkpoint_sha_verified": ckpt_sha,
               "model": MODEL, "rows": rows}
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    print("DONE", len(rows), flush=True)


if __name__ == "__main__":
    main()
