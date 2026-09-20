#!/usr/bin/env python3
"""G2 post-freeze error inspection (spec 32-36).

Runs after the official score freeze. Decrypts the sealed key in memory,
classifies every case with a deterministic taxonomy, and writes
aggregate-only artifacts. No plaintext labels, no per-case dumps, no
score rewrite, no rerun of the frozen scorer.
"""
import base64
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
HOLDOUT = RUN.parent
sys.path.insert(0, str(HERE))
import score_generalization_frozen as scorer  # noqa: E402

AUTO = ("AUTO_SUPPORTED", "AUTO_CONTRADICTED")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def polarity(label):
    label = scorer.normalize_semantic(label or "")
    if label in ("SUPPORTED", "PARTIALLY_SUPPORTED", "AUTO_SUPPORTED"):
        return "POS"
    if label in ("CONTRADICTED", "AUTO_CONTRADICTED"):
        return "NEG"
    return "NONE"


def derived_product(label):
    """Consistent product action implied by the truth labels themselves."""
    proof = scorer.normalize_proof_safe(label.get("proof_safe") or "")
    if proof == "SUPPORTED":
        return "AUTO_SUPPORTED"
    if proof == "CONTRADICTED":
        return "AUTO_CONTRADICTED"
    if label.get("genuine_insufficiency") is True:
        return "ABSTAIN_INSUFFICIENT"
    return "REVIEW_REQUIRED"


