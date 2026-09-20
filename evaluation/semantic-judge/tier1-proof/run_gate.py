#!/usr/bin/env python3
# Tier-1 operator gate over the 389 frozen hybrid rows (spec 16, 26).
# Rules:
#   - REVIEW_REQUIRED/INSUFFICIENT rows: operators may fire; valid proofs
#     move the row to auto; cross-operator conflict -> REVIEW (spec 19).
#   - Baseline auto rows whose (id, set) dual doctrine key is INSUFFICIENT:
#     re-derived. Valid Tier-1 proof keeps/sets the verdict; otherwise the
#     row is retracted to REVIEW_REQUIRED (spec 14: invalid proof -> review).
#   - All other rows: unchanged (frozen system finals stand).
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import tier1_operators as ops
import proof_validator as pv

SET_ALIAS = {"novel-development-40": "novel-40", "ent-controls": "ent"}


def norm(v):
    if not v:
        return None
    v = v.upper()
    return {"INSUFFICIENT_EVIDENCE": "INSUFFICIENT",
            "PARTIALLY_SUPPORTED": "PARTIAL"}.get(v, v)


def load_dual():
    dual = {}
    for fn in ["oracle-46-dual-labels.json", "novel-40-dual-labels.json",
               "ent-controls-dual-labels.json"]:
        d = json.load(open(os.path.join(BASE, "evaluation-contract", fn)))
        for c in d["cases"]:
            s = c.get("set") or ""
            dual[(c["case_id"], SET_ALIAS.get(s, s))] = {
                "semantic": norm(c.get("semantic_truth", {}).get("label")),
                "proof": norm(c.get("proof_safe", {}).get("label")),
                "inference": c.get("semantic_truth", {}).get(
                    "required_inference"),
                "status": c.get("annotation_status"),
            }
    return dual


def fresh_ops(claim, src):
    proofs, crashed = ops.run_operators(claim, src)
    valid, rejected = [], []
    for p in proofs:
        ok, why = pv.validate(p, claim, src)
        if ok:
            valid.append(p)
        else:
            rejected.append({"operator": p["operator"], "reason": why})
    return valid, rejected, crashed


