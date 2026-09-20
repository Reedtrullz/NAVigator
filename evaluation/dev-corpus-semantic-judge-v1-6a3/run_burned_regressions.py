#!/usr/bin/env python3
"""V1.6A.3 burned regression cascade: burned-120, targeted-60, official-80.
Official-80 uses dual accounting: strict, and dispute-aware per the frozen
repair hypothesis (4 registered gold disputes excluded from the repair gate
denominator and disclosed). No tuning between runs."""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from boundary_preclassifier import classify

DISPUTES = ["OFF-SAME-17", "OFF-SCOPE-08", "OFF-SCOPE-09", "OFF-SCOPE-16"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def family_stats(gold_ids, gold, results):
    st = {"n": len(gold_ids), "non_abstain_n": 0, "abstain_n": 0,
          "correct_n": 0, "false_deterministic_n": 0,
          "false_deterministic_ids": [], "evidence_valid_n": 0}
    for fid in gold_ids:
        g, r = gold[fid], results[fid]
        if r["abstained"]: st["abstain_n"] += 1
        else: st["non_abstain_n"] += 1
        if not r["abstained"] and r.get("evidence_span") is not None and r["evidence_span"] in r["_text"]:
            st["evidence_valid_n"] += 1
        if r["abstained"]: continue
        if r["label"] == g["expected_label"]: st["correct_n"] += 1
        else:
            st["false_deterministic_n"] += 1
            st["false_deterministic_ids"].append(fid)
    nb = st["non_abstain_n"]
    st["precision"] = round(st["correct_n"] / nb, 4) if nb else None
    st["coverage"] = round(nb / st["n"], 4) if st["n"] else None
    st["abstain_rate"] = round(st["abstain_n"] / st["n"], 4) if st["n"] else None
    st["evidence_span_validity"] = round(st["evidence_valid_n"] / nb, 4) if nb else None
    return st


def load_set(fix_path, gold_path, gold_key="id"):
    fdoc = json.loads(Path(fix_path).read_text())
    fx = fdoc["fixtures"] if isinstance(fdoc, dict) and "fixtures" in fdoc else fdoc
    gdoc = json.loads(Path(gold_path).read_text())
    glist = gdoc["gold"] if isinstance(gdoc, dict) and "gold" in gdoc else gdoc
    gold = {}
    for x in glist:
        k = x.get(gold_key, x.get("id"))
        gold[k] = x
    results = {}
    for x in fx:
        out = classify(x["text"], x.get("criterion"))
        dim = out.get(x.get("focus_dimension", "route_commitment"))
        fid = x["id"]
        results[fid] = {"id": fid, "category": x.get("category"),
                        "expected": gold[fid]["expected_label"],
                        "label": dim["label"], "abstained": dim["abstained"],
                        "rule_id": dim.get("rule_id"),
                        "evidence_span": dim.get("evidence_span"),
                        "evidence_span_valid": (dim["abstained"] or (dim.get("evidence_span") in x["text"])),
                        "reason": dim.get("reason"), "_text": x["text"]}
    return fx, gold, results


def summarize(gold, results, exclude_ids=()):
    ids = [i for i in gold if i not in exclude_ids]
    fam = family_stats(ids, gold, results)
    dis_ids = [i for i in gold if i in exclude_ids]
    dis = family_stats(dis_ids, gold, results) if dis_ids else None
    return fam, dis


eng_sha = sha(HERE / "boundary_preclassifier.py")

# ---- 1. burned-120 ----
fx, gold, results = load_set(
    "../dev-corpus-semantic-judge-v1-6a/boundary-validation-fixtures.json",
    "../dev-corpus-semantic-judge-v1-6a/boundary-validation-gold-v1-6a.json")
fam, _ = summarize(gold, results)
doc = {"artifact": "burned-120-regression-v1-6a3", "run_type": "BURNED_REGRESSION_ONLY",
       "basis": "120 burned V1.6A fixtures (BURNED_PRECLASSIFIER_DEVELOPMENT_DATA)",
       "engine_sha256": eng_sha, "fixtures": 120,
       "families": {"route_commitment": fam},
       "overall": {"non_abstain_n": fam["non_abstain_n"], "coverage": fam["coverage"],
                   "precision": fam["precision"],
                   "false_deterministic_n": fam["false_deterministic_n"],
                   "evidence_span_validity": fam["evidence_span_validity"]}}
vh = results["VR-H-08"]
doc["vr_h_08"] = {"label": vh["label"], "abstained": vh["abstained"],
                  "rule_id": vh["rule_id"], "requirement": "ABSTAIN", "pass": vh["abstained"]}
doc["false_deterministic_ids"] = fam["false_deterministic_ids"]
doc["hard_gates"] = {
    "overall_precision_ge_0_99": fam["precision"] is not None and fam["precision"] >= 0.99,
    "false_deterministic_zero": fam["false_deterministic_n"] == 0,
    "vr_h_08_abstains": vh["abstained"],
    "evidence_span_validity_100": fam["evidence_span_validity"] == 1.0,
}
doc["all_gates_pass"] = all(doc["hard_gates"].values())
(HERE / "burned-120-regression.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("burned-120:", json.dumps({"overall": doc["overall"], "all_gates_pass": doc["all_gates_pass"],
                                  "false_ids": doc["false_deterministic_ids"]}, ensure_ascii=False))

