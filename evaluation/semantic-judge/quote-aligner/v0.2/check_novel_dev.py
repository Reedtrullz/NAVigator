"""Run the development-only novel set; prints per-category results."""
import json
import os

import run_v02_benchmarks as R

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "novel-development-set.json"),
              encoding="utf-8") as f:
        data = json.load(f)
    assert data["meta"]["status"] == "DEVELOPMENT_ONLY_NEVER_BLIND_CERTIFICATION"
    import polarity_engine_v02 as E
    rows = []
    for c in data["claims"]:
        res = E.judge_claim(c["claim"], c["source"]["text"])
        rows.append({"id": c["id"], "expected": c["expected"],
                     "dimension": c["dimension"],
                     "verdict": res["verdict"],
                     "ok": res["verdict"] == c["expected"]})
    by_cat = {}
    for r in rows:
        d = by_cat.setdefault(r["dimension"], {"n": 0, "ok": 0, "miss": []})
        d["n"] += 1
        if r["ok"]:
            d["ok"] += 1
        else:
            d["miss"].append("%s: exp=%s got=%s" % (
                r["id"], r["expected"], r["verdict"]))
    total_ok = sum(r["ok"] for r in rows)
    print("NOVEL-40: %d/%d correct" % (total_ok, len(rows)))
    for cat, d in sorted(by_cat.items()):
        print("  %-10s %d/%d %s" % (cat, d["ok"], d["n"],
                                    "; ".join(d["miss"]) or ""))
    with open(os.path.join(HERE, "results", "qa06-novel-dev.json"),
              "w", encoding="utf-8") as f:
        json.dump({"meta": data["meta"], "results": rows}, f,
                  ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
