#!/usr/bin/env python3
"""V1.6A.2 burned regressions: V1.6A-120 and V1.6A.1 targeted-60."""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from boundary_preclassifier import classify


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def family_stats(gold_ids, gold, results):
    stats = {"n": len(gold_ids), "non_abstain_n": 0, "abstain_n": 0,
             "correct_n": 0, "false_deterministic_n": 0,
             "false_deterministic_ids": [], "evidence_valid_n": 0}
    for fid in gold_ids:
        g = gold[fid]
        r = results[fid]
        if r["abstained"]:
            stats["abstain_n"] += 1
        else:
            stats["non_abstain_n"] += 1
        if not r["abstained"] and r.get("evidence_span") is not None and r["evidence_span"] in r["_text"]:
            stats["evidence_valid_n"] += 1
        if r["abstained"]:
            continue
        if r["label"] == g["expected_label"]:
            stats["correct_n"] += 1
        else:
            stats["false_deterministic_n"] += 1
            stats["false_deterministic_ids"].append(fid)
    nb = stats["non_abstain_n"]
    stats["precision"] = round(stats["correct_n"] / nb, 4) if nb else None
    stats["coverage"] = round(nb / stats["n"], 4) if stats["n"] else None
    stats["abstain_rate"] = round(stats["abstain_n"] / stats["n"], 4) if stats["n"] else None
    stats["evidence_span_validity"] = round(stats["evidence_valid_n"] / nb, 4) if nb else None
    return stats


def run_set(fix_path, gold_path, out_name, run_type, basis):
    fdoc = json.loads(Path(fix_path).read_text())
    fx = fdoc["fixtures"] if isinstance(fdoc, dict) and "fixtures" in fdoc else fdoc
    gdoc = json.loads(Path(gold_path).read_text())
    glist = gdoc["gold"] if isinstance(gdoc, dict) and "gold" in gdoc else gdoc
    gold = {x["id"]: x for x in glist}
    results = {}
    for x in fx:
        out = classify(x["text"], x.get("criterion"))
        dim = out.get(x.get("focus_dimension", "route_commitment"))
        results[x["id"]] = {"id": x["id"], "category": x.get("category"),
                            "linguistic_mode": x.get("linguistic_mode"),
                            "expected": gold[x["id"]]["expected_label"],
                            "label": dim["label"], "abstained": dim["abstained"],
                            "rule_id": dim.get("rule_id"),
                            "evidence_span": dim.get("evidence_span"),
                            "evidence_span_valid": (dim["abstained"] or
                                                    (dim.get("evidence_span") in x["text"])),
                            "reason": dim.get("reason"), "_text": x["text"], "_fx": x}
    doc = {"artifact": out_name, "run_type": run_type, "basis": basis,
           "engine_sha256": sha(HERE / "boundary_preclassifier.py"),
           "fixtures": len(fx)}
    return doc, fx, gold, results


# ---- burned regression 1: V1.6A 120 ----
doc, fx, gold, results = run_set(
    "../dev-corpus-semantic-judge-v1-6a/boundary-validation-fixtures.json",
    "../dev-corpus-semantic-judge-v1-6a/boundary-validation-gold-v1-6a.json",
    "burned-120-regression", "BURNED_REGRESSION_ONLY",
    "120 burned V1.6A validation fixtures (BURNED_PRECLASSIFIER_DEVELOPMENT_DATA); not fresh validation")
by_dim = {}
for fid, x in gold.items():
    fx_row = next(y for y in fx if y["id"] == fid)
    dim = fx_row.get("focus_dimension", "route_commitment")
    by_dim.setdefault(dim, []).append(fid)
families = {}
for dim, ids in sorted(by_dim.items()):
    st = family_stats(ids, gold, results)
    st.pop("_text", None)
    families[dim] = st
non_abstain_total = sum(f["non_abstain_n"] for f in families.values())
correct_total = sum(f["correct_n"] for f in families.values())
fd_total = sum(f["false_deterministic_n"] for f in families.values())
ev_total = sum(f["evidence_valid_n"] for f in families.values())
doc["families"] = families
doc["overall"] = {"non_abstain_n": non_abstain_total, "coverage": round(non_abstain_total / 120, 4),
                  "precision": round(correct_total / non_abstain_total, 4),
                  "false_deterministic_n": fd_total,
                  "evidence_span_validity": round(ev_total / non_abstain_total, 4)}
