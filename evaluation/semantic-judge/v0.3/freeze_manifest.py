#!/usr/bin/env python3
"""Generate freeze manifest BEFORE opening any holdout answer key."""
import hashlib, json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    "judge-spec.md", "aggregation-spec.md", "semantic_judge.py",
    "decomposition-tests.json", "compound-set.json", "stability-set.json",
    "expected-stability.json", "adversarial-holdout.json",
    "holdout-v2-claims.json", "holdout-v2-answer-key.json",
    "metrics_v03.py", "decomposition_test.py", "compound_test.py",
]
THRESHOLDS = {
    "safety_unsupported_to_supported_fp": 0,
    "numeric_critical_fp": 0,
    "temporal_critical_fp": 0,
    "binary_unsupported_to_supported_fp_rate_max": 0.02,
    "four_class_accuracy_min": 0.925,
    "macro_f1_min": 0.90,
    "contradicted_recall_min": 0.95,
    "supported_precision_min": 0.97,
    "stability_modal_consistency_min": 0.95,
}
FENCE = chr(96) * 3

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    lines = ["# FREEZE MANIFEST - semantic-judge v0.3",
             "generated: " + datetime.now(timezone.utc).isoformat(), ""]
    for name in FILES:
        p = os.path.join(HERE, name)
        if not os.path.isfile(p):
            print(f"MISSING: {name}", file=sys.stderr)
            sys.exit(1)
        lines.append(f"{name} SHA256: {sha256(p)}")
    cal = os.path.join(HERE, "results", "v03-results-calibration-A-judge-a-gpt-5.5.json")
    if os.path.isfile(cal):
        meta = json.load(open(cal)).get("meta", {})
        lines += ["", f"model: {meta.get('model')}",
                  f"judge: {meta.get('judge')}",
                  f"decompose_prompt_sha256: {meta.get('decompose_prompt_sha256')}",
                  f"atom_prompt_sha256: {meta.get('atom_prompt_sha256')}",
                  f"aggregator: {meta.get('aggregator')}"]
    lines += ["", "## Pre-registered thresholds (mission spec section 23)",
              FENCE + "json", json.dumps(THRESHOLDS, indent=2), FENCE, "",
              "STATUS: FROZEN BEFORE HOLDOUT", ""]
    out = os.path.join(HERE, "freeze-manifest.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("WROTE " + out)

if __name__ == "__main__":
    main()