def main():
    key_b64 = os.environ.get("RC3_GENERALIZATION_KEY")
    if not key_b64:
        sys.exit("RC3_GENERALIZATION_KEY unavailable")
    key = base64.urlsafe_b64decode(key_b64 + "=" * (-len(key_b64) % 4))
    blob = json.loads((HOLDOUT / "answer-key.sealed").read_text())
    cases_sha = sha(HOLDOUT / "generalization-cases.json")
    payload = json.loads(AESGCM(key).decrypt(
        base64.b64decode(blob["nonce"]),
        base64.b64decode(blob["ciphertext"]),
        cases_sha.encode("ascii")))

    freeze = json.loads((HERE / "official-generalization-score-freeze.json").read_text())
    pred_doc = json.loads((RUN / "RC3G-predictions.json").read_text())
    predictions = pred_doc["predictions"]
    cases_doc = json.loads((HOLDOUT / "generalization-cases.json").read_text())
    case_by_id = {c["case_id"]: c for c in cases_doc["cases"]}
    compound_ids = {cid for cid, c in case_by_id.items() if c.get("compound") is True}

    def adapt(case_id, label):
        out = dict(label)
        out["case_id"] = case_id
        out["semantic_verdict"] = label.get("semantic_truth")
        out["proof_safe_verdict"] = label.get("proof_safe")
        return out

    labels = {cid: adapt(cid, lab) for cid, lab in payload["labels"].items()}

    taxonomy = Counter()
    failure_modes = Counter()
    severity = Counter()
    label_error_kinds = Counter()
    label_error_ids = []
    atom_stats = {"missing_atoms": 0, "extra_atoms": 0,
                  "cases_with_missing": 0, "cases_with_extra": 0}
    sound = {"auto_cases": 0, "sound_auto_cases": 0, "accepted_atoms": 0,
             "structurally_invalid": 0, "ungrounded": 0, "semantically_unsound": 0,
             "proof_safe_unsound_autos": 0}
    arbitration = {"reviewer_used": 0, "reviewer_flipped": 0}

    for row in predictions:
        cid = row["case_id"]
        lab = labels[cid]
        case = case_by_id.get(cid, {})
        source = scorer._source_for(case, row)
        evidence_ids = {item.get("span_id") for item in case.get("evidence", [])}
        truth_sem = scorer.normalize_semantic(scorer._truth_value(lab, "semantic_verdict"))
        truth_proof = scorer.normalize_proof_safe(scorer._truth_value(lab, "proof_safe_verdict"))
        truth_prod = scorer.normalize_product(scorer._truth_value(lab, "product_action"))
        pred_sem = scorer.normalize_semantic(row.get("semantic_verdict"))
        pred_proof = scorer.normalize_proof_safe(row.get("proof_safe_verdict"))
        pred_prod = scorer.normalize_product(row.get("product_action"))

        tags = set()
        if pred_sem != truth_sem:
            tags.add("semantic_wrong")
        if pred_proof != truth_proof:
            tags.add("proof_safe_wrong")
        if pred_prod != truth_prod:
            tags.add("product_wrong")

        expected_atoms = scorer._truth_atoms(lab)
        pairs, missing, extras = [], [], []
        if cid in compound_ids:
            pairs, missing, extras = scorer.align_atoms(row.get("atom_results", []), expected_atoms)
            if missing:
                tags.add("missing_atom")
                atom_stats["missing_atoms"] += len(missing)
                atom_stats["cases_with_missing"] += 1
            if extras:
                tags.add("extra_atom")
                atom_stats["extra_atoms"] += len(extras)
                atom_stats["cases_with_extra"] += 1
            if missing or extras:
                tags.add("wrong_decomposition")

        case_auto = pred_prod in AUTO
        atom_sound_all = True
        has_accepted = False
        if case_auto:
            sound["auto_cases"] += 1
            for atom in scorer.accepted_auto_proofs(row):
                has_accepted = True
                sound["accepted_atoms"] += 1
                if not scorer.structural_valid(atom, source):
                    sound["structurally_invalid"] += 1
                    atom_sound_all = False
                    tags.add("structurally_invalid_proof")
                if not scorer.grounded(atom, source, evidence_ids):
                    sound["ungrounded"] += 1
                    atom_sound_all = False
                    tags.add("ungrounded_proof")
                if not scorer._allowed_auto(scorer._truth_value(lab, "proof_safe_verdict"),
                                            scorer._atom_route(row, atom)):
                    sound["semantically_unsound"] += 1
                    atom_sound_all = False
                    tags.add("semantically_unsound_proof")
            if has_accepted and atom_sound_all:
                sound["sound_auto_cases"] += 1
                if pred_prod != truth_prod:
                    tags.add("sound_auto_wrong_product")
            if pred_proof != truth_proof:
                sound["proof_safe_unsound_autos"] += 1
                tags.add("proof_safe_unsound_auto")

        if "semantic_wrong" in tags:
            if polarity(pred_sem) != polarity(truth_sem) and polarity(truth_sem) != "NONE" and polarity(pred_sem) != "NONE":
                tags.add("engine_polarity")

        inference = " ".join((a.get("required_inference") or "") for a in expected_atoms)
        rationale = str(lab.get("rationale") or "").lower()
        if "NEGATION" in inference or " ikke " in rationale or "negation" in rationale:
            tags.add("negation")
        if "MODALITY" in inference or "DEONTIC" in inference:
            tags.add("deontic_modal")
        if "ACTOR" in inference:
            tags.add("actor_scope")
        if "NUMERIC" in inference:
            tags.add("numeric")
        if "TEMPORAL" in inference:
            tags.add("temporal")
        if truth_sem == "INSUFFICIENT_EVIDENCE" or lab.get("genuine_insufficiency") is True:
            tags.add("evidence_sufficiency")
        if (truth_prod == "REVIEW_REQUIRED" and pred_prod == "ABSTAIN_INSUFFICIENT") or +           (truth_prod == "ABSTAIN_INSUFFICIENT" and pred_prod == "REVIEW_REQUIRED"):
            tags.add("review_vs_abstain")
        if row.get("reviewer_used"):
            arbitration["reviewer_used"] += 1
            if row.get("route") and row.get("product_action") != row.get("route"):
                arbitration["reviewer_flipped"] += 1
                tags.add("arbitration")
        if case_auto:
            tags.add("auto_proof")
        atoms_all_correct = bool(pairs) and not missing and not extras and all(
            scorer.normalize_semantic(a.get("frozen_verdict") or "") ==
            scorer.normalize_semantic(m.get("semantic_truth") or "")
            for a, m in pairs)
        if cid in compound_ids and atoms_all_correct and pred_prod != truth_prod:
            tags.add("top_level_aggregation")

        classified = tags & {"engine_polarity", "negation", "deontic_modal", "actor_scope",
                             "numeric", "temporal", "evidence_sufficiency", "review_vs_abstain",
                             "wrong_decomposition", "missing_atom", "extra_atom",
                             "structurally_invalid_proof", "ungrounded_proof",
                             "semantically_unsound_proof", "arbitration"}
        if "semantic_wrong" in tags and not classified:
            tags.add("other")

        if "product_wrong" in tags:
            severity["CRITICAL" if case_auto else "HIGH"] += 1
        elif "semantic_wrong" in tags and "proof_safe_wrong" in tags:
            severity["MEDIUM"] += 1
        elif "semantic_wrong" in tags or "proof_safe_wrong" in tags:
            severity["LOW"] += 1
        else:
            severity["OK"] += 1

        for tag in sorted(tags):
            taxonomy[tag.upper()] += 1

        if (pred_sem == truth_sem and pred_proof == truth_proof
                and pred_prod != truth_prod):
            failure_modes["CORRECT_PROOF_WRONG_ROUTING"] += 1
        if "sound_auto_wrong_product" in tags:
            failure_modes["SOUND_AUTO_WRONG_PRODUCT"] += 1
        if "structurally_invalid_proof" in tags:
            failure_modes["STRUCTURALLY_INVALID_PROOF"] += 1
        if "ungrounded_proof" in tags:
            failure_modes["UNGROUNDED_PROOF"] += 1
        if "semantically_unsound_proof" in tags:
            failure_modes["SEMANTICALLY_UNSOUND_PROOF"] += 1
        if "proof_safe_unsound_auto" in tags:
            failure_modes["PROOF_SAFE_UNSOUND_AUTO"] += 1
        if "top_level_aggregation" in tags:
            failure_modes["CORRECT_ATOMS_WRONG_AGGREGATION"] += 1
        if "wrong_decomposition" in tags:
            failure_modes["WRONG_DECOMPOSITION"] += 1

        kinds = []
        if (truth_sem in ("SUPPORTED", "PARTIALLY_SUPPORTED")
                and truth_proof in ("SUPPORTED", "PARTIALLY_SUPPORTED")
                and truth_prod == "ABSTAIN_INSUFFICIENT"):
            kinds.append("SUPPORT_TRUTH_BUT_ABSTAIN_PRODUCT")
        if truth_sem == "INSUFFICIENT_EVIDENCE" and truth_prod in AUTO:
            kinds.append("INSUFFICIENT_TRUTH_BUT_AUTO_PRODUCT")
        if lab.get("genuine_insufficiency") is True and truth_prod != "ABSTAIN_INSUFFICIENT":
            kinds.append("GENUINE_INSUFFICIENCY_NOT_ABSTAIN")
        if (truth_prod == "AUTO_SUPPORTED" and truth_proof == "CONTRADICTED") or +           (truth_prod == "AUTO_CONTRADICTED" and truth_proof == "SUPPORTED"):
            kinds.append("PRODUCT_PROOF_SAFE_POLARITY_MISMATCH")
        for kind in kinds:
            label_error_ids.append({"case_id": cid, "kind": kind})
            label_error_kinds[kind] += 1

    error_ids = {entry["case_id"] for entry in label_error_ids}
    official = json.loads((HERE / "official-generalization-score.json").read_text())
    base_product = official["metrics"]["product_exact"]
    sens_correct = base_product["correct"]
    for row in predictions:
        cid = row["case_id"]
        if cid not in error_ids:
            continue
        lab = labels[cid]
        pred_prod = scorer.normalize_product(row.get("product_action"))
        if (pred_prod != scorer.normalize_product(scorer._truth_value(lab, "product_action"))
                and pred_prod == derived_product(lab)):
            sens_correct += 1
    product_sensitivity = scorer.proportion(sens_correct, base_product["denominator"])
    auto_rows = [(row, labels[row["case_id"]]) for row in predictions
                 if row.get("product_action") in AUTO and row["case_id"] not in error_ids]
    auto_correct = sum(
        scorer._allowed_auto(scorer._truth_value(lab, "proof_safe_verdict"), row.get("product_action"))
        for row, lab in auto_rows)
    auto_sensitivity = scorer.proportion(auto_correct, len(auto_rows))

    result = {
        "task_id": "NAV-EXPLORE-RC3-GENERALIZATION-G2",
        "stage": "POST_FREEZE_ERROR_INSPECTION",
        "official_score_sha256": freeze["official_score_sha256"],
        "cases_analyzed": len(predictions),
        "severity": dict(severity),
        "taxonomy": dict(sorted(taxonomy.items())),
        "failure_modes": dict(failure_modes),
        "atom_alignment": atom_stats,
        "auto_soundness": sound,
        "arbitration": arbitration,
        "label_audit": {
            "status": "REGISTERED_NO_RELABEL",
            "candidate_count": len(error_ids),
            "kinds": dict(label_error_kinds),
            "case_ids": sorted(error_ids),
        },
        "alternate_sensitivity": {
            "product_exact_as_labeled": base_product,
            "product_exact_consistent_relabel_sensitivity": product_sensitivity,
            "auto_precision_excluding_label_error_cases": auto_sensitivity,
            "note": "Sensitivity only. Official score and verdict unchanged.",
        },
    }
    (HERE / "error-analysis.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    (HERE / "label-audit.json").write_text(json.dumps({
        "task_id": "NAV-EXPLORE-RC3-GENERALIZATION-G2",
        "status": "POTENTIAL_GENERALIZATION_LABEL_ERROR_REGISTERED_NO_RELABEL",
        "candidate_count": len(error_ids),
        "kinds": dict(label_error_kinds),
        "case_ids": sorted(error_ids),
        "note": "Official score preserved. No relabel in this run.",
    }, indent=2, ensure_ascii=False))
    print("severity:", dict(severity))
    print("taxonomy:", json.dumps(dict(sorted(taxonomy.items())), ensure_ascii=False))
    print("failure_modes:", dict(failure_modes))
    print("label_audit_candidates:", len(error_ids), dict(label_error_kinds))
    print("product_sensitivity:", product_sensitivity["fraction"], product_sensitivity["percent"])
    print("auto_sensitivity:", auto_sensitivity["fraction"], auto_sensitivity["percent"],
          "denominator:", len(auto_rows))


if __name__ == "__main__":
    main()
