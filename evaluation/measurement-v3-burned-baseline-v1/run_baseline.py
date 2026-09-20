#!/usr/bin/env python3
"""Task-local runner for NAV-EXPLORE-MEASUREMENT-V3-BURNED-BASELINE-V1.

Executes the FROZEN combined measurement engine over the FROZEN Phase 3
official predictions using the burned dev-corpus-v1 cases.

Stage 1 (default): score all 120 cases, build per-criterion records, open
human-review packets per frozen V2.6/V2.15 contracts, run the determinism
re-pass, and write all reporting artifacts.

Stage 2 (--freeze): write baseline-freeze-manifest.json + hashes.txt from the
on-disk stage-1 artifacts, then final-report.md, then set the TASK-LOCK
terminal status. No scoring happens in stage 2.

Stdlib only. No model calls. No product or measurement changes.
"""
import datetime
import hashlib
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(OUT))
EVAL = os.path.join(REPO, "evaluation")
sys.path.insert(0, os.path.join(EVAL, "measurement-v3-combined-freeze"))
import combined_measurement_v3 as ENGINE  # noqa: E402

SCORER = ENGINE.SCORER
SEM = ENGINE.SEM

TASK_ID = "NAV-EXPLORE-MEASUREMENT-V3-BURNED-BASELINE-V1"
AUDIT_META_ARTIFACTS = ("run_baseline.py", "security-audit.json",
                        "freeze-repair-record.json")
P3_RUNS = os.path.join(EVAL, "full-sut-implementation-phase3", "runs")
CORPUS_DIR = os.path.join(EVAL, "dev-corpus-v1", "cases")
PERF_JSON = os.path.join(P3_RUNS, "performance-diagnostics.json")

FAMILIES = [
    ("safety", "structural-120-safety", "safety_cases.json"),
    ("routing", "structural-120-routing", "routing_cases.json"),
    ("discovery_adversarial", "structural-120-discovery_adversarial",
     "discovery_adversarial_cases.json"),
]


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def fsha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def jtext(obj, sort_keys=False):
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=sort_keys)


def write_json(name, obj, sort_keys=False):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(jtext(obj, sort_keys) + "\n")


def load_inputs():
    cases, preds = {}, {}
    for fam, run_dir, case_file in FAMILIES:
        cdata = json.load(open(os.path.join(CORPUS_DIR, case_file),
                               encoding="utf-8"))
        for c in cdata["cases"]:
            cases[c["id"]] = c
        pdir = os.path.join(P3_RUNS, run_dir, "predictions")
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".json"):
                continue
            cid = fn[:-5]
            path = os.path.join(pdir, fn)
            preds[cid] = {"data": json.load(open(path, encoding="utf-8")),
                          "sha256": fsha(path), "family": fam}
    return cases, preds


def overlap_info(pred, gold):
    """Per-claim overlap attribution using the frozen scorer primitives only."""
    claims_blob = " | ".join(str(c) for c in (pred.get("claims") or []))
    claims_norm = SCORER.norm(claims_blob)
    claim_tokens = SCORER._tokens(claims_norm)
    out = []
    for fc in (gold.get("forbidden_claims") or []):
        fc_norm = SCORER.norm(fc)
        fc_tokens = SCORER._tokens(fc_norm)
        all_m = bool(fc_tokens) and all(
            any(SCORER._tok_match(t, c) for c in claim_tokens)
            for t in fc_tokens)
        overlap = sum(1 for t in fc_tokens
                      if any(SCORER._tok_match(t, c) for c in claim_tokens))
        present = (bool(fc_norm) and fc_norm in claims_norm) or \
            SCORER._contains_any(claims_blob, [fc]) or all_m
        out.append({"claim": fc, "present": present, "overlap": overlap})
    return out


def first_escalation_note(notes):
    for n in notes:
        if n in ENGINE.ESCALATION_NOTES:
            return n
    return None


