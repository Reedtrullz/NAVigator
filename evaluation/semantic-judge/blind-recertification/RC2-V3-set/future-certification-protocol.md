# Future Certification Protocol - RC2 Blind V3

Two-phase prediction-freeze firewall (spec 41-42). RC1 remains RC1_NOT_CERTIFIED regardless of the outcome; this protocol certifies RC2 only.

## Phase 1 - keyless run

1. Verify frozen RC2: shasum -a 256 -c evaluation/semantic-judge/blind-recertification/RC2-V2-set/rc2-hashes-before.txt from the repo root. All 11 must be OK before anything runs.
2. Assert the V3 key is absent: not in the run context, not on disk, not in any environment or prompt. The operator must not have the key in the session that executes predictions.
3. Execute RC2 on the 160 CORE cases only (blind-cases.json). No reserve cases, no live dialog, no KB or engine changes.
4. Freeze predictions: write predictions + per-case outputs, compute SHA-256, record it.
5. STOP. No scoring, no label access, no threshold discussion.

## Phase 2 - scoring after freeze

1. Only after the Phase 1 prediction SHA is recorded: the user supplies the V3 key in-session (memory-only).
2. Decrypt answer-key.sealed (AES-256-GCM; AAD = UTF-8 bytes of the blind-cases.json SHA-256 hex string; the envelope associated_data field is urlsafe-b64 of the raw 32-byte digest).
3. Score against certification-metrics.md exactly as pre-registered. Publish the certification report and the official score SHA.

## Key-handling rules

The key was delivered exactly once, in the construction final message. It is memory-only: never written to disk, repo, Obsidian, reports, or shell history. If the key is lost, the set is unrecoverable as a certification instrument; the correct response is a fresh construction under the governing spec, never re-running seal_key.py against the sealed set (that generates a new key and rewrites the envelope).

## Firewall rationale

The agent or operator that executes Phase 1 must not hold label knowledge; the prediction freeze (SHA recorded before the key exists in the session) is what makes the run blind in the auditable sense. V2's burned set showed why: once labels and predictions share a context, no post-hoc gate can prove blindness.
