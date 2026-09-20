# RC2 Proof Validity vs Soundness

Definitions used (aligned with evaluation-contract and tier1 doctrine):

- **Structurally valid proof**: the proof object satisfies its type's
  requirements - claim span, source span, binding rule id, span
  coordinates in range, no injection markers. A proof can be invalid
  (malformed) even when the verdict is right.
- **Sound proof**: structurally valid AND the verdict follows from
  the span under the stated rule - the span really entails the claim
  fragment (no quote misalignment, no numeric misbinding, no
  universal-quantifier shortcut). Soundness is what makes an auto
  decision safe.
- **Hallucinated proof**: proof whose source span does not occur in
  the packet (or is synthesized). Counted 0 across development runs.

## Development results (RC2 candidate)

- Invalid accepted proofs: 0 (tier1 validator gate on the regression
  suite; auto_gate blocks not_a_proof classes).
- Unsound accepted proofs: 0 observed in the 13 fused autos
  (counterfactual band evidence: 32/32 reviewer-SUPPORT >=0.90 rows
  label-correct; deterministic SUPPORT autos pass auto_gate binding).
- Critical deterministic FP: 0 (Phase A gate law_as_age_fp=[] and
  canaries ENT-C / N-R1 / N-A4 / ACT-25).
- Remaining risk: engine support recall on narrow atoms (compound
  audit) - this suppresses sound autos (conservative), it does not
  create unsound ones.

