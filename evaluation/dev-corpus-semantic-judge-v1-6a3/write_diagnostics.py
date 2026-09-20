#!/usr/bin/env python3
"""Aggregation-only diagnostics over frozen official one-shot results."""
import hashlib, json
from pathlib import Path

HERE = Path(__file__).parent
BASE = HERE
res = json.loads((BASE / "official-validation-results.json").read_text())
per = res["per_fixture"]
fx = json.loads((BASE / "official-validation-fixtures.json").read_text())["fixtures"]


def stats(ids):
    s = {"n": len(ids), "non_abstain_n": 0, "abstain_n": 0, "correct_n": 0,
         "false_deterministic_ids": [], "unsafe_non_abstain_ids": []}
    for fid in ids:
        r = per[fid]
        if r["abstained"]:
            s["abstain_n"] += 1
        else:
            s["non_abstain_n"] += 1
            if r["correct_non_abstain"]:
                s["correct_n"] += 1
            else:
                s["false_deterministic_ids"].append(fid)
                if r["stratum"] == "REQUIRED_ABSTAIN":
                    s["unsafe_non_abstain_ids"].append(fid)
    nb = s["non_abstain_n"]
    s["precision"] = round(s["correct_n"] / nb, 4) if nb else None
    s["coverage"] = round(s["correct_n"] / s["n"], 4) if s["n"] else None
    return s


subgroups = {
    "quote_scope": [f["id"] for f in fx if "quote" in f["group"]],
    "parenthetical_scope": [f["id"] for f in fx if "parenthetical" in f["group"]],
    "mixed_polarity": [f["id"] for f in fx if "mixed_polarity" in f["group"]],
    "hedge_competition": [f["id"] for f in fx if "hedge_competition" in f["group"]],
    "multiple_candidates": [f["id"] for f in fx if "multi_candidate" in f["group"]],
    "retraction": [f["id"] for f in fx if "retraction" in f["group"]],
    "inventory": [f["id"] for f in fx if "inventory" in f["group"]],
    "cross_clause": [f["id"] for f in fx if "clause_scope_cross" in f["group"]],
}
sub = {k: stats(v) for k, v in subgroups.items()}
strata = {}
for name in ("CLEAN_DETERMINISTIC", "REQUIRED_ABSTAIN", "ADVERSARIAL_MIXED"):
    strata[name] = stats([f["id"] for f in fx if f["stratum"] == name])

results_sha = hashlib.sha256(
    (BASE / "official-validation-results.json").read_bytes()).hexdigest()
aggregation_note = ("Mechanical aggregation of frozen official-validation-results.json. "
                    "No engine rerun.")

doc = {"artifact": "subgroup-report.json", "task_id": res["task_id"],
       "run_type": "DIAGNOSTIC_AGGREGATION_OF_OFFICIAL_ONE_SHOT",
       "official_results_sha256": results_sha, "subgroups": sub,
       "note": aggregation_note}
(BASE / "subgroup-report.json").write_text(
    json.dumps(doc, indent=2, ensure_ascii=False) + chr(10))

sdoc = {"artifact": "stratum-report.json", "task_id": res["task_id"],
        "run_type": "DIAGNOSTIC_AGGREGATION_OF_OFFICIAL_ONE_SHOT",
        "official_results_sha256": results_sha, "strata": strata,
        "note": aggregation_note}
(BASE / "stratum-report.json").write_text(
    json.dumps(sdoc, indent=2, ensure_ascii=False) + chr(10))

pdoc = {"artifact": "precision-coverage-report.json", "task_id": res["task_id"],
        "overall": {
            "non_abstain_n": res["overall"]["non_abstain_n"],
            "precision": res["overall"]["precision"],
            "coverage_of_all": round(res["overall"]["correct_n"] / res["overall"]["n"], 4),
            "abstain_rate": round(res["overall"]["abstain_n"] / res["overall"]["n"], 4)},
        "clean_coverage": strata["CLEAN_DETERMINISTIC"]["coverage"],
        "clean_precision": strata["CLEAN_DETERMINISTIC"]["precision"],
        "adversarial_coverage": strata["ADVERSARIAL_MIXED"]["coverage"],
        "adversarial_precision": strata["ADVERSARIAL_MIXED"]["precision"],
        "required_abstain_unsafe_non_abstain":
            strata["REQUIRED_ABSTAIN"]["unsafe_non_abstain_ids"],
        "all_gates_pass": res["all_gates_pass"],
        "note": ("Coverage measures correct non-ABSTAIN share of each stratum; "
                 "ABSTAIN is the desired verdict on REQUIRED_ABSTAIN.")}
(BASE / "precision-coverage-report.json").write_text(
    json.dumps(pdoc, indent=2, ensure_ascii=False) + chr(10))

print("SUBGROUPS:")
for k, v in sub.items():
    print(" ", k, json.dumps({x: v[x] for x in
          ("n", "non_abstain_n", "abstain_n", "correct_n", "precision", "coverage")}))
print("STRATA:")
for k, v in strata.items():
    print(" ", k, json.dumps({x: v[x] for x in
          ("n", "non_abstain_n", "abstain_n", "correct_n", "precision", "coverage",
           "unsafe_non_abstain_ids")}))
print("WROTE subgroup-report.json, stratum-report.json, precision-coverage-report.json")
