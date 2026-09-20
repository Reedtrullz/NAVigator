#!/usr/bin/env python3
"""V1.6A.4 TDD runner. --baseline runs the frozen A3 engine (expected RED
on the new forbidden_claim dimension); --candidate runs the A4 engine."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A3_DIR = os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-6a3")
sys.path.insert(0, A3_DIR)


def run(engine_mod, tag):
    fixtures = json.load(open(os.path.join(HERE, "tdd-fixtures.json")))["fixtures"]
    rows, fails = [], []
    for f in fixtures:
        got = engine_mod.classify(f["text"], f.get("criterion"))
        for dim, e in f["expected"].items():
            g = got.get(dim)
            ok = (g is not None
                  and g.get("label") == e["label"]
                  and bool(g.get("abstained")) == bool(e["abstained"]))
            rows.append({"id": f["id"], "dim": dim, "expected": e["label"],
                         "got": (g or {}).get("label"), "ok": ok})
            if not ok:
                fails.append(rows[-1])
    print("[%s] total=%d pass=%d fail=%d" % (tag, len(rows),
                                             len(rows) - len(fails), len(fails)))
    for x in fails:
        print(" FAIL", x["id"], x["dim"], "expected", x["expected"],
              "got", x["got"])
    return len(fails)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--baseline"
    if mode == "--baseline":
        import boundary_preclassifier as eng
        n = run(eng, "A3-baseline")
        print("RED_EXPECTED" if n > 0 else "UNEXPECTED_GREEN_BASELINE")
    else:
        import a4_boundary_preclassifier as eng
        n = run(eng, "A4-candidate")
        print("GREEN" if n == 0 else "STILL_RED")
        sys.exit(1 if n else 0)

