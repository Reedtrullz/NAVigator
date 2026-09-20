# Future Certification Protocol

## Session

- Phase 1 (RC2 prediction run) must run in a fresh, isolated session that never
  saw construction, adjudication, or key material (spec 30-31).
- The V4 key must not appear in prompt, env, shell, repo, or Phase-1 conversation
  context. It is delivered once to the owner and used only afterwards to unseal
  `answer-key.sealed` for scoring.

## Phase-1 inputs

- Allowlist: `blind-cases.json`, `blind-cases.schema.json`, `blind-manifest.json`,
  `phase1-firewall-manifest.json`, plus the frozen RC2 runtime covered by
  `release-candidate/RC2/hashes.txt`.
- Forbidden: `answer-key.sealed`, `construction-audit.sealed`, `construction-v4/`,
  `RC2-V3-set/construction/`, `RC2-V3-set/pilot/`, and all other project docs.

## After Phase 1

1. Re-verify RC2 hashes: from `evaluation/semantic-judge/`, run
   `sha256sum -c release-candidate/RC2/hashes.txt`.
2. Unseal `answer-key.sealed` with the V4 key and verify the AAD convention
   before trusting contents: decrypt with AAD = UTF-8 bytes of the
   `blind-cases.json` SHA-256 hex string; the envelope `associated_data` field
   is urlsafe-b64 of those same hex-string bytes.
3. Score with the unchanged thresholds in `certification-metrics.md`.
4. Never reuse the V3 key; its SHA-256 fingerprint is registered as retired in
   `v4_qa.py`.

## Stop conditions (unchanged)

- Threshold tuning is not allowed. If a pure schema impossibility appears, stop
  and record it instead of silently changing a threshold.
- If RC2 hashes fail verification after Phase 1, the run is void.
