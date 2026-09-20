#!/usr/bin/env python3
"""Kalibreringskjoering for semantic judge V1. Settet blir burned etter kjoering."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantic_judge as sj


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "calibration-fixtures.json"), encoding="utf-8") as f:
        doc = json.load(f)

    rows = []
    for fx in doc["fixtures"]:
        res = sj.semantic_verdict(
            fx["dimension"], fx["case_context"], fx["gold_criterion"], fx["sut_answer"])
        verdict = res["verdict"]
        rows.append({
            "id": fx["id"],
            "dimension": fx["dimension"],
            "expected": fx["expected_verdict"],
            "actual": verdict,
            "match": verdict == fx["expected_verdict"],
            "evidence_spans": res.get("evidence_spans", []),
            "note": res.get("note"),
            "ok": res.get("meta", {}).get("ok"),
        })
        print(f"{fx['id']}: {verdict} (expected {fx['expected_verdict']}) "
              f"{'OK' if verdict == fx['expected_verdict'] else 'MISMATCH'}")

    by_dim = {}
    for r in rows:
        d = by_dim.setdefault(r["dimension"], {"n": 0, "match": 0})
        d["n"] += 1
        d["match"] += r["match"]
    summary = {
        "status": "BURNED",
        "prompt_sha_prefix": sj.prompt_hash()[:16],
        "total": len(rows),
        "matches": sum(r["match"] for r in rows),
        "by_dimension": by_dim,
        "rows": rows,
    }
    out = os.path.join(here, "calibration-results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"matches: {summary['matches']}/{summary['total']}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
