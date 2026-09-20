# Final Authority Provenance Repair V1

Provenance-only repair of the frozen Measurement V3 burned baseline
(NAV-EXPLORE-MEASUREMENT-V3-FINAL-AUTHORITY-PROVENANCE-REPAIR-V1, 2026-09-16).

The original terminal freeze
(evaluation/measurement-v3-residual-human-adjudication-v1/, now superseded
historical, not deleted) classified ROUT-025::forbidden:01 and
ROUT-066::forbidden:01 as HUMAN_REVIEWED/OWNER-01. Post-freeze owner audit
showed the semantic decisions originated from ChatGPT/LLM. This lineage
corrects both rows to LLM_ADJUDICATED / CHATGPT_SINGLE_REVIEW_RESIDUAL.

Semantic observations, derived verdicts (ABSENT via M1:NEGATED), packets,
gold, and measurement contracts are unchanged. Final authority mix:
526 deterministic, 64 LLM-reviewed, 10 LLM-adjudicated (8 dual-pass Astra
residual + 2 ChatGPT single-review residual), 0 human-reviewed, 600 total.

Classification: BURNED_DEV_BASELINE_ONLY. Not human-reviewed, not certified,
not production readiness.

## Files

- TASK-LOCK.json - task lock, closed at terminal status
- repair-record.json - finding, discovery, correction, invariants, historical trace
- combined-measurement-results-complete-provenance-corrected.json - corrected 600-row results
- authority-map-provenance-corrected.json - corrected authority map
- combined-aggregate-metrics-provenance-corrected.json - corrected authority-dependent aggregates
- apply-provenance-repair.py - deterministic derivation script (asserts provenance-only diff)
- final-report.md - full report
- final-freeze-manifest.json / hashes.txt / closure-log.json - terminal freeze and verification

## Verification

From repo root:

    shasum -a 256 -c evaluation/measurement-v3-final-authority-provenance-repair-v1/hashes.txt

Upstream integrity:

    shasum -a 256 -c evaluation/measurement-v3-residual-human-adjudication-v1/hashes.txt

Terminal status:
MEASUREMENT_V3_BURNED_BASELINE_COMPLETE_PROVENANCE_CORRECTED
