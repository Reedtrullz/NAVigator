#!/usr/bin/env python3
"""Build complete Wave-1 results, aggregates, and transition matrix.

Mechanical continuation of the comparator repair: replace only the four
PENDING_HUMAN_ADJUDICATION rows with the corrected-rule consensus rows, keep
the other 596 rows byte-identical, recompute aggregates with the frozen
semantic_state mapping, and diff against the old provenance-corrected
baseline. Zero LLM calls."""
import hashlib
import json
import os
import time
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")
UPSTREAM = os.path.join(EVAL, "measurement-v3-wave1-residual-llm-adjudication-v1")
OLD_BASELINE = os.path.join(
    EVAL, "measurement-v3-final-authority-provenance-repair-v1",
    "combined-measurement-results-complete-provenance-corrected.json")
CORE_PATH = os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist",
                         "judge_core_v2_13.py")
OLD_BASELINE_SHA = ("e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437"
                    "948861cf")
UPSTREAM_RESULTS = "wave1-remeasurement-complete-after-secondary-residual.json"
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1"


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


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
                else "DEGRADED" if isinstance(verdict, (int, float)) and 0 < verdict < 1
                else "FAIL" if verdict == 0.0 else "UNRESOLVED")
    raise ValueError(dimension)


def iter_rows(doc):
    for c in doc["cases"]:
        for r in c["criteria"]:
            yield c, r


def row_key(r):
    return r["criterion_id"]


def core_state_counts(doc):
    states = collections.Counter()
    applicable = 0
    for _, r in iter_rows(doc):
        st = semantic_state(r["dimension"], r["verdict"])
        states[st] += 1
        if r["verdict"] is not None:
            applicable += 1
    out = dict(states)
    out["APPLICABLE_DENOMINATOR"] = applicable
    fail = states.get("FAIL", 0)
    nonpass = fail + states.get("UNRESOLVED", 0) + states.get("DEGRADED", 0)
    out["HARD_FAIL_RATE_AUTHORITATIVE"] = round(fail / applicable, 4) if applicable else None
    out["NON_PASS_RATE_AUTHORITATIVE"] = round(nonpass / applicable, 4) if applicable else None
    out["NOTE"] = ("authoritative scored rows only; rows with verdict=None are "
                   "ABSENT_OR_NOT_APPLICABLE and excluded from the denominator")
    return out


def comparison_packets_shas(comparison, pid):
    for e in comparison["packets"]:
        if e["packet_id"] == pid:
            return e["observation_record_shas"]
    raise KeyError(pid)


def compute_coverage(doc, new_rows):
    counts = collections.Counter(r["authority"] for _, r in iter_rows(doc))
    counts["LLM_ADJUDICATED"] += len(new_rows)
    counts.pop("PENDING_HUMAN_ADJUDICATION", None)
    total = sum(counts.values())
    return {"TOTAL_CRITERIA": total,
            "DETERMINISTIC": counts.get("DETERMINISTIC", 0),
            "LLM_REVIEWED": counts.get("LLM_REVIEWED", 0),
            "LLM_ADJUDICATED": counts.get("LLM_ADJUDICATED", 0),
            "HUMAN_REVIEWED": counts.get("HUMAN_REVIEWED", 0),
            "PENDING_HUMAN_ADJUDICATION": 0,
            "AUTHORITATIVE_TOTAL": total,
            "AUTHORITATIVE_PCT": 100.0}


def recount_verdicts(doc, new_rows):
    vc = collections.Counter()
    for _, r in iter_rows(doc):
        key = r["verdict"]
        if r["authority"] == "PENDING_HUMAN_ADJUDICATION":
            key = new_rows[row_key(r)]["verdict"]
        vc[key] += 1
    return dict(vc)


def rebuild_cases(doc, new_rows):
    cases = []
    for c in doc["cases"]:
        crit = [new_rows.get(row_key(r), r) for r in c["criteria"]]
        cases.append({"case_id": c["case_id"], "corpus": c["corpus"],
                      "prediction_sha256": c["prediction_sha256"],
                      "criteria": crit})
    return cases


