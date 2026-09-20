"""Gold-blind structural replay diagnostics (Wave 4, spec section 22).

Mechanical counts over the frozen 120-case replay predictions. No gold,
no Measurement V3 scoring, no expected verdicts. Determinism check: the
discovery_adversarial family is re-executed into a second directory and
predictions are compared modulo executed_at.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "runtime"))
sys.path.insert(0, os.path.join(REPO_ROOT, "evaluation", "full-sut-implementation-phase3"))

from sut.schemas import SchemaError, validate_output  # noqa: E402

LINEAGE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(LINEAGE, "runs", "structural-120-replay-v1")

SENTENCE_STARTERS = ("ikke ", "kan ", "skal ", "er ", "har ", "blir ",
                     "motta ", "foreldreansvar ", "akutt ")
SERVICE_ACRONYMS = ("NAV",)
JUNK_DIGITS = any


def is_fragment_like(label):
    t = label.strip()
    if t.upper() in SERVICE_ACRONYMS:
        return False
    if len(t) < 4 or not any(ch.isalnum() for ch in t):
        return True
    if t.startswith(("#", "|", "**")) or "|" in t or "**" in t or "\n" in t:
        return True
    low = t.lower()
    if low.startswith(SENTENCE_STARTERS) or low.endswith((".", "!", "?")):
        return True
    return False


def is_junk_label(label):
    # ponytail: heuristic, not clause parsing; digits are only junk when they
    # dominate the label. Legal/paragraph references are legitimate names.
    digits = sum(1 for ch in label if ch.isdigit())
    letters = sum(1 for ch in label if ch.isalpha())
    return letters > 0 and digits >= letters


def load_predictions():
    preds = []
    for family in ("routing_cases", "safety_cases", "discovery_adversarial_cases"):
        for path in sorted(glob.glob(os.path.join(RUNS, family, "predictions", "*.json"))):
            with open(path, encoding="utf-8") as fh:
                preds.append((family, os.path.basename(path)[:-5], json.load(fh)))
    return preds


def diag_one(out):
    d = {
        "schema_valid": True,
        "routes": len(out.get("routes", [])),
        "structured_routes": len(out.get("evidence", {}).get("structured_routes", [])),
        "actionable_targets": 0,
        "track_binding_missing": 0,
        "evidence_join_missing": 0,
        "access_binding_missing": 0,
        "condition_binding_missing": 0,
        "no_route_consistent": True,
        "rendering_fidelity": True,
        "fragment_labels": 0,
        "junk_labels": 0,
        "label_fragment_samples": [],
    }
    try:
        validate_output(out)
    except SchemaError:
        d["schema_valid"] = False
    structured = out.get("evidence", {}).get("structured_routes", [])
    for r in structured:
        if r.get("route_state") in ("EVALUABLE", "PARTIAL", "ACCESS_PARTIAL", "EXISTENCE_ONLY"):
            d["actionable_targets"] += 1
        if not r.get("track_domain"):
            d["track_binding_missing"] += 1
        if not r.get("evidence_refs"):
            d["evidence_join_missing"] += 1
        if not r.get("access_model"):
            d["access_binding_missing"] += 1
        if not r.get("dims"):
            d["condition_binding_missing"] += 1
    if out.get("no_route_asserted") != (len(out.get("routes", [])) == 0):
        d["no_route_consistent"] = False
    labels = out.get("routes", [])
    if labels != [r.get("display_label") for r in structured]:
        d["rendering_fidelity"] = False
    for lab in labels:
        if is_fragment_like(lab):
            d["fragment_labels"] += 1
            if len(d["label_fragment_samples"]) < 3:
                d["label_fragment_samples"].append(lab[:60])
        if is_junk_label(lab):
            d["junk_labels"] += 1
    return d


def main():
    preds = load_predictions()
    by_family = {}
    for family, case_id, out in preds:
        by_family.setdefault(family, []).append((case_id, diag_one(out)))

    summary = {}
    for family, items in sorted(by_family.items()):
        agg = {
            "executions": len(items),
            "schema_valid": sum(1 for _, d in items if d["schema_valid"]),
            "cases_with_routes": sum(1 for _, d in items if d["routes"] > 0),
            "total_routes": sum(d["routes"] for _, d in items),
            "total_structured_routes": sum(d["structured_routes"] for _, d in items),
            "total_actionable_targets": sum(d["actionable_targets"] for _, d in items),
            "track_binding_missing": sum(d["track_binding_missing"] for _, d in items),
            "evidence_join_missing": sum(d["evidence_join_missing"] for _, d in items),
            "access_binding_missing": sum(d["access_binding_missing"] for _, d in items),
            "condition_binding_missing": sum(d["condition_binding_missing"] for _, d in items),
            "no_route_inconsistent": sum(1 for _, d in items if not d["no_route_consistent"]),
            "rendering_fidelity_violations": sum(1 for _, d in items if not d["rendering_fidelity"]),
            "fragment_labels": sum(d["fragment_labels"] for _, d in items),
            "junk_labels": sum(d["junk_labels"] for _, d in items),
        }
        samples = sorted({s for _, d in items for s in d["label_fragment_samples"]})
        if samples:
            agg["fragment_label_samples"] = samples[:6]
        summary[family] = agg

    total = {
        "executions": sum(v["executions"] for v in summary.values()),
        "schema_valid": sum(v["schema_valid"] for v in summary.values()),
        "total_routes": sum(v["total_routes"] for v in summary.values()),
        "total_structured_routes": sum(v["total_structured_routes"] for v in summary.values()),
        "total_actionable_targets": sum(v["total_actionable_targets"] for v in summary.values()),
        "fragment_labels": sum(v["fragment_labels"] for v in summary.values()),
        "junk_labels": sum(v["junk_labels"] for v in summary.values()),
    }

    # Determinism: re-run discovery family once, compare modulo timestamps.
    det_dir = os.path.join(LINEAGE, "runs", "determinism-check-v1")
    env = {**os.environ, "PYTHONPATH": os.path.join(
        REPO_ROOT, "evaluation", "full-sut-implementation-phase3")}
    subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "evaluation",
         "full-sut-implementation-phase3", "sut_runner", "run.py"),
         "--corpus", "evaluation/dev-corpus-v1/cases/discovery_adversarial_cases.json",
         "--out", det_dir, "--mode", "replay"],
        check=True, capture_output=True, env=env, cwd=REPO_ROOT)
    base = sorted(glob.glob(os.path.join(RUNS, "discovery_adversarial_cases", "predictions", "*.json")))
    second = sorted(glob.glob(os.path.join(det_dir, "predictions", "*.json")))
    diffs = 0
    for a, b in zip(base, second):
        da = json.load(open(a, encoding="utf-8"))
        db = json.load(open(b, encoding="utf-8"))
        da.pop("executed_at", None)
        db.pop("executed_at", None)
        if json.dumps(da, sort_keys=True) != json.dumps(db, sort_keys=True):
            diffs += 1
    determinism = {
        "method": "discovery_adversarial re-executed; predictions compared modulo executed_at",
        "pairs_compared": len(base),
        "differing": diffs,
        "deterministic": len(base) == len(second) and diffs == 0,
    }

    result = {"families": summary, "totals": total, "determinism": determinism}
    out_path = os.path.join(LINEAGE, "product-structural-replay-results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
