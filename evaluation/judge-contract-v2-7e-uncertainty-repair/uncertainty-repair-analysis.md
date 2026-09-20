# Uncertainty Repair Analysis (V2.7E)

Task: NAV-EXPLORE-JUDGE-CONTRACT-V2_7E-UNCERTAINTY-CONTRACT-REPAIR
Provenance: repairs preregistered in V2.7D diagnosis; frozen draft lineage verified before execution.

## UNC-A1: contradictory limitation maps to UNRESOLVED

Defect (V2.7D diagnosis): the frozen V1.4 table mapped EXPLICIT_LIMITATION x
CONTRADICTORY_LIMITATION to PARTIAL, while the semantics of unusable limitation
prose (self-contradicting, garbled, self-retracting) require UNRESOLVED. Burned
V2.7 gold used UNRESOLVED (UNC-46/47) and fresh human calibration split 9/18
boundary rows on this cell.

Repair: EXPLICIT_LIMITATION x CONTRADICTORY_LIMITATION => UNRESOLVED. The
PARTIAL row for this behavior is removed. PARTIAL remains valid only for
limitation prose communicating a real, identifiable, incomplete qualification.

Mechanical diff proof: derivation_tables/EXPLICIT_LIMITATION/CONTRADICTORY_LIMITATION
changed PARTIAL -> UNRESOLVED; no other derivation cell changed.

## UNC-A2: UNCLEAR_PROSE defined

Defect: UNCLEAR_PROSE was not defined by the frozen V1.4 contract; incoherent or
fragmentary limitation prose had no canonical classification path.

Repair: UNCLEAR_PROSE added as an output behavior with the preregistered
sentence-level definition, mapping to UNRESOLVED in all derivation tables
(EXPLICIT_LIMITATION and NON_ASSERTION_CONSTRAINT rows added; compound
components inherit via the same tables).

Mechanical diff proof: output_behaviors extended with UNCLEAR_PROSE;
derivation_tables/*/UNCLEAR_PROSE = UNRESOLVED; behavior_definitions added.

## Boundary semantics preserved

- Decision tree precedence: UNCLEAR_PROSE checked before CONTRADICTORY_LIMITATION
  (incoherent text cannot be safely classified as self-contradicting), then
  normal V1.4 classification.
- Absence of uncertainty language is never automatically VIOLATED.
- Compound aggregation rule preserved verbatim, including the preregistered
  consequence that [UNRESOLVED, SATISFIED] aggregates to PARTIAL. The Set A
  calibration did not exercise a compound row of this shape; that remains an
  observed-but-unchanged boundary for a future contract task if humans or
  models disagree on it.

## Human stability evidence

Set A: 32 fresh uncertainty fixtures (9 preregistered tag classes, including
4 contradictory, 3 unclear, 3 self-retracted boundary rows). Two blind
intra-annotator passes (table-first sequential / semantics-first reverse).
Overall agreement 32/32 = 1.0000. Zero-gates: 0 disagreements on contradictory,
unclear, and self-retracted rows. Both preregistered gates pass.
