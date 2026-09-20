#!/usr/bin/env python3
"""Comparator replay + mechanical derivation for the four Wave-1 Sol residuals.

Branch A conformance replay: the frozen upstream consensus builders
(build_primary_consensus.py / build_residual_consensus.py) compare
authoritative semantic fields only; the whole-object A==B rule used in the
Wave-1 residual task was task-local implementation scope, not contract.
No LLM calls, no observation changes."""
import hashlib
import importlib.util
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVAL = os.path.join(ROOT, "evaluation")
UPSTREAM = os.path.join(EVAL, "measurement-v3-wave1-residual-llm-adjudication-v1")
CORE_PATH = os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist",
                         "judge_core_v2_13.py")
CORE_SHA = "66004e3038eb483040f9dad326661aa501e43680b8024a79994b22db51b02682"
UPSTREAM_LOCK_SHA = "71a0b22441d69924226bf7835dc441df1b779e76dfbfff7fc867010c96c017fd"
UPSTREAM_LOCK_FILE_SHA = "3e5fd8b11ae7c118247ad3e6c16e9406bb9c2b1d728bcf5733a3af9df3cd2c7b"
UPSTREAM_RESULTS_SHA = ("25dca5775bf76f223247d05364cbba1479d887b3f26718b0ced"
                        "085fc847dc7d8")
OLD_BASELINE_SHA = ("e73bbb86e0514a59f36e21b382a8a95922b7f4924d5e1d4686438437"
                    "948861cf")
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-WAVE1-CONSENSUS-COMPARATOR-REPAIR-V1"

