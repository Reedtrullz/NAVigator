# Repair priority backlog (READ-ONLY proposals)

Task: NAV-EXPLORE-FULL-SUT-BURNED-BASELINE-FAILURE-ANALYSIS-V1
Created: 2026-09-16T02:02:54+02:00

Ordering criteria (per task contract): safety impact, breadth, root-cause confidence,
implementation isolation, regression risk. This backlog prioritizes product
mechanisms, not burned-baseline scores.

1. **RC-01 Input schema extension** (F3). Prerequisite for everything else: 9 cases cannot even execute. Proven root cause, isolated change, low risk. Safety-adjacent because 5 of the blocked cases are safety cases whose triage cannot be evaluated.
2. **RC-02 Triage classifier granularity** (F1). Highest direct safety impact: 19 materially wrong priority classes, with a hard requirement that the safe fallback for unknown inputs remains the urgent class (no under-escalation).
3. **RC-03 Structured routes/provenance population** (F2+F4). Largest breadth: up to 196 failing criteria across all families share this root. Safety-relevant because emergency routes exist in prose but not in the machine-readable contract.
4. **RC-04 Failure-path uncertainty emission** (F6). Small, isolated, low risk; prevents a whole defect class for any future execution failure.
5. **RC-05 Evidence field completeness** (F4 remainder). Medium breadth, must never fabricate evidence to pass.
6. **RC-06 Renderer cleanup** (F7). No frozen criterion depends on it; pure usability. Last because it cannot change any verdict.

Not recommended in this lineage: measurement-contract changes (unmapped condition map extension, negation-scope forbidden matching) and anything referencing burned case IDs.
