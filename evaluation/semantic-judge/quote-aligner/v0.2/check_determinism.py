"""5x determinism check over all benchmark sets plus ENT controls."""
import json
import os

import run_v02_benchmarks as R

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = 5


def main():
    verdicts = {}
    for name in R.BENCHES:
        res = R.run_bench(name, runs=RUNS)
        for row in res["results"]:
            key = (name, row["id"])
            verdicts.setdefault(key, set()).add(row.get("verdict"))
    res = R.run_ent()
    rows = res["results"]
    for rep in range(2, RUNS + 1):
        for row in R.run_ent()["results"]:
            verdicts.setdefault(("ent", row["id"]), set()).add(
                row.get("verdict"))
            rows.append({**row, "run": rep})

    unstable = {k: sorted(v) for k, v in verdicts.items() if len(v) > 1}
    out = {
        "meta": {"runs": RUNS, "engine": "quote-aligner-deterministic-v0.2"},
        "identical_across_runs": not unstable,
        "unstable_cases": unstable,
        "n_cases": len(verdicts),
    }
    path = os.path.join(HERE, "results", "qa06-determinism.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
