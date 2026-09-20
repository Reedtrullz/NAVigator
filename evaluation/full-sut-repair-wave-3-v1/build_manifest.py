"""Build the Wave-3 candidate manifest + hashes.txt from disk state.

Verifies every component against Wave-2 pins; only the authorized W3-RC-A
file may differ. Regenerating this manifest is deterministic given the
same source tree.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
W2 = os.path.join(REPO, "evaluation/full-sut-repair-wave-2-v1/repaired-sut-manifest.json")

w2 = json.load(open(W2, encoding="utf-8"))
components = {}
changed, unchanged = [], []
for path in sorted(w2["components"]):
    actual = hashlib.sha256(open(os.path.join(REPO, path), "rb").read()).hexdigest()
    components[path] = actual
    if actual == w2["components"][path]:
        unchanged.append(path)
    else:
        changed.append(path)

EXPECTED_CHANGED = {
    "runtime/sut/phase2/routes.py",
}
unexpected = set(changed) - EXPECTED_CHANGED
if unexpected:
    print("ABORT: unexpected changed components: %s" % sorted(unexpected))
    sys.exit(1)

manifest = {
    "artifact": "repaired-sut-manifest-wave3-v1",
    "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-3-V1",
    "candidate_status": "FULL_SUT_REPAIR_WAVE_3_CANDIDATE_FROZEN",
    "source_candidate": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1",
    "wave2_manifest_sha256": hashlib.sha256(open(W2, "rb").read()).hexdigest(),
    "starting_state": "POST_WAVE2_P0_ROUTING_WAVE3_SCOPE_GATE_COMPLETE",
    "runtime_version": "wave3-w3-rc-a-v1",
    "candidate_version": "v1",
    "mode_default": "replay",
    "component_count": len(components),
    "components": components,
    "components_changed_from_wave2": {p: {"wave2": w2["components"][p], "wave3": components[p]} for p in sorted(changed)},
    "components_unchanged_from_wave2": len(unchanged),
    "test_results": {"full_suite_passed": 242, "failed": 0, "ref": "regression-results.json"},
    "repair_codes": ["W3-RC-A"],
    "candidate_attempts_max": 2,
    "candidate_history": {
        "v1": {
            "note": "attempt 1 of max 2; W3-RC-A route-proposition construction in phase2/routes.py with 26-test section-18/19 suite (runtime/sut/phase2/test_route_propositions.py, tracked via w3-rc-a-tests.json)",
            "replay_runs": "runs/structural-120-replay-v1/",
            "official": None,
        },
    },
    "anti_tuning_attestation": {
        "case_ids_in_runtime_logic": False,
        "expected_verdicts_in_runtime_logic": False,
        "burned_scoring_during_implementation": False,
        "id_guard_runtime_hits": 0,
    },
    "invariants": {
        "EMERGENCY_TRIGGER_LOGIC_CHANGED": False,
        "safety_py_changed": False,
        "measurement_v3_run": False,
        "gold_changed": False,
        "historical_predictions_mutated": False,
    },
}
out = os.path.join(HERE, "repaired-sut-manifest.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")

with open(os.path.join(HERE, "hashes.txt"), "w", encoding="utf-8") as f:
    f.write("# Wave-3 candidate component hashes (sha256)\n")
    for p in sorted(components):
        f.write("%s  %s\n" % (components[p], p))

print("manifest: %d components (%d changed, %d unchanged vs wave2)" % (len(components), len(changed), len(unchanged)))
for p in sorted(changed):
    print("  changed: %s %s -> %s" % (p, w2["components"][p][:12], components[p][:12]))
print("wave2 manifest sha:", manifest["wave2_manifest_sha256"])
