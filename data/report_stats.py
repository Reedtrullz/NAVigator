#!/usr/bin/env python3
import json
from collections import Counter

d = json.load(open("data/municipal-mental-health-sample-v1.json"))
qa = d["_qa"]
print("SENTRALITY COMPARISON:")
print(json.dumps(qa["sentrality_comparison"], ensure_ascii=False, indent=1))
print()
print("AGE TEXTS:")
for m in d["municipalities"]:
    for s in m["services"]:
        t = s.get("target_age_text")
        if t:
            name = m["kommune"][:12]
            svc = s["service_name"][:40]
            print(f"{name:12} | {svc:40} | {t[:90]}")
print()
svcs = [s for m in d["municipalities"] for s in m["services"]]
print("SELF REFERRAL:", Counter(s.get("self_referral") for s in svcs))
print("COST:", Counter(s.get("cost") for s in svcs))
print("CATEGORY:", Counter(s.get("service_category") for s in svcs))
print("CONF:", Counter(s.get("confidence") for s in svcs))
