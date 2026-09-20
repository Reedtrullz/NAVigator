# Reviewer / Fusion Authority Report (Phase C)

## Old model (RC2, root cause)

RC2 fusion was a confidence mixer: reviewer SUPPORT at confidence
>= 0.90 plus a generic-flag check could auto, and the reviewer could
downgrade engine autos on confidence alone. One confidence number
stood for decomposition, evidence, proof, semantics, arbitration and
product routing at once (spec 6 violation). Consequence on V4:
143/160 routed to review, and reviewer authority was the dominant
final-verdict source.

## New model (RC3, ARBITRATION_V2 + PRODUCT_ROUTING_V2)

Proof states are explicit: ENGINE_PROOF_ACCEPTED, ENGINE_NO_PROOF,
ENGINE_CONFLICT, ENGINE_UNSAFE (spec 7). Routing table (frozen):

- accepted SUPPORT proof -> AUTO_SUPPORTED
- accepted CONTRADICTION proof -> AUTO_CONTRADICTED
- genuinely insufficient evidence -> ABSTAIN_INSUFFICIENT
- relevant-but-unresolved / unsafe / conflict / ambiguity ->
  REVIEW_REQUIRED
- no generic reviewer confidence alone produces an auto (spec 10).

Monotonic arbitration (spec 8-9):

- R1: a valid accepted proof stays auto. A bare
  requires_human_review flag is metadata only; downgrade requires
  grounded reviewer spans (bounded bugfix pass applied).
- R2: reversal requires a COUNTER_PROOF with concrete grounded spans
  that satisfies structural validation and soundness checks; even
  then the route is REVIEW (adjudication), never an auto flip.
- R3: ENGINE_UNSAFE / ENGINE_CONFLICT always review.
- R4: reviewer can NEVER upgrade NO_PROOF to auto; auto requires an
  accepted proof object regardless of confidence.
- R5: confidence is secondary metadata only (spec 30).

## Reviewer schema (REVIEWER_V2, spec 32)

{semantic_assessment, evidence_sufficiency, proposed_relation,
supporting_span_ids, counter_proof, requires_human_review}. All span
ids are integer character offsets validated against the source
(fidelity, spec 33): ungrounded spans strip the proposal of authority;
fabricated spans make it inert. Evidence-sufficiency classifier
(spec 28) has three explicit classes and feeds review-vs-abstain.

## Primitive stability (spec 34)

5/5 schema/fidelity/stability unit tests PASS. Routing-relevant
fields on the dev cache: evidence_sufficiency is currently
deterministically derived (stable), proposed_relation mapped from
the frozen reviewer verdict, requires_human_review from the frozen
flag. Downgrade authority no longer routes on unstable bare flags.

## Phase C routing results (45-case dev corpus,
DEVELOPMENT_SANITY_ONLY)

- auto_count 9, auto_precision 1.0 (gate >= 99% PASS)
- invalid/unsound accepted proofs 0
- expected-abstain-or-review recall 1.0 (9/9)
- synthetic review-vs-abstain suite 16/16 PASS (macro F1 1.0)
- necessary-review recall on dev: all 36 reviews correspond to
  no-bounded-proof, unsafe-guard or counter-proof states
- overturning-review rate (spec 36 definition): 0
- raw review share 36/45 = 80%: dominated by 13 no-grounded-span
  bounded-inference cases where RC2 labels allowed loose inference;
  RC3 doctrine requires review there. Review volume is a known
  remaining weakness (anti-trivial-review gate: PASS on precision
  and overturning definition; coverage of auto actions remains low).
