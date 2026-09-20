# Dev Corpus Semantic Judge V1.3 - Boundary Clarification

Task: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3-BOUNDARY-CLARIFICATION
Status: ACTIVE (boundary contract docs + Set A built; human calibration pending)

## Purpose

V1.2 stopped at SEMANTIC_JUDGE_V1_2_ANNOTATION_CONTRACT_NOT_READY with two
residual semantic boundaries: (A) negative uncertainty requirements
("must not conclude X") were collapsing into not-applicable, and (B) routes
that are merely mentioned, negated, retracted or vague were being scored as
NO_ACCEPTABLE_ROUTE. V1.3 adds two non-score-bearing intermediate fields:

1. uncertainty_requirement_mode: NONE / EXPLICIT_LIMITATION /
   NON_ASSERTION_CONSTRAINT / COMPOUND
2. route_commitment: POSITIVE_ASSERTION / HEDGED_POSITIVE_ASSERTION /
   NEGATED / SELF_RETRACTED / QUOTED_ONLY / HYPOTHETICAL_ONLY /
   VAGUE_UNIDENTIFIABLE / AMBIGUOUS_COMMITMENT

Score labels are unchanged from V1.2.

## Current state (2026-09-10)

* TASK-LOCK.json, baseline-integrity.json (29 artifacts SHA-verified MATCH),
  burned-data-registry.json (V1.2 official 80 = BURNED), contract docs
  (uncertainty-requirement-modes.md, route-commitment-contract.md,
  boundary-analysis.md, annotation-decision-trees.md): complete.
* boundary-calibration-a.json: 32 fresh fixtures built (16 route commitment,
  16 uncertainty mode), burned after labeling.
* v1_3_annotate.py: dual blind runner with fail-closed schema guards
  (non-evaluable commitment => UNRESOLVED; NONE => NOT_REQUIRED;
  NON_ASSERTION_CONSTRAINT + NOT_REQUIRED invalid).
* First annotation run failed: HTTP 429 "The usage limit has been reached"
  (account usage window), see calibration-a-run.log. No labels registered.

## Resume

Before rerunning, execute the frozen 7-step gate in resume-gate-v1-3.json
(lock ACTIVE, baseline SHA reverify, Set A/contract/runner SHA verify,
successful annotations == 0, no partial label outputs). If the first new
call still gets account-429: stop, no model switch, no extra retries.

When the usage window has reset:

    python3 v1_3_annotate.py boundary-calibration-a.json boundary-calibration-a

Then follow the spec: Set B (32 new fixtures) -> contract freeze -> model
calibration -> official 80 -> model validation -> stability -> scorer freeze.
MODEL_CALLS = 0 until boundary calibration passes.
