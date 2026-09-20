"""Batched reviewer-proposal cache builder.

Runs a few live reviewer calls per invocation (proxy latency ~4s each)
and appends proposals to /tmp/rc3_review_cache.json so the full
development evaluation can be replayed synchronously and offline.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "rc3_engine"))
import engine_rc3 as eng  # noqa: E402
import reviewer_bridge as rb  # noqa: E402

CACHE = Path("/tmp/rc3_review_cache.json")
BUDGET_S = 20.0


def main():
    dev = json.load(open(HERE.parent / "hybrid" / "development-set.json"))
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    pending = []
    for case in dev["cases"]:
        if case["id"] in cache:
            continue
        atom = eng.judge_atom(case["claim"], case["source"])
        if True:  # reviewer proposal on every case (R1 confirm/
            # downgrade authority applies to accepted proofs too)
            pending.append(case)
    print("pending:", len(pending), flush=True)
    t0 = time.time()
    done = 0
    for case in pending:
        atom = eng.judge_atom(case["claim"], case["source"])
        proposal = rb.review_atom(case["claim"], case["source"], atom)
        cache[case["id"]] = proposal
        done += 1
        if time.time() - t0 > BUDGET_S:
            break
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    print("reviewed this run:", done, "| cache size:", len(cache))


if __name__ == "__main__":
    main()
