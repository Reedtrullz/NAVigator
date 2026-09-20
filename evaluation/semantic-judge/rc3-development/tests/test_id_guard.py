"""ID guard (spec 43): no burned case IDs or literal expected-label
maps in runtime code. Docs may reference; runtime must not."""
import re
from pathlib import Path

RUNTIME_DIRS = ["rc3_engine"]
BANNED = re.compile(r"RC1B-|RC2B-|RC2B_")

RUNTIME_DIRS = [str(Path(__file__).resolve().parent.parent / d)
                for d in RUNTIME_DIRS]


def test_no_banned_ids_in_runtime():
    hits = []
    for d in RUNTIME_DIRS:
        for f in Path(d).rglob("*.py"):
            for i, line in enumerate(f.read_text().splitlines(), 1):
                if BANNED.search(line):
                    hits.append("%s:%d" % (f.name, i))
    assert not hits, "banned IDs in runtime: %s" % hits


if __name__ == "__main__":
    test_no_banned_ids_in_runtime()
    print("id_guard: 0 runtime hits PASS")

