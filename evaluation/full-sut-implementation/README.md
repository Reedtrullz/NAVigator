NAV-EXPLORE-FULL-SUT-IMPLEMENTATION-PHASE-1
============================================

Lineage: implementation of the frozen FULL_SUT_ARCHITECTURE_V1 design
(evaluation/full-sut-architecture-v1, spec: next-task-phase1.md,
SHA256 91d85301171b965f2af84ec8480f5368b60db67ba550affc60b49e6bd88a14c8)
against the frozen measurement baseline
(evaluation/measurement-v3-combined-freeze, manifest SHA256
331310497a6630dcefc2990079593eed048b9dc4808e8800b0b94b73cb9847c7).

Phase 1 scope: SUT skeleton, schemas, context, S1-S11 pipeline skeleton,
corpus loader with gold stripping, and a one-shot replay harness. No
business logic beyond fail-closed skeleton behavior. No scoring, no LLM
stages, no live discovery, no Phase 2.

Layout
------
runtime/sut/                     Product package (schemas, context, pipeline)
runtime/sut/schemas/             Frozen schema copies, byte-identical to
                                 evaluation/full-sut-architecture-v1 (see
                                 schemas/COPY-MANIFEST.json)
data/                            Frozen seed data (triage rules, routing rules,
                                 knowledge index)
sut_runner/                      Evaluator-side loader + one-shot harness
phase1-freeze/                   Frozen candidate hashes + manifest
runs/20260914T0830Z-phase1-freeze/  Official acceptance freeze run (120/120)
TASK-LOCK.json                   Task governance record
final-report.md                  Phase 1 terminal report

Running
-------
Product unit tests:
    PYTHONPATH=runtime python3 -m unittest discover -s runtime/sut -p 'test_*.py'
    -> 37 tests OK

Runner unit tests:
    PYTHONPATH='evaluation/full-sut-implementation:runtime' \
      python3 -m unittest discover -s evaluation/full-sut-implementation/sut_runner \
      -p 'test_*.py'
    -> 15 tests OK

One-shot replay (never scores; predictions only):
    PYTHONPATH='evaluation/full-sut-implementation:runtime' \
      python3 -m sut_runner.run \
      --corpus evaluation/dev-corpus-v1/cases/safety_cases.json \
      --out <out-dir> --mode replay

Determinism evidence: rerunning the safety corpus in replay mode produces
byte-identical prediction files (diff-verified against the official freeze
run, 2026-09-14).

Design notes
------------
INTERFACE_GAP-001: decision-context.schema.json permits
safety.priority = TRIAGE_FAILED, but the sut-output schema enum does not.
Fail-closed mapping: unverified triage becomes an ACUTE_RISK_NOW
placeholder with a TERMINAL failure record and presented_as_complete
= false. The frozen schemas were not edited; the gap is registered in
pipeline.py and phase1-freeze-manifest.json.

Gold-leak gate: acceptance greps predictions for the five gold-only
field names (acceptable_routes, forbidden_claims, required_uncertainty,
required_evidence_fields, critical_error_if) plus the literal "gold".
safety_priority is a REQUIRED output field mirroring the context field
of the same name, so it is excluded from the grep; the loader's serialized
JSON gold guard still guarantees no case gold reaches the pipeline.

S2 in Phase 1: triage evaluation is not implemented, so the safety layer
cannot be verified. Per FC-01 fail-closed logic the pipeline routes to
TERMINAL (EXECUTION_FAILED, refusal answer) rather than answering on an
unverifiable safety basis.

Hard stop: Phase 1 terminal status is FULL_SUT_PHASE_1_READY. Phase 2
requires a new explicit owner authorization.