MATCH_ENUM = {"MATCH", "NO_MATCH", "UNRESOLVED"}
COMMIT_ENUM = {"ASSERTED", "HEDGED_ASSERTION", "QUOTED_ONLY", "HYPOTHETICAL_ONLY",
               "NEGATED", "SELF_RETRACTED", "NONCOMMITTAL", "UNRESOLVED"}


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sha_obj(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_jsonl(name):
    path = os.path.join(UPSTREAM, name)
    return {json.loads(l)["packet_id"]: json.loads(l)
            for l in open(path, encoding="utf-8") if l.strip()}


def validate(rec, sut):
    if rec.get("status") != "OK":
        return rec.get("status", "INVALID_RECORD")
    if rec.get("packet_sha256") and rec["packet_sha256"] != sut["packet_sha256"]:
        return "PACKET_SHA_BINDING_MISMATCH"
    if rec.get("reasoning_effort") != "low":
        return "REASONING_EFFORT_VIOLATION"
    res = rec.get("result", {})
    if set(res.keys()) != {"criterion_semantic_match", "speaker_commitment",
                           "evidence_spans", "rationale"}:
        return "INVALID_SCHEMA"
    if res["criterion_semantic_match"] not in MATCH_ENUM:
        return "INVALID_ENUM"
    if res["speaker_commitment"] not in COMMIT_ENUM:
        return "INVALID_ENUM"
    spans = res["evidence_spans"]
    if not isinstance(spans, list) or not all(isinstance(s, str) for s in spans):
        return "INVALID_SPANS_TYPE"
    if any(s not in sut["sut_output"] for s in spans):
        return "INVALID_MODEL_REVIEW"
    need = (res["criterion_semantic_match"] == "MATCH"
            and res["speaker_commitment"] != "UNRESOLVED")
    if need and not spans:
        return "INVALID_MODEL_REVIEW"
    if not need and spans:
        return "INVALID_MODEL_REVIEW"
    return "OK"


def auth_fields(res):
    return {"criterion_semantic_match": res.get("criterion_semantic_match"),
            "speaker_commitment": res.get("speaker_commitment")}


def semantic_state(dimension, verdict):
    """Frozen measurement semantics (build_baseline_comparison.py)."""
    if verdict is None:
        return "ABSENT_OR_NOT_APPLICABLE"
    if dimension == "critical_condition":
        return ("FAIL" if verdict in ("TRIGGERED", "CRITICAL_ERROR")
                else "PASS" if verdict == "NOT_TRIGGERED" else "UNRESOLVED")
    if dimension == "forbidden_claim":
        return ("FAIL" if verdict in ("PRESENT", "CLAIM_PRESENT")
                else "PASS" if verdict in ("ABSENT", "CLAIM_ABSENT_TAKEN")
                else "UNRESOLVED")
    if dimension == "route_correctness":
        return ("PASS" if verdict == "ACCEPTABLE"
                else "UNRESOLVED" if verdict == "UNRESOLVED" else "FAIL")
    if dimension == "required_uncertainty":
        return ("PASS" if verdict in ("SATISFIED", "NOT_REQUIRED")
                else "DEGRADED" if verdict == "PARTIAL"
                else "FAIL" if verdict == "VIOLATED" else "UNRESOLVED")
    if dimension == "evidence_completeness":
        return ("PASS" if verdict == 1.0
                else "DEGRADED" if isinstance(verdict, (int, float)) and 0 < verdict < 1
                else "FAIL" if verdict == 0.0 else "UNRESOLVED")
    raise ValueError(dimension)


def main():
    checks = {}
    lock_path = os.path.join(UPSTREAM, "TASK-LOCK.json")
    lock = json.load(open(lock_path, encoding="utf-8"))
    checks["upstream_lock_terminal"] = (
        lock["status"] == "CLOSED"
        and lock["terminal_status"]
        == "MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING")
    checks["upstream_manifest_sha"] = (
        sha_file(os.path.join(UPSTREAM, "measurement-manifest.json"))
        == UPSTREAM_LOCK_SHA)
    checks["upstream_lock_file_sha"] = sha_file(lock_path) == UPSTREAM_LOCK_FILE_SHA
    up_results = os.path.join(
        UPSTREAM, "wave1-remeasurement-complete-after-secondary-residual.json")
    checks["upstream_results_sha"] = sha_file(up_results) == UPSTREAM_RESULTS_SHA
    checks["upstream_hashes_txt"] = True
    with open(os.path.join(UPSTREAM, "hashes.txt"), encoding="utf-8") as f:
        for line in f:
            digest, fname = line.split()
            if sha_file(os.path.join(UPSTREAM, fname)) != digest:
                checks["upstream_hashes_txt"] = False
    core_sha = sha_file(CORE_PATH)
    checks["derivation_core_sha"] = core_sha == CORE_SHA

    inputs = json.load(open(os.path.join(UPSTREAM, "sol-blind-inputs.json"),
                            encoding="utf-8"))["packets"]
    by_pid = {p["packet_id"]: p for p in inputs}
    a, b = load_jsonl("sol-pass-a.jsonl"), load_jsonl("sol-pass-b.jsonl")
    frozen = json.load(open(os.path.join(
        UPSTREAM, "sol-adjudication-frozen-observations.json"), encoding="utf-8"))
    old_consensus = json.load(open(os.path.join(
        UPSTREAM, "sol-adjudication-consensus.json"), encoding="utf-8"))

    entries, resolved = [], []
    for pid in ["PKT-ESC-DIS-118", "PKT-ESC-ROUT-026-F01",
                "PKT-ESC-ROUT-031-F01", "PKT-ESC-ROUT-037"]:
        p, ra, rb = by_pid[pid], a[pid], b[pid]
        va, vb = validate(ra, p), validate(rb, p)
        fa, fb = auth_fields(ra.get("result", {})), auth_fields(rb.get("result", {}))
        cons = va == "OK" and vb == "OK" and fa == fb
        whole_equal = ra.get("result") == rb.get("result")
        old = next(e for e in old_consensus["packets"] if e["packet_id"] == pid)
        assert old["status_a"] == "OK" and old["status_b"] == "OK"
        assert old["results_equal"] == whole_equal, pid
        entry = {
            "packet_id": pid,
            "packet_sha256": p["packet_sha256"],
            "validity_a": va, "validity_b": vb,
            "authoritative_fields_a": fa,
            "authoritative_fields_b": fb,
            "authoritative_fields_equal": fa == fb,
            "rationale_equal": (ra["result"]["rationale"]
                                == rb["result"]["rationale"]),
            "evidence_spans_identical": (ra["result"]["evidence_spans"]
                                         == rb["result"]["evidence_spans"]),
            "whole_object_equal": whole_equal,
            "old_rule_consensus": old["consensus"],
            "corrected_rule_consensus": "LLM_CONSENSUS" if cons
            else "PENDING_SEMANTIC_RESIDUAL",
            "observation_record_shas": {
                "sol_a": sha_obj(ra), "sol_b": sha_obj(rb)},
        }
        entries.append(entry)
        if cons:
            resolved.append((pid, p, ra, fa))

    spec = importlib.util.spec_from_file_location("judge_core_v2_13", CORE_PATH)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)

    derived_rows = []
    for pid, p, ra, fa in resolved:
        verdict, basis = core.derive_final("forbidden_claim", fa)
        derived_rows.append({
            "packet_id": pid, "packet_sha256": p["packet_sha256"],
            "authoritative_fields": fa,
            "observation_model": "gpt-5.6-sol", "reasoning_effort": "low",
            "authority_class": "LLM_ADJUDICATED",
            "authority_subtype": "GPT_5_6_SOL_DUAL_PASS_RESIDUAL",
            "evidence_spans": ra["result"]["evidence_spans"],
            "derived_verdict": verdict, "derivation_basis": basis,
            "derivation_core_sha256": CORE_SHA})

    comparator_replay = {
        "artifact": "semantic-consensus-comparison",
        "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corrected_rule": (
            "two valid independent reviews achieve semantic consensus iff all "
            "AUTHORITATIVE_SEMANTIC fields are identical; required evidence "
            "must independently validate for both passes; rationale, "
            "explanatory prose and transport metadata never break consensus"),
        "branch": "A_CONSENSUS_COMPARATOR_IMPLEMENTATION_DEFECT",
        "llm_calls": 0,
        "input_checks": checks,
        "summary": {
            "packets": len(entries),
            "authoritative_fields_consensus": sum(
                1 for e in entries
                if e["corrected_rule_consensus"] == "LLM_CONSENSUS"),
            "whole_object_consensus": sum(
                1 for e in entries if e["whole_object_equal"]),
        },
        "packets": entries,
    }
    with open(os.path.join(HERE, "semantic-consensus-comparison.json"), "w",
              encoding="utf-8") as f:
        json.dump(comparator_replay, f, indent=2, ensure_ascii=False)
        f.write("\n")

    derived = {
        "artifact": "derived-residual-results", "task_id": TASK_ID,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "derivation_rule": ("judge_core_v2_13.derive_final (frozen deterministic "
                            "mapper, unmodified)"),
        "derivation_core_sha256": CORE_SHA,
        "llm_calls_during_derivation": 0,
        "semantic_observations_changed": False,
        "derived_count": len(derived_rows),
        "derived_rows": derived_rows,
    }
    with open(os.path.join(HERE, "derived-residual-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(derived, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(json.dumps({"consensus": comparator_replay["summary"],
                      "derived": len(derived_rows),
                      "checks": checks}, indent=1))


if __name__ == "__main__":
    main()