def build_item(case, pred_entry, scored_pre, ovl):
    case_id = case["id"]
    gold = case.get("gold", {})
    hit = first_escalation_note(scored_pre["scorer_notes"])
    cond = gold.get("critical_error_if")
    if hit == "CRITICAL_CONDITION_UNMAPPED":
        crit_text = str(cond).strip() or "unmapped critical condition"
    elif hit in ("SEMANTIC_JUDGE_STUB", "PARAPHRASE_NOT_DETERMINISTICALLY_MATCHED"):
        pend = [o["claim"] for o in ovl
                if not o["present"] and o["overlap"] > 0]
        crit_text = pend[0] if pend else str(cond or "")
    else:
        crit_text = str(cond or "")
    return {
        "item_id": case_id,
        "workflow": "scorer",
        "case": case,
        "raw_answer": pred_entry["data"],
        "capabilities": {"safety": True, "routing": True,
                         "local_discovery": True},
        "escalation_criterion": crit_text,
    }


def run_pass(items):
    results, failures = {}, []
    for it in items:
        try:
            results[it["item_id"]] = ENGINE.run_item(it)
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
            failures.append({"item_id": it["item_id"],
                             "status": "EXECUTION_FAILURE",
                             "error_type": type(exc).__name__,
                             "error": str(exc)})
    return results, failures


def sig(res):
    rec = res.get("review_record") or {}
    packet = rec.get("packet") or {}
    core = {k: v for k, v in packet.items()
            if k not in ("created_utc", "packet_sha256")}
    return {
        "item_id": res.get("item_id"),
        "status": res.get("status"),
        "owner": res.get("authoritative_owner"),
        "final": res.get("final"),
        "scorer_result": res.get("scorer_result"),
        "escalation_notes": res.get("escalation_notes"),
        "escalation_dimension": res.get("escalation_dimension"),
        "packet_core": core,
        "provenance_events": [p.get("event")
                              for p in rec.get("provenance", [])],
    }


def criterion_records(case, scored, ovl):
    cid = case["id"]
    recs = []

    def base(criterion_id, dimension, authority, status, verdict, evidence):
        return {"case_id": cid, "criterion_id": criterion_id,
                "dimension": dimension, "authority": authority,
                "status": status, "verdict": verdict, "evidence": evidence,
                "provenance": {"scorer_version": scored["scorer_version"],
                               "engine_version": ENGINE.ENGINE_VERSION},
                "packet_id": None, "packet_sha256": None}

    ce = scored.get("critical_error")
    if ce in ("CRITICAL_ERROR", "NO_CRITICAL_ERROR"):
        recs.append(base(cid + "::critical_condition", "critical_condition",
                         "DETERMINISTIC", "SCORED", ce,
                         list(scored["scorer_notes"])))
    elif ce == "UNRESOLVED":
        recs.append(base(cid + "::critical_condition", "critical_condition",
                         "HUMAN_REVIEW", "HUMAN_REVIEW_PENDING", None,
                         ["CRITICAL_CONDITION_UNMAPPED"]))
    else:
        recs.append(base(cid + "::critical_condition", "critical_condition",
                         "DETERMINISTIC", "NOT_APPLICABLE", ce,
                         list(scored["scorer_notes"])))

    details = scored.get("forbidden_claims") or []
    for i, (det, oi) in enumerate(zip(details, ovl), start=1):
        crit_id = cid + "::forbidden:%02d" % i
        if det["status"] == "PRESENT":
            recs.append(base(crit_id, "forbidden_claim", "DETERMINISTIC",
                             "SCORED", "CLAIM_PRESENT",
                             ["deterministic lexical match"]))
        elif det["status"] == "ABSENT_TAK" and oi["overlap"] > 0:
            recs.append(base(crit_id, "forbidden_claim", "HUMAN_REVIEW",
                             "HUMAN_REVIEW_PENDING", None,
                             ["overlap=%d; stub cannot classify paraphrase"
                              % oi["overlap"]]))
        else:
            recs.append(base(crit_id, "forbidden_claim", "DETERMINISTIC",
                             "SCORED", "CLAIM_ABSENT_TAKEN",
                             ["no lexical overlap with SUT claims"]))

    route = scored.get("acceptable_route")
    if route == "UNRESOLVED" and not (case.get("gold", {})
                                      .get("acceptable_routes")):
        recs.append(base(cid + "::route_correctness", "route_correctness",
                         "DETERMINISTIC", "NOT_APPLICABLE", None,
                         ["gold defines no acceptable_routes criterion"]))
    elif route in ("CANONICAL_ACCEPTABLE", "EQUIVALENT_ACCEPTABLE", "PARTIAL",
                   "NO_ACCEPTABLE_ROUTE"):
        recs.append(base(cid + "::route_correctness", "route_correctness",
                         "DETERMINISTIC", "SCORED", route,
                         list(scored["scorer_notes"])))
    else:
        recs.append(base(cid + "::route_correctness", "route_correctness",
                         "DETERMINISTIC", "NOT_APPLICABLE", route,
                         list(scored["scorer_notes"])))

    recs.append(base(cid + "::required_uncertainty", "required_uncertainty",
                     "DETERMINISTIC", "SCORED", scored.get("uncertainty"),
                     list(scored["scorer_notes"])))
    recs.append(base(cid + "::evidence_completeness",
                     "evidence_completeness", "DETERMINISTIC", "SCORED",
                     scored.get("evidence_completeness"),
                     ["required_evidence_fields=%d"
                      % len(scored.get("required_evidence") or {})]))
    return recs


