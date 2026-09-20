#!/usr/bin/env python3
"""V2.2 official one-shot validation: 120 frozen fixtures, one call each.

Frozen runner. No fixture edits; no substantive reruns; retry policy lives in
judge_core_v2_2.call_judge only. Writes official-validation-results.json.
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from judge_core_v2_2 import call_judge, derive_final, prompt_hash  # noqa: E402

HERE = Path(__file__).parent
FIXTURES = HERE / "official-validation-fixtures.json"
RESULTS = HERE / "official-validation-results.json"


def pct(n, d):
    return round(n / d, 4) if d else None


def score(runs, fixtures):
    by_id = {f["id"]: f for f in fixtures}
    fam = {k: {"n": 0, "correct": 0} for k in ("m1", "m2", "control")}
    valid = 0
    deriv_ok = 0
    span_fail = 0
    for r in runs:
        f = by_id[r["id"]]
        fam[f["family"]]["n"] += 1
        if r.get("valid_result"):
            valid += 1
            fam[f["family"]]["correct"] += r["verdict_correct"]
            v2, _ = derive_final(f["dimension"], r["intermediate"])
            deriv_ok += (v2 == r["verdict"])
        else:
            span_fail += 1

    summary = {
        "overall": {"n": len(runs), "correct": sum(b["correct"] for b in fam.values()),
                    "accuracy": pct(sum(b["correct"] for b in fam.values()), len(runs))},
        "by_family": {k: {"n": v["n"], "accuracy": pct(v["correct"], v["n"])} for k, v in fam.items()},
        "valid_structured_rate": pct(valid, len(runs)),
        "derivation_consistency": pct(deriv_ok, valid),
    }

    m1_hedged = [r for r in runs if r["id"].startswith("V22-M1-")
                 and by_id[r["id"]]["gold_intermediate"]["criterion_semantic_match"] == "MATCH"
                 and by_id[r["id"]]["gold_intermediate"]["speaker_commitment"] == "HEDGED_ASSERTION"]
    m1_hedged_correct = sum(1 for r in m1_hedged if r.get("verdict_correct"))
    summary["m1_hedged_gate"] = {
        "n": len(m1_hedged), "correct": m1_hedged_correct,
        "evaluability_accuracy": pct(m1_hedged_correct, len(m1_hedged)),
        "false_absent_due_to_hedge": sum(1 for r in m1_hedged if r.get("verdict") == "ABSENT"),
        "false_unresolved_due_to_hedge": sum(1 for r in m1_hedged if r.get("verdict") == "UNRESOLVED"),
    }

    m2_runs = [r for r in runs if r["id"].startswith("V22-M2-")]
    amb = [r for r in m2_runs
           if by_id[r["id"]]["gold_intermediate"]["critical_evidence_state"] == "AMBIGUOUS_OR_CONFLICTING"]
    clear = [r for r in m2_runs
             if by_id[r["id"]]["gold_intermediate"]["critical_evidence_state"]
             in ("CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT")]
    summary["m2_gates"] = {
        "ambiguous": {"n": len(amb), "correct_unresolved": sum(1 for r in amb if r.get("verdict") == "UNRESOLVED"),
                      "unresolved_rate": pct(sum(1 for r in amb if r.get("verdict") == "UNRESOLVED"), len(amb)),
                      "forced_binary_triggered": sum(1 for r in amb if r.get("verdict") == "TRIGGERED"),
                      "forced_binary_not_triggered": sum(1 for r in amb if r.get("verdict") == "NOT_TRIGGERED")},
        "clear": {"n": len(clear), "correct": sum(1 for r in clear if r.get("verdict_correct")),
                  "accuracy": pct(sum(1 for r in clear if r.get("verdict_correct")), len(clear)),
                  "critical_false_negatives": sum(1 for r in clear
                                                  if by_id[r["id"]]["gold_intermediate"]["critical_evidence_state"] == "CLEAR_TRIGGER_SUPPORT"
                                                  and r.get("verdict") != "TRIGGERED")},
    }

    inter = {"m1_semantic_match": [0, 0], "m1_commitment": [0, 0], "m2_evidence_state": [0, 0]}
    for r in runs:
        f = by_id[r["id"]]
        if not r.get("valid_result"):
            continue
        if f["family"] == "m1" or f["dimension"] == "forbidden_claim":
            gi, ri = f["gold_intermediate"], r["intermediate"]
            inter["m1_semantic_match"][1] += 1
            inter["m1_semantic_match"][0] += gi["criterion_semantic_match"] == ri["criterion_semantic_match"]
            inter["m1_commitment"][1] += 1
            inter["m1_commitment"][0] += gi["speaker_commitment"] == ri["speaker_commitment"]
        if f["dimension"] == "critical_condition":
            inter["m2_evidence_state"][1] += 1
            inter["m2_evidence_state"][0] += (f["gold_intermediate"]["critical_evidence_state"]
                                              == r["intermediate"]["critical_evidence_state"])
    summary["intermediate_state_accuracy"] = {
        k: {"correct": v[0], "n": v[1], "accuracy": pct(v[0], v[1])} for k, v in inter.items()}

    lat = [r["telemetry"]["latency_seconds"] for r in runs if r.get("valid_result")]
    pt = [r["telemetry"]["prompt_tokens"] for r in runs if r.get("valid_result")]
    ct = [r["telemetry"]["completion_tokens"] for r in runs if r.get("valid_result")]
    rt = [r["telemetry"].get("reasoning_tokens", 0) for r in runs if r.get("valid_result")]
    fr = {}
    for r in runs:
        k = r["telemetry"].get("finish_reason", "missing") if r.get("valid_result") else "invalid"
        fr[k] = fr.get(k, 0) + 1
    summary["token_latency"] = {
        "n_valid": len(lat),
        "latency_seconds": {"median": round(statistics.median(lat), 2) if lat else None,
                            "p95": round(sorted(lat)[int(0.95 * (len(lat) - 1))], 2) if lat else None,
                            "max": round(max(lat), 2) if lat else None},
        "prompt_tokens": {"median": statistics.median(pt) if pt else None, "max": max(pt) if pt else None},
        "completion_tokens": {"median": statistics.median(ct) if ct else None, "max": max(ct) if ct else None},
        "reasoning_tokens_total": sum(rt),
        "finish_reasons": fr,
        "schema_failures": span_fail,
    }
    return summary


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = data["fixtures"]
    if len(fixtures) != 120:
        raise SystemExit("expected 120 fixtures, got %d" % len(fixtures))
    runs = []
    out_path = HERE / "official-validation-results.partial.json"
    for i, fixture in enumerate(fixtures, 1):
        result, telemetry = call_judge(fixture["dimension"], fixture["ctx"], fixture["crit"], fixture["sut"])
        entry = {"id": fixture["id"], "family": fixture["family"], "tag": fixture["tag"],
                 "gold_intermediate": fixture["gold_intermediate"], "gold_verdict": fixture["gold_verdict"],
                 "telemetry": telemetry}
        if result is not None:
            entry.update({"valid_result": True, "intermediate": result["intermediate"],
                          "verdict": result["verdict"], "derivation_basis": result["derivation_basis"],
                          "evidence_spans": result["evidence_spans"], "note": result["note"],
                          "verdict_correct": result["verdict"] == fixture["gold_verdict"]})
        else:
            entry.update({"valid_result": False, "verdict_correct": False})
        runs.append(entry)
        out_path.write_text(json.dumps({"runs": runs}, ensure_ascii=False) + chr(10), encoding="utf-8")
        print("%d/120 %s ok=%s correct=%s" % (i, entry["id"], entry["valid_result"], entry["verdict_correct"]), flush=True)
    summary = score(runs, fixtures)
    out = {"artifact": "official-validation-results.json",
           "task_id": "NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION",
           "run_type": "ONE_SHOT_OFFICIAL_VALIDATION",
           "prompt_sha": prompt_hash(), "fixtures_file": FIXTURES.name,
           "fixture_count": len(fixtures), "summary": summary, "runs": runs}
    RESULTS.write_text(json.dumps(out, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("overall", "by_family", "valid_structured_rate", "derivation_consistency")}, indent=2))


if __name__ == "__main__":
    main()
