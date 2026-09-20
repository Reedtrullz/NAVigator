#!/usr/bin/env python3
"""Deterministiske validator-failure-tester for V1.1. Ingen proxy-kall."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v1_1_judge as sj  # noqa: E402

ANSWER = "Fastlegen kan henvise til BUP ved behov."

CASES = [
    ("malformed_json", '{"verdict": "PRESENT", broken', None),
    ("invalid_enum", '{"verdict": "CANONICAL_ACCEPTABLE", "evidence_spans": ["BUP"], "note": "x"}', None),
    ("invalid_enum_v1_label", '{"verdict": "EQUIVALENT_ACCEPTABLE", "evidence_spans": ["BUP"], "note": "x"}', None),
    ("missing_span", '{"verdict": "ACCEPTABLE", "note": "x"}', None),
    ("span_not_in_answer", '{"verdict": "ACCEPTABLE", "evidence_spans": ["IKKE I SVARET"], "note": "x"}', None),
    ("extra_field_rejected", '{"verdict": "ACCEPTABLE", "evidence_spans": ["BUP"], "note": "x", "score": 0.99}', "reject"),
    ("valid_baseline", '{"verdict": "ACCEPTABLE", "evidence_spans": ["henvise til BUP"], "note": "x"}', "ok"),
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
        normalized, err = sj._validate(payload, ANSWER, "route_equivalence")
        if expect is None:
            if err is None:
                failures.append((name, "should have failed, got valid"))
            else:
                print(f"{name}: correctly rejected ({err})")
        elif expect == "reject":
            if err is None or not str(err).startswith("unsupported_fields"):
                failures.append((name, f"expected unsupported_fields rejection, got: {err}"))
            else:
                print(f"{name}: correctly rejected ({err})")
        elif expect == "ok":
            if err is not None:
                failures.append((name, f"should be valid, got: {err}"))
            else:
                print(f"{name}: valid as expected")

    if failures:
        print("FAILURES:", failures)
        sys.exit(1)
    print("schema failure tests V1.1: PASS")


if __name__ == "__main__":
    main()
