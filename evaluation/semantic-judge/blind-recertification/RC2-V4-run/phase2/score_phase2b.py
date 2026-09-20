#!/usr/bin/env python3
"""Phase 2B scoring driver.

Contains no key material: reads BLIND_RC2_V4_KEY from the environment,
decrypts answer-key.sealed in memory (AES-256-GCM, manifest AAD
convention), validates the structure, and feeds the plaintext to the
FROZEN scorer through an unlinked /tmp FIFO so no plaintext answer key
ever touches the filesystem. The FIFO is removed in a finally block.
"""
import base64
import json
import os
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, ".."))
SETS = os.path.abspath(os.path.join(HERE, "..", ".."))
V4 = os.path.join(SETS, "RC2-V4-set")
sys.path.insert(0, HERE)
import score_frozen_predictions as S  # frozen scorer, byte-for-byte

VALID_STATUS = {"two_pass_agreed", "adjudicated", "agreed",
                "adjudicated_structural"}


def die(msg):
    print("ABORT:", msg)
    sys.exit(1)


def main():
    key_b64 = os.environ.get("BLIND_RC2_V4_KEY", "")
    if not key_b64:
        die("BLIND_RC2_V4_KEY not set")
    # Preregistered key encoding (seal_key.py convention): urlsafe b64,
    # padding stripped, exactly "==" appended. Same decode helper as
    # run_phase_b_band_analysis.py.
    body = key_b64.rstrip("=")
    key = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
    if len(key) != 32:
        die("key must decode to 32 bytes")
    print("KEY_ACCEPTED = TRUE")

    env = json.load(open(os.path.join(V4, "answer-key.sealed")))
    nonce = base64.urlsafe_b64decode(env["nonce"])
    ct = base64.urlsafe_b64decode(env["ciphertext"])
    aad = base64.urlsafe_b64decode(env["associated_data"])
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    try:
        pt = AESGCM(key).decrypt(nonce, ct, aad)
    except Exception as exc:
        die("authenticated decryption failed: %s" % type(exc).__name__)
    print("AES_AUTH_OK | plaintext bytes:", len(pt))
    answer = json.loads(pt)
    cases = answer["cases"] if isinstance(answer, dict) and "cases" in answer else answer
    # Structural adapter: project sealed key fields onto the flat dict
    # form the frozen scorer's load_answer_structure already validates.
    # No labels are read, compared, or transformed; field mapping only.
    cases = [{
        "case_id": c["case_id"],
        "semantic_truth": c["final"]["semantic_truth"],
        "proof_safe": c["final"]["proof_safe"],
        "product_expected_action": c["final"]["product_action"],
        "criticality": c["criticality"].upper(),
        "final_flags": c["final_flags"],
        "atom_labels": c.get("atoms"),
        "annotation_status": c["annotation_status"],
    } for c in cases]

    pred_path = os.path.join(RUN, "RC2-V4-predictions.json")
    pred = json.load(open(pred_path))
    pids = [r["case_id"] for r in pred["predictions"]]
    aids = [c["case_id"] for c in cases]
    if len(cases) != 160 or len(set(aids)) != 160:
        die("answer rows not 160 unique")
    if set(aids) != set(pids):
        die("answer/prediction id mismatch")
    for f in ("semantic_truth", "proof_safe", "product_expected_action",
              "criticality", "final_flags"):
        n = sum(1 for c in cases if c.get(f) not in (None, "", []))
        if n != 160:
            die("field %s present on %d/160" % (f, n))
    n = sum(1 for c in cases
            if "compound" in (c.get("final_flags") or [])
            and c.get("atom_labels"))
    if n != 62:
        die("atom_labels present on %d/62 compound cases" % n)
    bad = sorted({c.get("annotation_status") for c in cases} - VALID_STATUS)
    if bad:
        die("invalid annotation_status values: %s" % bad)
    comp = [c for c in cases if "compound" in (c.get("final_flags") or [])]
    atoms = sum(len(c.get("atom_labels") or []) for c in comp)
    crit = sum(1 for c in cases if c.get("criticality") == "CRITICAL")
    if len(comp) != 62 or atoms != 141 or crit != 40:
        die("preregistered counts mismatch: compound=%d atoms=%d critical=%d"
            % (len(comp), atoms, crit))
    print("STRUCTURAL_VALIDATION_OK | rows=160 | compound=62 | atoms=%d | critical=%d"
          % (atoms, crit))

    fifo = os.path.join(tempfile.gettempdir(),
                        "rc2v4_answer_%d.fifo" % os.getpid())
    os.mkfifo(fifo)
    try:
        # Feed the ADAPTED structure (flat fields), not the raw nested
        # plaintext: the frozen scorer validates the flat schema.
        def feed():
            with open(fifo, "wb") as f:
                f.write(json.dumps({"cases": cases},
                                   ensure_ascii=False).encode("utf-8"))
        t = threading.Thread(target=feed)
        t.start()
        result = S.score(
            pred_path,
            os.path.join(V4, "blind-cases.json"),
            fifo,
            os.path.join(HERE, "scoring-policy.json"),
            os.path.join(HERE, "official-score.json"),
            structural_rederivation=True)
        t.join()
    finally:
        if os.path.exists(fifo):
            os.unlink(fifo)
    print("FIFO_CLEANED =", not os.path.exists(fifo))
    print("VERDICT:", result["verdict"])
    print(json.dumps({k: v for k, v in result.items()
                      if k in ("semantic_exact", "proof_safe_exact",
                               "product_exact", "auto_precision",
                               "critical_product_exact", "compound",
                               "review_metrics", "abstain_metrics",
                               "subgroups_product_exact", "gates",
                               "invalid_accepted_proofs",
                               "hallucinated_proofs",
                               "critical_unsafe_autos", "meta")},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
