# Wave-1 Consensus Comparator Repair V1

Terminal status: `MEASUREMENT_V3_REMEASURE_WAVE_1_COMPLETE`
(see TASK-LOCK.json). Classification: `BURNED_DEV_BASELINE_ONLY`.

Repairs the Wave-1 Sol residual comparator (Branch A implementation defect):
whole-object A==B was task-local scope; the measurement contract's semantic is
primitive-level consensus on AUTHORITATIVE_SEMANTIC fields with per-pass
evidence validation. Replayed with 0 LLM calls; 4/4 residuals resolved;
Wave-1 result completed to 600/600 authoritative criteria.

## Artifacts

- input-integrity.json — 10 frozen-input pins, all verified
- consensus-rule-provenance.json / consensus-rule-analysis.md — Branch A evidence
- field-authority-map.json — semantic field authority classes
- comparator-repair-record.json — old vs corrected rule
- semantic-consensus-comparison.json — 4/4 corrected-rule consensus replay
- derived-residual-results.json — frozen kernel derivation
- comparator-repair-freeze-manifest.json — task-local freeze pins
- complete-wave1-measurement-results.json — 600-row authoritative result
- complete-wave1-aggregate-metrics.json — aggregates (HARD_FAIL 0.4150, NON_PASS 0.5068 on 588)
- updated-baseline-transition-matrix.json — old-baseline delta, RC effects
- hashes.txt — SHA-256 of all artifacts except itself and TASK-LOCK.json
- final-report.md — 50-item spec report

## Read order

final-report.md -> consensus-rule-analysis.md -> updated-baseline-transition-matrix.json.

The terminal TASK-LOCK.json pins complete-wave1-measurement-results.json;
the lock's own SHA is recorded in the session report, not in the lock.
