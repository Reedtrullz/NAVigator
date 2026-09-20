#!/usr/bin/env python3
"""BURNED_DIAGNOSTIC_RETROSPECTIVE - spec section 43.

Mechanical re-run of the seven burned V2.1 miss rows through the frozen
V2.2 judge procedure. Runs only after official score freeze; non-scoring.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from judge_core_v2_2 import call_judge  # noqa: E402

BASE = HERE.parent
GOLD = BASE / "judge-selection-v2-subskill" / "judge-selection-gold.json"
FIXTURE_PATHS = [
    BASE / "judge-selection-v2-subskill" / "family-a-fixtures.json",
    BASE / "judge-selection-v2-subskill" / "family-c-fixtures.json",
]
SHARED = ["A-07", "A-13", "A-14", "A-18", "A-21", "A-23", "C-19"]
OUT = HERE / "burned-seven-retrospective.json"
GATE = HERE / "official-validation-results.json"


def main():
    if not GATE.exists():
        raise SystemExit("REFUSED: official score not frozen yet (spec section 43)")
    if OUT.exists():
        raise SystemExit("REFUSED: retrospective already frozen")

    gold = {g["fixture_id"]: g for g in json.loads(GOLD.read_text())["gold"]}
    fixtures = {}
    for path in FIXTURE_PATHS:
        for f in json.loads(path.read_text())["fixtures"]:
            fixtures[f["id"]] = f

    rows = []
    for fid in SHARED:
        fx = fixtures[fid]
        g = gold[fid]
        # Burned V2 screening fixtures carry no dimension field; the frozen
        # gold rows are the authority for dimension and verdict vocabulary.
        result, telemetry = call_judge(
            g["dimension"], fx["ctx"], fx["crit"], fx["sut"])
        row = {
            "id": fid,
            "dimension": g["dimension"],
            "gold_verdict": g["verdict"],
            "valid_result": result is not None,
            "v22_verdict": result["verdict"] if result else None,
            "v22_intermediate": result["intermediate"] if result else None,
            "v22_matches_gold": (result or {}).get("verdict") == g["verdict"],
            "telemetry": telemetry,
        }
        rows.append(row)
        print("%s valid=%s v22=%s gold=%s match=%s" % (
            fid, row["valid_result"], row["v22_verdict"],
            g["verdict"], row["v22_matches_gold"]), flush=True)

    artifact = {
        "artifact": "burned-seven-retrospective.json",
        "marker": "BURNED_DIAGNOSTIC_RETROSPECTIVE",
        "task_id": "NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION",
        "counted_in_pass": False,
        "rows": rows,
        "summary": {
            "n": len(rows),
            "valid": sum(r["valid_result"] for r in rows),
            "mechanism_repaired": sum(r["v22_matches_gold"] for r in rows),
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + chr(10))
    print("WROTE", OUT.name)


if __name__ == "__main__":
    main()