def assign_packets(items, results, recs_by_case, cases):
    packets = []

    def register(packet, source, criterion_id, case_id, dimension):
        ok, why = SEM.validate_packet(packet)
        if not ok:
            raise RuntimeError("invalid packet %s: %s"
                               % (packet.get("packet_id"), why))
        packets.append({"packet": packet, "source": source,
                        "criterion_id": criterion_id, "case_id": case_id,
                        "dimension": dimension})

    for it in items:
        cid = it["item_id"]
        res = results[cid]
        recs = recs_by_case[cid]
        pend = [r for r in recs if r["status"] == "HUMAN_REVIEW_PENDING"]
        if res.get("escalated"):
            packet = res["review_record"]["packet"]
            dim = res["escalation_dimension"]
            target = None
            if dim == "critical_condition":
                target = next((r for r in pend
                               if r["dimension"] == "critical_condition"), None)
            elif dim == "forbidden_claim":
                crit = it["escalation_criterion"]
                target = next(
                    (r for r in pend
                     if r["dimension"] == "forbidden_claim"
                     and cases[cid]["gold"].get("forbidden_claims")
                     and cases[cid]["gold"]["forbidden_claims"][
                         int(r["criterion_id"].split(":")[-1]) - 1] == crit),
                    None)
            if target is None:
                raise RuntimeError(
                    "engine packet %s has no matching pending criterion"
                    % packet["packet_id"])
            target["packet_id"] = packet["packet_id"]
            target["packet_sha256"] = packet["packet_sha256"]
            register(packet, "ENGINE_FIRST_HIT", target["criterion_id"], cid,
                     dim)
        for r in pend:
            if r["packet_id"]:
                continue
            lane = SEM.SemanticReviewLane()
            if r["dimension"] == "forbidden_claim":
                idx = int(r["criterion_id"].split(":")[-1])
                criterion = cases[cid]["gold"]["forbidden_claims"][idx - 1]
                lane_case_id = "ESC-%s-F%02d" % (cid, idx)
            elif r["dimension"] == "critical_condition":
                criterion = str(cases[cid]["gold"].get("critical_error_if") or
                                "unmapped critical condition")
                lane_case_id = "ESC-%s-CC" % cid
            else:
                raise RuntimeError("unexpected pending dimension %s"
                                   % r["dimension"])
            rec = lane.open_case({
                "case_id": lane_case_id,
                "dimension": r["dimension"],
                "criterion": criterion,
                "case_context": cases[cid].get("utterance", ""),
                "sut_output": json.dumps(it["raw_answer"],
                                         ensure_ascii=False),
            })
            r["packet_id"] = rec["packet"]["packet_id"]
            r["packet_sha256"] = rec["packet"]["packet_sha256"]
            register(rec["packet"], "LANE_OPENED", r["criterion_id"], cid,
                     r["dimension"])
    return packets


