"""Phase 3 one-shot SUT execution harness.

Ported from the Phase 1 runner; the only differences are the pipeline
entry point (sut.phase3.pipeline), the manifest artifact name, and the
harness version. Scoring happens in a separate command against frozen
predictions.
"""

import argparse
import hashlib
import json
import os
import sys
import time

_PHASE2_RUNNER_DIR = os.path.dirname(os.path.abspath(__file__))
if _PHASE2_RUNNER_DIR not in sys.path:
    sys.path.insert(0, _PHASE2_RUNNER_DIR)

from sut_runner.loader import iter_inputs, load_corpus  # noqa: E402


REPO_ROOT = os.path.abspath(os.path.join(_PHASE2_RUNNER_DIR, "..", "..", ".."))
PRODUCT_PATH = os.path.join(REPO_ROOT, "runtime")
if PRODUCT_PATH not in sys.path:
    sys.path.insert(0, PRODUCT_PATH)

_SUT_FILES = (
    "runtime/sut/__init__.py",
    "runtime/sut/schemas.py",
    "runtime/sut/context.py",
    "runtime/sut/pipeline.py",
    "runtime/sut/phase2/__init__.py",
    "runtime/sut/phase2/safety.py",
    "runtime/sut/phase2/decompose.py",
    "runtime/sut/phase2/knowledge.py",
    "runtime/sut/phase2/discovery_adapter.py",
    "runtime/sut/phase2/routes.py",
    "runtime/sut/phase2/aggregate.py",
    "runtime/sut/phase2/pipeline.py",
    "runtime/sut/phase3/__init__.py",
    "runtime/sut/phase3/planner.py",
    "runtime/sut/phase3/render.py",
    "runtime/sut/phase3/finalize.py",
    "runtime/sut/phase3/pipeline.py",
    "runtime/sut/schemas/COPY-MANIFEST.json",
    "runtime/sut/schemas/sut-input.schema.json",
    "runtime/sut/schemas/sut-output.schema.json",
    "runtime/sut/schemas/decision-context.schema.json",
    "data/safety-triage-rules-v2.json",
    "data/rules-v1.json",
    "data/knowledge-index-v1.json",
)


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def execute_case(sut_input, mode):
    """Import the Phase 3 pipeline and execute it exactly once."""
    from sut.phase3.pipeline import run_with_trace

    started = time.perf_counter()
    try:
        output, trace = run_with_trace(sut_input, config={"mode": mode})
        error_record = None
    except Exception as exc:  # execution error capture; no traceback text persisted
        output = None
        trace = []
        error_record = {
            "stage": "harness",
            "state": "TERMINAL",
            "message": "%s: %s" % (type(exc).__name__, exc),
        }
    total_ms = round((time.perf_counter() - started) * 1000, 3)
    return output, trace, error_record, total_ms


def main(argv=None):
    parser = argparse.ArgumentParser(description="Phase 3 SUT one-shot execution harness")
    parser.add_argument("--corpus", required=True, help="path to dev-corpus case file")
    parser.add_argument("--out", required=True, help="run output directory")
    parser.add_argument("--mode", default="replay", choices=["replay", "live"])
    args = parser.parse_args(argv)

    corpus_path = (
        os.path.join(REPO_ROOT, args.corpus) if not os.path.isabs(args.corpus) else args.corpus
    )
    manifest = json.load(
        open(os.path.join(REPO_ROOT, "evaluation/dev-corpus-v1/manifest.json"), encoding="utf-8")
    )
    corpus = load_corpus(corpus_path, sha_registry=manifest["files"])

    executed_at = _utc_now()
    out_dir = args.out
    pred_dir = os.path.join(out_dir, "predictions")
    err_dir = os.path.join(out_dir, "errors")
    os.makedirs(pred_dir, exist_ok=True)
    os.makedirs(err_dir, exist_ok=True)

    manifest_entries = []
    count = 0
    with open(os.path.join(out_dir, "run-log.jsonl"), "w", encoding="utf-8") as log:
        for sut_input in iter_inputs(corpus, executed_at=executed_at):
            case_id = sut_input["case_id"]
            output, trace, error_record, total_ms = execute_case(sut_input, args.mode)
            stages = trace or [
                {"stage": "harness", "state": "TERMINAL", "latency_ms": total_ms}
            ]
            status = (output or {}).get("execution_status", "EXECUTION_FAILED")
            rec = {
                "case_id": case_id,
                "executed_at": executed_at,
                "mode": args.mode,
                "stages": stages,
                "total_latency_ms": total_ms,
                "execution_status": status,
            }
            log.write(json.dumps(rec, ensure_ascii=False) + "\n")

            if output is not None:
                pred_path = os.path.join(pred_dir, case_id + ".json")
                with open(pred_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False, sort_keys=True, indent=1)
                manifest_entries.append({
                    "case_id": case_id,
                    "file": case_id + ".json",
                    "sha256": _sha(pred_path),
                })
            else:
                err_path = os.path.join(err_dir, case_id + ".json")
                with open(err_path, "w", encoding="utf-8") as f:
                    json.dump(error_record, f, ensure_ascii=False, indent=1)
            count += 1

    sut_component_shas = {
        rel: _sha(os.path.join(REPO_ROOT, rel)) for rel in _SUT_FILES
    }
    run_manifest = {
        "artifact": "sut-predictions-manifest-v1-phase3",
        "corpus": corpus["corpus"],
        "family": corpus["family"],
        "corpus_sha256": _sha(corpus_path),
        "mode": args.mode,
        "executed_at": executed_at,
        "prediction_count": len(manifest_entries),
        "case_count": count,
        "sut_component_shas": sut_component_shas,
        "harness_version": "sut_runner/3.0-phase3",
        "predictions": manifest_entries,
    }
    with open(os.path.join(out_dir, "predictions-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, ensure_ascii=False, indent=1)

    print(
        "FULL_SUT phase3 freeze complete: %d predictions, %d errors, mode=%s -> %s"
        % (len(manifest_entries), count - len(manifest_entries), args.mode, out_dir)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