# ---- 2. burned targeted-60 ----
fx2, gold2, results2 = load_set(
    "../dev-corpus-semantic-judge-v1-6a1/targeted-validation-fixtures.json",
    "../dev-corpus-semantic-judge-v1-6a1/targeted-validation-gold.json")
fam2, _ = summarize(gold2, results2)
doc2 = {"artifact": "burned-targeted60-regression-v1-6a3", "run_type": "BURNED_REGRESSION_ONLY",
        "basis": "60 burned V1.6A.1 targeted fixtures (BURNED_DIAGNOSTIC_DATA)",
        "engine_sha256": eng_sha, "fixtures": 60,
        "families": {"route_commitment": fam2},
        "overall": {"non_abstain_n": fam2["non_abstain_n"], "precision": fam2["precision"],
                    "false_deterministic_n": fam2["false_deterministic_n"],
                    "evidence_span_validity": fam2["evidence_span_validity"]}}
adv = results2["ADV-11"]
doc2["adv_11_diagnostic"] = {"label": adv["label"], "abstained": adv["abstained"],
                             "rule_id": adv["rule_id"], "requirement": "ABSTAIN", "pass": adv["abstained"]}
doc2["false_deterministic_ids"] = fam2["false_deterministic_ids"]
doc2["hard_gates"] = {
    "overall_precision_ge_0_99": fam2["precision"] is not None and fam2["precision"] >= 0.99,
    "false_deterministic_zero": fam2["false_deterministic_n"] == 0,
    "adv_11_abstains": adv["abstained"],
    "evidence_span_validity_100": fam2["evidence_span_validity"] == 1.0,
}
doc2["all_gates_pass"] = all(doc2["hard_gates"].values())
(HERE / "burned-targeted60-regression.json").write_text(json.dumps(doc2, indent=2, ensure_ascii=False) + "\n")
print("burned-60:", json.dumps({"overall": doc2["overall"], "all_gates_pass": doc2["all_gates_pass"],
                                 "false_ids": doc2["false_deterministic_ids"]}, ensure_ascii=False))

# ---- 3. burned official-80 (dual accounting) ----
fx3, gold3, results3 = load_set(
    "../dev-corpus-semantic-judge-v1-6a2/official-validation-fixtures.json",
    "../dev-corpus-semantic-judge-v1-6a2/official-validation-gold.json", gold_key="fixture_id")
strict, _ = summarize(gold3, results3)
aware, dis = summarize(gold3, results3, exclude_ids=DISPUTES)
doc3 = {"artifact": "burned-v1-6a2-80-regression-v1-6a3", "run_type": "BURNED_REGRESSION_ONLY",
        "basis": "80 burned official V1.6A.2 fixtures (BURNED_BOUNDARY_DIAGNOSTIC_DATA)",
        "engine_sha256": eng_sha, "fixtures": 80,
        "accounting": {
          "strict": {"note": "disputed fixtures counted as false deterministics",
                     "non_abstain_n": strict["non_abstain_n"], "abstain_n": strict["abstain_n"],
                     "correct_n": strict["correct_n"], "false_deterministic_n": strict["false_deterministic_n"],
                     "precision": strict["precision"], "evidence_span_validity": strict["evidence_span_validity"]},
          "dispute_aware": {"note": "4 registered gold disputes excluded from denominator per frozen repair-hypothesis; disclosed, not tuned",
                            "excluded_ids": DISPUTES,
                            "non_abstain_n": aware["non_abstain_n"], "abstain_n": aware["abstain_n"],
                            "correct_n": aware["correct_n"], "false_deterministic_n": aware["false_deterministic_n"],
                            "precision": aware["precision"], "evidence_span_validity": aware["evidence_span_validity"]}},
        "disputes": {i: {"expected": gold3[i]["expected_label"], "label": results3[i]["label"],
                         "abstained": results3[i]["abstained"], "rule_id": results3[i].get("rule_id")} for i in DISPUTES},
        "false_deterministic_ids_dispute_aware": aware["false_deterministic_ids"],
        "false_deterministic_ids_strict": strict["false_deterministic_ids"],
        "hard_gates_dispute_aware": {
            "overall_precision_ge_0_99": aware["precision"] is not None and aware["precision"] >= 0.99,
            "false_deterministic_zero": aware["false_deterministic_n"] == 0,
            "evidence_span_validity_100": aware["evidence_span_validity"] == 1.0,
        },
        "note": "Gate basis is dispute-aware per frozen repair-hypothesis (frozen pre-implementation); strict accounting disclosed alongside."}
doc3["all_gates_pass"] = all(doc3["hard_gates_dispute_aware"].values())
(HERE / "burned-v1-6a2-80-regression.json").write_text(json.dumps(doc3, indent=2, ensure_ascii=False) + "\n")
print("official-80 strict:", json.dumps({k: strict[k] for k in ("non_abstain_n", "correct_n", "false_deterministic_n", "precision")}, ensure_ascii=False))
print("official-80 dispute-aware:", json.dumps({k: aware[k] for k in ("non_abstain_n", "correct_n", "false_deterministic_n", "precision")}, ensure_ascii=False))
print("official-80 gates:", json.dumps(doc3["all_gates_pass"]), "false_ids_aware:", aware["false_deterministic_ids"])
