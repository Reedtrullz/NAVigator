# Historical Integrity

## Verified before work (integrity-start.json)

| Artifact | SHA-256 | Status |
|---|---|---|
| RC3.3.1 candidate manifest | c66c14a639afdcf98bc853f4fd0e8a4649c4f59aa16a65993d3390dce15fbdee | OK |
| Candidate components (per manifest) | all recorded | components_ok=true |
| Existing 30-case micro-validation | c231979d969f945184adaac9ad6fdd0b193c545dda96415b62facd57e4cfa20b | OK |
| Large sealed 60-case validation | 15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159 | OK |

## Verified after work

integrity_check.py re-run at terminal state: INTEGRITY_START_OK,
same three SHAs, components_ok=true. The 30-case SHA was additionally
verified immediately before the final passes.

HISTORICAL_FILES_MODIFIED = 0.

## Candidate execution

The candidate runtime was never imported, never executed, and never
received any case content in any context. 0 of 30 cases predicted.
No prediction file exists.

## Quarantine

Old (burned) annotations were used only to understand the earlier
contract's ambiguity during setup, before the contract was frozen. None of
the four new annotation passes received old labels, disagreements,
rationales, identities, or prior distributions; annotate.py sends only the
case, the contract, and the schema.

## Large validation

The 60-case sealed validation file was never opened, read, or unsealed;
only its SHA was computed. It remains untouched.
