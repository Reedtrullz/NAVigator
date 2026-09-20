#!/usr/bin/env python3
"""V1.6C.1 packet-builder TDD runner: mechanical packet tests only.

Tests the packet builder, NOT semantic accuracy. No model calls.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from packet_builder import build_packet  # noqa: E402

FORBIDDEN_PACKET_KEYS = {
    "gold", "expected", "stratum", "verdict", "acceptable",
    "forbidden_expected", "answer_key", "fixture_id", "id",
}
ALLOWED_TOP_KEYS = {
    "packet_version", "dimension", "source_text", "criterion", "case_context",
    "clause_spans", "route_candidates", "quote_spans", "negation_spans",
    "retraction_spans", "hedge_spans", "assertion_spans",
    "conditional_spans", "attribution_spans", "vague_spans", "a3",
    "deterministic_evidence",
}
SPAN_FIELDS = [
    "clause_spans", "route_candidates", "quote_spans", "negation_spans",
    "retraction_spans", "hedge_spans", "assertion_spans",
    "conditional_spans", "attribution_spans", "vague_spans",
]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def validate_packet(packet, fx, failures):
    tid = fx["tid"]
    def bad(msg):
        failures.append(f"{tid}: {msg}")
    for k in packet:
        if k not in ALLOWED_TOP_KEYS:
            bad(f"forbidden/unknown top-level key: {k}")
    for k in FORBIDDEN_PACKET_KEYS:
        if k in packet:
            bad(f"gold-leakage key present: {k}")
    src_lower = packet["source_text"].lower()
    for field in SPAN_FIELDS:
        for i, span in enumerate(packet.get(field, [])):
            if set(span.keys()) - {"start", "end", "text", "clause_index", "provenance"}:
                bad(f"{field}[{i}] unexpected keys: {sorted(span.keys())}")
            s, e, t = span.get("start"), span.get("end"), span.get("text")
            if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(src_lower)):
                bad(f"{field}[{i}] invalid offsets: {s},{e} len={len(src_lower)}")
                continue
            if src_lower[s:e] != t:
                bad(f"{field}[{i}] text does not match source at offsets")
            prov = span.get("provenance", "")
            if not (isinstance(prov, str) and prov.startswith("a3_")):
                bad(f"{field}[{i}] missing deterministic provenance")
    for i, ev in enumerate(packet.get("deterministic_evidence", [])):
        if ev.lower() not in src_lower:
            bad(f"deterministic_evidence[{i}] not found in source_text: {ev[:50]}")
    ex = fx.get("expects", {})
    if "min_clauses" in ex and len(packet.get("clause_spans", [])) < ex["min_clauses"]:
        bad(f"clause_spans {len(packet.get('clause_spans', []))} < {ex['min_clauses']}")
    for field, key in [("route_candidates", "route_candidates_min"),
                       ("quote_spans", "quote_spans_min"),
                       ("negation_spans", "negation_spans_min"),
                       ("retraction_spans", "retraction_spans_min"),
                       ("hedge_spans", "hedge_spans_min"),
                       ("assertion_spans", "assertion_spans_min"),
                       ("conditional_spans", "conditional_spans_min"),
                       ("attribution_spans", "attribution_spans_min")]:
        if key in ex and len(packet.get(field, [])) < ex[key]:
            bad(f"{field} {len(packet.get(field, []))} < {ex[key]}")
    a3 = packet.get("a3", {})
    rc = a3.get("route_commitment", {})
    if "a3_route_abstained" in ex and rc.get("abstained") is not ex["a3_route_abstained"]:
        bad(f"a3 route abstained {rc.get('abstained')} != {ex['a3_route_abstained']}")
    if ex.get("a3_route_reason_nonempty") and not rc.get("reason"):
        bad("a3 route abstain reason empty")
    stratum = fx.get("stratum", "").lower()
    if stratum and stratum in canonical(packet).lower():
        bad("stratum value leaked into packet")


def main():
    fixtures = json.load(open(os.path.join(HERE, "tdd-fixtures.json")))["fixtures"]
    failures = []
    for fx in fixtures:
        try:
            p1 = build_packet(fx["dimension"], fx["criterion"], fx["source_text"],
                              fx.get("ctx", ""))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{fx['tid']}: build_packet raised {type(exc).__name__}: {exc}")
            continue
        try:
            p2 = build_packet(fx["dimension"], fx["criterion"], fx["source_text"],
                              fx.get("ctx", ""))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{fx['tid']}: second build raised {exc}")
            continue
        if canonical(p1) != canonical(p2):
            failures.append(f"{fx['tid']}: non-deterministic build")
        validate_packet(p1, fx, failures)
    report = {
        "artifact": "V1.6C.1 PACKET-BUILDER TEST RESULT",
        "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
        "n_fixtures": len(fixtures),
        "n_failures": len(failures),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    out = os.path.join(HERE, "packet-builder-tests.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{report['status']}: {len(fixtures) - len(failures)}/{len(fixtures)} passed")
    for f in failures:
        print("  " + f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
