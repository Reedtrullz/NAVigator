# Execution Harness Design

Evaluator-side runner: evaluation/full-sut-implementation/sut_runner/
(Phase 1). The runner executes the PRODUCT pipeline once per case and freezes
raw predictions. It never scores.

## Runner contract

    python -m sut_runner.run --corpus evaluation/dev-corpus-v1/cases/routing_cases.json +        --out evaluation/full-sut-implementation/runs/<run-id>/ +        --mode replay

Steps per run:

1. Load corpus via loader (integrity + SHA registry check).
2. For each case, in corpus order: strip gold, execute SUT ONCE.
3. Store raw SUT output JSON per case: predictions/<case_id>.json
   (byte-exact output; no post-processing).
4. Store errors separately: errors/<case_id>.json with stage, state, message,
   traceback-free detail (no secrets, no gold).
5. Freeze: write predictions-manifest.json with per-file SHA-256, corpus SHA,
   SUT component SHAs, timestamp. After freeze the directory is immutable;
   reruns go to a new run-id.
6. NEVER score inline. No scorer import in the runner process. Scoring is a
   separate command reading frozen predictions + gold envelopes:

       python -m sut_runner.score --run evaluation/full-sut-implementation/runs/<run-id>/

   (score entrypoint lives in the scorer-adapter follow-up; the runner itself
   has no gold access.)

## Prediction freeze principle

    SUT execution -> predictions freeze -> scorer sees gold

There is no SUT-scorer feedback loop. If scoring reveals product defects, the
fix happens in a NEW run with a new run-id and a new frozen manifest; the old
run stands as history. Run IDs are timestamps (UTC) + corpus family; they are
never reused.

## Execution modes

| Mode | Behavior |
|---|---|
| replay | Discovery runtime in replay mode (frozen fixtures). Fully deterministic; default for Phase 1-3 development and any future holdout prediction freeze. |
| live | Discovery runtime in live mode. Recorded per execution; used only when a task explicitly authorizes live discovery. |

Mode is a runner flag, recorded in the manifest; the SUT code path is
identical (adapter receives mode).

## Observability (minimal, no secrets)

Per case the runner records in run-log.jsonl:

- case_id, stage entered/completed (S1-S11 names), stage state (SUCCESS/
  PARTIAL/RECOVERABLE/TERMINAL),
- sources attempted (source_ref only; no credentials, no cookies),
- provenance count, discovery activity flag, safety decision path
  (priority + rule ids),
- latency per stage and total (wall ms),
- final execution_status.

The log is the diagnostic surface for the measurement lanes' provenance
questions; it contains no user data beyond the case id and no gold.

## Determinism registration

Replay-mode runs are byte-reproducible given the same corpus SHA + SUT
component SHAs + harness version; the manifest records all three so any run
can be re-verified. LLM stages would register model/config/prompt-version in
the manifest (ADR-006); Phases 1-3 include none.
