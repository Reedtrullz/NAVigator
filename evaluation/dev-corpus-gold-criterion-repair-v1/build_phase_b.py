#!/usr/bin/env python3
"""Phase B entrypoint: materialize approved gold repairs and review batch 2."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_phase_b_lib import (APPROVED, BASELINE_DIR, BATCH2_DIR, EVAL, HERE,
                               NEW_CORPUS_DIR, OLD_ROUTING_SHA, OWNER_AUTH_PATH,
                               SAFETY_SHA, DISCOVERY_SHA, TASK_ID, sha_file,
                               write_json, build_repaired_corpus)
from build_batch2 import build_batch2_packets


def main():
    owner_sha = sha_file(OWNER_AUTH_PATH)
    assert owner_sha == "4d7d62f70b486b1441db3c68287b78eebe90d6847e3b4628617b7a1934bd9ffb"
    scores = json.load(open(os.path.join(BASELINE_DIR, "deterministic-scores.json"),
                            encoding="utf-8"))
    raw_scores = json.dumps(scores)
    for entry in APPROVED:
        assert entry["packet_id"] in raw_scores, entry["packet_id"]
    def blob_for(packet_id):
        for case in scores["cases"]:
            blob = json.dumps(case)
            if packet_id in blob:
                return blob
        return ""
    for entry in APPROVED:
        assert "HUMAN_REVIEW_PENDING" in blob_for(entry["packet_id"]), entry["packet_id"]

    new_raw, diff_rows = build_repaired_corpus()
    rows, packet_hashes, corpus_routing_sha = build_batch2_packets(new_raw)

    bm1 = json.load(open(os.path.join(BASELINE_DIR, "human-review-batch-manifest.json"),
                         encoding="utf-8"))
    bm1_by_id = {e["packet_id"]: e["sha256"] for e in bm1["packet_hashes"]}
    repaired_ids = {e["packet_id"] for e in APPROVED}
    matched = sum(1 for q in rows
                  if q["packet_id"] not in repaired_ids
                  and bm1_by_id.get(q["packet_id"]) == q["packet_sha256"])
    assert matched == 71, matched

    generated = write_corpus_manifest(owner_sha)
    write_repair_lineage_docs(owner_sha, diff_rows, generated)
    write_batch2_manifest(packet_hashes, corpus_routing_sha, generated)
    new_packets_sha = sha_file(os.path.join(BATCH2_DIR, "human-review-packets.jsonl"))
    write_integrity_and_hashes(corpus_routing_sha, new_packets_sha, owner_sha, matched, generated)
    update_task_lock(owner_sha, generated)
    print("PHASE B OK")
    print("repaired_routing_sha256:", corpus_routing_sha)
    print("repaired_packets_sha256:", new_packets_sha)
    print("diffs:", [(d["case_id"], d["diff_path"]) for d in diff_rows])
    print("unchanged_packets_match_batch1:", matched)
    print("terminal: DEV_CORPUS_GOLD_CRITERION_REPAIR_V1_COMPLETE_REVIEW_BATCH_READY")


def write_corpus_manifest(owner_sha):
    from build_phase_b_lib import now_utc
    generated = now_utc()
    files = {}
    for root, _dirs, names in os.walk(NEW_CORPUS_DIR):
        for fn in sorted(names):
            fp = os.path.join(root, fn)
            files[os.path.relpath(fp, NEW_CORPUS_DIR)] = sha_file(fp)
    write_json(os.path.join(NEW_CORPUS_DIR, "manifest.json"), {
        "artifact": "dev-corpus-v1-1-repair",
        "task_id": TASK_ID,
        "generated_utc": generated,
        "phase": "PHASE_B_MATERIALIZE_AND_FREEZE",
        "data_status": "BURNED_DEVELOPMENT_ONLY",
        "case_total": 120,
        "corpus": {"safety_cases": 20, "routing_cases": 75,
                   "discovery_adversarial_cases": 25},
        "manifest_version": 1,
        "parent_version": "dev-corpus-v1",
        "parent_routing_sha256": OLD_ROUTING_SHA,
        "provenance_classification": "REPAIR_WORDING_FROM_FROZEN_SUPPORTED_DIRECTION",
        "changed_forbidden_criterion_fields": 3,
        "changed_cases": [e["case_id"] for e in APPROVED],
        "owner_authorization_sha256": owner_sha,
        "files": files,
    })
    return generated


def write_repair_lineage_docs(owner_sha, diff_rows, generated):
    write_json(os.path.join(HERE, "approved-owner-decisions.json"), {
        "artifact": "approved-owner-decisions",
        "task_id": TASK_ID,
        "phase": "PHASE_B_MATERIALIZE_AND_FREEZE",
        "generated_utc": generated,
        "authorization_document": {"path": OWNER_AUTH_PATH, "sha256": owner_sha},
        "decisions": [
            {"case_id": e["case_id"],
             "approved_candidate_id": e["approved_candidate_id"],
             "new_criterion": e["new_criterion"],
             "classification": e["classification"]}
            for e in APPROVED
        ],
    })
    for e, d in zip(APPROVED, diff_rows):
        assert d["case_id"] == e["case_id"] and d["new"] == e["new_criterion"]
    write_json(os.path.join(HERE, "gold-repair-diff.json"), {
        "artifact": "gold-repair-diff",
        "task_id": TASK_ID,
        "entries": [
            {"case_id": e["case_id"], "packet_id": e["packet_id"],
             "diff_path": d["diff_path"],
             "original_criterion": e["old_criterion"],
             "repaired_criterion": e["new_criterion"],
             "approved_candidate_id": e["approved_candidate_id"],
             "phase_a_support_classification": e["classification"],
             "owner_approval_reference": {"document_sha256": owner_sha},
             "semantic_rationale": e["semantic_rationale"],
             "historical_wording_preserved": True}
            for e, d in zip(APPROVED, diff_rows)
        ],
    })
    write_json(os.path.join(HERE, "gold-repair-provenance.json"), {
        "artifact": "gold-repair-provenance",
        "task_id": TASK_ID,
        "provenance_classification": "REPAIR_WORDING_FROM_FROZEN_SUPPORTED_DIRECTION",
        "not": "HISTORICALLY_FROZEN_VERBATIM",
        "explanation": "Phase A classification new_authoring=false means the "
                       "proposed wording is supported by frozen artifacts "
                       "(critical_error_if, utterance scenario boundaries, "
                       "acceptable_routes family); the new strings are "
                       "owner-approved repairs, not historically frozen "
                       "verbatim sentences.",
        "defect_history": {
            "source_audit_task": "NAV-EXPLORE-HUMAN-REVIEW-CRITERION-SEMANTIC-COMPLETENESS-AUDIT",
            "terminal_status": "HUMAN_REVIEW_CRITERION_REPAIR_REQUIRED",
            "readjudication": "evaluation/measurement-v3-human-review-batch-1/pkt-esc-rout-070-readjudication.md",
        },
        "source_shas": {
            "dev-corpus-v1 routing_cases.json": OLD_ROUTING_SHA,
            "dev-corpus-v1 safety_cases.json": SAFETY_SHA,
            "dev-corpus-v1 discovery_adversarial_cases.json": DISCOVERY_SHA,
            "owner_authorization": owner_sha,
        },
    })


def write_batch2_manifest(packet_hashes, corpus_routing_sha, generated):
    write_json(os.path.join(BATCH2_DIR, "human-review-batch-manifest.json"), {
        "artifact": "human-review-batch-manifest",
        "task_id": TASK_ID,
        "lineage": "measurement-v3-human-review-batch-2-repaired",
        "created_utc": generated,
        "total_packets": 74,
        "m2_packets": 0,
        "packets_by_dimension": {"critical_condition": 10, "forbidden_claim": 64},
        "contract_versions": {"all": "semantic-judge-contract-v1-4"},
        "source_corpus": "dev-corpus-v1-1-repair",
        "source_corpus_routing_sha256": corpus_routing_sha,
        "criterion_repaired_packets": [e["packet_id"] for e in APPROVED],
        "packet_hashes": packet_hashes,
    })


def write_integrity_and_hashes(corpus_routing_sha, new_packets_sha, owner_sha, matched, generated):
    write_json(os.path.join(HERE, "phase-b-integrity.json"), {
        "artifact": "phase-b-integrity",
        "task_id": TASK_ID,
        "generated_utc": generated,
        "gates": {
            "FORBIDDEN_CRITERION_FIELDS_CHANGED": 3,
            "CASE_INPUTS_CHANGED": 0,
            "ACCEPTABLE_ROUTES_CHANGED": 0,
            "SAFETY_GOLD_CHANGED": 0,
            "REQUIRED_UNCERTAINTY_CHANGED": 0,
            "REQUIRED_EVIDENCE_FIELDS_CHANGED": 0,
            "CRITICAL_ERROR_IF_CHANGED": 0,
            "OTHER_FORBIDDEN_CLAIMS_CHANGED": 0,
            "ORIGINAL_GOLD_MUTATED": False,
            "DETERMINISTIC_RESULTS_AFFECTED": 0,
            "UNCHANGED_PACKETS_MATCH_BATCH1": matched,
            "REPAIRED_PACKETS_REHASHED": len(APPROVED),
            "NEW_GOLD_HASHES_VALID": True,
        },
        "shas": {
            "repaired_routing_cases.json": corpus_routing_sha,
            "repaired_packets.jsonl": new_packets_sha,
            "owner_authorization": owner_sha,
        },
    })
    targets = [
        os.path.join(NEW_CORPUS_DIR, "manifest.json"),
        os.path.join(NEW_CORPUS_DIR, "cases", "routing_cases.json"),
        os.path.join(NEW_CORPUS_DIR, "cases", "safety_cases.json"),
        os.path.join(NEW_CORPUS_DIR, "cases", "discovery_adversarial_cases.json"),
        os.path.join(BATCH2_DIR, "human-review-packets.jsonl"),
        os.path.join(BATCH2_DIR, "review-order.json"),
        os.path.join(BATCH2_DIR, "human-review-workbook.md"),
        os.path.join(BATCH2_DIR, "human-review-form.jsonl"),
        os.path.join(BATCH2_DIR, "review-leakage-audit.json"),
        os.path.join(BATCH2_DIR, "reviewability-check.json"),
        os.path.join(BATCH2_DIR, "source-repair-manifest.json"),
        os.path.join(BATCH2_DIR, "human-review-batch-manifest.json"),
        os.path.join(HERE, "approved-owner-decisions.json"),
        os.path.join(HERE, "gold-repair-diff.json"),
        os.path.join(HERE, "gold-repair-provenance.json"),
    ]
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for k in targets:
            f.write(sha_file(k) + "  " + os.path.relpath(k, EVAL) + "\n")


def update_task_lock(owner_sha, generated):
    lock_path = os.path.join(HERE, "TASK-LOCK.json")
    lock = json.load(open(lock_path, encoding="utf-8"))
    lock["owner_authorization"]["phase_b_authorized"] = True
    lock["owner_authorization"]["phase_b_document"] = OWNER_AUTH_PATH
    lock["owner_authorization"]["phase_b_document_sha256"] = owner_sha
    lock["current_state"] = "DEV_CORPUS_GOLD_CRITERION_REPAIR_V1_COMPLETE_REVIEW_BATCH_READY"
    lock["terminal_status"] = "DEV_CORPUS_GOLD_CRITERION_REPAIR_V1_COMPLETE_REVIEW_BATCH_READY"
    lock["terminal_utc"] = generated
    lock["invariants"].update({
        "ORIGINAL_CORPUS_MUTATED": False,
        "ORIGINAL_GOLD_MUTATED": False,
        "ORIGINAL_REVIEW_PACKETS_MUTATED": False,
        "ORIGINAL_BASELINE_MUTATED": False,
        "DETERMINISTIC_RESULTS_AFFECTED": 0,
        "OWNER_01_REVIEWS_COMPLETED": 0,
        "HUMAN_REVIEW_INGEST": 0,
        "SEMANTIC_VERDICTS_DERIVED": 0,
        "SUT_RERUN": False,
        "PREDICTIONS_CHANGED": False,
        "DETERMINISTIC_SCORING_RERUN": False,
        "MEASUREMENT_V3_RERUN": False,
        "GPT_5_5_USED": False,
        "SUBAGENTS_USED": 0,
    })
    write_json(lock_path, lock)


if __name__ == "__main__":
    main()