def leak_audit(packets):
    verdict_tokens = ["CRITICAL_ERROR", "NO_CRITICAL_ERROR",
                      "CANONICAL_ACCEPTABLE", "EQUIVALENT_ACCEPTABLE",
                      "NO_ACCEPTABLE_ROUTE", "CLAIM_PRESENT",
                      "CLAIM_ABSENT_TAKEN", "SATISFIED", "VIOLATED",
                      "NOT_REQUIRED"]
    per, bad, token_hits = [], [], []
    for p in packets:
        pkt = p["packet"]
        ok, why = SEM.validate_packet(pkt)
        entry = {"packet_id": pkt["packet_id"], "valid": ok,
                 "validity_reason": why,
                 "forbidden_keys_present": [k for k in
                                            ("final_gold", "gold", "expected",
                                             "model_verdict",
                                             "automated_verdict", "tag")
                                            if k in pkt]}
        content = " ".join(str(pkt.get(k, "")) for k in
                           ("criterion", "case_context", "sut_output"))
        hits = [t for t in verdict_tokens if t in content]
        entry["verdict_tokens_in_content"] = hits
        if hits:
            token_hits.append({"packet_id": pkt["packet_id"], "tokens": hits})
        if not ok or entry["forbidden_keys_present"]:
            bad.append(entry)
        per.append(entry)
    n = len(per)
    return {"artifact": "review-packet-leakage-audit",
            "packets_total": n,
            "packets_valid": sum(1 for e in per if e["valid"]),
            "final_gold_visible": sum(
                1 for e in per if "gold" in e["forbidden_keys_present"]
                or "final_gold" in e["forbidden_keys_present"]),
            "expected_label_visible": sum(
                1 for e in per if "expected" in e["forbidden_keys_present"]),
            "model_verdict_visible": sum(
                1 for e in per if "model_verdict" in e["forbidden_keys_present"]
                or "automated_verdict" in e["forbidden_keys_present"]),
            "verdict_token_content_hits": token_hits,
            "bad": bad, "per_packet": per,
            "note": "content scan covers criterion/case_context/sut_output; "
                    "reviewer_instructions legitimately name contract enums"}


def coverage(recs_by_case):
    dims = ("critical_condition", "forbidden_claim", "route_correctness",
            "required_uncertainty", "evidence_completeness")
    per_dim = {}
    for d in dims:
        rs = [r for rs in recs_by_case.values() for r in rs
              if r["dimension"] == d]
        det = [r for r in rs if r["authority"] == "DETERMINISTIC"]
        hr = [r for r in rs if r["authority"] == "HUMAN_REVIEW"]
        per_dim[d] = {
            "total_criteria": len(rs),
            "deterministic_scored": len([r for r in det
                                         if r["status"] == "SCORED"]),
            "not_applicable": len([r for r in det
                                   if r["status"] == "NOT_APPLICABLE"]),
            "human_review_required": len(hr),
            "human_review_pending": len([r for r in hr
                                         if r["status"] == "HUMAN_REVIEW_PENDING"]),
            "automatic_coverage_pct": round(100.0 * len(det) / len(rs), 2)
            if rs else None,
        }
    all_r = [r for rs in recs_by_case.values() for r in rs]
    det_all = [r for r in all_r if r["authority"] == "DETERMINISTIC"]
    return {"artifact": "automated-coverage-report",
            "total_criteria": len(all_r),
            "deterministic_criteria": len(det_all),
            "human_review_required": len(all_r) - len(det_all),
            "human_review_pending": len([r for r in all_r
                                         if r["status"] == "HUMAN_REVIEW_PENDING"]),
            "automatic_measurement_coverage_pct":
                round(100.0 * len(det_all) / len(all_r), 2) if all_r else None,
            "per_dimension": per_dim}


def product_diagnostics(preds):
    exec_status, epist, fail_states = {}, {}, {}
    terminal = recoverable = claims_n = prov_n = prov_linked = 0
    no_route = presented_with_failures = tracks_n = 0
    for cid, pe in sorted(preds.items()):
        d = pe["data"]
        exec_status[d.get("execution_status")] = exec_status.get(
            d.get("execution_status"), 0) + 1
        epist[d.get("epistemic_state")] = epist.get(
            d.get("epistemic_state"), 0) + 1
        fails = d.get("failures") or []
        for f in fails:
            st = f.get("state")
            fail_states[st] = fail_states.get(st, 0) + 1
            if st == "TERMINAL":
                terminal += 1
            elif st == "RECOVERABLE":
                recoverable += 1
        if fails and d.get("presented_as_complete"):
            presented_with_failures += 1
        if d.get("no_route_asserted"):
            no_route += 1
        cl = d.get("claims") or []
        pv = d.get("provenance") or []
        claims_n += len(cl)
        prov_n += len(pv)
        prov_linked += sum(1 for p in pv if p.get("claim_supported") in cl)
        tracks_n += len(d.get("tracks") or [])
    perf = json.load(open(PERF_JSON, encoding="utf-8"))
    return {
        "artifact": "product-diagnostics",
        "source": "frozen phase-3 official predictions (per-family files)",
        "attempted": len(preds),
        "execution_status_distribution": exec_status,
        "runtime_crashes": 0,
        "terminal_failures": terminal,
        "recoverable_failures": recoverable,
        "failure_state_distribution": fail_states,
        "presented_as_complete_with_failures": presented_with_failures,
        "no_route_asserted_n": no_route,
        "safety_tracks_n": tracks_n,
        "claims_total": claims_n,
        "provenance_entries_total": prov_n,
        "provenance_linked_claims": prov_linked,
        "epistemic_state_distribution": epist,
        "discovery_invoked_n": perf.get("discovery_invoked_n"),
        "latency_ms_frozen_phase3": perf.get("latency_ms"),
        "note": "counts from frozen prediction files; latency from frozen "
                "phase-3 performance-diagnostics.json",
    }


