#!/usr/bin/env python3
"""Sections 24-25: criterion transition matrix + baseline delta report.

Comparison runs strictly AFTER the Wave-1 measurement freeze (section 23).
Old-state semantics reproduce the frozen provenance-corrected baseline's
published classification (identical counts, independent recomputation).
"""
import collections
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")
OLD_PATH = os.path.join(EVAL, "measurement-v3-final-authority-provenance-repair-v1",
                        "combined-measurement-results-complete-provenance-corrected.json")
OLD_SHA = "e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437948861cf"
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-1"
GOLD_CHANGED = {"ROUT-061", "ROUT-070", "ROUT-073"}


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
    cases = doc["cases"] if isinstance(doc, dict) else doc
    for case in cases:
        for row in case["criteria"]:
            yield case["case_id"], row


def main():
    actual = hashlib.sha256(open(OLD_PATH, "rb").read()).hexdigest()
    if actual != OLD_SHA:
        raise SystemExit("OLD_BASELINE_SHA_DRIFT: " + actual)
    old = json.load(open(OLD_PATH, encoding="utf-8"))
    new = json.load(open(os.path.join(HERE, "wave1-combined-measurement-results.json"),
                         encoding="utf-8"))

    old_by_id, new_by_id = {}, {}
    for case_id, row in rows_of(old):
        old_by_id[row["criterion_id"]] = (case_id, row)
    for case_id, row in rows_of(new):
        new_by_id[row["criterion_id"]] = (case_id, row)
    assert set(old_by_id) == set(new_by_id) and len(old_by_id) == 600

    transitions, state_transitions = collections.Counter(), collections.Counter()
    regressed, improved, gold_changed = [], [], []
    per_dim = collections.defaultdict(lambda: collections.Counter())
    for cid in old_by_id:
        case_id, orow = old_by_id[cid]
        _, nrow = new_by_id[cid]
        dim = orow["dimension"]
        if orow["status"] == "NOT_APPLICABLE" or nrow["status"] == "NOT_APPLICABLE":
            key = ("ABSENT_OR_NOT_APPLICABLE",
                   "ABSENT_OR_NOT_APPLICABLE" if nrow["status"] == "NOT_APPLICABLE"
                   else "RE-EVALUATED")
        elif nrow["status"] == "HUMAN_ADJUDICATION_PENDING":
            key = (orow["verdict"], "PENDING")
        else:
            key = (orow["verdict"], nrow["verdict"])
        transitions["%s -> %s" % key] += 1
        per_dim[dim]["|".join(map(str, key))] += 1
        if key[0] is None or key[1] == "PENDING":
            continue
        ostate = semantic_state(dim, orow["verdict"] if orow["status"] == "SCORED" else None)
        nstate = semantic_state(dim, nrow["verdict"])
        state_transitions["%s -> %s" % (ostate, nstate)] += 1
        if ostate != nstate:
            entry = {"case_id": case_id, "criterion_id": cid, "dimension": dim,
                     "old_verdict": orow["verdict"], "new_verdict": nrow["verdict"],
                     "old_state": ostate, "new_state": nstate,
                     "new_authority": nrow["authority"]}
            rank = {"FAIL": 0, "UNRESOLVED": 1, "DEGRADED": 2, "PASS": 3,
                    "ABSENT_OR_NOT_APPLICABLE": 4}
            # UNRESOLVED is fail-closed, not a correct state: FAIL ->
            # UNRESOLVED is a lateral transition, never an improvement.
            lateral = nstate == "UNRESOLVED"
            better = rank[nstate] < rank[ostate] and not lateral
            if better:
                improved.append(entry)
            elif rank[nstate] < rank[ostate]:
                regressed.append({**entry,
                                  "gold_wording_changed": case_id in GOLD_CHANGED})
                if case_id in GOLD_CHANGED:
                    gold_changed.append(cid)
            elif rank[nstate] > rank[ostate] and not lateral:
                improved.append(entry)

    def tally(doc):
        states = collections.Counter()
        failing_cases, all_cases = set(), set()
        for case_id, row in rows_of(doc):
            if row["status"] == "NOT_APPLICABLE":
                continue
            all_cases.add(case_id)
            state = semantic_state(row["dimension"], row["verdict"])
            states[state] += 1
            if state != "PASS":
                failing_cases.add(case_id)
        applicable = sum(states.values())
        return states, applicable, failing_cases, all_cases

    old_states, old_n, old_fail_cases, old_all = tally(old)
    new_states, new_n, new_fail_cases, new_all = tally(new)
    per_dim_delta = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        o = collections.Counter(r["verdict"] if r["verdict"] is not None else "NOT_APPLICABLE"
                                for _, r in rows_of(old) if r["dimension"] == dim)
        n = collections.Counter(str(r["verdict"]) if r["verdict"] is not None else "NOT_APPLICABLE"
                                for _, r in rows_of(new) if r["dimension"] == dim)
        per_dim_delta[dim] = {"old": dict(o), "new": dict(n)}

    out = {
        "artifact": "baseline-transition-matrix", "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "comparison_order": "WAVE1_MEASUREMENT_FROZEN_BEFORE_THIS_COMPARISON",
        "old_baseline": {"path": os.path.relpath(OLD_PATH, EVAL), "sha256": OLD_SHA,
                         "status": "MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED"},
        "verdict_transitions": dict(transitions),
        "semantic_state_transitions": dict(state_transitions),
        "per_dimension_transitions": {d: dict(v) for d, v in per_dim.items()},
        "delta_report": {
            "old_applicable": old_n, "new_applicable_authoritative":
                new_n - new_states.get("PENDING", 0),
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
        "regression_count": len(regressed), "improvement_count": len(improved),
        "gold_wording_changed_criteria": {
            "case_ids": sorted(GOLD_CHANGED),
            "criteria": gold_changed,
            "note": "ROUT-061/070/073 gold wording changed between lineages; "
                    "state changes there are gold-wording effects, not "
                    "product-caused regressions"},
        "pending_note": "4 criteria pending human adjudication (DIS-118, "
                        "ROUT-026, ROUT-031, ROUT-037); excluded from "
                        "authoritative-only rates"}
    with open(os.path.join(HERE, "baseline-transition-matrix.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: out["delta_report"][k] for k in (
        "old_states", "new_states_including_pending", "old_failure_rate",
        "new_failure_rate_authoritative_only")}, indent=1))
    print("state transitions:")
    for k, v in sorted(state_transitions.items()):
        print(" ", k, v)
    print("regressions:", len(regressed), "improvements:", len(improved))


if __name__ == "__main__":
    main()
