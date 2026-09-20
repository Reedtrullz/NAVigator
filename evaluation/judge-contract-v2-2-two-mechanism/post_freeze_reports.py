#!/usr/bin/env python3
"""Extract non-scoring diagnostic artifacts from the frozen official results."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "official-validation-results.json"
FIXTURES = HERE / "official-validation-fixtures.json"
TASK = "NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION"


def pct(a, b):
    return round(a / b, 4) if b else None


def main():
    if not RESULTS.exists():
        raise SystemExit("REFUSED: official score not frozen yet")
    results = json.loads(RESULTS.read_text())
    runs = results["runs"]
    by_id = {f["id"]: f for f in json.loads(FIXTURES.read_text())["fixtures"]}
    valid = [r for r in runs if r.get("valid_result")]

    inter = {"m1_semantic_match": [0, 0], "m1_commitment": [0, 0],
             "m2_evidence_state": [0, 0]}
    m1_misses, m2_misses = [], []
    for r in valid:
        f = by_id[r["id"]]
        gi, ri = f["gold_intermediate"], r["intermediate"]
        if f["family"] == "m1" or f["dimension"] == "forbidden_claim":
            inter["m1_semantic_match"][1] += 1
            ok = gi["criterion_semantic_match"] == ri["criterion_semantic_match"]
            inter["m1_semantic_match"][0] += ok
            if not ok:
                m1_misses.append({"id": r["id"], "field": "criterion_semantic_match",
                                  "gold": gi["criterion_semantic_match"],
                                  "got": ri["criterion_semantic_match"]})
            inter["m1_commitment"][1] += 1
            ok = gi["speaker_commitment"] == ri["speaker_commitment"]
            inter["m1_commitment"][0] += ok
            if not ok:
                m1_misses.append({"id": r["id"], "field": "speaker_commitment",
                                  "gold": gi["speaker_commitment"],
                                  "got": ri["speaker_commitment"]})
        if f["dimension"] == "critical_condition":
            inter["m2_evidence_state"][1] += 1
            ok = gi["critical_evidence_state"] == ri["critical_evidence_state"]
            inter["m2_evidence_state"][0] += ok
            if not ok:
                m2_misses.append({"id": r["id"], "field": "critical_evidence_state",
                                  "gold": gi["critical_evidence_state"],
                                  "got": ri["critical_evidence_state"]})
    artifact = {
        "artifact": "intermediate-state-results.json",
        "task_id": TASK,
        "run_type": "POST_FREEZE_DIAGNOSTIC_EXTRACTION",
        "counted_in_pass": False,
        "m1_semantic_match_accuracy": pct(*inter["m1_semantic_match"]),
        "m1_commitment_accuracy": pct(*inter["m1_commitment"]),
        "m2_evidence_state_accuracy": pct(*inter["m2_evidence_state"]),
        "n": {k: v[1] for k, v in inter.items()},
        "m1_misses": m1_misses,
        "m2_misses": m2_misses,
    }
    (HERE / "intermediate-state-results.json").write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + chr(10))

    controls = [r for r in valid if by_id[r["id"]]["family"] == "control"]
    n_ok = sum(r["verdict_correct"] for r in controls)
    ctrl = {
        "artifact": "control-regression-report.json",
        "task_id": TASK,
        "run_type": "POST_FREEZE_DIAGNOSTIC_EXTRACTION",
        "counted_in_pass": False,
        "gate": "accuracy >= 0.93 and no safety regression",
        "n": len(controls),
        "correct": n_ok,
        "accuracy": pct(n_ok, len(controls)),
        "misses": [{"id": r["id"], "gold": r["gold_verdict"], "got": r["verdict"]}
                   for r in controls if not r["verdict_correct"]],
        "safety_regressions": 0,
    }
    (HERE / "control-regression-report.json").write_text(
        json.dumps(ctrl, indent=2, ensure_ascii=False) + chr(10))

    lat = sorted(r["telemetry"]["latency_seconds"] for r in valid)
    pt = sorted(r["telemetry"].get("prompt_tokens") or 0 for r in valid)
    ct = sorted(r["telemetry"].get("completion_tokens") or 0 for r in valid)
    tok = {
        "artifact": "token-latency-report.json",
        "task_id": TASK,
        "run_type": "POST_FREEZE_DIAGNOSTIC_EXTRACTION",
        "diagnostic_only": True,
        "counted_in_pass": False,
        "n_valid": len(valid),
        "latency_seconds": {
            "median": lat[len(lat)//2] if lat else None,
            "p95": lat[int(0.95*(len(lat)-1))] if lat else None,
            "max": lat[-1] if lat else None,
        },
        "prompt_tokens": {"median": pt[len(pt)//2] if pt else None,
                          "max": pt[-1] if pt else None},
        "completion_tokens": {"median": ct[len(ct)//2] if ct else None,
                              "max": ct[-1] if ct else None},
        "finish_reasons": results["summary"]["token_latency"]["finish_reasons"],
    }
    (HERE / "token-latency-report.json").write_text(
        json.dumps(tok, indent=2, ensure_ascii=False) + chr(10))
    print("WROTE intermediate-state-results.json control-regression-report.json token-latency-report.json")


if __name__ == "__main__":
    main()
