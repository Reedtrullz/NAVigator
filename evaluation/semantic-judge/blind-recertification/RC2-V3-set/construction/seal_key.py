#!/usr/bin/env python3
"""Build the V3 answer key from the annotated pool, seal it AES-256-GCM, verify roundtrip, print key once."""
import base64
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SLOTS = ("semantic_truth", "proof_safe", "product_action")


def main():
    pool = json.load(open(f"{HERE}/pool-annotated.json"))
    sel = json.load(open(f"{HERE}/selection.json"))
    blind_sha = hashlib.sha256(open(f"{ROOT}/blind-cases.json", "rb").read()).hexdigest()
    aad = base64.urlsafe_b64encode(bytes.fromhex(blind_sha)).decode().rstrip("=") + "=="
    key = os.urandom(32)
    key_b64 = base64.urlsafe_b64encode(key).decode().rstrip("=") + "=="
    entries = []
    for cid in sel["core"]:
        c = next(x for x in pool["cases"] if x["case_id"] == cid)
        entry = {
            "case_id": cid,
            "final": {s: c["final"][s] for s in SLOTS},
            "flags": c["final_flags"],
            "pass1": {s: c["pass1"][s] for s in SLOTS},
            "pass2": {s: c["pass2"][s] for s in SLOTS},
            "adjudicated": "rationale" in c["final"],
            "provenance": c["provenance"],
            "primary_kb": c["primary_kb"],
        }
        if "rationale" in c["final"]:
            entry["rationale"] = c["final"]["rationale"]
            atoms = [seg.strip() for seg in c["final"]["rationale"].split(";") if seg.strip()]
            entry["atoms"] = [{"description": a[:160], "outcome": c["final"]["semantic_truth"] if len(atoms) == 1 else ("mixed" if any(w in a.lower() for w in ("silent-absent", "contradicted", "unsupported", "unstated")) else c["final"]["semantic_truth"])} for a in atoms]
        entries.append(entry)
    key_doc = {
        "set_version": "NAV-EXPLORE-RC2-BLIND-V3",
        "created": "2026-09-04",
        "note": "Atom rows are documented per contract v3 for adjudicated compound/rider cases; single-atom and pass-agreed cases carry the triple + flags only. Rationale text doubles as the atom narrative where present.",
        "cases": entries,
    }
    plaintext = json.dumps(key_doc, ensure_ascii=False, separators=(",", ":")).encode()
    nonce = os.urandom(12)
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    ct = AESGCM(key).encrypt(nonce, plaintext, blind_sha.encode())
    env = {
        "algorithm": "AES-256-GCM",
        "nonce": base64.urlsafe_b64encode(nonce).decode().rstrip("=") + "==",
        "ciphertext": base64.urlsafe_b64encode(ct).decode().rstrip("=") + "==",
        "associated_data": aad,
    }
    json.dump(env, open(f"{ROOT}/answer-key.sealed", "w"), indent=1)
    back = AESGCM(key).decrypt(nonce, ct, blind_sha.encode())
    assert json.loads(back) == json.loads(plaintext), "roundtrip mismatch"
    print("ROUNDTRIP_OK")
    print("entries:", len(entries))
    print("blind_cases_sha256:", blind_sha)
    print("BLIND_RC2_V3_KEY=" + key_b64)


if __name__ == "__main__":
    sys.exit(main())
