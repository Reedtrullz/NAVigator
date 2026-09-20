# SLUTTRAPPORT - SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS

Dato: 2026-09-02. Alle tall verifisert mot resulttfiler generert av run_gate.py etter de siste sikkerhetsportene (dato/qualifier/aggregate).

1. Task lock: task_id SEMANTIC-JUDGE-TIER1-PROOF-OPERATORS; alle forbudte aktiviteter (Tier-2, packet R&D, holdout-v3, blind recert, live dialog, reviewer-tuning, NAV/kommune-research, KB-tuning) ikke utfort.
2. CI-046: INSUFFICIENT/INSUFFICIENT (semantisk/proof-safe). Motorens baseline CONTRADICTED (weak_contra_rule:exhaustive_list_exclusion) er en usikker over-tenning beholdt som historisk regressjonsbevis; kontrakt forbyr closed-world-slide paa umarkert referentliste.
3. CAL089: INSUFFICIENT (semantisk) + REVIEW_REQUIRED (proof-safe). Injisert instruksjonsblokk (S3) fjernet fra bevis; kontaminert dokument gir ingen auto-verdict.
4. Second-pass set: 32 kuraterte novel-tilfeller (uavhengig gpt-5.6-luna traad, ingen pass-1-lekkasje).
5. Semantisk enighet (pass1 vs pass2): 31/32 = 96.9%.
6. Proof-safe enighet: 23/32 = 71.9% (pass-1 proof-safe avledet under frossen doktrine).
7. Operator-enighet: 21/32 = 65.6% (10 operator-attribusjonsavvik med identisk verdict).
8. Annotationsdisputer: 0. 1 semantisk avvik (N-R1) avgjort RESOLVED_NEW_LABEL (INSUFFICIENT); 10 operator-avvik PASS1_CONFIRMED.
9. ENT-A current contract: SUPPORTED / INSUFFICIENT (semantisk / proof-safe).
10. ENT-B current contract: INSUFFICIENT / INSUFFICIENT.
11. ENT-C current contract: INSUFFICIENT / INSUFFICIENT.
12. ENT-D current contract: CONTRADICTED / CONTRADICTED.
13. Legacy/current separasjon: product_exact_legacy er egen LEGACY_SINGLE_TARGET_METRIC (389 rader, benchmark-etikett); kontrakt-evaluering skjares paa dual-utility (semantisk sannhet + proof-safe), ikke paa legacy-etikett.
14. Contract consistency: 0 brudd; alle dual-etiketter validerer mot frossen kontrakt.
15. Freeze manifest: 9/9 filer verifisert, NOT stale (results/freeze-verify.json).
16. Tier-1 operator-antall: 5 (ingen Tier-2).
17. DIRECT_ASSERTION: spec - lik polaritet, subject/scope/tid-kompatible premisser; resultat - 1 gylden fyring (ACT-25 -> SUPPORTED, korrekt), 150 abstentions, 0 false, 0 invalid.
18. EXPLICIT_NEGATION: spec - eksplicit omfangsavgrenset negasjon, alle claim-konsepter adressert; resultat - 0 fyrt, 0 false (N-R1-doctrine binder contra til equal/non-staff-subset).
19. NUMERIC_CONFLICT: spec - same-unit bounds under binding framing; resultat - 0 fyrt paa 389 rader, 0 false; aggregate-claim guard hindrer feilaktig sammenligning mot komponentpremiss.
20. TEMPORAL_CONFLICT: spec - eksplisitte datoankre, samme akse, delt tema; resultat - 0 fyrt, 0 false; date-as-value guard (bare datert utsagn uten frist/dato-anker gir abstain).
21. SIMPLE_ARITHMETIC: spec - dokumentert sum/diff rekalkulert til claim-verdi; resultat - 0 fyrt i gate, 0 false; exactly-one-relation gate og aggregate framing guard paa plass.
22. Operator unit tests: 34/34 PASS.
23. Proof validation: uavhengig re-derivasjon av hvert proof (proof_validator.py); 0 ugyldige proofs akseptert.
24. Cross-operator conflicts: 0 (spec 19 -> REVIEW).
25. Invalid accepted proofs: 0.
26. Tier-1 SUPPORTED precision: 1/1 (100%) - ACT-25 via DIRECT_ASSERTION, korrekt mot dual semantisk sannhet.
27. Tier-1 CONTRADICTED precision: ikke aktuelt - ingen kontradiksjonsoperator fyrt i korpuset (ingen false positives aa maale).
28. Critical auto errors: 2 foer (N-R1, ENT-C) -> 0 etter (begge retrahert til REVIEW_REQUIRED, spec 14).
29. Auto-dekning foer: 121/389.
30. Auto-dekning etter: 119/389.
31. Review rate foer: 27/389 = 6.9% (REVIEW_REQUIRED finals).
32. Review rate etter: 30/389 = 7.7%.
33. Reviews eliminert: 1 (ACT-25, review-path -> gyldig auto SUPPORTED).
34. Korrekt eliminert: 1/1.
35. Usikkert eliminert: 0.
36. Noedvendige reviews gjenstaaende: 9/9 dual-labellede review finals er noedvendige under kontrakten (+21 non-dual uendret).
37. Unnoedvendige reviews gjenstaaende: 0 blant dual-labellede. Gate-slice-metrikken (remaining_necessary=1, remaining_unnecessary=5) maaler baseline-review dual-rader der semantisk sannhet er avgjort men proof-safe=INSUFFICIENT - disse er annotasjonsdoktrine-gap (Tier-2-kandidater), ikke reviewerfeil.
38. Oracle-46 semantisk: 20/46 etter (19/46 foer; ACT-25 flyttet).
39. Oracle-46 proof-safe kvalitet: 33/46 etter (34/46 foer; retraksjonen endrer proof-safe-evalueringen for reraherte rader til korrekt REVIEW-haandtering - se evaluation-contract-results.json).
40. Oracle-46 produkt: 2/46 etter (1/46 foer; LEGACY_SINGLE_TARGET_METRIC).
41. Novel-40 semantisk: 27/40 etter (28/40 foer; N-A4 og N-R1 retrahert til kontrakt-riktig REVIEW).
42. Novel-40 proof-safe kvalitet: 31/40 etter (29/40 foer).
43. Novel-40 produkt: 25/40 etter (27/40 foer; LEGACY_SINGLE_TARGET_METRIC).
44. ENT current-contract: 2/4 semantisk match foer og etter; proof-safe 2/4 -> 3/4 (ENT-C retrahert korrekt).
45. Produkt selektiv noyaktighet: semantisk 45/80 paa dual-rader foer og etter (stabil).
46. Proof-safety metrics: invalid auto proofs 3 -> 0; critical auto errors 2 -> 0; validator-pass rate 100% paa aksepterte proofs.
47. Legacy metrikk: 317/389 -> 315/389 (LEGACY_SINGLE_TARGET_METRIC; -2 fra retraksjoner, +1/-1 fra ACT-25 flytt og dual-utility-haandtering).
48. Tier-2 kandidater observert: 28 (review-path, deduplisert, post-gate: dual rader med semantisk avgjort != INSUFFICIENT og proof_safe=INSUFFICIENT; ACT-25 gaatt ut av poolen etter gyldig auto-flytt).
49. Re-prioritisert Tier-2 backlog (etter inferensklasse, stoerste foerst): TRANSITIVE_EQUIVALENCE (7); SAME_PREDICATE_OPPOSITE_POLARITY (7); RULE_PLUS_CONDITION (4); DEFINITION_PLUS_INSTANCE (2); TEMPORAL_CONFLICT (2); NUMERIC_CONFLICT (2); SIMPLE_ARITHMETIC (1); RULE_PLUS_EXCEPTION (1); EXHAUSTIVE_SET_EXCLUSION (1); ACTOR_MEMBERSHIP (1).
50. Operator regressjons-suite: 16/16 PASS (operator-regression/).
51. ENT-C safety regressjon: baseline auto-CONTRADICTED mot INSUFFICIENT-sannhet er borte (retrahert); ENT-C forblir INSUFFICIENT/INSUFFICIENT under kontrakten.
52. ID guard: 0 brudd (check_id_guard.py; runtime-kode fri for case-ID-er).
53. KB regressjon: 48/48 PASS.
54. Evaluator regressjon: acc 1.00.
55. qa_check.sh: PASS.
56. READINESS: STOP_OPERATOR_EXPANSION - alle sikkerhetsporter bestaar (invalid 0, critical 0, SUPPORTED-precision 100%, validator pass, regressions rene), men review-reduksjon (1 rad) er ikke en meningsfull mengde; utvidelse uten ny annotasjonsdoktrine gir ikke forventet avkastning.
57. Blind recert: fortsatt ikke startes. Poolelementene (28) er doktrine-gap, ikke annotasjonsusikkerhet; recert forandrer ikke proof_safe-avledningen og gir ingen ny informasjon om Tier-1-operandflaten.
58. Gjenvaerende annotasjonsusikkerhet: lav - 1 semantisk avvik avgjort kontraktbasert (N-R1); 10 operator-attribusjonsavvik dokumentert; 0 disputter staar aapne. Non-dual review finals (21) er uannotert, ikke usikre.
59. Gjenvaerende arkitektonisk usikkerhet: Tier-1 leksikale dekning er smal ved design (hoy presisjon, lav recall); operator-attribusjon (65.6% enighet) viser at klassegrensene er subjektive selv med frossen kontrakt; proof_safe-avledning for pass-1 novel-rader er doktrine-simulert, ikke uavhengig annotert.
60. Anbefalt neste steg: annoter de 21 non-dual review finals og avgjoer om retraksjonstung konservativ postur er akseptabel som produktbeslutning; avgjoer deretter om en begrenset Tier-2-prototype (stoerste klasse foerst: TRANSITIVE_EQUIVALENCE + SAME_PREDICATE_OPPOSITE_POLARITY, 14 av 28 kandidater) er verdt aa prove - ikke start uten at begge deler er paa plass.
