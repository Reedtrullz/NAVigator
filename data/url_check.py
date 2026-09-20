#!/usr/bin/env python3
import json
import subprocess
import concurrent.futures

d = json.load(open("data/municipal-mental-health-sample-v1.json"))
urls = set()
for m in d["municipalities"]:
    for s in m["services"]:
        if s.get("source_url"):
            urls.add(s["source_url"])
    for blk in ("rph", "psychologist"):
        u = m.get(blk, {}).get("source_url")
        if u:
            urls.add(u)
urls = sorted(urls)

def check(u):
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-L",
             "--max-time", "30", "-A", "Mozilla/5.0", u],
            capture_output=True, text=True, timeout=35)
        return u, out.stdout.strip() or "000"
    except Exception:
        return u, "000"

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for u, code in ex.map(check, urls):
        results[u] = code

bad = {u: c for u, c in results.items() if c != "200"}
print(f"total={len(urls)} ok={len(results)-len(bad)} bad={len(bad)}")
for u, c in sorted(bad.items()):
    owners = []
    for m in d["municipalities"]:
        for s in m["services"]:
            if s.get("source_url") == u:
                owners.append(f"{m['kommune']} / service {s.get('service_name')}")
        for blk in ("rph", "psychologist"):
            if m.get(blk, {}).get("source_url") == u:
                owners.append(f"{m['kommune']} / {blk}")
    print(f"{c}  {u}")
    for o in owners:
        print(f"    -> {o}")
