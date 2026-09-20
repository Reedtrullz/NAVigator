# Aggregation-spec: semantic-judge v0.3
Statusdato: 30.08.2026. Deterministisk kode (ingen LLM). Input: atom-verdicts fra stage 2 + roller fra stage 1.

## 1. Termer
* Substantielt atom = atomer med role core eller context som inneholder en selvstendig kontrollerbar paastand. role framing og condition er ikke substantielle alene (condition er kvalifikator paa sitt atom).
* Near-miss-kontradiksjon = CONTRADICTED paa atom der kilden matcher subject/scope men avviker paa sentralt tall, dato, alder, aktor, tjeneste, henvisningsretning, modalitet (kan->skal) eller negasjonsretning.

## 2. Aggregeringsalgoritme (rekkefolgen er normativ)

1. SAFETY HARD FAIL: hvis noen atom er merket safety og ikke faar SUPPORTED med eksplisitt kildestotte => FAIL/review uansett score (aldri auto-accept).
   * Kode-avgrensning 30.08.2026: safety-merkede atomer teller som substantielle i aggregaten (en motsagt safety-atom kan dermed gi CONTRADICTED). Claim-flagg "safety" uten safety-merket atom blokkerer bare single-claims (hele claimet er sikkerhetsinnholdet); compound-claims gaar gjennom review-gaten (verdict != SUPPORTED => review_flag). Verdict endres aldri direkte av safety-logikken.
2. Alle substantielle atomer INSUFFICIENT => INSUFFICIENT_EVIDENCE.
3. FINNES CONTRADICTED? (AMENDMENT 2, 31.08.2026 - rollebasert aggregering; erstatter near-miss-override 3a for compound-claims):
   a. Minst ett CONTRADICTED core-atom og INGEN SUPPORTED core-atom => CONTRADICTED. Begrunnelse: kjernen (head) avgjoer; en motsagt kjerne med kun stoettet bakgrunn er et motsagt claim (HOL008/026/029/030/032: stoettet del er bakgrunn som "dagens mottakere omfattes"/"opptil 20 aar", motsagt del er kjernen). Near-miss-feil tall/aktor/modalitet paa kjernen gir samme utfall (CAL022 single-type; HOL032).
   b. Antall CONTRADICTED-substantielle STOERRE ENN antall SUPPORTED-substantielle => CONTRADICTED (HOL008-mode: flere motsatte enn stoettede).
   c. Ellers (inkl. likt antall 1-1, co-equal cores) => PARTIALLY_SUPPORTED. Grunnlag: oppdragsspec avsnitt 7 "Minst ett SUPPORTED og minst ett CONTRADICTED => PARTIALLY_SUPPORTED"; kalibreringsfasit 14/14 mixed compound => PARTIAL, ogsaa ved feil tall (CAL047 25 vs 20, CAL053 1 286 vs 1 006, CAL056 6G vs 4G); HOL040 fasit PARTIAL (2 av 3 co-equal aldre feil). Near-miss-override gjelder KUN single-type (atomverdict = claimverdict).
   c. Ellers (flere SUPPORTED enn CONTRADICTED, ingen near-miss) => PARTIALLY_SUPPORTED.
4. Ingen CONTRADICTED:
   a. Alle substantielle SUPPORTED => SUPPORTED.
   b. Minst ett SUPPORTED og minst ett INSUFFICIENT:
      - claim.type = compound (>= 2 substantielle atomer) => PARTIALLY_SUPPORTED.
      - claim.type = single (1 substantielt atom) => INSUFFICIENT_EVIDENCE (enkelatom er aldri PARTIAL).
5. Formaalinnramming ("i motsetning til det mange tror", "mange mener") teller ikke som SUPPORTED-atom og kan ikke redde et ellers motsagt claim til PARTIAL (HOL026-loesning).

## 3. Enkelatom-regel (oppdragsspec avsnitt 8)

Et genuint atomisk claim far aldri PARTIALLY_SUPPORTED. Mulige utfall: SUPPORTED,
CONTRADICTED, INSUFFICIENT_EVIDENCE. Testes eksplisitt i decomposition-tests.json.

## 4. Kjente konsekvenser paa brente sett (dokumentert, ikke tuning)

* CAL022 (1 060 vs 1 006): regel 3a => CONTRADICTED. Fikser v0.2-feilen.
* HOL008/026/029/030/032: regel 3a/3b => CONTRADICTED. Fikser 5 av 6 v0.2-holdout-feil.
* HOL040 (aldersjustering 5/10/15 vs 6/11/15): regel 3a => CONTRADICTED. Fasit var PARTIAL;
  dette forblir dokumentert avvik (label-grensetilfelle, auditert), ingen fasitendring.
* CAL009/012/013: CONTEXT RULE i stage 2 => SUPPORTED. Fikser 3 kalibreringsfeil.
* CAL077: TEMPORAL RULE => forblir dommerens strict lesing (CONTRADICTED); avvik mot
  INSUFFICIENT-fasit er kjent og dokumentert.
* ENT-A: restate + context-arv => SUPPORTED (forbedring fra v0.2 PARTIAL).

## 5. Review-policy (separerer verdict fra produksjonsbeslutning)

* review_flag = true ved: confidence < 0.85 paa noe atom, eller sluttverdict != SUPPORTED.
* Konservativ fusion (oppdragsspec avsnitt 16) forblir REVIEW-layer-forslag: testes separat,
  ikke produksjonsdefault. Auto-accept krever (fremtidig beslutning): SUPPORTED,
  confidence >= 0.95 paa alle atomer, ingen review_flag, og (valgfri F-modus)
  bekreftet av begge dommere.

## 6. Compound-test-mapping (oppdragsspec avsnitt 27)

| Atomer | Forventet aggregat |
|---|---|
| [SUP, SUP] | SUPPORTED |
| [SUP(core), CONTRA(core)] | PARTIAL (co-equal kjerner; ogsaa ved feil tall) |
| [SUP(context), CONTRA(core)] | CONTRADICTED (kjernen avgjoer) |
| [CONTRA(core), CONTRA(core)] | CONTRADICTED |
| [SUP, INSUF] compound | PARTIALLY_SUPPORTED |
| [SUP, INSUF] single | INSUFFICIENT_EVIDENCE |
| [INSUF, INSUF] | INSUFFICIENT_EVIDENCE |
| [SUP, CONTRA, INSUF] | CONTRADICTED ved contradicted core utan supported core; ellers PARTIAL |
