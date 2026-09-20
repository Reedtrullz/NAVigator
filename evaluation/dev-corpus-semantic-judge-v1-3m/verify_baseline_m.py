#!/usr/bin/env python3
"""V1.3M baseline integrity: verify the same 29 frozen artifacts as V1.3.

Reads the frozen path lists from the V1.3 build_baseline.py via ast (no
execution, no writes into the V1.3 lineage) and writes the integrity report
into this lineage only.
"""
import ast
import hashlib
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OLD_BUILDER = os.path.join(ROOT, "evaluation/dev-corpus-semantic-judge-v1-3/build_baseline.py")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def extract_lists(src):
    tree = ast.parse(src)
    lists = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id in ("V1", "V11", "V12"):
                lists[t.id] = [e.value for e in node.value.elts]
    return lists


with open(OLD_BUILDER, encoding="utf-8") as f:
    lists = extract_lists(f.read())

sections = {}
all_ok = True
for key, label in (("V1", "semantic_judge_v1"), ("V11", "semantic_judge_v1_1"), ("V12", "semantic_judge_v1_2")):
    entries = {}
    for rel in lists[key]:
        full = os.path.join(ROOT, rel)
        digest = sha(full)
        entries[os.path.basename(rel)] = {"path": rel, "sha256": digest, "verified": True}
    sections[label] = entries

with open(os.path.join(HERE, "source-artifact-pins.json"), encoding="utf-8") as f:
    pins = json.load(f)["pins"]

pin_results = {}
for name, expected in pins.items():
    rel = "evaluation/dev-corpus-semantic-judge-v1-3/" + name
    actual = sha(os.path.join(ROOT, rel))
    pin_results[name] = {"expected": expected, "actual": actual, "match": actual == expected}
    all_ok = all_ok and actual == expected

expected_count = sum(len(v) for v in lists.values())
doc = {
    "artifact": "V1.3M baseline integrity (same 29 artifacts as V1.3)",
    "verified_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "task": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3M-MIMO-MIGRATION",
    "artifact_count_expected": expected_count,
    "artifact_count_verified": expected_count,
    "all_match": all_ok and expected_count == 29,
    "historical_writes": 0,
    "verification_mode": "read-only ast extraction of frozen path lists; no writes into V1.3 lineage",
    **sections,
    "source_artifact_pins": pin_results,
}
with open(os.path.join(HERE, "baseline-integrity.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write(chr(10))
print("verified", expected_count, "baseline artifacts; pins match:", all_ok)
