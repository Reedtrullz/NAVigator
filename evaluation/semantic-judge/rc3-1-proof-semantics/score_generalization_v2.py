#!/usr/bin/env python3
"""Scorer V2: frozen G2 scorer with fixed zero-tolerance gate arithmetic.

The frozen scorer (score_generalization_frozen.py) evaluated zero-tolerance
proof gates as numerator / denominator with a hardcoded denominator of 0,
short-circuiting to 0.0 and always passing. V2 compares the raw violation
count directly for "==" gates. Official G2 artifacts are never modified;
V2 exists for future runs and for the corrected proof-gate audit.
"""
import argparse
import sys
from pathlib import Path

FROZEN_SCORER_DIR = (Path(__file__).resolve().parents[1] /
                     "rc3-generalization-holdout" / "run" / "scoring")
sys.path.insert(0, str(FROZEN_SCORER_DIR))

import score_generalization_frozen as frozen  # noqa: E402


def gate_results_v2(metrics):
    """Frozen gate table, with count-direct evaluation for zero-tolerance gates."""
    gates = {
        "semantic": (metrics["semantic_exact"]["correct"], metrics["semantic_exact"]["denominator"], 0.90, ">="),
        "proof_safe": (metrics["proof_safe_exact"]["correct"], metrics["proof_safe_exact"]["denominator"], 0.95, ">="),
        "product": (metrics["product_exact"]["correct"], metrics["product_exact"]["denominator"], 0.95, ">="),
        "auto_precision": (metrics["auto_precision"]["correct"], metrics["auto_precision"]["denominator"], 0.99, ">="),
        "auto_coverage": (metrics["auto_coverage"]["auto_count"], metrics["auto_coverage"]["denominator"], 0.20, ">="),
        "necessary_review_recall": (metrics["necessary_review"]["correct"], metrics["necessary_review"]["denominator"], 0.95, ">="),
        "unnecessary_review_rate": (metrics["unnecessary_review"]["unnecessary"], metrics["unnecessary_review"]["predicted_review"], 0.15, "<="),
        "abstain_recall": (metrics["abstain_recall"]["correct"], metrics["abstain_recall"]["denominator"], 0.90, ">="),
        "review_abstain_macro_f1": (metrics["review_abstain_macro_f1"]["macro_f1"], 1, 0.90, ">="),
        "structural_invalid_accepted_proofs": (metrics["proof_gates"]["structural_invalid_accepted_proofs"], None, 0, "=="),
        "ungrounded_accepted_proofs": (metrics["proof_gates"]["ungrounded_accepted_proofs"], None, 0, "=="),
        "semantically_unsound_accepted_proofs": (metrics["proof_gates"]["semantically_unsound_accepted_proofs"], None, 0, "=="),
        "proof_safe_unsound_autos": (metrics["proof_gates"]["proof_safe_unsound_autos"], None, 0, "=="),
        "compound_atom_semantic": (metrics["compound"]["atom_semantic_exact"]["correct"], metrics["compound"]["atom_semantic_exact"]["denominator"], 0.90, ">="),
        "compound_product": (metrics["compound"]["product_exact"]["correct"], metrics["compound"]["product_exact"]["denominator"], 0.90, ">="),
        "runtime_exceptions": (metrics["runtime_failures"], None, 0, "=="),
    }
    output = {}
    for name, (numerator, denominator, threshold, operator) in gates.items():
        if operator == "==":
            # Zero-tolerance: compare the raw violation count. Never divide.
            actual = numerator
            passed = numerator == threshold
        else:
            actual = numerator / denominator if denominator else 0.0
            passed = actual >= threshold if operator == ">=" else actual <= threshold
        output[name] = {"actual": actual, "threshold": threshold,
                        "operator": operator, "pass": passed}
    return output


def score_predictions_v2(prediction_doc, truth_doc, metadata):
    metrics = frozen.score_predictions(prediction_doc, truth_doc, metadata)
    metrics["gates"] = gate_results_v2(metrics)
    metrics["gate_engine"] = "SCORER_V2_ZERO_TOLERANCE_COUNT_DIRECT"
    return metrics