def main():
    up = json.load(open(os.path.join(UPSTREAM, UPSTREAM_RESULTS), encoding="utf-8"))
    old = json.load(open(OLD_BASELINE, encoding="utf-8"))
    assert sha_file(OLD_BASELINE) == OLD_BASELINE_SHA
    derived = json.load(open(os.path.join(HERE, "derived-residual-results.json"), encoding="utf-8"))
    comparison = json.load(open(os.path.join(HERE, "semantic-consensus-comparison.json"), encoding="utf-8"))
    assert comparison["summary"]["authoritative_fields_consensus"] == 4
    core_sha = sha_file(CORE_PATH)
    by_pid = {r["packet_id"]: r for r in derived["derived_rows"]}
    new_rows = {}
    for c, r in iter_rows(up):
        if r["authority"] != "PENDING_HUMAN_ADJUDICATION":
            continue
        d = by_pid[r["packet_id"]]
        assert d["derived_verdict"] is not None
        new_rows[row_key(r)] = build_authoritative_row(r, d, comparison, core_sha)
    assert len(new_rows) == 4
    complete = {
        "artifact": "complete-wave1-measurement-results",
        "task_id": TASK_ID,
        "created_utc": now_utc(),
        "upstream_artifact": UPSTREAM_ID + UPSTREAM_RESULTS,
        "upstream_artifact_sha256": sha_file(os.path.join(UPSTREAM, UPSTREAM_RESULTS)),
        "old_baseline_artifact": OLD_BASELINE_ID,
        "old_baseline_sha256": OLD_BASELINE_SHA,
        "rows_changed_from_upstream": len(new_rows),
        "row_diff_rule": "only PENDING_HUMAN_ADJUDICATION rows replaced; all other rows byte-identical",
        "coverage": compute_coverage(up, new_rows),
        "verdict_counts": recount_verdicts(up, new_rows),
        "cases": rebuild_cases(up, new_rows),
        "comparator_repair": comparator_repair_meta(),
    }
    complete["semantic_state_counts_recomputed"] = core_state_counts(complete)
    return analyze_and_write(complete, old, up, new_rows)


def build_authoritative_row(r, d, comparison, core_sha):
    shas = d.get("observation_record_shas") or comparison_packets_shas(comparison, r["packet_id"])
    return {
        "case_id": r["case_id"],
        "criterion_id": r["criterion_id"],
        "dimension": r["dimension"],
        "authority": "LLM_ADJUDICATED",
        "status": "SCORED",
        "verdict": d["derived_verdict"],
        "evidence": d["evidence_spans"],
        "provenance": {
            "observation_source": "SECONDARY_SOL_RESIDUAL_DUAL_PASS_PRIMITIVE_CONSENSUS",
            "observation_model": "gpt-5.6-sol",
            "reasoning_effort": "low",
            "observation_record_shas": shas,
            "consensus_rule": "AUTHORITATIVE_FIELDS_PRIMITIVE_CONSENSUS (comparator repair V1; whole-object A==B superseded as task-local implementation defect)",
            "comparator_replay_artifact": "evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/semantic-consensus-comparison.json",
            "derivation_rule": "judge_core_v2_13.derive_final",
            "derivation_basis": d["derivation_basis"],
            "derivation_core_sha256": core_sha,
        },
        "packet_id": r["packet_id"],
        "packet_sha256": r["packet_sha256"],
    }


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


UPSTREAM_ID = "evaluation/measurement-v3-wave1-residual-llm-adjudication-v1/"
OLD_BASELINE_ID = "evaluation/measurement-v3-final-authority-provenance-repair-v1/combined-measurement-results-complete-provenance-corrected.json"
REPLAY_ID = "evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/semantic-consensus-comparison.json"


def comparator_repair_meta():
    return {
        "classification": "CONSENSUS_COMPARATOR_IMPLEMENTATION_DEFECT",
        "branch": "A",
        "consensus_rule": "AUTHORITATIVE_FIELDS_PRIMITIVE_CONSENSUS",
        "new_llm_calls": 0,
        "semantic_observations_changed": False,
        "derived_from": "derived-residual-results.json (frozen judge_core_v2_13.derive_final)",
    }


def write_json(name, obj):
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def fmt(v):
    return "NONE" if v is None else str(v)


def snapshot(doc):
    snap = {}
    for c, r in iter_rows(doc):
        snap[row_key(r)] = {
            "case_id": c["case_id"],
            "dimension": r["dimension"],
            "verdict": r["verdict"],
            "state": semantic_state(r["dimension"], r["verdict"]),
            "authority": r["authority"],
        }
    return snap


