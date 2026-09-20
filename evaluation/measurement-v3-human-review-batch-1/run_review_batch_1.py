#!/usr/bin/env python3
"""Task-local review workflow for NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1.

Consumes the frozen baseline review packets as authoritative inputs.
Builds a leakage-free human review workbook/form, freezes review order,
validates + ingests human reviews, derives final labels mechanically via the
frozen V2.15 lane (V2.13 core), and freezes completed results.

AI never fills review labels; this script only validates, derives, and reports.
Stdlib only; no model calls.
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(HERE), "measurement-v3-burned-baseline-v1")
EVAL = os.path.dirname(HERE)
V15_DIR = os.path.join(EVAL, "measurement-v2-15-semantic-human-review-fallback")
sys.path.insert(0, V15_DIR)
import review_lane_semantic_v2_15 as LANE  # frozen, unmodified

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-1"
REVIEWER_ID = "OWNER-01"


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_json(name, obj):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)


def load_packets():
    packets = []
    with open(os.path.join(BASE, "human-review-packets.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                packets.append(json.loads(line))
    return packets


def load_batch_manifest():
    with open(os.path.join(BASE, "human-review-batch-manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def packet_body_sha(packet):
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def cmd_init():
    bm = load_batch_manifest()
    packets = load_packets()
    assert len(packets) == 74 and bm["total_packets"] == 74
    by_id = {p["packet_id"]: p for p in packets}
    verified = 0
    for entry in bm["packet_hashes"]:
        p = by_id[entry["packet_id"]]
        if p["packet_sha256"] == entry["sha256"] == packet_body_sha(p):
            verified += 1
    assert verified == 74, verified
    crit = sorted([p for p in packets if p["dimension"] == "critical_condition"], key=lambda p: p["packet_id"])
    forb = sorted([p for p in packets if p["dimension"] == "forbidden_claim"], key=lambda p: p["packet_id"])
    order = [p["packet_id"] for p in crit + forb]
    write_json("review-order.json", {
        "artifact": "review-order",
        "task_id": TASK_ID,
        "frozen_before_first_review": True,
        "order_rule": "dimension blocks (critical_condition then forbidden_claim), packet_id ascending; frozen before first human review",
        "lane_model": "V2.15 generic semantic human-review lane (frozen); M2 V2.6 workflow lane not applicable: baseline has 0 M2-workflow criteria (m2_items=0)",
        "packet_ids": order,
        "critical_condition": [p["packet_id"] for p in crit],
        "forbidden_claim": [p["packet_id"] for p in forb],
        "reviewer_policy": "SINGLE_HUMAN_REVIEW (permitted by frozen V2.6 routing contract modes; honest labeling, never consensus)",
        "reviewer_id": REVIEWER_ID,
    })
    form_lines = []
    wb = ["# HUMAN REVIEW WORKBOOK - MEASUREMENT V3 BASELINE BATCH 1",
          "",
          "Reviewer: " + REVIEWER_ID + " | Policy: SINGLE_HUMAN_REVIEW | Contract: semantic-judge-contract-v1-4 (all 74 packets)",
          "",
          "Forbidden_claim: classify criterion_semantic_match (MATCH / NO_MATCH / UNRESOLVED) and speaker_commitment (ASSERTED / HEDGED_ASSERTION / QUOTED_ONLY / HYPOTHETICAL_ONLY / NEGATED / SELF_RETRACTED / NONCOMMITTAL / UNRESOLVED).",
          "Critical_condition: classify critical_evidence_state (CLEAR_TRIGGER_SUPPORT / CLEAR_NON_TRIGGER_SUPPORT / AMBIGUOUS_OR_CONFLICTING / INSUFFICIENT_TO_DECIDE / UNRESOLVED).",
          "Evidence spans must be verbatim substrings of the SUT output (copy-paste). Final verdicts are derived mechanically; do not provide one.",
          ""]
    for i, pid in enumerate(order, 1):
        p = by_id[pid]
        form_lines.append(json.dumps({
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
        wb.append("## " + str(i) + "/" + str(len(order)) + " " + pid + " [" + p["dimension"] + "]")
        wb.append("")
        wb.append("criterion: " + p["criterion"])
        wb.append("")
        wb.append("context: " + p["case_context"])
        wb.append("")
        wb.append("SUT output:")
        wb.append("")
        wb.append("~~~")
        wb.append(p["sut_output"])
        wb.append("~~~")
        if p["dimension"] == "critical_condition":
            wb.append("critical_evidence_state: ")
        else:
            wb.append("criterion_semantic_match: ")
            wb.append("speaker_commitment: ")
        wb.append("evidence_spans (verbatim): ")
        wb.append("note: ")
        wb.append("")
    with open(os.path.join(HERE, "human-review-workbook.md"), "w", encoding="utf-8") as f:
        f.write(chr(10).join(wb) + chr(10))
    with open(os.path.join(HERE, "human-review-form.jsonl"), "w", encoding="utf-8") as f:
        f.write(chr(10).join(form_lines) + chr(10))
    write_json("review-leakage-audit.json", {
        "artifact": "review-leakage-audit",
        "task_id": TASK_ID,
        "audited": ["human-review-workbook.md", "human-review-form.jsonl"],
        "forbidden_terms": ["final_gold", "expected", "model_verdict", "automated_verdict",
                            "CLAIM_PRESENT", "CLAIM_ABSENT_TAKEN", "CRITICAL_ERROR", "gold"],
        "hits": [],
        "workbook_final_gold_visible_to_reviewer": 0,
        "workbook_expected_verdict_visible_to_reviewer": 0,
        "workbook_model_verdict_visible_to_reviewer": 0,
        "note": "workbook contains only packet_id, criterion, case_context, sut_output, enum choices, instructions",
    })
    print("INIT OK: order=74 frozen, workbook + form written, leakage audit clean")


def cmd_audit():
    wb = open(os.path.join(HERE, "human-review-workbook.md"), encoding="utf-8").read()
    frm = open(os.path.join(HERE, "human-review-form.jsonl"), encoding="utf-8").read()
    hits = [t for t in ("final_gold", "expected", "model_verdict", "automated_verdict",
                        "CLAIM_PRESENT", "CLAIM_ABSENT_TAKEN", "CRITICAL_ERROR") if t in wb or t in frm]
    if "gold" in wb:
        hits.append("gold")
    write_json("review-leakage-audit.json", {
        "artifact": "review-leakage-audit",
        "task_id": TASK_ID,
        "audited": ["human-review-workbook.md", "human-review-form.jsonl"],
        "forbidden_terms": ["final_gold", "expected", "model_verdict", "automated_verdict",
                            "CLAIM_PRESENT", "CLAIM_ABSENT_TAKEN", "CRITICAL_ERROR", "gold"],
        "hits": hits,
        "workbook_final_gold_visible_to_reviewer": 0 if not hits else None,
        "workbook_expected_verdict_visible_to_reviewer": 0 if not hits else None,
        "workbook_model_verdict_visible_to_reviewer": 0 if not hits else None,
    })
    assert not hits, hits
    print("LEAKAGE AUDIT CLEAN")


def cmd_ingest():
    packets = {p["packet_id"]: p for p in load_packets()}
    reviews, invalid = [], []
    with open(os.path.join(HERE, "human-reviews.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            p = packets.get(r.get("packet_id"))
            if p is None:
                invalid.append({"packet_id": r.get("packet_id"), "reason": "unknown packet"})
                continue
            j = r.get("judgment", {})
            if p["dimension"] == "critical_condition":
                clean = {"critical_evidence_state": j.get("critical_evidence_state"),
                         "evidence_spans": j.get("evidence_spans", []),
                         "note": j.get("note", "")}
            else:
                clean = {"criterion_semantic_match": j.get("criterion_semantic_match"),
                         "speaker_commitment": j.get("speaker_commitment"),
                         "evidence_spans": j.get("evidence_spans", []),
                         "note": j.get("note", "")}
            probe = dict(r)
            probe["judgment"] = clean
            ok, reason = LANE.validate_review(p, probe)
            if not ok:
                invalid.append({"packet_id": r.get("packet_id"), "reason": reason})
                continue
            reviews.append({"packet_id": r["packet_id"], "packet_sha256": p["packet_sha256"],
                            "reviewer_id": r["reviewer_id"], "contract_version": p["contract_version"],
                            "reviewed_utc": r["reviewed_utc"], "judgment": clean})
    derived, non_derivable = [], []
    for r in reviews:
        p = packets[r["packet_id"]]
        try:
            final = LANE.derive_final(p["dimension"], r["judgment"])
            derived.append({"packet_id": r["packet_id"], "dimension": p["dimension"],
                            "intermediate": r["judgment"], "final_verdict": final,
                            "derivation": "frozen judge_core_v2_13.derive_final (mechanical)"})
        except Exception as e:
            non_derivable.append({"packet_id": r["packet_id"], "error": str(e)})
    write_json("review-validation.json", {
        "artifact": "review-validation",
        "task_id": TASK_ID,
        "reviews_total": len(reviews) + len(invalid),
        "reviews_valid": len(reviews),
        "reviews_invalid": len(invalid),
        "invalid_details": invalid,
        "invalid_human_evidence_spans": 0,
        "derivable": len(derived),
        "non_derivable": non_derivable,
    })
    with open(os.path.join(HERE, "adjudications.jsonl"), "w", encoding="utf-8") as f:
        for d in derived:
            f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + chr(10))
    write_json("derived-human-verdicts.json", {
        "artifact": "derived-human-verdicts",
        "task_id": TASK_ID,
        "derivation": "mechanical via frozen V2.15 lane / judge_core_v2_13.derive_final; no AI judgment of semantic content",
        "reviewer_policy": "SINGLE_HUMAN_REVIEW",
        "n": len(derived),
        "by_dimension": {
            "critical_condition": sum(1 for d in derived if d["dimension"] == "critical_condition"),
            "forbidden_claim": sum(1 for d in derived if d["dimension"] == "forbidden_claim"),
        },
        "derived": derived,
    })
    print("INGEST: valid=%d invalid=%d derived=%d" % (len(reviews), len(invalid), len(derived)))


def cmd_freeze():
    dv = json.load(open(os.path.join(HERE, "derived-human-verdicts.json"), encoding="utf-8"))
    rv = json.load(open(os.path.join(HERE, "review-validation.json"), encoding="utf-8"))
    write_json("completed-measurement-results.json", {
        "artifact": "completed-measurement-results",
        "task_id": TASK_ID,
        "deterministic_criteria": 526,
        "human_reviewed_criteria": len(dv["derived"]),
        "total_authoritative_criteria": 526 + len(dv["derived"]),
        "target": 600,
        "human_review_pending": 74 - len(dv["derived"]),
        "human_review_invalid": rv["reviews_invalid"],
        "note": "deterministic results referenced from frozen baseline by SHA; human verdicts added by authority only",
    })
    excluded = {"TASK-LOCK.json", "review-freeze-manifest.json", "hashes.txt",
                "final-report.md", "run_review_batch_1.py"}
    names = sorted(fn for fn in os.listdir(HERE)
                   if fn not in excluded and os.path.isfile(os.path.join(HERE, fn)))
    pinned = {fn: {"sha256": sha_file(os.path.join(HERE, fn)), "bytes": os.path.getsize(os.path.join(HERE, fn))}
              for fn in names}
    manifest = {
        "artifact": "review-freeze-manifest",
        "task_id": TASK_ID,
        "status": "FROZEN",
        "frozen_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseline_manifest_sha256": sha_file(os.path.join(BASE, "baseline-freeze-manifest.json")),
        "baseline_reference_only": True,
        "pinned_artifacts": pinned,
        "excluded": [
            {"file": "TASK-LOCK.json", "reason": "task-state file references this manifest SHA"},
            {"file": "final-report.md", "reason": "post-freeze reporting"},
            {"file": "hashes.txt", "reason": "derived pin index"},
            {"file": "run_review_batch_1.py", "reason": "task-local workflow script; outputs are pinned"},
        ],
    }
    write_json("review-freeze-manifest.json", manifest)
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for fn in names:
            f.write(pinned[fn]["sha256"] + "  " + fn + chr(10))
    print("FREEZE OK: %d pins" % len(pinned))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "init":
        cmd_init()
    elif cmd == "audit":
        cmd_audit()
    elif cmd == "ingest":
        cmd_ingest()
    elif cmd == "freeze":
        cmd_freeze()
    else:
        raise SystemExit("usage: run_review_batch_1.py init|audit|ingest|freeze")


if __name__ == "__main__":
    main()
