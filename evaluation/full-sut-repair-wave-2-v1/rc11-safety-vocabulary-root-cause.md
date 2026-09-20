# RC-11 Root Cause: Safety Vocabulary / Category Collapse

## Root cause

Post-Wave-1 family PW1-R3: 19/20 safety cases had the correct collapsed
urgency LEVEL but failed the exact frozen category string. Over-triage
dominated (5 NON_ACUTE/REPORTING-family cases pushed to ACUTE_RISK_NOW;
3 reporting cases mapped to ACUTE instead of dedicated reporting categories).
No under-triage.

The internal classifier already produced a fine 12-class triage class, but
the emission layer collapsed it: both emission points applied
if priority not in OUTPUT_VALUES: priority = ACUTE_RISK_NOW, discarding the
fine class and substituting the coarse ACUTE bucket. The defect was output
vocabulary, not triage logic.

## Repair implemented

- Top-level safety_priority now carries the FINE 12-class triage class (e.g.
  SAFETY_CONCERN_NO_ACUTE_VIOLENCE) when valid. The nested safety.priority
  keeps the collapsed 3-level value required by the frozen scorer contract.
- Applied identically at both emission points: phase2/pipeline.py
  s11_output_emission and phase3/finalize.py finalize (the runner uses the
  phase3 path).
- evidence.safety_priority mirrors the fine class.
- EMERGENCY_TRIGGER_LOGIC_CHANGED = false: no changes to safety.py or
  trigger logic. Negated acute phrasing (e.g. ikke tanker om aa ta livet
  mitt) continues to fail closed to ACUTE_RISK_NOW (pre-existing behavior,
  safe direction). The guarded-able pattern (ikke livsfare) maps to
  NON_ACUTE_ROUTINE.
- Pinned test test_safety_granularity.py updated to expect the fine class at
  top level; new test_safety_output.py covers the 9-case matrix.
