#!/usr/bin/env python3
"""Task-local runner: evaluate a suite with a chosen engine_local copy."""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter

import re


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def _law_ref_error(claim, pred, gold):
    """A law-reference number parsed as a quantity that flips the verdict."""
    if pred == gold:
        return False
    law_spans = [(m.start(), m.end()) for m in re.finditer(
        r"(?:FOR-)?\d{4}-\d{2}-\d{2}(?:-\d+)?", claim)]
    if not law_spans:
        return False
    for q in parse_quantities(claim):
        span = (q.get("provenance") or {}).get("claim_span") or ""
        if not span:
            continue
        i = claim.find(span)
        if i >= 0 and any(i < te and ts < i + len(span)
                          for ts, te in law_spans):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    ap.add_argument("--engine-dir", required=True)
    ap.add_argument("--split", default=None,
                    help="development / hidden; omit for all cases")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", required=True,
                    choices=["baseline", "development", "global"])
    args = ap.parse_args()

    sys.path.insert(0, args.engine_dir)
    from engine_local.temporal import applicability_mismatch  # noqa: E402
    from engine_local.numeric import parse_quantities  # noqa: E402
    from engine_local.engine import evaluate_case  # noqa: E402

    cases = json.load(open(args.suite))["cases"]
    if args.split:
        cases = [c for c in cases if c.get("split") == args.split]

    STALE_TEMPORAL = {"HISTORICAL_VS_CURRENT", "PERIOD_MISMATCH",
                      "SUPERSEDED_VS_CURRENT"}
    MIS_CLASSES = {"HISTORICAL_VS_CURRENT", "PERIOD_MISMATCH",
                   "SUPERSEDED_VS_CURRENT"}
    out = {"mode": args.mode, "suite": os.path.basename(args.suite),
           "engine_dir": args.engine_dir, "cases": []}
    per_class = {}
    total = correct = 0
    false_stale = []
    rule_fail = Counter()
    ta_total = ta_correct = 0
    qid_total = qid_correct = 0
    comp_total = comp_correct = 0
    law_errors = 0
    unsound_eligible = []
    for c in cases:
        r = evaluate_case(c)
        atom_rels = [a.get("relation") or a["verdict"] for a in r["atoms"]]
        rules = [a.get("rule") for a in r["atoms"]]
        gold_rels = c.get("atom_rel") or [c["rel"]] * len(atom_rels)
        pred = atom_rels[0] if atom_rels else r["verdict"]
        gold = gold_rels[0] if gold_rels else c["rel"]
        total += len(gold_rels)
        for p, g in zip(atom_rels, gold_rels):
            per_class.setdefault(g, {"tp": 0, "fp": 0, "fn": 0})
            if p == g:
                correct += 1
                per_class[g]["tp"] += 1
            else:
                per_class[g]["fn"] += 1
                per_class.setdefault(p, {"tp": 0, "fp": 0, "fn": 0})
                per_class[p]["fp"] += 1
                rule_fail[rules[0] if rules else "?"] += 1
        is_stale_class = (c.get("temporal_applicability") in STALE_TEMPORAL
                          or c.get("quantity_status") in
                          {"HISTORICAL", "SUPERSEDED"})
        if pred == "CONTRADICTS" and gold != "CONTRADICTS" and is_stale_class:
            false_stale.append(c["case_id"])
        if pred == "ENTAILS" and gold != "ENTAILS":
            unsound_eligible.append(c["case_id"])
        ta = c.get("temporal_applicability")
        if ta and ta != "UNKNOWN":
            ta_total += 1
            all_text = " ".join(s["text"] for s in c["evidence"])
            if bool(applicability_mismatch(c["claim"], all_text)) == (
                    ta in MIS_CLASSES):
                ta_correct += 1
        if c.get("quantity_identity"):
            qid_total += 1
            if gold in ("ENTAILS", "CONTRADICTS"):
                if pred == gold:
                    qid_correct += 1
            elif pred not in ("ENTAILS", "CONTRADICTS"):
                qid_correct += 1
        if c.get("comparator_applicable"):
            comp_total += 1
            if pred == gold:
                comp_correct += 1
        if _law_ref_error(c["claim"], pred, gold):
            law_errors += 1
        out["cases"].append({"case_id": c["case_id"], "truth": gold,
                             "verdict": r["verdict"], "pred": pred,
                             "atom_relations": atom_rels, "rules": rules,
                             "stale_class": is_stale_class})

    f1s = []
    for k, v in per_class.items():
        p = v["tp"] / (v["tp"] + v["fp"]) if v["tp"] + v["fp"] else 0.0
        rc = v["tp"] / (v["tp"] + v["fn"]) if v["tp"] + v["fn"] else 0.0
        v["precision"] = round(p, 4)
        v["recall"] = round(rc, 4)
        v["f1"] = round(2 * p * rc / (p + rc), 4) if p + rc else 0.0
        if v["tp"] + v["fn"]:
            f1s.append(v["f1"])
    cp = per_class.get("CONTRADICTS", {})
    c_prec = cp.get("precision", 0.0)
    out["metrics"] = {
        "relation_accuracy": round(correct / max(1, total), 4),
        "macro_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        "per_class": per_class,
        "contradicts_precision": c_prec,
        "false_stale_contradicts": false_stale,
        "false_stale_contradicts_count": len(false_stale),
        "failing_rules": dict(rule_fail),
        "case_count": len(cases),
        "temporal_applicability_accuracy": (
            round(ta_correct / ta_total, 4) if ta_total else None),
        "temporal_applicability_scored": ta_total,
        "quantity_identity_accuracy": (
            round(qid_correct / qid_total, 4) if qid_total else None),
        "quantity_identity_scored": qid_total,
        "comparator_state_accuracy_on_applicable": (
            round(comp_correct / comp_total, 4) if comp_total else None),
        "comparator_applicable_count": comp_total,
        "law_reference_numeric_errors": law_errors,
        "unsound_eligible_proofs": unsound_eligible,
        "unsound_eligible_proofs_count": len(unsound_eligible),
    }
    out["provenance"] = {
        "engine_sha256": sha256(os.path.join(args.engine_dir,
                                             "engine_local", "engine.py")),
        "numeric_sha256": sha256(os.path.join(args.engine_dir,
                                              "engine_local", "numeric.py")),
        "boundary_sha256": sha256(os.path.join(args.engine_dir,
                                               "engine_local",
                                               "boundary.py")),
        "suite_sha256": sha256(args.suite),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    m = out["metrics"]
    print("mode:", args.mode, "| cases:", m["case_count"])
    print("relation_accuracy:", m["relation_accuracy"])
    print("macro_f1:", m["macro_f1"])
    for k in sorted(per_class):
        v = per_class[k]
        print("  %-24s P=%.3f R=%.3f F1=%.3f (tp=%d fp=%d fn=%d)"
              % (k, v["precision"], v["recall"], v["f1"],
                 v["tp"], v["fp"], v["fn"]))
    print("false_stale_contradicts:", m["false_stale_contradicts_count"],
          m["false_stale_contradicts"])
    print("failing_rules:", dict(rule_fail))
    print("temporal_applicability:", m["temporal_applicability_accuracy"],
          "on", m["temporal_applicability_scored"])
    print("quantity_identity:", m["quantity_identity_accuracy"], "on",
          m["quantity_identity_scored"])
    print("comparator_state_on_applicable:",
          m["comparator_state_accuracy_on_applicable"], "on",
          m["comparator_applicable_count"])
    print("law_reference_numeric_errors:",
          m["law_reference_numeric_errors"])
    print("unsound_eligible_proofs:",
          m["unsound_eligible_proofs_count"],
          m["unsound_eligible_proofs"])
    print("wrote", args.out)


if __name__ == "__main__":
    main()
