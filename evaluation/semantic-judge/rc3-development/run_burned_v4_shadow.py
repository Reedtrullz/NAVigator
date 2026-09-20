"""RC3_BURNED_V4_SHADOW_ONLY (one pass, post-freeze, spec 51-53).

Runs the frozen RC3 engine over the 160 burned V4 cases. The sealed V4
answer key is decrypted IN MEMORY ONLY for aggregate scoring: no
plaintext is persisted, no per-case label appears in the output.
No reviewer calls are made: the frozen RC2 reviewer transport output
cannot satisfy RC3 span-fidelity validation offline (no candidate
span offsets were frozen), so reviewer proposals would fail closed
to metadata-only. Per spec 52 nothing is tuned after this run.
NOT certification, NOT blind evidence, NOT threshold optimization.
"""
import base64
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SEM = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "rc3_engine"))
import engine_rc3 as eng  # noqa: E402
import routing as rt  # noqa: E402

SETS = os.path.join(SEM, "blind-recertification", "RC2-V4-set")


def load_labels():
    """Memory-only authenticated decryption (RC2 Phase-2B convention)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    body = os.environ["BLIND_RC2_V4_KEY"].rstrip("=")
    key = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
    env = json.load(open(os.path.join(SETS, "answer-key.sealed")))
    nonce = base64.urlsafe_b64decode(env["nonce"])
    ct = base64.urlsafe_b64decode(env["ciphertext"])
    aad = base64.urlsafe_b64decode(env["associated_data"])
    pt = AESGCM(key).decrypt(nonce, ct, aad)
    data = json.loads(pt)
    cases = data["cases"] if isinstance(data, dict) \
        and "cases" in data else data
    return {c["case_id"]: c for c in cases}


def main():
    set_cases = json.load(open(os.path.join(SETS,
                                            "blind-cases.json")))
    set_cases = set_cases["cases"]
    labels = load_labels()
    rows = []
    runtime_failures = 0
    invalid_proofs = 0
    sem_ok = psafe_ok = prod_ok = 0
    crit_n = crit_ok = 0
    comp_n = comp_prod_ok = comp_atom_count_ok = 0
    auto_n = auto_ok = 0
    abstain_n = abstain_ok = 0
    reason_counts = Counter()
    for c in set_cases:
        cid = c["case_id"]
        claim = c["claim"]
        src = "\n\n".join(s["text"] for s in c["sources"])
        lab = labels[cid]
        truth = lab["final"]["semantic_truth"]
        psafe_truth = lab["final"]["proof_safe"]
        prod_truth = lab["final"]["product_action"]
        critical = lab["criticality"].upper() in ("HIGH", "CRITICAL")
        try:
            out = eng.judge_claim(claim, src)
        except Exception as exc:
            runtime_failures += 1
            rows.append({"case_id": cid,
                         "product": "RUNTIME_FAILURE",
                         "error": type(exc).__name__})
            continue
        routes = []
        reasons = []
        fvs = []
        for atom in out["atoms"]:
            fvs.append(atom.get("frozen_verdict"))
            p = atom.get("proof")
            if atom["proof_state"] == "ENGINE_PROOF_ACCEPTED":
                if (not p or not p.get("source_span")
                        or p["source_span"] not in src):
                    invalid_proofs += 1
                routes.append(atom["final_verdict"])
            elif atom["proof_state"] in ("ENGINE_UNSAFE",
                                         "ENGINE_CONFLICT"):
                routes.append("REVIEW_REQUIRED")
                reasons.append("engine_unsafe_guard")
            else:
                route = rt.route_atom(atom, claim, src)
                if route == "REVIEW_REQUIRED":
                    reasons.append("no_bounded_proof")
                routes.append(route)
        product = rt.aggregate_atoms(
            [{"route": r} for r in routes])["product_action"]
        # Shadow semantic display: engine-layer verdicts only.
        if product == "AUTO_SUPPORTED":
            sem = "SUPPORTED"
        elif product == "AUTO_CONTRADICTED":
            sem = "CONTRADICTED"
        elif product == "ABSTAIN_INSUFFICIENT":
            sem = "INSUFFICIENT_EVIDENCE"
        else:
            uni = set(fvs)
            sem = fvs[0] if len(uni) == 1 and fvs[0] else None
        psafe = {"AUTO_SUPPORTED": "SUPPORTED",
                 "AUTO_CONTRADICTED": "CONTRADICTED",
                 "ABSTAIN_INSUFFICIENT":
                 "INSUFFICIENT_EVIDENCE"}.get(
            product,
            "INSUFFICIENT_EVIDENCE"
            if product == "REVIEW_REQUIRED" else product)
        sem_ok += sem == truth
        psafe_ok += psafe == psafe_truth
        prod_ok += product == prod_truth
        if critical:
            crit_n += 1
            crit_ok += product == prod_truth
        if "compound" in (lab.get("final_flags") or []):
            comp_n += 1
            comp_prod_ok += product == prod_truth
            lab_atoms = lab.get("atom_labels") or []
            comp_atom_count_ok += \
                len(out["atoms"]) == len(lab_atoms)
        if product in ("AUTO_SUPPORTED", "AUTO_CONTRADICTED"):
            auto_n += 1
            auto_ok += product == prod_truth
        if product == "ABSTAIN_INSUFFICIENT":
            abstain_n += 1
            abstain_ok += prod_truth == "ABSTAIN_INSUFFICIENT"
        reason_counts.update(reasons)
        rows.append({"case_id": cid, "product": product,
                     "review_reasons": reasons})
    prods = Counter(r["product"] for r in rows)
    out = {
        "run_type": "RC3_BURNED_V4_SHADOW_ONLY",
        "burned_marker": "BURNED_BLIND_DEVELOPMENT_ONLY",
        "not_certification": True,
        "not_blind_evidence": True,
        "no_tuning_after_run": True,
        "labels": "decrypted in memory only; no plaintext persisted",
        "reviewer_calls": 0,
        "reviewer_note": "no groundable frozen spans; fail-closed",
        "n": len(rows),
        "runtime_failures": runtime_failures,
        "semantic_shadow": {"correct": sem_ok, "denominator": len(rows),
                            "fraction": round(sem_ok / len(rows), 4)},
        "proof_safe_shadow": {"correct": psafe_ok,
                              "denominator": len(rows),
                              "fraction": round(psafe_ok / len(rows), 4)},
        "product_shadow": {"correct": prod_ok,
                           "denominator": len(rows),
                           "fraction": round(prod_ok / len(rows), 4)},
        "auto_precision_shadow": {"correct": auto_ok,
                                  "denominator": auto_n,
                                  "fraction":
                                  round(auto_ok / auto_n, 4)
                                  if auto_n else None},
        "critical_product_shadow": {"correct": crit_ok,
                                    "denominator": crit_n,
                                    "fraction":
                                    round(crit_ok / crit_n, 4)
                                    if crit_n else None},
        "compound_product_shadow": {"correct": comp_prod_ok,
                                    "denominator": comp_n,
                                    "fraction":
                                    round(comp_prod_ok / comp_n, 4)
                                    if comp_n else None},
        "compound_atom_count_exact": {"correct": comp_atom_count_ok,
                                      "denominator": comp_n,
                                      "fraction":
                                      round(comp_atom_count_ok / comp_n,
                                            4) if comp_n else None},
        "invalid_accepted_proofs": invalid_proofs,
        "review_rate": round(prods.get("REVIEW_REQUIRED", 0)
                             / len(rows), 4),
        "abstain_behavior": {"predicted_abstain": abstain_n,
                             "correct_abstain": abstain_ok},
        "product_distribution": dict(prods),
        "review_reason_counts": dict(reason_counts),
        "rows": rows,
    }
    path = os.path.join(HERE, "burned-v4-shadow-results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k != "rows"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
