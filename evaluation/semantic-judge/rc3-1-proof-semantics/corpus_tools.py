#!/usr/bin/env python3
"""RC3.1 proof-development corpus utilities.

Case validation, burned-set novelty guard, quota accounting, and the
AES-256-GCM validation-key seal (same convention as G2: AAD binds the
exact validation-cases.json bytes; key printed once, never stored).
"""
import base64
import hashlib
import json
import re
import secrets
from collections import Counter
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = Path(__file__).resolve().parent

RELATIONS = ("ENTAILS", "CONTRADICTS", "PARTIAL",
             "RELATED_BUT_INSUFFICIENT", "UNRELATED", "AMBIGUOUS")
SEM_FROM_REL = {
    "ENTAILS": "SUPPORTED",
    "CONTRADICTS": "CONTRADICTED",
    "PARTIAL": "PARTIALLY_SUPPORTED",
    "RELATED_BUT_INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
    "UNRELATED": "INSUFFICIENT_EVIDENCE",
    "AMBIGUOUS": "REVIEW_REQUIRED",
}
PS_FROM_REL = dict(SEM_FROM_REL)
PRODUCT_FROM_REL = {
    "ENTAILS": "AUTO_SUPPORTED",
    "CONTRADICTS": "AUTO_CONTRADICTED",
    "PARTIAL": "REVIEW_REQUIRED",
    "RELATED_BUT_INSUFFICIENT": "ABSTAIN_INSUFFICIENT",
    "UNRELATED": "ABSTAIN_INSUFFICIENT",
    "AMBIGUOUS": "REVIEW_REQUIRED",
}

MIN_QUOTAS = {
    "negation": 35,
    "modality": 35,
    "condition": 30,
    "actor": 25,
    "numeric": 25,
    "compound": 60,
}
_SHAPE_TO_QUOTA = {
    "negation": "negation",
    "modality": "modality",
    "condition": "condition",
    "exception": "condition",
    "actor": "actor",
    "scope": "actor",
    "numeric": "numeric",
    "temporal": "numeric",
    "compound": "compound",
}

_ID_RE = re.compile(r"^RC31-\d{4}$")
_SHINGLES_RE = re.compile(r"[a-zæøå]+")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def validate_case(case, kb_root="."):
    """Structural validation for one RC31 case dict."""
    errors = []
    if not _ID_RE.match(case.get("case_id", "")):
        errors.append("bad case_id")
    if not case.get("claim", "").strip():
        errors.append("empty claim")
    if case.get("track") not in ("A", "B"):
        errors.append("track must be A or B")
    sources = case.get("sources", [])
    if not sources:
        errors.append("no sources")
    for s in sources:
        ref = s.get("kb_ref", "")
        p = Path(kb_root) / ref.split("kb/", 1)[-1]
        if not p.exists():
            errors.append("missing kb file: " + ref)
        if not s.get("text", "").strip():
            errors.append("empty source text in " + ref)
    span_ids = {e.get("span_id") for e in case.get("evidence", [])}
    if len(span_ids) != len(case.get("evidence", [])):
        errors.append("duplicate span ids")
    atoms = case.get("atoms", [])
    if case.get("compound") and len(atoms) < 2:
        errors.append("compound case must have >= 2 atoms")
    if not case.get("compound") and atoms:
        errors.append("non-compound case must not declare atoms")
    seen = set()
    for a in atoms:
        aid = a.get("atom_id", "")
        if not re.match(r"^A\d+$", aid):
            errors.append("bad atom_id " + aid)
        if aid in seen:
            errors.append("duplicate atom_id " + aid)
        seen.add(aid)
        if not a.get("text", "").strip():
            errors.append("empty atom text " + aid)
        for sid in a.get("evidence_span_ids", []):
            if sid not in span_ids:
                errors.append("atom %s refs unknown span %s" % (aid, sid))
    for e in case.get("evidence", []):
        stext = e.get("text", "")
        if stext and not any(stext in s.get("text", "")
                             for s in sources):
            errors.append("evidence %s not contained in any source"
                          % e.get("span_id"))
    return errors


