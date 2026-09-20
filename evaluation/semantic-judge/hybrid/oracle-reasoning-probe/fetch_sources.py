"""Extract full source texts for the 45 oracle-error cases from frozen set files."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HY = os.path.dirname(HERE)
SEM_DIR = os.path.dirname(HY)
BENCH_DIR = os.path.join(SEM_DIR, "v0.4.1", "benchmarks")
JUDGE_DIR = os.path.join(SEM_DIR, "quote-aligner", "v0.2")

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


def main():
    claims = {}
    for name, path in SETS:
        data = json.load(open(path, encoding="utf-8"))
        for c in data.get("claims", data if isinstance(data, list) else []):
            claims[(name, c["id"])] = c
    packets = json.load(open(os.path.join(HERE, "oracle-packets.json"),
                             encoding="utf-8"))
    out_dir = os.path.join(HERE, "sources")
    os.makedirs(out_dir, exist_ok=True)
    for p in packets:
        c = claims[(p["set"], p["id"])]
        rec = {
            "set": p["set"], "id": p["id"],
            "expected": p["expected"],
            "claim": c["claim"],
            "source_text": c["source"]["text"],
            "spans": {s["span_id"]: s["text"]
                      for s in p["packet"]["candidate_spans"]},
        }
        fn = os.path.join(out_dir, "%s__%s.json" % (p["set"], p["id"]))
        json.dump(rec, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", len(packets), "source records")


if __name__ == "__main__":
    main()
