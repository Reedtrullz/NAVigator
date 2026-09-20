#!/usr/bin/env python3
"""Deterministiske validator-failure-tester. Ingen proxy-kall."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantic_judge as sj

ANSWER = "Fastlegen kan henvise til BUP ved behov."

CASES = [
    ("malformed_json", '{"verdict": "PRESENT", broken', None),
    ("invalid_enum", '{"verdict": "PROBABLY", "evidence_spans": ["BUP"], "note": "x"}', None),
    ("missing_span", '{"verdict": "PRESENT", "note": "x"}', None),
    ("span_not_in_answer", '{"verdict": "PRESENT", "evidence_spans": ["IKKE I SVARET"], "note": "x"}', None),
    ("extra_field_rejected", '{"verdict": "PRESENT", "evidence_spans": ["BUP"], "note": "x", "score": 0.99}', "reject"),
    ("valid_baseline", '{"verdict": "PRESENT", "evidence_spans": ["BUP"], "note": "x"}', "ok"),
]


def main():
    failures = []
    for name, raw, expect in CASES:
        try:
            payload = sj._parse_json_loose(raw)
        except Exception:
            if expect is None:
                print(f"{name}: correctly rejected (parse failure)")
                continue
            failures.append((name, "unexpected parse failure"))
            continue
        normalized, err = sj._validate(payload, ANSWER, "forbidden_claim")
        if expect is None:
            if err is None:
                failures.append((name, "should have failed, got valid"))
            else:
                print(f"{name}: correctly rejected ({err})")
        elif expect == "ok":
            if err is not None:
                failures.append((name, f"should be valid, got: {err}"))
            else:
                print(f"{name}: valid as expected")

    # Extra-field policy: check what _validate does with unknown keys
    payload = sj._parse_json_loose(CASES[4][1])
    normalized, err = sj._validate(payload, ANSWER, "forbidden_claim")
    print(f"extra_field behavior: err={err!r} keys={sorted((normalized or {}).keys())}")

    if failures:
        print("FAILURES:", failures)
        sys.exit(1)
    print("schema failure tests: PASS")


if __name__ == "__main__":
    main()
