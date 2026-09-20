"""Build the Wave-2 candidate manifest + hashes.txt from disk state.

Verifies every component against Wave-1 pins; only the 6 authorized RC
files may differ. Regenerating this manifest is deterministic given the
same source tree.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
W1 = os.path.join(REPO, "evaluation/full-sut-repair-wave-1-v1/repaired-sut-manifest.json")

w1 = json.load(open(W1, encoding="utf-8"))
components = {}
changed, unchanged = [], []
for path in sorted(w1["components"]):
    actual = hashlib.sha256(open(os.path.join(REPO, path), "rb").read()).hexdigest()
    components[path] = actual
    if actual == w1["components"][path]:
        unchanged.append(path)
    else:
        changed.append(path)

EXPECTED_CHANGED = {
    "data/knowledge-index-v1.json",
    "runtime/sut/phase2/knowledge.py",
    "runtime/sut/phase2/pipeline.py",
    "runtime/sut/phase2/routes.py",
    "runtime/sut/phase3/finalize.py",
    "runtime/sut/phase3/planner.py",
}
unexpected = set(changed) - EXPECTED_CHANGED
if unexpected:
    print("ABORT: unexpected changed components: %s" % sorted(unexpected))
    sys.exit(1)

manifest = {
    "artifact": "repaired-sut-manifest-wave2-v1",
    "task_id": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-2-V1",
    "candidate_status": "FULL_SUT_REPAIR_WAVE_2_CANDIDATE_FROZEN",
    "source_candidate": "NAV-EXPLORE-FULL-SUT-REPAIR-WAVE-1-V1",
    "wave1_manifest_sha256": hashlib.sha256(open(W1, "rb").read()).hexdigest(),
    "starting_state": "FULL_SUT_POST_WAVE1_RESIDUAL_FAILURE_ANALYSIS_COMPLETE",
    "runtime_version": "wave2-rc07+rc08+rc10+rc11-v2",
    "candidate_version": "v2",
    "mode_default": "replay",
    "component_count": len(components),
    "components": components,
    "components_changed_from_wave1": {p: {"wave1": w1["components"][p], "wave2": components[p]} for p in sorted(changed)},
    "components_unchanged_from_wave1": len(unchanged),
    "test_results": {"full_suite_passed": 216, "failed": 0, "ref": "regression-results.json"},
    "repair_codes": ["RC-07", "RC-08", "RC-10", "RC-11"],
    "frozen_candidate_attempts": 2,
    "candidate_history": {
        "v1": {
            "note": "attempt 1 of max 2; all four RCs implemented in one pass; official replay 99/120 SUCCESS, 21/120 EXECUTION_FAILED (fail-closed) from cross-track evidence_id collision; superseded by v2",
            "replay_runs": "runs/structural-120-replay-v1/",
            "official": False,
        },
        "v2": {
            "note": "attempt 2 of max 2 (final); adds global evidence_id/record_id renumbering across tracks in phase2/pipeline.py s4 + test_pipeline_ids.py; official replay 120/120 SUCCESS, determinism rerun 120/120 byte-identical",
            "replay_runs": "runs/structural-120-replay-v2/",
            "official": True,
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
    f.write("# Wave-2 candidate component hashes (sha256)\n")
    for p in sorted(components):
        f.write("%s  %s\n" % (components[p], p))

print("manifest: %d components (%d changed, %d unchanged vs wave1)" % (len(components), len(changed), len(unchanged)))
for p in sorted(changed):
    print("  changed: %s %s -> %s" % (p, w1["components"][p][:12], components[p][:12]))
print("wave1 manifest sha:", manifest["wave1_manifest_sha256"])
