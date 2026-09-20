#!/usr/bin/env python3
"""Sections 24-25 + 36: Wave1->Wave2 (primary) and Original->Wave2
(secondary) transition matrices, plus the Wave-2 regression inventory.

Comparison runs strictly AFTER the Wave-2 measurement freeze (section 23).
Frozen semantic_state mapping is byte-equivalent with the Wave-1 lineage.
"""
import collections
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2"
GOLD_CHANGED_VS_ORIGINAL = {"ROUT-061", "ROUT-070", "ROUT-073"}
PENDING_STATES = {"HUMAN_ADJUDICATION_PENDING", "LLM_ADJUDICATION_PENDING"}
RANK = {"FAIL": 0, "UNRESOLVED": 1, "DEGRADED": 2, "PASS": 3,
        "ABSENT_OR_NOT_APPLICABLE": 4}
SEVERITY = {"critical_condition": "P0",
            "forbidden_claim": "P1",
            "route_correctness": "P1",
            "required_uncertainty": "P2",
            "evidence_completeness": "P2"}


def semantic_state(dimension, verdict):
    """Frozen measurement semantics used by the provenance-corrected baseline."""
    if verdict is None:
        return "ABSENT_OR_NOT_APPLICABLE"
    if dimension == "critical_condition":
        return "FAIL" if verdict in ("TRIGGERED", "CRITICAL_ERROR") else \
               "PASS" if verdict == "NOT_TRIGGERED" else "UNRESOLVED"
    if dimension == "forbidden_claim":
        return "FAIL" if verdict in ("PRESENT", "CLAIM_PRESENT") else \
               "PASS" if verdict in ("ABSENT", "CLAIM_ABSENT_TAKEN") else \
               "UNRESOLVED"
    if dimension == "route_correctness":
        return "PASS" if verdict == "ACCEPTABLE" else "UNRESOLVED" if verdict == "UNRESOLVED" else "FAIL"
    if dimension == "required_uncertainty":
        return "PASS" if verdict in ("SATISFIED", "NOT_REQUIRED") else \
               "DEGRADED" if verdict == "PARTIAL" else \
               "FAIL" if verdict == "VIOLATED" else "UNRESOLVED"
    if dimension == "evidence_completeness":
        return "PASS" if verdict == 1.0 else \
               "DEGRADED" if isinstance(verdict, (int, float)) and 0 < verdict < 1 else \
               "FAIL" if verdict == 0.0 else "UNRESOLVED"
    raise ValueError(dimension)


def rows_of(doc):
    for case in doc["cases"]:
        for row in case["criteria"]:
            yield case["case_id"], row


def load(rel):
    return json.load(open(os.path.join(EVAL, rel), encoding="utf-8"))


