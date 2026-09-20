#!/usr/bin/env python3
"""Mechanical agreement computation for V1.4 dual-pass human calibration.

Score-bearing fields only; free-text note never affects agreement.
Also runs derivation validity (verdict == derive(mode, behavior)) and the
frozen zero gates, then evaluates the hard calibration gates.
"""
import json
import os
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


def behavior_signature(row):
    if row.get("uncertainty_requirement_mode") == "COMPOUND":
        comps = row.get("compound_components") or []
        return tuple(sorted((c["kind"], c["behavior"]) for c in comps))
    return row.get("output_uncertainty_behavior") or derive_behavior_from_verdict(row)


def derive_behavior_from_verdict(row):
    # For single-component rows the passes may record only the verdict; the
    # behavior is then the canonical behavior consistent with (mode, verdict)
    # when uniquely determined, else None (not comparable).
    mode, verdict = row.get("uncertainty_requirement_mode"), row.get("uncertainty_verdict")
    if mode == "NONE":
        return "NOT_REQUIRED"
    table = EXPL_ROWS if mode == "EXPLICIT_LIMITATION" else NONASSERT_ROWS
    matches = [b for b, v in table.items() if v == verdict]
    return matches[0] if len(matches) == 1 else None


def load(name):
    with open(os.path.join(HERE, name)) as f:
        return {r["id"]: r for r in json.load(f)["rows"]}


def pct(n, d):
    return round(n / d, 4) if d else None


