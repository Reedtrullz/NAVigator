# Final Report: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1

## 1-7: Grunnlag og integritet

1. Task ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1
2. Prior scorer status: dev-corpus-scorer-v1 frosset, 26/26 fixtures, determinisme verifisert
3. Corpus manifest SHA: 9c265731e6e17ea54844b6db646dac4abe1901e49ee1c5ce56c3ec081db177ef
4. Scorer V1 manifest SHA: cca4a57732cb9ba53c504c69c2abd4248e11281d535499e3ad055b13ec74e71c
5. Corpus changed: NO
6. Gold changed: NO
7. Scorer V1 changed: NO

## 8-17: Implementasjon

8. Semantic dimensions implemented: 4 (critical_condition, forbidden_claim, route_equivalence, uncertainty)
9. Deterministic-first enforced: YES (adapter kaller kun dommer der deterministisk lag er UNRESOLVED)
10. Deterministic override by LLM count: 0
11. Judge model: openai/gpt-5.6-luna via lokal proxy
12. Judge config: temperature 0, max_tokens 250, 1 teknisk retry ved schema-feil, fail-closed til UNRESOLVED
13. Prompt frozen before validation: YES, sha256 c23fab9bda99d1eec5b3bd848e22d4a9584d05dcef838946352712920f297204
14. UNRESOLVED supported: YES (i schema, labels og fail-closed sti)
15. Evidence spans required: YES for alle non-UNRESOLVED verdicts
16. Evidence spans mechanically validated: YES (normalisert verbatim-substring av SUT-svar)
17. External factual knowledge allowed: NO (hantes i systemprompt; testet via injection-fixtures)

## 18-24: Kalibrering, valideringssett og gold

18. Calibration used: YES (3 kjoeringer; prompt-utvikling skjedde kun her)
19. Calibration N: 20 fixtures, siste kjoering 14/20 match; gjenlevende avvik er etikettegrenser (CANONICAL/EQUIVALENT, SATISFIED/NOT_REQUIRED) som er score-benigne
20. Validation fixtures N: 66 (16 critical, 17 forbidden, 17 route, 16 uncertainty; 4 injection-fixtures inkludert)
21. Human pass-1/pass-2 agreement: 61/66 = 92.4%
22. Adjudicated disagreements: 5 (alle paa route-dimensjonen; gold = designer_intent)
23. Validation gold SHA: e1925e6063d44d28fadd84d74b91bd6379f8939d21cf6b33cecdcb334b2b53e3
24. Overall validation accuracy: 61/66 = 92.42% (GATE FAIL: < 95%)

## 25-35: Dimensjonsresultater

25. Critical-condition accuracy: 16/16 = 100%
26. Critical false negatives: 0
27. Critical false positives: 0
28. Forbidden-claim accuracy: 17/17 = 100%
29. Safety-critical forbidden false negatives: 0
30. Forbidden false positives: 0
31. Route-equivalence accuracy: 13/17 = 76.47% (GATE FAIL: < 90%)
32. False route equivalence: 4 (alle er CANONICAL_ACCEPTABLE <-> EQUIVALENT_ACCEPTABLE grensetilfellet; begge labelene er aksept-positive i scoreren)
33. Uncertainty accuracy: 15/16 = 93.75%
34. False uncertainty violations: 0 (ingen VIOLATED-falskpositive)
35. Clearly-adjudicable UNRESOLVED rate: 0/66 = 0% (GATE PASS: <= 10%)

## 36-45: Robusthet og integrasjon

36. Injection fixtures: 4/4 PASS (SUT-innhold ble aldri fulgt)
37. Schema-invalid fixtures: 5/5 deterministisk avvist + 1 gyldig baseline PASS (malformed JSON, invalid enum, manglende span, span ikke i svar, ekstra felt)
38. Stability subset N: 24 (6 per dimensjon)
39. Runs per stability fixture: 5
40. Modal stability: 21/24 = 87.5% (GATE FAIL: < 95%). Exact 5/5-agreement paa 21 fixtures; all ustabilitet ligger i CANONICAL/EQUIVALENT-grensetilfellet. Safety-relevante verdier (TRIGGERED, PRESENT, VIOLATED, PARTIAL) var 100% stabile.
41. Deterministic criteria coverage: 7/93 kritiske betingelser
42. Semantic-required criteria coverage: 93 kritiske betingelser er semantic-capable (COVERAGE, ikke correctness)
43. Remaining unresolved criterion types: ingen; rendyrket flaskehals er CANONICAL/EQUIVALENT-etikettegrensen
44. Combined scorer integration: YES (evaluation/dev-corpus-scorer-v1-semantic/, no-override invariant)
45. Scorer integration tests: mock 26/26 identisk med stub; live adapter 3 hook-kall med korrekte routes; 0 overrides

## 46-54: Grenser og status

46. Full corpus Phase B run: NO
47. Runtime modified: NO
48. Fresh holdout used: 0
49. Future product thresholds derived: NO
50. Semantic judge manifest: semantic-judge-manifest.json (FROZEN_INSTRUMENT_STATE)
51. Combined scorer manifest: scorer-v1-semantic-manifest.json (FROZEN_INSTRUMENT_STATE)
52. Gates passed: critical FN 0; forbidden FN 0; injection 4/4; schema 5/5; UNRESOLVED rate 0%; critical accuracy 100%; forbidden accuracy 100%; uncertainty accuracy 93.75%; integrasjon; corpus/gold/scorer integrity
53. Gates failed: overall accuracy 92.42% < 95%; route-equivalence accuracy 76.47% < 90%; modal stability 87.5% < 95%
54. STATUS: DEV_CORPUS_SEMANTIC_JUDGE_V1_NOT_READY

## 55-57: Vurdering og neste steg

55. Is scorer now suitable for burned Phase B once full SUT exists: NO. Ikke foer route-etikettegrensen er reparert og validering gjenkjoeres mot nye fixtures.
56. Remaining limitations:
    - CANONICAL_ACCEPTABLE vs EQUIVALENT_ACCEPTABLE er en ustabille grense for modellen; begge er aksept-positive, men strict-label-gaten slaar feil.
    - NOT_REQUIRED vs SATISFIED-grensen var flertydig i kalibrering og ble kollapset i begge annotasjons-pass; score-benign (begge ikke-feilende) men strict-gaten kan ikke testes for den.
    - Gold-konstruksjonen bruker samme modellfamilie som dommeren; uavhengig menneske-gold vil styrke instrumentet.
    - Offisiell validering viste 0 UNRESOLVED: modellen er alltid sikker; en juridisk "uklar" bane er stadig umodent.
57. Recommended next bounded stage: egen begrenset task for route-etikette-kontrakt: kollaps CANONICAL/EQUIVALENT til et enkelt ACCEPTABLE-label i scorer-ekvivalensklassen (krever scorer-contract-endring i ny task, ikke i denne) eller boundary-hardening med nye kalibreringsfixtures; deretter nytt dobbelt-pass gold og ny official validation mot ferske fixtures. Ingen gjenbruk av naavaerende validation-sett.

## Historisk grunnlag

V4 er burn-development-only. RC2 official status (RC2_NOT_CERTIFIED) er urort.
Ingen GPT-5.5 er brukt. Kjoeringer: kalibrering 3x20, dual-label 132 kall,
official 66 kall, stability 120 kall, integration 3+ kall via proxy.
