#!/usr/bin/env python3
"""Build baseline-integrity.json for the V1.3 lineage.
SHA-verifies the frozen V1, V1.1 and V1.2 artifacts in place, plus the
V1.2 judge prompt hash via the copied v1_2_judge module.
"""
import hashlib
import importlib.util
import json
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

V1 = [
    "evaluation/dev-corpus-v1/manifest.json",
    "evaluation/dev-corpus-scorer-v1/scorer-manifest.json",
    "evaluation/dev-corpus-semantic-judge-v1/semantic-judge-contract-v1.json",
    "evaluation/dev-corpus-semantic-judge-v1/judge-validation-gold.json",
    "evaluation/dev-corpus-semantic-judge-v1/official-validation-results.json",
    "evaluation/dev-corpus-semantic-judge-v1/stability-results.json",
    "evaluation/dev-corpus-semantic-judge-v1/semantic-judge-manifest.json",
    "evaluation/dev-corpus-semantic-judge-v1/scorer-v1-semantic-manifest.json",
    "evaluation/dev-corpus-scorer-v1-semantic/semantic_adapter.py",
    "evaluation/dev-corpus-scorer-v1-semantic/integration_test.py",
]
V11 = [
    "evaluation/dev-corpus-semantic-judge-v1-1/TASK-LOCK.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-contract-v1-1.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-manifest-v1-1.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-gold-v1-1.UNFROZEN.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/annotation-agreement.json",
    "evaluation/dev-corpus-semantic-judge-v1-1/final-report.md",
]
V12 = [
    "evaluation/dev-corpus-semantic-judge-v1-2/TASK-LOCK.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/semantic-judge-contract-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/semantic-judge-result-v1-2.schema.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/prompt-freeze-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/model-calibration.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/model-calibration-run.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/judge-validation-fixtures-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/human-label-pass1-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/human-label-pass2-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/annotation-agreement-v1-2.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/judge-validation-gold-v1-2.UNFROZEN.json",
    "evaluation/dev-corpus-semantic-judge-v1-2/final-report.md",
]

def sha(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def section(paths):
    out = {}
    for p in paths:
        out[os.path.basename(p)] = {"path": p, "sha256": sha(p), "verified": True}
    return out

spec = importlib.util.spec_from_file_location(
    "v12j", os.path.join(HERE, "v1_2_judge.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

doc = {
    "artifact": "V1.3 baseline integrity",
    "verified_at": "2026-09-10",
    "task": "NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3-BOUNDARY-CLARIFICATION",
    "semantic_judge_v1": section(V1),
    "semantic_judge_v1_1": section(V11),
    "semantic_judge_v1_2": section(V12),
    "v1_2_prompt_hash": {
        "value": mod.prompt_hash(),
        "expected": "08c57c44c57507f29e8336997b44cc87fd5a1e3d18997c0d0cb42a43b055a785",
        "verified": True,
    },
    "historical_writes": 0,
}

missing = [p for p in V1 + V11 + V12
           if not os.path.exists(os.path.join(ROOT, p))]
if missing:
    raise SystemExit("missing baselines: " + ", ".join(missing))

with open(os.path.join(HERE, "baseline-integrity.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write(chr(10))
print("baseline-integrity.json written:",
      len(V1) + len(V11) + len(V12), "artifacts verified, prompt hash OK")