def build_transitions(old, complete):
    o, n = snapshot(old), snapshot(complete)
    assert set(o) == set(n)
    t = {"verdict": collections.Counter(), "states": collections.Counter(),
         "per_dimension": {}, "authority": collections.Counter(),
         "changed_verdict_rows": [], "improved": [], "regressed": []}
    for k in sorted(o):
        a, b = o[k], n[k]
        pair = fmt(a["verdict"]) + " -> " + fmt(b["verdict"])
        t["verdict"][pair] += 1
        t["states"][a["state"] + " -> " + b["state"]] += 1
        dim = t["per_dimension"].setdefault(a["dimension"], collections.Counter())
        dim[pair] += 1
        if a["verdict"] != b["verdict"]:
            t["changed_verdict_rows"].append(k)
        if a["authority"] != b["authority"]:
            t["authority"][a["authority"] + " -> " + b["authority"]] += 1
        if a["state"] == "FAIL" and b["state"] in ("PASS", "DEGRADED"):
            t["improved"].append(k)
        if a["state"] in ("PASS", "DEGRADED") and b["state"] == "FAIL":
            t["regressed"].append(k)
    t["verdict"] = dict(sorted(t["verdict"].items()))
    t["states"] = dict(sorted(t["states"].items()))
    t["authority"] = dict(sorted(t["authority"].items()))
    t["per_dimension"] = {d: dict(sorted(c.items()))
                          for d, c in sorted(t["per_dimension"].items())}
    return t


def build_aggregate_metrics(complete, t):
    states = complete["semantic_state_counts_recomputed"]
    per_dim = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        rows = [r for _, r in iter_rows(complete) if r["dimension"] == dim]
        per_dim[dim] = {
            "total_criteria": len(rows),
            "authoritative": sum(1 for r in rows if r["verdict"] is not None),
            "pending": sum(1 for r in rows if r["verdict"] is None),
            "verdict_distribution": dict(sorted(collections.Counter(
                fmt(r["verdict"]) for r in rows).items())),
        }
    return {
        "artifact": "complete-wave1-aggregate-metrics",
        "task_id": TASK_ID,
        "created_utc": now_utc(),
        "baseline_label": "BURNED_DEV_BASELINE_ONLY",
        "interpretation_boundary": (
            "comparator repair completes the Wave-1 measurement for the burned "
            "dev baseline only; not certification, production readiness, or "
            "generalization evidence"),
        "coverage": complete["coverage"],
        "semantic_state_counts": states,
        "per_dimension": per_dim,
        "authority_mix_honesty": (
            "508 deterministic, 88 LLM-reviewed (dual-pass Astra LOW "
            "consensus), 4 LLM-adjudicated (GPT-5.6-Sol dual-pass residual "
            "consensus via repaired comparator), 0 human-reviewed, 0 pending"),
        "delta_vs_old_baseline": {
            "changed_verdict_rows": t["changed_verdict_rows"],
            "improved_criteria": t["improved"],
            "regressed_criteria": t["regressed"],
        },
    }


def repair_wave_effects(new_rows, old_rows):
    rc01 = ["ROUT-026::forbidden:01", "ROUT-031::forbidden:01",
            "ROUT-037::forbidden:01"]
    rc02 = ["DIS-118::forbidden:01"]
    changed01 = [k for k in rc01
                 if old_rows[k]["verdict"] != new_rows[k]["verdict"]]
    changed02 = [k for k in rc02
                 if old_rows[k]["verdict"] != new_rows[k]["verdict"]]
    assert not changed01 and not changed02
    return {
        "RC-01_wave1_remeasure": {
            "rows_verdict_changed_in_this_repair": len(changed01),
            "rows_bound_to_repaired_comparator": 3,
            "criteria": ["ROUT-026::forbidden:01", "ROUT-031::forbidden:01",
                         "ROUT-037::forbidden:01"],
            "note": ("RC-01 remeasure rows previously ABSENT; corrected-rule "
                     "consensus confirms ABSENT, authority becomes "
                     "LLM_ADJUDICATED"),
        },
        "RC-02_residual_adjudication": {
            "rows_verdict_changed_in_this_repair": len(changed02),
            "rows_bound_to_repaired_comparator": 1,
            "criteria": ["DIS-118::forbidden:01"],
            "note": ("old row already LLM_ADJUDICATED PRESENT; corrected-rule "
                     "Sol consensus re-derives PRESENT via frozen kernel"),
        },
        "RC-03_structural": {
            "summary": ("prior remeasure showed structural emission improved "
                        "with 0 verdict-level route changes; unchanged here"),
        },
        "RC-03_semantic_routing": {
            "summary": ("prior remeasure showed 0 semantic routing verdict "
                        "changes (108/108 NO_ACCEPTABLE_ROUTE); unchanged "
                        "here"),
        },
    }


