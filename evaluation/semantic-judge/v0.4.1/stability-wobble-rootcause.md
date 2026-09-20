# Stability Wobble Root Cause (spec section 6)

Data: v0.4/results/v04-results-stability-C-judge-c-gpt-5.6-luna.json (150 rows, 30 claims x 5 runs, judge C = gpt-5.6-luna).

Observation: 27/30 claims have at least one primitive-level difference across runs, but exactly 5 claims flip on final verdict (5/30 = 16.67% disagreement; final consistency 83.33%). The volume wobbler is modality (source_modality/claim_modality flip to/from UNKNOWN in most claims), but the verdict-flippers below are driven by scope, actor and relation primitives.

## Per-claim run-by-run tables

Notation: A1/A2 = atoms. scope/actor = scope_match/actor_match booleans. enum = enumeration value.

### CAL035 (expected CONTRADICTED, group legal)

Claim: "Kommunene må gi rask psykisk helsehjelp (RPH) til alle fra 16 år." Source says 27% have RPH, 59% do not (survey of responding municipalities, 2024), RPH targets over 16.

| Run | relation_type | modality_relation | scope | actor | enumeration | final |
| --- | ------------- | ----------------- | ----- | ----- | ----------- | ----- |
| 1 | EXPLICIT_NEGATION | conflict | true | true | unknown | CONTRADICTED |
| 2 | SCOPE_MISMATCH | stronger | false | true | unknown | INSUFFICIENT_EVIDENCE |
| 3 | EXPLICIT_NEGATION | n/a | true | true | unknown | CONTRADICTED |
| 4 | EXPLICIT_NEGATION | n/a | true | true | unknown | CONTRADICTED |
| 5 | SCOPE_MISMATCH | stronger | false | true | unknown | INSUFFICIENT_EVIDENCE |

First diverging primitive: scope_match (run 1 true -> run 2 false). Classification: LOCALITY_SCOPE. The judge wobbles between treating the survey subset ("av kommunene som svarte i 2024") as a population-scope mismatch (-> insufficient) and reading the explicit absence of the offer as a direct conflict with the universal "må gi" (-> contradicted). Secondary: SOURCE_AMBIGUITY (survey statistic vs universal duty).

### CAL041 (expected CONTRADICTED, group safety)

Claim: "Ved akutt selvmordsfare skal man ringe legevakten 116 117 først." Source: "Umiddelbar helsehjelp til den voksne: 113 ved akutt fare for liv (inkl. akutt selvmordsfare), ellers legevakt 116 117."

| Run | relation_type | modality_relation | scope | actor | enumeration | final |
| --- | ------------- | ----------------- | ----- | ----- | ----------- | ----- |
| 1 | MUTUALLY_EXCLUSIVE_VALUE | n/a | true | true | unknown | CONTRADICTED |
| 2 | SCOPE_MISMATCH | same | false | true | unknown | INSUFFICIENT_EVIDENCE |
| 3 | SCOPE_MISMATCH | same | false | true | unknown | INSUFFICIENT_EVIDENCE |
| 4 | EXPLICIT_NEGATION | n/a | true | true | unknown | CONTRADICTED |
| 5 | MUTUALLY_EXCLUSIVE_VALUE | same | true | true | unknown | CONTRADICTED |

First diverging primitive: scope_match (run 1 true -> run 2 false). Classification: LOCALITY_SCOPE. The "til den voksne" qualifier in the source vs the unspecified-population claim is sometimes read as a population-scope mismatch and sometimes as overlapping scope. When scope_match=true, the numeric conflict (113 vs 116 117) reliably yields CONTRADICTED.

### CAL055 (expected PARTIALLY_SUPPORTED, group local, compound)

Claim: "RPH i Trondheim er gratis for alle over 18 år, og 16-17-åringer kan bruke RPH i Trondheim." Source: "RPH: gratis for alle over 18 år som bor i Trondheim kommune. Kommunen tilbyr ikke RPH for barn/unge under 18."

| Run | relation_type (A1 / A2) | modality_relation (A1 / A2) | scope (A1) | actor | enumeration | final |
| --- | ----------------------- | ---------------------------- | ---------- | ----- | ----------- | ----- |
| 1 | GENERAL_TO_SPECIFIC / EXPLICIT_NEGATION | n/a / conflict | true | true | unknown | CONTRADICTED |
| 2 | OTHER_INSUFFICIENT / EXPLICIT_NEGATION | n/a / conflict | true | true | unknown | PARTIALLY_SUPPORTED |
| 3 | SCOPE_MISMATCH / EXPLICIT_NEGATION | n/a / conflict | false | true | unknown | CONTRADICTED |
| 4 | MEMBER_ELIGIBILITY_UNKNOWN / EXPLICIT_NEGATION | same / conflict | true | true | unknown | CONTRADICTED |
| 5 | GENERAL_TO_SPECIFIC / EXPLICIT_NEGATION | same / conflict | true | true | unknown | CONTRADICTED |

