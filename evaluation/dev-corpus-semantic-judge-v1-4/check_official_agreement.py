#!/usr/bin/env python3
"""Mechanical dual-pass agreement for V1.4 official human gold (spec 41)."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EXPL_ROWS = {
    "EXPLICIT_LIMITATION": "SATISFIED", "PARTIAL_LIMITATION": "PARTIAL",
    "HEDGE": "PARTIAL", "CONTRADICTORY_LIMITATION": "PARTIAL",
    "OVERCONFIDENT_ASSERTION": "VIOLATED", "NONE": "UNRESOLVED",
    "UNRESOLVED": "UNRESOLVED",
}
NONASSERT_ROWS = {
    "NONE": "SATISFIED", "HEDGE": "SATISFIED",
    "EXPLICIT_LIMITATION": "SATISFIED", "PARTIAL_LIMITATION": "SATISFIED",
    "CONTRADICTORY_LIMITATION": "VIOLATED",
    "OVERCONFIDENT_ASSERTION": "VIOLATED", "UNRESOLVED": "UNRESOLVED",
}
NON_EVALUABLE = {"HYPOTHETICAL_ONLY", "QUOTED_ONLY", "NEGATED",
                 "SELF_RETRACTED", "UNRESOLVED"}


def derive(mode, behavior, components=None):
    if mode == "NONE":
        return "NOT_REQUIRED"
    if mode == "EXPLICIT_LIMITATION":
        return EXPL_ROWS[behavior]
    if mode == "NON_ASSERTION_CONSTRAINT":
        return NONASSERT_ROWS[behavior]
    if mode == "COMPOUND":
        verdicts = []
        for c in components:
            verdicts.append(EXPL_ROWS[c["behavior"]] if c["kind"] == "EXPRESSION"
                            else NONASSERT_ROWS[c["behavior"]])
        if all(v == "SATISFIED" for v in verdicts):
            return "SATISFIED"
        if "VIOLATED" in verdicts and "SATISFIED" in verdicts:
            return "PARTIAL"
        if all(v == "VIOLATED" for v in verdicts):
            return "VIOLATED"
        if "VIOLATED" not in verdicts and "SATISFIED" in verdicts:
            return "PARTIAL"
        return "UNRESOLVED"
    raise ValueError(mode)


def norm(s):
    s = s.replace("aa", "å").replace("oe", "ø").replace("ae", "æ")
    return re.sub(r"\s+", " ", s.strip().lower())


def pct(n, d):
    return round(n / d, 4) if d else None


def main():
    fxdoc = json.load(open(os.path.join(HERE, "official-validation-fixtures.json")))
    fixtures = {f["id"]: f for f in fxdoc["fixtures"]}
    p1 = {r["id"]: r for r in json.load(open(os.path.join(HERE, "human-label-pass1.json")))["rows"]}
    p2 = {r["id"]: r for r in json.load(open(os.path.join(HERE, "human-label-pass2.json")))["rows"]}

    rows, violations = [], []
    evidence_bad = {"pass1": 0, "pass2": 0}
    for rid in sorted(fixtures):
        fx, a, b = fixtures[rid], p1[rid], p2[rid]
        ans_norm = norm(fx["sut_answer"])
        for tag, r in (("pass1", a), ("pass2", b)):
            spans = r.get("evidence_spans") or []
            if spans:
                ok = any(norm(s) in ans_norm for s in spans)
                if not ok:
                    evidence_bad[tag] += 1
                    violations.append(f"{rid}/{tag}: no verbatim evidence span in SUT answer")
        if fx["dimension"] in ("critical_condition", "forbidden_claim"):
            fa, fb = a["verdict"], b["verdict"]
            fields = {"verdict": fa == fb}
            rows.append({"id": rid, "dimension": fx["dimension"],
                         "pass1": {"verdict": fa}, "pass2": {"verdict": fb},
                         "fields": fields, "semantic_fields_agree": fields["verdict"],
                         "note_only_mismatch": fields["verdict"] and a.get("note") != b.get("note")})
        elif fx["dimension"] == "route_correctness":
            keys = ("proposition_present", "speaker_commitment", "route_verdict")
            fields = {k: a[k] == b[k] for k in keys}
            for tag, r in (("pass1", a), ("pass2", b)):
                if r["speaker_commitment"] in NON_EVALUABLE and r["route_verdict"] == "NO_ACCEPTABLE_ROUTE":
                    violations.append(f"{rid}/{tag}: non-evaluable commitment -> NO_ACCEPTABLE_ROUTE")
                if r["speaker_commitment"] in {"ASSERTED", "HEDGED_ASSERTION"} and r["route_verdict"] == "UNRESOLVED":
                    violations.append(f"{rid}/{tag}: evaluable commitment must be scored, got UNRESOLVED")
            rows.append({"id": rid, "dimension": fx["dimension"],
                         "pass1": {k: a[k] for k in keys},
                         "pass2": {k: b[k] for k in keys},
                         "fields": fields, "semantic_fields_agree": all(fields.values()),
                         "note_only_mismatch": all(fields.values()) and a.get("note") != b.get("note")})
        else:
            mode1, mode2 = a["uncertainty_requirement_mode"], b["uncertainty_requirement_mode"]

            def sig(r):
                if r["uncertainty_requirement_mode"] == "COMPOUND":
                    return tuple(sorted((c["kind"], c["behavior"]) for c in r["compound_components"]))
                return r["output_uncertainty_behavior"]

            s1, s2 = sig(a), sig(b)
            for tag, r in (("pass1", a), ("pass2", b)):
                mode = r["uncertainty_requirement_mode"]
                if mode == "NON_ASSERTION_CONSTRAINT" and r["uncertainty_verdict"] == "NOT_REQUIRED":
                    violations.append(f"{rid}/{tag}: NON_ASSERTION_CONSTRAINT + NOT_REQUIRED (schema-invalid)")
                expected = derive(mode, sig(r), r.get("compound_components"))
                if expected != r["uncertainty_verdict"]:
                    violations.append(f"{rid}/{tag}: verdict {r['uncertainty_verdict']} != derived {expected}")
            fields = {"uncertainty_requirement_mode": mode1 == mode2,
                      "uncertainty_behavior_or_components": s1 == s2,
                      "uncertainty_verdict": a["uncertainty_verdict"] == b["uncertainty_verdict"]}
            rows.append({"id": rid, "dimension": fx["dimension"],
                         "pass1": {"mode": mode1, "behavior_or_components": list(s1) if isinstance(s1, tuple) else s1, "verdict": a["uncertainty_verdict"]},
                         "pass2": {"mode": mode2, "behavior_or_components": list(s2) if isinstance(s2, tuple) else s2, "verdict": b["uncertainty_verdict"]},
                         "fields": fields, "semantic_fields_agree": all(fields.values()),
                         "note_only_mismatch": all(fields.values()) and a.get("note") != b.get("note")})

    route_rows = [r for r in rows if r["dimension"] == "route_correctness"]
    unc_rows = [r for r in rows if r["dimension"] == "required_uncertainty"]

    def fstats(subset, fields):
        out = {}
        for fl in fields:
            n = sum(1 for r in subset if r["fields"][fl])
            out[fl] = {"agree": n, "n": len(subset), "rate": pct(n, len(subset))}
        n_full = sum(1 for r in subset if r["semantic_fields_agree"])
        out["full_semantic"] = {"agree": n_full, "n": len(subset), "rate": pct(n_full, len(subset))}
        return out

    route_stats = fstats(route_rows, ["proposition_present", "speaker_commitment", "route_verdict"])
    unc_stats = fstats(unc_rows, ["uncertainty_requirement_mode", "uncertainty_behavior_or_components", "uncertainty_verdict"])
    n_full = sum(1 for r in rows if r["semantic_fields_agree"])
    overall = pct(n_full, len(rows))
    crit_n = sum(1 for r in rows if r["dimension"] == "critical_condition" and r["semantic_fields_agree"])
    forb_n = sum(1 for r in rows if r["dimension"] == "forbidden_claim" and r["semantic_fields_agree"])
    crit_rate, forb_rate = pct(crit_n, 25), pct(forb_n, 25)
    gates = {
        "overall_semantic_agreement": {"required": ">=0.95", "value": overall, "pass": overall is not None and overall >= 0.95},
        "critical_agreement": {"required": ">=0.95", "value": crit_rate, "pass": (crit_rate or 0) >= 0.95},
        "forbidden_agreement": {"required": ">=0.95", "value": forb_rate, "pass": (forb_rate or 0) >= 0.95},
        "route_agreement": {"required": ">=0.95", "value": route_stats["full_semantic"]["rate"], "pass": (route_stats["full_semantic"]["rate"] or 0) >= 0.95},
        "route_commitment_state_agreement": {"required": ">=0.90", "value": route_stats["speaker_commitment"]["rate"], "pass": (route_stats["speaker_commitment"]["rate"] or 0) >= 0.90},
        "uncertainty_agreement": {"required": ">=0.95", "value": unc_stats["full_semantic"]["rate"], "pass": (unc_stats["full_semantic"]["rate"] or 0) >= 0.95},
        "uncertainty_behavior_agreement": {"required": ">=0.90", "value": unc_stats["uncertainty_behavior_or_components"]["rate"], "pass": (unc_stats["uncertainty_behavior_or_components"]["rate"] or 0) >= 0.90},
    }
    zero_gates = {
        "non_evaluable_to_no_acceptable": sum(1 for v in violations if "NO_ACCEPTABLE_ROUTE" in v),
        "non_assertion_not_required": sum(1 for v in violations if "NOT_REQUIRED (schema-invalid)" in v),
        "derivation_violations": sum(1 for v in violations if "!= derived" in v),
        "evaluable_must_be_scored": sum(1 for v in violations if "must be scored" in v),
        "invalid_evidence_spans": evidence_bad,
    }
    out = {
        "artifact": "V1.4 official dual-pass human agreement (mechanical, pre-adjudication)",
        "protocol": "score-bearing fields only; note excluded; zero gates and derivation checked on both passes",
        "n": len(rows),
        "overall_semantic_agreement": overall,
        "note_only_mismatch_rows": sum(1 for r in rows if r.get("note_only_mismatch")),
        "critical": {"agree": crit_n, "n": 25, "rate": crit_rate},
        "forbidden": {"agree": forb_n, "n": 25, "rate": forb_rate},
        "route": route_stats, "uncertainty": unc_stats,
        "gates": gates, "zero_gates": zero_gates,
        "violations": violations,
        "disagreement_rows": [r for r in rows if not r["semantic_fields_agree"]],
        "rows": rows,
    }
    with open(os.path.join(HERE, "annotation-agreement.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    all_pass = (all(g["pass"] for g in gates.values())
                and zero_gates["non_evaluable_to_no_acceptable"] == 0
                and zero_gates["non_assertion_not_required"] == 0
                and zero_gates["derivation_violations"] == 0
                and zero_gates["evaluable_must_be_scored"] == 0
                and sum(evidence_bad.values()) == 0)
    print("OFFICIAL_GOLD_AGREEMENT", "PASS" if all_pass else "FAIL",
          f"overall={overall}",
          f"critical={crit_rate} forbidden={forb_rate}",
          f"route={route_stats['full_semantic']['rate']} commitment={route_stats['speaker_commitment']['rate']}",
          f"unc={unc_stats['full_semantic']['rate']} behavior={unc_stats['uncertainty_behavior_or_components']['rate']}",
          f"violations={len(violations)} evidence_bad={evidence_bad}")
    for v in violations:
        print("VIOLATION:", v)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
