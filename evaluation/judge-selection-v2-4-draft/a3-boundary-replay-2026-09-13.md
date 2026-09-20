# A3 Boundary Layer Read-Only Replay - 2026-09-13

Status: VERIFICATION_ONLY / NO_WRITES_TO_FROZEN_LINEAGES / NO_MODEL_CALLS

Purpose: confirm the frozen, proven A3 boundary pre-classifier still reproduces deterministically on current machine state while V2.4 awaits owner authorization.

## Method

Inline Python only (no scratch files, no lineage writes). Imported the frozen engine directly and recomputed the burned regression cascade in memory, then compared to the frozen artifacts. The existing `run_burned_regressions.py` was NOT executed because it writes in-place to frozen artifact paths.

- Engine: `dev-corpus-semantic-judge-v1-6a3/boundary_preclassifier.py`
- Engine SHA-256: `21047fdaaaa4cc28fca1d4f075a922555e742ca2022d7059be22036694f2563b` (matches frozen `preclassifier-manifest-v1-6a3.json` = `0fedd38b5aa680a891dd9e16307e5de200cd3e06464789b8393580d4d71bcd00` embedded engine hash)

## Results

| Set | Frozen artifact | Frozen precision | Replay precision | False deterministics | Drift |
|---|---|---|---|---|---|
| burned-120 (V1.6A) | burned-120-regression.json, all_gates_pass=true | 1.0 | 1.0 | 0 | MATCH |
| burned-60 (V1.6A.1 targeted) | burned-targeted60-regression.json, all_gates_pass=true | 1.0 | 1.0 | 0 | MATCH |
| burned-80 strict (V1.6A.2 official) | burned-v1-6a2-80-regression.json | 0.871 | 0.871 | 4 (the 4 registered gold disputes, exactly) | MATCH |
| burned-80 dispute-aware | same | 1.0 | 1.0 | 0 | MATCH |

Dispute rows re-checked label-for-label (label, abstained, rule_id): OFF-SAME-17 NEGATED / BC_ROUTE_NEGATED_01, OFF-SCOPE-08 QUOTED_ONLY / BC_ROUTE_QUOTED_01, OFF-SCOPE-09 HYPOTHETICAL_ONLY / BC_ROUTE_HYPOTHETICAL_01, OFF-SCOPE-16 QUOTED_ONLY / BC_ROUTE_QUOTED_01. Zero drift on all four.

## Interpretation and Non-Claims

- The proven boundary layer (1.0 fresh precision, 120-fixture fresh set, frozen candidate) remains byte-stable and deterministically reproducible. No environmental drift.
- This is burned-data regression verification only; it is not new generalization evidence and adds no boundary capability.
- First replay attempt showed an apparent burned-80 mismatch caused by comparing strict replay against the frozen dispute-aware accounting (and vice versa); corrected mapping shown above. The corrected comparison matches exactly.
- V2.3 terminal status (V2_3_NO_MODEL_QUALIFIES) unchanged; V2.4 draft (TASK-SPEC-DRAFT.md SHA 44c269c6f5fb652510b781068994936445de3b370275f20b2b6ed3b117750ec1) still awaiting explicit owner authorization.
