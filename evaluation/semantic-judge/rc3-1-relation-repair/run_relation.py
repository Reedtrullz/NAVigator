"""Relation harness for the RC3.1 engine (provenance-logged).

Scores the fresh relation suite at ATOM level against the frozen metric
contract (relation-metrics-v2.json): per-atom expected_atoms for compound
cases, top-level rel for single-atom cases. Also re-runs burned TRAIN as
diagnostics. No case-ID logic, no expected-label maps in the engine.
"""
import collections
import hashlib
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.abspath(os.path.join(HERE, "..", "rc3-1-proof-semantics"))
sys.path.insert(0, PROOF_DIR)

from rc3_1_engine import engine  # noqa: E402


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def provenance():
    return {
        "python": platform.python_version(),
        "engine_sha256": sha256_file(
            os.path.join(PROOF_DIR, "rc3_1_engine", "engine.py")),
        "suite_sha256": sha256_file(os.path.join(HERE, "fresh-relation-cases.json")),
        "contract_sha256": sha256_file(
            os.path.join(HERE, "relation-contract-v2.md")),
        "metrics_sha256": sha256_file(os.path.join(HERE, "relation-metrics-v2.json")),
        "lattice_sha256": sha256_file(
            os.path.join(HERE, "modality-relation-lattice.json")),
    }


def atom_decisions(suite):
    """Yield (case, atom_index, expected, got, rule) for every atom."""
    for c in suite:
        expected_atoms = c.get("expected_atoms")
        if c.get("compound") and expected_atoms:
            r = engine.evaluate_case(c)
            for i, a in enumerate(r["atoms"]):
                exp = expected_atoms[i] if i < len(expected_atoms) else c["rel"]
                got = a.get("relation", a["verdict"])
                yield c, i, exp, got, a["rule"]
        else:
            r = engine.evaluate_atom(c["claim"], c["evidence"])
            yield c, 0, c["rel"], r.get("relation", r["verdict"]), r["rule"]


def score_fresh(suite):
    conf = collections.Counter()
    critical_false_entails = []
    critical_false_contradicts = []
    errors = []
    group_hit = collections.Counter()
    group_total = collections.Counter()
    for c, ai, exp, got, rule in atom_decisions(suite):
        conf[(exp, got)] += 1
        group_total[c["group"]] += 1
        if exp == got:
            group_hit[c["group"]] += 1
        else:
            errors.append({"case_id": c["case_id"], "atom": ai + 1,
                           "expected": exp, "got": got, "rule": rule,
                           "group": c["group"], "critical": c.get("critical", False)})
        if c.get("critical") and exp != got:
            if got == "ENTAILS":
                critical_false_entails.append(
                    {"case_id": c["case_id"], "atom": ai + 1, "expected": exp})
            if got == "CONTRADICTS":
                critical_false_contradicts.append(
                    {"case_id": c["case_id"], "atom": ai + 1, "expected": exp})
    labels = ["ENTAILS", "CONTRADICTS", "PARTIAL",
              "RELATED_BUT_INSUFFICIENT", "AMBIGUOUS", "UNRELATED"]
    prec, rec, f1 = {}, {}, {}
    for lab in labels:
        tp = conf[(lab, lab)]
        fp = sum(v for (e, g), v in conf.items() if g == lab and e != lab)
        fn = sum(v for (e, g), v in conf.items() if e == lab and g != lab)
        prec[lab] = round(tp / (tp + fp), 4) if tp + fp else None
        rec[lab] = round(tp / (tp + fn), 4) if tp + fn else None
        f1[lab] = (round(2 * prec[lab] * rec[lab] / (prec[lab] + rec[lab]), 4)
                   if prec[lab] and rec[lab] else None)
    valid_f1 = [v for v in f1.values() if v is not None]
    total = sum(conf.values())
    metrics = {
        "atom_decisions": total,
        "atom_relation_accuracy": round(
            sum(v for (e, g), v in conf.items() if e == g) / total, 4),
        "macro_f1": round(sum(valid_f1) / len(valid_f1), 4) if valid_f1 else None,
        "entails_precision": prec["ENTAILS"],
        "contradicts_precision": prec["CONTRADICTS"],
        "insufficient_recall": rec["RELATED_BUT_INSUFFICIENT"],
        "critical_false_entails": len(critical_false_entails),
        "critical_false_contradicts": len(critical_false_contradicts),
        "per_class": {lab: {"precision": prec[lab], "recall": rec[lab],
                            "f1": f1[lab]} for lab in labels},
        "subgroup_accuracy": {g: round(group_hit[g] / group_total[g], 4)
                              for g in sorted(group_total)},
        "confusion_matrix": {f"{e}->{g}": v for (e, g), v in sorted(conf.items())},
    }
    return {"metrics": metrics, "errors": errors,
            "critical_false_entails_rows": critical_false_entails,
            "critical_false_contradicts_rows": critical_false_contradicts}


def score_train(cases):
    rows = []
    unsound_eligible = 0
    correct = 0
    atom_total = 0
    atom_correct = 0
    for c in cases:
        r = engine.evaluate_case(c)
        got = r["verdict"]
        correct += got == c["rel"]
        rows.append({"case_id": c["case_id"], "expected": c["rel"], "got": got})
        for a in r["atoms"]:
            atom_total += 1
            atom_correct += a.get("relation", a["verdict"]) == c["rel"]
            if (a.get("relation", a["verdict"]) == "ENTAILS"
                    and c["rel"] != "ENTAILS"
                    and a.get("boundary", {}).get("overall")
                    == "BOUNDARY_COMPATIBLE"):
                unsound_eligible += 1
    return {"n": len(cases), "relation_correct": correct,
            "relation_accuracy": round(correct / len(cases), 4),
            "atom_relation_accuracy": round(atom_correct / atom_total, 4)
            if atom_total else None,
            "unsound_eligible_support_atoms": unsound_eligible,
            "rows": rows}


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "baseline-results.json"
    suite = json.load(open(os.path.join(HERE, "fresh-relation-cases.json"),
                           encoding="utf-8"))["cases"]
    train = json.load(open(os.path.join(PROOF_DIR, "corpus", "train-cases.json"),
                           encoding="utf-8"))["cases"]
    fresh = score_fresh(suite)
    train_res = score_train(train)
    result = {"provenance": provenance(), "fresh_suite": fresh,
              "burned_train": train_res}
    with open(os.path.join(HERE, out_path), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({"engine_sha256": result["provenance"]["engine_sha256"][:16],
                      "fresh": fresh["metrics"], "train": {
                          k: train_res[k] for k in
                          ("relation_accuracy", "atom_relation_accuracy",
                           "unsound_eligible_support_atoms")}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
