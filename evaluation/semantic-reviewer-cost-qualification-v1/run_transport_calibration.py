#!/usr/bin/env python3
"""Stage 0: transport calibration for the five primary candidates.

Runs the frozen TRANSPORT partitions (13 forbidden + 6 critical rows per
candidate) through each candidate route on the local commandcode proxy.
May fix ONLY transport issues (JSON mode, parsing, enum serialization).
Semantic performance on this partition does NOT qualify any candidate.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CORPUS = os.path.join(HERE, "reference-corpus.jsonl")
SPLIT = os.path.join(HERE, "qualification-split.json")
CONTRACT = os.path.join(HERE, "qualification-contract.json")
OUT = os.path.join(HERE, "transport-screen-results.json")
AUTH = os.path.join(os.path.expanduser("~"), ".codex", "auth.json")
PROXY = "http://127.0.0.1:10100/v1/chat/completions"

CANDIDATES = [
    {"logical_id": "nemotron-3-ultra", "wire_id": "RouteOpen/nemotron-3-ultra-550b-a55b"},
    {"logical_id": "nex-n2.5-pro", "wire_id": "openrouter/nex-agi/nex-n2.5-pro:free"},
    {"logical_id": "gemma-4-31b-it", "wire_id": "openrouter/google/gemma-4-31b-it:free"},
    {"logical_id": "mimo-v2.5-pro", "wire_id": "command-code/xiaomi/mimo-v2.5-pro"},
    {"logical_id": "inkling", "wire_id": "openrouter/thinkingmachines/inkling:free"},
]


def load_frozen():
    contract = json.load(open(CONTRACT, encoding="utf-8"))
    split = json.load(open(SPLIT, encoding="utf-8"))
    rows = {}
    for line in open(CORPUS, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            rows[r["canonical_hash"]] = r
    return contract, split, rows


def call_model(wire_id, system_prompt, user_prompt, use_json_mode):
    tok = json.load(open(AUTH))["tokens"]["access_token"]
    payload = {
        "model": wire_id,
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": user_prompt}],
    }
    if use_json_mode:
        payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        PROXY, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"})
    t0 = time.time()
    resp = json.load(urllib.request.urlopen(req, timeout=90))
    elapsed = round(time.time() - t0, 1)
    raw = resp["choices"][0]["message"]["content"]
    usage = resp.get("usage", {})
    return raw, elapsed, usage


def spans_ok(parsed, sut):
    spans = parsed.get("evidence_spans", [])
    verbatim = isinstance(spans, list) and all(
        isinstance(s, str) and s in sut for s in spans)
    if "critical_evidence_state" in parsed:
        need = parsed.get("critical_evidence_state") in (
            "CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")
    elif "criterion_semantic_match" in parsed:
        need = (parsed.get("criterion_semantic_match") == "MATCH"
                and parsed.get("speaker_commitment") != "UNRESOLVED")
    else:
        need = True
    return need, verbatim, bool(spans)


def validate(parsed, row, contract):
    lane = row["lane"]
    enums = contract["semantic_instructions"]["enum_domains"]
    schema_valid = isinstance(parsed, dict)
    enum_valid = True
    if lane == "critical_condition":
        schema_valid = schema_valid and "critical_evidence_state" in parsed
        enum_valid = parsed.get("critical_evidence_state") in enums[
            "critical_evidence_state"]
    else:
        schema_valid = schema_valid and (
            "criterion_semantic_match" in parsed
            and "speaker_commitment" in parsed)
        enum_valid = (parsed.get("criterion_semantic_match")
                      in enums["criterion_semantic_match"]
                      and parsed.get("speaker_commitment")
                      in enums["speaker_commitment"])
    need, verbatim, has = spans_ok(parsed, row["packet"]["sut_output"])
    evidence_valid = verbatim and (has == need)
    return schema_valid, enum_valid, evidence_valid


def build_prompts(row, contract):
    si = contract["semantic_instructions"]
    lane = row["lane"]
    system_prompt = si["system_prompt"]
    contract_text = (si["critical_contract"] if lane == "critical_condition"
                     else si["forbidden_contract"])
    schema = si["schemas"][lane]
    p = row["packet"]
    user_prompt = (
        "### FROZEN CONTRACT\n%s\n\n### SVARFORMAT (strict JSON)\n%s\n\n"
        "### CASE CONTEXT\n%s\n\n### CRITERION (verbatim)\n%s\n\n"
        "### SUT OUTPUT\n<<<SUT\n%s\nSUT>>>\n\n"
        "Klassifiser naa ifoelge kontrakten. evidence_spans MAA vaere "
        "ordrett kopiert fra SUT OUTPUT."
        % (contract_text, schema, p["case_context"], p["criterion"],
           p["sut_output"]))
    return system_prompt, user_prompt


def run_candidate(cand, rows, contract):
    wire_id = cand["wire_id"]
    results = []
    json_mode = True  # transport fix path: disable on unsupported errors
    for chash in rows:
        row = rows[chash]
        print("  row", row["packet_id"], row["lane"], flush=True)
        system_prompt, user_prompt = build_prompts(row, contract)
        rec = {"logical_id": cand["logical_id"],
               "canonical_hash": chash,
               "lane": row["lane"]}
        attempts = []
        raw, parsed, elapsed, usage, err = None, None, None, None, None
        for attempt in (1, 2):
            try:
                raw, elapsed, usage = call_model(
                    wire_id, system_prompt, user_prompt, json_mode)
                err = None
                break
            except urllib.error.HTTPError as exc:
                body = ""
                try:
                    body = exc.read().decode(errors="replace")[:300]
                except Exception:
                    pass
                err = "HTTP_%d: %s" % (exc.code, body)
                if exc.code in (400, 422) and json_mode:
                    json_mode = False  # provider-specific structured-output fix
                attempts.append({"attempt": attempt, "error": err[:300]})
            except Exception as exc:
                err = type(exc).__name__ + ": " + str(exc)[:300]
                attempts.append({"attempt": attempt, "error": err[:300]})
        rec["attempts"] = attempts
        if err is not None:
            rec.update(status="TRANSPORT_ERROR", error=err[:300])
            results.append(rec)
            continue
        try:
            parsed = json.loads(raw)
        except Exception:
            rec.update(status="INVALID_JSON", raw=raw[:300], elapsed_s=elapsed)
            results.append(rec)
            continue
        schema_valid, enum_valid, evidence_valid = validate(parsed, row, contract)
        valid = schema_valid and enum_valid and evidence_valid
        rec.update(status="OK" if valid else "INVALID_MODEL_REVIEW",
                   schema_valid=schema_valid, enum_valid=enum_valid,
                   evidence_valid=evidence_valid, elapsed_s=elapsed,
                   usage=usage, parsed=parsed)
        results.append(rec)
        with open(os.path.join(HERE, "transport-progress-%s.jsonl" % cand["logical_id"].replace("/", "_")), "a", encoding="utf-8") as pf:
            pf.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return results


def main():
    contract, split, rows = load_frozen()
    todo = {c["logical_id"]: c for c in CANDIDATES}
    state = {"candidates": {}}
    if os.path.exists(OUT):
        state = json.load(open(OUT, encoding="utf-8"))
        for lid in list(state["candidates"]):
            if lid not in todo:
                del state["candidates"][lid]
    for cand in CANDIDATES:
        lid = cand["logical_id"]
        if lid in state["candidates"]:
            print("SKIP (already calibrated):", lid)
            continue
        hashes = (split["partitions"]["forbidden_claim"].get("TRANSPORT", [])
                  + split["partitions"]["critical_condition"].get("TRANSPORT", []))
        print("calibrating", lid, "rows:", len(hashes))
        results = run_candidate(cand, {h: rows[h] for h in hashes}, contract)
        ok = sum(1 for r in results if r["status"] == "OK")
        terr = sum(1 for r in results if r["status"] == "TRANSPORT_ERROR")
        inv = sum(1 for r in results if r["status"] == "INVALID_MODEL_REVIEW")
        ij = sum(1 for r in results if r["status"] == "INVALID_JSON")
        state["candidates"][lid] = {
            "wire_id": cand["wire_id"],
            "rows": len(results), "ok": ok, "transport_errors": terr,
            "invalid_model_reviews": inv, "invalid_json": ij,
            "results": results,
        }
        print("  ->", lid, "ok:", ok, "terr:", terr, "inv:", inv, "ij:", ij)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    print("DONE")


if __name__ == "__main__":
    main()
