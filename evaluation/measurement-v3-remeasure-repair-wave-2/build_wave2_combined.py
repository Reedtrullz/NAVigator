#!/usr/bin/env python3
"""Section 23: combine 506 deterministic + 94 semantic criteria into the
Wave-2 measurement result and aggregate metrics."""
import collections
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-REPAIR-WAVE-2"


def sha(path):
    return hashlib.sha256(open(os.path.join(HERE, path), "rb").read()).hexdigest()


def main():
    det = json.load(open(os.path.join(HERE, "deterministic-results.json"),
                         encoding="utf-8"))
    derived = json.load(open(os.path.join(HERE, "derived-measurement-results.json"),
                             encoding="utf-8"))
    freeze = json.load(open(os.path.join(HERE,
                                         "semantic-review-freeze-manifest.json"),
                            encoding="utf-8"))
    obs = {r["criterion_id"]: r for r in derived["derived_rows"]}
    obs.update({r["criterion_id"]: r for r in derived["pending_rows"]})

    cases, verdict_counts = [], collections.Counter()
    coverage = {"TOTAL_CRITERIA": 0, "DETERMINISTIC": 0, "LLM_REVIEWED": 0,
                "LLM_ADJUDICATED": 0, "HUMAN_REVIEWED": 0,
                "PENDING_LLM_ADJUDICATION": 0, "AUTHORITATIVE_TOTAL": 0}
    for case in det["cases"]:
        crit = []
        for row in case["criteria"]:
            cid = row["criterion_id"]
            coverage["TOTAL_CRITERIA"] += 1
            if row["authority"] == "DETERMINISTIC":
                coverage["DETERMINISTIC"] += 1
                if row["verdict"] is not None:
                    verdict_counts[str(row["verdict"])] += 1
                crit.append(row)
                coverage["AUTHORITATIVE_TOTAL"] += 1
                continue
            d = obs[cid]
            if d["authority_class"] == "PENDING_LLM_ADJUDICATION":
                coverage["PENDING_LLM_ADJUDICATION"] += 1
                crit.append({"case_id": row["case_id"], "criterion_id": cid,
                             "dimension": row["dimension"],
                             "authority": "PENDING_LLM_ADJUDICATION",
                             "status": "LLM_ADJUDICATION_PENDING", "verdict": None,
                             "evidence": [], "provenance": {
                                 "observation_source": d["observation_source"],
                                 "observation_model": d["observation_model"],
                                 "reasoning_effort": "low",
                                 "pending_reason": d["pending_reason"]},
                             "packet_id": d["packet_id"], "packet_sha256": None})
            else:
                coverage[d["authority_class"]] += 1
                coverage["AUTHORITATIVE_TOTAL"] += 1
                verdict_counts[str(d["derived_verdict"])] += 1
                crit.append({"case_id": row["case_id"], "criterion_id": cid,
                             "dimension": row["dimension"],
                             "authority": d["authority_class"], "status": "SCORED",
                             "verdict": d["derived_verdict"],
                             "evidence": d["evidence_spans"],
                             "provenance": {
                                 "observation_source": d["observation_source"],
                                 "observation_model": d["observation_model"],
                                 "reasoning_effort": "low",
                                 "observation_record_shas": d["observation_record_shas"],
                                 "derivation_rule": "judge_core_v2_13.derive_final",
                                 "derivation_basis": d["derivation_basis"],
                                 "derivation_core_sha256": d["derivation_core_sha256"],
                                 "review_freeze_manifest_sha256":
                                     freeze and sha(os.path.join(HERE, "semantic-review-freeze-manifest.json"))},
                             "packet_id": d["packet_id"],
                             "packet_sha256": d["packet_sha256"]})
        cases.append({"case_id": case["case_id"], "corpus": case["corpus"],
                      "prediction_sha256": case["prediction_sha256"],
                      "criteria": crit})
    assert coverage["TOTAL_CRITERIA"] == 600, coverage

    pending_case_ids = sorted({c["case_id"] for cse in cases
                               for c in cse["criteria"]
                               if c["status"] == "LLM_ADJUDICATION_PENDING"})
    results = {"artifact": "wave2-combined-measurement-results",
               "task_id": TASK_ID,
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "coverage": dict(coverage,
                                AUTHORITATIVE_PCT=round(
                                    100 * coverage["AUTHORITATIVE_TOTAL"] / 600, 2)),
               "verdict_counts": dict(verdict_counts),
               "semantic_review_freeze_manifest_sha256":
                   sha(os.path.join(HERE, "semantic-review-freeze-manifest.json")),
               "derivation": {"core_sha256": derived["derivation_rule"]["core_sha256"],
                              "llm_calls_during_derivation": 0},
               "cases": cases}
    with open(os.path.join(HERE, "wave2-combined-measurement-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    per_dim = {}
    for dim in ("critical_condition", "forbidden_claim", "route_correctness",
                "required_uncertainty", "evidence_completeness"):
        rows = [c for cse in cases for c in cse["criteria"]
                if c["dimension"] == dim]
        dist = collections.Counter(
            str(r["verdict"]) for r in rows if r["verdict"] is not None)
        per_dim[dim] = {
            "total_criteria": len(rows),
            "authoritative": sum(1 for r in rows
                                 if r["status"] in ("SCORED", "NOT_APPLICABLE")),
            "pending": sum(1 for r in rows
                           if r["status"] == "LLM_ADJUDICATION_PENDING"),
            "verdict_distribution": dict(dist)}
    aggregates = {"artifact": "wave2-aggregate-metrics", "task_id": TASK_ID,
                  "created_utc": results["created_utc"],
                  "baseline_label": "BURNED_DEV_BASELINE_ONLY",
                  "interpretation_boundary":
                      "Wave-2 dual-pass Astra consensus plus bounded Sol "
                      "residual adjudication is measurement-system evidence "
                      "for the burned dev baseline only; not certification, "
                      "production readiness, or generalization evidence.",
                  "coverage": results["coverage"],
                  "per_dimension": per_dim,
                  "pending_criteria": [r["criterion_id"]
                                       for r in derived["pending_rows"]],
                  "case_level_coverage": {
                      "total_cases": 120,
                      "fully_authoritative_cases": 120 - len(pending_case_ids),
                      "cases_with_pending_criteria": len(pending_case_ids),
                      "pending_case_ids": pending_case_ids},
                  "authority_mix_honesty":
                      "506 deterministic criteria, 90 LLM-reviewed (dual-pass "
                      "Astra LOW consensus), 3 LLM-adjudicated (dual-pass Sol "
                      "LOW residual consensus), 1 pending LLM adjudication, "
                      "0 human-reviewed; no criterion in this remeasurement "
                      "was decided by a human.",
                  "review_freeze_manifest_sha256":
                      sha(os.path.join(HERE, "semantic-review-freeze-manifest.json"))}
    with open(os.path.join(HERE, "wave2-aggregate-metrics.json"), "w",
              encoding="utf-8") as f:
        json.dump(aggregates, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"coverage": results["coverage"],
                      "pending_cases": pending_case_ids}, indent=1))


if __name__ == "__main__":
    main()
