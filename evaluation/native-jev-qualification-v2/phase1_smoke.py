#!/usr/bin/env python3
"""Phase 1: single connectivity smoke call against native TypeSafe System One."""
import json, pathlib
from jev_client import system_one

OUT = pathlib.Path(__file__).parent / "phase1-smoke-result.json"

state = {
    "reference": "The application may be submitted digitally.",
    "candidate": "The application must always be submitted in person.",
}
questions = {
    "same_core_meaning": {
        "type": "noul",
        "instructions": "Do the reference and the candidate state the same core meaning?",
        "criteria": {
            "true": "Same core obligation or permission is conveyed, allowing minor paraphrase",
            "false": "They differ in a way that changes what a person must or may do",
        },
    },
    "material_contradiction": {
        "type": "noul",
        "instructions": "Does the candidate materially contradict the reference?",
        "criteria": {
            "true": "A person following both texts could not comply with both",
            "false": "Both texts can be true at the same time, or the candidate merely adds detail",
        },
    },
}
data, latency = system_one(state, questions)
record = {
    "phase": 1,
    "purpose": "connectivity_smoke",
    "state": state,
    "questions": questions,
    "latency_seconds": round(latency, 3),
    "response": data,
}
OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
if "http_error" in data or "transport_error" in data:
    print("SMOKE_FAILED", json.dumps({k: data.get(k) for k in ("http_error", "transport_error", "error_body")}, ensure_ascii=False))
else:
    print("SMOKE_OK latency=%.3fs" % latency)
    print(json.dumps(data.get("answers", data), indent=2, ensure_ascii=False)[:1200])
