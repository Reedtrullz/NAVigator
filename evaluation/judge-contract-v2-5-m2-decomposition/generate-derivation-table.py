#!/usr/bin/env python3
"""Generate the frozen V2.5 M2 deterministic derivation table (81 rows)."""

import hashlib
import itertools
import json


def derive(ts, nts, conf, suff):
    if conf == "YES":
        return "AMBIGUOUS_OR_CONFLICTING"
    if ts == "PRESENT" and nts == "ABSENT" and conf == "NO" and suff == "SUFFICIENT":
        return "CLEAR_TRIGGER_SUPPORT"
    if nts == "PRESENT" and ts == "ABSENT" and conf == "NO" and suff == "SUFFICIENT":
        return "CLEAR_NON_TRIGGER_SUPPORT"
    # Frozen L69 disjunct 1: an answer that clearly does not put the condition
    # forward, with sufficient evidence and no conflict, is decidable CNTS.
    if ts == "ABSENT" and nts == "ABSENT" and conf == "NO" and suff == "SUFFICIENT":
        return "CLEAR_NON_TRIGGER_SUPPORT"
    if suff == "INSUFFICIENT" and conf != "YES":
        return "INSUFFICIENT_TO_DECIDE"
    return "UNRESOLVED"


rows = []
for ts, nts in itertools.product(["PRESENT", "ABSENT", "UNRESOLVED"], repeat=2):
    for conf, suff in itertools.product(
        ["YES", "NO", "UNRESOLVED"], ["SUFFICIENT", "INSUFFICIENT", "UNRESOLVED"]
    ):
        rows.append(
            {
                "trigger_support": ts,
                "non_trigger_support": nts,
                "evidence_conflict": conf,
                "evidence_sufficiency": suff,
                "derived_state": derive(ts, nts, conf, suff),
            }
        )

counts = {}
for r in rows:
    counts[r["derived_state"]] = counts.get(r["derived_state"], 0) + 1

# Equivalence asserts: frozen semantic families preserved.
for r in rows:
    if r["derived_state"].startswith("CLEAR_"):
        assert r["evidence_conflict"] == "NO", r
        assert r["evidence_sufficiency"] == "SUFFICIENT", r
    if r["evidence_conflict"] == "YES":
        assert r["derived_state"] == "AMBIGUOUS_OR_CONFLICTING", r
    if r["evidence_sufficiency"] == "INSUFFICIENT":
        assert not r["derived_state"].startswith("CLEAR_"), r
    if "UNRESOLVED" in (
        r["trigger_support"],
        r["non_trigger_support"],
        r["evidence_conflict"],
        r["evidence_sufficiency"],
    ):
        assert not r["derived_state"].startswith("CLEAR_"), r

doc = {
    "artifact": "deterministic-derivation-table.json",
    "task_id": "NAV-EXPLORE-JUDGE-CONTRACT-V2_5-M2-EVIDENCE-STATE-DECOMPOSITION",
    "created_utc": "2026-09-13",
    "derivation_version": "M2_DECOMPOSITION_V1",
    "frozen_semantics_trace": "frozen-semantics-trace.md",
    "frozen_derivation_anchor_sha256": "ad0f60af34e28df8741f42240dc3ce0317b927f002e8b9ee09640ec649dd1c85",
    "final_labels_unchanged": True,
    "derivation_order": [
        "1. conflict YES -> AMBIGUOUS_OR_CONFLICTING",
        "2. CLEAR_TRIGGER: trigger PRESENT, non_trigger ABSENT, conflict NO, sufficiency SUFFICIENT",
        "3. CLEAR_NON_TRIGGER: non_trigger PRESENT, trigger ABSENT, conflict NO, sufficiency SUFFICIENT",
        "3b. CLEAR_NON_TRIGGER (trivial absence): trigger ABSENT, non_trigger ABSENT, conflict NO, sufficiency SUFFICIENT (frozen L69 disjunct 1)",
        "4. sufficiency INSUFFICIENT (conflict not YES) -> INSUFFICIENT_TO_DECIDE",
        "5. all other combinations -> UNRESOLVED (conservative; unknown combinations never best-guessed)",
    ],
    "conservative_default": "UNRESOLVED",
    "equivalence_asserts": {
        "clear_requires_conflict_no_and_sufficient": True,
        "conflict_yes_never_clear": True,
        "insufficient_never_clear": True,
        "unresolved_subfield_never_clear": True,
        "frozen_mapping_for_old_reachable_states": "Any V2.2-conformant output maps to the same final verdict under V2.5 derivation (see frozen-semantics-trace.md equivalence obligation).",
    },
    "row_count": len(rows),
    "derived_state_distribution": counts,
    "rows": rows,
}

with open("deterministic-derivation-table.json", "w") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False)
    f.write("\n")

h = hashlib.sha256(
    open("deterministic-derivation-table.json", "rb").read()
).hexdigest()
print("rows:", len(rows), "distribution:", counts)
print("sha256:", h)
