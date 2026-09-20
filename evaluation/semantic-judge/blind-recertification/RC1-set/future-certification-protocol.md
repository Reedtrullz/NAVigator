# Future certification protocol - two-phase, prediction-freeze firewall

## Phase 1 (agent must NOT have the blind key)

1. Verify RC1 hashes: run sha256sum -c release-candidate/hashes.txt and record RC1_UNCHANGED.
2. Run RC1 exactly on blind-cases.json (NAV-EXPLORE-RC1-BLIND-V1).
3. Write RC1-predictions.json plus prediction SHA-256 and timestamp.
4. Freeze predictions: STATUS = PREDICTIONS_FROZEN_BEFORE_KEY.
5. Stop and report the prediction hash.

## Phase 2 (only after prediction freeze)

6. The user provides BLIND_RC1_KEY in a separate message. The user must NOT paste the key into the certification prompt itself; the next agent asks for it as a separate message after predictions are frozen.
7. Decrypt answer-key.sealed (AES-256-GCM, associated data = SHA-256 of blind-cases.json).
8. Score against the pre-registered metrics in certification-metrics.md.
9. Report aggregate results; no post-hoc label edits.

## Firewall rules

- No label inspection, similarity search, or answer-key access before prediction freeze.
- No set modification after sealing; a construction bug requires a V2 set, never an edit of V1.
- Reserve cases are not scored in the first certification pass.
- If RC1 is accidentally executed against blind cases before Phase 1 formalities, the set is COMPROMISED and must not be used.
