# RC3 Architecture Contract

Six separated stages (spec 6). No single confidence score represents all.

1. CLAIM DECOMPOSITION (DECOMPOSITION_V1): claim-logical, canonical, stable
   atom IDs, before any evidence judgment (rc3_engine/decomposition.py).
2. EVIDENCE RELATION EXTRACTION: frozen RC2 engine (v0.2) per atom,
   unchanged; RC3 adds context validation, no edits to frozen files.
3. DETERMINISTIC PROOF (PROOF_ENGINE_RC3): wrapper
   rc3_engine/engine_rc3.py producing explicit proof states:
   ENGINE_PROOF_ACCEPTED | ENGINE_NO_PROOF | ENGINE_CONFLICT | ENGINE_UNSAFE.
4. SEMANTIC REVIEWER (REVIEWER_V2): structured output only; reviewer
   proposals are evidence, not authority (rc3_engine/reviewer_v2.py schema +
   validator; frozen hybrid/reviewer.py remains the transport).
5. PROOF ARBITRATION (ARBITRATION_V2): monotonic, rc3_engine/arbitration.py.
   A validated engine proof cannot be reversed by reviewer verdict/confidence
   alone; reversal requires a valid COUNTER_PROOF (grounded spans + proof
   doctrine + structural validity + soundness). Reviewer without counter-proof
   may confirm, request review, or add uncertainty metadata - never flip.
   NO_PROOF cannot become auto from confidence; auto requires an accepted
   proof object.
6. PRODUCT ROUTING (PRODUCT_ROUTING_V2): frozen table in
   rc3_engine/routing.py:
   valid sound SUPPORT proof -> AUTO_SUPPORTED
   valid sound CONTRADICTION proof -> AUTO_CONTRADICTED
   evidence genuinely insufficient -> ABSTAIN_INSUFFICIENT
   relevant evidence, no bounded proof -> REVIEW_REQUIRED
   conflict/ambiguous proof -> REVIEW_REQUIRED
   No generic reviewer confidence alone grants auto.

Proof doctrine is unchanged (absence != contradiction; positive proof
obligation for all contradiction paths). The context guard adds source-text
scan obligations; it never converts absence of support into contradiction.

