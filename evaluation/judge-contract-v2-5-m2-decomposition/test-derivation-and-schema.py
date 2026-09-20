#!/usr/bin/env python3
"""Spot-checks for the V2.5 M2 derivation table and decomposition schema."""

import json


TABLE = json.load(open("deterministic-derivation-table.json"))
SCHEMA = json.load(open("m2-decomposition.schema.json"))

def derive(ts, nts, conf, suff):
    for row in TABLE["rows"]:
        if (
            row["trigger_support"] == ts
            and row["non_trigger_support"] == nts
            and row["evidence_conflict"] == conf
            and row["evidence_sufficiency"] == suff
        ):
            return row["derived_state"]
    raise KeyError((ts, nts, conf, suff))


def expect(ts, nts, conf, suff, want):
    got = derive(ts, nts, conf, suff)
    assert got == want, (ts, nts, conf, suff, got, want)


expect("PRESENT", "ABSENT", "NO", "SUFFICIENT", "CLEAR_TRIGGER_SUPPORT")
expect("PRESENT", "ABSENT", "YES", "SUFFICIENT", "AMBIGUOUS_OR_CONFLICTING")
expect("ABSENT", "PRESENT", "NO", "SUFFICIENT", "CLEAR_NON_TRIGGER_SUPPORT")
expect("ABSENT", "ABSENT", "NO", "SUFFICIENT", "CLEAR_NON_TRIGGER_SUPPORT")
expect("ABSENT", "ABSENT", "NO", "INSUFFICIENT", "INSUFFICIENT_TO_DECIDE")
expect("PRESENT", "UNRESOLVED", "NO", "SUFFICIENT", "UNRESOLVED")
expect("UNRESOLVED", "UNRESOLVED", "UNRESOLVED", "UNRESOLVED", "UNRESOLVED")

assert TABLE["row_count"] == 81

try:
    import jsonschema
except ImportError:
    print("jsonschema not installed; schema structural checks skipped")
else:
    ok = {
        "trigger_support": "PRESENT",
        "non_trigger_support": "ABSENT",
        "evidence_conflict": "NO",
        "evidence_sufficiency": "SUFFICIENT",
        "evidence_spans": ["kommunen har barnevernsvakt"],
        "note": "clear_trigger",
    }
    jsonschema.validate(ok, SCHEMA)
    no_span = dict(ok, evidence_spans=[])
    try:
        jsonschema.validate(no_span, SCHEMA)
        raise SystemExit("FAIL: PRESENT without span was accepted")
    except jsonschema.ValidationError:
        pass
    extra = dict(ok, critical_evidence_state="CLEAR_TRIGGER_SUPPORT")
    try:
        jsonschema.validate(extra, SCHEMA)
        raise SystemExit("FAIL: additional property was accepted")
    except jsonschema.ValidationError:
        pass
    print("schema checks: PASS")

print("derivation spot-checks: PASS")
