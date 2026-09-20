#!/usr/bin/env python3
"""Wave-4 quota-resume ASTRA-A/B runner (gpt-6-astra, LOW only).

Imports the frozen Wave-3 review module so prompts, schema validation,
evidence-span checks, and transport-retry policy are byte-identical to the
frozen technique. Transport log and outputs live in THIS resume lineage;
the frozen Wave-3 lineage is never written."""
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "evaluation",
                   "measurement-v3-remeasure-repair-wave-4-quota-safe-v1")
PACKETS = os.path.join(SRC, "quota-resume-semantic-packets.jsonl")

_spec = importlib.util.spec_from_file_location(
    "frozen_astra_review",
    os.path.join(REPO, "evaluation", "measurement-v3-remeasure-repair-wave-3",
                 "run_astra_review.py"))
_review = importlib.util.module_from_spec(_spec)
sys.modules["frozen_astra_review"] = _review
_spec.loader.exec_module(_review)
_review.TRANSPORT_LOG = os.path.join(HERE, "astra-transport-log.jsonl")


def main():
    packets = [json.loads(l) for l in open(PACKETS, encoding="utf-8")
               if l.strip()]
    order = [p["packet_id"] for p in packets]
    by_id = {p["packet_id"]: p for p in packets}
    for p in packets:
        if _review.packet_body_sha(p) != p["packet_sha256"]:
            raise SystemExit("PACKET_BODY_DRIFT " + p["packet_id"])
    done = {}
    for fname in ("astra-pass-a.jsonl", "astra-pass-b.jsonl"):
        path = os.path.join(HERE, fname)
        done[fname] = set()
        if os.path.exists(path):
            done[fname] = {json.loads(l)["packet_id"]
                           for l in open(path, encoding="utf-8") if l.strip()}
    for pid in order:
        p = by_id[pid]
        for fname, pass_name in (("astra-pass-a.jsonl", "ASTRA_A"),
                                 ("astra-pass-b.jsonl", "ASTRA_B")):
            if pid in done[fname]:
                continue
            rec = _review.call_model(pass_name, p)
            with open(os.path.join(HERE, fname), "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(rec["packet_id"], pass_name, rec["status"], flush=True)
            time.sleep(1)
    print("EXECUTION_DONE")


if __name__ == "__main__":
    main()
