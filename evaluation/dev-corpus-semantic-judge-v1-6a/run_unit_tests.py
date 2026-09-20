#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="GREEN", choices=["RED", "GREEN"])
    args = ap.parse_args()
    fixtures = json.loads((HERE / "unit-fixtures.json").read_text())["fixtures"]
    try:
        from boundary_preclassifier import classify
        import_ok = True
        import_error = None
    except Exception as exc:  # RED phase: module missing or broken
        classify = None
        import_ok = False
        import_error = f"{type(exc).__name__}: {exc}"

    results = []
    passed = 0
    for fx in fixtures:
        if not import_ok:
            results.append({
                "id": fx["id"], "pass": False,
                "expected": fx["expected_label"], "got": None,
                "error": "classifier module unavailable",
            })
            continue
        try:
            out = classify(fx["text"], fx.get("criterion"))
            dim = out[fx["dimension"]]
            label_ok = dim["label"] == fx["expected_label"]
            span_ok = dim["abstained"] or (dim.get("evidence_span") in fx["text"])
            entry = {
                "id": fx["id"],
                "pass": bool(label_ok and span_ok),
                "expected": fx["expected_label"],
                "got": dim["label"],
                "rule_id": dim.get("rule_id"),
                "evidence_span_valid": span_ok,
            }
            if not label_ok:
                entry["detail"] = dim
        except Exception as exc:
            entry = {
                "id": fx["id"], "pass": False,
                "expected": fx["expected_label"], "got": None,
                "error": f"{type(exc).__name__}: {exc}",
            }
        results.append(entry)
        passed += entry["pass"]

    doc = {
        "phase": args.phase,
        "module_loaded": import_ok,
        "import_error": import_error,
        "fixtures": len(fixtures),
        "passed": passed,
        "failed": len(fixtures) - passed,
        "all_pass": passed == len(fixtures),
        "results": results,
    }
    (HERE / "unit-test-results.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    )
    summary = {k: doc[k] for k in ("phase", "module_loaded", "fixtures", "passed", "failed", "all_pass")}
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if doc["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
