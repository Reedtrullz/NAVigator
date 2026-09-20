# Dev Corpus Semantic Judge V1.3M - mimo-v2.5 Model Migration

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3M-MIMO-MIGRATION
Status: DEV_CORPUS_SEMANTIC_JUDGE_V1_3M_NOT_READY

## What this is

Explicit, user-authorized model migration of the V1.3 semantic-judge lineage
from GPT-5.6-Luna (blocked by account usage window; 0 valid semantic
observations) to commandcode-auth mimo-v2.5
(wire model command-code/xiaomi/mimo-v2.5 via local proxy). One variable
changed: JUDGE_MODEL. Contract, fixtures, scoring rules, decision trees and
the fail-closed parser were reused after SHA verification.

## Artifacts

- TASK-LOCK.json: task lock with full execution notes and terminal status.
- migration-rationale.md: why Set A was reusable, what changed, what did not.
- source-artifact-pins.json: SHA pins for all reused frozen V1.3 artifacts.
- verify_baseline_m.py + baseline-integrity.json: 29/29 baseline artifacts
  verified (read-only; no writes into the V1.3 lineage).
- model-identity.json: model/provider/endpoint/auth-mechanism capture.
- transport-smoke.json: single non-evaluation smoke call (PASS).
- boundary-calibration-a.json: byte-identical copy of V1.3 Set A
  (SHA 0e1491c6...703d verified before the run).
- v1_3m_annotate.py: adapter (model binding + max_tokens 2000 headroom +
  mechanical zero-gate guard fix; semantics byte-identical).
- set-a-run.json / set-a-agreement.json / calibration-a-run.log: the single
  completed dual-blind Set A run and its provenance.

## Terminal result

Set A gate FAILED under frozen V1.3 gates:

- overall (full-label, frozen protocol): 0.0
- note-only disagreement rows (agree on all semantic fields): 24/32
- route_commitment 0.8125; route_verdict 0.8125
- uncertainty_mode 0.8125; uncertainty_verdict 0.6875
- zero-gates: all 0 (the important hard-safety gates held)
- schema/transport failures: 3 (2 empty-content, 1 JSON parse)

Real semantic-field disagreements: 5 (BRT-10, BRT-11: quoted/hypothetical vs
hedged-positive; BUN-01: NONE vs EXPLICIT_LIMITATION; BUN-09: UNRESOLVED vs
VIOLATED; BUN-13: PARTIAL vs VIOLATED) - concentrated exactly on the boundary
classes V1.3 was designed to clarify.

Per sections 8 and 19 of the migration spec: no clarification pass, no Set B,
no threshold adjustment, no prompt tuning. The correct reading is: the V1.3
contract is implementable with mimo (structured output, zero-gates held), but
mimo's dual-pass primitive stability on boundary classes is below what Set B
would require. Set A is burned (labels were delivered, unlike Luna).

## Not done (per spec)

No Set B, no contract freeze, no model calibration, no official 80, no
stability run, no product holdout, no runtime change, no GPT-5.5.
