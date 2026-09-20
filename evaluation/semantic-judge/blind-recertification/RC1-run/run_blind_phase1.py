#!/usr/bin/env python3
"""PHASE 1 blind prediction driver for NAV-EXPLORE-EVALUATOR-RC1.

Calls the exact frozen RC1 pipeline in the same import configuration as
hybrid/run_hybrid_eval.py: polarity_engine_v02.judge_claim ->
auto_gate -> reviewer.review_claim.  Deterministic only until a case
routes to semantic review (openai/gpt-5.6-luna via local OpenCodex
proxy).  No scoring, no retries beyond RC1's own, no label access.

Input normalization (documented, not a runtime change): blind cases
with >1 source have their source texts joined with a blank line into
the single source string the frozen engine interface accepts; the
reviewer evidence packet is built from that same joined string.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                         "quote-aligner", "v0.2")
HYBRID_DIR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "hybrid")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR),
          HYBRID_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
import polarity_engine_v02 as E  # noqa: E402
from auto_gate import auto_gate  # noqa: E402
from reviewer import review_claim  # noqa: E402

RC1_SET = os.path.join(os.path.dirname(HERE), "RC1-set")

VERDICT_MAP = {
    "SUPPORTED": "SUPPORTED",
    "CONTRADICTED": "CONTRADICTED",
    "PARTIAL": "PARTIALLY_SUPPORTED",
    "INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
}


def engine_semantic(v):
    return VERDICT_MAP.get(v, "REVIEW_REQUIRED")


def proof_safe(engine_verdict, gate_reason, route):
    """Proof-safety classification from RC1's own fusion decision.

    AUTO fusion routes are considered proven; anything routed to or
    held for review is not proven and maps to INSUFFICIENT_EVIDENCE.
    """
    if route == "accepted":
        return VERDICT_MAP.get(engine_verdict, "REVIEW_REQUIRED")
    return "INSUFFICIENT_EVIDENCE"


def main():
    blind = json.load(open(os.path.join(RC1_SET, "blind-cases.json"),
                           encoding="utf-8"))
    core = blind["core"]
    assert len(core) == 120
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rows = []
    n_calls = 0
    runtime_failures = 0
    for c in core:
        src = "\n\n".join(s["text"] for s in c["sources"])
        row = {"case_id": c["case_id"], "runtime_status": "OK"}
        try:
            res = E.judge_claim(c["claim"], src)
            reason = auto_gate(c["case_id"], src, res)
            engine_sem = engine_semantic(res["verdict"])
            if reason is None:
                final, route = engine_sem, "accepted"
                rv = None
            else:
                rv = review_claim(c["claim"], src, res, reason)
                n_calls += 1
                rverdict = rv["final_verdict"]
                if rverdict in VERDICT_MAP:
                    final, route = VERDICT_MAP[rverdict], rv["route"]
                else:
                    final, route = "REVIEW_REQUIRED", rv["route"]
            pa = ("AUTO_SUPPORTED" if final == "SUPPORTED"
                  else "AUTO_CONTRADICTED" if final == "CONTRADICTED"
                  else "REVIEW_REQUIRED" if final == "PARTIALLY_SUPPORTED"
                  else "ABSTAIN_INSUFFICIENT")
            row.update({
                "semantic_verdict": final,
                "engine_verdict": res["verdict"],
                "engine_semantic_verdict": engine_sem,
                "proof_safe_verdict": proof_safe(res["verdict"], reason, route),
                "product_action": pa,
                "auto_or_review": "AUTO" if reason is None else "REVIEW",
                "gate_reason": reason,
                "proof_object": {"engine": res, "route": route},
                "proof_valid": reason is None,
                "reviewer_used": rv is not None,
                "reviewer_output": (rv or {}).get("reviewer_output"),
                "reviewer_route": (rv or {}).get("route"),
                "confidence": res.get("confidence"),
                "operator": None,
            })
        except Exception as exc:  # recorded, never reconstructed
            runtime_failures += 1
            row.update({"runtime_status": "RUNTIME_FAILURE",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc)[:300]})
        rows.append(row)
        done = sum(1 for r in rows)
        if done % 20 == 0:
            print("progress %d/120 (reviewer_calls=%d failures=%d)"
                  % (done, n_calls, runtime_failures), flush=True)
    artifact = {
        "meta": {
            "release_candidate": "NAV-EXPLORE-EVALUATOR-RC1",
            "blind_set": "NAV-EXPLORE-RC1-BLIND-V1",
            "phase": "PREDICTION_BEFORE_KEY",
            "driver": "run_blind_phase1.py (deterministic input adapter; "
                      "frozen RC1 pipeline functions unmodified)",
            "started_at": started,
            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "prediction_count": len(rows),
            "reviewer_model": "openai/gpt-5.6-luna",
        },
        "runtime_metrics": {
            "deterministic_only": sum(1 for r in rows
                                      if not r.get("reviewer_used")),
            "reviewer_used": sum(1 for r in rows if r.get("reviewer_used")),
            "total_model_calls": n_calls,
            "retry_count": 0,
            "runtime_failures": runtime_failures,
            "elapsed_s": round(time.time() - time.mktime(time.strptime(
                started[:19], "%Y-%m-%dT%H:%M:%S")), 1),
        },
        "predictions": rows,
    }
    out = os.path.join(HERE, "RC1-predictions.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("WROTE %s rows=%d calls=%d failures=%d"
          % (out, len(rows), n_calls, runtime_failures))


if __name__ == "__main__":
    main()