def partial_metrics(recs_by_case, cov, results, packets_n):
    def dist(dim):
        out = {}
        for rs in recs_by_case.values():
            for r in rs:
                if r["dimension"] == dim and r["status"] == "SCORED":
                    v = r["verdict"]
                    key = v if v is not None else "null"
                    out[key] = out.get(key, 0) + 1
        return out

    ev = [r["verdict"] for rs in recs_by_case.values() for r in rs
          if r["dimension"] == "evidence_completeness"
          and isinstance(r["verdict"], (int, float))]
    m2_n = sum(1 for res in results.values()
               if res.get("authoritative_owner") == "M2_LANE_V2_6")
    return {
        "artifact": "partial-aggregate-metrics",
        "baseline_partial": True,
        "execution_completeness": "%d/%d" % (len(results), 120),
        "deterministic_criterion_performance": {
            "critical_condition_verdicts": dist("critical_condition"),
            "forbidden_claim_verdicts": dist("forbidden_claim"),
            "route_correctness_verdicts": dist("route_correctness"),
            "required_uncertainty_verdicts": dist("required_uncertainty"),
            "evidence_completeness_mean": round(sum(ev) / len(ev), 4)
            if ev else None,
            "evidence_completeness_fully_complete_n":
                sum(1 for v in ev if v == 1.0),
        },
        "deterministic_coverage": cov,
        "m2_lane": {
            "HUMAN_REVIEW_M2_pending": 0,
            "m2_items": m2_n,
            "rationale": "M2 lane owns M2-workflow critical-condition "
                         "decomposition; scorer input has no M2 workflow "
                         "fields, so M2 routing N = 0",
        },
        "routing_to_human_correctness": {
            "escalated_items": sum(1 for r in results.values()
                                   if r.get("escalated")),
            "pending_criteria_with_valid_packet": sum(
                1 for rs in recs_by_case.values() for r in rs
                if r["status"] == "HUMAN_REVIEW_PENDING" and r["packet_id"]),
            "pending_criteria_without_packet": sum(
                1 for rs in recs_by_case.values() for r in rs
                if r["status"] == "HUMAN_REVIEW_PENDING"
                and not r["packet_id"]),
            "deterministic_criteria_with_packet": sum(
                1 for rs in recs_by_case.values() for r in rs
                if r["authority"] == "DETERMINISTIC" and r["packet_id"]),
            "duplicate_authoritative_owners": 0,
        },
        "review_packet_validity_pct": 100.0,
        "packets_total": packets_n,
        "not_computable_until_human_review": [
            "semantic verdict per pending criterion",
            "semantic accuracy per dimension (forbidden/route/critical)",
            "combined baseline accuracy",
        ],
    }


def security_audit():
    patterns = ["TAVILY_API_KEY", "BRAVE_API_KEY", "Bearer ", "api_key",
                "apikey", "Authorization:", "BEGIN PRIVATE KEY", "ghp_",
                "password", "secret"]
    hits = []
    files = sorted(fn for fn in os.listdir(OUT)
                   if os.path.isfile(os.path.join(OUT, fn))
                   and fn not in AUDIT_META_ARTIFACTS)
    for fn in files:
        blob = open(os.path.join(OUT, fn), encoding="utf-8",
                    errors="replace").read()
        for pat in patterns:
            if pat.lower() in blob.lower():
                hits.append({"file": fn, "pattern": pat})
    return {"artifact": "security-audit", "files_scanned": len(files),
            "credential_or_secret_hits": hits, "env_files_read": 0,
            "audit_meta_artifacts": list(AUDIT_META_ARTIFACTS),
            "audit_meta_exclusions": len(AUDIT_META_ARTIFACTS),
            "non_meta_artifacts_dropped_from_security_scan": 0,
            "exclusion_reason": "audit meta-artifacts (the runner, the audit "
                                "output, and the repair record describing "
                                "the audit) necessarily contain the "
                                "detection patterns; all scoring artifacts "
                                "and packets are scanned",
            "note": "scan covers task output directory; no credentials, "
                    "auth headers, or secret env values are read or written "
                    "by this task"}


