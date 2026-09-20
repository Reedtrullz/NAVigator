# Hybrid architecture - FROZEN v1.0 (2026-09-02)

    claims
      |
      v
    quote-aligner v0.2 (frozen, deterministic, modellfri)
      |
      v
    auto_gate.py (deterministic routing, frozen v1.0)
      |-- gate passes (~31% of dev claims) --> AUTO verdict
      |-- gate fails (~69%)                --> reviewer.py
                                              |
                                              v
                                           evidence packet builder
                                           (claim atoms + candidate
                                            spans + findings, no web)
                                              |
                                              v
                                           gpt-5.6-luna via local
                                           OpenCodex proxy (127.0.0.1:10100)
                                              |
                                     fidelity validator (deterministic)
                                              |
                                    pass + conf>=T -> reviewer verdict
                                    else           -> REVIEW_REQUIRED

## Components

* measure_auto_coverage.py - strict baseline (no gates)
* auto_gate.py - frozen routing gates
* measure_gated_coverage.py - gated coverage measurement
* reviewer.py - packet builder + luna caller + schema + fidelity check
* run_hybrid_eval.py - full harness (fusion per fusion-spec.md)
* results/ - all measurements

## Model

One reviewer config only: openai/gpt-5.6-luna, temperature 0,
local proxy, direct chat-completions calls.  Documented in
reviewer-config section of reviewer.py docstring.  No model bake-off.

## Non-goals this stage

holdout-v3, blind recert, live dialog, NAV/kommune research, KB tuning,
deterministic lexical v0.3, more than one reviewer iteration (B max).
