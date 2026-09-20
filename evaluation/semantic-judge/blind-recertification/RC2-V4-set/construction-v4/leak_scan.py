#!/usr/bin/env python3
"""Full-project V3/V4 label-leakage scan (spec 4-5, 16).

A file is label-bearing when a Phase-1 agent could derive the expected
verdict for a concrete RC2B case from it: case ID + label vocabulary
co-occurrence, including indirect mappings. Raw claim/evidence text and
aggregate counts are allowed.
"""
import json
import os
import re
import sys

ROOT = "/Users/reidar/Projectos/NAV Explore"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "label-leakage-inventory.json")

ID_RE = re.compile(r"RC2B-\d{4}")
TOKENS = [
    "semantic_truth", "proof_safe", "product_action",
    "PASS1_CONFIRMED", "PASS2_CONFIRMED", "RESOLVED_NEW",
    "AUTO_SUPPORTED", "AUTO_CONTRADICTED", "ABSTAIN_INSUFFICIENT",
    "REVIEW_REQUIRED", "INSUFFICIENT_EVIDENCE", "PARTIALLY_SUPPORTED",
    "CONTRADICTED", "SUPPORTED",
    "expected_operator", "expected operator",
]
ENCRYPTED_OK = ("answer-key.sealed", "construction-audit.sealed")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
TEXT_EXT = {".json", ".md", ".py", ".txt", ".sh", ".csv", ".yaml", ".yml", ".toml", ""}


def is_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXT:
        return True
    try:
        with open(path, "rb") as f:
            return b"\x00" not in f.read(1024)
    except OSError:
        return False


def scan():
    findings = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if any(path.endswith(e) for e in ENCRYPTED_OK):
                continue
            if not is_text(path):
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            ids = sorted(set(ID_RE.findall(text)))
            hits = [t for t in TOKENS if t in text]
            if ids and hits:
                findings.append({
                    "path": os.path.relpath(path, ROOT),
                    "bytes": os.path.getsize(path),
                    "case_ids_found": len(ids),
                    "label_tokens": hits,
                    "verdict": "LABEL_BEARING_MUST_HIDE",
                })
    findings.sort(key=lambda f: f["path"])
    doc = {
        "scan_root": ROOT,
        "scan_time": "2026-09-04",
        "rule": "case ID + label vocabulary co-occurrence (spec 4-5)",
        "encrypted_whitelist": list(ENCRYPTED_OK),
        "n_label_bearing": len(findings),
        "findings": findings,
    }
    json.dump(doc, open(OUT, "w"), indent=1, ensure_ascii=False)
    for f in findings:
        print(f["verdict"], f["path"], f"{f['case_ids_found']} ids")
    print("total label-bearing files:", len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(scan())
