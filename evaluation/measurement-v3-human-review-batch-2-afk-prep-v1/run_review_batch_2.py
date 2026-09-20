#!/usr/bin/env python3
"""Mechanical ingest/derive/freeze runner for Batch 2 OWNER-01 reviews.

Reads owner-reviews-draft.jsonl (written by the cockpit or transcribed
externally), validates every row (schema, enums, SHA binding, verbatim
spans via the frozen V2.15 lane), derives final verdicts mechanically,
and can freeze completed results. No semantic decisions are made here.

Commands:
  validate   dry-run validation of the draft file (0 rows is OK)
  ingest     validate + derive; refuses unless all 74 packets have a valid
             review unless --allow-partial is given explicitly
  freeze     freeze completed results + manifest + hashes (ingest required)
"""
import argparse, datetime, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
BATCH = os.path.join(EVAL, "measurement-v3-human-review-batch-2-repaired")
V15 = os.path.join(EVAL, "measurement-v2-15-semantic-human-review-fallback")
sys.path.insert(0, HERE)
sys.path.insert(0, V15)
import prep_lib as P
import review_lane_semantic_v2_15 as LANE

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2"
DRAFT = os.path.join(HERE, "owner-reviews-draft.jsonl")


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_json(name, obj):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)


def load_draft():
    rows = []
    if not os.path.exists(DRAFT):
        return rows
    with open(DRAFT, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def validate_rows(rows, require_all):
    packets = P.load_packets()
    by_id = {p["packet_id"]: p for p in packets}
    order = P.load_order()
    seen, valid, invalid = set(), [], []
    for r in rows:
        errs = P.validate_review_row(r, by_id, seen)
        if errs:
            invalid.append({"packet_id": r.get("packet_id"), "errors": errs})
        else:
            valid.append(r)
    missing = [pid for pid in order if pid not in seen]
    result = {"rows_total": len(rows), "valid": len(valid), "invalid": len(invalid),
              "invalid_details": invalid, "missing_packet_ids": missing,
              "complete": len(valid) == 74 and not invalid}
    if require_all and not result["complete"]:
        print("REFUSED: %d/74 valid, %d invalid, %d missing." % (len(valid), len(invalid), len(missing)))
        print("All 74 OWNER-01 reviews are required. --allow-partial is a bounded",
              "checkpoint only and never produces a final freeze.")
        sys.exit(2)
    return valid, invalid, result


def clean_row(r, p):
    j = r["judgment"]
    if p["dimension"] == "critical_condition":
        clean = {"critical_evidence_state": j["critical_evidence_state"],
                 "evidence_spans": j.get("evidence_spans", []), "note": j.get("note", "")}
    else:
        clean = {"criterion_semantic_match": j["criterion_semantic_match"],
                 "speaker_commitment": j["speaker_commitment"],
                 "evidence_spans": j.get("evidence_spans", []), "note": j.get("note", "")}
    return {"packet_id": r["packet_id"], "packet_sha256": p["packet_sha256"],
            "reviewer_id": r["reviewer_id"], "contract_version": p["contract_version"],
            "reviewed_utc": r["reviewed_utc"], "judgment": clean}


def cmd_ingest(allow_partial):
    rows = load_draft()
    if not rows:
        print("REFUSED: owner-reviews-draft.jsonl has no rows. Nothing to ingest.")
        sys.exit(2)
    valid, invalid, report = validate_rows(rows, require_all=not allow_partial)
    packets = {p["packet_id"]: p for p in P.load_packets()}
    derived, non_derivable = [], []
    for r in valid:
        p = packets[r["packet_id"]]
        probe = clean_row(r, p)
        ok, why = LANE.validate_review(p, probe)
        if not ok:
            non_derivable.append({"packet_id": r["packet_id"], "reason": why})
            continue
        try:
            final = LANE.derive_final(p["dimension"], probe["judgment"])
        except Exception as e:
            non_derivable.append({"packet_id": r["packet_id"], "reason": repr(e)})
            continue
        derived.append({"packet_id": r["packet_id"], "dimension": p["dimension"],
                        "intermediate": probe["judgment"], "final_verdict": final,
                        "reviewer_id": r["reviewer_id"], "reviewed_utc": r["reviewed_utc"],
                        "derivation": "frozen judge_core_v2_13.derive_final (mechanical)"})
    write_json("review-validation.json", {
        "artifact": "review-validation", "task_id": TASK_ID,
        "reviews_total": len(rows), "reviews_valid": len(valid),
        "reviews_invalid": len(invalid), "invalid_details": report["invalid_details"],
        "non_derivable": non_derivable, "complete_74": report["complete"],
        "by_dimension": {d: sum(1 for x in derived if x["dimension"] == d)
                         for d in ("critical_condition", "forbidden_claim")}})
    write_json("derived-human-verdicts.json", {
        "artifact": "derived-human-verdicts", "task_id": TASK_ID,
        "derivation": "mechanical via frozen V2.15 lane / judge_core_v2_13.derive_final; no AI judgment",
        "reviewer_policy": "SINGLE_HUMAN_REVIEW", "n": len(derived),
        "derived": derived})
    with open(os.path.join(HERE, "adjudications.jsonl"), "w", encoding="utf-8") as f:
        for d in derived:
            f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + chr(10))
    print("INGEST: valid=%d invalid=%d derived=%d non_derivable=%d complete=%s"
          % (len(valid), len(invalid), len(derived), len(non_derivable), report["complete"]))
    sys.exit(0 if derived and not non_derivable else 3)


