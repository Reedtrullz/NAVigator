#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase A gate: validate V1.7-draft extension against burned V2.9 fixtures.

Hard gates (TASK-SPEC-DRAFT.md section 2):
  - 100% precision on every V2.9 barrel where each detector fires
  - zero new wrong resolutions vs frozen base behavior
  - ABSTAIN rate reported
Zero model calls. Read-only over V2.9 lineage.
"""

import hashlib
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bx = _load("bx", os.path.join(_HERE, "boundary-extension-v1-7-draft.py"))

FIX = os.path.join(
    _ROOT, "evaluation", "judge-selection-v2-9-non-m2-post-diagnostic",
    "screening-fixtures.json")
GOLD = os.path.join(
    _ROOT, "evaluation", "judge-selection-v2-9-non-m2-post-diagnostic",
    "screening-gold.json")

fixtures = json.load(open(FIX))["fixtures"]
gold = json.load(open(GOLD))["gold"]

unc_fired, route_fired, wrong = [], [], []
base_label_changes = []
unc_abstain = route_abstain = 0
for fx in fixtures:
    fid, crit, sut = fx["id"], fx["crit"], fx["sut"]
    g = gold[fid]
    base = bx.bp.classify(sut, None)
    ext = bx.classify_extended(sut, crit)
    u, r = ext["uncertainty_behavior"], ext["route_commitment"]
    if u["abstained"]:
        unc_abstain += 1
    if r["abstained"]:
        route_abstain += 1
    if (not u["abstained"]
            and u.get("source") == "v1_7_draft_extension"):
        unc_fired.append(fid)
        if g["verdict"] != u["semantic_verdict"]:
            wrong.append({"id": fid, "detector": "unc",
                          "gold": g["verdict"],
                          "got": u["semantic_verdict"]})
    if (not r["abstained"]
            and r.get("source") == "v1_7_draft_extension"):
        route_fired.append(fid)
        if g["verdict"] != r["semantic_verdict"]:
            wrong.append({"id": fid, "detector": "route",
                          "gold": g["verdict"],
                          "got": r["semantic_verdict"]})
    for dim in ("uncertainty_behavior", "route_commitment",
                "assertion_scope"):
        if (base[dim]["label"] != ext[dim]["label"]
                and ext[dim].get("source") != "v1_7_draft_extension"):
            base_label_changes.append(
                {"id": fid, "dim": dim, "base": base[dim]["label"],
                 "ext": ext[dim]["label"]})

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

n = len(fixtures)
result = {
    "task_id": "NAV-EXPLORE-JUDGE-SELECTION-V2_10-BOUNDARY-EXTENSION-AND-RESCREEN",
    "validation_scope": "PHASE_A_BURNED_V2_9_BARRELS",
    "model_calls": 0,
    "fixture_count": n,
    "unc_fired": unc_fired,
    "route_fired": route_fired,
    "unc_fired_count": len(unc_fired),
    "route_fired_count": len(route_fired),
    "unc_precision_on_fired": (
        1.0 if not unc_fired else None),
    "route_precision_on_fired": (
        1.0 if not route_fired else None),
    "wrong_resolutions": wrong,
    "wrong_resolution_count": len(wrong),
    "frozen_base_label_changes_without_extension": base_label_changes,
    "unc_abstain_rate": round(unc_abstain / n, 4),
    "route_abstain_rate": round(route_abstain / n, 4),
    "module_sha256": sha(os.path.join(
        _HERE, "boundary-extension-v1-7-draft.py")),
    "test_sha256": sha(os.path.join(
        _HERE, "test_boundary_extension_draft.py")),
    "gate": {
        "precision_on_fired_100pct": len(wrong) == 0,
        "frozen_base_unchanged": not base_label_changes,
    },
}
# precise precision values when any fired
if unc_fired:
    ok = sum(1 for w in wrong if w["detector"] != "unc")
    result["unc_precision_on_fired"] = round(
        (len(unc_fired) - sum(1 for w in wrong if w["detector"] == "unc"))
        / len(unc_fired), 4)
if route_fired:
    result["route_precision_on_fired"] = round(
        (len(route_fired) - sum(1 for w in wrong if w["detector"] == "route"))
        / len(route_fired), 4)

out = os.path.join(_HERE, "boundary-extension-validation-draft.json")
json.dump(result, open(out, "w"), ensure_ascii=False, indent=2)
print(json.dumps({k: result[k] for k in (
    "fixture_count", "unc_fired", "route_fired",
    "unc_precision_on_fired", "route_precision_on_fired",
    "wrong_resolution_count", "unc_abstain_rate", "route_abstain_rate",
    "gate")}, ensure_ascii=False, indent=1))
sys.exit(0 if all(result["gate"].values()) else 1)
