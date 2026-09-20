#!/usr/bin/env python3
"""V2.4 DeepSeek calibration runner (60 fixtures, checkpoint per row).

Imports the frozen V2.2 judge core and the frozen official score() verbatim.
Applies only the authorized model swap (opencode-go/deepseek-v4.1-flash) and
the frozen empty-delta prompt mechanism from prompt_deltas_v2_4.py.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
V22 = HERE.parent / "judge-contract-v2-2-two-mechanism"
sys.path.insert(0, str(V22))
sys.path.insert(0, str(HERE))

import judge_core_v2_2  # noqa: E402
import run_official_v2_2  # noqa: E402
from judge_core_v2_2 import call_judge, prompt_hash  # noqa: E402
from prompt_deltas_v2_4 import deltas_for  # noqa: E402

FIXTURES = HERE / "calibration-fixtures.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, required=True, choices=[0, 1, 2])
    args = ap.parse_args()

    sys_delta, dim_deltas = deltas_for(args.iteration)
    for dim, delta in dim_deltas.items():
        if dim not in judge_core_v2_2.DIMENSION_INSTRUCTIONS:
            raise SystemExit("unknown dimension in deltas: " + dim)

    judge_core_v2_2.MODEL = "opencode-go/deepseek-v4.1-flash"
    judge_core_v2_2.SYSTEM_PROMPT = judge_core_v2_2.SYSTEM_PROMPT + sys_delta
    for dim, delta in dim_deltas.items():
        judge_core_v2_2.DIMENSION_INSTRUCTIONS[dim] = (
            judge_core_v2_2.DIMENSION_INSTRUCTIONS[dim] + delta)

    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = data["fixtures"]
    if len(fixtures) != 60:
        raise SystemExit("expected 60 fixtures, got %d" % len(fixtures))

    results_path = HERE / ("calibration-results-iter%d.json" % args.iteration)
    partial_path = results_path.with_suffix(".partial.json")
    existing = []
    if partial_path.exists():
        existing = json.loads(partial_path.read_text(encoding="utf-8"))["runs"]
    done_ids = {r["id"] for r in existing}

    runs = list(existing)
    total = len(fixtures)
    for i, fixture in enumerate(fixtures, 1):
        if fixture["id"] in done_ids:
            continue
        result, telemetry = call_judge(
            fixture["dimension"], fixture["ctx"], fixture["crit"], fixture["sut"])
        entry = {
            "id": fixture["id"],
            "family": fixture["family"],
            "tag": fixture["tag"],
            "gold_intermediate": fixture["gold_intermediate"],
            "gold_verdict": fixture["gold_verdict"],
            "telemetry": telemetry,
        }
        if result is not None:
            entry["valid_result"] = True
            entry["intermediate"] = result["intermediate"]
            entry["verdict"] = result["verdict"]
            entry["derivation_basis"] = result["derivation_basis"]
            entry["evidence_spans"] = result["evidence_spans"]
            entry["note"] = result["note"]
            entry["intermediate_match"] = (
                result["intermediate"] == fixture["gold_intermediate"])
            entry["verdict_correct"] = result["verdict"] == fixture["gold_verdict"]
        else:
            entry["valid_result"] = False
            entry["verdict_correct"] = False
        runs.append(entry)
        partial_path.write_text(
            json.dumps({"runs": runs}, ensure_ascii=False), encoding="utf-8")
        print("%d/%d %s ok=%s" % (i, total, entry["id"], entry["valid_result"]),
              flush=True)

    summary = run_official_v2_2.score(runs, fixtures)
    out = {
        "artifact": results_path.name,
        "task_id": "NAV-EXPLORE-JUDGE-DEEPSEEK-V2_4-M2-CALIBRATION-FRESH-VALIDATION",
        "iteration": args.iteration,
        "model": judge_core_v2_2.MODEL,
        "prompt_sha": prompt_hash(),
        "fixtures_file": FIXTURES.name,
        "fixture_count": total,
        "summary": summary,
        "runs": runs,
    }
    results_path.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "overall", "by_family", "valid_structured_rate", "derivation_consistency")},
        indent=2))


if __name__ == "__main__":
    main()
