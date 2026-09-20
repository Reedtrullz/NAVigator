#!/usr/bin/env python3
"""V1.6A.2 TDD runner for fresh clause-grounding dev fixtures."""
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).parent

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="RED", choices=["RED", "GREEN"])
    args = ap.parse_args()
    fixtures = json.loads((HERE / "tdd-fixtures.json").read_text())["fixtures"]
    from boundary_preclassifier import classify
    results, passed = [], 0
    for fx in fixtures:
        out = classify(fx["text"], fx.get("criterion"))
        dim = out[fx["dimension"]]
        label_ok = dim["label"] == fx["expected_label"]
        span_ok = dim["abstained"] or (dim.get("evidence_span") in fx["text"])
        entry = {"id": fx["id"], "group": fx["group"], "pass": bool(label_ok and span_ok),
                 "expected": fx["expected_label"], "got": dim["label"],
                 "rule_id": dim.get("rule_id"), "evidence_span_valid": span_ok}
        if not label_ok:
            entry["detail"] = dim
        results.append(entry)
        passed += entry["pass"]
    doc = {"phase": args.phase, "fixtures": len(fixtures), "passed": passed,
           "failed": len(fixtures) - passed, "all_pass": passed == len(fixtures),
           "results": results}
    name = "tdd-red-result.json" if args.phase == "RED" else "tdd-green-result.json"
    (HERE / name).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    summary = {k: doc[k] for k in ("phase", "fixtures", "passed", "failed", "all_pass")}
    print(json.dumps(summary, ensure_ascii=False))
    for e in results:
        if not e["pass"]:
            print("FAIL", e["id"], "expected", e["expected"], "got", e["got"], e["rule_id"])
    return 0 if doc["all_pass"] else 1

if __name__ == "__main__":
    sys.exit(main())
