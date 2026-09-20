# RC-06 Assessment (Renderer, Wave 2)

## Status: STILL_REQUIRED (UX-dominant, one semantically material residue)

## UX_ONLY (dominant)
- 103/120 cases emit 2+ "Nasjonal informasjon" blocks (duplicated/repeated national information; excessive answer length).
- Repeated claims and structured/rendered mismatch (structured routes absent while prose asserts routes) persist.

## SEMANTICALLY_MATERIAL
- DIS-100 forbidden FAIL: contamination-shaped text ("Fant ingen registrerte kommunale tilbud...") lives inside cross-contaminated national-information blocks. Renderer-level source-block scoping/deduplication would reduce this failure surface, though the deterministic lexical verdict itself is a measurement-lane matter.
- The structured/prose divergence (routes: [] while prose asserts routes) is not just cosmetic: it is the R3 trigger surface. Route construction (Wave 3 primary) removes most of the divergence; renderer dedup is complementary cleanup.

## Recommendation
Renderer cleanup should not outrank route correctness. Schedule RC-06 after Wave-3 route semantics; treat dedup as UX improvement with a targeted exception for source-block scoping that feeds forbidden-claim text.
