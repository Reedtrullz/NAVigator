#!/usr/bin/env python3
"""Seal the holdout answer key + construction audit (AES-256-GCM).

Key is generated via secrets.token_bytes(32), printed once to stdout
and never written to disk. AAD binds the seal to the exact bytes of
generalization-cases.json. Removes all plaintext label material after
a successful roundtrip verification.
"""
import base64
import hashlib
import json
import secrets
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "construction-audit"


def main():
    cases_bytes = (HERE / "generalization-cases.json").read_bytes()
    cases_sha = hashlib.sha256(cases_bytes).hexdigest()
    aad = cases_sha.encode("ascii")

    final = json.loads((AUDIT / "labels-final.json")
                       .read_text(encoding="utf-8"))
    adj = json.loads((AUDIT / "adjudication.json")
                     .read_text(encoding="utf-8"))
    sel = json.loads((AUDIT / "selection.json").read_text(encoding="utf-8"))
    core_ids = set(sel["core_ids"])
    final_core = {k: v for k, v in final.items() if k in core_ids}
    key_payload = {
        "task_id": "NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION",
        "set_id": "RC3G-HOLDOUT-V1",
        "cases_sha256": cases_sha,
        "aad_convention": "AAD = ASCII bytes of lowercase hex sha256 "
                          "digest of the exact generalization-cases.json "
                          "file bytes",
        "labels": final_core,
        "adjudication": adj,
    }
    plaintext = json.dumps(key_payload, ensure_ascii=False,
                           indent=1).encode("utf-8")

    key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(12)
    sealed = AESGCM(key).encrypt(nonce, plaintext, aad)
    blob = {"alg": "AES-256-GCM", "nonce": base64.b64encode(nonce).decode(),
            "aad": cases_sha, "ciphertext":
            base64.b64encode(sealed).decode()}
    (HERE / "answer-key.sealed").write_text(
        json.dumps(blob, indent=1) + "\n", encoding="utf-8")

    audit_payload = {
        "cases-pass1": json.loads((AUDIT / "cases-pass1.json")
                                  .read_text(encoding="utf-8")),
        "labels-pass2": json.loads((AUDIT / "labels-pass2.json")
                                   .read_text(encoding="utf-8")),
        "labels-final": final,
        "agreement": json.loads((AUDIT / "agreement.json")
                                .read_text(encoding="utf-8")),
        "adjudication": adj,
        "selection": sel,
        "novelty-pass1": json.loads((AUDIT / "novelty-pass1.json")
                                    .read_text(encoding="utf-8")),
        "quota-pass1": json.loads((AUDIT / "quota-pass1.json")
                                  .read_text(encoding="utf-8")),
    }
    # Construction scripts embed per-case label codes; they are part of
    # the sealed audit material, not runner-accessible plaintext.
    SOURCE_FILES = ["case_list_a.py", "case_list_b1.py", "case_list_b2.py",
                    "case_list_b3.py", "adjudicate_resolve.py",
                    "pass2-run.log"]
    audit_payload["source_files"] = {
        name: (AUDIT / name).read_text(encoding="utf-8")
        if (AUDIT / name).exists()
        else (HERE / name).read_text(encoding="utf-8")
        for name in SOURCE_FILES}
    audit_plain = json.dumps(audit_payload, ensure_ascii=False,
                             indent=1).encode("utf-8")
    nonce2 = secrets.token_bytes(12)
    sealed2 = AESGCM(key).encrypt(nonce2, audit_plain, aad)
    blob2 = {"alg": "AES-256-GCM", "nonce":
             base64.b64encode(nonce2).decode(), "aad": cases_sha,
             "ciphertext": base64.b64encode(sealed2).decode()}
    (HERE / "construction-audit.sealed").write_text(
        json.dumps(blob2, indent=1) + "\n", encoding="utf-8")

    # Roundtrip verification before cleanup
    rb = json.loads((HERE / "answer-key.sealed").read_text(encoding="utf-8"))
    dec = AESGCM(key).decrypt(base64.b64decode(rb["nonce"]),
                              base64.b64decode(rb["ciphertext"]),
                              rb["aad"].encode("ascii"))
    assert json.loads(dec)["labels"].keys() == final_core.keys()
    rb2 = json.loads((HERE / "construction-audit.sealed")
                     .read_text(encoding="utf-8"))
    dec2 = AESGCM(key).decrypt(base64.b64decode(rb2["nonce"]),
                               base64.b64decode(rb2["ciphertext"]),
                               rb2["aad"].encode("ascii"))
    assert json.loads(dec2)["labels-pass2"].keys()

    manifest = json.loads((HERE / "blind-manifest.json")
                          .read_text(encoding="utf-8"))
    manifest["status"] = "SEALED"
    manifest["sealed_key_sha256"] = hashlib.sha256(
        (HERE / "answer-key.sealed").read_bytes()).hexdigest()
    (HERE / "blind-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    # Plaintext cleanup: labels must leave the runner-accessible tree.
    import shutil
    shutil.rmtree(AUDIT)
    for name in SOURCE_FILES:
        p = HERE / name
        if p.exists():
            p.unlink()
    shutil.rmtree(HERE / "__pycache__", ignore_errors=True)

    key_b64 = base64.urlsafe_b64encode(key).decode().rstrip("=")
    print("SEALED answer-key.sealed + construction-audit.sealed")
    print("cases_sha256=" + cases_sha)
    print("RC3_GENERALIZATION_KEY=" + key_b64)


if __name__ == "__main__":
    main()
