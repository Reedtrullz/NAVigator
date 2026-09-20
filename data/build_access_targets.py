import json

src = json.load(open("data/18-23-local-routing-gap-v1.json"))
targets = []
n = 0
for m in src["municipalities"]:
    for s in m["services_18_23"]:
        if s.get("pub_info", {}).get("access_clear") != "no":
            continue
        n += 1
        targets.append({
            "target_id": f"T{n}",
            "kommune": m["kommune"],
            "kommunenummer": m["kommunenummer"],
            "ssb_sentralitetsklasse": m["ssb_sentralitetsklasse"],
            "service_name": s["service_name"],
            "service_category": s.get("service_category", "unknown"),
            "existing_source_url": s.get("source_url"),
            "target_age_text": s.get("target_age_text"),
            "covers_age_19": s.get("covers_age_19"),
            "covers_age_22": s.get("covers_age_22"),
            "existing_access_fields": {
                "direct_access": s.get("direct_access"),
                "pub_info_access_clear": s.get("pub_info", {}).get("access_clear"),
                "pub_info_contact_clear": s.get("pub_info", {}).get("contact_clear"),
            },
            "why_access_unclear": s.get("notes", ""),
            "existing_evidence_quote": s.get("evidence_quote", ""),
            "source_provenance": {
                "source_file": "data/18-23-local-routing-gap-v1.json",
                "retrieved_date": "2026-09-08",
            },
        })

out = {
    "task_id": "NAV-EXPLORE-LOCAL-ACCESS-DISCOVERY-PROTOCOL-V1",
    "frozen_before_research": True,
    "frozen_at": "2026-09-08",
    "target_count": len(targets),
    "targets": targets,
}
json.dump(out, open("data/access-unclear-targets-v1.json", "w"), ensure_ascii=False, indent=2)
print("frozen targets:", len(targets))