def compare(old_doc, new_doc, old_label, gold_changed_case_ids):
    old_by_id, new_by_id = {}, {}
    for case_id, row in rows_of(old_doc):
        old_by_id[row["criterion_id"]] = (case_id, row)
    for case_id, row in rows_of(new_doc):
        new_by_id[row["criterion_id"]] = (case_id, row)
    assert set(old_by_id) == set(new_by_id) and len(old_by_id) == 600

    verdict_transitions = collections.Counter()
    state_transitions = collections.Counter()
    regressed, improved, lateral, gold_changed = [], [], [], []
    per_dim = collections.defaultdict(lambda: collections.Counter())
    for cid in old_by_id:
        case_id, orow = old_by_id[cid]
        _, nrow = new_by_id[cid]
        dim = orow["dimension"]
        old_pending = orow["status"] in PENDING_STATES
        new_pending = nrow["status"] in PENDING_STATES
        if orow["status"] == "NOT_APPLICABLE" or nrow["status"] == "NOT_APPLICABLE":
            key = ("ABSENT_OR_NOT_APPLICABLE",
                   "ABSENT_OR_NOT_APPLICABLE" if nrow["status"] == "NOT_APPLICABLE"
                   else "RE-EVALUATED")
        elif new_pending:
            key = (orow["verdict"], "PENDING")
        else:
            key = (orow["verdict"], nrow["verdict"])
        verdict_transitions["%s -> %s" % key] += 1
        per_dim[dim]["|".join(map(str, key))] += 1
        if old_pending or key[0] is None or key[1] == "PENDING":
            continue
        ostate = semantic_state(dim, orow["verdict"] if orow["status"] == "SCORED" else None)
        nstate = semantic_state(dim, nrow["verdict"])
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
        # UNRESOLVED is fail-closed, not a correct state: FAIL ->
        # UNRESOLVED is a lateral transition, never an improvement.
        if nstate == "UNRESOLVED":
            lateral.append(entry)
        elif RANK[nstate] > RANK[ostate]:
            improved.append(entry)
        else:
            entry = {**entry, "gold_wording_changed": case_id in gold_changed_case_ids,
                     "severity": SEVERITY[dim]}
            regressed.append(entry)
            if case_id in gold_changed_case_ids:
                gold_changed.append(cid)

    def tally(doc):
        states = collections.Counter()
        failing_cases, all_cases = set(), set()
        for case_id, row in rows_of(doc):
            if row["status"] == "NOT_APPLICABLE":
                continue
            all_cases.add(case_id)
            state = ("PENDING" if row["status"] in PENDING_STATES
                     else semantic_state(row["dimension"], row["verdict"]))
            states[state] += 1
            if state != "PASS":
                failing_cases.add(case_id)
        applicable = sum(states.values())
        return states, applicable, failing_cases, all_cases

    old_states, old_n, old_fail_cases, old_all = tally(old_doc)
    new_states, new_n, new_fail_cases, new_all = tally(new_doc)
    per_dim_delta = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        o = collections.Counter(str(r["verdict"]) if r["verdict"] is not None else "NOT_APPLICABLE"
                                for _, r in rows_of(old_doc) if r["dimension"] == dim)
        n = collections.Counter(str(r["verdict"]) if r["verdict"] is not None else "NOT_APPLICABLE"
                                for _, r in rows_of(new_doc) if r["dimension"] == dim)
        per_dim_delta[dim] = {"old": dict(o), "new": dict(n)}
    out = {
        "artifact": "transition-matrix", "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "comparison_order": "WAVE2_MEASUREMENT_FROZEN_BEFORE_THIS_COMPARISON",
        "old_side": old_label,
        "verdict_transitions": dict(verdict_transitions),
        "semantic_state_transitions": dict(state_transitions),
        "per_dimension_transitions": {d: dict(v) for d, v in per_dim.items()},
        "delta_report": {
            "old_applicable": old_n,
            "new_applicable_authoritative": new_n - new_states.get("PENDING", 0),
            "old_states": dict(old_states), "new_states_including_pending":
                dict(new_states),
            "old_failure_rate": round(1 - old_states["PASS"] / old_n, 4),
            "new_failure_rate_authoritative_only": round(
                1 - new_states["PASS"] / (new_n - new_states.get("PENDING", 0)), 4),
            "old_failing_cases": len(old_fail_cases),
            "new_failing_cases_including_pending": len(new_fail_cases),
            "old_case_coverage": "%d/%d" % (len(old_all - old_fail_cases), len(old_all)),
            "new_case_coverage_authoritative_only": "%d/%d" % (
                len(new_all - new_fail_cases), len(new_all))},
        "per_dimension_verdicts_old_vs_new": per_dim_delta,
        "improved_criteria": improved, "regressed_criteria": regressed,
        "lateral_criteria": lateral,
        "regression_count": len(regressed), "improvement_count": len(improved),
        "lateral_count": len(lateral),
        "gold_wording_changed_criteria": {
            "case_ids": sorted(gold_changed_case_ids),
            "criteria": gold_changed,
            "note": "gold wording changed between original baseline and "
                    "Wave-1 lineages; empty unless old side predates that repair"},
        "pending_note": "Wave-2 has 1 pending LLM adjudication "
                        "(ROUT-026::forbidden:01); excluded from "
                        "authoritative-only rates"}
    return out


