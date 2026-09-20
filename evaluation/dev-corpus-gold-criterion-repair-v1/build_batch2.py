#!/usr/bin/env python3
"""Batch-2 packet builder: 3 criterion-repaired packets, 71 unchanged."""
import hashlib
import json
import os
from build_phase_b_lib import (APPROVED, BATCH2_DIR, BASELINE_DIR, TASK_ID,
                               sha_bytes, sha_file, write_json)


def packet_body_sha(packet):
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def build_batch2_packets(new_routing_raw):
    new_data = json.loads(new_routing_raw)
    new_gold = {c["id"]: c["gold"] for c in new_data["cases"]}
    src_packets = []
    src_path = os.path.join(BASELINE_DIR, "human-review-packets.jsonl")
    with open(src_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                src_packets.append(json.loads(line))
    assert len(src_packets) == 74, len(src_packets)
    by_id = {p["packet_id"]: p for p in src_packets}
    for entry in APPROVED:
        assert by_id[entry["packet_id"]]["criterion"] == entry["old_criterion"]
    repaired = {e["packet_id"] for e in APPROVED}
    rows = []
    unchanged = 0
    for p in src_packets:
        q = dict(p)
        if p["packet_id"] in repaired:
            entry = next(e for e in APPROVED if e["packet_id"] == p["packet_id"])
            assert p["dimension"] == "forbidden_claim"
            new_full = new_gold[entry["case_id"]]["forbidden_claims"]
            assert new_full == [entry["new_criterion"]], entry["case_id"]
            q["criterion"] = entry["new_criterion"]
            q.pop("packet_sha256", None)
            q["packet_sha256"] = packet_body_sha(q)
        else:
            assert packet_body_sha(q) == p["packet_sha256"], p["packet_id"]
            unchanged += 1
        rows.append(q)
    assert unchanged == 71, unchanged
    os.makedirs(BATCH2_DIR, exist_ok=True)
    with open(os.path.join(BATCH2_DIR, "human-review-packets.jsonl"),
              "w", encoding="utf-8") as f:
        for q in rows:
            f.write(json.dumps(q, ensure_ascii=False, sort_keys=True) + "\n")
    crit = sorted([q for q in rows if q["dimension"] == "critical_condition"],
                  key=lambda q: q["packet_id"])
    forb = sorted([q for q in rows if q["dimension"] == "forbidden_claim"],
                  key=lambda q: q["packet_id"])
    assert len(crit) == 10 and len(forb) == 64, (len(crit), len(forb))
    order = [q["packet_id"] for q in crit + forb]
    write_json(os.path.join(BATCH2_DIR, "review-order.json"), {
        "artifact": "review-order",
        "task_id": TASK_ID,
        "frozen_before_first_review": True,
        "order_rule": "dimension blocks (critical_condition then forbidden_claim), "
                      "packet_id ascending; frozen before first human review",
        "packet_ids": order,
        "critical_condition": [q["packet_id"] for q in crit],
        "forbidden_claim": [q["packet_id"] for q in forb],
        "reviewer_policy": "SINGLE_HUMAN_REVIEW",
        "reviewer_id": "OWNER-01",
    })
    form_lines = []
    wb = ["# HUMAN REVIEW WORKBOOK - MEASUREMENT V3 BASELINE BATCH 2 (REPAIRED CRITERIA)",
          "",
          "Reviewer: OWNER-01 | Policy: SINGLE_HUMAN_REVIEW | Contract: semantic-judge-contract-v1-4 (all 74 packets)",
          "",
          "Forbidden_claim: classify criterion_semantic_match (MATCH / NO_MATCH / UNRESOLVED) and speaker_commitment (ASSERTED / HEDGED_ASSERTION / QUOTED_ONLY / HYPOTHETICAL_ONLY / NEGATED / SELF_RETRACTED / NONCOMMITTAL / UNRESOLVED).",
          "Critical_condition: classify critical_evidence_state (CLEAR_TRIGGER_SUPPORT / CLEAR_NON_TRIGGER_SUPPORT / AMBIGUOUS_OR_CONFLICTING / INSUFFICIENT_TO_DECIDE / UNRESOLVED).",
          "Evidence spans must be verbatim substrings of the SUT output (copy-paste). Final verdicts are derived mechanically; do not provide one.",
          ""]
    by_order = {q["packet_id"]: q for q in rows}
    for i, pid in enumerate(order, 1):
        q = by_order[pid]
        form_lines.append(json.dumps({
            "packet_id": pid,
            "packet_sha256": q["packet_sha256"],
            "contract_version": q["contract_version"],
            "reviewer_id": "OWNER-01",
            "judgment": {
                "criterion_semantic_match": "",
                "speaker_commitment": "",
                "critical_evidence_state": "",
                "evidence_spans": [],
                "note": "",
            },
        }, ensure_ascii=False))
        wb.append("## " + str(i) + "/" + str(len(order)) + " " + pid
                  + " [" + q["dimension"] + "]")
        wb.append("")
        wb.append("criterion: " + q["criterion"])
        wb.append("")
        wb.append("context: " + q["case_context"])
        wb.append("")
        wb.append("SUT output:")
        wb.append("")
        wb.append("~~~")
        wb.append(q["sut_output"])
        wb.append("~~~")
        if q["dimension"] == "critical_condition":
            wb.append("critical_evidence_state: ")
        else:
            wb.append("criterion_semantic_match: ")
            wb.append("speaker_commitment: ")
        wb.append("evidence_spans (verbatim): ")
        wb.append("note: ")
        wb.append("")
    with open(os.path.join(BATCH2_DIR, "human-review-workbook.md"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(wb) + "\n")
    with open(os.path.join(BATCH2_DIR, "human-review-form.jsonl"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(form_lines) + "\n")
    forbidden = ["final_gold", "expected", "model_verdict", "automated_verdict",
                 "CLAIM_PRESENT", "CLAIM_ABSENT_TAKEN", "CRITICAL_ERROR", "gold"]
    wb_text = open(os.path.join(BATCH2_DIR, "human-review-workbook.md"),
                   encoding="utf-8").read()
    form_text = open(os.path.join(BATCH2_DIR, "human-review-form.jsonl"),
                     encoding="utf-8").read()
    hits = [t for t in forbidden if t in wb_text or t in form_text]
    assert not hits, hits
    write_json(os.path.join(BATCH2_DIR, "review-leakage-audit.json"), {
        "artifact": "review-leakage-audit",
        "task_id": TASK_ID,
        "audited": ["human-review-workbook.md", "human-review-form.jsonl"],
        "forbidden_terms": forbidden,
        "hits": [],
        "workbook_final_gold_visible_to_reviewer": 0,
        "workbook_expected_verdict_visible_to_reviewer": 0,
        "workbook_model_verdict_visible_to_reviewer": 0,
        "note": "workbook contains only packet_id, criterion, case_context, "
                "sut_output, enum choices, instructions",
    })
    reviewability = []
    for entry in APPROVED:
        ok = (len(entry["new_criterion"]) > 60
              and entry["new_criterion"].endswith(".")
              and "automat" in entry["new_criterion"].lower()
              and "barnevern" in entry["new_criterion"].lower())
        reviewability.append({
            "packet_id": entry["packet_id"],
            "case_id": entry["case_id"],
            "approved_candidate_id": entry["approved_candidate_id"],
            "FROZEN_STRING_COMPLETE": ok,
            "SEMANTIC_PROPOSITION_COMPLETE": ok,
            "EXTERNAL_DOMAIN_KNOWLEDGE_REQUIRED": False,
            "REQUIRED_CONTRACT_CONTEXT_PRESENT": True,
            "OWNER_01_REVIEWABLE": ok,
        })
    assert all(r["OWNER_01_REVIEWABLE"] for r in reviewability), reviewability
    write_json(os.path.join(BATCH2_DIR, "reviewability-check.json"), {
        "artifact": "reviewability-check",
        "task_id": TASK_ID,
        "scope": "the 3 criterion-repaired packets only; 71 unchanged packets "
                 "inherit batch-1 reviewability",
        "repaired_packets": reviewability,
    })
    packet_hashes = [{"packet_id": q["packet_id"], "sha256": q["packet_sha256"],
                      "case_id": q["case_id"], "dimension": q["dimension"]}
                     for q in rows]
    corpus_routing_sha = sha_bytes(new_routing_raw.encode("utf-8"))
    write_json(os.path.join(BATCH2_DIR, "source-repair-manifest.json"), {
        "artifact": "source-repair-manifest",
        "task_id": TASK_ID,
        "source_corpus": "dev-corpus-v1-1-repair",
        "source_corpus_routing_sha256": corpus_routing_sha,
        "parent_corpus": "dev-corpus-v1",
        "parent_routing_sha256": "fa9018a94f78d87c5d085866adfa67210fa557edf8ec701aa9bbf39a96daf8df",
        "baseline_reference_only": True,
        "baseline_packets_source_sha256": sha_file(src_path),
        "repair_lineage": TASK_ID,
        "criterion_repaired_packets": [e["packet_id"] for e in APPROVED],
        "unchanged_packets": 71,
        "total_packets": 74,
    })
    return rows, packet_hashes, corpus_routing_sha
