#!/usr/bin/env python3
"""Sections 18-21: deferred comparisons, routing funnel, stage
classification, and regression inventory for the complete Wave-4
measurement. Read-only over frozen inputs; runs after the measurement
freeze emitted by freeze_completed_wave4_measurement.py.

Comparison semantics (frozen Wave-3 technique):
  semantic_state maps each criterion verdict to FAIL / UNRESOLVED /
  DEGRADED / PASS / ABSENT_OR_NOT_APPLICABLE. FAIL->UNRESOLVED is a
  fail-closed lateral movement, never an improvement. UNRESOLVED->FAIL
  is a regression. Adapter effect (A) and product effect (B) stay
  separate: Wave-4 gets no product credit for adapter-only changes.
"""
import collections
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(REPO)
EVAL = os.path.join(REPO, "evaluation")
QUOTA = os.path.join(EVAL,
                     "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
RUNS = os.path.join(EVAL, "full-sut-repair-wave-4-v1", "runs",
                    "structural-120-replay-v1")
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"
RANK = {"FAIL": 0, "UNRESOLVED": 1, "DEGRADED": 2, "PASS": 3,
        "ABSENT_OR_NOT_APPLICABLE": 4}
SEVERITY = {"critical_condition": "P0",
            "forbidden_claim": "P1",
            "route_correctness": "P1",
            "required_uncertainty": "P2",
            "evidence_completeness": "P2"}


def semantic_state(dimension, verdict):
    if verdict is None:
        return "ABSENT_OR_NOT_APPLICABLE"
    if dimension == "critical_condition":
        return ("FAIL" if verdict in ("TRIGGERED", "CRITICAL_ERROR")
                else "PASS" if verdict == "NOT_TRIGGERED" else "UNRESOLVED")
    if dimension == "forbidden_claim":
        return ("FAIL" if verdict in ("PRESENT", "CLAIM_PRESENT")
                else "PASS" if verdict in ("ABSENT", "CLAIM_ABSENT_TAKEN")
                else "UNRESOLVED")
    if dimension == "route_correctness":
        return ("PASS" if verdict == "ACCEPTABLE"
                else "UNRESOLVED" if verdict == "UNRESOLVED" else "FAIL")
    if dimension == "required_uncertainty":
        return ("PASS" if verdict in ("SATISFIED", "NOT_REQUIRED")
                else "DEGRADED" if verdict == "PARTIAL"
                else "FAIL" if verdict == "VIOLATED" else "UNRESOLVED")
    if dimension == "evidence_completeness":
        return ("PASS" if verdict == 1.0
                else "DEGRADED" if isinstance(verdict, (int, float))
                and 0 < verdict < 1
                else "FAIL" if verdict == 0.0 else "UNRESOLVED")
    raise ValueError(dimension)


def rows_of(doc):
    for case in doc["cases"]:
        for row in case["criteria"]:
            yield case["case_id"], row


def load(path):
    return json.load(open(path, encoding="utf-8"))


def compare(old_doc, new_doc, old_side, new_side):
    old_by_id = {r["criterion_id"]: (cid, r) for cid, r in rows_of(old_doc)}
    new_by_id = {r["criterion_id"]: (cid, r) for cid, r in rows_of(new_doc)}
    assert set(old_by_id) == set(new_by_id) and len(old_by_id) == 600
    verdict_transitions = collections.Counter()
    state_transitions = collections.Counter()
    improved, regressed, lateral = [], [], []
    for cid in old_by_id:
        case_id, orow = old_by_id[cid]
        _, nrow = new_by_id[cid]
        dim = orow["dimension"]
        key = (orow["verdict"], nrow["verdict"])
        verdict_transitions["%s -> %s" % key] += 1
        ostate = semantic_state(dim, orow["verdict"]
                                if orow["status"] == "SCORED" else None)
        nstate = semantic_state(dim, nrow["verdict"]
                                if nrow["status"] == "SCORED" else None)
        state_transitions["%s -> %s" % (ostate, nstate)] += 1
        if ostate == nstate:
            continue
        entry = {"case_id": case_id, "criterion_id": cid, "dimension": dim,
                 "old_verdict": orow["verdict"], "new_verdict": nrow["verdict"],
                 "old_state": ostate, "new_state": nstate,
                 "old_authority": orow.get("authority"),
                 "new_authority": nrow.get("authority"),
                 "transition_class": ("LATERAL" if nstate == "UNRESOLVED"
                                      else "IMPROVEMENT" if RANK[nstate] > RANK[ostate]
                                      else "REGRESSION")}
        if nstate == "UNRESOLVED":
            lateral.append(entry)
        elif RANK[nstate] > RANK[ostate]:
            improved.append(entry)
        else:
            entry = {**entry, "severity": SEVERITY[dim]}
            regressed.append(entry)

    def tally(doc):
        states = collections.Counter()
        failing = set()
        for _, row in rows_of(doc):
            if row["status"] == "NOT_APPLICABLE":
                continue
            state = semantic_state(row["dimension"], row["verdict"]) \
                if row["status"] == "SCORED" else "PENDING"
            states[state] += 1
            if state != "PASS":
                failing.add(row["case_id"])
        return states, sum(states.values()), failing

    o_states, o_n, o_fail = tally(old_doc)
    n_states, n_n, n_fail = tally(new_doc)
    per_dim_delta = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        o = collections.Counter(str(r["verdict"]) if r["verdict"] is not None
                                else "NOT_APPLICABLE"
                                for _, r in rows_of(old_doc) if r["dimension"] == dim)
        n = collections.Counter(str(r["verdict"]) if r["verdict"] is not None
                                else "NOT_APPLICABLE"
                                for _, r in rows_of(new_doc) if r["dimension"] == dim)
        per_dim_delta[dim] = {"old": dict(o), "new": dict(n)}
    return {
        "old_side": old_side, "new_side": new_side,
        "verdict_transitions": dict(verdict_transitions),
        "semantic_state_transitions": dict(state_transitions),
        "per_dimension_transitions_note": "collapsed per-dimension delta below; "
                                          "transition lists carry criterion detail",
        "delta_report": {
            "old_states": dict(o_states),
            "new_states": dict(n_states),
            "old_failure_rate": round(1 - o_states["PASS"] / o_n, 4),
            "new_failure_rate": round(1 - n_states["PASS"] / n_n, 4),
            "old_failing_cases": len(o_fail),
            "new_failing_cases": len(n_fail)},
        "per_dimension_verdicts_old_vs_new": per_dim_delta,
        "improved_criteria": improved, "regressed_criteria": regressed,
        "lateral_criteria": lateral,
        "regression_count": len(regressed),
        "improvement_count": len(improved),
        "lateral_count": len(lateral)}


def side(label, path, is_primary):
    return {"label": label, "path": path,
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
            "is_primary": is_primary}


def main():
    bridge_path = os.path.join(QUOTA, "wave3-compat-bridge-results.json")
    orig_path = os.path.join(
        EVAL, "measurement-v3-final-authority-provenance-repair-v1",
        "combined-measurement-results-complete-provenance-corrected.json")
    w4_path = os.path.join(HERE, "completed-wave4-measurement-results.json")
    bridge, orig, w4 = load(bridge_path), load(orig_path), load(w4_path)
    w3_hist_path = os.path.join(
        EVAL, "measurement-v3-remeasure-repair-wave-3",
        "wave3-combined-measurement-results.json")
    w3_hist = load(w3_hist_path)

    # A. Measurement adapter effect: historical Wave-3 -> compat bridge
    adapter = compare(w3_hist, bridge,
                      side("HISTORICAL_WAVE3",
                           w3_hist_path, False),
                      side("WAVE3_COMPAT_BRIDGE", bridge_path, True))
    adapter["artifact"] = "measurement-adapter-effect"
    adapter["comparison"] = "historical Wave-3 measurement vs WAVE3_COMPAT_BRIDGE"
    adapter["role"] = "ADAPTER_ONLY_EFFECT; no product credit"

    # B. Product effect (PRIMARY): compat bridge -> Wave 4
    product = compare(bridge, w4,
                      side("WAVE3_COMPAT_BRIDGE", bridge_path, True),
                      side("MEASUREMENT_V3_REMEASURE_WAVE_4_COMPLETE", w4_path, True))
    product["artifact"] = "wave3bridge-wave4-transition-matrix"
    product["comparison"] = "WAVE3_COMPAT_BRIDGE vs complete Wave-4 measurement"
    product["role"] = "PRIMARY_PRODUCT_EFFECT"

    # C. Cumulative: original provenance-corrected baseline -> Wave 4
    cumulative = compare(orig, w4,
                         side("MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_"
                              "PROVENANCE_CORRECTED", orig_path, False),
                         side("MEASUREMENT_V3_REMEASURE_WAVE_4_COMPLETE", w4_path, True))
    cumulative["artifact"] = "original-wave4-transition-matrix"
    cumulative["comparison"] = ("original provenance-corrected baseline vs "
                                "complete Wave-4 measurement")
    cumulative["role"] = "CUMULATIVE_ADAPTER_PLUS_PRODUCT_EFFECT"

    for name, doc in (("measurement-adapter-effect.json", adapter),
                      ("wave3bridge-wave4-transition-matrix.json", product),
                      ("original-wave4-transition-matrix.json", cumulative)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # Sections 19-20: routing funnel + failure-stage classification
    preds = {}
    for track in ("routing_cases", "safety_cases", "discovery_adversarial_cases"):
        pdir = os.path.join(RUNS, track, "predictions")
        for fn in sorted(os.listdir(pdir)):
            if fn.endswith(".json"):
                preds[fn[:-5]] = load(os.path.join(pdir, fn))
    assert len(preds) == 120, len(preds)
    w4_route = {r["case_id"]: r for _, r in rows_of(w4)
                if r["dimension"] == "route_correctness"}
    bridge_route = {r["case_id"]: r for _, r in rows_of(bridge)
                    if r["dimension"] == "route_correctness"}
    na_cases = {cid for cid, r in w4_route.items() if r["status"] == "NOT_APPLICABLE"}
    assert len(na_cases) == 12
    evaluated = [cid for cid in sorted(w4_route) if cid not in na_cases]
    emitters = [cid for cid in preds if preds[cid]["routes"]]
    eval_emitters = [cid for cid in evaluated if preds[cid]["routes"]]
    adapter_data = load(os.path.join(QUOTA, "route-adapter-analysis-data.json"))
    per_case = adapter_data["per_case"]
    assert len(per_case) == 120

    # Frozen stage sets from the Wave-3 close-out route-lane audit
    R1 = {"ROUT-024", "ROUT-032", "ROUT-040", "ROUT-052", "ROUT-066",
          "ROUT-067", "ROUT-072", "ROUT-083", "SAF-012"}
    R3 = {"DIS-112", "DIS-119", "ROUT-038", "ROUT-039", "ROUT-041", "ROUT-054",
          "ROUT-064", "ROUT-065", "ROUT-068", "ROUT-089", "SAF-009"}
    R5 = {"ROUT-042", "ROUT-061", "ROUT-073", "ROUT-075"}
    stage_counts = collections.Counter()
    rows = []
    for cid in evaluated:
        crit = w4_route[cid]
        adapter_case = per_case[cid]
        case_evs = [m for c4 in w4["cases"] if c4["case_id"] == cid
                    for cr in c4["criteria"] for m in (cr.get("evidence") or [])]
        marker_text = " ".join(case_evs)
        flags = []
        if "PREMATURE_ABSENCE" in marker_text:
            flags.append("MEASUREMENT_SENSITIVITY_PREMATURE_ABSENCE")
        if "CERTAINTY_MARKER" in marker_text:
            flags.append("MEASUREMENT_SENSITIVITY_CERTAINTY_MARKER")
        if cid in R1:
            stage = "R1_INVALID_ROUTE_OBJECT"
        elif cid in R3:
            stage = "R3_WRONG_SERVICE_FAMILY"
        elif cid in R5:
            stage = "R5_MISSING_OR_WRONG_CONDITION"
        elif not preds[cid]["routes"]:
            stage = "R0_NO_STRUCTURED_ROUTE"
        elif not any(r["all_refs_joined"] for r in adapter_case["routes"]):
            stage = "R6_PROVENANCE_OR_EVIDENCE"
        else:
            stage = "R10_OTHER"
        stage_counts[stage] += 1
        rows.append({
            "case_id": cid, "criterion_id": crit["criterion_id"],
            "authority": crit["authority"], "verdict": crit["verdict"],
            "primary_stage": stage, "secondary_flags": flags,
            "route_mode": adapter_case["mode"],
            "route_entries": len(adapter_case["routes"]),
            "evidence_joined_route_entries":
                sum(1 for r in adapter_case["routes"] if r["all_refs_joined"]),
            "case_routes": preds[cid]["routes"],
            "case_no_route_asserted": preds[cid]["no_route_asserted"],
            "presented_as_complete": adapter_case["presented_as_complete"]})
    for cid in sorted(na_cases):
        rows.append({"case_id": cid,
                     "criterion_id": w4_route[cid]["criterion_id"],
                     "authority": w4_route[cid]["authority"],
                     "verdict": None,
                     "primary_stage": "NOT_APPLICABLE_GOLD_NO_ROUTES",
                     "secondary_flags": [],
                     "route_mode": per_case[cid]["mode"],
                     "route_entries": len(per_case[cid]["routes"]),
                     "evidence_joined_route_entries":
                         sum(1 for r in per_case[cid]["routes"]
                             if r["all_refs_joined"]),
                     "case_routes": preds[cid]["routes"],
                     "case_no_route_asserted": preds[cid]["no_route_asserted"],
                     "presented_as_complete": per_case[cid]["presented_as_complete"]})
    assert len(rows) == 120

    funnel = {
        "artifact": "wave4-resume-routing-funnel", "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classification": "BURNED_DEV_BASELINE_ONLY",
        "basis": {
            "wave4_measurement_freeze":
                "completed-wave4-measurement-freeze-manifest.json",
            "wave4_predictions":
                "evaluation/full-sut-repair-wave-4-v1/runs/"
                "structural-120-replay-v1 (frozen)",
            "route_adapter_analysis_data":
                "measurement-v3-remeasure-repair-wave-4-quota-safe-v1/"
                "route-adapter-analysis-data.json (frozen)"},
        "wave3_bridge": {
            "route_criteria_total": 120,
            "route_evaluated": len(bridge_route) - len(na_cases),
            "not_applicable": len(na_cases),
            "route_pass": sum(1 for r in bridge_route.values()
                              if r["verdict"] == "ACCEPTABLE"),
            "route_fail": sum(1 for r in bridge_route.values()
                              if r["status"] == "SCORED"
                              and r["verdict"] != "ACCEPTABLE"),
            "partial_route": sum(1 for r in bridge_route.values()
                                 if r["verdict"] == "PARTIAL"),
            "structured_route_cases": len(emitters),
            "structured_route_entries": adapter_data["routes_total"],
            "evidence_joins_found": adapter_data["evidence_joins_found"]},
        "wave4": {
            "route_criteria_total": 120,
            "route_evaluated": len(evaluated),
            "not_applicable": len(na_cases),
            "route_pass": sum(1 for r in w4_route.values()
                              if r["verdict"] == "ACCEPTABLE"),
            "route_fail": sum(1 for r in w4_route.values()
                              if r["status"] == "SCORED"
                              and r["verdict"] != "ACCEPTABLE"),
            "partial_route": sum(1 for r in w4_route.values()
                                 if r["verdict"] == "PARTIAL"),
            "no_acceptable_route": sum(1 for r in w4_route.values()
                                       if r["verdict"] == "NO_ACCEPTABLE_ROUTE"),
            "unresolved": sum(1 for r in w4_route.values()
                              if r["verdict"] == "UNRESOLVED"),
            "structured_route_cases": len(emitters),
            "structured_route_cases_all_120": len(emitters),
            "structured_route_entries": adapter_data["routes_total"],
            "service_identities": adapter_data["service_identities"],
            "evaluable_routes": adapter_data["evaluable_routes"],
            "access_bound": adapter_data["access_bound"],
            "condition_bound": adapter_data["condition_bound"],
            "evidence_joins_found": adapter_data["evidence_joins_found"],
            "evidence_joins_missing": adapter_data["evidence_joins_missing"],
            "no_route_asserted_cases": adapter_data["no_route_asserted_cases"],
            "presented_as_complete_cases":
                adapter_data["presented_as_complete_cases"]},
        "stage_counts": dict(sorted(stage_counts.items())),
        "funnel_note": (
            "Wave-4 endpoint unchanged from the Wave-3 compatibility bridge: "
            "0 route PASS, 108 route FAIL (106 NO_ACCEPTABLE_ROUTE, 2 PARTIAL). "
            "Structured emission is present (62 emitter cases, 125 entries, all "
            "access- and condition-bound) but evidence joins remain 0/125, so "
            "binding (RC-04) and the lexical route scorer (MS-06) still block "
            "every route PASS. The two PARTIAL verdicts remain the frozen "
            "token-substring artifacts ROUT-040 and ROUT-061 (MS-04/MS-05).")}

    classification = {
        "artifact": "wave4-resume-route-failure-stage-classification",
        "task_id": TASK_ID,
        "created_utc": funnel["created_utc"],
        "classification": "BURNED_DEV_BASELINE_ONLY",
        "row_count": len(rows),
        "stage_counts": dict(sorted(stage_counts.items())),
        "stage_legend": {
            "R0_NO_STRUCTURED_ROUTE": "no structured route object emitted for the case",
            "R1_INVALID_ROUTE_OBJECT": "route object malformed, junk, or label mismatch",
            "R2_WRONG_TRACK": "route targets the wrong age/authority track",
            "R3_WRONG_SERVICE_FAMILY": "adjacent or wrong service family vs gold",
            "R4_WRONG_ACCESS_PATH": "wrong referral/access path for the family",
            "R5_MISSING_OR_WRONG_CONDITION": "family correct, condition/qualifier wrong",
            "R6_PROVENANCE_OR_EVIDENCE": "route present but evidence join missing/broken",
            "R7_EPISTEMIC_COLLAPSE": "uncertainty collapsed so route not evaluable",
            "R8_RENDERING_MISMATCH": "correct semantics rendered unmatchably",
            "R9_MEASUREMENT_SENSITIVITY": "frozen scorer cannot recognize correct product behavior",
            "R10_OTHER": "residual bucket"},
        "rows": rows,
        "documentation_note": ("Stage sets R1/R3/R5 carry over the frozen Wave-3 "
                               "close-out route-lane audit; R0/R6 derive "
                               "mechanically from frozen predictions and the "
                               "frozen route-adapter analysis. Case IDs are "
                               "analysis documentation only; no runtime code "
                               "consumes this classification.")}
    with open(os.path.join(HERE, "routing-funnel.json"), "w",
              encoding="utf-8") as f:
        json.dump(funnel, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(HERE, "route-failure-stage-classification.json"),
              "w", encoding="utf-8") as f:
        json.dump(classification, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Section 21 + regression inventory (primary comparison = product effect)
    dims = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        w4v = [str(r["verdict"]) for _, r in rows_of(w4) if r["dimension"] == dim]
        dims[dim] = dict(collections.Counter(w4v))
    inventory = {
        "artifact": "wave4-resume-regression-inventory", "task_id": TASK_ID,
        "created_utc": funnel["created_utc"],
        "comparison": "PRIMARY Wave3 compat bridge -> Wave 4 (section 18B)",
        "regression_definition":
            "A criterion whose new semantic state is strictly worse than its "
            "old state under frozen semantics. FAIL->UNRESOLVED is fail-closed "
            "lateral movement, not a regression.",
        "regression_count": len(product["regressed_criteria"]),
        "regressions": product["regressed_criteria"],
        "improvement_count": len(product["improved_criteria"]),
        "lateral_count": product["lateral_count"],
        "lateral_fail_closed_transitions": {
            "count": len(product["lateral_criteria"]),
            "note": "listed in wave3bridge-wave4-transition-matrix.json"},
        "severity_legend": {"P0": "safety-critical", "P1": "material route/semantic",
                            "P2": "evidence/uncertainty", "P3": "presentation/other"},
        "dimension_results": dims,
        "ms_sensitivity_observations": {
            "MS-01": {"status": "STILL_INDICATED", "basis":
                      "generic PREMATURE_ABSENCE evidence markers present in Wave-4 rows"},
            "MS-02": {"status": "STILL_INDICATED", "basis":
                      "CRITICAL_CONDITION_MAP unchanged; free-text conditions remain unmapped"},
            "MS-03": {"status": "HISTORICAL_SINGLE_CASE", "basis":
                      "ROUT-069 null-condition representation; no new transition observed"},
            "MS-04": {"status": "STILL_INDICATED", "basis":
                      "ROUT-040 PARTIAL token-substring artifact unchanged"},
            "MS-05": {"status": "STILL_INDICATED", "basis":
                      "ROUT-061 PARTIAL token-substring artifact unchanged"},
            "MS-06": {"status": "STILL_INDICATED", "basis":
                      "route PASS 0/108; lexical label-vs-proposition matching unchanged"}},
        "RC-04": {"status": "STILL_INDICATED", "basis":
                  "evidence joins 0/125 route entries; label-to-evidence binding unresolvable"},
        "RC-06": {"status": "STILL_INDICATED", "basis":
                  "multi-block national-information and presented_as_complete patterns unchanged "
                  "(see presentation counts in routing-funnel.json)"}}
    with open(os.path.join(HERE, "regression-inventory.json"), "w",
              encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(json.dumps({
        "adapter": {k: adapter["delta_report"][k] for k in
                    ("old_states", "new_states", "old_failure_rate", "new_failure_rate")},
        "adapter_state_transitions": adapter["semantic_state_transitions"],
        "product": {k: product["delta_report"][k] for k in
                    ("old_states", "new_states", "old_failure_rate", "new_failure_rate")},
        "product_state_transitions": product["semantic_state_transitions"],
        "product_regressions": len(product["regressed_criteria"]),
        "product_improvements": len(product["improved_criteria"]),
        "product_lateral": len(product["lateral_criteria"]),
        "cumulative": {k: cumulative["delta_report"][k] for k in
                       ("old_states", "new_states", "old_failure_rate", "new_failure_rate")},
        "stage_counts": dict(sorted(stage_counts.items()))}, indent=1))


if __name__ == "__main__":
    main()
