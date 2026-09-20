#!/usr/bin/env python3
"""Finalize LUNA-MAX completion: tokens, comparisons, lane decisions, router.

Token accounting: frozen screening baseline (330,899 tokens / 90 calls from
predecessor token-cost-analysis.json) plus this lineage's dual-pass actuals
from the four spec-named progress JSONLs. No pricing is invented.

Exit codes: 0 done; 3 = Stage-2 lanes passed, stability still pending.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)
from run_transport_calibration import load_frozen  # noqa: E402

AUTH = {"forbidden_claim": ["criterion_semantic_match", "speaker_commitment"],
        "critical_condition": ["critical_evidence_state"]}
PROGRESS = {
    "forbidden_claim": ["max-forbidden-pass-a.jsonl",
                        "max-forbidden-pass-b.jsonl"],
    "critical_condition": ["max-critical-pass-a.jsonl",
                           "max-critical-pass-b.jsonl"],
}
FROZEN_HIGH_TOTAL = {"calls": 544, "input_tokens": 1849736,
                     "output_tokens": 165255, "reasoning_tokens": 113581,
                     "total_tokens": 2014991}
SCREENING_BASELINE = {"calls": 90, "input_tokens": 301720,
                      "output_tokens": 29179, "reasoning_tokens": 20248,
                      "total_tokens": 330899}


def usage_sum(recs):
    out = {"calls": 0, "input_tokens": 0, "output_tokens": 0,
           "reasoning_tokens": 0, "total_tokens": 0,
           "technical_retries": 0, "rate_limit_events": 0}
    lat = []
    for r in recs:
        out["calls"] += 1
        u = r.get("usage") or {}
        out["input_tokens"] += u.get("prompt_tokens", 0) or 0
        comp = u.get("completion_tokens", 0) or 0
        out["output_tokens"] += comp
        rt = (u.get("completion_tokens_details") or {}).get(
            "reasoning_tokens", 0) or 0
        out["reasoning_tokens"] += rt
        out["total_tokens"] += u.get("total_tokens", comp) or comp
        out["technical_retries"] += max(0, len(r.get("attempts") or []) - 1)
        if r.get("elapsed_s") is not None:
            lat.append(r["elapsed_s"])
        for a in r.get("attempts") or []:
            if "429" in str(a.get("error", "")):
                out["rate_limit_events"] += 1
    if lat:
        s = sorted(lat)
        out["latency"] = {"n": len(s),
                          "mean_s": round(sum(s) / len(s), 2),
                          "p50_s": s[len(s) // 2],
                          "p95_s": s[int(len(s) * 0.95)]}
    return out


def load_lane(lane):
    recs = []
    for name in PROGRESS[lane]:
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            recs += [json.loads(l) for l in open(path, encoding="utf-8")
                     if l.strip()]
    return recs


def stability_stats(lane, results, rows):
    errs = []
    ok = 0
    for r in results:
        if r["status"] != "OK":
            errs.append({"canonical_hash": r["canonical_hash"],
                         "status": r["status"]})
            continue
        ok += 1
        ref = tuple(rows[r["canonical_hash"]]["observation"]
                    ["authoritative_fields"][f] for f in AUTH[lane])
        got = tuple((r.get("parsed") or {}).get(f) for f in AUTH[lane])
        if got != ref:
            errs.append({"canonical_hash": r["canonical_hash"],
                         "type": "REF_MISMATCH"})
    n = len(results)
    return {"rows": n, "ok": ok, "errors": len(errs),
            "agreement": round((n - len(errs)) / max(1, n), 4),
            "error_rows": errs}


def main():
    contract, split, rows = load_frozen()
    fq = json.load(open(os.path.join(HERE, "max-full-qualification.json"),
                        encoding="utf-8"))
    gates = contract["gates_allowed_error_counts"]

    # token accounting
    per_lane = {}
    total = dict(SCREENING_BASELINE)
    for lane, names in PROGRESS.items():
        recs = load_lane(lane)
        s = usage_sum(recs)
        per_lane[lane] = s
        for k in ("calls", "input_tokens", "output_tokens",
                  "reasoning_tokens", "total_tokens", "technical_retries",
                  "rate_limit_events"):
            total[k] = total.get(k, 0) + s[k]
    ratio = round(total["total_tokens"]
                  / max(1, FROZEN_HIGH_TOTAL["total_tokens"]), 3)
    tokens = {
        "pricing_metadata_available": False,
        "pricing_note": "No authoritative pricing metadata exposed by "
                        "provider; token usage and latency only.",
        "LUNA-MAX-this-lineage": {
            "screening_frozen_baseline": SCREENING_BASELINE,
            "stage2_per_lane": per_lane,
            "total_including_frozen_screening": total,
        },
        "LUNA-HIGH-frozen-predecessor": FROZEN_HIGH_TOTAL,
        "relative_token_ratio_MAX_vs_HIGH": ratio,
    }
    json.dump(tokens, open(os.path.join(HERE, "token-cost-comparison.json"),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # stability handling
    qualified = [l for l, s in fq["configs"]["LUNA-MAX"].items()
                 if s.get("lane_pass")]
    stab_path = os.path.join(HERE, "max-stability-results.json")
    stability = {"config_id": "LUNA-MAX", "status": None}
    if not qualified:
        stability.update(status="NOT_RUN_NO_LANE_PASSED_STAGE_2",
                         reason="no lane passed all Stage-2 gates; Stage 3 "
                                "not authorized by frozen stage order")
    elif not os.path.exists(stab_path):
        print("STABILITY_PENDING", qualified, flush=True)
        sys.exit(3)
    else:
        sr = json.load(open(stab_path, encoding="utf-8"))
        lanes = {}
        lane_ok = {}
        for lane, res in sr["configs"]["LUNA-MAX"].items():
            st = stability_stats(lane, res, rows)
            g = gates[lane]
            st["gate_agreement_min"] = g["stability_agreement_min"]
            st["gate_errors_max"] = g["stability_errors_max"]
            st["pass"] = (st["agreement"] >= g["stability_agreement_min"]
                          and st["errors"] <= g["stability_errors_max"])
            lanes[lane] = st
            lane_ok[lane] = st["pass"]
        stability.update(status="DONE", lanes=lanes)
        for lane in qualified:
            fq["configs"]["LUNA-MAX"][lane]["stability"] = lanes[lane]
            cfg = fq["configs"]["LUNA-MAX"][lane]
            cfg["stability_pass"] = lane_ok[lane]
            cfg["lane_qualified"] = cfg["lane_pass"] and lane_ok[lane]
    json.dump(stability, open(os.path.join(HERE, "max-stability.json"),
                              "w", encoding="utf-8"), ensure_ascii=False,
              indent=2)

    # lane results + decisions
    for lane in ("forbidden_claim", "critical_condition"):
        s = fq["configs"]["LUNA-MAX"][lane]
        s.setdefault("stability", stability.get("lanes", {}).get(lane))
        if "lane_qualified" not in s:
            s["lane_qualified"] = (
                None if stability["status"] != "DONE"
                else (s["lane_pass"] and s.get("stability_pass", False))
            )
        s["lane_decision"] = (
            "LUNA_HIGH_NOT_QUALIFIED_MAX_QUALIFIED" if s["lane_qualified"]
            else "NO_LUNA_CONFIG_QUALIFIES")
    qualified_final = [l for l in ("forbidden_claim", "critical_condition")
                       if fq["configs"]["LUNA-MAX"][l]["lane_qualified"]]
    overall = ("LUNA_REVIEWER_QUALIFIED" if len(qualified_final) == 2
               else "LUNA_REVIEWER_PARTIALLY_QUALIFIED" if qualified_final
               else "NO_LUNA_REVIEWER_CONFIG_QUALIFIES_CONFIRMED")
    fq["terminal_status"] = overall
    json.dump(fq, open(os.path.join(HERE, "max-full-qualification.json"),
                       "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    lane_results = {
        "qualification_rule": "frozen inherited contract gates; Stage-2 "
                              "(core+EDGE) and Stage-3 stability where run",
        "configs": {
            "LUNA-HIGH": {
                l: {"core_dual_pass": "FAIL_FROZEN_PREDECESSOR",
                    "lane_qualified": False}
                for l in ("forbidden_claim", "critical_condition")},
            "LUNA-MAX": {
                l: {k: fq["configs"]["LUNA-MAX"][l].get(k)
                    for k in ("core_pass", "edge_pass", "lane_pass",
                              "stability_pass", "lane_qualified",
                              "lane_decision")}
                for l in ("forbidden_claim", "critical_condition")},
        },
        "overall_status": overall,
    }
    json.dump(lane_results, open(os.path.join(
        HERE, "lane-qualification-results.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=2)

    # final comparison
    def lane_cmp(lane):
        s = fq["configs"]["LUNA-MAX"][lane]
        return {
            "LUNA-HIGH-frozen": "FAIL (consensus/field/evidence/pass-level "
                                "gates all exceeded; critical: 69/80 invalid)",
            "LUNA-MAX-completion": {
                "status_counts": s["status_counts"],
                "consensus_rows": s["consensus_rows"],
                "consensus_vs_ref_errors": s["consensus_vs_ref_errors"],
                "dual_consensus_field_errors": s["dual_consensus_field_errors"],
                "pass_level_vs_ref_errors": s["pass_level_vs_ref_errors"],
                "evidence_invalid_rows": s["evidence_invalid_rows"],
                "edge": s["edge"],
                "core_pass": s["core_pass"],
                "edge_pass": s["edge_pass"],
                "stability_pass": s.get("stability_pass"),
                "lane_decision": s["lane_decision"],
            },
        }
    cmp = {"reference_note": fq["reference_note"],
           "forbidden_claim": lane_cmp("forbidden_claim"),
           "critical_condition": lane_cmp("critical_condition"),
           "tokens": {"LUNA-MAX-total": total,
                      "LUNA-HIGH-total": FROZEN_HIGH_TOTAL,
                      "ratio": ratio}}
    json.dump(cmp, open(os.path.join(HERE,
              "high-vs-max-final-comparison.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # router
    if qualified_final == ["forbidden_claim"]:
        router = {"forbidden_claim": {
            "PRIMARY": "LUNA_MAX_DUAL_PASS",
            "ESCALATION": "GPT_6_ASTRA_LOW",
            "RESIDUAL": "GPT_5_6_SOL"},
            "critical_condition": {
                "PRIMARY": "GPT_6_ASTRA_LOW",
                "RESIDUAL": "GPT_5_6_SOL"}}
    elif qualified_final == ["critical_condition"]:
        router = {"forbidden_claim": {"PRIMARY": "GPT_6_ASTRA_LOW",
                                      "RESIDUAL": "GPT_5_6_SOL"},
                  "critical_condition": {
                      "PRIMARY": "LUNA_MAX_DUAL_PASS",
                      "ESCALATION": "GPT_6_ASTRA_LOW",
                      "RESIDUAL": "GPT_5_6_SOL"}}
    elif qualified_final:
        router = {"note": "both lanes qualified",
                  "forbidden_claim": {"PRIMARY": "LUNA_MAX_DUAL_PASS"},
                  "critical_condition": {"PRIMARY": "LUNA_MAX_DUAL_PASS"}}
    else:
        router = {"forbidden_claim": {
            "PRIMARY": "GPT_6_ASTRA_LOW",
            "reason": "no Luna config passed frozen full qualification"},
            "critical_condition": {
                "PRIMARY": "GPT_6_ASTRA_LOW",
                "reason": "no Luna config passed frozen full qualification"}}
    router["direct_replacement_answer"] = overall
    router["activation_authorized"] = False
    json.dump(router, open(os.path.join(HERE,
              "proposed-review-router.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("FINALIZED overall:", overall, "qualified:", qualified_final)


if __name__ == "__main__":
    main()
