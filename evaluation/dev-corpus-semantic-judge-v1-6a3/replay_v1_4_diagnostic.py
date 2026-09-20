#!/usr/bin/env python3
"""Burned V1.4 diagnostic replay (contract section 44). Diagnostic only:
no gold re-adjudication, no scoring change, no certification claim."""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).parent
V14 = HERE.parent / "dev-corpus-semantic-judge-v1-4"
sys.path.insert(0, str(HERE))
from boundary_preclassifier import classify


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


NON_COMMITMENT = {"NEGATED", "SELF_RETRACTED", "QUOTED_ONLY",
                  "HYPOTHETICAL_ONLY", "VAGUE_NONCOMMITTAL"}


def main():
    fxdoc = json.loads((V14 / "official-validation-fixtures.json").read_text())
    res = json.loads((V14 / "official-validation-results.json").read_text())
    rows = res["rows"]
    fx_by_id = {f["id"]: f for f in fxdoc["fixtures"]}

    per_row = {}
    for r in rows:
        fid = r["id"]
        f = fx_by_id[fid]
        text = f["sut_answer"]
        out = classify(text)
        dims = {k: v["label"] for k, v in out.items()}
        abstains = [k for k, v in out.items() if v["abstained"]]
        model_ok = r.get("status") == "OK"
        model_miss = (not model_ok) or (r.get("verdict_correct") is False)
        route_label = dims["route_commitment"]
        # Narrow preregistered false-deterministic definition: the classifier
        # returned a POSITIVE commitment label (ASSERTED/HEDGED) on a row the
        # frozen gold adjudicated as NO route assertion problem AND the model
        # agreed with gold - i.e., classifier contradicts two independent
        # agreement sources. Anything weaker is reported, not gated.
        gold = r.get("gold") or {}
        false_det = False
        if (model_ok and r.get("verdict_correct") is True
                and f["dimension"] == "route_correctness"
                and route_label in ("ASSERTED", "HEDGED_ASSERTION")
                and gold.get("verdict") == "TRIGGERED"):
            false_det = True
        per_row[fid] = {
            "dimension": f["dimension"],
            "route_label": route_label,
            "uncertainty_label": dims["uncertainty_behavior"],
            "scope_label": dims["assertion_scope"],
            "abstain_dims": abstains,
            "model_ok": model_ok,
            "model_miss": model_miss,
            "false_deterministic_narrow": false_det,
        }

    n = len(per_row)
    full_det = [fid for fid, r in per_row.items() if not r["abstain_dims"]]
    judge_required = [fid for fid, r in per_row.items() if r["abstain_dims"]]
    misses = [fid for fid, r in per_row.items() if r["model_miss"]]
    misses_captured = [fid for fid in misses if per_row[fid]["abstain_dims"]]
    misses_route_det = [fid for fid in misses
                        if "route_commitment" not in per_row[fid]["abstain_dims"]]
    false_dets = [fid for fid, r in per_row.items()
                  if r["false_deterministic_narrow"]]

    doc = {
        "artifact": "burned-v1-4-diagnostic-replay.json",
        "task_id": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A3-AMBIGUITY-ABSTENTION-HARDENING",
        "run_type": "BURNED_DIAGNOSTIC_REPLAY",
        "diagnostic_only": True,
        "certification_claim": False,
        "engine_sha256": sha(HERE / "boundary_preclassifier.py"),
        "v1_4_inputs": {
            "fixtures_sha256": sha(V14 / "official-validation-fixtures.json"),
            "results_sha256": sha(V14 / "official-validation-results.json"),
            "gold_sha256": sha(V14 / "official-validation-gold.json"),
        },
        "n": n,
        "deterministic_resolution": {
            "full_all_three_dims": len(full_det),
            "share": round(len(full_det) / n, 4),
            "route_dim_non_abstain": len(
                [1 for r in per_row.values()
                 if "route_commitment" not in r["abstain_dims"]]),
            "uncertainty_dim_non_abstain": len(
                [1 for r in per_row.values()
                 if "uncertainty_behavior" not in r["abstain_dims"]]),
            "scope_dim_non_abstain": len(
                [1 for r in per_row.values()
                 if "assertion_scope" not in r["abstain_dims"]]),
        },
        "remaining_judge_required": {
            "n": len(judge_required),
            "share": round(len(judge_required) / n, 4),
            "definition": ">=1 pre-classifier dimension ABSTAIN (conservative)",
        },
        "historical_model_misses": {
            "n": len(misses),
            "captured_by_abstain": len(misses_captured),
            "captured_ids": misses_captured,
            "route_deterministic_on_miss": len(misses_route_det),
            "note": ("Captured = model-miss rows where the pre-classifier "
                     "abstains on >=1 dimension, flagging the row for stricter "
                     "adjudication rather than mechanical resolution."),
        },
        "false_deterministics": {
            "narrow_definition_n": len(false_dets),
            "narrow_definition_ids": false_dets,
            "definition": ("Positive route commitment label on a route_correctness "
                           "row where frozen gold and historical model agree the "
                           "route criterion is TRIGGERED"),
        },
        "per_row": per_row,
        "note": ("Diagnostic replay of the frozen V1.6A.3 pre-classifier over the "
                 "burned V1.4 official benchmark SUT answers. No gold changes, "
                 "no scoring changes, no semantic judge calls."),
    }
    (HERE / "burned-v1-4-diagnostic-replay.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + chr(10))

    estimate = {
        "artifact": "judge-call-reduction-estimate.json",
        "task_id": doc["task_id"],
        "basis": "burned-v1-4-diagnostic-replay.json",
        "v1_4_n": n,
        "pre_classifier_abstain_share": doc["remaining_judge_required"]["share"],
        "full_deterministic_share": doc["deterministic_resolution"]["share"],
        "conservative_estimate": {
            "assumption": ("Judge still called for every row (critical/forbidden "
                           "safety checks are outside pre-classifier scope); "
                           "reduction applies to route/uncertainty/scope "
                           "sub-adjudication only where all three pre-classifier "
                           "dimensions resolve deterministically."),
            "reducible_sub_adjudication_share":
                doc["deterministic_resolution"]["share"],
            "full_judge_call_reduction_share": 0.0,
        },
        "note": ("Diagnostic-only estimate. The pre-classifier is a boundary "
                 "gate, not a judge replacement: safety dimensions still require "
                 "the semantic judge on every row."),
    }
    (HERE / "judge-call-reduction-estimate.json").write_text(
        json.dumps(estimate, indent=2, ensure_ascii=False) + chr(10))

    print(json.dumps({
        "n": n,
        "full_deterministic": len(full_det),
        "judge_required": len(judge_required),
        "model_misses": len(misses),
        "misses_captured_by_abstain": len(misses_captured),
        "false_deterministics_narrow": len(false_dets),
    }, indent=1))


if __name__ == "__main__":
    main()
