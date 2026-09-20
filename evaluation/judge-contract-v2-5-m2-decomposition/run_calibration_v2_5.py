#!/usr/bin/env python3
"""V2.5 M2 DeepSeek calibration runner (spec sections 22-23).

Burned V2.4 calibration fixtures, M2 dimension rows only. One model call per
fixture per iteration, max 2 iterations. Checkpoint per row. No CoT, no
substantive reruns. Only authorized wire ID is used.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
V22 = HERE.parent / "judge-contract-v2-2-two-mechanism"
V24 = HERE.parent / "judge-deepseek-v2-4-m2-validation"
sys.path.insert(0, str(V22))
sys.path.insert(0, str(HERE))

import judge_core_v2_2 as jc  # noqa: E402
import judge_m2_v2_5 as m25  # noqa: E402
from m2_prompt_v2_5 import PROMPT_ITER0, PROMPT_ITER1  # noqa: E402


def _validate_v2_5(dimension, parsed, sut_answer):
    """Route parsing through the V2.5 validator; keep raw preview for attribution."""
    try:
        return m25.validate_result_v2_5(dimension, parsed, sut_answer)
    except ValueError as exc:
        preview = json.dumps(parsed, ensure_ascii=False)[:200] if parsed is not None else "None"
        raise ValueError(str(exc) + " | raw: " + preview) from exc


# call_judge resolves validate_result at call time from module globals; this
# auditable substitution is the only parser change (spec section 24 freeze item).
jc.validate_result = _validate_v2_5

FIXTURES = V24 / "calibration-fixtures.json"
NECESSARY = {
    "clear_trigger": [("trigger_support", "PRESENT")],
    "clear_non_trigger": [("trigger_support", "ABSENT"), ("non_trigger_support", "PRESENT")],
    "ambiguous_conflicting": [("evidence_conflict", "YES")],
    "insufficient_to_decide": [("evidence_sufficiency", "INSUFFICIENT")],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, required=True, choices=[0, 1])
    args = ap.parse_args()

    jc.MODEL = "opencode-go/deepseek-v4.1-flash"
    jc.DIMENSION_INSTRUCTIONS["critical_condition"] = PROMPT_ITER0 if args.iteration == 0 else PROMPT_ITER1

    fixtures = [x for x in json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
                if x["dimension"] == "critical_condition"]
    assert len(fixtures) == 36, len(fixtures)

    suffix = str(args.iteration)
    results_path = HERE / ("calibration-results-v2-5-iter%s.json" % suffix)
    partial_path = HERE / ("calibration-results-v2-5-iter%s.partial.json" % suffix)
    runs = []
    if partial_path.exists():
        runs = json.loads(partial_path.read_text(encoding="utf-8"))["runs"]
    done = {r["id"] for r in runs}

    for fixture in fixtures:
        if fixture["id"] in done:
            continue
        result, telemetry = jc.call_judge(
            fixture["dimension"], fixture["ctx"], fixture["crit"], fixture["sut"])
        entry = {"id": fixture["id"], "tag": fixture["tag"], "telemetry": telemetry}
        gold_state = fixture["gold_intermediate"]["critical_evidence_state"]
        gold_verdict = fixture["gold_verdict"]
        if result is None:
            entry["valid_result"] = False
            entry["gold_state"] = gold_state
            entry["gold_verdict"] = gold_verdict
        else:
            entry["valid_result"] = True
            entry["intermediate"] = result["intermediate"]
            entry["verdict"] = result["verdict"]
            entry["derived_state"] = result["derivation_basis"].split(":", 1)[1]
            entry["evidence_spans"] = result["evidence_spans"]
            entry["note"] = result["note"]
            entry["derived_state_correct"] = entry["derived_state"] == gold_state
            entry["verdict_correct"] = result["verdict"] == gold_verdict
            necessary = NECESSARY.get(fixture["tag"], [])
            entry["field_diagnostics"] = {
                f: result["intermediate"][f] == v for f, v in necessary}
        runs.append(entry)
        partial_path.write_text(json.dumps(
            {"iteration": args.iteration, "runs": runs}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    scored = [r for r in runs if r["valid_result"]]
    for r in runs:
        r.setdefault("gold_state", "UNKNOWN")
    n = len(fixtures)
    def rate(key):
        return round(sum(r[key] for r in scored) / n, 4) if scored else 0.0
    field_rates = {}
    for tag, conds in NECESSARY.items():
        subset = [r for r in scored if r["tag"] == tag]
        for f, _ in conds:
            field_rates.setdefault(f, []).extend(r["field_diagnostics"][f] for r in subset)
    report = {
        "iteration": args.iteration,
        "n_fixtures": n,
        "valid_structured": len(scored),
        "valid_structured_rate": round(len(scored) / n, 4),
        "derived_final_accuracy": rate("derived_state_correct"),
        "final_verdict_accuracy": rate("verdict_correct"),
        "field_reference_diagnostics": {
            f: round(sum(v) / len(v), 4) if v else None for f, v in sorted(field_rates.items())},
        "critical_fn": sum(
            1 for r in scored if r["gold_state"] in ("CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")
            and r["verdict_correct"] is False),
        "error_breakdown": {
            "transport_or_schema": [r["id"] for r in runs if not r["valid_result"]],
        },
    }
    (HERE / ("calibration-summary-v2-5-iter%s.json" % suffix)).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "error_breakdown"}, indent=1))


if __name__ == "__main__":
    main()