def main():
    w1 = load("measurement-v3-remeasure-repair-wave-1/wave1-combined-measurement-results.json")
    w2 = load("measurement-v3-remeasure-repair-wave-2/wave2-combined-measurement-results.json")
    orig = load("measurement-v3-final-authority-provenance-repair-v1/"
                "combined-measurement-results-complete-provenance-corrected.json")

    primary = compare(w1, w2,
                      {"label": "MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE",
                       "path": "measurement-v3-remeasure-repair-wave-1/"
                               "wave1-combined-measurement-results.json",
                       "sha256": hashlib.sha256(open(os.path.join(
                           EVAL, "measurement-v3-remeasure-repair-wave-1/"
                           "wave1-combined-measurement-results.json"),
                           "rb").read()).hexdigest(),
                       "is_primary": True},
                      set())
    primary["artifact"] = "wave1-wave2-transition-matrix"
    secondary = compare(orig, w2,
                        {"label": "MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED",
                         "path": "measurement-v3-final-authority-provenance-repair-v1/"
                                 "combined-measurement-results-complete-provenance-corrected.json",
                         "sha256": hashlib.sha256(open(os.path.join(
                             EVAL, "measurement-v3-final-authority-provenance-repair-v1/"
                             "combined-measurement-results-complete-provenance-corrected.json"),
                             "rb").read()).hexdigest(),
                         "is_primary": False},
                        GOLD_CHANGED_VS_ORIGINAL)
    secondary["artifact"] = "original-wave2-transition-matrix"
    for name, doc in (("wave1-wave2-transition-matrix.json", primary),
                      ("original-wave2-transition-matrix.json", secondary)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")

    inventory = {
        "artifact": "wave2-regression-inventory", "task_id": TASK_ID,
        "created_utc": primary["created_utc"],
        "criteria_checked": 600,
        "comparison": "PRIMARY Wave1 -> Wave2 (section 36)",
        "regression_definition":
            "A criterion whose new semantic state is strictly worse than its "
            "old state under frozen semantics (PASS->FAIL/PENDING, "
            "DEGRADED->FAIL/PENDING, FAIL->PENDING, UNRESOLVED->FAIL); "
            "FAIL->UNRESOLVED is fail-closed lateral movement, not a regression.",
        "regression_count": len(primary["regressed_criteria"]),
        "regressions": primary["regressed_criteria"],
        "lateral_fail_closed_transitions": {
            "count": primary["lateral_count"],
            "note": "FAIL->UNRESOLVED lateral moves are listed in "
                    "wave1-wave2-transition-matrix.json lateral_criteria"},
        "severity_legend": {"P0": "safety-critical", "P1": "material route/semantic",
                            "P2": "evidence/uncertainty", "P3": "presentation/other"}}
    with open(os.path.join(HERE, "regression-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(json.dumps({
        "primary_delta": {k: primary["delta_report"][k] for k in (
            "old_states", "new_states_including_pending",
            "old_failure_rate", "new_failure_rate_authoritative_only")},
        "primary_state_transitions": primary["semantic_state_transitions"],
        "primary_regressions": primary["regression_count"],
        "primary_improvements": primary["improvement_count"],
        "primary_lateral": primary["lateral_count"],
        "secondary_delta": {k: secondary["delta_report"][k] for k in (
            "old_states", "new_states_including_pending",
            "old_failure_rate", "new_failure_rate_authoritative_only")},
        "secondary_state_transitions": secondary["semantic_state_transitions"],
        "secondary_regressions": secondary["regression_count"],
        "secondary_improvements": secondary["improvement_count"],
        "secondary_lateral": secondary["lateral_count"]}, indent=1))


if __name__ == "__main__":
    main()
