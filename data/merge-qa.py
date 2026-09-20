#!/usr/bin/env python3
"""Merge subagent splits + QA for NAV-EXPLORE-MUNICIPAL-MENTAL-HEALTH-SAMPLE-V1."""
import json, sys, re, urllib.request
from collections import Counter, defaultdict

ROOT = "/Users/reidar/Projectos/NAV Explore"
DATE = "2026-09-08"

def load_split(path):
    try:
        with open(f"{ROOT}/{path}") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def norm_knr(k):
    return str(k).zfill(4)

DIAG_MAP = {
    "diagnoser": "diagnoser", "stiller diagnoser": "diagnoser", "kan stille diagnoser": "diagnoser",
    "diagnoser stilles ikke": "ikke_diagnoser", "stiller ikke diagnoser": "ikke_diagnoser",
    "ikke diagnoser": "ikke_diagnoser", "ikke_diagnoser": "ikke_diagnoser",
    "ikke opplyst": "ikke_opplyst", "ikke_opplyst": "ikke_opplyst", "unknown": "unknown",
}

def norm_diag(v):
    if not isinstance(v, str): return "unknown"
    return DIAG_MAP.get(v.strip().lower(), DIAG_MAP.get(v.strip(), "ikke_opplyst" if "opplyst" in v.lower() else "unknown"))