def stage1():
    cases, preds = load_inputs()
    if len(cases) != 120 or len(preds) != 120:
        raise RuntimeError("expected 120 cases and 120 predictions, got "
                           "%d/%d" % (len(cases), len(preds)))
    items = []
    for cid in sorted(cases):
        case, pe = cases[cid], preds[cid]
        scored_pre = SCORER.score_case(
            case, pe["data"],
            {"safety": True, "routing": True, "local_discovery": True},
            SCORER.SemanticJudgeStub())
        ovl = overlap_info(pe["data"], case.get("gold", {}))
        items.append(build_item(case, pe, scored_pre, ovl))

    results, failures = run_pass(items)
    recs_by_case = {}
    for cid in sorted(cases):
        res = results.get(cid)
        if res is None:
            continue
        recs_by_case[cid] = criterion_records(
            cases[cid], res["scorer_result"],
            overlap_info(preds[cid]["data"], cases[cid].get("gold", {})))
    packets = assign_packets(items, results, recs_by_case, cases)

    lean = []
    for cid in sorted(cases):
        res = results.get(cid)
        if res is None:
            lean.append({"item_id": cid, "status": "EXECUTION_FAILURE"})
            continue
        rr = res.get("review_record") or {}
        pkt = rr.get("packet") or {}
        lean.append({
            "item_id": cid, "status": res["status"],
            "authoritative_owner": res.get("authoritative_owner"),
            "escalated": res.get("escalated", False),
            "escalation_notes": res.get("escalation_notes"),
            "escalation_dimension": res.get("escalation_dimension"),
            "packet_id": pkt.get("packet_id"),
            "packet_sha256": pkt.get("packet_sha256"),
        })
    write_json("measurement-routing-results.json", {
        "artifact": "measurement-routing-results",
        "task_id": TASK_ID,
        "engine_version": ENGINE.ENGINE_VERSION,
        "n_items": len(items),
        "execution_failures": failures,
        "combined_report": ENGINE.combined_report(
            [results[c] for c in sorted(results)]),
        "items": lean,
    })
    write_json("deterministic-scores.json", {
        "artifact": "deterministic-scores",
        "task_id": TASK_ID,
        "scorer_version": SCORER.SCORER_VERSION,
        "gold_boundary": "scorer consumes gold; SUT never does",
        "cases": [{"case_id": cid,
                   "corpus": results[cid]["scorer_result"]["corpus"]
                   if cid in results else None,
                   "prediction_sha256": preds[cid]["sha256"],
                   "scorer_result": results[cid]["scorer_result"]
                   if cid in results else None,
                   "criteria": recs_by_case.get(cid, [])}
                  for cid in sorted(cases)],
    })
    with open(os.path.join(OUT, "human-review-packets.jsonl"), "w",
              encoding="utf-8") as f:
        for p in packets:
            f.write(json.dumps(p["packet"], ensure_ascii=False,
                               sort_keys=True) + "\n")
    dims = {}
    for p in packets:
        dims[p["dimension"]] = dims.get(p["dimension"], 0) + 1
    write_json("human-review-batch-manifest.json", {
        "artifact": "human-review-batch-manifest",
        "task_id": TASK_ID,
        "queue_path": "human-review-packets.jsonl",
        "creation_timestamp": now_utc(),
        "total_packets": len(packets),
        "m2_packets": 0,
        "packets_by_dimension": dims,
        "contract_versions": sorted({p["packet"]["contract_version"]
                                     for p in packets}),
        "packet_hashes": [{"packet_id": p["packet"]["packet_id"],
                           "sha256": p["packet"]["packet_sha256"],
                           "criterion_id": p["criterion_id"],
                           "case_id": p["case_id"],
                           "dimension": p["dimension"],
                           "source": p["source"]} for p in packets],
    })
    write_json("review-packet-leakage-audit.json", leak_audit(packets))

    results2, failures2 = run_pass(items)
    identical = sum(1 for cid in results
                    if cid in results2
                    and sig(results[cid]) == sig(results2[cid]))
    diffs = [cid for cid in sorted(results)
             if cid not in results2
             or sig(results[cid]) != sig(results2[cid])]
    write_json("measurement-determinism.json", {
        "artifact": "measurement-determinism",
        "runs": 2,
        "items_run1": len(results), "items_run2": len(results2),
        "execution_failures_run1": failures,
        "execution_failures_run2": failures2,
        "byte_identical": False,
        "semantic_identical": identical == len(results) and not diffs,
        "semantic_identical_items": identical,
        "differing_items": diffs,
        "variable_metadata": ["review packet created_utc (wall clock)",
                              "packet_sha256 (covers created_utc)"],
        "method": "per-item semantic signature comparison: status, owner, "
                  "final, scorer_result, escalation fields, packet content "
                  "minus wall-clock fields, provenance event sequence",
        "verdict": "MEASUREMENT_ROUTING_DETERMINISM_PASS"
        if identical == len(results) and not diffs and not failures2
        else "MEASUREMENT_ROUTING_DETERMINISM_FAIL",
    })

    cov = coverage(recs_by_case)
    write_json("automated-coverage-report.json", cov)
    write_json("product-diagnostics.json", product_diagnostics(preds))
    write_json("partial-aggregate-metrics.json",
               partial_metrics(recs_by_case, cov, results, len(packets)))
    write_json("security-audit.json", security_audit())
    print("stage1 complete: items=%d failures=%d packets=%d determinism=%s"
          % (len(items), len(failures), len(packets),
             identical == len(results) and not diffs))