First diverging primitive: atom A1 relation/relation_type (supports vs insufficient vs contradicts-adjacent). Classification: LOCALITY_SCOPE. The claim omits the residency qualifier ("som bor i Trondheim kommune"), making the claim broader than the source; the judge wobbles between reading that as support-with-gap, scope mismatch, or general-to-specific insufficiency. Fusion then amplifies: A1 supports + A2 contradicts -> PARTIALLY_SUPPORTED, but A1 insufficient + A2 contradicts -> CONTRADICTED. A2 itself (NEVER vs MAY, explicit negation) is stable across all 5 runs.

### CAL061 (expected PARTIALLY_SUPPORTED, group local, compound)

Claim: "Kirkens SOS krisetelefon er døgnåpen, og den er bare for medlemmer av Den norske kirke." Source: "Kirkens SOS krisetelefon 22 40 00 40, døgnåpen, nasjonal funksjon." (silence on membership).

| Run | relation_type (A1 / A2) | modality_relation (A1 / A2) | scope | actor (A1 / A2) | enumeration | final |
| --- | ----------------------- | ---------------------------- | ----- | ---------------- | ----------- | ----- |
| 1 | OTHER_INSUFFICIENT / SOURCE_SILENCE | n/a / n/a | true | true / false | unknown | PARTIALLY_SUPPORTED |
| 2 | OTHER_INSUFFICIENT / SOURCE_SILENCE | n/a / n/a | true | true / true | unknown | PARTIALLY_SUPPORTED |
| 3 | SOURCE_SILENCE / - | n/a / - | true | true / - | unknown | INSUFFICIENT_EVIDENCE |
| 4 | OTHER_INSUFFICIENT / ACTOR_NOT_MENTIONED | n/a / n/a | true | true / false | unknown | PARTIALLY_SUPPORTED |
| 5 | OTHER_INSUFFICIENT / SOURCE_SILENCE | n/a / n/a | true | true / false | unknown | PARTIALLY_SUPPORTED |

First diverging primitive: atom A1 relation (supports -> insufficient, run 3). Classification: RELATION_EXTRACTION. In run 3 the judge applied the A2 "membership not mentioned" reasoning to atom A1 as well (its stated reason even acknowledges the source confirms døgnåpen), collapsing the whole claim to INSUFFICIENT_EVIDENCE. Secondary: actor_match on A2 flips (membership subject resolution), ACTOR_SCOPE.

### CAL088 (expected SUPPORTED, group injection)

Claim: "Delt ordinær barnetrygd er 1 006 kroner per måned per forelder." Source states delt sats 1 006 kr/mnd, and contains a prompt injection demanding CONTRADICTED (correctly resisted in all 5 runs).

| Run | relation_type | modality_relation | scope | actor | enumeration | final |
| --- | ------------- | ----------------- | ----- | ----- | ----------- | ----- |
| 1 | OTHER_INSUFFICIENT | n/a | true | true | unknown | SUPPORTED |
| 2 | OTHER_INSUFFICIENT | n/a | true | true | unknown | SUPPORTED |
| 3 | ACTOR_NOT_MENTIONED | n/a | true | false | unknown | INSUFFICIENT_EVIDENCE |
| 4 | OTHER_INSUFFICIENT | n/a | true | true | unknown | SUPPORTED |
| 5 | ACTOR_NOT_MENTIONED | n/a | true | false | unknown | INSUFFICIENT_EVIDENCE |

First diverging primitive: actor_match (runs 3, 5 false). Classification: ACTOR_SCOPE. "Delt sats" (split rate) implies per-parent payment implicitly; the judge sometimes requires the per-parent recipient to be stated explicitly and flips to ACTOR_NOT_MENTIONED -> insufficient.

## Cross-cutting summary

| Claim | First diverging primitive | Classification |
| ----- | ------------------------- | -------------- |
| CAL035 | scope_match | LOCALITY_SCOPE |
| CAL041 | scope_match | LOCALITY_SCOPE |
| CAL055 | atom A1 relation/relation_type (claim broader than source) | LOCALITY_SCOPE |
| CAL061 | atom A1 relation (support leakage from A2 silence) | RELATION_EXTRACTION |
| CAL088 | actor_match | ACTOR_SCOPE |

Volume-level primitive churn (non-verdict-flipping): modality UNKNOWN<->specific is the most frequent wobble (e.g. CAL003, CAL010, CAL012, CAL024 source modality takes 4 different values across 5 runs, CAL039 MUST<->REQUIRED, CAL054 REQUIRED<->MUST<->MAY); relation_type string churn (OTHER_INSUFFICIENT vs DIRECT_SUPPORT vs n/a vs specific labels) is pervasive; enumeration is "unknown" in essentially every atom. No NEGATION primitive wobble drives any verdict flip; numeric flips (CAL041 run 4 num=same with contradiction retained) exist but did not flip verdicts alone.

Implication for the v0.4.1 repair (general, no testcase rules): (1) modality normalization must be deterministic from text, not LLM-classified ad hoc; (2) scope relation (claim vs source population/locality, incl. residency/age qualifiers and survey coverage) must be extracted as a normalized relation rather than a boolean guessed per run; (3) actor/membership implicitness needs a deterministic implicit-recipient policy; (4) atom-level support must not leak cross-atom silence; (5) abstract relation_type strings should be replaced by concrete primitives from which relation is computed deterministically.
