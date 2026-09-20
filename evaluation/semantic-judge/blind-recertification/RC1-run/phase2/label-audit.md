# LABEL AUDIT - RC1 BLIND RECERTIFICATION PHASE 2

Question: are any RC1B answer-key labels plausibly wrong, independent of evaluator defects?

Method: all error rows where the reviewer accepted a proof (route "accepted") and the product outcome was wrong were re-read against the claim text, source span, atom verdicts, and the evaluation contract's own compound rule. Count: 5 cases.

## Case-by-case

- RC1B-0116: key CONTRADICTED on a compound claim; engine atom A1 INSUFFICIENT ("utferdes naar mekling er gjennomfoert"), atom A2 SUPPORTED ("gyldig i 12 maaneder"); reviewer PARTIAL 0.99 (one_atom_supported_one_contradicted). The contract's own partial rule (one atom supported + one contradicted) arguably fits better than full CONTRADICTED. Strong POTENTIAL_BLIND_LABEL_ERROR.
- RC1B-0165: key CONTRADICTED on "vedtatt" + "tradt i kraft per 30.08.2026" (adopted_but_not_in_force pattern); reviewer PARTIAL 0.98. Same one-atom-supported/one-contradicted structure; label plausibly should be PARTIALLY_SUPPORTED. Strong POTENTIAL_BLIND_LABEL_ERROR.
- RC1B-0143: key SUPPORTED; reviewer PARTIAL 0.95 ("egne telefonnumre per bydel" - source documents the service but district numbers are only partially evidenced). Borderline; either SUPPORTED or PARTIALLY_SUPPORTED is defensible. Weak label-error candidate.
- RC1B-0005: key SUPPORTED is correct; the failure is the evaluator numeric cross-amount bug (root cause 1). Not a label error.
- RC1B-0169: key REVIEW_REQUIRED is correct; the failure is the evaluator weak-contra rule (neg_object_conflict). Not a label error.

## Impact

- 2 strong candidates (RC1B-0116, RC1B-0165). If both labels were flipped to PARTIALLY_SUPPORTED, semantic and product accuracy would move from 79/120 (65.83%) to 81/120 (67.5%) and critical product from 37/60 to 39/60. Every threshold still fails; the verdict RC1_NOT_CERTIFIED is unchanged either way.
- No alternate score was computed and no score artifact was modified; the official score remains frozen at fff9b539b97d414389fbc6198d1ecbc92f546556bbc7374fdbbfa29d5ef93d72.
- The official answer key was not edited and must not be edited. Candidate flips are recorded here only; any relabeling decision belongs to the owner and would require a versioned key update outside this certification run.

## Verdict

LABEL_AUDIT: 2 strong potential label errors flagged (RC1B-0116, RC1B-0165), 1 borderline (RC1B-0143), 2 evaluator-attributed (RC1B-0005, RC1B-0169). No alternate score computed. Certification verdict unaffected.
