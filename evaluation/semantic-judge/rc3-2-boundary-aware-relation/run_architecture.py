"""Baseline harness for RC3.2 boundary-aware relation recovery.

Scores the fresh architecture suite at atom level (relation) and at
dimension level (rich states vs expected_dims). Also reports the
BOUNDARY_INFORMATION_COLLAPSE_RATE diagnostic (spec section 27) and runs
the burned TRAIN suite as diagnostics. Provenance is logged; no case-ID
logic, no expected-label maps.
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
from rc3_1_engine import boundary  # noqa: E402


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def provenance():
    return {
        "python": platform.python_version(),
        "engine_sha256": sha256_file(
            os.path.join(PROOF_DIR, "rc3_1_engine", "engine.py")),
        "boundary_sha256": sha256_file(
            os.path.join(PROOF_DIR, "rc3_1_engine", "boundary.py")),
        "suite_sha256": sha256_file(
            os.path.join(HERE, "fresh-architecture-cases.json")),
        "contract_sha256": sha256_file(
            os.path.join(HERE, "dimension-evidence-contract-v1.md")),
        "schema_sha256": sha256_file(
            os.path.join(HERE, "dimension-evidence-schema-v1.json")),
        "metrics_sha256": sha256_file(
            os.path.join(HERE, "relation-recovery-metrics-v1.json")),
    }


def atom_decisions(suite):
    for c in suite:
        if c.get("compound") and c.get("expected_atoms"):
            r = engine.evaluate_case(c)
            for i, a in enumerate(r["atoms"]):
                exp = (c["expected_atoms"][i] if i < len(c["expected_atoms"])
                       else c["rel"])
                got = a.get("relation", a["verdict"])
                yield c, i, exp, got, a
        else:
            r = engine.evaluate_atom(c["claim"], c["evidence"])
            yield c, 0, c["rel"], r.get("relation", r["verdict"]), r


def score_relation(suite):
    conf = collections.Counter()
    critical_false_entails = []
    critical_false_contradicts = []
    errors = []
    group_hit = collections.Counter()
    group_total = collections.Counter()
    for c, ai, exp, got, atom_r in atom_decisions(suite):
        conf[(exp, got)] += 1
        group_total[c["group"]] += 1
        if exp == got:
            group_hit[c["group"]] += 1
        else:
            errors.append({
                "case_id": c["case_id"], "atom": ai + 1,
                "expected": exp, "got": got,
                "rule": atom_r.get("rule"),
                "boundary_overall": (atom_r.get("boundary") or {}).get("overall"),
                "group": c["group"],
                "critical": c.get("critical", False),
            })
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
        "confusion_matrix": {f"{e}->{g}": v
                             for (e, g), v in sorted(conf.items())},
    }
    return {"metrics": metrics, "errors": errors,
            "critical_false_entails_rows": critical_false_entails,
            "critical_false_contradicts_rows": critical_false_contradicts}


def score_dimensions(suite):
    """Score gold expected_dims against what the current 3-state boundary
    layer can express. The current layer is collapsed (MATCH/MISMATCH/
    UNKNOWN); rich-state scoring is only possible after the pass. Here we
    record per-dimension gold distributions and which errors co-occur with
    dimension conflicts, as the pre-pass baseline."""
    dim_gold = collections.Counter()
    errors_with_conflict_dims = 0
    rel_errors = 0
    CONFLICT_STATES = {"EXPLICIT_CONFLICT", "DEONTIC_OPPOSITION",
                       "CONDITION_MISSING", "EXCEPTION_CONFLICT",
                       "DIFFERENT_ACTOR", "SCOPE_CONFLICT",
                       "TEMPORAL_CONFLICT", "NUMERIC_CONFLICT"}
    for c in suite:
        for k, v in (c.get("expected_dims") or {}).items():
            dim_gold[(k, v)] += 1
    for c, ai, exp, got, atom_r in atom_decisions(suite):
        if exp != got:
            rel_errors += 1
            gold_dims = c.get("expected_dims") or {}
            if any(v in CONFLICT_STATES for v in gold_dims.values()):
                errors_with_conflict_dims += 1
    return {
        "gold_dimension_state_distribution": {
            f"{k}|{v}": n for (k, v), n in sorted(dim_gold.items())},
        "relation_errors_total": rel_errors,
        "relation_errors_with_gold_conflict_dim": errors_with_conflict_dims,
    }


def collapse_rate(suite):
    """Spec section 27: group relation errors by (overall,
    blocking_dimensions); groups with >=2 distinct gold dimension patterns
    count toward BOUNDARY_INFORMATION_COLLAPSE_RATE (diagnostic only)."""
    groups = collections.defaultdict(set)
    total_errors = 0
    for c, ai, exp, got, atom_r in atom_decisions(suite):
        if exp == got:
            continue
        total_errors += 1
        b = atom_r.get("boundary") or {}
        key = (b.get("overall"), tuple(b.get("blocking_dimensions") or []))
        gold_sig = tuple(sorted((c.get("expected_dims") or {}).items()))
        groups[key].add(gold_sig)
    collapsed_groups = sum(1 for s in groups.values() if len(s) >= 2)
    return {
        "relation_errors": total_errors,
        "error_groups": len(groups),
        "collapsed_groups": collapsed_groups,
        "BOUNDARY_INFORMATION_COLLAPSE_RATE": round(
            collapsed_groups / total_errors, 4) if total_errors else 0.0,
    }


def score_train(cases):
    rows = []
    correct = 0
    atom_total = 0
    atom_correct = 0
    for c in cases:
        r = engine.evaluate_case(c)
        got = r["verdict"]
        correct += got == c["rel"]
        rows.append({"case_id": c["case_id"], "expected": c["rel"],
                     "got": got})
        for a in r["atoms"]:
            atom_total += 1
            atom_correct += a.get("relation", a["verdict"]) == c["rel"]
    return {"n": len(cases), "relation_correct": correct,
            "relation_accuracy": round(correct / len(cases), 4),
            "atom_relation_accuracy": round(atom_correct / atom_total, 4)
            if atom_total else None,
            "rows": rows}


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "baseline-results.json"
    suite = json.load(open(os.path.join(HERE, "fresh-architecture-cases.json"),
                           encoding="utf-8"))["cases"]
    train = json.load(open(os.path.join(PROOF_DIR, "corpus", "train-cases.json"),
                           encoding="utf-8"))["cases"]
    fresh = score_relation(suite)
    dims = score_dimensions(suite)
    collapse = collapse_rate(suite)
    train_res = score_train(train)
    result = {
        "provenance": provenance(),
        "fresh_suite": fresh,
        "dimension_baseline": dims,
        "collapse_diagnostic": collapse,
        "burned_train": train_res,
    }
    with open(os.path.join(HERE, out_path), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({
        "engine": result["provenance"]["engine_sha256"][:16],
        "fresh": fresh["metrics"],
        "collapse": collapse,
        "train": {k: train_res[k] for k in
                  ("relation_accuracy", "atom_relation_accuracy")},
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
