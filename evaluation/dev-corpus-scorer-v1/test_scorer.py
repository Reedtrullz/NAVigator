#!/usr/bin/env python3
"""Scorer self-test for dev-corpus-scorer-v1.

Runs RED-first fixture suite, gold-leakage invariant, determinism check,
and basic schema checks. Writes scorer-fixture-results.json and
determinism-report.json when green. Exits non-zero on any failure.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scorer import (
    SemanticJudgeStub,
    build_sut_input,
    score_case,
    run_fixtures,
)


def load_json(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def test_fixtures():
    fixtures = load_json("scorer-fixtures.json")["fixtures"]
    results = run_fixtures(fixtures)
    mismatches = []
    for r in results:
        exp = r["expected"]
        act = r["actual"]
        for key, want in exp.items():
            got = act.get(key)
            if want != got:
                mismatches.append(f"{r['id']}.{key}: expected {want!r}, got {got!r}")
        for note in exp.get("notes", []):
            if note not in act.get("notes", []):
                mismatches.append(f"{r['id']}: missing note {note}")
    if mismatches:
        fail("fixture mismatches:\n" + "\n".join(mismatches))
    print(f"fixtures: {len(results)}/{len(results)} PASS")
    return fixtures, results


def test_gold_leakage():
    fixtures = load_json("scorer-fixtures.json")["fixtures"]
    gold_keys = {
        "acceptable_routes", "forbidden_claims", "required_uncertainty",
        "required_evidence_fields", "critical_error_if", "safety_priority",
        "gold", "expected_answer",
    }
    exposed = 0
    for f in fixtures:
        sut_input = build_sut_input(f["case"])
        blob = json.dumps(sut_input, ensure_ascii=False)
        for key in gold_keys:
            if key in sut_input:
                exposed += 1
                fail(f"gold key {key!r} exposed in SUT input for {f['id']}")
            if f'"{key}"' in blob:
                exposed += 1
                fail(f"gold key {key!r} string-exposed in SUT input for {f['id']}")
    assert exposed == 0
    print("gold leakage: GOLD_FIELDS_EXPOSED_TO_SUT = 0")


def test_determinism():
    fixtures = load_json("scorer-fixtures.json")["fixtures"]
    judge = SemanticJudgeStub()
    runs = []
    for _ in range(3):
        out = json.dumps(
            [score_case(f["case"], f["raw_answer"], f["capabilities"], judge)
             for f in fixtures],
            ensure_ascii=False, sort_keys=True,
        )
        runs.append(out)
    identical = all(r == runs[0] for r in runs)
    if not identical:
        fail("deterministic layer not byte-identical across 3 runs")
    report = {
        "runs": 3,
        "layer": "deterministic",
        "byte_identical": True,
        "sha256_first_run": __import__("hashlib").sha256(runs[0].encode()).hexdigest(),
    }
    (HERE / "determinism-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("determinism: 3/3 byte-identical")


def test_schema_shape():
    fixtures = load_json("scorer-fixtures.json")["fixtures"]
    judge = SemanticJudgeStub()
    result = score_case(fixtures[0]["case"], fixtures[0]["raw_answer"],
                        fixtures[0]["capabilities"], judge)
    required = [
        "case_id", "corpus", "applicability", "execution_status",
        "critical_error", "forbidden_claims", "safety_priority",
        "acceptable_route", "uncertainty", "required_evidence",
        "evidence_completeness", "scorer_notes", "scorer_version",
    ]
    missing = [k for k in required if k not in result]
    if missing:
        fail(f"result schema missing keys: {missing}")
    if result["applicability"] not in {"APPLICABLE", "NOT_APPLICABLE_TO_SUT", "EXECUTION_FAILED", "SCORED"}:
        fail("invalid applicability enum")
    print("schema shape: required keys and enums present")


def main():
    test_gold_leakage()
    fixtures, results = test_fixtures()
    test_schema_shape()
    test_determinism()
    payload = {
        "fixture_count": len(fixtures),
        "pass": len(results),
        "fail": 0,
        "results": results,
    }
    (HERE / "scorer-fixture-results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("ALL GREEN")


if __name__ == "__main__":
    main()
