#!/usr/bin/env python3
"""Read-only residual-failure analysis over the frozen Wave-1 measurement.

Recomputes every number in the deliverables from frozen artifacts on disk.
No conclusion is hardcoded; outputs are derived and stamped with provenance.
Task: NAV-EXPLORE-FULL-SUT-POST-WAVE1-RESIDUAL-FAILURE-ANALYSIS-V1
"""
import collections, hashlib, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
WD = os.path.dirname(EVAL)

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def rel(p):
    return os.path.relpath(p, WD)

def load(p):
    with open(os.path.join(WD, p)) as f:
        return json.load(f)

def save(obj, name):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    return rel(p), sha(p)

COMPLETE = "evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/complete-wave1-measurement-results.json"
COMPLETE_SHA = "1f4aac89aa90ef2e5b7e2da2455249633cf2d2c12c7856c64b202a5e45e5e7c1"
OLD_BASE = "evaluation/measurement-v3-final-authority-provenance-repair-v1/combined-measurement-results-complete-provenance-corrected.json"
RUNS = "evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2"
FAMFILE = {"routing_cases": "routing", "discovery_adversarial_cases": "discovery_adversarial", "safety_cases": "safety"}

def semantic_state(dimension, verdict):
    if dimension == "critical_condition":
        return "FAIL" if verdict in ("TRIGGERED", "CRITICAL_ERROR") else ("PASS" if verdict == "NOT_TRIGGERED" else "UNRESOLVED")
    if dimension == "forbidden_claim":
        return "FAIL" if verdict in ("PRESENT", "CLAIM_PRESENT") else ("PASS" if verdict in ("ABSENT", "CLAIM_ABSENT_TAKEN") else "UNRESOLVED")
    if dimension == "route_correctness":
        if verdict is None:
            return "ABSENT_OR_NOT_APPLICABLE"
        return "PASS" if verdict == "ACCEPTABLE" else ("UNRESOLVED" if verdict == "UNRESOLVED" else "FAIL")
    if dimension == "required_uncertainty":
        return "PASS" if verdict in ("SATISFIED", "NOT_REQUIRED") else ("DEGRADED" if verdict == "PARTIAL" else ("FAIL" if verdict == "VIOLATED" else "UNRESOLVED"))
    if dimension == "evidence_completeness":
        return "PASS" if verdict == 1.0 else ("DEGRADED" if isinstance(verdict, (int, float)) and 0 < verdict < 1 else ("FAIL" if verdict == 0.0 else "UNRESOLVED"))
    return "UNRESOLVED"

