# RC3.3.1 Legacy Regression Report

All legacy suites that can run under the task write-sandbox were re-executed green:

| Suite | Result | Mode |
|---|---|---|
| RC2 generalized regressions | 37/37 PASS | in-process import, output redirected |
| Tier-1 operator battery | 43/43 PASS | read-only execution |
| Operator regression | 23/23 PASS | in-process re-execution, redirected |
| RC3.1 engine probes | ALL PASS | read-only execution |
| RC3.1 relation runner | reproduces frozen baseline (0.6277 / 0.6866) | task-local output path |
| RC3.2 architecture runner | reproduces frozen baseline (0.514 / 0.4693, collapse 0.1034) | task-local output path |

SHA identity: task-local boundary.py (9200aa90...) and proposition.py (4e3b2d00...) are byte-identical to frozen RC3.3/RC3.2 artifacts; rc3-1-proof-semantics engine (16d4fdbf...) and boundary (9200aa90...) match recorded provenance. Legacy R31/R32 diagnostics are burned-development data only; no tuning was performed against them.

Not run (same rationale as RC3.3, preserved): RC2 phase-a bundle (writes into forbidden dirs; frozen RC2_PHASE_A_PASS artifact stands), KB 48/48 (no runner on disk), RC3 dev evaluator (missing /tmp cache, frozen artifact stands), decomposition 44/44 (no runner), quote-aligner standalone (out of scope per spec 41).
