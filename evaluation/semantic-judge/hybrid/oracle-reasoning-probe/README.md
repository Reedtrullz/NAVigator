# Oracle Reasoning Probe

Task SEMANTIC-JUDGE-ORACLE-REASONING-PROBE (semantic-judge family). Status: COMPLETED 2026-09-02. Deliverable is analysis only — no packet R&D, holdout-v3, blind recert, or live dialog.

## Question

Why does the frozen v1.1 oracle reviewer score 7/45? Category-audit all 45 cases (+ ENT-D canary), test whether a structured-proof prompt and a deterministic proof validator recover the errors, and decide the failure mode.

## Decision

CURRENT_PROOF_DOCTRINE_IS_TOO_STRICT. Baseline doctrine accuracy on the 24-case probe is 22/24 (91.7%) vs 5/24 (20.8%) benchmark accuracy; 33/46 benchmark labels diverge from doctrine-consistent verdicts. Next step (not implemented): split the evaluation target (proof-doctrine vs semantic-intent score), then add a small bounded-operator layer in the deterministic evidence layer.

## Files

- final-report.md — all 44 SLUTTRAPPORT points with evidence
- analysis.md — headline metrics and decision rationale
- oracle-case-audit.md — per-category audit, canaries, label-issue list
- oracle-proof-ledger.json — 46-row audited ledger (A=6, B=17, C=12, D=3, E=6, F=2)
- probe-set.json — 24 probe cases + 21 negative controls
- baseline-results.json — frozen v1.1 baseline copy (provenance header)
- structured-proof-results.json / structured-proof-controls.json / stability-results.json — Luna runs
- validate_proof.py, inference-operators.json, proof-validator-spec.md — deterministic validator (15 operators)
- run_proof_probe.py, run_stability.py — runners
- build_ledger.py, cases_data.json — ledger builder + case data
- oracle-packets.json, sources/ — frozen inputs, do not modify

## Re-run

All calls go through the local proxy (openai/gpt-5.6-luna, temp 0, max_tokens 300).

    python3 build_ledger.py
    python3 validate_proof.py --export-operators
    python3 run_proof_probe.py
    python3 run_stability.py

Frozen artifacts (oracle-packets.json, ../packet-redesign/*, ../results/hybrid-eval.json, sources/) must not be modified.