def main():
    cmap = json.load(open(os.path.join(HERE, "results", "claims-map.json")))
    hyb = json.load(open(os.path.join(BASE, "hybrid", "results",
                                      "hybrid-eval.json")))
    dual = load_dual()
    rows = hyb["rows"]

    opnames = [f.__name__.upper() for f in ops.OPERATORS]
    impact = {n: {"eligible": 0, "fired": 0, "valid": 0,
                  "correct_semantic": 0, "correct_proof_safe": 0,
                  "reviews_eliminated": 0, "false_decisions": 0,
                  "invalid_rejected": 0, "conflicts": 0,
                  "abstentions": 0} for n in opnames}
    gate, conflicts, moved, retracted = [], 0, 0, 0
    for r in rows:
        cid, setn = r["id"], r["set"]
        d = dual.get((cid, setn))
        rec = {"id": cid, "set": setn,
               "baseline_final": r["final"], "baseline_path": r["path"],
               "fused_final": r["final"], "fused_path": r["path"],
               "valid_ops": [], "rejected": [], "conflict": False,
               "retracted": False, "dual_semantic": d["semantic"] if d else None,
               "dual_proof": d["proof"] if d else None}
        claim = cmap.get(cid, {}).get("claim", "")
        src = cmap.get(cid, {}).get("source_text", "")
        considered = False
        if r["final"] in ("REVIEW_REQUIRED", "INSUFFICIENT"):
            considered = True
        elif d and r["path"] == "auto" and d["proof"] == "INSUFFICIENT":
            considered = True
        if considered and claim and src:
            for n in opnames:
                impact[n]["eligible"] += 1
            valid, rejected, crashed = fresh_ops(claim, src)
            rec["operator_crash"] = crashed
            rec["rejected"] = rejected
            for p in valid:
                impact[p["operator"]]["fired"] += 1
                impact[p["operator"]]["valid"] += 1
            for rej in rejected:
                impact[rej["operator"]]["invalid_rejected"] += 1
            results = sorted({p["result"] for p in valid})
            if len(results) > 1:
                rec["conflict"] = True
                rec["fused_final"] = "REVIEW_REQUIRED"
                rec["fused_path"] = "review"
                conflicts += 1
                for p in valid:
                    impact[p["operator"]]["conflicts"] += 1
            elif len(results) == 1:
                rec["fused_final"] = results[0]
                rec["fused_path"] = "auto"
                rec["valid_ops"] = sorted({p["operator"] for p in valid})
                moved += 1
                for name in rec["valid_ops"]:
                    impact[name]["correct_semantic"] += int(
                        d is None or results[0] == d["semantic"])
                    impact[name]["correct_proof_safe"] += int(
                        d is None or results[0] == d["semantic"])
                    if r["final"] == "REVIEW_REQUIRED":
                        impact[name]["reviews_eliminated"] += 1
                    if d is not None and results[0] != d["semantic"]:
                        impact[name]["false_decisions"] += 1
            else:
                for n in opnames:
                    if not any(p["operator"] == n for p in valid):
                        impact[n]["abstentions"] += 1
                if r["path"] == "auto" and d and d["proof"] == "INSUFFICIENT":
                    rec["retracted"] = True
                    rec["fused_final"] = "REVIEW_REQUIRED"
                    rec["fused_path"] = "review"
                    retracted += 1
        gate.append(rec)

    # ---- product metrics
    after_auto = sum(1 for g in gate if g["fused_path"] == "auto")
    after_review = sum(1 for g in gate if g["fused_final"] == "REVIEW_REQUIRED")
    dual_rows = [g for g in gate if g["dual_semantic"]]
    sem_correct = sum(1 for g in dual_rows if g["fused_final"] == g["dual_semantic"])
    review_correct = sum(1 for g in dual_rows
                         if g["fused_final"] == "REVIEW_REQUIRED" and
                         (g["dual_semantic"] == "INSUFFICIENT" or
                          g["dual_proof"] == "INSUFFICIENT"))
    new_invalid = [g for g in gate if g["fused_path"] == "auto" and
                   g["dual_semantic"] and g["fused_final"] != g["dual_semantic"] and
                   g["baseline_path"] != "auto"]
    critical = [g for g in gate if g["fused_final"] in ("SUPPORTED", "CONTRADICTED")
                and g["dual_semantic"] in ("SUPPORTED", "CONTRADICTED")
                and g["fused_final"] != g["dual_semantic"]]
    # ---- review analysis (dual-labelled rows with baseline REVIEW final)
    rev = [g for g in gate if g["baseline_final"] == "REVIEW_REQUIRED" and
           g["dual_semantic"]]
    elim = [g for g in rev if g["fused_path"] == "auto" and not g["conflict"]]
    elim_correct = [g for g in elim if g["fused_final"] == g["dual_semantic"]]
    elim_unsafe = [g for g in elim if g["fused_final"] != g["dual_semantic"]]
    remaining = [g for g in rev if g["fused_path"] != "auto"]
    rem_nec = [g for g in remaining if g["dual_semantic"] == "INSUFFICIENT"]
    rem_unnec = [g for g in remaining if g["dual_semantic"] != "INSUFFICIENT"]
    tier2 = [{"id": g["id"], "set": g["set"],
              "semantic": g["dual_semantic"],
              "inference": dual.get((g["id"], g["set"]), {}).get("inference")}
             for g in rem_unnec]

    out = {
        "n_rows": len(rows),
        "after_auto": after_auto,
        "after_review_final": after_review,
        "conflicts": conflicts,
        "rows_moved_to_auto": moved,
        "rows_retracted_to_review": retracted,
        "dual_rows": len(dual_rows),
        "semantic_accuracy_dual_after": {"match": sem_correct,
                                         "n": len(dual_rows)},
        "review_abstention_appropriate": review_correct,
        "new_invalid_proofs": new_invalid,
        "critical_auto_errors_after": critical,
        "review_before": sum(1 for g in gate if g["baseline_final"] == "REVIEW_REQUIRED"),
        "reviews_eliminated": len(elim),
        "eliminated_correct": len(elim_correct),
        "eliminated_unsafe": len(elim_unsafe),
        "remaining_necessary": len(rem_nec),
        "remaining_unnecessary": len(rem_unnec),
        "tier2_candidates": tier2,
    }
    json.dump(out, open(os.path.join(HERE, "operator-impact-summary.json"),
                        "w"), ensure_ascii=False, indent=1)
    json.dump(impact, open(os.path.join(HERE, "results",
                                        "operator-impact.json"), "w"),
              ensure_ascii=False, indent=1)
    json.dump(gate, open(os.path.join(HERE, "results", "gate-results.json"),
                         "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "tier2_candidates"},
                     ensure_ascii=False))
    print("tier2_candidates:", len(tier2))
    print("impact:", json.dumps(impact))


if __name__ == "__main__":
    main()
