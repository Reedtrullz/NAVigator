#!/usr/bin/env python3
"""Merge + QA for 18-23 routing deep-dive (task NAV-EXPLORE-18-23-LOCAL-ROUTING-GAP-V1)."""
import json
import sys
from collections import Counter

GAPS = ["VERIFIED_LOCAL_ROUTE", "VERIFIED_LOCAL_SERVICE_ACCESS_UNCLEAR", "GP_GATEWAY_ONLY",
        "SPECIALIST_GATEWAY", "NO_LOCAL_MATCH_FOUND", "INSUFFICIENT_PUBLIC_DATA"]
SEARCH_KEYS = ["municipal_service_catalog", "mental_health_page", "hfu", "rph",
               "intermunicipal_search", "adult_mental_health"]

def load_merged():
    muns = []
    for p in ("data/18-23-routing-deep-a.json", "data/18-23-routing-deep-b.json"):
        try:
            part = json.load(open(p))
            muns.extend(part if isinstance(part, list) else part.get("municipalities", []))
        except FileNotFoundError:
            print(f"MISSING: {p}", file=sys.stderr)
    return muns

def qa(muns):
    problems = []
    seen = set()
    for m in muns:
        k = m.get("kommune")
        if k in seen:
            problems.append(f"DUPLICATE: {k}")
        seen.add(k)
        log = m.get("search_log", {})
        missing = [x for x in SEARCH_KEYS if x not in log]
        if missing:
            problems.append(f"SEARCH_LOG_INCOMPLETE {k}: {missing}")
        for fld in ("gap_classification", "gap_classification_c_19", "gap_classification_d_22"):
            v = m.get(fld)
            if v not in GAPS:
                problems.append(f"BAD_GAP_ENUM {k} {fld}: {v}")
        for s in m.get("services_18_23", []):
            for f in ("covers_age_19", "covers_age_22"):
                if s.get(f) not in (True, False, "unknown", "UNKNOWN"):
                    problems.append(f"BAD_COVER {k} {s.get('service_name')} {f}={s.get(f)}")
            if not s.get("source_url"):
                problems.append(f"NO_SOURCE {k} {s.get('service_name')}")
    return problems

if __name__ == "__main__":
    muns = load_merged()
    problems = qa(muns)
    out = {
        "task_id": "NAV-EXPLORE-18-23-LOCAL-ROUTING-GAP-V1",
        "retrieved_date": "2026-09-08",
        "municipality_count": len(muns),
        "municipalities": muns,
        "_qa": {"problems": problems,
                "gap_tally_c": dict(Counter(m.get("gap_classification_c_19") for m in muns)),
                "gap_tally_d": dict(Counter(m.get("gap_classification_d_22") for m in muns)),
                "gap_tally_overall": dict(Counter(m.get("gap_classification") for m in muns))},
    }
    json.dump(out, open("data/18-23-local-routing-gap-v1.json", "w"), ensure_ascii=False, indent=1)
    print(f"municipalities={len(muns)} problems={len(problems)}")
    for p in problems:
        print(" ", p)
    print("gap C:", dict(Counter(m.get("gap_classification_c_19") for m in muns)))
    print("gap D:", dict(Counter(m.get("gap_classification_d_22") for m in muns)))
