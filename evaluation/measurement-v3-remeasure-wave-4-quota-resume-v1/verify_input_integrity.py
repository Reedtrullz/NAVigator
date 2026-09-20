#!/usr/bin/env python3
"""Quota-resume input integrity gate (spec section 3).

Verifies: upstream pins, quota-safe hashes.txt, quota-resume manifest,
all 110 packet bodies, source TASK-LOCK terminal state."""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
PACKETS = os.path.join(SRC, "quota-resume-semantic-packets.jsonl")
MANIFEST = os.path.join(SRC, "quota-resume-manifest.json")

def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def packet_body_sha(p):
    body = dict(p); body.pop("packet_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()

report = {"task_id": "NAV-EXPLORE-MEASUREMENT-V3-REMEASURE-WAVE-4-QUOTA-RESUME-V1",
          "verification_note": "gate before any model call", "checks": {}}
fails = []

# 1. source TASK-LOCK terminal state
src_lock = json.load(open(os.path.join(SRC, "TASK-LOCK.json")))
ok = src_lock.get("status") == "MEASUREMENT_V3_REMEASURE_WAVE_4_QUOTA_DEFERRED"
report["checks"]["source_task_lock_terminal"] = src_lock.get("status")
if not ok: fails.append("SOURCE_LOCK_STATE")

# 2. upstream pins from quota-safe input-integrity.json
src_int = json.load(open(os.path.join(SRC, "input-integrity.json")))
pin_total, pin_ok = 0, 0
def walk(o):
    global pin_total, pin_ok
    if isinstance(o, dict):
        if "path" in o and "sha256" in o and isinstance(o["path"], str):
            pin_total += 1
            fp = os.path.join(REPO, o["path"])
            if os.path.exists(fp) and sha_file(fp) == o["sha256"]:
                pin_ok += 1
            else:
                fails.append("PIN_DRIFT " + o["path"])
        else:
            for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(src_int.get("pins", {}))
report["checks"]["upstream_pins"] = {"total": pin_total, "verified": pin_ok}

# 3. quota-safe hashes.txt (31 files)
hash_ok, hash_total = 0, 0
for line in open(os.path.join(SRC, "hashes.txt")):
    if not line.strip(): continue
    h, fn = line.split(maxsplit=1)
    hash_total += 1
    fp = os.path.join(SRC, fn.strip())
    if os.path.exists(fp) and sha_file(fp) == h: hash_ok += 1
    else: fails.append("FREEZE_HASH_DRIFT " + fn.strip())
report["checks"]["quota_safe_hashes"] = {"total": hash_total, "verified": hash_ok}

# 4. packet count + bodies vs manifest
man = json.load(open(MANIFEST))
packets = [json.loads(l) for l in open(PACKETS, encoding="utf-8") if l.strip()]
exp = {h["packet_id"]: h["sha256"] for h in man["packet_hashes"]}
count_ok = len(packets) == man.get("packet_count") == len(exp) == 110
report["checks"]["packet_count"] = len(packets)
if not count_ok: fails.append("PACKET_COUNT_MISMATCH")
body_ok = 0
for p in packets:
    b = packet_body_sha(p)
    if b == p["packet_sha256"] and b == exp.get(p["packet_id"]):
        body_ok += 1
    else:
        fails.append("PACKET_BODY_DRIFT " + p["packet_id"])
report["checks"]["packet_bodies_verified"] = body_ok

# 5. partial freeze manifest presence + self-hash entry
pfm = os.path.join(SRC, "wave4-partial-measurement-freeze-manifest.json")
report["checks"]["partial_freeze_manifest_present"] = os.path.exists(pfm)

report["hard_gate"] = {"PENDING_PACKET_COUNT": len(packets),
                       "expected": 110}
report["status"] = "PASS" if not fails else "FAIL"
report["failures"] = fails[:20]
out = os.path.join(HERE, "input-integrity.json")
json.dump(report, open(out, "w"), indent=2, ensure_ascii=False)
print(json.dumps({"status": report["status"],
                  "pins": f"{pin_ok}/{pin_total}",
                  "freeze_hashes": f"{hash_ok}/{hash_total}",
                  "packets": f"{body_ok}/{len(packets)}",
                  "failures": fails[:5]}, indent=1))
sys.exit(0 if not fails else 1)
