# Historical integrity / incident record

Task: NAV-EXPLORE-RC3_3-GATE-CONSUMPTION-NUMERIC-COVERAGE

## Incident carried forward

During RC3.2, the file
rc3-1-support-boundary/baseline-results.json was accidentally
overwritten and later restored headline-only. It is therefore NOT
byte-identical historical provenance.

Status: HISTORICAL_ARTIFACT_RECONSTRUCTED_NONAUTHORITATIVE

This task does not use that reconstructed file as SHA-authoritative
provenance. Authoritative provenance for prior states is taken from
frozen manifests, recorded summaries, immutable task reports, and
captured post-change artifacts.

## Immutability rules honored in this task

- RC2 release candidate, manifests, predictions, freezes, official
  score and its freeze: untouched.
- RC2 blind V4 set and answer artifacts: untouched.
- RC3 / RC3.1 / RC3.2 task directories: untouched (writes only in the
  RC3.3 task directory; see write-sandbox-report.md).
- Sealed 60-case validation
  rc3-1-proof-semantics/corpus/validation-answer-key.sealed:
  never decrypted, never opened, never executed, never scored.
  Rehashed before implementation; expected SHA256:
  15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159.
- No new blind set is built in this task. No certification is run.
