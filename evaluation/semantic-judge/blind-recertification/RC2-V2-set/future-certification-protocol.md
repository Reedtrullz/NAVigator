# Future certification protocol - two-phase, prediction-freeze firewall

Set: NAV-EXPLORE-RC2-BLIND-V2. Release candidate: NAV-EXPLORE-EVALUATOR-RC2 (frozen, hash-verified).

## Phase 1 (agent must NOT have the blind key)

1. Verify RC2 hashes: from evaluation/semantic-judge/ run shasum -a 256 -c blind-recertification/RC2-V2-set/rc2-hashes-before.txt and record RC2_UNCHANGED.
2. Run RC2 exactly on blind-cases.json (160 CORE cases, set NAV-EXPLORE-RC2-BLIND-V2). Never on the reserve in this pass. Never on RC1 or any other set.
3. Write RC2-predictions.json plus prediction SHA-256 and timestamp.
4. Freeze predictions: STATUS = PREDICTIONS_FROZEN_BEFORE_KEY.
5. Stop and report the prediction hash.

**The Phase 1 agent must not be given the blind key (BLIND_RC2_V2_KEY) under any circumstances (spec 61).** The user must not paste the key into the Phase 1 prompt.

## Phase 2 (only after prediction freeze)

6. The user provides BLIND_RC2_V2_KEY in a separate message. The agent asks for it as a separate message after predictions are frozen and never includes it in any prompt, log, report, or file.
7. Decrypt answer-key.sealed: AES-256-GCM, urlsafe-base64 nonce and ciphertext (pad with ==), associated data = the envelope's associated_data field, which binds the SHA-256 of the exact blind-cases.json bytes.
8. Score the frozen predictions against the pre-registered metrics in certification-metrics.md. Wilson 95 percent intervals on central proportions; raw counts decide hard-gate failures.
9. Report aggregate results. No post-hoc label edits; potential label errors are flagged separately from the frozen score.

## Firewall rules

- No label inspection, similarity search, or answer-key access before prediction freeze.
- No set modification after sealing; a construction bug requires a V3 set, never an edit of V2.
- Reserve cases are not scored in the first certification pass.
- If RC2 is executed against blind cases before Phase 1 formalities, the set is COMPROMISED and must not be used for certification.
- No evaluator, fusion, reviewer, quote-aligner, Tier-1, or KB changes between freeze and scoring.
