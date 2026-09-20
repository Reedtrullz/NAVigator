#!/usr/bin/env python3
"""Spec section 34 control: no testcase ids in evaluator code/config.

Testcase ids are allowed ONLY in benchmark/set data files (JSON). This
guard scans every python file in the v0.4 directory (excluding itself)
and fails if an id pattern appears in code.
"""
import os
import re
import sys

PATTERN = re.compile(r"\b(?:HV2|CAL|DEC|HOL|CMP|ENT|MP|CI|MOD|ACT|LOC)[- ]?\d{2,4}\b")
SELF = os.path.basename(os.path.abspath(__file__))


def scan(root):
    hits = []
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if not name.endswith(".py") or name == SELF:
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if PATTERN.search(line):
                        hits.append({"file": os.path.relpath(path, root),
                                     "line": lineno,
                                     "text": line.strip()[:140]})
    return hits


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.abspath(__file__))
    hits = scan(root)
    print("ID GUARD: scanned", root, "-", len(hits), "hits")
    for h in hits:
        print("  HIT:", h)
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
