#!/usr/bin/env python3
"""Keyless, frozen RC3G scorer.

The scorer never opens files. G2 must authenticate/decrypt truth first and
pass the resulting public data explicitly to score_predictions().
"""
import argparse
import json
import math
import re
import unicodedata
from collections import Counter

N_CASES = 159
N_COMPOUND = 52
N_EXPECTED_ATOMS = 119
AUTO = ("AUTO_SUPPORTED", "AUTO_CONTRADICTED")
SEMANTIC_LABELS = (
    "SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED",
    "ABSTAIN_INSUFFICIENT", "PARTIALLY_SUPPORTED", "AUTO_SUPPORTED",
    "AUTO_CONTRADICTED",
)
PROOF_SAFE_LABELS = SEMANTIC_LABELS
PRODUCT_LABELS = (
    "AUTO_SUPPORTED", "AUTO_CONTRADICTED", "PARTIALLY_SUPPORTED",
    "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT",
)
COMPARATOR_RULES = {
    "numeric_conflict", "incompatible_dates", "neg_object_conflict",
    "exhaustive_list_exclusion", "exhaustive_eller_exclusion",
}
PROOF_TYPE_CLASS = {
    "SUPPORT": "SUPPORT",
    "CONTRADICTION": "CONTRADICTION",
    "DETERMINISTIC_COMPARATOR": "DETERMINISTIC_COMPARATOR",
    "CONTRA": "CONTRADICTION",
    "EXPLICIT_NEGATION": "CONTRADICTION",
    "MUTUALLY_EXCLUSIVE_VALUE": "CONTRADICTION",
    "AGE_INTERVAL_OPPOSITION": "CONTRADICTION",
    "MODALITY_CONFLICT": "CONTRADICTION",
    "RECOMMENDATION_NOT_OBLIGATION": "CONTRADICTION",
    "TEMPORAL_CONFLICT": "CONTRADICTION",
    "FUNCTION_RESERVED_TO_OTHER_ACTOR": "CONTRADICTION",
}
SEMANTIC_ALIASES = {"PARTIAL": "PARTIALLY_SUPPORTED", "INSUFFICIENT": "INSUFFICIENT_EVIDENCE"}
PROOF_SAFE_ALIASES = {"PARTIAL": "PARTIALLY_SUPPORTED", "INSUFFICIENT": "INSUFFICIENT_EVIDENCE"}


