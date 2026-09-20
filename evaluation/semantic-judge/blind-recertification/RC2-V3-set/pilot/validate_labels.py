#!/usr/bin/env python3
"""Validate a pilot pass file against the fixed vocabulary and slot mapping (contract v3)."""
import json
import sys

SEMANTIC = {"SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"}
PROOF = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"}
PRODUCT = {"AUTO_SUPPORTED", "AUTO_CONTRADICTED", "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"}
PAIRS = {
    "SUPPORTED": ("SUPPORTED", "AUTO_SUPPORTED"),
    "CONTRADICTED": ("CONTRADICTED", "AUTO_CONTRADICTED"),
}


def main(path):
    rows = json.load(open(path))
    errors = []
    ids = set()
    for r in rows:
        cid = r.get("case_id", "<missing>")
        if cid in ids:
            errors.append(f"{cid}: duplicate case_id")
        ids.add(cid)
        s, p, a = r.get("semantic_truth"), r.get("proof_safe"), r.get("product_action")
        if s not in SEMANTIC:
            errors.append(f"{cid}: invalid semantic_truth {s!r}")
        if p not in PROOF:
            errors.append(f"{cid}: invalid proof_safe {p!r}")
        if a not in PRODUCT:
            errors.append(f"{cid}: invalid product_action {a!r}")
        if s in PAIRS and (p, a) != PAIRS[s]:
            errors.append(f"{cid}: mapping violation {s} -> ({p}, {a})")
    for e in errors:
        print("FAIL:", e)
    print(f"{path}: {len(rows)} rows, {'OK' if not errors else str(len(errors)) + ' violations'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