def main():
    integrity = {"checks": {}, "pins": {}}
    # P1..P6 pins
    pins = {
        "P1_wave1_product_candidate_manifest": "evaluation/full-sut-repair-wave-1-v1/repaired-sut-manifest.json",
        "P2_wave1_prediction_manifests": ["evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2/safety/predictions-manifest.json", "evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2/routing/predictions-manifest.json", "evaluation/full-sut-repair-wave-1-v1/runs/structural-120-replay-v2/discovery_adversarial/predictions-manifest.json"],
        "P3_wave1_measurement_freeze": "evaluation/measurement-v3-remeasure-repair-wave-1/wave1-measurement-freeze-manifest.json",
        "P4_comparator_terminal": "evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/TASK-LOCK.json",
        "P5_final_600row": COMPLETE,
        "P6_old_baseline": OLD_BASE,
    }
    for k, v in pins.items():
        paths = v if isinstance(v, list) else [v]
        integrity["pins"][k] = [{"path": rel(os.path.join(WD, p)), "sha256": sha(os.path.join(WD, p))} for p in paths]
    comp_lock = load(rel(os.path.join(WD, pins["P4_comparator_terminal"])))
    integrity["checks"]["comparator_lock_closed"] = comp_lock.get("status") == "CLOSED" and comp_lock.get("terminal_status") == "MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE"
    comp_man = load("evaluation/measurement-v3-wave1-consensus-comparator-repair-v1/comparator-repair-freeze-manifest.json")
    got = [p["sha256"] for p in integrity["pins"]["P5_final_600row"]][0]
    integrity["checks"]["final_600row_matches_comparator_manifest_pin"] = got == comp_man["pins"]["complete-wave1-measurement-results.json"]["sha256"] == COMPLETE_SHA
    integrity["checks"]["final_600row_sha256"] = got
    res = load(COMPLETE)
    cov = res["coverage"]
    integrity["checks"]["authority_mix"] = {"TOTAL": cov.get("TOTAL_CRITERIA"), "DETERMINISTIC": cov.get("DETERMINISTIC"), "LLM_REVIEWED": cov.get("LLM_REVIEWED"), "LLM_ADJUDICATED": cov.get("LLM_ADJUDICATED"), "HUMAN_REVIEWED": cov.get("HUMAN_REVIEWED"), "PENDING": cov.get("PENDING_HUMAN_ADJUDICATION")}
    counts = collections.Counter(); per_dim = collections.Counter(); rows = []
    for c in res["cases"]:
        for r in c["criteria"]:
            st = semantic_state(r["dimension"], r["verdict"])
            counts[st] += 1; per_dim[(r["dimension"], st)] += 1
            rows.append({"case_id": r["case_id"], "criterion_id": r["criterion_id"], "dimension": r["dimension"], "verdict": r["verdict"], "state": st, "authority": r["authority"], "evidence": r.get("evidence")})
    applicable = sum(v for k, v in counts.items() if k not in ("ABSENT_OR_NOT_APPLICABLE",))
    agg = {"TOTAL": sum(counts.values()), "states": dict(counts), "APPLICABLE_DENOMINATOR": applicable,
           "HARD_FAIL_RATE": round(counts.get("FAIL", 0) / applicable, 4),
           "NON_PASS_RATE": round((counts.get("FAIL", 0) + counts.get("UNRESOLVED", 0) + counts.get("DEGRADED", 0)) / applicable, 4),
           "per_dimension": {f"{a}|{b}": v for (a, b), v in sorted(per_dim.items())}}
    integrity["checks"]["aggregate_recomputed"] = {"PASS": counts.get("PASS"), "FAIL": counts.get("FAIL"), "UNRESOLVED": counts.get("UNRESOLVED"), "DEGRADED": counts.get("DEGRADED"), "N_A": counts.get("ABSENT_OR_NOT_APPLICABLE"), "TOTAL": agg["TOTAL"], "hard_fail_rate": agg["HARD_FAIL_RATE"], "non_pass_rate": agg["NON_PASS_RATE"]}
    old = load(OLD_BASE)
    oldrows = {}
    for c in old["cases"]:
        for r in c["criteria"]:
            oldrows[r["criterion_id"]] = semantic_state(r["dimension"], r["verdict"])
    # Frozen authority policy (updated-baseline-transition-matrix.json): FAIL->PASS/DEGRADED
    # counts as improvement; FAIL->UNRESOLVED is a move to LLM review, not an improvement.
    transitions = collections.Counter()
    for r in rows:
        transitions[(oldrows.get(r["criterion_id"]), r["state"])] += 1
    improved = transitions.get(("FAIL", "PASS"), 0) + transitions.get(("FAIL", "DEGRADED"), 0)
    regressed = sum(1 for r in rows if r["state"] == "FAIL" and oldrows.get(r["criterion_id"]) != "FAIL")
    integrity["checks"]["delta_vs_old_baseline"] = {"improved": improved, "regressed": regressed,
        "fail_to_unresolved_review_moves": transitions.get(("FAIL", "UNRESOLVED"), 0),
        "semantic_state_transitions_recomputed": {f"{a} -> {b}": v for (a, b), v in sorted(transitions.items())}}

    # prediction joins
    def pred(cid, fam):
        return load(os.path.join(RUNS, fam, "predictions", cid + ".json"))
    goldmap = {}
    for f in FAMFILE:
        d = load(f"evaluation/dev-corpus-v1-1-repair/cases/{f}.json")
        for c in d["cases"]:
            goldmap[c["id"]] = (f, c["gold"], c.get("utterance"))

    inventory = []
    for r in rows:
        if r["state"] not in ("FAIL", "UNRESOLVED", "DEGRADED"):
            continue
        fam, gold, utt = goldmap[r["case_id"]]
        p = pred(r["case_id"], FAMFILE[fam])
        old_state = oldrows.get(r["criterion_id"])
        rec = {"case_id": r["case_id"], "criterion_id": r["criterion_id"], "dimension": r["dimension"], "state": r["state"], "authority": r["authority"], "verdict": r["verdict"], "criterion_text": r["criterion_id"], "prior_baseline_state": old_state, "wave1_changed_relevant": old_state != r["state"], "provenance_state": "has_source_url" if any(pr.get("source_url") for pr in (p.get("provenance") or [])) else "no_source_url", "route_state": {"no_route_asserted": p.get("no_route_asserted"), "routes": p.get("routes"), "presented_as_complete": p.get("presented_as_complete")}, "epistemic_state": p.get("epistemic_state"), "evidence_scorer_note": r.get("evidence"), "prediction_ref": rel(os.path.join(WD, RUNS, FAMFILE[fam], "predictions", r["case_id"] + ".json"))}
        inventory.append(rec)
    # RC-01 residual: EXEC failure mechanisms
    rc01 = sum(1 for r in rows if r["dimension"] == "critical_condition" and r["verdict"] == "CRITICAL_ERROR" and any(x in ("SOURCE_URL_REQUIRED_MISSING", "PROVENANCE_CHAIN_BROKEN") for x in (r.get("evidence") or [])))
    # RC-02: safety mismatches
    safemis = []
    ordermap = {"ACUTE": 0, "URGENT": 1, "PRIORITY": 2, "NON_ACUTE": 3}
    def lvl(s):
        s = str(s).upper()
        if "NOT_ACUTE" in s or "NO_ACUTE" in s: return "NON_ACUTE"
        for k in ordermap:
            if k in s: return k
        return s
    for c in load("evaluation/dev-corpus-v1-1-repair/cases/safety_cases.json")["cases"]:
        p = pred(c["id"], "safety")
        gp, sp = c["gold"].get("safety_priority"), p.get("safety_priority")
        if gp is None or sp is None or lvl(gp) != lvl(sp):
            safemis.append({"case_id": c["id"], "gold": gp, "sut": sp})
    junk_pat = re.compile(r"^(#|kilde|nasjonal|hensikt|anbefalt|tilgangsverifisering|revisjon|\d+[.:]|§|-)", re.I)
    rcls = collections.Counter(); rex = collections.defaultdict(list)
    funnel = collections.Counter()
    for cid, (fam, gold, _) in sorted(goldmap.items()):
        p = pred(cid, FAMFILE[fam])
        if gold.get("acceptable_routes") is None:
            funnel["route_not_applicable"] += 1; continue
        funnel["cases_requiring_route_eval"] += 1
        routes = [str(x) for x in (p.get("routes") or []) if str(x).strip()]
        if not routes:
            funnel["no_structured_route"] += 1; rcls["A_NO_ROUTE_GENERATED"] += 1; rex["A_NO_ROUTE_GENERATED"].append(cid); continue
        funnel["structured_route_produced"] += 1
        real = [x for x in routes if not junk_pat.match(x.strip())]
        if not real:
            funnel["no_usable_route_junk_only"] += 1; rcls["A_NO_ROUTE_GENERATED_JUNK_ONLY"] += 1; rex["A_NO_ROUTE_GENERATED_JUNK_ONLY"].append(cid); continue
        funnel["route_with_content"] += 1
        has_url = any(pr.get("source_url") for pr in (p.get("provenance") or []))
        funnel["route_case_with_provenance_url" if has_url else "route_case_without_provenance_url"] += 1
        ans_norm = str(p.get("answer") or "").lower()
        hit = any(any(t in ans_norm for t in re.findall(r"[a-zæøå]{5,}", str(gr).lower())) for gr in gold["acceptable_routes"])
        funnel["rendered_mentions_gold_route_token" if hit else "rendered_misses_gold_route_token"] += 1
        rcls["B_WRONG_ROUTE_TARGET"] += 1; rex["B_WRONG_ROUTE_TARGET"].append(cid)
    # contamination
    nat = {"answers_with_nasjonal_blocks": 0, "answers_with_2plus": 0, "max_blocks": 0, "block_total": 0}
    lens = []
    for fam in FAMFILE.values():
        d = os.path.join(WD, RUNS, fam, "predictions")
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"): continue
            ans = str(load(rel(f"{RUNS}/{fam}/predictions/{fn[:-5]}.json")).get("answer") or "")
            n = ans.count("Nasjonal informasjon")
            lens.append(len(ans))
            if n: nat["answers_with_nasjonal_blocks"] += 1; nat["block_total"] += n
            if n >= 2: nat["answers_with_2plus"] += 1
            nat["max_blocks"] = max(nat["max_blocks"], n)
    noise = {"answers_with_nasjonal_blocks": nat["answers_with_nasjonal_blocks"], "nasjonal_block_total": nat["block_total"], "answers_with_2plus_blocks": nat["answers_with_2plus"], "max_blocks_in_one_answer": nat["max_blocks"], "answer_len_median": statistics.median(lens), "answer_len_p90": sorted(lens)[int(0.9 * len(lens))], "answer_len_max": max(lens)}
    # evidence attachment classes
    ev_attach = collections.Counter()
    for r in rows:
        if r["dimension"] == "evidence_completeness" and r["verdict"] == 0.0:
            fam = goldmap[r["case_id"]][0]
            p = pred(r["case_id"], FAMFILE[fam])
            prov = p.get("provenance") or []
            nonempty = [k for k, v in (p.get("evidence") or {}).items() if v]
            has_url = any(pr.get("source_url") for pr in prov)
            ev_attach["NO_PROVENANCE_ENTRIES" if not prov else ("PROV_HAS_URL_NOT_ATTACHED_TO_EVIDENCE_FIELDS" if has_url and not nonempty else ("PROV_NO_URL_FIELDS_UNPOPULATED" if not nonempty else "MIXED"))] += 1
    out = {"artifact": "post-wave1-residual-analysis-derived", "integrity": integrity, "aggregate": agg,
           "residual_count": len(inventory), "residual_by_dimension": dict(collections.Counter(r["dimension"] + "|" + r["state"] for r in inventory)),
           "residual_cases": len(set(r["case_id"] for r in inventory)),
           "rc01_critical_provenance_residual": rc01, "rc02_safety_mismatches": safemis,
           "route_classification": dict(rcls), "route_examples": {k: v for k, v in rex.items()},
           "routing_funnel": dict(funnel), "retrieval_contamination": noise, "evidence_attachment_classes": dict(ev_attach),
           "inventory": inventory}
    p1, s1 = save(out, "wave1-residual-inventory.json")
    # derived copies
    p2, s2 = save({"artifact": "residual-failure-families-derived", "note": "counts derived from wave1-residual-inventory.json", "residual_count": len(inventory), "route_classification": dict(rcls), "funnel": dict(funnel), "contamination": noise, "evidence_attachment": dict(ev_attach), "rc01_residual": rc01, "rc02_mismatches": len(safemis)}, "derived-summary.json")
    print(json.dumps({"inventory": p1, "sha": s1, "derived": p2, "derived_sha": s2, "residual_count": len(inventory), "residual_cases": len(set(r["case_id"] for r in inventory)), "agg": agg, "improved": improved, "regressed": regressed, "fail_to_unresolved": integrity["checks"]["delta_vs_old_baseline"]["fail_to_unresolved_review_moves"], "rc01": rc01, "safety_mis": len(safemis), "route_cls": dict(rcls), "funnel": dict(funnel), "contamination": noise, "ev": dict(ev_attach)}, indent=1))

if __name__ == "__main__":
    main()