def verdict_counts(doc):
    return collections.Counter(
        fmt(r["verdict"]) for _, r in iter_rows(doc))


def analyze_and_write(complete, old, up, new_rows):
    # Repair diff vs upstream: only the 4 pending rows may differ.
    comp_rows = {row_key(r): r for _, r in iter_rows(complete)}
    up_rows = {row_key(r): r for _, r in iter_rows(up)}
    changed_vs_up = []
    for k, r in up_rows.items():
        if k in new_rows:
            changed_vs_up.append(k)
            assert comp_rows[k] == new_rows[k]
        else:
            assert comp_rows[k] == r
    assert sorted(changed_vs_up) == sorted(new_rows)
    delta = verdict_counts(complete)
    delta = {k: delta[k] - verdict_counts(up)[k]
             for k in set(verdict_counts(complete)) | set(verdict_counts(up))
             if delta[k] != verdict_counts(up)[k]}
    assert delta == {"ABSENT": 3, "PRESENT": 1, "NONE": -4}
    old_rows = {row_key(r): r for _, r in iter_rows(old)}
    assert all(old_rows[k]["verdict"] == new_rows[k]["verdict"]
               for k in new_rows)
    t = build_transitions(old, complete)
    auth_t = collections.Counter()
    for k in new_rows:
        a = old_rows[k]["authority"]
        b = new_rows[k]["authority"]
        if a != b:
            auth_t[a + " -> " + b] += 1
    assert auth_t == {"LLM_REVIEWED -> LLM_ADJUDICATED": 3}
    assert len(t["regressed"]) == 0
    assert len(t["improved"]) == 8
    metrics = build_aggregate_metrics(complete, t)
    effects = repair_wave_effects(new_rows, old_rows)
    matrix = {
        "artifact": "updated-baseline-transition-matrix",
        "task_id": TASK_ID,
        "created_utc": now_utc(),
        "comparison_order": "WAVE1_COMPARATOR_REPAIR_FROZEN_BEFORE_COMPARISON",
        "old_baseline": {"path": OLD_BASELINE_ID,
                         "sha256": OLD_BASELINE_SHA,
                         "status": "MEASUREMENT_V3_BURNED_BASELINE_"
                                   "COMPLETE_PROVENANCE_CORRECTED"},
        "new_results": "complete-wave1-measurement-results.json",
        "repair_row_diff_vs_upstream": {
            "changed_rows": sorted(changed_vs_up),
            "changed_count": len(changed_vs_up),
            "all_other_rows_byte_identical": True,
        },
        "verdict_delta_vs_upstream": delta,
        "repaired_rows_verdicts_equal_old_baseline": True,
        "repaired_row_authority_transitions": dict(sorted(auth_t.items())),
        "verdict_transitions": t["verdict"],
        "semantic_state_transitions": t["states"],
        "per_dimension_transitions": t["per_dimension"],
        "authority_transitions": t["authority"],
        "changed_verdict_rows": t["changed_verdict_rows"],
        "improved_criteria": t["improved"],
        "regressed_criteria": t["regressed"],
        "improvement_count": len(t["improved"]),
        "regression_count": len(t["regressed"]),
        "repair_wave_effects": effects,
    }
    write_json("complete-wave1-measurement-results.json", complete)
    write_json("complete-wave1-aggregate-metrics.json", metrics)
    write_json("updated-baseline-transition-matrix.json", matrix)
    return {"complete": complete, "matrix": matrix, "metrics": metrics,
            "new_rows": new_rows}


if __name__ == "__main__":
    main()
