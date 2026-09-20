#!/usr/bin/env python3
"""V4 construction QA regressions (spec 36).

Live gate: plaintext-label scan over the whole project (key never needed).
Fixture checks: atom completeness, criticality, subgroup metadata, two-pass
coverage, aggregation consistency, retired-key reuse. Run with no args for
the live gate; import the check_* functions or run qa-tests for the rest.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RETIRED_KEY_FINGERPRINT = "7a3a1488afcc8287adc4ac295f535081cac6c5e98bda9b01afe40d8122a233e4"
ID_RE = re.compile(r"RC2B-\d{4}")
TOKENS = [
    "semantic_truth", "proof_safe", "product_action",
    "AUTO_SUPPORTED", "AUTO_CONTRADICTED", "ABSTAIN_INSUFFICIENT",
    "REVIEW_REQUIRED", "INSUFFICIENT_EVIDENCE", "PARTIALLY_SUPPORTED",
    "CONTRADICTED", "SUPPORTED",
]
SEALED_OK = ("answer-key.sealed", "construction-audit.sealed")
INCIDENTAL_ALLOW = {
    "semantic-judge/blind-recertification/RC2-V2-set/annotation-summary.md",
    "semantic-judge/blind-recertification/RC2-V2-set/blind-manifest.json",
    "semantic-judge/blind-recertification/RC2-V2-set/final-report.md",
    "semantic-judge/blind-recertification/RC2-V2-set/quota-report.md",
    "semantic-judge/blind-recertification/RC2-V3-set/construction/annot-prompt.txt",
    "semantic-judge/blind-recertification/RC2-V3-set/final-report.md",
    "semantic-judge/blind-recertification/RC2-V3-set/v2-selection-qa-root-cause.md",
    "semantic-judge/blind-recertification/V2-construction-audit.md",
}
SUBGROUP_FLAGS = {"safety", "legal", "numeric", "temporal", "locality",
                  "modality", "actor", "cond_exc", "compound", "multi_span", "age_legal"}
ATOM_SEM = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"}


def scan_label_bearing(project=PROJECT):
    leaks = []
    for dirpath, dirnames, filenames in os.walk(project):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "__pycache__", ".venv", "venv"}]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if any(path.endswith(e) for e in SEALED_OK):
                continue
            rel = os.path.relpath(path, project)
            if rel in INCIDENTAL_ALLOW:
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if ID_RE.search(text) and any(t in text for t in TOKENS):
                leaks.append(rel)
    return sorted(leaks)


def check_plaintext_leak():
    leaks = scan_label_bearing()
    return (not leaks, leaks)


def check_atoms_complete(keydoc):
    missing = []
    for case in keydoc["cases"]:
        if "compound" in case.get("final_flags", []):
            atoms = case.get("atoms") or []
            if not atoms or any(a.get("semantic_truth") not in ATOM_SEM for a in atoms):
                missing.append(case["case_id"])
    return (not missing, missing)


def check_criticality(keydoc):
    missing = [c["case_id"] for c in keydoc["cases"] if c.get("criticality") not in ("critical", "standard")]
    return (not missing, missing)


def check_subgroups(keydoc):
    bad = []
    for case in keydoc["cases"]:
        flags = case.get("final_flags")
        if not isinstance(flags, list) or not flags or not set(flags) <= SUBGROUP_FLAGS:
            bad.append(case["case_id"])
    return (not bad, bad)


def check_two_pass(atom_audit):
    bad = [cid for cid, rec in atom_audit.items()
           if not (rec.get("pass1_atoms") and rec.get("pass2_atoms"))]
    return (not bad, bad)


def check_aggregation(keydoc):
    def aggregate(atoms):
        sems = [a["semantic_truth"] for a in atoms]
        if all(s == "SUPPORTED" for s in sems):
            return {"semantic_truth": "SUPPORTED", "proof_safe": "SUPPORTED", "product_action": "AUTO_SUPPORTED"}
        if all(s == "CONTRADICTED" for s in sems):
            return {"semantic_truth": "CONTRADICTED", "proof_safe": "CONTRADICTED", "product_action": "AUTO_CONTRADICTED"}
        if all(s == "INSUFFICIENT_EVIDENCE" for s in sems):
            return {"semantic_truth": "INSUFFICIENT_EVIDENCE", "proof_safe": "INSUFFICIENT_EVIDENCE", "product_action": "ABSTAIN_INSUFFICIENT"}
        gap = any(a["semantic_truth"] == "INSUFFICIENT_EVIDENCE" and a["proof_safe"] == "INSUFFICIENT_EVIDENCE" for a in atoms)
        proof = "INSUFFICIENT_EVIDENCE" if gap else "REVIEW_REQUIRED"
        product = "ABSTAIN_INSUFFICIENT" if gap else "REVIEW_REQUIRED"
        return {"semantic_truth": "PARTIALLY_SUPPORTED", "proof_safe": proof, "product_action": product}
    bad = []
    for case in keydoc["cases"]:
        if "compound" in case.get("final_flags", []):
            want = aggregate(case["atoms"])
            if case.get("aggregation") != want or {k: case["final"][k] for k in want} != want:
                bad.append(case["case_id"])
    return (not bad, bad)


def check_key_not_retired(key_bytes):
    fp = hashlib.sha256(key_bytes).hexdigest()
    return (fp != RETIRED_KEY_FINGERPRINT, fp)


def main():
    ok, leaks = check_plaintext_leak()
    print("live plaintext-label gate:", "PASS" if ok else "FAIL")
    for rel in leaks:
        print("  LEAK", rel)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
