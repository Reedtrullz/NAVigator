"""Oracle packet experiment (spec 17, diagnostic only).

For every review-layer error from Iteration B: build the automatic v2
packet, then prune it to a rule-based oracle selection for the EXPECTED
verdict. Runs the frozen v1.1 reviewer semantics on the oracle packet.
No oracle mapping is used at runtime (spec 18); this file only measures
packet-routing vs reviewer-reasoning ceiling.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HY = os.path.dirname(HERE)
JUDGE_DIR = os.path.join(os.path.dirname(HY), "quote-aligner", "v0.2")
SEM_DIR = os.path.dirname(HY)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR), HY, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from packet_router import build_v2_packet  # noqa: E402
from reviewer_v2 import (call_luna_v2, fusion_v2,  # noqa: E402
                         classify_threshold, prompt_meta)

SETS = [
    ("minimal-pairs", os.path.join(BENCH_DIR, "minimal-pairs.json")),
    ("minimal-pairs-supplement", os.path.join(BENCH_DIR, "minimal-pairs-supplement.json")),
    ("contra-insuff", os.path.join(BENCH_DIR, "contra-insuff.json")),
    ("modality", os.path.join(BENCH_DIR, "modality.json")),
    ("actor-scope", os.path.join(BENCH_DIR, "actor-scope.json")),
    ("locality", os.path.join(BENCH_DIR, "locality.json")),
    ("diagnostic-20", os.path.join(BENCH_DIR, "diagnostic-20.json")),
    ("novel-40", os.path.join(JUDGE_DIR, "novel-development-set.json")),
    ("ent", os.path.join(SEM_DIR, "ent-controls-set.json")),
    ("calibration", os.path.join(SEM_DIR, "calibration-set.json")),
    ("holdout-v2-burned", os.path.join(SEM_DIR, "holdout-set.json")),
]
NORM = {"INSUFFICIENT_EVIDENCE": "INSUFFICIENT",
        "PARTIALLY_SUPPORTED": "PARTIAL"}


def _is_s0(sid, spans, source_text):
    import sys as _s
    from packet_router import _canon
    return _canon(spans[sid]["text"]) == _canon(source_text)


def oracle_prune(pkt, expected, source_text):
    """Keep the rule-selected minimum packet for the expected verdict."""
    spans = {s["span_id"]: s for s in pkt["candidate_spans"]}
    keep = set()
    for a in pkt["atoms"]:
        cands = a["candidate_evidence"]
        if not cands:
            continue
        if expected == "SUPPORTED":
            # top-3 non-qualifier evidence per atom + joint set + context
            nonq = [c for c in cands if c["relation"] != "qualifier"]
            for c in (nonq[:3] or cands[:3]):
                keep.add(c["span_id"])
            keep.update(a.get("evidence_set") or [])
            q = [c for c in cands if c["relation"] == "qualifier"]
            if q:
                keep.add(q[0]["span_id"])
        elif expected == "INSUFFICIENT":
            # neutral candidate surface, full-source span removed
            keep.update(c["span_id"] for c in cands
                        if c["span_id"] in spans
                        and not _is_s0(c["span_id"], spans, source_text))
        else:
            # CONTRADICTED / PARTIAL: full evidence surface incl. S0
            keep.update(c["span_id"] for c in cands)
            keep.update(a.get("evidence_set") or [])
    if not keep and pkt["candidate_spans"]:
        keep = {pkt["candidate_spans"][0]["span_id"]}
    pkt["candidate_spans"] = [s for s in pkt["candidate_spans"]
                              if s["span_id"] in keep]
    kept = keep
    for a in pkt["atoms"]:
        a["candidate_evidence"] = [e for e in a["candidate_evidence"]
                                   if e["span_id"] in kept]
        if a.get("evidence_set"):
            a["evidence_set"] = [s for s in a["evidence_set"] if s in kept]
    return pkt


def main():
    claims = {}
    for name, path in SETS:
        data = json.load(open(path, encoding="utf-8"))
        for c in data.get("claims", data if isinstance(data, list) else []):
            claims[(name, c["id"])] = c
    errors = json.load(open(os.path.join(HERE, "audit-data.json"),
                            encoding="utf-8"))
    rows = []
    correct = 0
    for e in errors:
        key = (e["set"], e["id"])
        c = claims[key]
        src = c["source"]["text"]
        expected = NORM.get(e["expected"], e["expected"])
        pkt = build_v2_packet(c["claim"], src, {"atom_results": [
            {"atom_id": "A1", "atom_text": c["claim"],
             "verdict": "INSUFFICIENT_EVIDENCE"}]},
            "oracle", s0_mode="include", max_spans=6)
        pkt = oracle_prune(pkt, expected, src)
        out = call_luna_v2(pkt)
        final, route, atoms = fusion_v2(pkt, out, classify_threshold(c["claim"]))
        final = NORM.get(final, final)
        ok = final == expected
        correct += ok
        rows.append({"id": e["id"], "set": e["set"], "expected": expected,
                     "oracle_verdict": final, "route": route,
                     "correct": ok, "n_spans": len(pkt["candidate_spans"]),
                     "reviewer_output": out})
        print("%-10s exp=%-13s oracle=%-13s %s (%d spans)" % (
            e["id"], expected, final, "OK" if ok else "MISS",
            len(pkt["candidate_spans"])))
    out_doc = {"meta": {"stage": "oracle-packet-diagnostic",
                        "n_claims": len(rows), "n_correct": correct,
                        "oracle_accuracy": round(correct / len(rows), 4)
                        if rows else None,
                        "prompt_meta": prompt_meta()},
               "rows": rows}
    with open(os.path.join(HERE, "results", "oracle-packet-results.json"),
              "w", encoding="utf-8") as f:
        json.dump(out_doc, f, ensure_ascii=False, indent=1)
    print("ORACLE acc=%s (%d/%d)" % (
        out_doc["meta"]["oracle_accuracy"], correct, len(rows)))


if __name__ == "__main__":
    main()
