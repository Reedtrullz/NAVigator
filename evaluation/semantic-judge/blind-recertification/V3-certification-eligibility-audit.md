# V3 Certification Eligibility Audit

Status: `SEALED_BUT_NOT_CERTIFICATION_ELIGIBLE` (never `COMPROMISED`).

## What held

- The V3 seal held: no key exposure, no unauthorized unsealing, no tampering.
- `RC2-V3-set/blind-cases.json` stayed byte-identical through V4 reuse
  (SHA-256 `ad4fc1008063e52fb004fcdf5a3e48c2ca0277c7cf6dd9251b04d43c3e29a36d`).

## Why V3 is not certification eligible

1. Plaintext leakage evidence: 16 per-case label-bearing files existed in
   plaintext under V3 construction/pilot surfaces before the V4 cleanup.
2. Incomplete atom key: V3 reported atom rows for only 10 adjudicated CORE cases,
   so the preregistered compound-atom accuracy could not be scored.

## Disposition

- The V3 key is RETIRED (SHA-256 fingerprint
  `7a3a1488afcc8287adc4ac295f535081cac6c5e98bda9b01afe40d8122a233e4`); never reuse
  it for any future set.
- V4 is the certification path: byte-identical blind cases, complete atom key,
  sealed construction evidence, full leak cleanup.