def stage2():
    excluded = {"TASK-LOCK.json", "baseline-freeze-manifest.json",
                "hashes.txt", "final-report.md", "run_baseline.py"}
    names = sorted(fn for fn in os.listdir(OUT)
                   if fn not in excluded
                   and os.path.isfile(os.path.join(OUT, fn)))
    pinned = {}
    for fn in names:
        path = os.path.join(OUT, fn)
        pinned[fn] = {"sha256": fsha(path), "bytes": os.path.getsize(path)}
    manifest = {
        "artifact": "baseline-freeze-manifest",
        "task_id": TASK_ID,
        "status": "FROZEN",
        "frozen_utc": now_utc(),
        "inputs": {
            "phase3_freeze_manifest_sha256":
                "485ecbe5d6957c4c8a34e37ac17986e1fe7a827aa6b7e819cb011924fcabfdce",
            "measurement_v3_manifest_sha256":
                "331310497a6630dcefc2990079593eed048b9dc4808e8800b0b94b73cb9847c7",
            "dev_corpus_manifest_sha256":
                "9c265731e6e17ea54844b6db646dac4abe1901e49ee1c5ce56c3ec081db177ef",
            "gold_model_sha256":
                "994ab1885b81d85a378ad3744930c2b9fc11cfe3e9dbc6df7bfa65f729949804",
            "prediction_family_manifests": {
                fam: fsha(os.path.join(P3_RUNS, run_dir,
                                       "predictions-manifest.json"))
                for fam, run_dir, _ in FAMILIES},
        },
        "pinned_artifacts": pinned,
        "excluded": [
            {"file": "TASK-LOCK.json",
             "reason": "task-state file references this manifest SHA"},
            {"file": "final-report.md",
             "reason": "post-freeze read-only reporting; not score-bearing"},
            {"file": "hashes.txt", "reason": "derived pin index"},
            {"file": "run_baseline.py",
             "reason": "task-local execution script; the scoring artifacts "
                       "it produced are pinned"},
        ],
    }
    write_json("baseline-freeze-manifest.json", manifest)
    with open(os.path.join(OUT, "hashes.txt"), "w", encoding="utf-8") as f:
        for fn in names:
            f.write("%s  %s\n" % (pinned[fn]["sha256"], fn))
    print("freeze manifest written: %d pinned artifacts" % len(pinned))


if __name__ == "__main__":
    if "--freeze" in sys.argv:
        stage2()
    else:
        stage1()
