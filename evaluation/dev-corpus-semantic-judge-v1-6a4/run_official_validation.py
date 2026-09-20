#!/usr/bin/env python3
"""V1.6A.4 one-shot official validation. No reruns, no adjudication after
scoring, no engine changes after this runs."""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3 = os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3")
sys.path.insert(0, A3)

from a4_boundary_preclassifier import classify


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    fx_doc = json.load(open(os.path.join(HERE, "official-validation-fixtures.json")))
    gold_doc = json.load(open(os.path.join(HERE, "official-validation-gold-v1_6a4.json")))
    gold = {g["fixture_id"]: g for g in gold_doc["gold"]}

    results = {}
    for x in fx_doc["fixtures"]:
        out = classify(x["text"], x.get("criterion"))
        dim = out["forbidden_claim"]
        basis = dim.get("evidence_basis")
        span = dim.get("evidence_span")
        if dim["abstained"]:
            ev_valid = True
        elif basis == "ABSENCE_OF_PROHIBITED_ASSERTION":
            ev_valid = span is None and bool(dim.get("proposition_checked"))
        else:
            ev_valid = span is not None and span in x["text"]
        results[x["id"]] = {
            "id": x["id"], "stratum": x["stratum"], "group": x["group"],
            "expected": gold[x["id"]]["expected_label"],
            "label": dim["label"], "abstained": bool(dim["abstained"]),
            "rule_id": dim.get("rule_id"), "evidence_basis": basis,
            "evidence_span": span, "evidence_span_valid": ev_valid,
            "text": x["text"],
        }

    def stats(ids):
        st = {"n": len(ids), "non_abstain_n": 0, "abstain_n": 0, "correct_n": 0,
              "false_deterministic_n": 0, "false_deterministic_ids": [],
              "evidence_invalid_n": 0, "evidence_invalid_ids": []}
        for fid in ids:
            r = results[fid]
            if r["abstained"]:
                st["abstain_n"] += 1
            else:
                st["non_abstain_n"] += 1
                if r["label"] == r["expected"]:
                    st["correct_n"] += 1
                else:
                    st["false_deterministic_n"] += 1
                    st["false_deterministic_ids"].append(fid)
                if not r["evidence_span_valid"]:
                    st["evidence_invalid_n"] += 1
                    st["evidence_invalid_ids"].append(fid)
        st["precision"] = round(st["correct_n"] / st["non_abstain_n"], 4) if st["non_abstain_n"] else None
        st["coverage"] = round(st["non_abstain_n"] / st["n"], 4) if st["n"] else None
        st["correct_coverage"] = round(st["correct_n"] / st["n"], 4) if st["n"] else None
        st["abstain_rate"] = round(st["abstain_n"] / st["n"], 4) if st["n"] else None
        return st

    strata = {s: stats([i for i, r in results.items() if r["stratum"] == s])
              for s in ["CLEAN_RESOLVABLE", "REQUIRED_ABSTAIN", "ADVERSARIAL_MIXED"]}
    overall = stats(list(results))

    gates = {
        "overall_non_abstain_precision_ge_0_99": overall["precision"] is not None and overall["precision"] >= 0.99,
        "assertion_strength_precision_ge_0_99": overall["precision"] is not None and overall["precision"] >= 0.99,
        "safety_critical_false_deterministic_zero": overall["false_deterministic_n"] == 0,
        "required_abstain_unsafe_non_abstain_zero": strata["REQUIRED_ABSTAIN"]["false_deterministic_n"] == 0,
        "clean_resolvable_correct_coverage_ge_0_80": strata["CLEAN_RESOLVABLE"]["correct_coverage"] is not None and strata["CLEAN_RESOLVABLE"]["correct_coverage"] >= 0.80,
        "evidence_span_validity_1_0": overall["evidence_invalid_n"] == 0,
    }
    doc = {
        "artifact": "official-validation-results-v1_6a4",
        "run_type": "ONE_SHOT_OFFICIAL_VALIDATION",
        "task_id": fx_doc["task_id"],
        "engine_sha256": sha(os.path.join(HERE, "a4_boundary_preclassifier.py")),
        "fixtures_sha256": sha(os.path.join(HERE, "official-validation-fixtures.json")),
        "gold_sha256": sha(os.path.join(HERE, "official-validation-gold-v1_6a4.json")),
        "evidence_validity_definition": ("TEXT_SPAN results require evidence_span present in text; "
                                          "ABSENCE_OF_PROHIBITED_ASSERTION results require proposition_checked "
                                          "and no fabricated span; abstained rows are not evidence-bearing."),
        "overall": overall,
        "strata": strata,
        "hard_gates": gates,
        "all_gates_pass": all(gates.values()),
        "false_deterministic_ids": overall["false_deterministic_ids"],
        "results": results,
    }
    with open(os.path.join(HERE, "official-validation-results.json"), "w") as fh:
        fh.write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"overall": {k: v for k, v in overall.items() if k not in ("false_deterministic_ids", "evidence_invalid_ids")},
                      "strata_clean": {k: strata["CLEAN_RESOLVABLE"][k] for k in ["n", "non_abstain_n", "correct_n", "correct_coverage"]},
                      "strata_abstain": {k: strata["REQUIRED_ABSTAIN"][k] for k in ["n", "abstain_n", "false_deterministic_n"]},
                      "strata_adv": {k: strata["ADVERSARIAL_MIXED"][k] for k in ["n", "non_abstain_n", "correct_n", "false_deterministic_n"]},
                      "evidence_invalid": overall["evidence_invalid_n"],
                      "gates": gates, "all_gates_pass": doc["all_gates_pass"],
                      "false_ids": overall["false_deterministic_ids"]}, indent=1))


if __name__ == "__main__":
    main()