def main():
    fixtures = json.load(open(os.path.join(HERE, "boundary-calibration-a.json")))["fixtures"]
    dims = {f["id"]: f for f in fixtures}
    p1, p2 = load("calibration-a-label1.json"), load("calibration-a-label2.json")

    route_fields = ["proposition_present", "speaker_commitment", "route_verdict"]
    rows, violations = [], []
    for rid in sorted(dims):
        a, b, fx = p1[rid], p2[rid], dims[rid]
        if fx["dimension"].startswith("route"):
            fa = {k: a[k] for k in route_fields}
            fb = {k: b[k] for k in route_fields}
            field_agree = {k: fa[k] == fb[k] for k in route_fields}
            full = all(field_agree.values())
            rows.append({"id": rid, "dimension": fx["dimension"],
                         "pass1": fa, "pass2": fb,
                         "fields": field_agree, "semantic_fields_agree": full,
                         "note_only_mismatch": full and a.get("note") != b.get("note")})
            # Zero gates + schema invariants (both passes)
            for tag, r in (("pass1", a), ("pass2", b)):
                if r["speaker_commitment"] in NON_EVALUABLE and r["route_verdict"] == "NO_ACCEPTABLE_ROUTE":
                    violations.append(f"{rid}/{tag}: non-evaluable commitment -> NO_ACCEPTABLE_ROUTE")
                if r["speaker_commitment"] in {"ASSERTED", "HEDGED_ASSERTION"} and r["route_verdict"] == "UNRESOLVED":
                    violations.append(f"{rid}/{tag}: evaluable commitment must be scored, got UNRESOLVED")
                if r["speaker_commitment"] == "HEDGED_ASSERTION" and r["route_verdict"] == "ACCEPTABLE" and rid == "CAR-11":
                    violations.append(f"{rid}/{tag}: known boundary marker")
        else:
            mode1, mode2 = a["uncertainty_requirement_mode"], b["uncertainty_requirement_mode"]
            # Derivation validity per pass
            for tag, r in (("pass1", a), ("pass2", b)):
                mode = r["uncertainty_requirement_mode"]
                if mode == "NON_ASSERTION_CONSTRAINT" and r["uncertainty_verdict"] == "NOT_REQUIRED":
                    violations.append(f"{rid}/{tag}: NON_ASSERTION_CONSTRAINT + NOT_REQUIRED (schema-invalid)")
                sig = behavior_signature(r)
                if mode == "NONE" or sig is not None:
                    expected = derive(mode, sig, r.get("compound_components"))
                    if expected != r["uncertainty_verdict"]:
                        violations.append(f"{rid}/{tag}: verdict {r['uncertainty_verdict']} != derived {expected} from mode {mode} behavior {sig}")
            field_agree = {"uncertainty_requirement_mode": mode1 == mode2}
            sig1, sig2 = behavior_signature(a), behavior_signature(b)
            sig_comparable = sig1 is not None and sig2 is not None
            field_agree["uncertainty_behavior_or_components"] = sig1 == sig2
            field_agree["uncertainty_verdict"] = a["uncertainty_verdict"] == b["uncertainty_verdict"]
            full = all(field_agree.values())
            rows.append({"id": rid, "dimension": fx["dimension"],
                         "pass1": {"mode": mode1, "behavior_or_components": sig1 if not isinstance(sig1, tuple) else [list(t) for t in sig1], "verdict": a["uncertainty_verdict"]},
                         "pass2": {"mode": mode2, "behavior_or_components": sig2 if not isinstance(sig2, tuple) else [list(t) for t in sig2], "verdict": b["uncertainty_verdict"]},
                         "fields": field_agree, "semantic_fields_agree": full,
                         "behavior_comparison_informative": sig_comparable,
                         "note_only_mismatch": full and a.get("note") != b.get("note")})

    route_rows = [r for r in rows if r["dimension"].startswith("route")]
    unc_rows = [r for r in rows if r["dimension"].startswith("uncertainty")]
    n_unc_informative = sum(1 for r in unc_rows if r["behavior_comparison_informative"])

    def fstats(subset, fields):
        out = {}
        for fl in fields:
            n = sum(1 for r in subset if r["fields"][fl])
            out[fl] = {"agree": n, "n": len(subset), "rate": pct(n, len(subset))}
        n_full = sum(1 for r in subset if r["semantic_fields_agree"])
        out["full_semantic"] = {"agree": n_full, "n": len(subset), "rate": pct(n_full, len(subset))}
        return out

    route_stats = fstats(route_rows, route_fields)
    unc_stats = fstats(unc_rows, ["uncertainty_requirement_mode",
                                  "uncertainty_behavior_or_components", "uncertainty_verdict"])
    n_full = sum(1 for r in rows if r["semantic_fields_agree"])
    n_note_only = sum(1 for r in rows if r.get("note_only_mismatch"))
    overall = pct(n_full, len(rows))

    gates = {
        "overall_full_semantic_agreement": {"required": ">=0.95", "value": overall, "pass": overall is not None and overall >= 0.95},
        "route_verdict_agreement": {"required": ">=0.95", "value": route_stats["route_verdict"]["rate"], "pass": (route_stats["route_verdict"]["rate"] or 0) >= 0.95},
        "route_commitment_state_agreement": {"required": ">=0.90", "value": route_stats["speaker_commitment"]["rate"], "pass": (route_stats["speaker_commitment"]["rate"] or 0) >= 0.90},
        "uncertainty_verdict_agreement": {"required": ">=0.95", "value": unc_stats["uncertainty_verdict"]["rate"], "pass": (unc_stats["uncertainty_verdict"]["rate"] or 0) >= 0.95},
        "uncertainty_behavior_agreement": {"required": ">=0.90", "value": unc_stats["uncertainty_behavior_or_components"]["rate"], "pass": (unc_stats["uncertainty_behavior_or_components"]["rate"] or 0) >= 0.90},
    }
    zero_gate_results = {
        "non_evaluable_to_no_acceptable": sum(1 for v in violations if "NO_ACCEPTABLE_ROUTE" in v),
        "non_assertion_not_required": sum(1 for v in violations if "NOT_REQUIRED (schema-invalid)" in v),
        "derivation_violations": sum(1 for v in violations if "derived" in v),
        "evaluable_must_be_scored": sum(1 for v in violations if "must be scored" in v),
    }

    out = {
        "artifact": "V1.4 Calibration A dual-pass agreement (mechanical)",
        "protocol": "dual independent human passes, frozen V1.4 trees; note excluded from agreement",
        "n": len(rows),
        "overall_full_semantic_agreement": overall,
        "note_only_mismatch_rows": n_note_only,
        "uncertainty_behavior_comparisons": {
            "informative": n_unc_informative,
            "inferred_not_unique": len(unc_rows) - n_unc_informative,
            "n": len(unc_rows),
            "note": "single-component rows with ambiguous (mode,verdict)->behavior mapping are not behavior-comparable; they still count for mode and verdict agreement",
        },
        "route": route_stats,
        "uncertainty": unc_stats,
        "gates": gates,
        "zero_gates": zero_gate_results,
        "violations": violations,
        "disagreement_rows": [r for r in rows if not r["semantic_fields_agree"]],
        "rows": rows,
    }
    with open(os.path.join(HERE, "calibration-a-agreement.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    all_pass = all(g["pass"] for g in gates.values()) and not violations
    print("CALIBRATION_A", "PASS" if all_pass else "FAIL",
          f"overall={overall} note_only={n_note_only}",
          f"route_verdict={route_stats['route_verdict']['rate']}",
          f"commitment={route_stats['speaker_commitment']['rate']}",
          f"unc_verdict={unc_stats['uncertainty_verdict']['rate']}",
          f"unc_behavior={unc_stats['uncertainty_behavior_or_components']['rate']}",
          f"violations={len(violations)}")
    for v in violations:
        print("VIOLATION:", v)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
