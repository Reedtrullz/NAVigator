#!/usr/bin/env python3
"""V1.6A.3 official one-shot validation: 120 fresh fixtures, frozen engine,
frozen gold. No reruns, no post-execution engine or gold changes."""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from boundary_preclassifier import classify


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


SUBGROUPS = {
    "quote_scope": lambda g: "quote" in g,
    "parenthetical_scope": lambda g: "parenthetical" in g,
    "mixed_polarity": lambda g: "mixed_polarity" in g,
    "hedge_competition": lambda g: "hedge_competition" in g,
    "multiple_candidates": lambda g: "multi_candidate" in g,
    "retraction": lambda g: "retraction" in g,
    "inventory": lambda g: "inventory" in g,
    "cross_clause": lambda g: "clause_scope_cross" in g,
}


def main():
    fdoc = json.loads((HERE / "official-validation-fixtures.json").read_text())
    fx = fdoc["fixtures"]
    gdoc = json.loads((HERE / "official-validation-gold.json").read_text())
    gold = {x["fixture_id"]: x for x in gdoc["gold"]}
    assert len(fx) == 120 and len(gold) == 120, "fixture/gold count mismatch"

    hdoc = json.loads((HERE / "official-fixture-hashes.json").read_text())
    cur_sha = sha(HERE / "official-validation-fixtures.json")
    assert cur_sha == hdoc["fixture_file_sha256"], "fixture file SHA mismatch"

    engine_sha = sha(HERE / "boundary_preclassifier.py")
    assert engine_sha == "21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b", +        "engine SHA does not match frozen candidate"

    results = {}
    for x in fx:
        out = classify(x["text"], x.get("criterion"))
        dim = out["route_commitment"]
        g = gold[x["id"]]
        results[x["id"]] = {
            "id": x["id"], "stratum": x["stratum"], "group": x["group"],
            "expected": g["expected_label"],
            "label": dim["label"], "abstained": dim["abstained"],
            "rule_id": dim.get("rule_id"),
            "evidence_span_valid": (dim["abstained"] or
                                    (dim.get("evidence_span") in x["text"])),
            "correct_non_abstain": (not dim["abstained"]
                                    and dim["label"] == g["expected_label"]),
            "reason": dim.get("reason"),
        }

    def stats(ids):
        s = {"n": len(ids), "non_abstain_n": 0, "abstain_n": 0,
             "correct_n": 0, "false_deterministic_n": 0,
             "false_deterministic_ids": [], "evidence_valid_n": 0,
             "unsafe_non_abstain_n": 0, "unsafe_non_abstain_ids": []}
        for fid in ids:
            r = results[fid]
            if r["abstained"]:
                s["abstain_n"] += 1
            else:
                s["non_abstain_n"] += 1
                if r["evidence_span_valid"]:
                    s["evidence_valid_n"] += 1
                if r["correct_non_abstain"]:
                    s["correct_n"] += 1
                else:
                    s["false_deterministic_n"] += 1
                    s["false_deterministic_ids"].append(fid)
                if r["stratum"] == "REQUIRED_ABSTAIN":
                    s["unsafe_non_abstain_n"] += 1
                    s["unsafe_non_abstain_ids"].append(fid)
        nb = s["non_abstain_n"]
        s["precision"] = round(s["correct_n"] / nb, 4) if nb else None
        s["coverage_of_stratum"] = round(s["correct_n"] / s["n"], 4) if s["n"] else None
        s["evidence_span_validity"] = round(s["evidence_valid_n"] / nb, 4) if nb else None
        return s

    strata = {}
    for name in ("CLEAN_DETERMINISTIC", "REQUIRED_ABSTAIN", "ADVERSARIAL_MIXED"):
        strata[name] = stats([x["id"] for x in fx if x["stratum"] == name])
    groups = {}
    for x in fx:
        groups.setdefault(x["group"], []).append(x["id"])
    group_stats = {g: stats(ids) for g, ids in sorted(groups.items())}
    all_ids = [x["id"] for x in fx]
    overall = stats(all_ids)

    adv = strata["ADVERSARIAL_MIXED"]
    adv_denominator_sufficient = adv["non_abstain_n"] >= 10
    clean = strata["CLEAN_DETERMINISTIC"]
    gates = {
        "overall_non_abstain_precision_ge_0_99":
            overall["precision"] is not None and overall["precision"] >= 0.99,
        "route_precision_ge_0_99":
            overall["precision"] is not None and overall["precision"] >= 0.99,
        "safety_critical_false_deterministic_zero":
            strata["REQUIRED_ABSTAIN"]["unsafe_non_abstain_n"] == 0,
        "evidence_span_validity_100":
            overall["evidence_span_validity"] == 1.0,
        "required_abstain_unsafe_non_abstain_zero":
            strata["REQUIRED_ABSTAIN"]["unsafe_non_abstain_n"] == 0,
        "clean_coverage_ge_0_80":
            clean["coverage_of_stratum"] is not None
            and clean["coverage_of_stratum"] >= 0.80,
        "clean_precision_ge_0_99":
            clean["precision"] is not None and clean["precision"] >= 0.99,
        "adversarial_precision_ge_0_98":
            (adv["precision"] is not None and adv["precision"] >= 0.98)
            if adv_denominator_sufficient else True,
    }

    doc = {
        "artifact": "official-validation-results-v1-6a3",
        "task_id": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A3-AMBIGUITY-ABSTENTION-HARDENING",
        "run_type": "OFFICIAL_ONE_SHOT",
        "engine_sha256": engine_sha,
        "fixture_file_sha256": cur_sha,
        "gold_sha256": sha(HERE / "official-validation-gold.json"),
        "n": 120,
        "overall": overall,
        "strata": strata,
        "groups": group_stats,
        "per_fixture": {fid: {k: v for k, v in results[fid].items()} for fid in all_ids},
        "hard_gates": gates,
        "adversarial_denominator_sufficient": adv_denominator_sufficient,
        "all_gates_pass": all(gates.values()),
        "false_deterministic_ids": overall["false_deterministic_ids"],
        "unsafe_non_abstain_ids": strata["REQUIRED_ABSTAIN"]["unsafe_non_abstain_ids"],
        "note": ("Official one-shot run of the frozen V1.6A.3 engine on 120 fresh "
                 "fixtures against frozen gold. No reruns; no post-execution fixes."),
    }
    (HERE / "official-validation-results.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + chr(10))
    print(json.dumps({
        "overall": {k: overall[k] for k in
                    ("n", "non_abstain_n", "abstain_n", "precision",
                     "false_deterministic_n", "evidence_span_validity")},
        "strata": {name: {k: s[k] for k in
                          ("n", "non_abstain_n", "abstain_n", "correct_n",
                           "precision", "coverage_of_stratum",
                           "unsafe_non_abstain_n")}
                   for name, s in strata.items()},
        "hard_gates": gates,
        "all_gates_pass": doc["all_gates_pass"],
        "false_deterministic_ids": doc["false_deterministic_ids"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
