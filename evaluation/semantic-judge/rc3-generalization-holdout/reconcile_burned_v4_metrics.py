"""BURNED_V4_METRIC_RECONCILIATION_ONLY (spec 3-6 of the task).

Re-runs the frozen RC3 engine over the burned V4 blind cases in
memory and computes the five separated proof-metric categories of
proof-soundness-contract-v2. The historical
rc3-development/burned-v4-shadow-results.json is NOT modified.
Labels are decrypted in memory only; only aggregate counts and
class codes are persisted. No case text, no per-case labels.
NOT certification. NOT tuning evidence. NOT threshold search.
"""
import base64
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SEM = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(SEM, "rc3-development", "rc3_engine"))
import engine_rc3 as eng  # noqa: E402
import routing as rt  # noqa: E402

SETS = os.path.join(SEM, "blind-recertification", "RC2-V4-set")
PSAFE_AUTO_ALLOW = {"SUPPORTED": "AUTO_SUPPORTED",
                    "CONTRADICTED": "AUTO_CONTRADICTED"}


def load_labels():
    """Memory-only authenticated decryption (Phase-2B convention)."""
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
    cases = json.load(open(os.path.join(SETS, "blind-cases.json")))
    cases = cases["cases"]
    labels = load_labels()
    m = Counter()
    runtime_failures = 0
    accepted_n = 0
    auto_n = 0
    for c in cases:
        src = "\n\n".join(s["text"] for s in c["sources"])
        lab = labels[c["case_id"]]["final"]
        try:
            out = eng.judge_claim(c["claim"], src)
        except Exception:
            runtime_failures += 1
            continue
        routes = []
        for atom in out["atoms"]:
            state = atom["proof_state"]
            if state != "ENGINE_PROOF_ACCEPTED":
                routes.append(atom.get("final_verdict",
                                      "REVIEW_REQUIRED"))
                continue
            accepted_n += 1
            p = atom.get("proof") or {}
            if not p or not p.get("source_span"):
                m["structural_invalid_accepted_proofs"] += 1
                routes.append("REVIEW_REQUIRED")
                continue
            if p["source_span"] not in src:
                m["ungrounded_accepted_proofs"] += 1
                routes.append("REVIEW_REQUIRED")
                continue
            verdict = atom["final_verdict"]
            if verdict in ("AUTO_SUPPORTED", "AUTO_CONTRADICTED"):
                # M3 semantic soundness (spec 4 invariant, atom
                # granularity): an accepted auto whose conclusion the
                # sealed proof-safe target does not allow is unsound,
                # regardless of structural validity.
                allow = PSAFE_AUTO_ALLOW.get(
                    lab.get("proof_safe"))
                if allow != verdict:
                    m["semantically_unsound_accepted_proofs"] += 1
            routes.append(verdict)
        product = rt.aggregate_atoms(
            [{"route": r} for r in routes])["product_action"]
        if product in ("AUTO_SUPPORTED", "AUTO_CONTRADICTED"):
            auto_n += 1
            # M4 proof-safe auto correctness: the case-level auto is
            # PROOF_SAFE_UNSOUND when the sealed proof-safe target
            # does not allow exactly this auto polarity.
            allow = PSAFE_AUTO_ALLOW.get(lab.get("proof_safe"))
            if allow != product:
                m["proof_safe_unsound_autos"] += 1
            # M5 product action correctness (autos only).
            if product != lab.get("product_action"):
                m["wrong_product_autos"] += 1
    result = {
        "run_type": "BURNED_V4_METRIC_RECONCILIATION_ONLY",
        "burned_marker": "BURNED_BLIND_DEVELOPMENT_ONLY",
        "not_certification": True,
        "no_tuning_based_on_result": True,
        "historical_shadow_artifact": "rc3-development/burned-v4-shadow-results.json (unchanged)",
        "n_cases": len(cases),
        "runtime_failures": runtime_failures,
        "accepted_proofs_total": accepted_n,
        "autos_total": auto_n,
        "structural_invalid_accepted_proofs":
        m["structural_invalid_accepted_proofs"],
        "ungrounded_accepted_proofs":
        m["ungrounded_accepted_proofs"],
        "semantically_unsound_accepted_proofs":
        m["semantically_unsound_accepted_proofs"],
        "proof_safe_unsound_autos":
        m["proof_safe_unsound_autos"],
        "wrong_product_autos": m["wrong_product_autos"],
        "labels_persisted": False,
        "case_ids_persisted": False,
    }
    path = os.path.join(HERE, "burned-v4-metric-reconciliation.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
