"""Stage 3 combined integration test: 150 synthetic mixed-workflow fixtures.
Gates: routing 100%, no authority overlap 100%, fail-closed 100%, provenance
100%, leakage 0, reporting arithmetic 100%. Deterministic rerun stability.
No model calls."""
import hashlib
import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from combined_measurement_v3 import (  # noqa: E402
    FORBIDDEN_ITEM_KEYS, RESPONSIBILITY_MAP, combined_report, provenance_complete_review,
    run_item, route)


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return json.load(f)


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    data = load("integration-fixtures-v3.json")
    fixtures = data["fixtures"]
    assert len(fixtures) == 150
    results = []
    failures = {"routing": [], "overlap": [], "fail_closed": [], "provenance": [],
                "leakage": [], "expectation": []}
    for fx in fixtures:
        try:
            res = run_item(fx)
        except Exception as exc:  # any unhandled engine exception is an execution failure
            res = {"item_id": fx["item_id"], "workflow": fx["workflow"],
                   "status": "EXECUTION_FAILURE", "error": repr(exc),
                   "authoritative_owner": None}
        results.append(res)

        # routing: exactly one owner, matching the frozen workflow map
        got_owner = res.get("authoritative_owner")
        if fx["workflow"] == "scorer":
            # Deterministic items may escalate to the generic lane; the owner
            # must match the escalation outcome in either branch.
            expected = ("GENERIC_LANE_V2_15" if res.get("escalated")
                        else "DETERMINISTIC_SCORER_V1")
            owner_ok = got_owner == expected
        else:
            owner = None
            try:
                owner = route(fx)
            except Exception:
                pass
            owner_ok = owner is not None and got_owner == owner
        if not owner_ok:
            failures["routing"].append(fx["item_id"])
        # no authority overlap: deterministic finals must not carry lane records;
        # human-lane items must never produce automated semantic verdicts
        if got_owner == "DETERMINISTIC_SCORER_V1" and res.get("review_record"):
            failures["overlap"].append(fx["item_id"])
        if got_owner in ("M2_LANE_V2_6", "GENERIC_LANE_V2_15"):
            rec = res.get("record") or {}
            if rec.get("review_mode") == "AUTOMATED" or res.get("automated_semantic_final"):
                failures["overlap"].append(fx["item_id"])
        # leakage: no forbidden keys reached any stored record
        blob = json.dumps(res, sort_keys=True)
        for bad in FORBIDDEN_ITEM_KEYS:
            if '"' + bad + '":' in blob and bad != "expected":
                failures["leakage"].append({"item": fx["item_id"], "field": bad})
        # fail-closed: pending/invalid/disagreement must have no final
        if res["status"] in ("HUMAN_REVIEW_PENDING", "HUMAN_REVIEW_INVALID",
                             "HUMAN_REVIEW_DISAGREEMENT") and res.get("final"):
            failures["fail_closed"].append(fx["item_id"])
        # provenance completeness for lane records
        rec = res.get("record")
        if rec and not provenance_complete_review(rec):
            failures["provenance"].append(fx["item_id"])
        # expectations
        exp = fx.get("expect", {})
        if exp.get("status") and res["status"] != exp["status"]:
            failures["expectation"].append({"item": fx["item_id"],
                                            "expected": exp["status"],
                                            "got": res["status"]})
            continue
        if exp.get("status") == "HUMAN_REVIEW_RESOLVED":
            if exp.get("any_final"):
                if not res.get("final"):
                    failures["expectation"].append({"item": fx["item_id"],
                                                    "expected": "any final", "got": None})
            elif exp.get("final") is not None and res.get("final") != exp["final"]:
                failures["expectation"].append({"item": fx["item_id"],
                                                "expected": exp["final"],
                                                "got": res.get("final")})

    # deterministic scorer finals need no provenance check beyond scorer notes
    report = combined_report(results)

    # reporting arithmetic: all buckets sum to n_items
    total = (report["deterministic_criteria"]["scored_final"]
             + report["human_reviewed_criteria"]["resolved"] + report["review_pending"]
             + report["review_invalid"] + report["review_disagreement"]
             + report["execution_failure"])
    arithmetic_ok = total == report["n_items"] == 150

    # rerun stability
    sig1 = json.dumps([{k: res.get(k) for k in ("item_id", "status", "final")}
                       for res in results], sort_keys=True)
    results2 = []
    for fx in fixtures:
        try:
            res = run_item(fx)
        except Exception as exc:
            res = {"item_id": fx["item_id"], "status": "EXECUTION_FAILURE", "error": repr(exc)}
        results2.append({k: res.get(k) for k in ("item_id", "status", "final")})
    sig2 = json.dumps(results2, sort_keys=True)
    rerun_stable = sig1 == sig2

    gates = {
        "routing_100": not failures["routing"],
        "no_authority_overlap_100": not failures["overlap"],
        "fail_closed_100": not failures["fail_closed"],
        "provenance_100": not failures["provenance"],
        "leakage_0": not failures["leakage"],
        "reporting_arithmetic_100": arithmetic_ok,
        "deterministic_rerun_stable": rerun_stable,
        "expectations_100": not failures["expectation"],
        "no_automated_semantic_verdicts": (report["automated_semantic_criteria"]["present"] is False),
    }
    out = {"artifact": "integration-results-v3",
           "task_id": "NAV-EXPLORE-MEASUREMENT-V3-COMBINED-FREEZE",
           "n_fixtures": 150, "gates": gates, "gate_names_failing":
           [k for k, v in gates.items() if not v], "failures": failures,
           "report": report, "results": results}
    with open(os.path.join(DIR, "integration-results-v3.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("gates:", {k: v for k, v in gates.items()})
    print("integration:", "PASS" if all(gates.values()) else "FAIL")
    sys.exit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
