# RC3.2 Implementation Report - DIMENSION_EVIDENCE_LAYER_V1

Task: NAV-EXPLORE-RC3_2-BOUNDARY-AWARE-RELATION-RECOVERY

## Budget

- Implementation pass: 1 of 1 (spec section 28).
- Bounded bugfix pass: 1 of 1 (spec section 31). Budget exhausted; all
  post-bugfix numbers below are final for this task. No further tuning
  was performed after the bugfix pass.
- Subagents: 0 of 2 allowed.

## What changed

### boundary.py (rich dimension-evidence layer)

Rich polarity provenance now distinguishes a general EXPLICIT_CONFLICT
from an exception-bounded conflict via the new rule id
"DE-polarity-exception-bounded" (state kept EXPLICIT_CONFLICT so the
frozen section-5 projection is unchanged). The direction-unknown
modality mismatch fallback keeps state DEONTIC_OPPOSITION for
projection compatibility but is labeled "DE-modality-unresolved-direction"
so the relation layer knows deontic opposition is NOT established.

### engine.py (relation consumption, the one implementation pass)

"_relation" now consumes the rich states first, per the frozen contract
section 6 pattern table:

1. clause_coverage PARTIAL_OVERLAP -> RBI (clause scope breaks
   proposition identity; negation after the aligned span is not yet
   propositional).
2. polarity EXPLICIT_CONFLICT on shared content -> CONTRADICTS, except
   the exception-bounded rule id, which falls to RBI.
3. modality DEONTIC_OPPOSITION with the named opposition rule id
   (DE-modality-deontic-opposition) on shared content -> CONTRADICTS;
   the direction-unknown fallback never auto-contradicts.
4. modality SOURCE_WEAKER_THAN_CLAIM -> RBI (never ENTAILS).
5. condition CONDITION_MISSING / actor DIFFERENT_ACTOR / scope
   SCOPE_CONFLICT -> capped at RBI.
6. modality EXACT_MATCH / CONDITIONALLY_COMPATIBLE /
   SOURCE_STRONGER_THAN_CLAIM -> ENTAILS (relation layer; the 3-state
   gate still controls final auto-support).

The R13/R14/R15/R15b battery rules now fire CONTRADICTS only when the
dimension layer reports positive conflict (EXPLICIT_CONFLICT, or
DEONTIC_OPPOSITION from the named rule); otherwise they report RBI as
the relation. "_hard_polarity_opposition" gained two generalized
guards: exception scope is checked at sentence level (an "unntak"
clause bounds the rule it belongs to, even when the clause splitter
separates them), and claim-side restrictive absolutes
("aldri/bare/kun") are not neutralized by evidence-side exceptions.

"modality-lattice-v2.json" was corrected BEFORE implementation to
match the frozen contract section 6 exactly (removed an extra
ACTOR_UNRESOLVED cap that the contract does not contain).

## Gate safety

The 3-state auto-support gate is untouched. test_gate_equivalence.py:
0/677 gate diffs, 0 projection mismatches (run after every edit).
Frozen boundary suite (80 cases) after the change: FALSE_AUTO_SUPPORT =
0, precision 1.0, recall 0.973, unsound eligible 0.

## Known limitations (documented, not patched)

- Rich modality has no SOURCE_WEAKER_THAN_CLAIM hits on the current
  suites (gate MISMATCH + weaker direction maps elsewhere); the
  consumption rule is in place and contract-compliant.
- ACTOR_UNRESOLVED does not cap relation (per frozen contract section
  6); ENTAILS relations under an unresolved actor remain ineligible
  for auto-support because the 3-state gate stays UNKNOWN.
- BA-099/BA-149-style gate collapse (rich scope/actor honest, 3-state
  UNKNOWN) is the dominant residual class; fixing it requires a gate
  change, which this task forbids.
