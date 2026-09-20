# NAV Explore RC3G Scoring Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze a keyless, mechanically unambiguous RC3 generalization scoring policy and scorer without changing predictions, runtime, snapshot, thresholds, or preregistered gates.

**Architecture:** Record an immutable task lock, derive policy metadata from the frozen prediction schema and public holdout metadata, and implement pure scoring functions that accept already-authenticated truth data only as an explicit input. Keep proof layers, product routes, compound atoms, subgroup membership, confusion labels, exact counts, and Wilson intervals separate.

**Tech Stack:** Python 3 standard library, JSON, SHA-256, unittest-style synthetic self-tests.

**Spec:** `/Users/reidar/.codex/attachments/0b9b34e4-756b-4024-8793-24b277f2533d/pasted-text.txt`

## Global Constraints

- Prediction SHA must remain `6923c66c8abafde0bd0e3e58a282e2b40a3da4adefd3a364b25cddcd3a88a361`.
- Answer-key and construction-audit material must not be read, decrypted, or scored.
- No snapshot/runtime changes, rerun, threshold tuning, preregistration changes, or truth accuracy.
- Frozen `evaluation-metrics.md` wins over conflicting prompt text; deviations are documented.
- No truth artifacts, error analysis, label audit, or readiness verdict before G2.

### Task 1: Lock and verify frozen inputs

**Files:**
- Create: `evaluation/semantic-judge/rc3-generalization-holdout/run/scoring/TASK-LOCK.json`

- [ ] Rehash the prediction artifact and compare it to the required SHA.
- [ ] Verify snapshot manifest/component hashes, public holdout hashes, and keyless state without reading sealed payloads.
- [ ] Write the active scoring task lock with all mutation and scoring permissions disabled.

### Task 2: Freeze policy metadata

**Files:**
- Create: `evaluation/semantic-judge/rc3-generalization-holdout/run/scoring/scoring-policy.json`
- Create: `evaluation/semantic-judge/rc3-generalization-holdout/run/scoring/scoring-policy.md`

- [ ] Record authoritative prediction fields, exact aliases, denominators, proof definitions, accepted-proof boundary, compound alignment, subgroup source, label orders, Wilson/rounding rules, and every frozen gate.
- [ ] Record the prediction-only auto-coverage failure without issuing readiness.
- [ ] Record the exact public metadata source for 52 compound cases and the preregistered critical count of 25.

### Task 3: Implement scorer and synthetic checks

**Files:**
- Create: `evaluation/semantic-judge/rc3-generalization-holdout/run/scoring/score_generalization_frozen.py`

- [ ] Write a failing synthetic test for exact semantic scoring before implementation.
- [ ] Implement pure mechanical metric functions, explicit truth input, no sealed-file access, exact fractions, Wilson 95% intervals, proof-layer separation, compound metrics, confusion totals, and readiness logic.
- [ ] Run self-tests covering every item in spec section 39, including missing/extra atoms and runtime failure.

### Task 4: Freeze and QA

**Files:**
- Create: `evaluation/semantic-judge/rc3-generalization-holdout/run/scoring/scoring-policy-freeze.json`

- [ ] Hash policy, scorer, evaluation metrics, and proof contract.
- [ ] Run the section 44 QA checks and rehash all section 42 inputs.
- [ ] Confirm no official score, truth confusion matrix, per-case correctness, error analysis, or label audit artifact exists.
- [ ] Log the evidence-backed result to the Obsidian daily note without secrets or label material.
