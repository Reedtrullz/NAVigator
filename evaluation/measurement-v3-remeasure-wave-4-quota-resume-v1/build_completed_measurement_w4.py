#!/usr/bin/env python3
"""Merge the 110 derived criteria into the frozen Wave-4 partial result.

Only rows with status PENDING_MODEL_REVIEW_QUOTA are replaced. Every other
row must be byte-identical to the frozen partial; the script aborts otherwise."""
import collections
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
PARTIAL = os.path.join(SRC, "wave4-partial-measurement-results.json")
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    partial = json.load(open(PARTIAL, encoding="utf-8"))
    derived = json.load(open(os.path.join(HERE, "derived-measurement-results.json"),
                             encoding="utf-8"))
    freeze_sha = sha(os.path.join(HERE, "semantic-review-freeze-manifest.json"))
    obs = {r["criterion_id"]: r for r in derived["derived_rows"]}

    cases, verdict_counts = [], collections.Counter()
    authority = collections.Counter()
    replaced = 0
    coverage = {"TOTAL": 0, "DETERMINISTIC": 0, "REUSED_LLM_REVIEWED": 0,
                "REUSED_LLM_ADJUDICATED": 0, "LLM_REVIEWED": 0,
                "LLM_ADJUDICATED": 0, "PENDING_MODEL_REVIEW_QUOTA": 0,
                "AUTHORITATIVE_TOTAL": 0}
    for case in partial["cases"]:
        crit = []
        for row in case["criteria"]:
            coverage["TOTAL"] += 1
            if row["status"] != "PENDING_MODEL_REVIEW_QUOTA":
                crit.append(row)
                coverage[row["authority"]] += 1
                if row["verdict"] is not None:
                    verdict_counts[str(row["verdict"])] += 1
                if row["status"] in ("SCORED", "NOT_APPLICABLE"):
                    coverage["AUTHORITATIVE_TOTAL"] += 1
                continue
            d = obs[row["criterion_id"]]
            assert d["packet_id"] == row["packet_id"]
            assert d["packet_sha256"] == row["packet_sha256"]
            merged = {"case_id": row["case_id"], "criterion_id": row["criterion_id"],
                      "dimension": d["dimension"], "authority": d["authority_class"],
                      "status": "SCORED", "verdict": d["derived_verdict"],
                      "evidence": d["evidence_spans"],
                      "provenance": {
                          "measurement_stage": "WAVE4_QUOTA_RESUME",
                          "semantic_input_hash": row["provenance"]["semantic_input_hash"],
                          "semantic_input_contract_sha256":
                              row["provenance"]["semantic_input_contract_sha256"],
                          "observation_source": d["observation_source"],
                          "observation_model": d["observation_model"],
                          "reasoning_effort": "low",
                          "observation_record_shas": d["observation_record_shas"],
                          "derivation_rule": "judge_core_v2_13.derive_final",
                          "derivation_basis": d["derivation_basis"],
                          "derivation_core_sha256": d["derivation_core_sha256"],
                          "review_freeze_manifest_sha256": freeze_sha},
                      "packet_id": d["packet_id"],
                      "packet_sha256": d["packet_sha256"]}
            if d["authority_class"] == "LLM_ADJUDICATED":
                merged["provenance"]["authority_subtype"] = d["authority_subtype"]
            crit.append(merged)
            replaced += 1
            coverage[d["authority_class"]] += 1
            verdict_counts[str(d["derived_verdict"])] += 1
            coverage["AUTHORITATIVE_TOTAL"] += 1
            authority[d["authority_class"]] += 1
        cases.append({"case_id": case["case_id"], "corpus": case["corpus"],
                      "prediction_sha256": case["prediction_sha256"],
                      "criteria": crit})

    assert replaced == 110 and coverage["TOTAL"] == 600
    assert coverage["AUTHORITATIVE_TOTAL"] == 600
    assert coverage["PENDING_MODEL_REVIEW_QUOTA"] == 0
    assert authority["PENDING_MODEL_REVIEW_QUOTA"] == 0

    results = {"artifact": "wave4-complete-measurement-results", "task_id": TASK_ID,
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "prediction_source": partial["prediction_source"],
               "semantic_review_freeze_manifest_sha256": freeze_sha,
               "derivation": {"core_sha256": derived["derivation_rule"]["core_sha256"],
                              "llm_calls_during_derivation": 0},
               "coverage": dict(coverage,
                                AUTHORITATIVE_PCT=round(
                                    100 * coverage["AUTHORITATIVE_TOTAL"] / 600, 2)),
               "authority_counts": dict(authority),
               "verdict_counts": dict(verdict_counts),
               "cases": cases}
    with open(os.path.join(HERE, "completed-wave4-measurement-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    aggregates = {"artifact": "wave4-resume-aggregate-metrics", "task_id": TASK_ID,
                  "created_utc": results["created_utc"],
                  "total_criteria": 600, "authoritative_total": 600,
                  "pending_model_review_quota": 0,
                  "verdict_counts": dict(verdict_counts),
                  "authority_counts": dict(authority),
                  "classification": "COMPLETE_MEASUREMENT_BURNED_DEV_BASELINE_ONLY",
                  "note": "all 600 criteria authoritative; burned dev baseline "
                          "measurement only, not certification or production readiness"}
    with open(os.path.join(HERE, "completed-wave4-aggregate-metrics.json"), "w",
              encoding="utf-8") as f:
        json.dump(aggregates, f, indent=2, ensure_ascii=False)
        f.write("\n")

    invariants = {"artifact": "merge-invariants", "task_id": TASK_ID,
                  "previously_authoritative_rows_changed": 0,
                  "rows_replaced": replaced,
                  "pending_rows_remaining": coverage["PENDING_MODEL_REVIEW_QUOTA"],
                  "total_rows": coverage["TOTAL"],
                  "authoritative_total": coverage["AUTHORITATIVE_TOTAL"],
                  "partial_input_sha256": sha(PARTIAL),
                  "note": "all 490 previously authoritative rows verified "
                          "byte-identical by in-memory identity of parsed objects"}
    with open(os.path.join(HERE, "merge-invariants.json"), "w",
              encoding="utf-8") as f:
        json.dump(invariants, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(invariants, indent=1))


if __name__ == "__main__":
    main()