def _shingles(text, n=3):
    toks = _SHINGLES_RE.findall(text.lower())
    if len(toks) < n:
        return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def load_burned_claims(holdout_dir):
    p = Path(holdout_dir) / "generalization-cases.json"
    cases = json.loads(p.read_text(encoding="utf-8"))["cases"]
    return [c["claim"] for c in cases]


def check_novelty(claims, burned_claims, threshold=0.55):
    """Reject rewrites of burned public claims (Jaccard >= threshold)."""
    burned_sets = [(c, _shingles(c)) for c in burned_claims]
    flagged = []
    for claim in claims:
        cs = _shingles(claim)
        best_id, best = None, 0.0
        for bid, bs in burned_sets:
            inter = len(cs & bs)
            union = len(cs | bs) or 1
            j = inter / union
            if j > best:
                best, best_id = j, bid
        if best >= threshold:
            flagged.append({"claim": claim, "burned_case_id": best_id,
                            "jaccard": round(best, 3)})
    return flagged


def shape_quotas(entries):
    """Overlap allowed: a case counts toward every bucket it carries
    (spec 24). Compound counts only real >=2-atom case dicts."""
    counts = Counter()
    for e in entries:
        for shape in e.get("shapes", []):
            bucket = _SHAPE_TO_QUOTA.get(shape)
            if bucket:
                counts[bucket] += 1
    # compound quota must reflect actual compound cases, not tags
    counts["compound"] = sum(
        1 for e in entries
        if e.get("compound") or e.get("atoms"))
    return dict(counts)


def check_quotas(entries):
    counts = shape_quotas(entries)
    missing = {k: v for k, v in MIN_QUOTAS.items()
               if counts.get(k, 0) < v}
    return counts, missing


def relation_balance(entries):
    return dict(Counter(e["rel"] for e in entries))


def seal_validation_key(validation_cases_path, labels, out_path,
                       task_id="NAV-EXPLORE-RC3_1-PROOF-SEMANTICS-REPAIR"):
    """Seal validation labels; return (key_hex, seal_path).

    labels: {case_id: {"relation": rel}} from the authoring entries;
    public case dicts carry no relation field by design.
    """
    cases_bytes = Path(validation_cases_path).read_bytes()
    aad = sha256_bytes(cases_bytes).encode("ascii")
    labels_out = {}
    for cid, lab in labels.items():
        rel = lab["relation"]
        rec = {
            "relation": rel,
            "semantic_verdict": SEM_FROM_REL[rel],
            "proof_safe_verdict": PS_FROM_REL[rel],
            "product_action": PRODUCT_FROM_REL[rel],
        }
        if "expected_atoms" in lab:
            rec["expected_atoms"] = lab["expected_atoms"]
        labels_out[cid] = rec
    payload = {
        "schema": 2,
        "task_id": task_id,
        "set_id": "RC31-PROOF-DEV-VALIDATION",
        "cases_sha256": aad.decode("ascii"),
        "aad_convention": "AAD = ASCII bytes of lowercase hex sha256 "
                          "digest of the exact validation-cases.json "
                          "file bytes",
        "labels": labels_out,
    }
    plaintext = json.dumps(payload, ensure_ascii=False,
                           indent=1).encode("utf-8")
    key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(12)
    blob = {"alg": "AES-256-GCM",
            "nonce": base64.b64encode(nonce).decode(),
            "aad": aad.decode("ascii"),
            "ciphertext": base64.b64encode(
                AESGCM(key).encrypt(nonce, plaintext, aad)).decode()}
    Path(out_path).write_text(json.dumps(blob, indent=1) + "\n",
                              encoding="utf-8")
    return key.hex(), str(out_path)


def open_validation_key(sealed_path, validation_cases_path):
    """Open the seal with the hex key stored beside it (.key file)."""
    blob = json.loads(Path(sealed_path).read_text(encoding="utf-8"))
    aad = sha256_bytes(
        Path(validation_cases_path).read_bytes()).encode("ascii")
    key = bytes.fromhex(Path(str(sealed_path) + ".key").read_text()
                        .strip())
    plain = AESGCM(key).decrypt(
        base64.b64decode(blob["nonce"]),
        base64.b64decode(blob["ciphertext"]), aad)
    return json.loads(plain.decode("utf-8"))
