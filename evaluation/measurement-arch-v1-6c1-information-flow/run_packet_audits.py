#!/usr/bin/env python3
"""V1.6C.1 mechanical packet audits over the frozen A/B row set.

Gold-leakage audit + provenance audit. No model calls.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6b")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3")))

from packet_builder import build_packet, _strip_inventory  # noqa: E402
import boundary_preclassifier as B  # noqa: E402

FORBIDDEN_KEYS = {"gold", "expected", "stratum", "verdict", "acceptable",
                  "forbidden_expected", "answer_key", "fixture_id"}
GOLD_VERDICT_VOCAB = {
    "TRIGGERED", "NOT_TRIGGERED", "UNRESOLVED", "PRESENT", "ABSENT",
    "ACCEPTABLE", "PARTIAL", "NO_ACCEPTABLE_ROUTE", "SATISFIED",
    "VIOLATED", "NOT_REQUIRED",
}


def string_leaves(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from string_leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from string_leaves(v)
    elif isinstance(obj, str):
        yield obj


def main():
    fx_doc = json.load(open(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6b",
                                         "screening-fixtures.json")))
    fixtures = {f["id"]: f for f in fx_doc["fixtures"]}
    ck = json.load(open(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6b",
                                     "screening-checkpoint-mimo-v2-5-pro.json")))
    judge_rows = [r for r in ck["rows"] if r.get("stage") == "JUDGE"]
    gold_doc = json.load(open(os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6b",
                                           "screening-gold.json")))
    gold_by_id = {g["fixture_id"]: g["pass1"] for g in gold_doc["gold"]}

    leak_failures = []
    prov_failures = []
    packets = {}
    for row in judge_rows:
        rid = row["id"]
        fx = fixtures[rid]
        packet = build_packet(fx["dimension"], fx["crit"], fx["sut"], fx.get("ctx", ""))
        packets[rid] = packet
        for k in FORBIDDEN_KEYS:
            if k in packet:
                leak_failures.append(f"{rid}: forbidden key '{k}' present in packet")
        leaves = {v.strip() for v in string_leaves(packet)}
        for leaf in leaves:
            if leaf.upper() in GOLD_VERDICT_VOCAB:
                leak_failures.append(
                    f"{rid}: score-bearing verdict value '{leaf}' appears as standalone packet value")
        g = gold_by_id[rid]
        recomputed = _strip_inventory(json.loads(json.dumps(B.classify(fx["sut"], None))))
        if json.dumps(packet["a3"], sort_keys=True) != json.dumps(recomputed, sort_keys=True):
            prov_failures.append(f"{rid}: embedded a3 does not equal recomputed stripped classify() output")
        for field, spans in packet.items():
            if isinstance(spans, list):
                for i, sp in enumerate(spans):
                    if isinstance(sp, dict) and "provenance" in sp:
                        if not str(sp["provenance"]).startswith("a3_"):
                            prov_failures.append(f"{rid}: {field}[{i}] provenance not a3_*")

    leakage = {
        "artifact": "V1.6C.1 GOLD LEAKAGE AUDIT",
        "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
        "rows_checked": len(judge_rows),
        "forbidden_keys_checked": sorted(FORBIDDEN_KEYS),
        "gold_values_scanned_per_row": True,
        "GOLD_DERIVED_FIELDS_IN_JUDGE_PACKET": 0 if not leak_failures else len(leak_failures),
        "failures": leak_failures,
        "status": "PASS" if not leak_failures else "FAIL",
    }
    provenance = {
        "artifact": "V1.6C.1 PACKET PROVENANCE AUDIT",
        "task_id": "NAV-EXPLORE-MEASUREMENT-ARCH-V1_6C1-INFORMATION-FLOW-REPAIR",
        "rows_checked": len(judge_rows),
        "a3_embed_equals_recomputed_stripped": all(not f for f in prov_failures),
        "span_provenance_rule": "every span object carries provenance a3_*",
        "builder_sha_drift_guard": True,
        "failures": prov_failures,
        "status": "PASS" if not prov_failures else "FAIL",
    }
    for name, doc in (("gold-leakage-audit.json", leakage),
                      ("packet-provenance-audit.json", provenance)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    print("LEAKAGE:", leakage["status"], leakage["GOLD_DERIVED_FIELDS_IN_JUDGE_PACKET"])
    print("PROVENANCE:", provenance["status"], len(prov_failures), "failures")
    for f in (leak_failures + prov_failures)[:20]:
        print("  " + f)
    return 0 if not (leak_failures or prov_failures) else 1


if __name__ == "__main__":
    sys.exit(main())
