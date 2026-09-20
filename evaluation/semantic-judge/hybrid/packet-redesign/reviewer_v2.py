"""Reviewer bridge for packet-v2.1 (per-atom evidence groups).

Doctrine is the frozen v1.1 semantic reviewer (no new semantic rules);
the only prompt change is syntactic schema support (spec 32).  Output
is per-atom verdicts; claim aggregation is deterministic via the
frozen aggregate() spec.  Fusion keeps hard-contra and injection
locks and confidence gating.  INSUFFICIENT stays first-class.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HY = os.path.dirname(HERE)
JUDGE_DIR = os.path.join(os.path.dirname(HY), "quote-aligner", "v0.2")
ALIGN_DIR = os.path.dirname(JUDGE_DIR)
for p in (JUDGE_DIR, ALIGN_DIR, HY, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from polarity_engine import aggregate  # noqa: E402
from reviewer import (_api_key, _hard_contra_locked, classify_threshold,
                      PROXY_URL, MODEL, TEMPERATURE,
                      MAX_TOKENS)  # noqa: E402
import packet_router  # noqa: E402

SCHEMA_VERSION = packet_router.SCHEMA_VERSION
BS = chr(92)

BASE_PROMPT_DEF = open(os.path.join(HY, "reviewer.py"),
                       encoding="utf-8").read()
_m = re.search(r"SYSTEM_PROMPT = \"\"\"(.*?)\"\"\"", BASE_PROMPT_DEF, re.DOTALL)
BASE_PROMPT = _m.group(1) if _m else ""

SYNTAX_ADDENDUM_LINES = [
    "8. Packet-skjema: claimet er delt i atomer (A1, A2, ...). Hvert atom har kandidat-evidence (span_id, roles, relation) og det finnes en felles candidate_spans-liste med selve span-teksten.",
    "9. relation single_support: spanet alene dekker atomet. relation joint_support: spans i evidence_set maa kombineres for aa dekke atomet. relation qualifier: kontekst. group_type RULE_WITH_CONDITION/RULE_WITH_EXCEPTION markerer koblede regler.",
    "10. Output per atom, KUN gyldig JSON, ingen annen tekst:",
    "   {\"atoms\": [{\"atom_id\": \"A1\", \"verdict\": \"SUPPORTED\", \"evidence_span_ids\": [\"S2\"], \"confidence\": 0.95, \"needs_human_review\": false}], \"reason_code\": \"kort_snake_case\"}",
    "11. Alle atomer skal vaere representert i output. evidence_span_ids maa vaere span_id-er fra atomets egen kandidat-evidence-liste."
]
SYSTEM_PROMPT_V2 = BASE_PROMPT.rstrip() + "\n\n" + "\n".join(SYNTAX_ADDENDUM_LINES)
_PROMPT_SHA = hashlib.sha256(SYSTEM_PROMPT_V2.encode()).hexdigest()[:16]

VERDICTS = {"SUPPORTED", "CONTRADICTED", "PARTIAL", "INSUFFICIENT"}


def prompt_meta():
    return {"prompt_sha": _PROMPT_SHA, "model": MODEL,
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "packet_schema": SCHEMA_VERSION}


def call_luna_v2(packet, transport=None):
    if transport is None:
        def transport(messages):
            req = urllib.request.Request(
                PROXY_URL,
                data=json.dumps({"model": MODEL, "temperature": TEMPERATURE,
                                 "max_tokens": MAX_TOKENS,
                                 "messages": messages}).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer " + _api_key()})
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.load(resp)
            return body["choices"][0]["message"]["content"]
    user_msg = json.dumps(packet, ensure_ascii=False)
    raw = transport([{"role": "system", "content": SYSTEM_PROMPT_V2},
                     {"role": "user", "content": user_msg}])
    try:
        return json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(),
                                 flags=re.MULTILINE).strip())
    except (json.JSONDecodeError, AttributeError):
        return None


def validate_fidelity_v2(packet, output):
    """None if output passes deterministic checks, else reason."""
    if not isinstance(output, dict):
        return "not_json_object"
    atoms_out = output.get("atoms")
    if not isinstance(atoms_out, list) or not atoms_out:
        return "missing_atoms"
    pkt_atoms = {a["atom_id"]: a for a in packet["atoms"]}
    span_ids = {s["span_id"] for s in packet["candidate_spans"]}
    seen = set()
    for a in atoms_out:
        if not isinstance(a, dict):
            return "atom_not_object"
        aid = a.get("atom_id")
        if aid not in pkt_atoms:
            return "unknown_atom_id:%s" % aid
        if aid in seen:
            return "duplicate_atom_id:%s" % aid
        seen.add(aid)
        verdict = a.get("verdict")
        if verdict not in VERDICTS:
            return "bad_verdict:%s" % verdict
        conf = a.get("confidence")
        if not isinstance(conf, (int, float)) or not 0.0 <= conf <= 1.0:
            return "bad_confidence"
        if verdict in ("SUPPORTED", "CONTRADICTED", "PARTIAL"):
            ev = a.get("evidence_span_ids") or []
            if not isinstance(ev, list) or any(x not in span_ids for x in ev):
                return "unknown_span_id"
            if not ev:
                return "verdict_without_evidence:%s" % aid
            allowed = set(e["span_id"]
                          for e in pkt_atoms[aid]["candidate_evidence"])
            if not set(ev) <= allowed:
                return "span_not_in_atom_group:%s" % aid
    return None


def _atom_map(r):
    v = r["verdict"]
    if v == "PARTIAL":
        return "SUPPORTED"
    if v == "INSUFFICIENT":
        return "INSUFFICIENT_EVIDENCE"
    return v


def fusion_v2(packet, output, threshold):
    """Return (final_verdict, route, atom_results) deterministically."""
    if output is None:
        return "REVIEW_REQUIRED", "no_output", []
    reason = validate_fidelity_v2(packet, output)
    if reason:
        return "REVIEW_REQUIRED", "fidelity_failed:" + reason, []
    atom_results = []
    for a in output["atoms"]:
        verdict = a["verdict"]
        conf = float(a["confidence"])
        if a.get("needs_human_review"):
            return "REVIEW_REQUIRED", "human_review_flag", []
        if verdict in ("SUPPORTED", "CONTRADICTED", "PARTIAL") \
                and conf < threshold:
            atom_results.append({"atom_id": a["atom_id"],
                                 "verdict": "INSUFFICIENT",
                                 "evidence_span_ids": [],
                                 "confidence": conf,
                                 "route": "below_threshold"})
        else:
            atom_results.append({"atom_id": a["atom_id"],
                                 "verdict": verdict,
                                 "evidence_span_ids": a.get("evidence_span_ids") or [],
                                 "confidence": conf, "route": "accepted"})
    shim = {"deterministic_findings": packet["deterministic_findings"]}
    if _hard_contra_locked(shim) and any(
            r["verdict"] in ("SUPPORTED", "PARTIAL") for r in atom_results):
        return "REVIEW_REQUIRED", "hard_contra_lock", atom_results
    if packet["deterministic_findings"].get("injection_detected") and any(
            r["verdict"] in ("SUPPORTED", "CONTRADICTED", "PARTIAL")
            for r in atom_results):
        return "REVIEW_REQUIRED", "injection_lock", atom_results
    if any(r["verdict"] == "PARTIAL" for r in atom_results):
        final = "PARTIAL"
    else:
        final = aggregate(
            [{"verdict": _atom_map(r), "confidence": r["confidence"]}
             for r in atom_results], is_compound=len(atom_results) > 1)
    return final, "aggregated", atom_results


def review_claim_v2(claim_text, source_text, engine_result, gate_reason,
                    s0_mode="no_s0", max_spans=6, transport=None):
    packet = packet_router.build_v2_packet(
        claim_text, source_text, engine_result, gate_reason,
        s0_mode=s0_mode, max_spans=max_spans)
    output = call_luna_v2(packet, transport=transport)
    final, route, atom_results = fusion_v2(
        packet, output, classify_threshold(claim_text))
    approx_chars = sum(len(s["text"]) for s in packet["candidate_spans"])
    approx_chars += sum(len(json.dumps(a, ensure_ascii=False))
                        for a in packet["atoms"])
    return {"packet": packet, "reviewer_output": output,
            "final_verdict": final, "route": route,
            "atom_results": atom_results,
            "threshold": classify_threshold(claim_text),
            "n_spans": len(packet["candidate_spans"]),
            "approx_packet_tokens": approx_chars // 4,
            "prompt_meta": prompt_meta()}


if __name__ == "__main__":
    # Offline self-check with a scripted transport: no network, no cost.
    engine = {"verdict": "INSUFFICIENT_EVIDENCE",
              "atom_results": [
                  {"atom_id": "A1",
                   "atom_text": "Kommunen krever henvisning.",
                   "verdict": "INSUFFICIENT_EVIDENCE",
                   "rule": "no_candidate_span"}]}
    src = ("Lavterskel psykisk helsehjelp i kommunen krever henvisning "
           "fra fastlege.")
    pkt = packet_router.build_v2_packet(
        "Kommunen krever henvisning.", src, engine, "test",
        s0_mode="include")
    assert pkt["schema"] == SCHEMA_VERSION
    assert pkt["atoms"] and pkt["atoms"][0]["claim_atom"]

    def fake(messages):
        aid = pkt["atoms"][0]["atom_id"]
        sid = pkt["atoms"][0]["candidate_evidence"][0]["span_id"]
        return json.dumps({
            "atoms": [{"atom_id": aid, "verdict": "SUPPORTED",
                       "evidence_span_ids": [sid], "confidence": 0.92,
                       "needs_human_review": False}],
            "reason_code": "direct_quote"})
    out = call_luna_v2(pkt, transport=fake)
    assert validate_fidelity_v2(pkt, out) is None, validate_fidelity_v2(pkt, out)
    verdict, route, _ = fusion_v2(pkt, out, 0.8)
    assert (verdict, route) == ("SUPPORTED", "aggregated"), (verdict, route)

    bad = dict(out)
    bad["atoms"] = [dict(out["atoms"][0], evidence_span_ids=["S99"])]
    assert validate_fidelity_v2(pkt, bad) == "unknown_span_id"
    wrong_group = dict(out)
    wrong_group["atoms"] = [dict(out["atoms"][0], evidence_span_ids=["S9"])]
    if "S9" in {s["span_id"] for s in pkt["candidate_spans"]}:
        wrong_group["atoms"] = [dict(out["atoms"][0], evidence_span_ids=["S9"])]
        assert validate_fidelity_v2(pkt, wrong_group) in (
            "span_not_in_atom_group:A1", "unknown_span_id")
    no_ev = dict(out)
    no_ev["atoms"] = [dict(out["atoms"][0], evidence_span_ids=[])]
    assert validate_fidelity_v2(
        pkt, no_ev) == "verdict_without_evidence:A1"
    none_out = fusion_v2(pkt, None, 0.8)
    assert none_out[0] == "REVIEW_REQUIRED"
    print("reviewer_v2 self-check OK | prompt_sha=%s schema=%s" % (
        _PROMPT_SHA, SCHEMA_VERSION))