vh = results["VR-H-08"]
doc["vr_h_08"] = {"label": vh["label"], "abstained": vh["abstained"], "rule_id": vh["rule_id"],
                  "reason": vh.get("reason"), "requirement": "ABSTAIN",
                  "pass": vh["abstained"]}
va = results["VR-AB-04"]
doc["vr_ab_04"] = {"label": va["label"], "abstained": va["abstained"], "rule_id": va["rule_id"],
                   "reason": va.get("reason"),
                   "note": "expected ABSTAIN; compare label vs V1.6A/A.1 history"}
fam = families.get("route_commitment", {})
doc["hard_gates"] = {
    "overall_precision_ge_0_99": doc["overall"]["precision"] is not None and doc["overall"]["precision"] >= 0.99,
    "route_precision_ge_0_98": fam.get("precision") is not None and fam["precision"] >= 0.98,
    "every_family_precision_ge_0_98": all(f["precision"] is not None and f["precision"] >= 0.98 for f in families.values()),
    "safety_false_deterministic_zero": all(
        results[fid]["abstained"] or gold[fid]["expected_label"] == results[fid]["label"]
        for fid in results if results[fid].get("category") in ("safety", "critical", "safety_critical")),
    "total_false_deterministic_zero": fd_total == 0,
    "vr_h_08_abstains": vh["abstained"],
    "evidence_span_validity_100": doc["overall"]["evidence_span_validity"] == 1.0,
}
doc["all_gates_pass"] = all(doc["hard_gates"].values())
(Path(HERE) / "burned-120-regression.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("burned-120:", json.dumps({"overall": doc["overall"], "all_gates_pass": doc["all_gates_pass"],
                                  "false_ids": [i for f in families.values() for i in f["false_deterministic_ids"]]},
                                 ensure_ascii=False))

# ---- burned regression 2: V1.6A.1 targeted 60 ----
doc2, fx2, gold2, results2 = run_set(
    "../dev-corpus-semantic-judge-v1-6a1/targeted-validation-fixtures.json",
    "../dev-corpus-semantic-judge-v1-6a1/targeted-validation-gold.json",
    "burned-targeted60-regression", "BURNED_DIAGNOSTIC_REGRESSION",
    "60 V1.6A.1 targeted fixtures (BURNED_DIAGNOSTIC_DATA per process deviation); not official evidence")
by_dim2 = {}
for fid, x in gold2.items():
    fx_row = next(y for y in fx2 if y["id"] == fid)
    dim = fx_row.get("focus_dimension", "route_commitment")
    by_dim2.setdefault(dim, []).append(fid)
fam2 = {}
for dim, ids in sorted(by_dim2.items()):
    fam2[dim] = family_stats(ids, gold2, results2)
nb2 = sum(f["non_abstain_n"] for f in fam2.values())
c2 = sum(f["correct_n"] for f in fam2.values())
fd2 = sum(f["false_deterministic_n"] for f in fam2.values())
ev2 = sum(f["evidence_valid_n"] for f in fam2.values())
doc2["families"] = fam2
doc2["overall"] = {"non_abstain_n": nb2, "precision": round(c2 / nb2, 4) if nb2 else None,
                   "false_deterministic_n": fd2,
                   "abstain_n": 60 - nb2,
                   "evidence_span_validity": round(ev2 / nb2, 4) if nb2 else None}
adv = results2["ADV-11"]
doc2["adv_11_diagnostic"] = {"label": adv["label"], "abstained": adv["abstained"],
                             "rule_id": adv["rule_id"], "reason": adv.get("reason"),
                             "historical_label": "ASSERTED (BC_ROUTE_ASSERTED_01)"}
doc2["false_deterministic_ids"] = [i for f in fam2.values() for i in f["false_deterministic_ids"]]
doc2["note"] = "diagnostic only; no tuning based on this run"
(Path(HERE) / "burned-targeted60-regression.json").write_text(json.dumps(doc2, indent=2, ensure_ascii=False) + "\n")
print("burned-60:", json.dumps({"overall": doc2["overall"], "adv_11": doc2["adv_11_diagnostic"],
                                 "false_ids": doc2["false_deterministic_ids"]}, ensure_ascii=False))
