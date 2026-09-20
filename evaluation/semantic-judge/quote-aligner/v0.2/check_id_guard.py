"""id_guard: no benchmark IDs or literal benchmark claims in runtime code.
Also flags unusually long lexicon phrases (benchmark-specific entries)."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                         "v0.4.1", "benchmarks")


def norm(s):
    return re.sub(r"[^a-z0-9æøå]+", "", s.lower())


def main():
    ids, claims = set(), set()
    for fn in os.listdir(BENCH_DIR):
        if fn.endswith(".json"):
            with open(os.path.join(BENCH_DIR, fn), encoding="utf-8") as f:
                data = json.load(f)
            for c in data.get("claims", []):
                ids.add(c["id"])
                claims.add(norm(c["claim"]))
    runtime = ["polarity_engine_v02.py", "domain-lexicon.json"]
    hits, long_phrases = [], []
    for fn in runtime:
        with open(os.path.join(HERE, fn), encoding="utf-8") as f:
            text = f.read()
        ntext = norm(text)
        for cid in ids:
            for m in re.finditer(r"%s" % re.escape(cid), text):
                hits.append((fn, cid, m.start()))
        for cl in claims:
            if len(cl) >= 12 and cl in ntext:
                hits.append((fn, "literal-claim", cl[:40]))
    with open(os.path.join(HERE, "domain-lexicon.json"),
              encoding="utf-8") as f:
        lex = json.load(f)

    def walk(node, path):
        if isinstance(node, str):
            if len(node) > 60:
                long_phrases.append((path, node[:70]))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, "%s.%s" % (path, k))

    walk(lex, "lexicon")
    print("id_guard violations:", len(hits))
    for h in hits:
        print("  ", h)
    print("lexicon phrases > 60 chars:", len(long_phrases))
    for p in long_phrases:
        print("  ", p)
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
