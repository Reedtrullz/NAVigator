#!/usr/bin/env python3
"""Write-sandbox probe (spec 3, 37): historical writes must fail."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from write_guard import WriteGuardError, open_w, write_text

SEM = HERE.parent.parent
HISTORICAL = [
    SEM / "rc3-3-1-residual-contradiction" / "WRITE-PROBE-ILLEGAL.txt",
    SEM / "rc3-generalization-holdout" / "WRITE-PROBE-ILLEGAL.txt",
    SEM / "rc3-1-proof-semantics" / "corpus" / "WRITE-PROBE-ILLEGAL.txt",
    SEM / "rc3-development" / "WRITE-PROBE-ILLEGAL.txt",
]


def main():
    results = []
    for p in HISTORICAL:
        blocked = False
        try:
            open_w(p, "w").close()
        except WriteGuardError:
            blocked = True
        results.append({
            "path": str(p),
            "blocked": blocked,
            "file_exists_after": p.exists(),
        })
    probe = HERE / "sandbox-probe-ok.txt"
    write_text(probe, "ok\n")
    sandbox_ok = probe.exists() and probe.read_text() == "ok\n"
    probe.unlink()
    ok = all(r["blocked"] and not r["file_exists_after"]
             for r in results) and sandbox_ok
    write_text(HERE / "write-guard-results.json",
               json.dumps({"tests": results,
                           "sandbox_write_ok": sandbox_ok,
                           "pass": ok}, indent=1) + "\n")
    print("WRITE_GUARD_PASS" if ok else "WRITE_GUARD_FAIL")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
