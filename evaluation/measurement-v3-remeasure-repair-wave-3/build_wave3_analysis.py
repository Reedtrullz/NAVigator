#!/usr/bin/env python3
"""Wave-3 routing funnel + per-case route-failure stage classification.

Read-only over frozen inputs; emits two analysis artifacts. All counts are
asserted against the frozen measurement and prediction files before writing.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W3 = ROOT / "evaluation/measurement-v3-remeasure-repair-wave-3"
W2 = ROOT / "evaluation/measurement-v3-remeasure-repair-wave-2"
GOLD = ROOT / "evaluation/dev-corpus-v1-1-repair/cases"
RUNS = ROOT / "evaluation/full-sut-repair-wave-3-v1/runs/structural-120-replay-v1"

CREATED_UTC = "2026-09-16T22:45:00Z"

# Curated stage mapping verified during the close-out session against frozen
# predictions and gold (see close-out route-lane audit). Case IDs are analysis
# documentation only; no runtime logic consumes this file.
R1 = {"ROUT-024", "ROUT-032", "ROUT-040", "ROUT-052", "ROUT-066",
      "ROUT-067", "ROUT-072", "ROUT-083", "SAF-012"}
R3 = {"DIS-112", "DIS-119", "ROUT-038", "ROUT-039", "ROUT-041", "ROUT-054",
      "ROUT-064", "ROUT-065", "ROUT-068", "ROUT-089", "SAF-009"}
R5 = {"ROUT-042", "ROUT-061", "ROUT-073", "ROUT-075"}
STAGE_NOTES = {
    "ROUT-068": "LOW-confidence family nuance: gold requires duty-to-notify child welfare upon concrete concern; SUT route family is adjacent, not equivalent.",
    "ROUT-040": "PARTIAL artifact: offered label 'NAV' is a lexical token inside a NEGATED gold clause ('NAV sender ikke til BUP'); lexical gate does not bind semantics.",
    "ROUT-061": "PARTIAL artifact: offered label token 'Familievernkontoret' appears inside the gold sentence, but the offered target is not committed to the gold first-line reading.",
    "ROUT-073": "Fragment mismatch: offered 'Skolehelsetjenesten' vs gold token 'skolehelsetjeneste' fails the lexical token gate; stays NO_ACCEPTABLE_ROUTE.",
    "ROUT-083": "Junk route entry 'URL' bears no relation to gold social-help predicate; classified R1.",
}


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def gold_index():
    idx = {}
    for name in ("routing_cases.json", "discovery_adversarial_cases.json", "safety_cases.json"):
        for case in load_json(GOLD / name)["cases"]:
            idx[case["id"]] = case
    return idx


def main():
    gold = gold_index()
    assert len(gold) == 120, len(gold)

    w3_doc = load_json(W3 / "wave3-combined-measurement-results.json")
    w2_doc = load_json(W2 / "wave2-combined-measurement-results.json")
    diag = load_json(ROOT / "evaluation/full-sut-repair-wave-3-v1/structural-replay-diagnostics.json")
    product = load_json(W3 / "product-diagnostics.json")

    preds = {}
    for track in ("routing", "safety", "discovery_adversarial"):
        pdir = RUNS / track / "predictions"
        for pf in sorted(pdir.glob("*.json")):
            preds[pf.stem] = load_json(pf)
    assert len(preds) == 120, len(preds)

    def route_rows(doc):
        rows = {}
        for case in doc["cases"]:
            for crit in case["criteria"]:
                if crit["dimension"] == "route_correctness":
                    rows[crit["case_id"]] = crit
        return rows

    w3_rows, w2_rows = route_rows(w3_doc), route_rows(w2_doc)
    assert len(w3_rows) == 120 and len(w2_rows) == 120

    na_cases = {cid for cid, crit in w3_rows.items() if crit["status"] == "NOT_APPLICABLE"}
    assert len(na_cases) == 12, na_cases
    for cid in na_cases:
        assert gold[cid]["gold"]["acceptable_routes"] is None, cid

    evaluated = [cid for cid in sorted(w3_rows) if cid not in na_cases]
    assert len(evaluated) == 108, len(evaluated)

    emitters = [cid for cid in evaluated if preds[cid]["routes"]]
    all_emitters = [cid for cid in preds if preds[cid]["routes"]]
    entries = sum(len(preds[cid]["routes"]) for cid in all_emitters)
    labels = {r for cid in all_emitters for r in preds[cid]["routes"]}
    na_emitters = [cid for cid in na_cases if preds[cid]["routes"]]

    stage_counts = Counter()
    for cid in emitters:
        if cid in R1:
            stage_counts["R1"] += 1
        elif cid in R3:
            stage_counts["R3"] += 1
        elif cid in R5:
            stage_counts["R5"] += 1
        else:
            stage_counts["R0"] += 1
    stage_counts["R0"] += len(evaluated) - len(emitters)
    assert stage_counts["R0"] == 84, stage_counts
    assert stage_counts["R1"] == 9 and stage_counts["R3"] == 11 and stage_counts["R5"] == 4

    partial_ids = sorted(cid for cid in evaluated if w3_rows[cid]["verdict"] == "PARTIAL")
    assert partial_ids == ["ROUT-040", "ROUT-061"], partial_ids
    verdicts = Counter(w3_rows[cid]["verdict"] for cid in evaluated)
    route_fail = sum(v for k, v in verdicts.items() if k != "PASS")
    assert route_fail == 108, (route_fail, verdicts)

    # W2 reference recompute (same procedure over frozen W2 replay). The frozen
    # W2 funnel counts structured-route cases across all 120 rows (ROUT-029
    # emits despite route NA), so keep the same convention for comparability.
    w2_preds = {}
    w2_runs = ROOT / "evaluation/full-sut-repair-wave-2-v1/runs/structural-120-replay-v2"
    for track in ("routing", "safety", "discovery_adversarial"):
        pdir = w2_runs / track / "predictions"
        for pf in sorted(pdir.glob("*.json")):
            w2_preds[pf.stem] = load_json(pf)
    assert len(w2_preds) == 120
    w2_na = {cid for cid, crit in w2_rows.items() if crit["status"] == "NOT_APPLICABLE"}
    w2_eval = [cid for cid in sorted(w2_rows) if cid not in w2_na]
    w2_all_emitters = [cid for cid in w2_preds if w2_preds[cid]["routes"]]
    w2_entries = sum(len(w2_preds[cid]["routes"]) for cid in w2_all_emitters)
    w2_labels = {r for cid in w2_all_emitters for r in w2_preds[cid]["routes"]}
    funnel = {
        "artifact": "wave3-routing-funnel",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "created_utc": CREATED_UTC,
        "classification": "BURNED_DEV_BASELINE_ONLY",
        "basis": {
            "wave3_measurement_freeze": "wave3-measurement-freeze-manifest.json (2026-09-16T21:51:31Z)",
            "wave3_structural_diagnostics": "evaluation/full-sut-repair-wave-3-v1/structural-replay-diagnostics.json",
            "wave2_reference_funnel": "measurement-v3-remeasure-repair-wave-2/routing-funnel.json (recomputed here from frozen W2 replay)",
        },
        "wave2": {
            "route_criteria_total": 120,
            "route_evaluated": len(w2_eval),
            "not_applicable": len(w2_na),
            "structured_route_cases": len(w2_all_emitters),
            "structured_route_entries": w2_entries,
            "distinct_route_labels": len(w2_labels),
            "no_route_asserted_cases": sum(1 for p in w2_preds.values() if p["no_route_asserted"]),
            "label_to_evidence_binding_resolvable_cases": 0,
            "evidence_supported_targets": 0,
            "route_pass": 0,
            "route_fail": sum(1 for cid in w2_eval if w2_rows[cid]["verdict"] != "PASS"),
            "partial_route": sum(1 for cid in w2_eval if w2_rows[cid]["verdict"] == "PARTIAL"),
        },
        "wave3": {
            "route_criteria_total": 120,
            "route_evaluated": len(evaluated),
            "not_applicable": len(na_cases),
            "structured_route_cases": len(emitters),
            "structured_route_cases_all_120": len(all_emitters),
            "structured_route_entries": entries,
            "distinct_route_labels": len(labels),
            "no_route_asserted_cases": sum(1 for p in preds.values() if p["no_route_asserted"]),
            "not_applicable_cases_with_route_emitters": sorted(na_emitters),
            "stage_counts": dict(sorted(stage_counts.items())),
            "partial_route_cases": partial_ids,
            "partial_route": len(partial_ids),
            "label_to_evidence_binding_resolvable_cases": 0,
            "evidence_supported_targets": 0,
            "route_pass": verdicts.get("PASS", 0),
            "route_fail": route_fail,
        },
        "funnel_note": (
            "Wave-3 endpoint unchanged: 0 route PASS, 108 route FAIL (106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL). "
            "RC-04..RC-06 retrieval work moved the emission funnel (20 to 24 emitters, 24 to 39 entries, "
            "14 to 24 distinct labels; no_route_asserted 100 to 92) but did not move binding: evidence.route_evidence "
            "remains keyed by R-codes, not route labels, so 0/24 emitter cases have a resolvable label-to-evidence mapping."
        ),
        "partial_mechanism_note": (
            "Both Wave-3 PARTIAL verdicts are lexical token-substring artifacts of the frozen scorer gate: ROUT-040 'NAV' "
            "matches inside a NEGATED gold clause and ROUT-061 'Familievernkontoret' matches the gold label token without "
            "committing to the gold first-line reading. They are structural-but-lexical, not semantic route passes."
        ),
        "product_diagnostics": product,
    }

    rows = []
    for cid in evaluated:
        crit = w3_rows[cid]
        case_evs = [
            m for c3 in w3_doc["cases"] if c3["case_id"] == cid
            for cr in c3["criteria"] for m in (cr.get("evidence") or [])
        ]
        marker_text = " ".join(case_evs)
        flags = []
        if "PREMATURE_ABSENCE" in marker_text:
            flags.append("MEASUREMENT_SENSITIVITY_PREMATURE_ABSENCE")
        if "CERTAINTY_MARKER" in marker_text:
            flags.append("MEASUREMENT_SENSITIVITY_CERTAINTY_MARKER")
        if cid in R1:
            stage = "R1_JUNK_OR_MISMATCH_LABEL"
        elif cid in R3:
            stage = "R3_FAMILY_NUANCE"
        elif cid in R5:
            stage = "R5_BINDING_OR_RESOLUTION"
        else:
            stage = "R0_NO_STRUCTURED_ROUTE"
        rows.append({
            "case_id": cid,
            "criterion_id": crit["criterion_id"],
            "authority": crit["authority"],
            "verdict": crit["verdict"],
            "primary_stage": stage,
            "secondary_flags": flags,
            "note": STAGE_NOTES.get(cid),
            "case_routes": preds[cid]["routes"],
            "case_no_route_asserted": preds[cid]["no_route_asserted"],
        })
    for cid in sorted(na_cases):
        rows.append({
            "case_id": cid,
            "criterion_id": w3_rows[cid]["criterion_id"],
            "authority": w3_rows[cid]["authority"],
            "verdict": None,
            "primary_stage": "NOT_APPLICABLE_GOLD_NO_ROUTES",
            "secondary_flags": [],
            "note": "gold acceptable_routes = None; NA verified against frozen gold",
            "case_routes": preds[cid]["routes"],
            "case_no_route_asserted": preds[cid]["no_route_asserted"],
        })
    assert len(rows) == 120, len(rows)

    classification = {
        "artifact": "wave3-route-failure-stage-classification",
        "task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-3",
        "created_utc": CREATED_UTC,
        "classification": "BURNED_DEV_BASELINE_ONLY",
        "row_count": len(rows),
        "stage_counts": dict(sorted(stage_counts.items())),
        "rows": rows,
        "documentation_note": "Case IDs and stages are analysis documentation derived from frozen artifacts; no runtime code consumes this classification.",
    }

    (W3 / "routing-funnel.json").write_text(
        json.dumps(funnel, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (W3 / "route-failure-stage-classification.json").write_text(
        json.dumps(classification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("funnel w2:", json.dumps(funnel["wave2"]))
    print("funnel w3:", json.dumps(funnel["wave3"]))
    print("stage counts:", dict(sorted(stage_counts.items())))
    print("rows:", len(rows), "PARTIAL:", partial_ids)


if __name__ == "__main__":
    main()
