#!/usr/bin/env python3
"""PHASE 1 blind prediction driver for NAV-EXPLORE-EVALUATOR-RC2.

Executes the exact frozen RC2 composition over the 160 CORE cases of
NAV-EXPLORE-RC2-BLIND-V4 (blind-cases.json is CORE-only, 160 entries;
no reserve IDs are present to execute).

Frozen composition (no code from this file changes any component):
  1. engine   : rc2-development/engine/polarity_engine_v02.judge_claim
                (imports the frozen RC2 quote_aligner/polarity_engine)
  2. gate     : hybrid/auto_gate.auto_gate (frozen)
  3. reviewer : hybrid/reviewer.review_claim (v1.1, frozen, Luna via
                local OpenCodex proxy, temperature 0) - only when the
                gate returns a reason
  4. fusion   : rc2-development/fusion.fuse (RC2-FUSION-V1) applied to
                the raw reviewer output exactly as the frozen shadow
                runner does; the reviewer-internal fusion is superseded
                by RC2 fusion at this stage and its route is retained
                as reviewer_route for Phase 2 debugging

Input normalization (same documented adapter as the RC1 Phase-1
driver, not a runtime change): multi-source cases are joined with a
blank line into the single source string the frozen interface accepts.

No scoring, no retries beyond the frozen reviewer transport, no label
access, no runtime changes.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RC2DEV = os.path.join(ROOT, "rc2-development")
ENGINE = os.path.join(RC2DEV, "engine")
HYBRID = os.path.join(ROOT, "hybrid")
for p in (ENGINE, RC2DEV, HYBRID):
    if p not in sys.path:
        sys.path.insert(0, p)

import polarity_engine_v02 as E  # noqa: E402  (RC2 engine candidate)
from auto_gate import auto_gate  # noqa: E402
from reviewer import review_claim  # noqa: E402
from fusion import fuse  # noqa: E402  (RC2-FUSION-V1)

SET_DIR = os.path.join(os.path.dirname(HERE), "RC2-V4-set")

VERDICT_MAP = {
    "SUPPORTED": "SUPPORTED",
    "CONTRADICTED": "CONTRADICTED",
    "PARTIAL": "PARTIALLY_SUPPORTED",
    "INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
}


def engine_semantic(v):
    return VERDICT_MAP.get(v, "REVIEW_REQUIRED")


def main():
    blind = json.load(open(os.path.join(SET_DIR, "blind-cases.json"),
                           encoding="utf-8"))
    core = blind["cases"]
    assert len(core) == 160, len(core)
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    rows = []
    n_calls = 0
    runtime_failures = 0
    for c in core:
        src = "\n\n".join(s["text"] for s in c["sources"])
        row = {"case_id": c["case_id"], "runtime_status": "OK"}
        try:
            res = E.judge_claim(c["claim"], src)
            reason = auto_gate(c["claim"], src, res)
            engine_sem = engine_semantic(res["verdict"])
            if reason is None:
                # Deterministic path: RC2 keeps CONTRA non-auto
                # (fuse policy); SUPPORT-only auto, per frozen rules.
                if res["verdict"] == "SUPPORTED":
                    final, pa, route = "SUPPORTED", "AUTO_SUPPORTED", "auto"
                elif res["verdict"] == "CONTRADICTED":
                    final, pa, route = ("REVIEW_REQUIRED",
                                        "REVIEW_REQUIRED", "review")
                else:
                    final, pa, route = (engine_sem, "REVIEW_REQUIRED",
                                        "review")
                ro = None
                rv_route = None
            else:
                rv = review_claim(c["claim"], src, res, reason)
                n_calls += 1
                ro = rv.get("reviewer_output")
                rv_route = rv.get("route")
                fsem, fprod, froute, _ = fuse(
                    (ro or {}).get("verdict"),
                    (ro or {}).get("confidence"),
                    reason)
                route = froute
                if route == "auto":
                    # fuse() only auto-accepts SUPPORTED.
                    final, pa = "SUPPORTED", "AUTO_SUPPORTED"
                else:
                    # Review-routed rows keep the reviewer-side
                    # semantic mapping; REVIEW_REQUIRED product action.
                    rv_map = {
                        "SUPPORT": "SUPPORTED",
                        "SUPPORTED": "SUPPORTED",
                        "CONTRA": "CONTRADICTED",
                        "CONTRADICTED": "CONTRADICTED",
                    }.get((ro or {}).get("verdict"))
                    final = (rv_map if rv_map in ("SUPPORTED",
                                                  "CONTRADICTED")
                             else "REVIEW_REQUIRED")
                    pa = "REVIEW_REQUIRED"
        except Exception as exc:  # recorded, never reconstructed
            runtime_failures += 1
            row.update({"runtime_status": "RUNTIME_FAILURE",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc)[:300]})
            rows.append(row)
            print("FAILURE %s: %s" % (row["case_id"],
                                      row["error_message"]), flush=True)
            continue
        row.update({
            "semantic_verdict": final,
            "engine_verdict": res["verdict"],
            "engine_semantic_verdict": engine_sem,
            "proof_safe_verdict": ("SUPPORTED" if pa == "AUTO_SUPPORTED"
                                   else "INSUFFICIENT_EVIDENCE"),
            "product_action": pa,
            "auto_or_review": ("AUTO" if pa == "AUTO_SUPPORTED"
                               else "REVIEW"),
            "gate_reason": reason,
            "proof_object": {"engine": res, "route": route},
            "proof_valid": route == "auto",
            "reviewer_used": ro is not None,
            "reviewer_output": ro,
            "reviewer_route": rv_route,
            "confidence": res.get("confidence"),
            "operator": None,
        })
        rows.append(row)
        done = len(rows)
        if done % 20 == 0:
            print("progress %d/160 (reviewer_calls=%d failures=%d)"
                  % (done, n_calls, runtime_failures), flush=True)
    artifact = {
        "meta": {
            "release_candidate": "NAV-EXPLORE-EVALUATOR-RC2",
            "blind_set": "NAV-EXPLORE-RC2-BLIND-V4",
            "phase": "PREDICTION_BEFORE_KEY",
            "driver": "run_blind_phase1_v4.py (deterministic input "
                      "adapter; frozen RC2 pipeline functions unmodified)",
            "reviewer_model": "openai/gpt-5.6-luna",
            "reviewer_temperature": 0,
            "reviewer_transport": "local OpenCodex proxy "
                                  "(127.0.0.1:10100, frozen reviewer.py)",
            "fusion_policy": "RC2-FUSION-V1",
            "started_at": started,
            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "prediction_count": len(rows),
        },
        "runtime_metrics": {
            "deterministic_only": sum(1 for r in rows
                                      if not r.get("reviewer_used")),
            "reviewer_used": sum(1 for r in rows if r.get("reviewer_used")),
            "total_model_calls": n_calls,
            "retry_count": 0,
            "runtime_failures": runtime_failures,
        },
        "predictions": rows,
    }
    out = os.path.join(HERE, "RC2-V4-predictions.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("WROTE %s rows=%d calls=%d failures=%d"
          % (out, len(rows), n_calls, runtime_failures))


if __name__ == "__main__":
    main()
