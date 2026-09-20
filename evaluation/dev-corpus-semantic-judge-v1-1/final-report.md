# Final Report: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_1-ROUTE-CONTRACT-REPAIR

## Grunnlag og integritet (1-7)

1. Task ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_1-ROUTE-CONTRACT-REPAIR
2. Prior semantic judge status: DEV_CORPUS_SEMANTIC_JUDGE_V1_NOT_READY (uendret)
3. Corpus manifest SHA: 9c265731e6e17ea54844b6db646dac4abe1901e49ee1c5ce56c3ec081db177ef
4. Scorer V1 manifest SHA: cca4a57732cb9ba53c504c69c2abd4248e11281d535499e3ad055b13ec74e71c
5. Semantic Judge V1 integrity: verifisert; contract, gold, official results, stability, manifests og adapter re-hashet identisk ved oppstart og lukking
6. Historical files changed: 0

## Kontrakthypotese og labels (7-13)

7. Route-contract hypothesis: CANONICAL/EQUIVALENT-distinksjonen er ikke noedvendig for correctness-scoring naar begge tilfredsstiller acceptable_routes-kontrakten
8. Old score-bearing route labels: CANONICAL_ACCEPTABLE, EQUIVALENT_ACCEPTABLE, PARTIAL, NO_ACCEPTABLE_ROUTE, UNRESOLVED
9. New score-bearing route labels: ACCEPTABLE, PARTIAL, NO_ACCEPTABLE_ROUTE, UNRESOLVED
10. Diagnostic route detail retained: YES (CANONICAL, ALIAS, SEMANTIC_EQUIVALENT, NONE, UNRESOLVED; ikke score-baerende)
11. Uncertainty contract changed: NO (labels uendret; kun avklarende instruksjonstekst i kalibrering)
12. Critical contract changed: NO
13. Forbidden contract changed: NO

## Kontrafaktisk projeksjon (14-19)

14. Burned counterfactual run: YES (mechanical-only, ingen modellkall)
15. Original V1 overall accuracy: 61/66 = 92.42 %
16. Projected V1.1 overall accuracy: 98.48 %
17. Original route accuracy: 13/17 = 76.47 %
18. Projected route accuracy: 17/17 = 100 %
19. Counterfactual marked non-validation: YES (BURNED_COUNTERFACTUAL_NOT_VALIDATION)

Projeksjonen gjenopprettet ikke full stabilitet (87.5 % -> 91.67 %). Resterende ustabilitet ligger pa ACCEPTABLE<->PARTIAL og NO_ACCEPTABLE_ROUTE<->UNRESOLVED, ikke pa den kollapsete grensen.

## Kalibrering og frysing (20-22)

20. Calibration used: YES, 20 fixtures, 3 kjoeringer, 3 prompt-iterasjoner
21. Calibration N: 20 (5 per dimensjon); final modal match 16/20, stabilitet 18/20
22. Prompt/contract frozen before official validation: YES (prompt sha 541dca57b8fe4142c775976d2a60bd00d5f65ac2dd50adc3e4952731ffacf24d; contract file sha fc47022f24038507e6c95f0559ea6cbd4c4e1ed03805013a2b8ba1bf52047f70)

## Fresh validation data og agreement gates (23-32)

23. Fresh validation fixtures N: 80 (20 per dimensjon; route-miks 10/5/3/2; 6 injection-fixtures)
24. Human pass-1/pass-2 agreement overall: 75/80 = 93.75 %
25. Critical agreement: 20/20 = 100 %
26. Forbidden agreement: 20/20 = 100 %
27. Route agreement: 18/20 = 90.0 %
28. Uncertainty agreement: 17/20 = 85.0 %
29. Disagreements adjudicated: 5 (gold IKKE frosset; fil merket .UNFROZEN.json)
30. Validation gold SHA: IKKE FROZEN (agreement gate feilet)
31. Model/config: openai/gpt-5.6-luna via lokal proxy, temperature 0
32. Prompt frozen before official validation: YES, men official validation ble aldri startet

## Gate-utfall (33)

33. Agreement gate: FAIL
  - Krevet: overall >= 95 %, per dimensjon >= 90 %
  - Oppnaadd: 93.75 % overall; uncertainty 85 %
  - Konsekvens per preregistrert protokoll: ingen modellkjoring mot official fixtures; status SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY

## Ikke utfoert pga. gate-stop (34-48)

34-48. Official validation, FALSE_ACCEPTABLE-telling, stability suite, route stability, uncertainty-diagnostikk, evidence-span validity pa modellresultat, injection gate og combined scorer: NOT_RUN eller NOT_CREATED. Aldri startet; ingen resultater fabrikkert.

Deterministisk QA som ble utfoert:

- Schema failure tests: PASS (malformed JSON, V1-labels som invalid enum, manglende spans, span utenfor svar, ekstra felt, gyldig baseline)
- Baseline integrity: PASS (10/10 SHA re-verifisert identisk ved lukking)

## Root-cause analyse av agreement-feilen (49)

Ingen av de 5 uenighetene ligger pa den kollapsete CANONICAL/EQUIVALENT-grensen (0 treff). Fordeling:

- 2x NO_ACCEPTABLE_ROUTE vs UNRESOLVED: bevisst vage svar ("Det finnes steder ungdom kan gaa..."). Pass 1 leser mangel av konkret rute som NO_ACCEPTABLE_ROUTE; pass 2 folger UNRESOLVED-regelen. Begge deler av svaret er forsvarlig; kriteriet burde trolig ha vaert PARTIAL-referert eller mer presist designet.
- 2x SATISFIED vs NOT_REQUIRED: adversarielle kriterier med "Stillers ikke usikkerhetskrav". Frivillig forsiktighet utloste SATISFIED hos pass 1. Dette er samme score-benigne grense V1 allerede dokumenterte.
- 1x PARTIAL vs UNRESOLVED: "Dette kan variere." mot kriterium om aa uttrykke lokal variasjon. Grad av eksplisittethet er en reell gradvis grense.

Konklusjon: kontraktsreparasjonen (collapse) fungerer som designet pa route-aksen; agreement-feilen kommer fra (a) vaghetsdesign i mine egne fixtures og (b) den bevart-uendrede uncertainty-grensen, som tasken eksplisitt forbyr aa reparere her.

## Status og videre (68-71)

68. STATUS: SEMANTIC_JUDGE_V1_1_CONTRACT_NOT_READY
69. Ready for burned Phase B when a legitimate SUT exists: NO
70. Remaining limitations: uncertainty SATISFIED<->NOT_REQUIRED grensen er fortsatt ustabil for annotatorer; vaghetsdesign i UNRESOLVED/PARTIAL-testmassen trenger skjerpede designregler; official modellatferd er umalt i denne tasken
71. Recommended next bounded stage:
  1. Fixture-design-revisjon (ingen modellkall): skriv designregler som forbyr vage "noe finnes"-svar uten referansepunkt, og bytt ut de 5 uenighetsfixtures med minst like harde varianter. Gjenbruk de 75 enige fixtures etter re-hash.
  2. Ny dual-label med sammekravede gates. Ved PASS: fortsett den frosne V1.1-kontrakten til official validation uten prompt-endring.
  3. Separat oppfoelging forblir anbefalt: UNCERTAINTY_BOUNDARY_FOLLOWUP (SATISFIED/NOT_REQUIRED/PARTIAL-grensen), siden tasken forbyr a endre den her.

STOPP: ingen full SUT, ingen Phase B, ingen product holdout, ingen runtime patching.
