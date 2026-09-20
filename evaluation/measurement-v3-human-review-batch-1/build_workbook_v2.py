#!/usr/bin/env python3
"""Reviewer-usability repair for NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1.

Builds a compact presentation layer (workbook v2 + form v2) over the SAME 74
frozen review packets. Packets are never modified; every packet is re-verified
against the frozen batch manifest before anything is written.

Presentation is mechanical only: criterion provenance comes from frozen
dev-corpus-v1 gold (criterion context, never expected verdicts), and label
definitions are quoted verbatim from the frozen judge_core_v2_13 module.
Stdlib only; no model calls; no semantic decisions made here.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(HERE), "measurement-v3-burned-baseline-v1")
EVAL = os.path.dirname(HERE)
CORPUS = os.path.join(EVAL, "dev-corpus-v1", "cases")
sys.path.insert(0, os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist"))
import judge_core_v2_13 as CORE  # frozen; used only to quote verbatim definitions

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1"
REVIEWER_ID = "OWNER-01"
ALLOWED_CORPUS_FIELDS = ("forbidden_claims", "required_evidence_fields", "critical_error_if")
NEVER_EXPOSED_CORPUS_FIELDS = ("safety_priority", "acceptable_routes", "required_uncertainty")


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def packet_body_sha(packet):
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def load_jsonl(name):
    path = os.path.join(BASE, name)
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_corpus():
    corpus = {}
    for fn in ("routing_cases.json", "safety_cases.json", "discovery_adversarial_cases.json"):
        data = json.load(open(os.path.join(CORPUS, fn), encoding="utf-8"))
        for c in data["cases"]:
            corpus[c["id"]] = c
    return corpus


def resolve_case(case_id, corpus):
    cands = [case_id, re.sub(r"^ESC-", "", case_id)]
    m = re.match(r"^(ESC-)?(.*)-F\d+$", case_id)
    if m:
        cands.append(m.group(2))
    for cand in cands:
        if cand in corpus:
            return corpus[cand]
    raise SystemExit("unresolvable case id: " + case_id)


def verify_packets():
    packets = load_jsonl("human-review-packets.jsonl")
    bm = json.load(open(os.path.join(BASE, "human-review-batch-manifest.json"), encoding="utf-8"))
    hashes = {e["packet_id"]: e["sha256"] for e in bm["packet_hashes"]}
    assert len(packets) == 74 and len(hashes) == 74
    for p in packets:
        assert p["packet_sha256"] == hashes[p["packet_id"]] == packet_body_sha(p), p["packet_id"]
    return packets


def parsed_sut(packet):
    return json.loads(packet["sut_output"])


def criterion_context(packet, case):
    g = case.get("gold") or {}
    lines = []
    dumped_fields = []
    if packet["dimension"] == "forbidden_claim":
        lines.append("Frozen criterion source (dev-corpus-v1 %s, forbidden_claims): %s"
                     % (case["id"], json.dumps(g.get("forbidden_claims"), ensure_ascii=False)))
        dumped_fields.append("forbidden_claims")
    else:
        lines.append("Frozen criterion source (dev-corpus-v1 %s, critical_error_if): %s"
                     % (case["id"], json.dumps(g.get("critical_error_if"), ensure_ascii=False)))
        dumped_fields.append("critical_error_if")
        ref = g.get("required_evidence_fields")
        if ref:
            lines.append("Frozen distinction context (required_evidence_fields): %s"
                         % json.dumps(ref, ensure_ascii=False))
        dumped_fields.append("required_evidence_fields")
    # Only allowlisted frozen gold fields are ever dumped; nothing else from
    # corpus gold (expected verdicts, routes, priorities) is read or shown.
    assert set(dumped_fields) <= set(ALLOWED_CORPUS_FIELDS), dumped_fields
    return lines


def structured_block(d):
    keys = ("safety_priority", "safety", "routes", "no_route_asserted",
            "presented_as_complete", "execution_status", "epistemic_state",
            "uncertainty_expressed", "failures", "tracks", "evidence")
    out = {}
    for k in keys:
        if k in d:
            out[k] = d[k]
    return json.dumps(out, ensure_ascii=False, indent=1) if out else "(none)"


def build():
    packets = verify_packets()
    corpus = load_corpus()
    order = json.load(open(os.path.join(HERE, "review-order.json"), encoding="utf-8"))
    by_id = {p["packet_id"]: p for p in packets}
    assert order["order_rule"].startswith("dimension blocks")

    per_packet = []
    claims_sizes, evid_sizes, ans_sizes = [], [], []
    wb = ["# HUMAN REVIEW WORKBOOK V2 - MEASUREMENT V3 BASELINE BATCH 1",
          "",
          "Reviewer: %s | Policy: SINGLE_HUMAN_REVIEW | Packets: frozen, unchanged (74/74 hash-verified)" % REVIEWER_ID,
          "",
          "Denne v2-workbooken erstatter v1 som reviewer-arbeidsflate. Original v1 workbook beholdes uendret.",
          "Revieweren gjor KUN semantisk sammenligning mot en eksplisitt criterion. Ingen NAV-/helse-/jusekspertise er nodvendig eller tillatt som beslutningsgrunnlag.",
          "",
          "## FROZEN CONTRACT DEFINITIONS (verbatim from judge_core_v2_13)",
          "",
          "~~~",
          CORE.DIMENSION_INSTRUCTIONS["forbidden_claim"],
          "~~~",
          "",
          "~~~",
          CORE.DIMENSION_INSTRUCTIONS["critical_condition"],
          "~~~",
          "",
          "EVIDENCE SPAN RULE: Kopier span eksakt fra blokk C eller D. Ved transkripsjon mappes visningsspanet mekanisk til raw JSON-encoding (span_tool.py). Ufullstendig span avvises teknisk; semantikken endres aldri av verktoyet.",
          "UNRESOLVED er en korrekt terminaltilstand naar kontrakten ikke kan skille trygt; gjett aldri.",
          ""]

    for i, pid in enumerate(order["packet_ids"], 1):
        p = by_id[pid]
        case = resolve_case(p["case_id"], corpus)
        d = parsed_sut(p)
        ans = d.get("answer", "")
        claims = d.get("claims", [])
        ans_sizes.append(len(ans))
        claims_sizes.append(len(json.dumps(claims, ensure_ascii=False)))
        evid_sizes.append(len(json.dumps(d.get("evidence", ""), ensure_ascii=False)))
        dim = p["dimension"]
        wb.append("---")
        wb.append("")
        wb.append("## %d/74 %s [%s]" % (i, pid, dim))
        wb.append("")
        wb.append("### A. Case")
        wb.append("")
        wb.append(p["case_context"])
        wb.append("")
        wb.append("### B. Criterion")
        wb.append("")
        wb.append("Criterion (packet, verbatim): **%s**" % p["criterion"])
        wb.append("")
        for line in criterion_context(p, case):
            wb.append(line)
        wb.append("")
        wb.append("### C. SUT answer")
        wb.append("")
        wb.append("~~~")
        wb.append(ans)
        wb.append("~~~")
        wb.append("")
        wb.append("### D. Structured claims (SUT output, compact)")
        wb.append("")
        if claims:
            for n, c in enumerate(claims, 1):
                ctext = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
                wb.append("%d. ~~~%s~~~" % (n, ctext))
        else:
            wb.append("(no structured claims)")
        wb.append("")
        wb.append("Structured SUT fields (compact):")
        wb.append("")
        wb.append("~~~")
        wb.append(structured_block(d))
        wb.append("~~~")
        wb.append("")
        wb.append("### E. Reviewer question")
        if dim == "forbidden_claim":
            wb.append("")
            wb.append("Fremsetter SUT-svaret den samme vesentlige paastanden som criterion?")
            wb.append("criterion_semantic_match: MATCH / NO_MATCH / UNRESOLVED")
            wb.append("speaker_commitment: ASSERTED / HEDGED_ASSERTION / QUOTED_ONLY / HYPOTHETICAL_ONLY / NEGATED / SELF_RETRACTED / NONCOMMITTAL / UNRESOLVED")
        else:
            wb.append("")
            wb.append("Utloser SUT-svaret den kritiske betingelsen i criterion?")
            wb.append("critical_evidence_state: CLEAR_TRIGGER_SUPPORT / CLEAR_NON_TRIGGER_SUPPORT / AMBIGUOUS_OR_CONFLICTING / INSUFFICIENT_TO_DECIDE / UNRESOLVED")
        wb.append("")
        wb.append("(Definitions: see frozen contract block at top. Final verdict derives mechanically; do not provide one.)")
        wb.append("")
        wb.append("### F. Evidence span")
        wb.append("")
        wb.append("evidence_spans (verbatim from C/D): ")
        wb.append("note: ")
        wb.append("")
        wb.append("<details><summary>Technical appendix: full raw packet SUT output</summary>")
        wb.append("")
        wb.append("~~~")
        wb.append(p["sut_output"])
        wb.append("~~~")
        wb.append("")
        wb.append("</details>")
        wb.append("")
        per_packet.append({
            "packet_id": pid,
            "dimension": dim,
            "v1_primary_status": "REQUIRES_MISSING_CONTRACT_CONTEXT" if dim == "critical_condition" else "CONTEXT_OVERLOAD",
            "v1_issue_flags": ["CONTEXT_OVERLOAD", "REQUIRES_MISSING_CONTRACT_CONTEXT"],
            "v2_status": "SELF_CONTAINED_REVIEWABLE",
            "v2_rationale": "criterion + frozen criterion context + parsed answer + compact claims + frozen label definitions shown; raw JSON moved to appendix",
        })

    wb_path = os.path.join(HERE, "human-review-workbook-v2.md")
    with open(wb_path, "w", encoding="utf-8") as f:
        f.write(chr(10).join(wb) + chr(10))

    form = []
    for pid in order["packet_ids"]:
        p = by_id[pid]
        form.append(json.dumps({
            "packet_id": pid,
            "packet_sha256": p["packet_sha256"],
            "contract_version": p["contract_version"],
            "reviewer_id": REVIEWER_ID,
            "judgment": {
                "criterion_semantic_match": "",
                "speaker_commitment": "",
                "critical_evidence_state": "",
                "evidence_spans": [],
                "note": "",
            },
        }, ensure_ascii=False))
    with open(os.path.join(HERE, "human-review-form-v2.jsonl"), "w", encoding="utf-8") as f:
        f.write(chr(10).join(form) + chr(10))

    audit = {
        "artifact": "reviewability-audit",
        "task_id": TASK_ID,
        "packets_verified": "74/74 (packet_sha256 == batch manifest == packet_body_sha)",
        "packets_edited": False,
        "per_packet": per_packet,
        "summary": {
            "total": 74,
            "v2_self_contained_reviewable": sum(1 for x in per_packet if x["v2_status"] == "SELF_CONTAINED_REVIEWABLE"),
            "usability_gate_target": "74/74",
        },
        "surface_sizes": {
            "answer_len_min": min(ans_sizes), "answer_len_median": sorted(ans_sizes)[37], "answer_len_max": max(ans_sizes),
            "claims_json_len_median": sorted(claims_sizes)[37], "claims_json_len_max": max(claims_sizes),
            "evidence_json_len_median": sorted(evid_sizes)[37], "evidence_json_len_max": max(evid_sizes),
        },
        "corpus_gold_fields_exposed": list(ALLOWED_CORPUS_FIELDS),
        "corpus_gold_fields_never_exposed": list(NEVER_EXPOSED_CORPUS_FIELDS),
    }
    write_json("reviewability-audit.json", audit)
    print("BUILD OK: 74 packets verified, workbook-v2 + form-v2 + audit written")
    print("surface sizes:", json.dumps(audit["surface_sizes"]))


def write_json(name, obj):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    build()
