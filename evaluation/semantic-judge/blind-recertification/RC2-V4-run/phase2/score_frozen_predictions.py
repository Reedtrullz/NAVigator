#!/usr/bin/env python3
"""Frozen mechanical scorer for RC2-V4 Phase 2B (written in Phase 2A).

Reads the frozen prediction artifact, applies scoring-policy.json
mechanically to a decrypted answer structure, and writes
official-score.json. The scorer never decrypts anything; Phase 2B
performs authenticated decryption OUTSIDE this script and passes the
validated plaintext structure in.

Self-test mode (--self-test) runs synthetic fixtures only: no RC2B
case ids, no V4 labels, no key material.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SEMANTIC_TARGETS = ["SUPPORTED", "CONTRADICTED",
                    "PARTIALLY_SUPPORTED", "INSUFFICIENT_EVIDENCE"]
PROOF_TARGETS = ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
                 "REVIEW_REQUIRED"]
PRODUCT_CLASSES = ["AUTO_SUPPORTED", "AUTO_CONTRADICTED",
                   "REVIEW_REQUIRED", "ABSTAIN_INSUFFICIENT"]
SEMANTIC_CONFUSION_ORDER = SEMANTIC_TARGETS + \
    ["REVIEW_REQUIRED_PREDICTED_ONLY"]
ALIASES = {"PARTIAL": "PARTIALLY_SUPPORTED",
           "INSUFFICIENT": "INSUFFICIENT_EVIDENCE"}
AUTO_CLASSES = ("AUTO_SUPPORTED", "AUTO_CONTRADICTED")


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def norm_sem(v):
    return ALIASES.get(v, v)


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 6), round(c + h, 6)]


def frac_block(k, n):
    return {"correct": k, "denominator": n,
            "fraction": (k / n if n else None),
            "percent_display": (round(100 * k / n, 2) if n else None),
            "wilson_95": wilson(k, n)}


def _ascii_fold(t):
    return (str(t).lower().translate(str.maketrans(
        {"å": "a", "æ": "ae", "ø": "o",
         "Å": "a", "Æ": "ae", "Ø": "o"})))


def norm_atom_text(t):
    return re.sub(r"\s+", " ", _ascii_fold(t)).strip()


def align_atoms(pred_atoms, key_atoms):
    """Deterministic alignment per frozen policy: atom_id, then
    normalized exact text. Returns (matched, missing, extra)."""
    if pred_atoms and key_atoms and all(
            "atom_id" in a for a in key_atoms) and all(
            "atom_id" in a for a in pred_atoms):
        kid = {a["atom_id"]: a for a in key_atoms}
        matched, extra, seen = [], [], set()
        for p in pred_atoms:
            if p.get("atom_id") in kid:
                matched.append((p, kid[p["atom_id"]]))
                seen.add(p["atom_id"])
            else:
                extra.append(p)
        missing = [a for a in key_atoms if a["atom_id"] not in seen]
        return matched, missing, extra
    ktexts = {}
    for j, a in enumerate(key_atoms):
        t = norm_atom_text(a.get("atom_text") or a.get("text") or "")
        if t:
            ktexts.setdefault(t, j)
    matched, missing, extra = [], [], []
    used = set()
    for p in pred_atoms:
        pt = norm_atom_text(p.get("atom_text") or p.get("text") or "")
        j = ktexts.get(pt)
        if pt and j is not None and j not in used:
            used.add(j)
            matched.append((p, key_atoms[j]))
        else:
            extra.append(p)
    missing = [a for j, a in enumerate(key_atoms) if j not in used]
    return matched, missing, extra


def load_answer_structure(raw, pred_ids):
    """Structural answer-key validation (score-order step 2)."""
    if isinstance(raw, dict) and "cases" in raw:
        cases = raw["cases"]
    elif isinstance(raw, dict):
        cases = [{"case_id": k, **v} for k, v in raw.items()]
    else:
        cases = raw
    by_id, problems = {}, []
    for c in cases:
        cid = c.get("case_id")
        if not cid:
            problems.append("case without case_id")
            continue
        if cid in by_id:
            problems.append("duplicate key case %s" % cid)
        by_id[cid] = c
    missing = [i for i in pred_ids if i not in by_id]
    extra = [i for i in by_id if i not in set(pred_ids)]
    if missing:
        problems.append("key missing case ids: %s" % missing[:5])
    if extra:
        problems.append("key extra case ids: %s" % extra[:5])
    for cid, c in by_id.items():
        if norm_sem(c.get("semantic_truth")) not in SEMANTIC_TARGETS:
            problems.append("%s bad semantic_truth" % cid)
        if c.get("proof_safe") not in PROOF_TARGETS:
            problems.append("%s bad proof_safe" % cid)
        if c.get("product_expected_action") not in PRODUCT_CLASSES:
            problems.append("%s bad product_expected_action" % cid)
        if c.get("criticality") not in ("CRITICAL", "STANDARD"):
            problems.append("%s bad criticality" % cid)
        if not isinstance(c.get("final_flags"), list):
            problems.append("%s bad final_flags" % cid)
        if "compound" in (c.get("final_flags") or []):
            atoms = c.get("atom_labels")
            if not isinstance(atoms, list) or not atoms:
                problems.append("%s compound without atom_labels" % cid)
            else:
                for a in atoms:
                    if norm_sem(a.get("semantic_truth")) not in \
                            SEMANTIC_TARGETS:
                        problems.append("%s atom bad semantic_truth" % cid)
                        break
    return by_id, problems


def structural_proof_rederivation(pred_row, blind_case):
    """Deterministic re-derivation on accepted routes (no model calls).
    Returns list of failure reasons (empty = structurally valid)."""
    if pred_row.get("runtime_status") != "OK":
        return ["runtime_failure"]
    sj = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    for p in (os.path.join(sj, "rc2-development", "engine"),
              os.path.join(sj, "rc2-development"),
              os.path.join(sj, "hybrid")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import polarity_engine_v02 as E  # noqa
    from auto_gate import auto_gate  # noqa
    src = "\n\n".join(s["text"] for s in blind_case["sources"])
    fails = []
    try:
        res = E.judge_claim(blind_case["claim"], src)
        recorded = (pred_row.get("proof_object") or {}).get("engine") or {}
        if res.get("verdict") != recorded.get("verdict"):
            fails.append("engine_verdict_not_reproduced")
    except Exception as exc:
        fails.append("engine_rerun_exception:%s" % type(exc).__name__)
        return fails
    if pred_row.get("reviewer_used"):
        try:
            from reviewer import build_packet, validate_fidelity
            reason = auto_gate(blind_case["claim"], src, res)
            packet = build_packet(blind_case["claim"], src, res, reason)
            fid = validate_fidelity(packet, pred_row.get("reviewer_output")
                                    or {})
            if fid:
                fails.append("fidelity:%s" % fid)
        except Exception as exc:
            fails.append("packet_exception:%s" % type(exc).__name__)
    return fails


def score(predictions_path, blind_cases_path, answer_path, policy_path,
          output_path, structural_rederivation=True, expected_rows=160):
    policy = json.load(open(policy_path, encoding="utf-8"))
    got_pred_sha = sha256_file(predictions_path)
    if got_pred_sha != policy["prediction_artifact"]["sha256"]:
        sys.exit("ABORT: prediction SHA mismatch: %s" % got_pred_sha)
    art = json.load(open(predictions_path, encoding="utf-8"))
    rows = art["predictions"]
    ids = [r["case_id"] for r in rows]
    if len(rows) != expected_rows or len(set(ids)) != expected_rows:
        sys.exit("ABORT: prediction rows are not %d unique cases"
                 % expected_rows)
    blind = {c["case_id"]: c for c in json.load(
        open(blind_cases_path, encoding="utf-8"))["cases"]}
    key, problems = load_answer_structure(
        json.load(open(answer_path, encoding="utf-8")), ids)
    if problems:
        sys.exit("ABORT: answer-key structural validation failed:\n" +
                 "\n".join(problems))

    sem_ok = proof_ok = prod_ok = 0
    auto_rows, auto_proof_ok, auto_prod_ok = [], 0, 0
    invalid_proofs, hallucinated = [], []
    crit_unsafe = {"AUTO_SUPPORTED": [], "AUTO_CONTRADICTED": []}
    sem_conf, proof_conf, prod_conf = Counter(), Counter(), Counter()
    review, abstain, subgroup = Counter(), Counter(), Counter()
    compound_rows = []
    atom_correct = atom_den = 0
    atom_mismatch = {}
    comp_prod_ok = 0
    for r in rows:
        cid = r["case_id"]
        k = key[cid]
        flags = set(k.get("final_flags") or [])
        rt_fail = r.get("runtime_status") != "OK"
        prod_hit = (not rt_fail) and \
            r.get("product_action") == k["product_expected_action"]
        for f in flags:
            subgroup["%s:product_total" % f] += 1
            if prod_hit:
                subgroup["%s:product_correct" % f] += 1
        if norm_sem(k["semantic_truth"]) == "INSUFFICIENT_EVIDENCE":
            subgroup["insufficiency:product_total"] += 1
            if prod_hit:
                subgroup["insufficiency:product_correct"] += 1
        if rt_fail:
            sem_conf[("RUNTIME_FAILURE",
                      norm_sem(k["semantic_truth"]))] += 1
            proof_conf[("RUNTIME_FAILURE", k["proof_safe"])] += 1
            prod_conf[("RUNTIME_FAILURE",
                       k["product_expected_action"])] += 1
        else:
            psem = norm_sem(r.get("semantic_verdict"))
            sem_ok += psem == norm_sem(k["semantic_truth"])
            sem_conf[(psem, norm_sem(k["semantic_truth"]))] += 1
            pproof = r.get("proof_safe_verdict")
            proof_ok += pproof == k["proof_safe"]
            proof_conf[(pproof, k["proof_safe"])] += 1
            pprod = r.get("product_action")
            prod_ok += prod_hit
            prod_conf[(pprod, k["product_expected_action"])] += 1
            if pprod in AUTO_CLASSES:
                auto_rows.append(cid)
                pb_ok = ((pprod == "AUTO_SUPPORTED" and
                          k["proof_safe"] == "SUPPORTED") or
                         (pprod == "AUTO_CONTRADICTED" and
                          k["proof_safe"] == "CONTRADICTED"))
                auto_proof_ok += pb_ok
                auto_prod_ok += prod_hit
                if not pb_ok:
                    invalid_proofs.append({"case_id": cid,
                                           "kind": "exceeds_proof_safe"})
                if structural_rederivation:
                    struct = structural_proof_rederivation(r, blind[cid])
                    if struct:
                        invalid_proofs.append({"case_id": cid,
                                               "kind": "structural",
                                               "detail": struct})
                    if any(s == "engine_verdict_not_reproduced" or
                           s.startswith("fidelity:") for s in struct):
                        hallucinated.append({"case_id": cid,
                                             "detail": struct})
                if k["criticality"] == "CRITICAL" and not prod_hit:
                    crit_unsafe[pprod].append(cid)
            if pprod == "REVIEW_REQUIRED":
                review["pred"] += 1
                review["tp"] += prod_hit
            if k["product_expected_action"] == "REVIEW_REQUIRED" and \
                    not prod_hit:
                review["fn"] += 1
            if pprod == "ABSTAIN_INSUFFICIENT":
                abstain["pred"] += 1
                abstain["tp"] += prod_hit
            if k["product_expected_action"] == "ABSTAIN_INSUFFICIENT" and \
                    not prod_hit:
                abstain["fn"] += 1
        if "compound" in flags:
            compound_rows.append(cid)
            comp_prod_ok += prod_hit
            pred_atoms = ((r.get("proof_object") or {}).get("engine")
                          or {}).get("atom_results") or []
            matched, missing, extra = align_atoms(
                pred_atoms, k.get("atom_labels") or [])
            if missing or extra:
                atom_mismatch[cid] = {"missing_expected": len(missing),
                                      "extra_predicted": len(extra)}
            atom_den += len(k.get("atom_labels") or [])
            atom_correct += sum(
                1 for p, a in matched
                if norm_sem(p.get("verdict")) ==
                norm_sem(a.get("semantic_truth")))
    critical_ids = [c for c, v in key.items()
                    if v["criticality"] == "CRITICAL"]
    row_by_id = {r["case_id"]: r for r in rows}
    crit_prod_ok = sum(
        1 for cid in critical_ids
        if row_by_id[cid].get("runtime_status") == "OK" and
        row_by_id[cid].get("product_action") ==
        key[cid]["product_expected_action"])

    def conf_to_matrix(order_key, order_pred, counter):
        return {pk: {pp: counter.get((pp, pk), 0)
                     for pp in order_pred} for pk in order_key}

    n = len(rows)
    review["fp"] = review["pred"] - review["tp"]
    abstain["fp"] = abstain["pred"] - abstain["tp"]
    auto_n = len(auto_rows)
    gates = [
        {"gate": "semantic_exact_accuracy >= 0.90",
         "actual": sem_ok / n, "required_min": 0.90,
         "pass": sem_ok / n >= 0.90},
        {"gate": "proof_safe_exact_accuracy >= 0.95",
         "actual": proof_ok / n, "required_min": 0.95,
         "pass": proof_ok / n >= 0.95},
        {"gate": "product_exact_accuracy >= 0.95",
         "actual": prod_ok / n, "required_min": 0.95,
         "pass": prod_ok / n >= 0.95},
        {"gate": "combined_auto_precision_proof_based >= 0.99",
         "actual": (auto_proof_ok / auto_n) if auto_n else None,
         "required_min": 0.99,
         "pass": auto_n > 0 and auto_proof_ok / auto_n >= 0.99},
        {"gate": "critical_product_exact_accuracy == 1.00",
         "actual": crit_prod_ok / len(critical_ids),
         "required_exact": 1.00,
         "pass": crit_prod_ok == len(critical_ids)},
        {"gate": "compound_atom_accuracy >= 0.90",
         "actual": (atom_correct / atom_den) if atom_den else None,
         "required_min": 0.90,
         "pass": atom_den > 0 and atom_correct / atom_den >= 0.90},
        {"gate": "compound_product_accuracy >= 0.90",
         "actual": (comp_prod_ok / len(compound_rows))
         if compound_rows else None,
         "required_min": 0.90,
         "pass": bool(compound_rows) and
         comp_prod_ok / len(compound_rows) >= 0.90},
        {"gate": "invalid_accepted_proofs == 0",
         "actual": len(invalid_proofs), "required_max": 0,
         "pass": not invalid_proofs},
        {"gate": "hallucinated_proofs == 0",
         "actual": len(hallucinated), "required_max": 0,
         "pass": not hallucinated},
        {"gate": "critical_unsafe_AUTO_SUPPORTED == 0",
         "actual": len(crit_unsafe["AUTO_SUPPORTED"]), "required_max": 0,
         "pass": not crit_unsafe["AUTO_SUPPORTED"]},
        {"gate": "critical_unsafe_AUTO_CONTRADICTED == 0",
         "actual": len(crit_unsafe["AUTO_CONTRADICTED"]), "required_max": 0,
         "pass": not crit_unsafe["AUTO_CONTRADICTED"]},
        {"gate": "unhandled_runtime_exception == 0",
         "actual": sum(1 for r in rows
                       if r.get("runtime_status") != "OK"),
         "required_max": 0,
         "pass": all(r.get("runtime_status") == "OK" for r in rows)},
    ]
    verdict = "RC2_CERTIFIED" if all(g["pass"] for g in gates) \
        else "RC2_NOT_CERTIFIED"
    out = {
        "meta": {
            "policy_id": policy["policy_id"],
            "scoring_policy": "scoring-policy.json (frozen before key)",
            "prediction_sha256": got_pred_sha,
            "answer_structural_validation": "PASS",
            "runtime_failures": sum(1 for r in rows
                                    if r.get("runtime_status") != "OK"),
            "atom_count_mismatch_cases": atom_mismatch,
        },
        "semantic_exact": frac_block(sem_ok, n),
        "proof_safe_exact": frac_block(proof_ok, n),
        "product_exact": frac_block(prod_ok, n),
        "auto_precision": {
            "proof_based_primary": frac_block(auto_proof_ok, auto_n),
            "product_based_secondary": frac_block(auto_prod_ok, auto_n),
            "auto_case_ids": auto_rows,
        },
        "critical_product_exact": frac_block(crit_prod_ok,
                                             len(critical_ids)),
        "compound": {
            "product_exact": frac_block(comp_prod_ok,
                                        len(compound_rows)),
            "atom_accuracy": frac_block(atom_correct, atom_den),
        },
        "invalid_accepted_proofs": invalid_proofs,
        "hallucinated_proofs": hallucinated,
        "critical_unsafe_autos": crit_unsafe,
        "review_metrics": {
            "predicted": review["pred"], "tp": review["tp"],
            "fp": review["fp"], "fn": review["fn"],
            "precision": (review["tp"] / review["pred"]
                          if review["pred"] else None),
            "recall": (review["tp"] / (review["tp"] + review["fn"])
                       if review["tp"] + review["fn"] else None)},
        "abstain_metrics": {
            "predicted": abstain["pred"], "tp": abstain["tp"],
            "fp": abstain["fp"], "fn": abstain["fn"],
            "note": "RC2 never predicts abstain; reported mechanically"},
        "confusion": {
            "semantic_key_rows_by_prediction_columns":
                conf_to_matrix(SEMANTIC_TARGETS,
                               SEMANTIC_CONFUSION_ORDER, sem_conf),
            "proof_safe": conf_to_matrix(PROOF_TARGETS, PROOF_TARGETS,
                                         proof_conf),
            "product": conf_to_matrix(PRODUCT_CLASSES, PRODUCT_CLASSES,
                                      prod_conf),
        },
        "subgroups_product_exact": {
            f: frac_block(subgroup.get("%s:product_correct" % f, 0),
                          subgroup.get("%s:product_total" % f, 0))
            for f in sorted(set(k.split(":")[0] for k in subgroup))},
        "gates": gates,
        "verdict": verdict,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("WROTE %s verdict=%s" % (output_path, verdict))
    return out


def _fixture_row(cid, sem, proof, prod, rt="OK", atoms=None,
                 reviewer=False):
    return {"case_id": cid, "semantic_verdict": sem,
            "proof_safe_verdict": proof, "product_action": prod,
            "runtime_status": rt, "reviewer_used": reviewer,
            "proof_object": {"engine": {"atom_results": atoms or []},
                             "route": ("auto" if prod in AUTO_CLASSES
                                       else "review")}}


def _fixture_case(cid, sem, proof, prod, crit="STANDARD", flags=None,
                  atoms=None):
    c = {"case_id": cid, "semantic_truth": sem, "proof_safe": proof,
         "product_expected_action": prod, "criticality": crit,
         "final_flags": flags or []}
    if atoms is not None:
        c["atom_labels"] = atoms
    return c


def _run_fixture_score(preds_path, key_path, policy_path, out_path):
    """Run score() on synthetic fixtures with expected_rows=5
    (all scoring rules unchanged; production default is 160)."""
    import score_frozen_predictions as S
    return S.score(preds_path, key_path, key_path, policy_path, out_path,
                   structural_rederivation=False, expected_rows=5)


def self_test():
    """Synthetic fixtures; no RC2B ids, no V4 labels, no key."""
    import tempfile
    assert wilson(0, 0) is None and wilson(8, 8)[0] > 0.6
    pa = [{"atom_id": "A1", "atom_text": "Kommunen krever henvisning",
           "verdict": "SUPPORTED"},
          {"atom_id": "A2", "atom_text": "Det gjelder alle",
           "verdict": "CONTRADICTED"}]
    ka = [{"atom_id": "A1", "atom_text": "Kommunen krever henvisning",
           "semantic_truth": "SUPPORTED"},
          {"atom_id": "A2", "atom_text": "Det gjelder alle",
           "semantic_truth": "CONTRADICTED"}]
    m, miss, extra = align_atoms(pa, ka)
    assert len(m) == 2 and not miss and not extra
    m, miss, extra = align_atoms(pa[:1], ka)
    assert len(m) == 1 and len(miss) == 1 and not extra
    m, miss, extra = align_atoms(pa, ka[:1])
    assert len(m) == 1 and not miss and len(extra) == 1
    m, miss, extra = align_atoms(
        [{"atom_text": " det gjelder alle ", "verdict": "CONTRADICTED"}],
        ka)
    assert len(m) == 1 and m[0][1]["atom_id"] == "A2"
    assert norm_sem("PARTIAL") == "PARTIALLY_SUPPORTED"
    assert norm_sem("INSUFFICIENT") == "INSUFFICIENT_EVIDENCE"
    key = {"cases": [
        _fixture_case("T-0001", "SUPPORTED", "SUPPORTED",
                      "AUTO_SUPPORTED"),
        _fixture_case("T-0002", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
                      "REVIEW_REQUIRED"),
        _fixture_case("T-0003", "INSUFFICIENT_EVIDENCE",
                      "INSUFFICIENT_EVIDENCE", "ABSTAIN_INSUFFICIENT"),
        _fixture_case("T-0004", "SUPPORTED", "SUPPORTED",
                      "AUTO_SUPPORTED", "CRITICAL", ["safety"]),
        _fixture_case("T-0005", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
                      "REVIEW_REQUIRED", "CRITICAL",
                      ["age_legal", "compound"],
                      [{"atom_id": "A1",
                        "semantic_truth": "CONTRADICTED"},
                       {"atom_id": "A2",
                        "semantic_truth": "SUPPORTED"}]),
    ]}
    preds = {"predictions": [
        _fixture_row("T-0001", "SUPPORTED", "SUPPORTED",
                     "AUTO_SUPPORTED"),
        _fixture_row("T-0002", "REVIEW_REQUIRED",
                     "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"),
        _fixture_row("T-0003", "REVIEW_REQUIRED",
                     "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"),
        _fixture_row("T-0004", "SUPPORTED", "SUPPORTED",
                     "AUTO_SUPPORTED"),
        _fixture_row("T-0005", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
                     "AUTO_CONTRADICTED",
                     atoms=[{"atom_id": "A1", "atom_text": "x",
                             "verdict": "CONTRADICTED"}]),
    ]}
    tmp = tempfile.mkdtemp()
    pp = os.path.join(tmp, "p.json")
    kp = os.path.join(tmp, "k.json")
    op = os.path.join(tmp, "o.json")
    polp = os.path.join(tmp, "policy.json")
    json.dump(preds, open(pp, "w"))
    json.dump(key, open(kp, "w"))
    policy = {"policy_id": "TEST",
              "prediction_artifact": {"sha256": sha256_file(pp)}}
    json.dump(policy, open(polp, "w"))
    out = _run_fixture_score(pp, kp, polp, op)
    assert out["semantic_exact"]["correct"] == 3, out["semantic_exact"]
    assert out["product_exact"]["correct"] == 3
    assert out["proof_safe_exact"]["correct"] == 5
    assert out["auto_precision"]["proof_based_primary"]["correct"] == 2
    assert out["auto_precision"]["proof_based_primary"]["denominator"] == 3
    assert out["critical_product_exact"]["correct"] == 1
    assert out["compound"]["product_exact"]["correct"] == 0
    assert out["compound"]["product_exact"]["denominator"] == 1
    assert out["critical_unsafe_autos"]["AUTO_CONTRADICTED"] == ["T-0005"]
    assert out["invalid_accepted_proofs"]
    assert out["gates"][-1]["pass"] is True
    assert out["verdict"] == "RC2_NOT_CERTIFIED"
    assert out["abstain_metrics"]["predicted"] == 0
    assert out["abstain_metrics"]["fn"] == 1
    assert (out["review_metrics"]["tp"] == 1 and
            out["review_metrics"]["fp"] == 1 and
            out["review_metrics"]["fn"] == 1)
    assert out["compound"]["atom_accuracy"]["correct"] == 1
    assert out["compound"]["atom_accuracy"]["denominator"] == 2
    assert out["meta"]["atom_count_mismatch_cases"]["T-0005"] == \
        {"missing_expected": 1, "extra_predicted": 0}
    preds["predictions"][0]["runtime_status"] = "RUNTIME_FAILURE"
    json.dump(preds, open(pp, "w"))
    policy["prediction_artifact"]["sha256"] = sha256_file(pp)
    json.dump(policy, open(polp, "w"))
    out = _run_fixture_score(pp, kp, polp, op)
    assert out["semantic_exact"]["correct"] == 2
    assert out["product_exact"]["correct"] == 2
    assert out["proof_safe_exact"]["correct"] == 4
    assert out["meta"]["runtime_failures"] == 1
    print("SELF-TEST OK (synthetic fixtures only)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--predictions")
    ap.add_argument("--blind-cases")
    ap.add_argument("--answer")
    ap.add_argument("--policy",
                    default=os.path.join(HERE, "scoring-policy.json"))
    ap.add_argument("--output",
                    default=os.path.join(HERE, "official-score.json"))
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not (a.predictions and a.blind_cases and a.answer):
        ap.error("--predictions --blind-cases --answer required "
                 "(or --self-test)")
    score(a.predictions, a.blind_cases, a.answer, a.policy, a.output)


if __name__ == "__main__":
    main()
