#!/usr/bin/env python3
"""AFK prep V1 integrity gate.

Read-only verification of the authoritative Batch 2 review lineage.
Writes SHA pins + PASS/FAIL to authoritative-integrity.json in this prep
lineage only. Never repairs or mutates authoritative inputs.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
CORPUS = os.path.join(EVAL, "dev-corpus-v1-1-repair")
BATCH = os.path.join(EVAL, "measurement-v3-human-review-batch-2-repaired")

def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def packet_body_sha(packet):
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

def main():
    pins = {}
    for name in ("manifest.json",):
        pins["corpus/" + name] = sha_file(os.path.join(CORPUS, name))
    for root, dirs, files in os.walk(os.path.join(CORPUS, "cases")):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), EVAL)
            pins["corpus/" + rel.split("cases" + os.sep, 1)[1] if False else rel] = sha_file(os.path.join(root, fn))
    for name in ("human-review-batch-manifest.json", "human-review-packets.jsonl",
                 "review-order.json", "human-review-workbook.md", "human-review-form.jsonl",
                 "reviewability-check.json", "review-leakage-audit.json", "source-repair-manifest.json"):
        pins["batch2/" + name] = sha_file(os.path.join(BATCH, name))

    packets = []
    with open(os.path.join(BATCH, "human-review-packets.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                packets.append(json.loads(line))
    with open(os.path.join(BATCH, "human-review-batch-manifest.json"), encoding="utf-8") as f:
        bm = json.load(f)
    with open(os.path.join(BATCH, "review-order.json"), encoding="utf-8") as f:
        ro = json.load(f)
    by_id = {p["packet_id"]: p for p in packets}
    manifest_map = {h["packet_id"]: h["sha256"] for h in bm["packet_hashes"]}
    mismatches = []
    for pid, p in by_id.items():
        calc = packet_body_sha(p)
        if not (p["packet_sha256"] == calc == manifest_map.get(pid)):
            mismatches.append(pid)
    order_ids = ro["critical_condition"] + ro["forbidden_claim"]
    order_match = order_ids == sorted(p["packet_id"] for p in packets if p["dimension"] == "critical_condition") + \
                  sorted(p["packet_id"] for p in packets if p["dimension"] == "forbidden_claim")

    existing_reviews = []
    for root, dirs, files in os.walk(BATCH):
        for fn in files:
            if "review" in fn.lower() and fn.endswith(".jsonl") and fn != "human-review-packets.jsonl" and fn != "human-review-form.jsonl":
                path = os.path.join(root, fn)
                with open(path, encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            row = json.loads(line)
                        except Exception:
                            continue
                        j = row.get("judgment") if isinstance(row, dict) else None
                        if isinstance(j, dict) and any(j.get(k) for k in
                            ("critical_evidence_state", "criterion_semantic_match", "speaker_commitment")):
                            existing_reviews.append({"file": os.path.relpath(path, EVAL), "line": i})

    checks = {
        "packet_count_file": len(packets) == 74,
        "packet_count_manifest": bm["total_packets"] == 74,
        "packet_hashes_valid_74": len(mismatches) == 0,
        "review_order_frozen_intact": order_match and len(order_ids) == 74,
        "reviewability_check_present": os.path.isfile(os.path.join(BATCH, "reviewability-check.json")),
        "leakage_audit_present": os.path.isfile(os.path.join(BATCH, "review-leakage-audit.json")),
        "existing_owner_reviews": len(existing_reviews),
        "zero_existing_owner_reviews": len(existing_reviews) == 0,
    }
    ok = all(v is True or (isinstance(v, int) and v == 0) for v in checks.values())
    result = {
        "artifact": "authoritative-integrity",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1",
        "checks": checks,
        "packet_sha_mismatches": mismatches,
        "existing_owner_review_rows": existing_reviews,
        "sha_pins": pins,
        "verdict": "PASS" if ok else "FAIL",
    }
    out = os.path.join(HERE, "authoritative-integrity.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, sort_keys=True)
    print("INTEGRITY:", result["verdict"], "| checks:", json.dumps(checks))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
