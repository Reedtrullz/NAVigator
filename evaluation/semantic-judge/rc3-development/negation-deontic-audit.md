# Negation / Deontic Root-Cause Audit (spec 14-18)

Scope: the 3 RC2 unsound accepted autos plus generalized engine
negation/deontic failure classes. Per spec 42: no RC2B case IDs in
runtime code; IDs here are diagnosis-only (DOCUMENTATION provenance).

## The 3 unsound accepted autos (RC2 proof-audit.json)

All three were engine auto-SUPPORTED where the sealed proof-safe label
was not SUPPORTED ("exceeds_proof_safe").

1. Class NEGATION_AFTER_ALIGNED_SPAN + CLAUSE_SCOPE. Source states
   childrens income and wealth are NOT counted; claim asserts they
   are counted. The aligned fragment matched the claim text; the
   polarity-reversing negation lived in the adjacent clause of the
   same bullet. RC2 validated the proof on the lexical fragment alone.
   RC3: clause-context guard fires (negation/subject overlap in the
   adjacent sentence) -> ENGINE_UNSAFE -> REVIEW_REQUIRED. Verified.

2. Class DEONTIC_QUALIFIER_OUTSIDE_MATCH / MODALITY_SHIFT. Claim
   asserts discretion ("kan selv velge aa ignorere") where the source
   imposes obligation ("skal kontakte") with an alternatives clause.
   RC2 matched the actor/topic fragment and auto-supported.
   RC3: clause-context guard fires (deontic modality shift between
   claim sentence and aligned/adjacent sentence) -> ENGINE_UNSAFE ->
   REVIEW_REQUIRED. Verified.

3. Class SENTENCE_SCOPE / EXCEPTION_SCOPE (LABEL_SENSITIVITY_ONLY).
   Distribution rule ("delt bosted ... inntekt i stedet for
   samvaersfradrag") is supported by an implied calculation-rule
   sentence the packet expresses indirectly across clauses. Under the
   official sealed label this case stays an RC2 official-history miss;
   per spec 44 the engine is NOT tuned to the alternate reading. RC3
   routes it AUTO_SUPPORTED from an accepted grounded proof; the
   structural validator accepts it and the soundness audit finds no
   polarity/modality violation in the aligned sentence.

## Generalized failure classes (spec 14 taxonomy)

- NEGATION_AFTER_ALIGNED_SPAN: fixed by full-clause binding guard.
- DEONTIC_QUALIFIER_OUTSIDE_MATCH: fixed by deontic marker guard
  (must/shall vs may/cannot/ikke krav om) with subject overlap.
- SENTENCE_SCOPE: adjacent-sentence guard with 6-char stem subject
  overlap; fail-closed to review.
- CLAUSE_SCOPE: clause-context guard runs on the aligned sentence and
  the adjacent sentence; no bare +-N token window (spec 16).
- EXCEPTION_SCOPE: hovedregel/exception qualifier check inside
  contra spans; bare/kun/enten exhaustivity marker required before
  an exclusion-based CONTRA can auto.
- MODALITY_SHIFT: deontic normalization distinguishes must/shall,
  may, may-have-right, usually, only-if, cannot, not-required,
  exception, individual assessment (spec 17); modality is never
  collapsed into polarity.
- OTHER: empty-span CONTRA now requires a deterministic comparator
  rule (numeric conflict, incompatible dates, negated-object conflict,
  exhaustive list) plus a positive contra span; otherwise
  NO_POSITIVE_CONTRA_SPAN -> review.

## Negation window doctrine (spec 16)

Sentence/clause boundaries via the frozen RC2 sentence splitter,
adjacency by source offset, subject-overlap by 6-char stems. Regex is
used only for marker detection inside already-selected sentences;
limitation documented: markers outside the two-sentence window are
invisible, and the failure mode is fail-closed (REVIEW), never an
unsupported auto.

## Regression status

11/11 generalized negation/deontic regressions PASS (tests/
test_negation_deontic.py, includes support-phrase-followed-by-
negation, nested exception, kan-vs-skal, ikke krav om, bare dersom,
positive clause + negative exception, cross-clause qualifier).
0 unsound accepted proofs on the dev corpus and 0 invalid accepted
proofs on the burned V4 shadow.
