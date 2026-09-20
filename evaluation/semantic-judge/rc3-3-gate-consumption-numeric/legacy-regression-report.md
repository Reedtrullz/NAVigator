# Legacy Regression Report (RC3.3)

Machine-readable detail: results/legacy-regression-report.json.

RC3.3 modifies only engine_local/engine.py and engine_local/numeric.py
in the task-local copy. Frozen ancestor artifacts are byte-identical
to their recorded SHAs, so legacy suites that execute ancestor code
need no re-execution; where ancestor code was re-executed read-only,
results are recorded below. In-process re-execution with task-local
output redirection was used for suites that would otherwise write into
their own (forbidden) task directories.

## Executed

| Suite | Result | Mode | Output |
|---|---|---|---|
| RC2 engine regressions | 37/37 PASS | in-process re-execution | results/legacy-rc2-regression.json |
| Tier-1 operator battery | 43/43 PASS | read-only (writes nothing) | stdout recorded here |
| Operator regression | 23/23 PASS | in-process re-execution | results/legacy-operator-regression.json |
| RC3.1 engine probes (21) | ALL PASS | read-only | stdout recorded here |
| RC3.1 relation runner | reproduced frozen baseline | explicit task-local output | results/legacy-r31-relation.json |
| RC3.2 architecture runner | reproduced frozen baseline | explicit task-local output | results/legacy-r32-arch.json |
| Sibling SHA audit | byte-identical | sha256 only | results/legacy-regression-report.json |

Burned diagnostics (not gates, no tuning): RC3.1 fresh atom acc
0.6277 / macro-F1 0.6866; RC3.2 fresh atom acc 0.514 / macro-F1
0.4693, collapse rate 0.1034. Both reproduce their frozen records.

## Not run (documented)

- RC2 phase-a bundle (qa_check, canaries, id_guard): invokes runners
  that write into forbidden task dirs. Frozen evidence:
  rc2-development/phase-a-gates.json (RC2_PHASE_A_PASS). The Tier-1
  battery and RC2 regression suite from that bundle were re-executed
  green here.
- KB baseline 48/48: no score_baseline.py runner exists on disk; the
  frozen phase-a-gates.json record stands. RC3.3 does not touch the
  RC2 engine layer that gate executed.
- RC3 dev evaluator regression: rc3-development/evaluate_dev.py
  requires a missing /tmp review cache and writes into its own dir;
  rc3_engine bytes are unchanged by this task.
- Decomposition 44/44: no such standalone runner found on disk;
  decomposition.py is byte-identical to the RC3.2 freeze and all 21
  deterministic probes pass.
- Quote-aligner standalone: out of scope per spec 41 (no RC3.3
  runtime import path).

## Safety canaries

Frozen RC2 canaries (ENT-C, N-R1, product variants) all pass in the
frozen phase-a-gates.json artifact. RC3.3 fresh-suite equivalents:
critical false ENTAILS = 0, critical false CONTRADICTS = 0, ungrounded
accepted proofs = 0 (results/proof-safety-audit.json).
