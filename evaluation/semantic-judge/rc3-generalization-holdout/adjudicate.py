#!/usr/bin/env python3
"""Adjudication: pass 1 vs pass 2, resolve disputes deterministically.

Agreement = equal semantic_truth, proof_safe, product_action,
genuine_insufficiency and (compounds) equal atom count with per-atom
semantic truth in order. Disputes are resolved by re-reading the exact
evidence packet; resolutions recorded with short notes.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "construction-audit"


def atom_match(c_atoms, p2_atoms):
    # Atom annotation contract applies to compound cases only; pass-2
    # atom decomposition of single claims is not a label dispute.
    if not c_atoms and not p2_atoms:
        return True
    if not c_atoms:
        return True
    if not c_atoms or not p2_atoms:
        return False
    if len(c_atoms) != len(p2_atoms):
        return False
    return all(a["semantic_truth"] == b["semantic_truth"]
               for a, b in zip(c_atoms, p2_atoms))


def main():
    data = json.loads((AUDIT / "cases-pass1.json").read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in data["cases"]}
    labels1 = data["labels"]
    pass2 = json.loads((AUDIT / "labels-pass2.json").read_text(encoding="utf-8"))
    selection = json.loads((AUDIT / "selection.json").read_text(encoding="utf-8"))
    core_ids = selection["core_ids"]
    rows, disputes = [], []
    for cid in core_ids:
        c = cases[cid]
        l1 = labels1[cid]
        p2 = pass2.get(cid, {})
        if p2.get("status") != "OK":
            disputes.append({"case_id": cid, "kind": "PASS2_MISSING",
                             "status": p2.get("status", "MISSING")})
            continue
        l2 = p2["label"]
        agree = (l1["semantic_truth"] == l2["semantic_truth"]
                 and l1["proof_safe"] == l2["proof_safe"]
                 and l1["product_action"] == l2["product_action"]
                 and l1["genuine_insufficiency"] == l2["genuine_insufficiency"]
                 and atom_match(c.get("atoms", []), l2.get("atoms", [])))
        rows.append({"case_id": cid, "agreement": agree,
                     "pass1": {k: l1[k] for k in
                               ("semantic_truth", "proof_safe",
                                "product_action")},
                     "pass2": {k: l2[k] for k in
                               ("semantic_truth", "proof_safe",
                                "product_action")},
                     "atom_count_pass1": len(c.get("atoms", [])),
                     "atom_count_pass2": len(l2.get("atoms", []))})
        if not agree:
            disputes.append({"case_id": cid, "kind": "LABEL_DISPUTE",
                             "pass1": l1, "pass2": l2,
                             "claim": c["claim"],
                             "sources": [s["text"] for s in c["sources"]]})
    n = max(1, len(rows))
    n_comp = sum(1 for r in rows if r["atom_count_pass1"])
    n_atom_agree = sum(1 for r in rows
                       if r["atom_count_pass1"] and
                       r["atom_count_pass1"] == r["atom_count_pass2"])
    stats = {
        "core": len(core_ids),
        "annotated_both": len(rows),
        "agreements": sum(1 for r in rows if r["agreement"]),
        "semantic_agreement": round(sum(
            1 for r in rows
            if r["pass1"]["semantic_truth"] == r["pass2"]["semantic_truth"]) / n, 4),
        "proof_safe_agreement": round(sum(
            1 for r in rows
            if r["pass1"]["proof_safe"] == r["pass2"]["proof_safe"]) / n, 4),
        "product_agreement": round(sum(
            1 for r in rows
            if r["pass1"]["product_action"] == r["pass2"]["product_action"]) / n, 4),
        "full_agreement": round(sum(
            1 for r in rows if r["agreement"]) / n, 4),
        "atom_count_agreement": round(n_atom_agree / max(1, n_comp), 4),
        "dispute_count": len(disputes),
    }
    (AUDIT / "agreement.json").write_text(
        json.dumps({"stats": stats, "rows": rows, "disputes": disputes},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
