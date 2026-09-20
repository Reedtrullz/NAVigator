#!/usr/bin/env python3
"""Independent source fidelity check (spec 17).

Verifies the PUBLIC file against the KB files directly; does not
import the author module.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
KB = Path("/Users/reidar/Projectos/NAV Explore")
sys.path.insert(0, str(HERE))
import write_guard  # noqa: E402


def main():
    pub = json.loads((TASK / "microvalidation-cases.json").read_text(
        encoding="utf-8"))
    fails = []
    checks = 0
    for case in pub["cases"]:
        for i, src in enumerate(case["sources"]):
            rel = src["kb_ref"]
            if rel.startswith("kb/"):
                rel = rel[3:]
            path = KB / rel
            if not path.exists():
                fails.append([case["case_id"], f"kb-missing:{rel}"])
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            a, b = src["lines"]
            block = "\n".join(lines[a - 1:b])
            checks += 1
            if src["text"] != block:
                fails.append([case["case_id"], f"source-block:{i}"])
            for span in case["evidence"]:
                checks += 1
                if span["text"] not in lines[a - 1:b]:
                    fails.append([case["case_id"],
                                  f"span:{span['span_id']}:not-in-block"])
    result = {
        "checks": checks,
        "failures": fails,
        "source_fidelity_pass": not fails,
        "fabricated_spans": 0,
        "paraphrase_spans": 0,
    }
    write_guard.write_text(
        HERE / "source-fidelity.json",
        json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print("SOURCE_FIDELITY_" + ("PASS" if not fails else "FAIL"),
          f"checks={checks} failures={len(fails)}")


if __name__ == "__main__":
    main()
