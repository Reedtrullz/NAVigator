"""Differential test: dimension-evidence layer preserves gate semantics.

Contract-v1 section 5: the rich-state projection to the 3-state gate MUST
reproduce the pre-change gate output for all inputs. Run before relation
consumption is enabled (spec section 28).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROOF_DIR = os.path.abspath(os.path.join(HERE, "..", "rc3-1-proof-semantics"))
sys.path.insert(0, PROOF_DIR)

from rc3_1_engine import boundary  # noqa: E402

GATE_KEYS = ["polarity", "modality", "actor", "temporal", "scope",
             "condition", "exception", "numeric_quantity", "clause_coverage",
             "overall", "blocking_dimensions"]
CONFLICT = {"EXPLICIT_CONFLICT", "DEONTIC_OPPOSITION", "CONDITION_MISSING",
            "EXCEPTION_CONFLICT", "DIFFERENT_ACTOR", "SCOPE_CONFLICT",
            "TEMPORAL_CONFLICT", "NUMERIC_CONFLICT"}
UNRES = {"RELEVANT_BUT_UNRESOLVED", "ACTOR_UNRESOLVED"}
PROJ = {"EXACT_MATCH": "MATCH", "SOURCE_STRONGER_THAN_CLAIM": "MATCH",
        "SOURCE_WEAKER_THAN_CLAIM": "MATCH",
        "CONDITIONALLY_COMPATIBLE": "MATCH", "SAME_ACTOR": "MATCH",
        "LICENSED_ACTOR_EQUIVALENCE": "MATCH", "SCOPE_COMPATIBLE": "MATCH",
        "TEMPORAL_COMPATIBLE": "MATCH", "NUMERIC_COMPATIBLE": "MATCH",
        "NOT_APPLICABLE": "NOT_APPLICABLE", "PARTIAL_OVERLAP": "MISMATCH"}
for s in CONFLICT:
    PROJ[s] = "MISMATCH"
for s in UNRES:
    PROJ[s] = "UNKNOWN"


def norm3(v):
    return "MATCH" if v == "LICENSED_ENTAILMENT" else v


def main():
    snap_path = os.path.join(HERE, "gate-snapshot-before.json")
    snap = json.load(open(snap_path, encoding="utf-8"))
    gate_diffs = 0
    proj_bad = 0
    for row in snap:
        d = boundary.compare(row["claim"], row["span"])
        for k in GATE_KEYS:
            if d[k] != row["gate"][k]:
                gate_diffs += 1
                print("GATE DIFF", k, row["gate"][k], "->", d[k],
                      "|", row["claim"][:60])
        for dim, st in d["dimension_evidence"].items():
            if PROJ[st["state"]] != norm3(d[dim]):
                proj_bad += 1
                print("PROJ BAD", dim, st["state"], "|", row["claim"][:60])
    print(f"gate diffs: {gate_diffs} / {len(snap)} rows")
    print(f"projection mismatches: {proj_bad}")
    if gate_diffs or proj_bad:
        sys.exit(1)
    print("GATE EQUIVALENCE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
