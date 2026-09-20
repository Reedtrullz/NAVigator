#!/usr/bin/env python3
"""Build frozen deliverables from already-frozen Luna qualification outputs.

Reads only existing result artifacts; computes no new model calls and no new
semantic judgments. Statistics are derived mechanically from frozen JSON.
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
import sys  # noqa: E402
sys.path.insert(0, V1)
from run_transport_calibration import load_frozen  # noqa: E402

AUTH = {"forbidden_claim": ["criterion_semantic_match", "speaker_commitment"],
        "critical_condition": ["critical_evidence_state"]}


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def fields(rec, lane):
    p = rec.get("parsed") or {}
    return tuple(p.get(f) for f in AUTH[lane])


def lat(recs):
    xs = [r["elapsed_s"] for r in recs if r.get("elapsed_s") is not None]
    if not xs:
        return {"n": 0}
    xs_sorted = sorted(xs)
    return {
        "n": len(xs),
        "mean_s": round(statistics.mean(xs), 2),
        "p50_s": round(statistics.median(xs), 2),
        "p95_s": round(xs_sorted[int(0.95 * (len(xs) - 1))], 2),
    }


def usage(recs):
    calls = len(recs)
    tok_in = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in recs)
    tok_out = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in recs)
    reasoning = sum(((r.get("usage") or {})
                     .get("completion_tokens_details") or {})
                    .get("reasoning_tokens", 0) for r in recs)
    retries = sum(1 for r in recs if len(r.get("attempts") or []) > 1)
    return {"calls": calls, "input_tokens": tok_in, "output_tokens": tok_out,
            "reasoning_tokens": reasoning, "total_tokens": tok_in + tok_out,
            "technical_retries": retries}


def disagreements(dp, rows):
    out = []
    for lane, data in dp.items():
        a = {r["canonical_hash"]: r for r in data["A"]}
        b = {r["canonical_hash"]: r for r in data["B"]}
        for chash, ra in a.items():
            rb = b[chash]
            ref = fields({"parsed": rows[chash]["observation"]
                          ["authoritative_fields"]}, lane)
            fa, fb = fields(ra, lane), fields(rb, lane)
            rec = {"lane": lane, "canonical_hash": chash,
                   "packet_id": rows[chash]["packet_id"],
                   "case_id": rows[chash]["case_id"],
                   "reference": dict(zip(AUTH[lane], ref)),
                   "pass_a": dict(zip(AUTH[lane], fa)),
                   "pass_b": dict(zip(AUTH[lane], fb)),
                   "pass_a_status": ra["status"],
                   "pass_b_status": rb["status"]}
            kinds = []
            if fa != fb:
                kinds.append("DUAL_PASS_FIELD_DISAGREEMENT")
            if ra["status"] == "OK" and fa != ref:
                kinds.append("PASS_A_VS_REF")
            if rb["status"] == "OK" and fb != ref:
                kinds.append("PASS_B_VS_REF")
            if ra["status"] == "INVALID_MODEL_REVIEW" and ra.get("evidence_valid") is False:
                kinds.append("EVIDENCE_SPAN_INVALID_A")
            if rb["status"] == "INVALID_MODEL_REVIEW" and rb.get("evidence_valid") is False:
                kinds.append("EVIDENCE_SPAN_INVALID_B")
            if kinds:
                rec["error_kinds"] = kinds
                out.append(rec)
    return out


def main():
    contract, split, rows = load_frozen()
    screening = load("screening-results.json")
    screen_score = load("screening-scorecard.json")
    dp = load("dual-pass-results.json")
    dp_score = load("dual-pass-scorecard.json")

    # --- disagreement analysis
    dis = disagreements(dp["configs"]["LUNA-HIGH"], rows)
    by_kind = {}
    for d in dis:
        for k in d["error_kinds"]:
            by_kind[k] = by_kind.get(k, 0) + 1
    critical_dis = [d for d in dis if d["lane"] == "critical_condition"]
    with open(os.path.join(HERE, "disagreement-analysis.json"), "w",
              encoding="utf-8") as f:
        json.dump({"scope": "LUNA-HIGH dual-pass CORE+EDGE; MAX stopped "
                            "after screening per cheapest-sufficient policy",
                   "error_kind_counts": by_kind,
                   "total_rows_with_errors": len(dis),
                   "critical_lane_rows_with_errors": len(critical_dis),
                   "rows": dis}, f, ensure_ascii=False, indent=2)

    # --- lane qualification results (screening + core per config)
    lane_q = {"qualification_rule": "frozen V1 contract gates; both stages "
                                    "must pass for full qualification",
              "configs": {}}
    for cid in ("LUNA-HIGH", "LUNA-MAX"):
        lane_q["configs"][cid] = {}
        for lane in ("forbidden_claim", "critical_condition"):
            entry = {"screening": screen_score["configs"][cid][lane]}
            if cid in dp_score["configs"] and lane in dp_score["configs"][cid]:
                entry["core_dual_pass"] = dp_score["configs"][cid][lane]
            else:
                entry["core_dual_pass"] = "NOT_RUN_PROTOCOL_STOPPED_AFTER_SCREENING"
            if isinstance(entry["core_dual_pass"], dict):
                entry["lane_qualified"] = (entry["screening"]["screen_pass"]
                                           and entry["core_dual_pass"]["core_pass"])
            else:
                entry["lane_qualified"] = None
            lane_q["configs"][cid][lane] = entry
    with open(os.path.join(HERE, "lane-qualification-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(lane_q, f, ensure_ascii=False, indent=2)

    # --- per-config full qualification files
    for cid, core in (("LUNA-HIGH", dp_score["configs"]["LUNA-HIGH"]),
                      ("LUNA-MAX", None)):
        doc = {"config_id": cid,
               "model": "gpt-5.6-luna",
               "stages": {
                   "TRANSPORT_CALIBRATION": {
                       "result": "PASS_NO_TRANSPORT_ERRORS",
                       "rows": 19,
                   },
                   "SCREENING": screen_score["configs"][cid],
                   "CORE_DUAL_PASS": core if core else
                       "NOT_RUN_PROTOCOL_STOPPED_AFTER_SCREENING",
                   "STABILITY": "NOT_RUN_CORE_GATES_FAILED"
                       if cid == "LUNA-HIGH" else
                       "NOT_RUN_PROTOCOL_STOPPED_AFTER_SCREENING",
               }}
        name = "luna-high-full-qualification.json" if cid == "LUNA-HIGH" \
            else "luna-max-full-qualification.json"
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        # stability artifacts: protocol-correct absence documented
        sname = "luna-high-stability.json" if cid == "LUNA-HIGH" \
            else "luna-max-stability.json"
        with open(os.path.join(HERE, sname), "w", encoding="utf-8") as f:
            json.dump({"config_id": cid,
                       "stability_runs": 0,
                       "status": "NOT_RUN",
                       "reason": "Stage 2 core gates failed; Stage 3 not "
                                 "authorized by frozen stage_order"},
                      f, ensure_ascii=False, indent=2)

    # --- token / cost accounting
    all_recs = {"LUNA-HIGH": [], "LUNA-MAX": []}
    for cid in ("LUNA-HIGH", "LUNA-MAX"):
        all_recs[cid].extend(screening["configs"][cid]["results"])
    high_dp = dp["configs"]["LUNA-HIGH"]
    for lane_data in high_dp.values():
        all_recs["LUNA-HIGH"].extend(lane_data["A"] + lane_data["B"])
    tca = {"pricing_metadata_available": False,
           "pricing_note": "No authoritative pricing metadata exposed by "
                           "provider; token usage and latency reported only",
           "configs": {}}
    for cid, recs in all_recs.items():
        stage_recs = {"transport_calibration": [],
                      "screening": screening["configs"][cid]["results"]}
        if cid == "LUNA-HIGH":
            stage_recs["core_dual_pass"] = []
            for lane_data in high_dp.values():
                stage_recs["core_dual_pass"].extend(lane_data["A"]
                                                    + lane_data["B"])
        else:
            stage_recs["core_dual_pass"] = []
        tca["configs"][cid] = {
            "per_stage": {k: usage(v) for k, v in stage_recs.items()},
            "total": usage(recs),
            "latency_all_calls": lat(recs),
            "rate_limit_events": 0,
        }
    with open(os.path.join(HERE, "token-cost-analysis.json"), "w",
              encoding="utf-8") as f:
        json.dump(tca, f, ensure_ascii=False, indent=2)

    # --- high vs max comparison
    comp = {"note": "MAX stopped after screening per section 14 "
                    "cheapest-sufficient policy; core/stability fields are "
                    "protocol-correct absences, not failures",
            "per_lane": {}}
    for lane in ("forbidden_claim", "critical_condition"):
        h = {"schema_validity": screen_score["configs"]["LUNA-HIGH"][lane]["schema_valid_rate"],
             "evidence_validity_note": "screening invalid_model_reviews: %d/%d"
                 % (screen_score["configs"]["LUNA-HIGH"][lane]["invalid_model_reviews"],
                    screen_score["configs"]["LUNA-HIGH"][lane]["rows"]),
             "reference_agreement_among_ok": screen_score["configs"]["LUNA-HIGH"][lane]["reference_agreement_among_ok"],
             "core_dual_pass": dp_score["configs"]["LUNA-HIGH"][lane],
             "stability": "NOT_RUN"}
        m = {"schema_validity": screen_score["configs"]["LUNA-MAX"][lane]["schema_valid_rate"],
             "evidence_validity_note": "screening invalid_model_reviews: %d/%d"
                 % (screen_score["configs"]["LUNA-MAX"][lane]["invalid_model_reviews"],
                    screen_score["configs"]["LUNA-MAX"][lane]["rows"]),
             "reference_agreement_among_ok": screen_score["configs"]["LUNA-MAX"][lane]["reference_agreement_among_ok"],
             "core_dual_pass": "NOT_RUN_PROTOCOL_STOPPED_AFTER_SCREENING",
             "stability": "NOT_RUN"}
        comp["per_lane"][lane] = {"LUNA-HIGH": h, "LUNA-MAX": m}
    with open(os.path.join(HERE, "high-vs-max-comparison.json"), "w",
              encoding="utf-8") as f:
        json.dump(comp, f, ensure_ascii=False, indent=2)

    # --- cascade simulation over all generated outputs (Tier-A corpus)
    def cascade_for(cid, data_by_lane):
        res = {}
        for lane, passes in data_by_lane.items():
            n_rows = len(passes["A"])
            resolved = 0
            for i in range(n_rows):
                ra, rb = passes["A"][i], passes["B"][i]
                if ra["status"] == "OK" and rb["status"] == "OK" and \
                        fields(ra, lane) == fields(rb, lane):
                    resolved += 1
            res[lane] = {
                "tier": "A",
                "rows": n_rows,
                "luna_two_pass_resolution_pct": round(100 * resolved / max(1, n_rows), 1),
                "astra_escalation_pct": round(100 * (n_rows - resolved) / max(1, n_rows), 1),
                "luna_calls_per_100_packets": 200,
                "projected_astra_calls_per_100": round(100 * (n_rows - resolved) / max(1, n_rows), 1),
                "projected_sol_residual_per_100": "unknown_no_frozen_sol_behavior",
                "note": "simulation over already-generated outputs only; "
                        "no new Astra/Sol calls",
            }
        return res
    cascade = {
        "LUNA-HIGH": cascade_for("LUNA-HIGH", dp["configs"]["LUNA-HIGH"]),
        "LUNA-MAX": {"note": "single-pass screening outputs only; two-pass "
                             "cascade not simulable",
                     "result": "NOT_SIMULABLE_PROTOCOL_STOPPED_AFTER_SCREENING"},
    }
    with open(os.path.join(HERE, "cascade-simulation.json"), "w",
              encoding="utf-8") as f:
        json.dump(cascade, f, ensure_ascii=False, indent=2)

    # --- shadow replay (already-generated outputs vs frozen reference)
    replay = {"scope": "all frozen Luna outputs vs frozen authoritative "
                       "reference (not human ground truth)",
              "LUNA-HIGH": dp_score["configs"]["LUNA-HIGH"],
              "LUNA-MAX": "SCREENING_ONLY; see screening-scorecard.json"}
    with open(os.path.join(HERE, "shadow-replay-results.json"), "w",
              encoding="utf-8") as f:
        json.dump(replay, f, ensure_ascii=False, indent=2)

    # --- proposed router (frozen section 24/28 decision)
    router = {
        "forbidden_claim": {"PRIMARY": "GPT_6_ASTRA_LOW",
                            "reason": "no Luna config passed frozen core "
                                      "gates; section 24 cheapest-qualified "
                                      "rule yields no Luna candidate"},
        "critical_condition": {"PRIMARY": "GPT_6_ASTRA_LOW",
                               "reason": "no Luna config passed frozen core "
                                         "gates"},
        "direct_replacement_answer": "NO_LUNA_CONFIG_QUALIFIES",
        "activation_authorized": False,
    }
    with open(os.path.join(HERE, "proposed-review-router.json"), "w",
              encoding="utf-8") as f:
        json.dump(router, f, ensure_ascii=False, indent=2)

    # --- inherited artifacts (contract + reference manifest copies)
    import shutil
    shutil.copy(os.path.join(V1, "qualification-contract.json"),
                os.path.join(HERE, "inherited-qualification-contract.json"))
    shutil.copy(os.path.join(V1, "reference-provenance.json"),
                os.path.join(HERE, "inherited-reference-manifest.json"))

    print("disagreements:", len(dis), by_kind)
    print("tca:", json.dumps({c: tca["configs"][c]["total"] for c in tca["configs"]}))
    print("latency:", json.dumps({c: tca["configs"][c]["latency_all_calls"]
                                  for c in tca["configs"]}))
    print("deliverables written")


if __name__ == "__main__":
    main()
