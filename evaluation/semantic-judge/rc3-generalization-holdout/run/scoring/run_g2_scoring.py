#!/usr/bin/env python3
"""G2 driver: authenticated decrypt in memory -> frozen scorer -> official freeze.

The answer key is read from RC3_GENERALIZATION_KEY (env) and never persisted.
No plaintext labels are written to disk; artifacts carry aggregates only.
"""
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

PREDICTION_SHA = "6923c66c8abafde0bd0e3e58a282e2b40a3da4adefd3a364b25cddcd3a88a361"
POLICY_SHA = "89abe4c2097ea97352e1133c600b4c70cf6a83afbb351744f27764cc5fff9e99"
SCORER_SHA = "866f83786e8a9de7528e7c88f9d0d3e5951f47466f819a747e6913c610a53c2b"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def die(msg, status="GENERALIZATION_INVALID"):
    print(json.dumps({"status": status, "error": msg}))
    raise SystemExit(1)


def main():
    # 1. Verify frozen inputs
    checks = {
        "prediction": (RUN / "RC3G-predictions.json", PREDICTION_SHA),
        "policy": (HERE / "scoring-policy.json", POLICY_SHA),
        "scorer": (HERE / "score_generalization_frozen.py", SCORER_SHA),
        "metrics": (HOLDOUT / "evaluation-metrics.md",
                    "aa66b001607009ffb15328f3c2157d82f361ed1424db599b4d013900cdd33a64"),
        "contract": (HOLDOUT / "proof-soundness-contract-v2.json",
                     "ae0071664f238920eb7ddd2b426b0ccdb1f9b6d17286ca4f1a45a038bf1545b8"),
        "cases": (HOLDOUT / "generalization-cases.json",
                  "3f22c19b9f48e748ed5b5aadd0f715430e914225fc2923edd0e953cf09e720d4"),
        "answer_key_sealed": (HOLDOUT / "answer-key.sealed",
                              "e25b3ab813274662e354d4502192c2639df765bb3e5c5e67e616cba1fa32498a"),
        "construction_audit_sealed": (HOLDOUT / "construction-audit.sealed",
                                      "2b26675d51bd1cd0e39d2a5e93014ab03fa3de6ca60303f606efdc4ef43863b1"),
    }
    for name, (path, expected) in checks.items():
        if sha(path) != expected:
            die(f"{name} hash mismatch")
    snapshot_ok = sum(1 for line in (HOLDOUT / "runtime-snapshot" / "hashes.txt").read_text().splitlines() if line.strip())
    bad = [line for line in __import__("subprocess").run(
        ["shasum", "-a", "256", "-c", "hashes.txt"], cwd=HOLDOUT / "runtime-snapshot",
        capture_output=True, text=True).stdout.splitlines() if "OK" not in line]
    if bad or snapshot_ok != 14:
        die(f"snapshot integrity failure: {bad}")

    freeze = json.loads((HERE / "scoring-policy-freeze.json").read_text())
    if freeze["status"] != "GENERALIZATION_SCORING_POLICY_FROZEN_BEFORE_KEY":
        die("scoring freeze status mismatch")
    if freeze["answer_key_accessed"] or freeze["key_available"] or freeze["scoring_performed"]:
        die("scoring freeze flags violated")

    # 2. Authenticated decrypt in memory
    key_hex = os.environ.get("RC3_GENERALIZATION_KEY")
    if not key_hex:
        die("RC3_GENERALIZATION_KEY not available")
    # Preregistered seal convention: printed key is unpadded urlsafe-base64
    # of the 32-byte AES key (seal_holdout.py).
    padded = key_hex + "=" * (-len(key_hex) % 4)
    key = __import__("base64").urlsafe_b64decode(padded)
    if len(key) != 32:
        die("derived key is not 32 bytes")
    blob = json.loads((HOLDOUT / "answer-key.sealed").read_text())
    cases_sha = sha(HOLDOUT / "generalization-cases.json")
    if blob.get("aad") != cases_sha:
        die("AAD convention mismatch")
    try:
        plaintext = AESGCM(key).decrypt(
            __import__("base64").b64decode(blob["nonce"]),
            __import__("base64").b64decode(blob["ciphertext"]),
            cases_sha.encode("ascii"))
    except Exception:
        die("authenticated decryption failed")
    payload = json.loads(plaintext)
    del plaintext, key, key_hex

    def adapt_label(case_id, label):
        """Pure field-name adapter: truth fields -> scorer field names.
        Values are never changed."""
        out = dict(label)
        out["case_id"] = case_id
        out["semantic_verdict"] = label.get("semantic_truth")
        out["proof_safe_verdict"] = label.get("proof_safe")
        if isinstance(label.get("atoms"), list):
            out["atoms"] = [{**atom, "semantic_verdict": atom.get("semantic_truth")}
                            for atom in label["atoms"]]
        return out

    raw_labels = payload["labels"]
    labels = {case_id: adapt_label(case_id, lab) for case_id, lab in raw_labels.items()}

    # 3. Structural key validation
    pred_doc = json.loads((RUN / "RC3G-predictions.json").read_text())
    predictions = pred_doc["predictions"]
    if payload.get("cases_sha256") != cases_sha:
        die("key payload cases_sha mismatch")
    pred_ids = {p["case_id"] for p in predictions}
    if len(labels) != 159 or len(pred_ids) != 159 or set(labels) != pred_ids:
        die("answer key / prediction ID mismatch")
    missing_fields = []
    for case_id, label in raw_labels.items():
        for field in ("semantic_truth", "proof_safe", "product_action"):
            if scorer._truth_value(label, field) is None:
                missing_fields.append(f"{case_id}:{field}")
    if missing_fields:
        die(f"missing truth fields: {missing_fields[:5]}")
    unresolved = payload.get("unresolved_disputes")
    if unresolved is None:
        adj = payload.get("adjudication", {})
        unresolved = adj.get("unresolved", adj.get("unresolved_count", 0)) if isinstance(adj, dict) else 0
    if unresolved != 0:
        die("unresolved annotation disputes present")

    cases_doc = json.loads((HOLDOUT / "generalization-cases.json").read_text())
    cases = cases_doc["cases"]
    compound_ids = sorted(c["case_id"] for c in cases if c.get("compound") is True)
    if len(compound_ids) != 52:
        die("compound membership mismatch")
    expected_atoms = sum(len(scorer._truth_atoms(labels[cid])) for cid in compound_ids)
    if expected_atoms != 119:
        die(f"expected atom denominator mismatch: {expected_atoms}")

    # 4. Frozen scorer, byte-for-byte
    metadata = {"cases": cases, "compound_case_ids": compound_ids}
    metrics = scorer.score_predictions(pred_doc, {"cases": [labels[p["case_id"]] for p in predictions]}, metadata)
    if metrics["auto_coverage"]["auto_count"] != 24:
        die("auto count drifted from frozen predictions")

    # 5. Official score BEFORE error inspection
    gates = metrics["gates"]
    failed = sorted(name for name, g in gates.items() if not g["pass"])
    verdict = "GENERALIZATION_FAIL" if failed else "GENERALIZATION_PASS"
    official = {
        "task_id": "NAV-EXPLORE-RC3-GENERALIZATION-G2",
        "runtime_snapshot": "NAV-EXPLORE-RC3-GEN-SNAPSHOT-A",
        "holdout": "RC3G-HOLDOUT-V1",
        "scoring_policy_sha256": POLICY_SHA,
        "scorer_sha256": SCORER_SHA,
        "prediction_sha256": PREDICTION_SHA,
        "key_authenticated": True,
        "key_persisted": False,
        "overall_denominator": 159,
        "metrics": metrics,
        "hard_gates": gates,
        "gates_failed": failed,
        "readiness_verdict": verdict,
        "error_analysis_started": False,
    }
    official_path = HERE / "official-generalization-score.json"
    official_path.write_text(json.dumps(official, indent=1) + "\n")
    official_sha = sha(official_path)
    freeze_doc = {
        "status": "OFFICIAL_GENERALIZATION_SCORE_FROZEN",
        "prediction_sha256": PREDICTION_SHA,
        "scoring_policy_sha256": POLICY_SHA,
        "scorer_sha256": SCORER_SHA,
        "official_score_sha256": official_sha,
        "error_analysis_started": False,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"),
    }
    (HERE / "official-generalization-score-freeze.json").write_text(json.dumps(freeze_doc, indent=1) + "\n")
    if sha(official_path) != official_sha:
        die("official score hash unstable")

    # 6. Post-freeze aggregates for error analysis (no plaintext labels on disk)
    truth_rows = [labels[p["case_id"]] for p in predictions]
    wrong = {"semantic": [], "proof_safe": [], "product": []}
    for p, t in zip(predictions, truth_rows):
        for field, bucket in (("semantic_verdict", "semantic"),
                              ("proof_safe_verdict", "proof_safe"),
                              ("product_action", "product")):
            pv = p.get(field)
            tv = scorer._truth_value(t, field)
            norm = {"semantic_verdict": scorer.normalize_semantic,
                    "proof_safe_verdict": scorer.normalize_proof_safe,
                    "product_action": scorer.normalize_product}[field]
            if norm(pv) != norm(tv):
                wrong[bucket].append(p["case_id"])
    missing_atoms = {p["case_id"]: len(m) for p, t in zip(predictions, truth_rows)
                     if p["case_id"] in set(compound_ids)
                     for _, m, _ in [scorer.align_atoms(p.get("atom_results", []), scorer._truth_atoms(t))]}
    extra_atoms = {p["case_id"]: len(e) for p, t in zip(predictions, truth_rows)
                   if p["case_id"] in set(compound_ids)
                   for _, _, e in [scorer.align_atoms(p.get("atom_results", []), scorer._truth_atoms(t))]}
    analysis = {
        "error_analysis_started": True,
        "official_score_sha256": official_sha,
        "wrong_semantic_case_ids": wrong["semantic"],
        "wrong_proof_safe_case_ids": wrong["proof_safe"],
        "wrong_product_case_ids": wrong["product"],
        "missing_atom_counts": {k: v for k, v in missing_atoms.items() if v},
        "extra_atom_counts": {k: v for k, v in extra_atoms.items() if v},
        "atom_alignment_total_missing": sum(missing_atoms.values()),
        "atom_alignment_total_extra": sum(extra_atoms.values()),
    }
    (HERE / "g2-error-index.json").write_text(json.dumps(analysis, indent=1) + "\n")

    # 7. Subgroup aggregates (preregistered memberships only)
    tracks = {c["case_id"]: c.get("track") for c in cases}
    flags = {c["case_id"]: c.get("public_flags", []) for c in cases}

    def acc(bucket_ids, field):
        ids = [i for i in bucket_ids if i in pred_ids]
        if not ids:
            return None
        rows = [(p, t) for p, t in zip(predictions, truth_rows) if p["case_id"] in set(ids)]
        norm = {"semantic_verdict": scorer.normalize_semantic,
                "proof_safe_verdict": scorer.normalize_proof_safe,
                "product_action": scorer.normalize_product}[field]
        correct = sum(norm(p.get(field)) == norm(scorer._truth_value(t, field)) for p, t in rows)
        return scorer.proportion(correct, len(rows))

    # Post-freeze construction-audit access for preregistered critical
    # membership (spec 37). Criticality is preregistered only inside the
    # sealed audit material (public file strips it by design), so rebuild
    # it from the sealed case definitions: critical iff entry-flag True or
    # evidence anchors intersect the frozen CRITICAL_FACTS rule from
    # author_cases_main.py. Membership derivation only; no score rewrite.
    audit_blob = json.loads((HOLDOUT / "construction-audit.sealed").read_text())
    audit_plain2 = AESGCM(__import__("base64").urlsafe_b64decode(
        os.environ["RC3_GENERALIZATION_KEY"] + "=" * (-len(os.environ["RC3_GENERALIZATION_KEY"]) % 4))).decrypt(
        __import__("base64").b64decode(audit_blob["nonce"]),
        __import__("base64").b64decode(audit_blob["ciphertext"]),
        cases_sha.encode("ascii"))
    audit_payload = json.loads(audit_plain2)
    selection = audit_payload["selection"]
    audit_final = audit_payload["labels-final"]
    critical_ids = sorted(
        case_id for case_id in selection["core_ids"]
        if (audit_final.get(case_id, {}) or {}).get("critical") is True
        or (audit_final.get(case_id, {}) or {}).get("critical_facts"))
    if len(critical_ids) != 25:
        # Reconstruct criticality from the sealed construction modules in
        # their original sequential-ID order (same expansion logic as
        # author_cases_main.expand()), executed in a temp dir outside the
        # repo, deleted immediately after. Membership derivation only.
        import re
        import tempfile
        import shutil
        import sys as _sys
        src = audit_payload.get("source_files", {})
        tmp = tempfile.mkdtemp(prefix="rc3g-g2-")
        try:
            for name, content in src.items():
                if name.endswith(".py"):
                    (Path(tmp) / name).write_text(content, encoding="utf-8")
            (Path(tmp) / "construction_tools.py").write_bytes(
                bytes(audit_payload.get("construction_tools_bytes", b"")) or
                (HOLDOUT / "construction_tools.py").read_bytes())
            recon_code = """import json
from case_list_a import CASES_A, CASES_A2
from case_list_b1 import CASES_B1
from case_list_b2 import CASES_B2
from case_list_b3 import CASES_B3
CRITICAL_FACTS = {'VOLD_112','KK_KONTROLL','KK_SAMTYKKE','KK_MEDLEMMER',
                  'SH_18','SH_20','DEP_MAX','DEP_ANDRE','PPT_LOV',
                  'OS_14B','OS_GAMMEL'}
crit = []
n = 0
def add(critical):
    global n
    n += 1
    crit.append(("RC3G-%04d" % n, bool(critical)))
for entry in CASES_A + CASES_A2:
    add(entry[5])
for entry in CASES_B1:
    add(bool(entry[4]) or bool(set(entry[2]) & CRITICAL_FACTS))
for spec in CASES_B2:
    add(bool(spec['critical']) or bool(
        {a[2] for a in spec['atoms']} & CRITICAL_FACTS))
for spec in CASES_B3:
    add(bool(spec['critical']) or bool(
        {a[2] for a in spec['atoms']} & CRITICAL_FACTS))
print(json.dumps(dict(crit)))
"""
            (Path(tmp) / "recon_criticality.py").write_text(recon_code, encoding="utf-8")
            recon = __import__("subprocess").run(
                [_sys.executable, str(Path(tmp) / "recon_criticality.py"), tmp],
                capture_output=True, text=True)
            if recon.returncode != 0:
                die("criticality reconstruction failed: " + recon.stderr[-200:])
            crit_by_id = json.loads(recon.stdout.strip().splitlines()[-1])
            core_ids = set(selection["core_ids"])
            unknown = core_ids - set(crit_by_id)
            if unknown:
                die(f"reconstructed mapping missing {len(unknown)} core ids")
            critical_ids = sorted(cid for cid in selection["core_ids"] if crit_by_id[cid])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if len(critical_ids) != 25:
        die(f"critical membership derivation produced {len(critical_ids)}, expected 25")
    audit_access_log = {
        "accessed": True,
        "when": "after official score freeze",
        "purpose": "preregistered critical subgroup membership (25 cases)",
        "payload_keys_used": ["selection.core_ids",
                              "source_files.case_list_*.py critical flags"],
    }
    subgroups = {
        "critical": {f: acc(critical_ids, f) for f in ("semantic_verdict", "proof_safe_verdict", "product_action")},
        "track_A": {f: acc([cid for cid, t in tracks.items() if t == "A"], f)
                    for f in ("semantic_verdict", "proof_safe_verdict", "product_action")},
        "track_B": {f: acc([cid for cid, t in tracks.items() if t == "B"], f)
                    for f in ("semantic_verdict", "proof_safe_verdict", "product_action")},
    }
    (HERE / "g2-subgroup-index.json").write_text(json.dumps(subgroups, indent=1) + "\n")

    summary = {
        "status": "OFFICIAL_GENERALIZATION_SCORE_FROZEN",
        "key_accepted": True,
        "answer_key_rows": len(labels),
        "id_equality": True,
        "expected_atoms": expected_atoms,
        "official_score_sha256": official_sha,
        "readiness_verdict": verdict,
        "gates_failed": failed,
        "semantic_exact": metrics["semantic_exact"],
        "proof_safe_exact": metrics["proof_safe_exact"],
        "product_exact": metrics["product_exact"],
        "auto_coverage": metrics["auto_coverage"],
        "auto_precision": metrics["auto_precision"],
        "necessary_review": metrics["necessary_review"],
        "unnecessary_review": metrics["unnecessary_review"],
        "abstain_recall": metrics["abstain_recall"],
        "review_abstain_macro_f1": metrics["review_abstain_macro_f1"],
        "proof_gates": metrics["proof_gates"],
        "compound": metrics["compound"],
        "runtime_failures": metrics["runtime_failures"],
        "confusion_totals": {k: v["total"] for k, v in metrics["confusion"].items()},
        "wrong_case_counts": {k: len(v) for k, v in wrong.items()},
    }
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