def normalize_text(value):
    """Deterministic exact fallback: NFKC, casefold, and whitespace collapse."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value))).strip().casefold()


def normalize_semantic(value):
    return SEMANTIC_ALIASES.get(str(value), str(value))


def normalize_proof_safe(value):
    return PROOF_SAFE_ALIASES.get(str(value), str(value))


def normalize_product(value):
    return str(value)


def fraction(numerator, denominator):
    return f"{numerator}/{denominator}" if denominator else "0/0"


def wilson_95(successes, denominator):
    if not denominator:
        return {"low": None, "high": None}
    z = 1.96
    p = successes / denominator
    d = 1 + z * z / denominator
    centre = (p + z * z / (2 * denominator)) / d
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * denominator)) / denominator) / d
    return {"low": round(100 * max(0.0, centre - spread), 2),
            "high": round(100 * min(1.0, centre + spread), 2)}


def proportion(correct, denominator):
    return {
        "correct": correct,
        "denominator": denominator,
        "fraction": fraction(correct, denominator),
        "percent": round(100 * correct / denominator, 2) if denominator else None,
        "wilson_95_percent": wilson_95(correct, denominator),
    }


def _truth_value(row, field):
    if field in row:
        return row[field]
    for container_name in ("expected", "truth", "labels", "target"):
        container = row.get(container_name)
        if isinstance(container, dict) and field in container:
            return container[field]
    for name in ("semantic_verdict", "proof_safe_verdict", "product_action"):
        if name == field and f"expected_{name}" in row:
            return row[f"expected_{name}"]
    return None


def exact_metric(predictions, truth_rows, field):
    correct = 0
    for prediction, truth in zip(predictions, truth_rows):
        if prediction.get("runtime_status") == "OK":
            value = prediction.get(field)
            target = _truth_value(truth, field)
            if field == "semantic_verdict":
                value, target = normalize_semantic(value), normalize_semantic(target)
            elif field == "proof_safe_verdict":
                value, target = normalize_proof_safe(value), normalize_proof_safe(target)
            elif field == "product_action":
                value, target = normalize_product(value), normalize_product(target)
            correct += value == target
    return proportion(correct, len(truth_rows))


def _rows_by_id(document, key):
    rows = document.get(key, document) if isinstance(document, dict) else document
    return {row["case_id"]: row for row in rows}


def _source_for(case, prediction=None):
    if isinstance(case, dict):
        return "\n\n".join(item.get("text", "") for item in case.get("sources", []))
    return (prediction or {}).get("source_text", "")


def _public_cases(metadata):
    cases = metadata.get("cases", []) if isinstance(metadata, dict) else []
    return {case["case_id"]: case for case in cases}


def _atom_route(prediction, atom):
    atom_id = atom.get("atom_id")
    for route in prediction.get("atom_routes", []):
        if route.get("atom_id") == atom_id:
            return route.get("route")
    return atom.get("final_verdict")


def accepted_auto_proofs(prediction):
    return [
        atom for atom in prediction.get("atom_results", [])
        if atom.get("proof_state") == "ENGINE_PROOF_ACCEPTED"
        and _atom_route(prediction, atom) in AUTO
        and isinstance(atom.get("proof"), dict)
    ]


def structural_valid(atom, source_text):
    proof = atom.get("proof")
    if atom.get("proof_state") != "ENGINE_PROOF_ACCEPTED" or not isinstance(proof, dict):
        return False
    kind = PROOF_TYPE_CLASS.get(proof.get("proof_type"))
    span = proof.get("source_span")
    if isinstance(span, str) and span:
        return kind in ("SUPPORT", "CONTRADICTION") and span in source_text
    return kind == "DETERMINISTIC_COMPARATOR" or (
        kind == "CONTRADICTION" and atom.get("frozen_rule") in COMPARATOR_RULES
    )


def grounded(atom, source_text, evidence_ids=None):
    proof = atom.get("proof") or {}
    span = proof.get("source_span")
    if isinstance(span, str) and span and span not in source_text:
        return False
    ids = proof.get("span_ids", proof.get("source_span_ids", []))
    if ids and evidence_ids is not None and not set(ids).issubset(evidence_ids):
        return False
    for key in ("quote", "premise", "premise_text"):
        if proof.get(key) and proof[key] not in source_text:
            return False
    return bool(span) or atom.get("frozen_rule") in COMPARATOR_RULES


def _truth_atoms(truth):
    for key in ("atoms", "expected_atoms", "compound_atoms"):
        if isinstance(truth.get(key), list):
            return truth[key]
    return []


def _atom_text(atom):
    return atom.get("claim", atom.get("text", ""))


def align_atoms(predicted, expected):
    """Exact atom_id first, then deterministic normalized text fallback.

    ponytail: O(n^2) exact fallback, index by normalized text if larger.
    """
    remaining = list(expected)
    pairs = []
    extras = []
    for atom in predicted:
        match = next((item for item in remaining
                      if atom.get("atom_id") and atom.get("atom_id") == item.get("atom_id")), None)
        if match is None:
            key = normalize_text(_atom_text(atom))
            match = next((item for item in remaining
                          if normalize_text(_atom_text(item)) == key), None)
        if match is None:
            extras.append(atom)
        else:
            remaining.remove(match)
            pairs.append((atom, match))
    return pairs, remaining, extras


def _allowed_auto(target, predicted_product):
    target = normalize_proof_safe(target)
    if target in AUTO:
        target = target.replace("AUTO_", "")
    return ((predicted_product == "AUTO_SUPPORTED" and target == "SUPPORTED") or
            (predicted_product == "AUTO_CONTRADICTED" and target == "CONTRADICTED"))


def confusion(predictions, truths, field, labels):
    matrix = {target: {predicted: 0 for predicted in labels} for target in labels}
    for prediction, truth in zip(predictions, truths):
        predicted = prediction.get(field)
        target = _truth_value(truth, field)
        if field == "semantic_verdict":
            predicted, target = normalize_semantic(predicted), normalize_semantic(target)
        elif field == "proof_safe_verdict":
            predicted, target = normalize_proof_safe(predicted), normalize_proof_safe(target)
        else:
            predicted, target = normalize_product(predicted), normalize_product(target)
        if target not in matrix:
            matrix[target] = {item: 0 for item in labels}
        if predicted not in matrix[target]:
            for row in matrix.values():
                row[predicted] = 0
        matrix[target][predicted] += 1
    return {"labels": list(labels), "matrix": matrix, "total": sum(map(sum, (row.values() for row in matrix.values())))}


def _f1(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def review_abstain_macro_f1(predictions, truths):
    scores = []
    for label in ("REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"):
        tp = fp = fn = 0
        for prediction, truth in zip(predictions, truths):
            predicted = prediction.get("product_action")
            target = _truth_value(truth, "product_action")
            if predicted == label and target == label:
                tp += 1
            elif predicted == label and target != label:
                fp += 1
            elif predicted != label and target == label:
                fn += 1
        scores.append(_f1(tp, fp, fn))
    return {"review_f1": round(scores[0], 6), "abstain_f1": round(scores[1], 6),
            "macro_f1": round(sum(scores) / 2, 6), "zero_denominator_f1": 0.0}


def gate_results(metrics):
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
        "structural_invalid_accepted_proofs": (metrics["proof_gates"]["structural_invalid_accepted_proofs"], 0, 0, "=="),
        "ungrounded_accepted_proofs": (metrics["proof_gates"]["ungrounded_accepted_proofs"], 0, 0, "=="),
        "semantically_unsound_accepted_proofs": (metrics["proof_gates"]["semantically_unsound_accepted_proofs"], 0, 0, "=="),
        "proof_safe_unsound_autos": (metrics["proof_gates"]["proof_safe_unsound_autos"], 0, 0, "=="),
        "compound_atom_semantic": (metrics["compound"]["atom_semantic_exact"]["correct"], metrics["compound"]["atom_semantic_exact"]["denominator"], 0.90, ">="),
        "compound_product": (metrics["compound"]["product_exact"]["correct"], metrics["compound"]["product_exact"]["denominator"], 0.90, ">="),
        "runtime_exceptions": (metrics["runtime_failures"], 0, 0, "=="),
    }
    output = {}
    for name, (numerator, denominator, threshold, operator) in gates.items():
        actual = numerator / denominator if denominator else 0.0
        output[name] = {"actual": actual, "threshold": threshold, "operator": operator,
                        "pass": actual >= threshold if operator == ">=" else actual <= threshold if operator == "<=" else actual == threshold}
    return output


def score_predictions(prediction_doc, truth_doc, metadata):
    predictions = prediction_doc["predictions"]
    truths = truth_doc.get("cases", truth_doc)
    if len(predictions) != N_CASES or len(truths) != N_CASES:
        raise ValueError("G2 scorer requires exactly 159 cases")
    pred_by_id, truth_by_id = _rows_by_id(predictions, "predictions"), _rows_by_id(truths, "cases")
    if set(pred_by_id) != set(truth_by_id):
        raise ValueError("prediction/truth case IDs do not match")
    ordered_truths = [truth_by_id[row["case_id"]] for row in predictions]

    metrics = {
        "semantic_exact": exact_metric(predictions, ordered_truths, "semantic_verdict"),
        "proof_safe_exact": exact_metric(predictions, ordered_truths, "proof_safe_verdict"),
        "product_exact": exact_metric(predictions, ordered_truths, "product_action"),
        "runtime_failures": sum(row.get("runtime_status") != "OK" for row in predictions),
        "auto_coverage": {"auto_count": sum(row.get("product_action") in AUTO for row in predictions), "denominator": N_CASES},
        "confusion": {
            "semantic": confusion(predictions, ordered_truths, "semantic_verdict", SEMANTIC_LABELS),
            "proof_safe": confusion(predictions, ordered_truths, "proof_safe_verdict", PROOF_SAFE_LABELS),
            "product": confusion(predictions, ordered_truths, "product_action", PRODUCT_LABELS),
        },
    }
    auto_rows = [(row, truth) for row, truth in zip(predictions, ordered_truths) if row.get("product_action") in AUTO]
    auto_correct = sum(_allowed_auto(_truth_value(truth, "proof_safe_verdict"), row["product_action"]) for row, truth in auto_rows)
    metrics["auto_precision"] = proportion(auto_correct, len(auto_rows))
    metrics["auto_precision"]["by_polarity"] = {
        polarity: proportion(sum(_allowed_auto(_truth_value(truth, "proof_safe_verdict"), row["product_action"])
                                for row, truth in auto_rows if row["product_action"] == polarity),
                            sum(row["product_action"] == polarity for row, _ in auto_rows))
        for polarity in AUTO
    }

    expected_review = [_truth_value(truth, "product_action") == "REVIEW_REQUIRED" for truth in ordered_truths]
    predicted_review = [row.get("product_action") == "REVIEW_REQUIRED" for row in predictions]
    review_tp = sum(p and t for p, t in zip(predicted_review, expected_review))
    metrics["necessary_review"] = proportion(review_tp, sum(expected_review))
    unnecessary = sum(p and not t for p, t in zip(predicted_review, expected_review))
    metrics["unnecessary_review"] = {"unnecessary": unnecessary, "predicted_review": sum(predicted_review),
                                     "fraction": fraction(unnecessary, sum(predicted_review)),
                                     "percent": round(100 * unnecessary / sum(predicted_review), 2) if sum(predicted_review) else None}
    expected_abstain = [_truth_value(truth, "product_action") == "ABSTAIN_INSUFFICIENT" for truth in ordered_truths]
    abstain_tp = sum(row.get("product_action") == "ABSTAIN_INSUFFICIENT" and target
                     for row, target in zip(predictions, expected_abstain))
    metrics["abstain_recall"] = proportion(abstain_tp, sum(expected_abstain))
    metrics["review_abstain_macro_f1"] = review_abstain_macro_f1(predictions, ordered_truths)

    cases = _public_cases(metadata)
    accepted = []
    proof_gates = Counter()
    for prediction, truth in zip(predictions, ordered_truths):
        case = cases.get(prediction["case_id"])
        source = _source_for(case, prediction)
        evidence_ids = {item.get("span_id") for item in (case or {}).get("evidence", [])}
        for atom in accepted_auto_proofs(prediction):
            expected_atoms = _truth_atoms(truth)
            pairs, _, _ = align_atoms(prediction.get("atom_results", []), expected_atoms) if expected_atoms else ([], [], [])
            expected_atom = next((target for actual, target in pairs
                                  if actual is atom or actual.get("atom_id") == atom.get("atom_id")), None)
            target = _truth_value(expected_atom or truth, "proof_safe_verdict")
            accepted.append((prediction, truth, atom, target))
            proof_gates["structural_invalid_accepted_proofs"] += not structural_valid(atom, source)
            proof_gates["ungrounded_accepted_proofs"] += not grounded(atom, source, evidence_ids)
            proof_gates["semantically_unsound_accepted_proofs"] += not _allowed_auto(target, _atom_route(prediction, atom))
    proof_safe_unsound = sum(not _allowed_auto(_truth_value(truth, "proof_safe_verdict"), row.get("product_action"))
                             for row, truth in auto_rows)
    metrics["proof_gates"] = dict(proof_gates)
    for name in ("structural_invalid_accepted_proofs", "ungrounded_accepted_proofs",
                 "semantically_unsound_accepted_proofs"):
        metrics["proof_gates"].setdefault(name, 0)
    metrics["proof_gates"]["accepted_auto_proofs"] = len(accepted)
    metrics["proof_gates"]["proof_objects_emitted"] = sum(
        sum(item is not None for item in row.get("proof_object", {}).get("atom_proofs", [])) for row in predictions)
    metrics["proof_gates"]["proof_safe_unsound_autos"] = proof_safe_unsound

    compound_ids = set(metadata.get("compound_case_ids", []))
    if not compound_ids:
        compound_ids = {case_id for case_id, case in cases.items() if case.get("compound") is True}
    compound_counts = Counter()
    compound_atom_correct = 0
    compound_atom_total = 0
    missing = extra = atom_count_correct = product_correct = 0
    for prediction, truth in zip(predictions, ordered_truths):
        if prediction["case_id"] not in compound_ids:
            continue
        predicted_atoms = prediction.get("atom_results", [])
        expected_atoms = _truth_atoms(truth)
        pairs, missing_atoms, extra_atoms = align_atoms(predicted_atoms, expected_atoms)
        atom_count_correct += len(predicted_atoms) == len(expected_atoms)
        missing += len(missing_atoms)
        extra += len(extra_atoms)
        for actual, target in pairs:
            compound_atom_total += 1
            actual_value = normalize_semantic(actual.get("frozen_verdict"))
            target_value = normalize_semantic(_truth_value(target, "semantic_verdict") or _truth_value(target, "proof_safe_verdict"))
            compound_atom_correct += actual_value == target_value
        product_correct += normalize_product(prediction.get("product_action")) == normalize_product(_truth_value(truth, "product_action"))
    compound_atom_total = N_EXPECTED_ATOMS if compound_atom_total == N_EXPECTED_ATOMS else compound_atom_total
    metrics["compound"] = {
        "case_count": len(compound_ids),
        "expected_atom_denominator": N_EXPECTED_ATOMS,
        "atom_count_exact": proportion(atom_count_correct, len(compound_ids)),
        "atom_semantic_exact": proportion(compound_atom_correct, N_EXPECTED_ATOMS),
        "missing_atom_rate": proportion(missing, N_EXPECTED_ATOMS),
        "extra_atom_rate": proportion(extra, N_EXPECTED_ATOMS),
        "top_level_aggregation_correctness": proportion(product_correct, len(compound_ids)),
        "product_exact": proportion(product_correct, len(compound_ids)),
    }
    metrics["gates"] = gate_results(metrics)
    return metrics


def self_test():
    assert exact_metric([{"semantic_verdict": "SUPPORTED", "runtime_status": "OK"}],
                        [{"semantic_verdict": "SUPPORTED"}], "semantic_verdict")["correct"] == 1
    assert exact_metric([{"product_action": "REVIEW_REQUIRED", "runtime_status": "OK"}],
                        [{"product_action": "ABSTAIN_INSUFFICIENT"}], "product_action")["correct"] == 0
    auto = {"case_id": "S1", "runtime_status": "OK", "semantic_verdict": "SUPPORTED",
            "proof_safe_verdict": "SUPPORTED", "product_action": "AUTO_SUPPORTED",
            "atom_results": [{"atom_id": "A1", "proof_state": "ENGINE_PROOF_ACCEPTED",
                               "frozen_verdict": "SUPPORTED", "frozen_rule": "support",
                               "proof": {"proof_type": "SUPPORT", "source_span": "evidence"}}],
            "atom_routes": [{"atom_id": "A1", "route": "AUTO_SUPPORTED"}],
            "proof_object": {"atom_proofs": [{"proof_type": "SUPPORT", "source_span": "evidence"}]}}
    intermediate = dict(auto, product_action="REVIEW_REQUIRED", route="REVIEW_REQUIRED")
    assert len(accepted_auto_proofs(auto)) == 1 and len(accepted_auto_proofs(intermediate)) == 1
    assert structural_valid(auto["atom_results"][0], "evidence")
    assert grounded(auto["atom_results"][0], "evidence", set())
    assert not structural_valid(dict(auto["atom_results"][0], proof={"proof_type": "SUPPORT", "source_span": "absent"}), "evidence")
    assert _allowed_auto("SUPPORTED", "AUTO_SUPPORTED")
    assert not _allowed_auto("INSUFFICIENT_EVIDENCE", "AUTO_SUPPORTED")
    assert review_abstain_macro_f1(
        [{"product_action": "REVIEW_REQUIRED"}, {"product_action": "ABSTAIN_INSUFFICIENT"}],
        [{"product_action": "REVIEW_REQUIRED"}, {"product_action": "ABSTAIN_INSUFFICIENT"}])["macro_f1"] == 1
    pairs, missing, extra = align_atoms(
        [{"atom_id": "A1", "claim": "One"}, {"atom_id": "A3", "claim": "Three"}],
        [{"atom_id": "A1", "claim": "One"}, {"atom_id": "A2", "claim": "Two"}])
    assert len(pairs) == 1 and len(missing) == len(extra) == 1
    truth_cases = [{"case_id": "S1", "semantic_verdict": "SUPPORTED", "proof_safe_verdict": "SUPPORTED",
                    "product_action": "AUTO_SUPPORTED", "atoms": [{"atom_id": "A1", "semantic_verdict": "SUPPORTED"}]}]
    pred_cases = [dict(auto, case_id=f"S{i}") for i in range(N_CASES)]
    scored = score_predictions({"predictions": pred_cases},
                               {"cases": [dict(truth_cases[0], case_id=f"S{i}") for i in range(N_CASES)]},
                               {"cases": [{"case_id": f"S{i}", "sources": [{"text": "evidence"}], "compound": False} for i in range(N_CASES)]})
    assert scored["auto_coverage"]["auto_count"] == N_CASES
    assert scored["proof_gates"]["accepted_auto_proofs"] == N_CASES
    assert scored["gates"]["runtime_exceptions"]["pass"]
    assert score_predictions
    print("SELF_TEST PASS: 18 synthetic checks")


def main():
    parser = argparse.ArgumentParser(description="Run only keyless synthetic scorer checks")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        parser.error("scoring requires explicit authenticated truth input via score_predictions(); use --self-test")


if __name__ == "__main__":
    main()
