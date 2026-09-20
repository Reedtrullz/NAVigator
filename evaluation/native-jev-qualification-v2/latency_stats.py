#!/usr/bin/env python3
"""Latency and usage statistics from raw Jev response JSONLs (no API calls)."""
import json, pathlib, statistics

BASE = pathlib.Path(__file__).resolve().parent
out = {}
for name in [f"raw-responses-run{n}{s}.jsonl" for n in (1, 2, 3) for s in ("", "-v2")]:
    rows = [json.loads(l) for l in (BASE / name).read_text().splitlines() if l.strip()]
    lat = [r["latency_seconds"] for r in rows if not r["error"]]
    tin = [r["usage"]["input_tokens"] for r in rows if not r["error"] and r.get("usage")]
    tout = [r["usage"]["output_tokens"] for r in rows if not r["error"] and r.get("usage")]
    out[name] = {
        "n": len(rows),
        "errors": sum(1 for r in rows if r["error"]),
        "median_latency_s": round(statistics.median(lat), 3) if lat else None,
        "p95_latency_s": round(sorted(lat)[int(0.95 * (len(lat) - 1))], 3) if lat else None,
        "mean_latency_s": round(statistics.mean(lat), 3) if lat else None,
        "input_tokens_total": sum(tin),
        "input_tokens_mean": round(statistics.mean(tin), 1) if tin else None,
        "output_tokens_total": sum(tout),
    }
(BASE / "latency-stats.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(out, indent=2, ensure_ascii=False))
