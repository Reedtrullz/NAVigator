# Source integrity report (Source Gate 0)

## Authoritative source state

Source engine: RC3.2 frozen state in
evaluation/semantic-judge/rc3-1-proof-semantics/rc3_1_engine/.

Recorded before copy (SHA256):

- engine.py
  16d4fdbf34afe1ca460c6ea2c43b2937dc1cc4c7ace21c4da6324520a28b2f20
- boundary.py
  9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c48c3ef026343fc1e

## Task-local copy

Copied to engine_local/ before any edit and verified byte-identical
against the recorded SHAs above. proposition.py and
decomposition.py copied alongside.

Import verification: engine_local.engine imports from
.../rc3-3-gate-consumption-numeric/engine_local/engine.py after
sys.path.insert(0, task_dir). The copy resolves the frozen
modality-lattice-v2.json (RC3.2) and modality-boundary-table.json
(RC3.1 support boundary) through the same relative paths as the
original; those files are read at import time and never written.

## Checks

- py_compile: PASS (all engine_local modules)
- actual import: PASS (path recorded above)
- imported engine path: task-local copy, not the RC3.1 original
- engine SHA before edit: 16d4fdbf34af...4520a28b2f20 (full above)
- Python: 3.14.6
- C0 control-char scan: PASS (run at QA stage on all task files;
  results recorded in final report)
- write-path guard: built before first evaluator run (see
  write-sandbox-report.md)
