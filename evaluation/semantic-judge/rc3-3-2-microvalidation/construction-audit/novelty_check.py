#!/usr/bin/env python3
"""Mechanical novelty check (spec 18) via RC3G construction_tools.

Firewall: only per-claim rejection metadata crosses back.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(HERE))
import write_guard  # noqa: E402

RC3G_TOOLS = Path("/Users/reidar/Projectos/NAV Explore/evaluation/"
                  "semantic-judge/rc3-generalization-holdout/"
                  "construction_tools.py")


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rc3g_tools", RC3G_TOOLS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pub = json.loads((TASK / "microvalidation-cases.json").read_text(
        encoding="utf-8"))
    claims = [(c["case_id"], c["claim"]) for c in pub["cases"]]
    report = mod.check_novelty(claims)
    rejects = [r for r in report if r["verdict"] != "OK"]
    max_sim = max(r["max_similarity"] for r in report)
    result = {
        "tool": "rc3-generalization-holdout/construction_tools.check_novelty",
        "n_claims": len(report),
        "max_similarity": max_sim,
        "rejects": rejects,
        "novelty_pass": not rejects,
    }
    write_guard.write_text(
        HERE / "novelty.json",
        json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print("NOVELTY_" + ("PASS" if not rejects else "FAIL"),
          f"max_similarity={max_sim} rejects={len(rejects)}")


if __name__ == "__main__":
    main()
