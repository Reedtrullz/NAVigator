# Future Generalization Protocol (G1/G2)

The snapshot has NEVER been executed against this holdout. Scoring is a
separate task and must follow this protocol exactly.

## G1 - fresh keyless session
1. New session without the key; verify runtime-snapshot hashes
   (runtime-snapshot/hashes.txt + manifest.sha256) and that
   generalization-cases.json sha256 equals
   3f22c19b9f48e748ed5b5aadd0f715430e914225fc2923edd0e953cf09e720d4.
2. Execute the snapshot on all 159 CORE cases exactly once.
3. Freeze all predictions (bytes + sha256) and runtime outcome ledger.
4. STOP. No scoring, no key access, no iteration. If any gate input
   looks wrong, report and stop; do not rerun selectively.

## G2 - after prediction freeze
1. Provide the key from the construction session final message.
2. Decrypt answer-key.sealed (AAD = ASCII bytes of the lowercase hex
   sha256 of generalization-cases.json; AES-256-GCM, 12-byte nonce).
3. Score with the preregistered policy in evaluation-metrics.md.
4. Report all metrics separately; no tuning between G1 and G2 or after.

## Rules
- No runtime changes in this cycle (spec 1/10). If the runtime changed
  since NAV-EXPLORE-RC3-GEN-SNAPSHOT-A, this holdout is invalid for it.
- No threshold search, prompt iteration, or variant selection against
  this set (spec 11).
- If the key is lost, the set is void for scoring; a new construction
  task must rebuild and reseal.
