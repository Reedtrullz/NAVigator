"""Rebuild iteration-B packets for every review-layer error."""
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
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
from reviewer import build_packet  # noqa: E402
from quote_aligner import content_tokens  # noqa: E402

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
NOTD = {"REVIEW_REQUIRED", "NO_EVIDENCE", "AMBIGUOUS"}


def cov(span_text, atom_text):
    a = set(content_tokens(atom_text))
    if not a:
        return 1.0
    s = set(content_tokens(span_text))
    return len(a & s) / len(a)


def main():
    claims = {}
    for name, path in SETS:
        data = json.load(open(path, encoding="utf-8"))
        for c in data.get("claims", data if isinstance(data, list) else []):
            claims[(name, c["id"])] = c
    rows = json.load(open(os.path.join(HY, "results", "hybrid-eval.json"),
                          encoding="utf-8"))["rows"]
    errs = [r for r in rows if r["final"] not in NOTD
            and NORM.get(r["expected"], r["expected"])
            != NORM.get(r["final"], r["final"])]
    out = []
    for r in errs:
        c = claims[(r["set"], r["id"])]
        src = c["source"]["text"]
        res = E.judge_claim(c["claim"], src)
        reason = auto_gate(r["id"], src, res)
        pkt = build_packet(c["claim"], src, res, reason or "audit")
        ro = r.get("reviewer_output") or {}
        used = (ro.get("support_span_ids") or []) + (ro.get("contradiction_span_ids") or [])
        atoms = pkt["claim_atoms"]
        spans = {s["id"]: s["text"] for s in pkt["candidate_spans"]}
        atom_stats = []
        for at in atoms:
            single = sorted(((sid, round(cov(t, at), 2))
                             for sid, t in spans.items()),
                            key=lambda x: -x[1])
            used_union = set()
            for sid in used:
                used_union |= set(content_tokens(spans.get(sid, "")))
            a_tok = set(content_tokens(at))
            ucover = round(len(a_tok & used_union) / len(a_tok), 2) if a_tok else 1.0
            atom_stats.append({"atom": at[:110], "best_single": single[:3],
                               "used_union_coverage": ucover})
        out.append({
            "id": r["id"], "set": r["set"],
            "expected": r["expected"], "actual": r["final"],
            "confidence": ro.get("confidence"),
            "used_spans": used,
            "ignored_spans": [s for s in spans if s not in used],
            "s0_in_packet": "S0" in spans,
            "s0_used": "S0" in used,
            "n_spans": len(spans),
            "span_texts": {k: v[:140] for k, v in spans.items()},
            "claim": c["claim"], "source_excerpt": src[:220],
            "atoms": atom_stats})
    json.dump(out, open(os.path.join(HERE, "audit-data.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
    print("audit-data.json:", len(out), "error cases")
    for e in out:
        dist = any(a["best_single"][0][1] < 0.6 and a["used_union_coverage"] >= 0.7
                   for a in e["atoms"]) if e["used_spans"] else False
        print("%-10s %-20s %s->%s used=%-8s s0used=%-5s dist=%s" % (
            e["id"], e["set"][:20],
            NORM.get(e["expected"], e["expected"])[:4], e["actual"][:4],
            ",".join(e["used_spans"]) or "-", e["s0_used"], dist))


if __name__ == "__main__":
    main()
