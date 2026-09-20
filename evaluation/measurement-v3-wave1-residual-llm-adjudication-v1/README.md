# Wave-1 Residual LLM Adjudication (gpt-5.6-sol, LOW)

Task: NAV-EXPLORE-MEASUREMENT-V3-WAVE1-RESIDUAL-LLM-ADJUDICATION-V1
Terminal: MEASUREMENT_V3_REMEASURE_WAVE_1_SECONDARY_RESIDUAL_PENDING

Blind dual-pass Sol adjudication of the 4 wave-1 residual packets. All 8 calls valid;
whole-object A==B consensus reached on 0/4; routing-relevant primitives agreed 4/4 but
rationale text differed, so all 4 remain PENDING_HUMAN_ADJUDICATION under the frozen rule.

Key artifacts:
- TASK-LOCK.json (frozen constraints + terminal status)
- accounting-audit.json (check A/B + open-item resolution, raw-row recount)
- sol-config.json / run_sol_adjudication.py (frozen execution config + runner)
- sol-blind-inputs.json + sol-blind-inputs-leakage-audit.json (blindness, PASS)
- sol-pass-a.jsonl / sol-pass-b.jsonl / sol-adjudication-consensus.json (observations)
- sol-adjudication-frozen-observations.json (pre-derivation freeze with hashes)
- wave1-remeasurement-complete-after-secondary-residual.json (600/600 lineage artifact,
  596 authoritative, 4 pending; aggregates recomputed from raw rows)
- measurement-manifest.json / hashes.txt (integrity pins)
- final-report.md (full report)

Upstream lineage untouched: evaluation/measurement-v3-remeasure-repair-wave-1/
Old baseline untouched: evaluation/measurement-v3-final-authority-provenance-repair-v1/

Hard stop: human adjudication or a consensus-semantics amendment both require separate
owner authorization.