def main():
    sample = json.load(open(f"{ROOT}/municipality-sample.json"))
    a = load_split("data/sample-split-a.json") or []
    b = load_split("data/sample-split-b.json") or []
    splits = {norm_knr(m["kommunenummer"]): m for m in a + b}

    problems = []
    municipalities = []
    for s in sample:
        knr = norm_knr(s["kommunenummer"])
        if knr not in splits:
            problems.append(f"MISSING split data for {knr} {s['kommune']}")
            continue
        m = dict(splits[knr])
        m["fylke"] = s["fylke"]
        m["region"] = s["region"]
        m["previously_researched"] = s["previously_researched"]
        m["ssb_sentralitetsklasse"] = s["ssb_sentralitetsklasse"]
        if int(m.get("ssb_sentralitetsklasse", -1)) != s["ssb_sentralitetsklasse"]:
            problems.append(f"KLASSE MISMATCH {knr}")
        for svc in m.get("services", []):
            svc["diagnostic_service"] = norm_diag(svc.get("diagnostic_service"))
            if svc.get("retrieved_date") != DATE:
                problems.append(f"DATE {knr} {svc.get('service_name','?')}: {svc.get('retrieved_date')}")
            if svc.get("waiting_time_published") is False and svc.get("waiting_time_value") not in (None, "NOT_PUBLISHED"):
                problems.append(f"WAITING-TIME INFERENCE? {knr} {svc.get('service_name')}")
            if svc.get("self_referral") not in ("direkte","skjema","fastlege","annen_fagperson","unclear","unknown"):
                problems.append(f"SELF_REFERRAL BAD {knr}: {svc.get('self_referral')}")
            if svc.get("diagnostic_service") not in ("diagnoser","ikke_diagnoser","ikke_opplyst","unknown"):
                problems.append(f"DIAG BAD {knr}: {svc.get('diagnostic_service')}")
            if not svc.get("source_url"):
                problems.append(f"NO SOURCE {knr} {svc.get('service_name')}")
        rout = {"CLEAR_LOCAL_ROUTE","MULTIPLE_VALID_ROUTES","LOCAL_ROUTING_UNCLEAR","NO_MATCHING_LOCAL_SERVICE_FOUND"}
        for sc in "ABCD":
            if m.get("scenarios",{}).get(sc) not in rout:
                problems.append(f"SCENARIO BAD {knr} {sc}: {m.get('scenarios',{}).get(sc)}")
        municipalities.append(m)

    knrs = [m["kommunenummer"] for m in municipalities]
    if len(set(knrs)) != len(knrs):
        problems.append("DUPLICATE kommunenummer")

    # coverage metrics
    n = len(municipalities)
    def frac(pred, denom=None):
        d = denom if denom is not None else n
        return {"numerator": sum(1 for x in municipalities if pred(x)), "denominator": d}
    coverage = {
      "municipal_coverage": frac(lambda m: bool(m.get("services")) or m.get("rph",{}).get("classification") not in (None,"UNCLEAR")),
      "service_source_coverage": frac(lambda m: any(s.get("source_url") for s in m.get("services",[]))),
      "age_boundary_completeness": None,
      "referral_completeness": None,
      "cost_completeness": None,
      "published_waiting_time_completeness": None,
      "rph_classification_completeness": frac(lambda m: m.get("rph",{}).get("classification") in ("OWN_RPH","INTERMUNICIPAL_RPH","OTHER_RPH_ACCESS","NO_RPH_FOUND")),
      "psychologist_delivery_model_completeness": frac(lambda m: m.get("psychologist",{}).get("delivery_model") not in (None,"no_public_documentation_found") or m.get("psychologist",{}).get("delivery_model")=="no_public_documentation_found" and False),
    }
    all_svcs = [(m, s) for m in municipalities for s in m.get("services", [])]
    def svc_frac(pred):
        d = len(all_svcs)
        return {"numerator": sum(1 for _, s in all_svcs if pred(s)), "denominator": d}
    coverage["age_boundary_completeness"] = svc_frac(lambda s: s.get("target_age_text") or s.get("target_age_min") is not None or s.get("target_age_max") is not None)
    coverage["referral_completeness"] = svc_frac(lambda s: s.get("self_referral") not in ("unclear","unknown",None) or s.get("referral_required") in ("yes","no"))
    coverage["cost_completeness"] = svc_frac(lambda s: s.get("cost") not in ("ukjent","unknown",None))
    coverage["published_waiting_time_completeness"] = svc_frac(lambda s: s.get("waiting_time_published") is True)

    # RPH + psychologist tallies
    rph_tally = Counter(m.get("rph",{}).get("classification","UNCLEAR") for m in municipalities)
    psy_tally = Counter(m.get("psychologist",{}).get("delivery_model","no_public_documentation_found") for m in municipalities)

    # scenario tallies per scenario + sentrality comparison
    scenario_tally = {sc: Counter(m.get("scenarios",{}).get(sc) for m in municipalities) for sc in "ABCD"}
    by_class = defaultdict(list)
    for m in municipalities:
        by_class[m["ssb_sentralitetsklasse"]].append(m)
    sentrality = {}
    for kl in range(1,7):
        ms = by_class[kl]
        svcs = [s for m in ms for s in m.get("services",[])]
        sentrality[kl] = {
          "n": len(ms),
          "service_count": len(svcs),
          "services_per_municipality": round(len(svcs)/len(ms),2) if ms else 0,
          "direct_access_services": sum(1 for s in svcs if s.get("self_referral") in ("direkte","skjema")),
          "rph_available": sum(1 for m in ms if m.get("rph",{}).get("classification") in ("OWN_RPH","INTERMUNICIPAL_RPH","OTHER_RPH_ACCESS")),
          "psy_direct": sum(1 for m in ms if m.get("psychologist",{}).get("delivery_model")=="direct_to_residents"),
          "clear_or_multiple_routes": sum(1 for m in ms for sc in "ABCD" if m.get("scenarios",{}).get(sc) in ("CLEAR_LOCAL_ROUTE","MULTIPLE_VALID_ROUTES")),
          "scenario_cells": 4*len(ms),
          "public_data_completeness": round(sum(1 for s in svcs if s.get("self_referral") not in ("unclear","unknown") and s.get("cost") not in ("ukjent","unknown"))/max(len(svcs),1),2),
        }

    out = {
      "task_id": "NAV-EXPLORE-MUNICIPAL-MENTAL-HEALTH-SAMPLE-V1",
      "sample_source": "SSB KLASS 128 Standard for sentralitet, correspondence 131->128 (2024-01-01)",
      "retrieved_date": DATE,
      "municipality_count": n,
      "centralitetsklasse_distribution": {str(k): v for k, v in sorted(Counter(m["ssb_sentralitetsklasse"] for m in municipalities).items())},
      "municipalities": municipalities,
      "_qa": {"problems": problems, "coverage": coverage, "rph_tally": dict(rph_tally), "psychologist_tally": dict(psy_tally), "scenario_tally": {k: dict(v) for k, v in scenario_tally.items()}, "sentrality_comparison": sentrality},
    }
    with open(f"{ROOT}/data/municipal-mental-health-sample-v1.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({"municipalities": n, "services": len(all_svcs), "problems": problems[:20], "coverage": coverage, "rph": dict(rph_tally), "psy": dict(psy_tally), "scenarios": {k: dict(v) for k, v in scenario_tally.items()}}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
