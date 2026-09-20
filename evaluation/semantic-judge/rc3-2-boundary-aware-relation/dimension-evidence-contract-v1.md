# Dimension Evidence Contract V1

Frozen before implementation (spec section 7). No metric/schema change
after implementation starts.

## 1. Purpose

The boundary layer currently computes nine dimensions and collapses each to
MATCH / MISMATCH / UNKNOWN before the relation layer sees anything. 51/88
baseline relation errors are classified RELATION_BOUNDARY_COLLAPSE. This
contract adds a richer per-dimension evidence representation WITHOUT
changing the frozen 3-state auto-support gate output.

## 2. Layer separation

A. DIMENSION EVIDENCE (rich, this contract): what the source says vs the
claim on each dimension.
B. AUTO-SUPPORT GATE (frozen): 3-state projection, unchanged semantics.
C. RELATION LAYER: consumes A (not B) for relation classification.

## 3. Dimension evidence states

Canonical state vocabulary (per dimension, codebase conventions):

- polarity: EXACT_MATCH | EXPLICIT_CONFLICT | PARTIAL_OVERLAP |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
- modality: EXACT_MATCH | SOURCE_STRONGER_THAN_CLAIM |
  SOURCE_WEAKER_THAN_CLAIM | DEONTIC_OPPOSITION |
  CONDITIONALLY_COMPATIBLE | RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
  (the reverse-direction licensing weaker-source -> stronger-claim is
  forbidden by definition; it can never be a licensed state)
- condition: EXACT_MATCH | CONDITIONALLY_COMPATIBLE | CONDITION_MISSING |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
- exception: EXACT_MATCH | EXCEPTION_CONFLICT |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
- actor: SAME_ACTOR | LICENSED_ACTOR_EQUIVALENCE | DIFFERENT_ACTOR |
  ACTOR_UNRESOLVED | NOT_APPLICABLE
- scope: SCOPE_COMPATIBLE | SCOPE_CONFLICT | RELEVANT_BUT_UNRESOLVED |
  NOT_APPLICABLE
- temporal: TEMPORAL_COMPATIBLE | TEMPORAL_CONFLICT |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
- numeric_quantity: NUMERIC_COMPATIBLE | NUMERIC_CONFLICT |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE
- clause_coverage: EXACT_MATCH | PARTIAL_OVERLAP |
  RELEVANT_BUT_UNRESOLVED | NOT_APPLICABLE

## 4. Provenance

Every dimension entry carries:

{"state": <state>, "rule": <deterministic rule id>, "evidence_span_id":
<span id or null>, "note": <short detail or null>}

No hidden heuristic: each state resolves to an explicit span, a named
deterministic rule, or RELEVANT_BUT_UNRESOLVED/NOT_APPLICABLE.

## 5. Frozen projection to the 3-state gate

Per dimension: conflict-class states (EXPLICIT_CONFLICT,
DEONTIC_OPPOSITION, CONDITION_MISSING, EXCEPTION_CONFLICT, DIFFERENT_ACTOR,
SCOPE_CONFLICT, TEMPORAL_CONFLICT, NUMERIC_CONFLICT) -> MISMATCH;
RELEVANT_BUT_UNRESOLVED / ACTOR_UNRESOLVED -> UNKNOWN; all compatible /
NOT_APPLICABLE states -> non-blocking. The projected gate output MUST be
equivalent to the current compare() for all inputs; equivalence is checked
by a differential test over the combined suites before relation consumption
is enabled. Gate keys (overall, blocking_dimensions, per-dimension 3-state
values) keep their current meaning and shapes.

## 6. Relation layer consumption

_relation() receives the dimension_evidence object and applies a frozen
pattern table (data, not scattered rules):

- polarity EXPLICIT_CONFLICT or modality DEONTIC_OPPOSITION (same
  proposition) -> CONTRADICTS candidate (positive incompatibility; final
  AUTO_CONTRADICTED still requires the existing proof obligation).
- modality SOURCE_WEAKER_THAN_CLAIM on an otherwise compatible proposition
  -> RELATED_BUT_INSUFFICIENT (never ENTAILS).
- modality SOURCE_STRONGER_THAN_CLAIM -> may license ENTAILS (stronger
  source grounds weaker claim).
- condition CONDITION_MISSING -> at most RELATED_BUT_INSUFFICIENT.
- actor DIFFERENT_ACTOR or scope SCOPE_CONFLICT -> at most
  RELATED_BUT_INSUFFICIENT unless a positive conflict rule applies.
- clause_coverage PARTIAL_OVERLAP blocks ENTAILS.

No case IDs, no literal case->relation maps (spec section 21).

## 7. Modality lattice as data

Modality direction decisions come from modality-lattice-v2.json (versioned
data file; relation layer reads it, does not re-encode direction logic in
branches). The frozen boundary modality table is untouched.

## 8. Safety invariants

- UNKNOWN is never upgraded to a compatible state by this layer.
- Gate semantics unchanged: previously blocked unsafe support stays
  blocked (differential test + frozen boundary suite).
- Final eligibility stays: relation == ENTAILS AND boundary
  BOUNDARY_COMPATIBLE AND structural validity AND grounded.
