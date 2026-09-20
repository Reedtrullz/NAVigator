#!/usr/bin/env python3
"""V2.2 calibration runner: 48 fresh fixtures, one call each, MiMo v2.5 Pro.

Scores final verdicts against fixture gold and writes calibration-results.json.
No fixture edits; no retry beyond the frozen technical policy in the core.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from judge_core_v2_2 import call_judge, prompt_hash  # noqa: E402

HERE = Path(__file__).parent
FIXTURES = HERE / "calibration-fixtures.json"
RESULTS = HERE / "calibration-results.json"


def score(results, fixtures):
    by_family = {}
    valid = 0
    for fixture, call in zip(fixtures, results):
        family = fixture["family"]
        bucket = by_family.setdefault(family, {"n": 0, "correct": 0})
        bucket["n"] += 1
        if call.get("valid_result"):
            valid += 1
            if call["verdict"] == fixture["gold_verdict"]:
                bucket["correct"] += 1
    accs = {}
    total_n = sum(b["n"] for b in by_family.values())
    total_c = sum(b["correct"] for b in by_family.values())
    for fam, bucket in sorted(by_family.items()):
        accs[fam] = round(bucket["correct"] / bucket["n"], 4) if bucket["n"] else None
    overall = round(total_c / total_n, 4) if total_n else None
    return {
        "overall": {"n": total_n, "correct": total_c, "accuracy": overall},
        "by_family": accs,
        "valid_structured_rate": round(valid / total_n, 4) if total_n else None,
    }


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = data["fixtures"]
    if len(fixtures) != 48:
        raise SystemExit("expected 48 fixtures, got %d" % len(fixtures))
    runs = []
    results_path = RESULTS
    out_path = results_path.with_suffix(".partial.json")
    for i, fixture in enumerate(fixtures, 1):
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
            entry["intermediate_match"] = result["intermediate"] == fixture["gold_intermediate"]
            entry["verdict_correct"] = result["verdict"] == fixture["gold_verdict"]
        else:
            entry["valid_result"] = False
            entry["verdict_correct"] = False
        runs.append(entry)
        out_path.write_text(json.dumps({"runs": runs}, ensure_ascii=False), encoding="utf-8")
        print("%d/48 %s ok=%s" % (i, entry["id"], entry["valid_result"]), flush=True)
    summary = score(runs, fixtures)
    out = {
        "artifact": "calibration-results.json",
        "task_id": "NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION",
        "prompt_sha": prompt_hash(),
        "fixtures_file": FIXTURES.name,
        "fixture_count": len(fixtures),
        "summary": summary,
        "runs": runs,
    }
    RESULTS.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
