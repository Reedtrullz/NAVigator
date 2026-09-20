#!/usr/bin/env python3
"""Run the frozen 235-row fresh pool through native Jev (System One).

One request per case, V1 questions both lanes, identical to V2 invocation.
Writes raw JSONL incrementally; HTTP 429 stops the batch; no semantic retries.
"""
import hashlib, json, pathlib, sys, time

BASE = pathlib.Path(__file__).resolve().parent
V2 = BASE.parent / "native-jev-qualification-v2"
sys.path.insert(0, str(V2))
from jev_client import system_one
from question_schema import critical_questions, forbidden_questions

manifest = json.loads((BASE / "fresh-case-manifest.json").read_text())

corpus_path = BASE.parent / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"
corpus_sha = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
assert corpus_sha == manifest["source_corpus_sha256"], "source corpus SHA mismatch"
context_by_packet = {
    row["packet_id"]: row["packet"]["case_context"]
    for row in (json.loads(l) for l in corpus_path.read_text().splitlines() if l.strip())
}

out_name = sys.argv[1] if len(sys.argv) > 1 else "raw-responses-run1.jsonl"
out_path = BASE / out_name
assert not out_path.exists(), f"refusing to overwrite existing raw output: {out_name}"

def build_state(row):
    return {
        "criterion": row["criterion"],
        "case_context": context_by_packet[row["packet_id"]],
        "sut_output": row["state_sut_for_jev"],
    }

def questions_for(row):
    return critical_questions() if row["lane"] == "critical_condition" else forbidden_questions()

def main():
    results, n = [], 0
    total = len(manifest["cases"])
    for row in manifest["cases"]:
        data, latency = system_one(build_state(row), questions_for(row))
        rec = {
            "case_id": row["case_id"],
            "packet_id": row["packet_id"],
            "lane": row["lane"],
            "expected": row["expected"],
            "model": data.get("model"),
            "latency_seconds": round(latency, 3),
            "usage": data.get("usage"),
            "answers": data.get("answers"),
            "error": None if "http_error" not in data and "transport_error" not in data
                     else {k: data[k] for k in ("http_error", "transport_error", "error_body") if k in data},
        }
        results.append(rec)
        n += 1
        tag = "ERR" if rec["error"] else "ok"
        print(f"{n:03d}/{total} {row['case_id']} {row['lane']} {tag} {rec['latency_seconds']}s", flush=True)
        if rec["error"] and rec["error"].get("http_error") == 429:
            out_path.write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in results))
            print("rate limited; stopping batch to honor quota", flush=True)
            return
        out_path.write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in results))
        time.sleep(0.3)
    print(f"wrote {n} records -> {out_path.name}")

if __name__ == "__main__":
    main()
