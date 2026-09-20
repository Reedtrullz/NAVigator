"""Build oracle-proof-ledger.json from cases_data.json (audit data).

Category rules follow probe spec sections 3-9. Every premise span id is
verified against the frozen packets. Case rows live in JSON so testcase
ids stay out of Python files (id_guard contract).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

PROBE_CATEGORIES = {"DIRECTLY_PROVABLE",
                    "PROVABLE_WITH_BOUNDED_INFERENCE",
                    "REVIEWER_REASONING_FAILURE"}


def main():
    cases = json.load(open(os.path.join(HERE, "cases_data.json"),
                           encoding="utf-8"))
    packets = {r["id"]: r for r in json.load(
        open(os.path.join(HERE, "oracle-packets.json"), encoding="utf-8"))}
    results = {r["id"]: r for r in json.load(
        open(os.path.join(HERE,
            "../packet-redesign/results/oracle-packet-results.json"),
            encoding="utf-8"))["rows"]}

    ledger = {"schema": "oracle-proof-ledger-v1",
              "frozen_baseline":
                  "../packet-redesign/results/oracle-packet-results.json",
              "cases": []}
    errors = []
    seen = set()
    for c in cases:
        cid = c["case_id"]
        c["in_probe_set"] = cid != "ENT-D"
        if cid in seen:
            errors.append(cid + ": duplicate")
        seen.add(cid)
        if cid == "ENT-D":
            hybrid = json.load(open(
                os.path.join(HERE, "../results/hybrid-eval.json"),
                encoding="utf-8"))
            rows = hybrid.get("rows") or hybrid.get("results") or hybrid
            items = rows.values() if isinstance(rows, dict) else rows
            entd = [r for r in items
                    if isinstance(r, dict) and r.get("id") == "ENT-D"][0]
            c["oracle_result"] = entd["final"]
            c["correct"] = entd["final"] == c["expected"]
            c["oracle_provenance"] = "../results/hybrid-eval.json"
        else:
            res = results.get(cid)
            if res is None:
                errors.append(cid + ": missing oracle result")
                continue
            if (res["expected"] != c["expected"]
                    or res["oracle_verdict"] != c["oracle_result"]):
                errors.append(cid + ": expected/oracle mismatch")
            c["oracle_result"] = res["oracle_verdict"]
            c["correct"] = res["correct"]
            spans = {s["span_id"]
                     for s in packets[cid]["packet"]["candidate_spans"]}
            for prem in c["premises"]:
                if prem["span_id"] not in spans:
                    errors.append(cid + ": premise "
                                  + prem["span_id"] + " not in packet")
        ledger["cases"].append(c)

    for r in results:
        if r not in seen:
            errors.append(r + ": in baseline but missing from ledger")

    counts = {}
    for c in ledger["cases"]:
        counts[c["category"]] = counts.get(c["category"], 0) + 1
    ledger["category_counts"] = counts
    ledger["probe_set"] = [c["case_id"] for c in ledger["cases"]
                           if c.get("in_probe_set")
                           and c["category"] in PROBE_CATEGORIES]
    out = os.path.join(HERE, "oracle-proof-ledger.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=1)
    print("categories:", json.dumps(counts, ensure_ascii=False))
    print("probe set:", len(ledger["probe_set"]))
    print("errors:", errors or "none")


if __name__ == "__main__":
    main()
