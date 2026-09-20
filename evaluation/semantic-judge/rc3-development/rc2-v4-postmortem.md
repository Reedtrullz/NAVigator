# RC2-V4 Postmortem (forensic; burned data, non-certification)

Baseline frozen from official Phase 2B scoring (official-score SHA
e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2, re-verified
this session against the artifact on disk). RC2_NOT_CERTIFIED stands permanently.

## Baseline (historical, NOT an RC3 target set)

| Metric | Value |
|---|---|
| semantic | 53/160 = 33.12% |
| proof-safe | 40/160 = 25.00% |
| product | 68/160 = 42.50% |
| combined auto precision | 14/17 = 82.35% |
| critical product | 16/40 = 40% |
| compound atom | 36/141 = 25.53% |
| compound product | 46/62 = 74.19% |
| invalid/unsound accepted proofs | 3 |
| hallucinated proofs | 0 |
| critical unsafe autos | 0 |
| runtime failures | 0 |
| review predictions | 143/160 |
| review precision | 37.76% |
| review recall | 98.18% |
| expected abstain missed | 26/26 |

## Verified root causes (mechanical, from phase2 artifacts + engine reruns)

1. PROOF-BOUND UNSOUNDNESS: all 3 invalid accepted autos are engine
   auto-SUPPORTED via quote-alignment support where the polarity flip lives
   outside the aligned fragment but inside the same clause/sentence or the
   adjacent sentence of the same source. Rerun of the frozen engine reproduces
   all three: the aligned sentence wins lexical support while
   (a) a neighboring sentence with the same subject states the negated
   predicate ("er ikke med"), (b) the aligned clause carries an obligation
   ("skal kontakte") while the claim asserts free choice to do the opposite
   ("kan velge aa ignorere"), and (c) a general-rule qualifier ("som
   hovedregel") sits in the same sentence outside the matched fragment.
2. REVIEW/ABSTAIN COLLAPSE: the fusion layer has exactly two routes
   (auto / REVIEW_REQUIRED). No ABSTAIN_INSUFFICIENT product action exists at
   runtime, so all 26 genuine-insufficiency cases were review-routed.
3. REVIEWER AUTHORITY: fusion auto-accepts reviewer SUPPORT at confidence
   >= 0.90 (a confidence mix), and reviewer output can otherwise flip or
   discard a deterministic engine proof without a counter-proof obligation.
4. COMPOUND DECOMPOSITION: 35/62 compound cases predicted fewer atoms than
   the sealed canonical decomposition (0 extra atoms). Decomposition is
   evidence-driven, not claim-logical.
5. SCORER DISPLAY: semantic confusion display dropped predicted-review cells
   (counter-key mismatch); metrics unaffected. Analytics-only fix in RC3.

## Failure taxonomy (generalized, no per-case coding)

- NEGATION_AFTER_ALIGNED_SPAN: negation in the same sentence/adjacent
  sentence outside the matched fragment (mechanism 1a).
- DEONTIC_QUALIFIER_OUTSIDE_MATCH: obligation/permission mismatch across the
  aligned boundary (mechanism 1b).
- QUALIFIER_OUTSIDE_MATCH: hovedregel/unntak/bare-dersom qualifiers outside
  the matched fragment (mechanism 1c).
- SENTENCE_SCOPE / CLAUSE_SCOPE: polarity scoped to one clause only.
- LABEL_SENSITIVITY_ONLY: the case 0030 label itself is disputed in phase2
  label-audit; official label retained; engine fix targets the general
  qualifier mechanism, not the alternate label.

Case-level identity for mechanisms 1a-1c lives in the phase2 proof-audit
artifact; this postmortem intentionally codes mechanisms, not per-case rules.