def cmd_freeze():
    dv_path = os.path.join(HERE, "derived-human-verdicts.json")
    rv_path = os.path.join(HERE, "review-validation.json")
    if not (os.path.exists(dv_path) and os.path.exists(rv_path)):
        print("REFUSED: run ingest first.")
        sys.exit(2)
    dv = json.load(open(dv_path, encoding="utf-8"))
    rv = json.load(open(rv_path, encoding="utf-8"))
    if not rv.get("complete_74") or dv["n"] != 74:
        print("REFUSED: freeze requires 74/74 complete valid reviews.")
        sys.exit(2)
    write_json("completed-measurement-results.json", {
        "artifact": "completed-measurement-results", "task_id": TASK_ID,
        "deterministic_criteria": 526, "human_reviewed_criteria": 74,
        "total_authoritative_criteria": 600, "target": 600,
        "human_review_pending": 0, "human_review_invalid": rv["reviews_invalid"],
        "note": "deterministic results referenced from frozen baseline by SHA; human verdicts added by authority only"})
    excluded = {"TASK-LOCK.json", "review-freeze-manifest.json", "hashes.txt",
                "final-report.md", "run_review_batch_2.py", "owner-reviews-draft.jsonl"}
    names = sorted(fn for fn in os.listdir(HERE)
                   if fn not in excluded and os.path.isfile(os.path.join(HERE, fn)))
    pinned = {fn: sha_file(os.path.join(HERE, fn)) for fn in names}
    write_json("review-freeze-manifest.json", {
        "artifact": "review-freeze-manifest", "task_id": TASK_ID, "status": "FROZEN",
        "frozen_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "batch_manifest_sha256": sha_file(os.path.join(BATCH, "human-review-batch-manifest.json")),
        "pinned_artifacts": pinned})
    with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
        for fn in names:
            f.write(pinned[fn] + "  " + fn + chr(10))
    print("FREEZE OK: %d pins" % len(pinned))


def main():
    ap = argparse.ArgumentParser(description="Batch 2 mechanical ingest/derive/freeze (no semantic decisions).")
    ap.add_argument("command", choices=["validate", "ingest", "freeze"])
    ap.add_argument("--allow-partial", action="store_true",
                    help="bounded checkpoint ingest of fewer than 74 reviews; never freezes")
    a = ap.parse_args()
    if a.command == "validate":
        _, _, report = validate_rows(load_draft(), require_all=False)
        print(json.dumps(report, indent=2))
        sys.exit(0 if not report["invalid"] else 1)
    elif a.command == "ingest":
        cmd_ingest(a.allow_partial)
    elif a.command == "freeze":
        cmd_freeze()


if __name__ == "__main__":
    main()
