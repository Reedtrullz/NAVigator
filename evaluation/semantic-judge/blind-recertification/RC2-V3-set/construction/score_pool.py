#!/usr/bin/env python3
"""Merge two independent construction passes, score pool agreement, list disputes."""
import json
import sys

SLOTS = ("semantic_truth", "proof_safe", "product_action")
VALID_FLAGS = {
    "multi_span", "compound", "numeric", "temporal", "actor", "modality",
    "cond_exc", "safety", "legal", "locality", "age_legal",
}


def load_rows(path):
    rows = json.load(open(path))
    assert len(rows) == 277, f"{path}: expected 277 rows, got {len(rows)}"
    by_id = {}
    for r in rows:
        cid = r["case_id"]
        assert cid not in by_id, f"{path}: duplicate {cid}"
        by_id[cid] = r
    return by_id


def main(pool_path, p1_path, p2_path):
    pool = json.load(open(pool_path))["cases"]
    a, b = load_rows(p1_path), load_rows(p2_path)
    ids = {c["case_id"] for c in pool}
    assert set(a) == set(b) == ids, "pass files do not cover the pool exactly"
    slot_same = {s: 0 for s in SLOTS}
    flag_same = 0
    disputes = []
    merged = []
    for c in pool:
        cid = c["case_id"]
        p1 = {s: a[cid][s] for s in SLOTS}
        p2 = {s: b[cid][s] for s in SLOTS}
        f1, f2 = set(a[cid]["flags"]), set(b[cid]["flags"])
        bad = (f1 | f2) - VALID_FLAGS
        assert not bad, f"{cid}: invalid flags {sorted(bad)}"
        agree = all(p1[s] == p2[s] for s in SLOTS)
        for s in SLOTS:
            if p1[s] == p2[s]:
                slot_same[s] += 1
        flags_agree = f1 == f2
        flag_same += flags_agree
        row = {"case_id": cid, "claim": c["claim"], "sources": c["sources"],
               "provenance": c["provenance"], "v2_batch": c["v2_batch"],
               "pass1": {**p1, "flags": sorted(f1)},
               "pass2": {**p2, "flags": sorted(f2)},
               "labels_agree": agree, "flags_agree": flags_agree}
        if not agree or not flags_agree:
            disputes.append({"case_id": cid,
                             "label_disputes": [s for s in SLOTS if p1[s] != p2[s]],
                             "flag_disputes": sorted(f1 ^ f2),
                             "pass1": row["pass1"], "pass2": row["pass2"]})
        merged.append(row)
    n = len(merged)
    summary = {
        "n": n,
        "slot_agreement": {s: round(slot_same[s] / n, 4) for s in SLOTS},
        "flag_agreement": round(flag_same / n, 4),
        "n_full_agreement": sum(1 for r in merged if r["labels_agree"] and r["flags_agree"]),
        "n_disputes": len(disputes),
    }
    json.dump({"summary": summary, "disputes": disputes}, open("construction/disputes.json", "w"), indent=1, ensure_ascii=False)
    json.dump({"cases": merged}, open("construction/pool-annotated.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
