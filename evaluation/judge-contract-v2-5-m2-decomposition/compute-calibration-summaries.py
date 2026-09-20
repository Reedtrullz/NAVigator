#!/usr/bin/env python3
"""Offline V2.5 calibration summaries + error attribution (no model calls).

Recomputes spec-23 metrics with gold_state present on all rows; the runner's
first cut silently undercounted critical_fn because valid entries lacked the key.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
NECESSARY = {
    "clear_trigger": {"trigger_support": "PRESENT"},
    "clear_non_trigger": {"trigger_support": "ABSENT", "non_trigger_support": "PRESENT"},
    "ambiguous_conflicting": {"evidence_conflict": "YES"},
    "insufficient_to_decide": {"evidence_sufficiency": "INSUFFICIENT"},
}


def sha(p):
    return hashlib.sha256((HERE / p).read_bytes()).hexdigest()


def summarize(suffix):
    runs = json.loads((HERE / ("calibration-results-v2-5-iter%s.partial.json" % suffix)).read_text())["runs"]
    gold_doc = json.loads(
        (HERE.parent / "judge-deepseek-v2-4-m2-validation" / "calibration-gold.json").read_text())
    gold = {f["id"]: f for f in gold_doc["gold"] if f.get("dimension") == "critical_condition"}
    for r in runs:
        g = gold[r["id"]]
        r.setdefault("gold_state", g["gold_intermediate"]["critical_evidence_state"])
        r.setdefault("gold_verdict", g["gold_verdict"])
    scored = [r for r in runs if r["valid_result"]]
    n = 36
    field_rates = {}
    for tag, conds in NECESSARY.items():
        subset = [r for r in scored if r["tag"] == tag]
        for f, v in conds.items():
            field_rates[f] = round(sum(r["intermediate"][f] == v for r in subset) / len(subset), 4)
    critical_fn = sum(1 for r in scored
                      if r["gold_state"] in ("CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")
                      and not r["verdict_correct"])
    report = {
        "iteration": int(suffix),
        "n_fixtures": n,
        "valid_structured": len(scored),
        "valid_structured_rate": round(len(scored) / n, 4),
        "derived_final_accuracy": round(sum(r["derived_state_correct"] for r in scored) / n, 4),
        "derived_final_accuracy_over_valid": round(sum(r["derived_state_correct"] for r in scored) / len(scored), 4),
        "final_verdict_accuracy": round(sum(r["verdict_correct"] for r in scored) / n, 4),
        "field_reference_diagnostics": field_rates,
        "critical_fn": critical_fn,
        "critical_fn_note": "computed offline with gold_state on all rows; runner v1 undercounted because valid rows lacked the gold_state key",
        "error_breakdown": {"transport_or_schema": [r["id"] for r in runs if not r["valid_result"]]},
        "provenance": "computed offline from checkpoint partial file; no model calls",
    }
    (HERE / ("calibration-summary-v2-5-iter%s.json" % suffix)).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
    return report


ATTR = {
    "task_id": "NAV-EXPLORE-JUDGE-CONTRACT-V2_5-M2-EVIDENCE-STATE-DECOMPOSITION",
    "spec_section": "35",
    "iteration_0": {
        "total_misses": 18,
        "attribution": {
            "evidence_conflict": ["V24-CAL-M2A-02", "V24-CAL-M2A-03", "V24-CAL-M2A-04",
                                   "V24-CAL-M2A-05", "V24-CAL-M2A-08", "V24-CAL-M2A-09",
                                   "V24-CAL-M2A-10", "V24-CAL-M2A-13", "V24-CAL-M2A-15",
                                   "V24-CAL-M2A-16", "V24-CAL-M2A-18"],
            "evidence_sufficiency": ["V24-CAL-M2I-01", "V24-CAL-M2I-02", "V24-CAL-M2I-03",
                                      "V24-CAL-M2I-04", "V24-CAL-M2I-05", "V24-CAL-M2I-06"],
            "trigger_support": ["V24-CAL-M2N-01"],
            "non_trigger_support": ["V24-CAL-M2N-01"],
            "derivation_bug": [],
            "schema_or_transport": [],
        },
        "pattern": "model refuses uncertain observations: conflict=NO on competing-reading texts (11x); sufficiency=SUFFICIENT on on-topic-stanceless texts (6x); one negation-scope over-read (M2N-01 requirement-statement read as condition assertion, missed explicit exclusion)",
    },
    "iteration_1": {
        "total_misses_valid": 5,
        "schema_invalid": ["V24-CAL-M2A-02"],
        "attribution": {
            "evidence_conflict": ["V24-CAL-M2A-03", "V24-CAL-M2A-05", "V24-CAL-M2A-09", "V24-CAL-M2A-10"],
            "evidence_sufficiency": ["V24-CAL-M2N-01"],
            "non_trigger_support": ["V24-CAL-M2N-01"],
            "trigger_support": [],
            "derivation_bug": [],
            "schema_or_transport": ["V24-CAL-M2A-02 (HTTP 200; validator rejected non-verbatim evidence span; no label produced; transport observation only)"],
        },
        "pattern": "targeted clarifications fixed sufficiency (0/6 -> 6/6) and improved conflict (7/18 -> 13/17); residual conflict misses are mixed-signal texts the model still reads as clear exclusions; M2N-01 flipped from over-read PRESENT to overcorrection (INSUFFICIENT, missed explicit negation); M2A-02 span-validity failure",
        "critical_fn": 1,
        "critical_fn_case": "V24-CAL-M2N-01 (gold CLEAR_NON_TRIGGER_SUPPORT, derived INSUFFICIENT_TO_DECIDE)",
    },
}


def main():
    s0 = summarize("0")
    s1 = summarize("1")
    (HERE / "error-attribution.json").write_text(json.dumps(ATTR, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
    shas = {p: sha(p) for p in [
        "m2-decomposition-contract-v2-5.json", "m2_prompt_v2_5.py", "judge_m2_v2_5.py",
        "run_calibration_v2_5.py", "deterministic-derivation-table.json", "m2-decomposition.schema.json",
        "m2-fixtures-v2-5.json", "intermediate-field-contract.md",
        "calibration-results-v2-5-iter0.partial.json", "calibration-results-v2-5-iter1.partial.json",
        "error-attribution.json"]}
    (HERE / "calibration-artifact-shas.json").write_text(json.dumps(shas, indent=2) + chr(10), encoding="utf-8")
    print(json.dumps({"iter0": s0, "iter1": s1}, ensure_ascii=False, indent=1))
    print(json.dumps(shas, indent=1))


if __name__ == "__main__":
    main()
