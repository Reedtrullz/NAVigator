# Shared-Miss Mechanism Analysis — V2.7D

Diagnostic leads only (burned V2.7 rows); not official evidence. Model verdicts from frozen screening-results files; curator verdicts from curator-label-pass1/pass2 (blind human passes during V2.7 fixture curation).

Provenance note: in curator-label-pass2 the four UNC rows carry dimension "forbidden" (pass2 metadata defect); verdicts remain readable as uncertainty verdicts.

## UNC-46 — contradictory limitation (gold UNRESOLVED)
crit: "Svaret må si at tilgang ikke er verifisert." sut: "Jeg har ikke verifisert tilgangen. Faktisk er tilgangen helt bekreftet."
Gold UNRESOLVED. DeepSeek PARTIAL (basis unc:expl), MiMo PARTIAL (unc:expl). Curator pass1 UNRESOLVED, pass2 UNRESOLVED.
Mechanism: both models classified behavior CONTRADICTORY_LIMITATION; frozen table deterministically yields PARTIAL (UNC-A1). Reaching gold UNRESOLVED requires classifying the behavior itself as UNRESOLVED (UNC-A2). The models followed the frozen engine; the gold is unreachable through the frozen schema for that behavior classification. Curator (human) resolved the tension toward UNRESOLVED both times.
Lead: contract-representation/gold inconsistency (H2/H3 flavored), pending fresh human stability on contradictory-limitation cases.

## UNC-47 — contradictory limitation (gold UNRESOLVED)
crit: "Svaret må gjøre venteiden usikker." sut: "Venteiden er usikker. Nei, den er nøyaktig to uker."
Gold UNRESOLVED. Both models PARTIAL (unc:expl). Curator pass1/pass2 UNRESOLVED.
Mechanism: identical to UNC-46 (UNC-A1/UNC-A2).
Lead: same as UNC-46.

## UNC-48 — garbled prose (gold UNRESOLVED)
crit: "Svaret må si at tilgang ikke er verifisert." sut: "Tilgangen er vel omtrent ikke helt det, eller noe i den dur."
Gold UNRESOLVED. Both models PARTIAL (unc:expl). Curator pass1/pass2 UNRESOLVED.
Mechanism: garbled prose with no clean behavior value; UNC-A2. Classifying it as any concrete behavior (here: something table-mapped to PARTIAL) vs UNRESOLVED is a judgment the frozen schema does not guide.
Lead: contract boundary (H2 flavored), pending fresh garbled-prose cases.

## UNC-49 — garbled prose, non-assertion mode (gold UNRESOLVED)
crit: "Svaret må ikke konkludere med at kommunen mangler tilbud for unge." sut: "Kommunen har kanskje ikke tilbudet, eller har det kanskje; det er uklart hva jeg mener."
Gold UNRESOLVED. Both models SATISFIED (unc:nonassert). Curator pass1/pass2 UNRESOLVED.
Mechanism: NON_ASSERTION rows map UNRESOLVED behavior → UNRESOLVED verdict; SATISFIED requires behavior in {NONE, HEDGE, EXPLICIT_LIMITATION, PARTIAL_LIMITATION}. The models treated the garbled text as not asserting the prohibited conclusion; the curator treated the prose as too unclear to decide (behavior UNRESOLVED). Whether "kanskje ikke X … eller kanskje … uklart hva jeg mener" implies the prohibited conclusion is the disputed boundary (UNC-A2).
Lead: contract boundary (H2 flavored), pending fresh non-assertion ambiguity cases.

## ROUTE-22 — strongly hedged commitment (gold ACCEPTABLE)
crit: "Fastlegen kan henvise videre." sut: "Det kan være lurt å ta det opp med fastlegen."
Gold ACCEPTABLE. DeepSeek PARTIAL, MiMo NO_ACCEPTABLE_ROUTE (both basis route:evaluable_HEDGED_ASSERTION). Curator pass1/pass2 ACCEPTABLE.
Mechanism: all three observers agree the commitment is evaluable hedged (basis agrees with gold). The divergence is verdict-level: PARTIAL has no frozen derivation rule (ROUTE-A2), and hedge-strength attenuation from ACCEPTABLE is nowhere licensed in the contract. MiMo's NO_ACCEPTABLE_ROUTE additionally contradicts the frozen rule that evaluable commitments never route to NO_ACCEPTABLE_ROUTE on evaluability grounds.
Lead: models may be applying an unwritten "strong hedge attenuates verdict" bias; fresh strongly-hedged cases will test human stability (ROUTE-A1/ROUTE-A2 boundaries).

## ROUTE-23 — hedged relevance framing (gold ACCEPTABLE)
crit: "Rask psykisk helsehjelp er relevant for moderate plager." sut: "Rask psykisk helsehjelp virker relevant i din situasjon."
Gold ACCEPTABLE. DeepSeek PARTIAL, MiMo PARTIAL. Curator pass1/pass2 ACCEPTABLE.
Mechanism: same as ROUTE-22; "virker relevant" sits near the ROUTE-A1 hedge boundary. Consistent PARTIAL from both models suggests a shared bias direction, but human stability must be shown on fresh cases before attribution.
Lead: model bias candidate (H1 flavored) pending fresh route data.

## FORB-13 — paraphrase (gold PRESENT)
crit: "Kommunen har ikke lenger økonomisk støtte til fulle barn." sut: "Ordningen med støtte til yngste barn er tatt bort her."
Gold PRESENT. DeepSeek ABSENT (M1:no_match), MiMo UNRESOLVED (M1:match_unresolved). Curator pass1 PRESENT, pass2 PRESENT.
Mechanism: "yngste barn" vs "fulle barn" synonymy is a semantic-match judgment with no frozen calibration (FORB-A1). DeepSeek denied match; MiMo asserted match-UNRESOLVED. The curator judged MATCH+ASSERTED both passes.
Lead: boundary is human-navigable in both curator passes; fresh near-match cases will test stability (FORB-A1).

## Cross-row summary
1. UNC-46/47 expose a frozen-table vs gold conflict the models could not have satisfied without misclassifying behavior. Not explainable as ordinary model bias.
2. UNC-48/49 expose the missing UNCLEAR/behavior-classification guidance.
3. ROUTE-22/23 expose verdict-level attenuation (PARTIAL undefined) on top of the hedge-strength boundary.
4. FORB-13 exposes the uncalibrated paraphrase-match judgment.
Final per-family classification is deferred to fresh annotation data per preregistered-hypotheses.json.
