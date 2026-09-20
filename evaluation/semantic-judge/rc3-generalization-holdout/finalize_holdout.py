#!/usr/bin/env python3
"""Build public holdout file, schema, blind manifest.

Public file carries no labels, no criticality, no rationale.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "construction-audit"

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RC3 generalization holdout cases",
    "type": "object",
    "required": ["set_id", "cases"],
    "properties": {
        "set_id": {"const": "RC3G-HOLDOUT-V1"},
        "case_count": {"type": "integer"},
        "cases": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["case_id", "claim", "track", "sources",
                             "evidence"],
                "properties": {
                    "case_id": {"pattern": "^RC3G-[0-9]{4}$"},
                    "claim": {"type": "string", "minLength": 10},
                    "track": {"enum": ["A", "B"]},
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["kb_ref", "lines", "text"],
                        },
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["span_id", "text"],
                        },
                    },
                    "compound": {"type": "boolean"},
                    "public_flags": {"type": "array",
                                     "items": {"type": "string"}},
                },
            },
        },
    },
}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    data = json.loads((AUDIT / "cases-pass1.json").read_text(encoding="utf-8"))
    selection = json.loads((AUDIT / "selection.json").read_text(encoding="utf-8"))
    core_ids = set(selection["core_ids"])
    pub_cases = []
    for c in data["cases"]:
        if c["case_id"] not in core_ids:
            continue
        pub = {k: c[k] for k in ("case_id", "claim", "track", "sources",
                                 "evidence", "compound", "public_flags")}
        if c["compound"]:
            pub["atoms"] = [
                {k: a[k] for k in ("atom_id", "text", "relation_to_parent",
                                   "evidence_span_ids", "required_inference")}
                for a in c["atoms"]]
        pub_cases.append(pub)
    pub = {"set_id": "RC3G-HOLDOUT-V1", "case_count": len(pub_cases),
           "cases": pub_cases}
    pub_bytes = json.dumps(pub, ensure_ascii=False, indent=1).encode("utf-8")
    (HERE / "generalization-cases.json").write_bytes(pub_bytes)
    (HERE / "generalization-cases.schema.json").write_text(
        json.dumps(SCHEMA, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest = {
        "set_id": "RC3G-HOLDOUT-V1",
        "task_id": "NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION",
        "runtime_snapshot": "NAV-EXPLORE-RC3-GEN-SNAPSHOT-A",
        "cases_file": "generalization-cases.json",
        "cases_sha256": sha256_bytes(pub_bytes),
        "sealed_key_file": "answer-key.sealed",
        "aad_convention": "AAD = ASCII bytes of lowercase hex sha256 "
                          "digest of the exact generalization-cases.json "
                          "file bytes",
        "status": "CONSTRUCTION_SEAL_PENDING",
    }
    (HERE / "blind-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print("public cases:", len(pub_cases))
    print("cases_sha256:", manifest["cases_sha256"])


if __name__ == "__main__":
    main()