def _synthetic_docs(unsound_count=0, structural_bad_count=0, runtime_failures=0):
    """159-case synthetic doc mirroring the frozen self-test pattern."""
    n = frozen.N_CASES
    preds, truths, meta_cases = [], [], []
    for i in range(n):
        case_id = f"S{i}"
        unsound = i < unsound_count
        structural_bad = unsound_count <= i < unsound_count + structural_bad_count
        runtime_fail = i >= n - runtime_failures
        if unsound or structural_bad:
            span = "absent" if structural_bad else "evidence"
            pred = {"case_id": case_id, "runtime_status": "OK",
                    "semantic_verdict": "SUPPORTED",
                    "proof_safe_verdict": "SUPPORTED",
                    "product_action": "AUTO_SUPPORTED",
                    "atom_results": [{"atom_id": "A1",
                                      "proof_state": "ENGINE_PROOF_ACCEPTED",
                                      "frozen_verdict": "SUPPORTED",
                                      "frozen_rule": "support",
                                      "proof": {"proof_type": "SUPPORT",
                                                "source_span": span}}],
                    "atom_routes": [{"atom_id": "A1", "route": "AUTO_SUPPORTED"}],
                    "proof_object": {"atom_proofs": [{"proof_type": "SUPPORT"}]}}
            truth = {"case_id": case_id,
                     "semantic_verdict": "INSUFFICIENT_EVIDENCE",
                     "proof_safe_verdict": "INSUFFICIENT_EVIDENCE",
                     "product_action": "REVIEW_REQUIRED"}
        elif runtime_fail:
            pred = {"case_id": case_id, "runtime_status": "RUNTIME_FAILURE"}
            truth = {"case_id": case_id, "semantic_verdict": "REVIEW_REQUIRED",
                     "proof_safe_verdict": "REVIEW_REQUIRED",
                     "product_action": "REVIEW_REQUIRED"}
        else:
            pred = {"case_id": case_id, "runtime_status": "OK",
                    "semantic_verdict": "REVIEW_REQUIRED",
                    "proof_safe_verdict": "REVIEW_REQUIRED",
                    "product_action": "REVIEW_REQUIRED",
                    "atom_results": [], "atom_routes": [],
                    "proof_object": {"atom_proofs": []}}
            truth = {"case_id": case_id, "semantic_verdict": "REVIEW_REQUIRED",
                     "proof_safe_verdict": "REVIEW_REQUIRED",
                     "product_action": "REVIEW_REQUIRED"}
        preds.append(pred)
        truths.append(truth)
        meta_cases.append({"case_id": case_id,
                           "sources": [{"text": "evidence"}],
                           "evidence": [], "compound": False})
    return ({"predictions": preds}, {"cases": truths}, {"cases": meta_cases})


def self_test():
    zero = score_predictions_v2(*_synthetic_docs())
    zg = zero["gates"]
    for name in ("structural_invalid_accepted_proofs",
                 "ungrounded_accepted_proofs",
                 "semantically_unsound_accepted_proofs",
                 "proof_safe_unsound_autos", "runtime_exceptions"):
        assert zg[name]["pass"], name
        assert zg[name]["actual"] == 0, name

    one = score_predictions_v2(*_synthetic_docs(unsound_count=1))["gates"]
    assert not one["semantically_unsound_accepted_proofs"]["pass"]
    assert one["semantically_unsound_accepted_proofs"]["actual"] == 1

    fifty_three = score_predictions_v2(*_synthetic_docs(unsound_count=53))["gates"]
    assert not fifty_three["semantically_unsound_accepted_proofs"]["pass"]
    assert fifty_three["semantically_unsound_accepted_proofs"]["actual"] == 53
    assert not fifty_three["proof_safe_unsound_autos"]["pass"]

    structural = score_predictions_v2(*_synthetic_docs(structural_bad_count=1))["gates"]
    assert not structural["structural_invalid_accepted_proofs"]["pass"]
    assert structural["structural_invalid_accepted_proofs"]["actual"] == 1
    assert not structural["ungrounded_accepted_proofs"]["pass"]

    runtime = score_predictions_v2(*_synthetic_docs(runtime_failures=1))["gates"]
    assert not runtime["runtime_exceptions"]["pass"]
    assert runtime["runtime_exceptions"]["actual"] == 1

    frozen_metrics = frozen.score_predictions(*_synthetic_docs(unsound_count=53))
    frozen_gate = frozen.gate_results(frozen_metrics)
    assert frozen_gate["semantically_unsound_accepted_proofs"]["actual"] == 0.0
    assert frozen_gate["semantically_unsound_accepted_proofs"]["pass"]

    for field in ("semantic", "proof_safe", "product"):
        assert zero["confusion"][field]["total"] == frozen.N_CASES
    print("SCORER_V2 SELF_TEST PASS: 12 checks incl. frozen-bug demonstration")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scorer V2 synthetic checks")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        parser.error("use --self-test")
