# Rotårsaksanalyse: semantic judge v0.2 (grunnlag for v0.3)

Statusdato: 30.08.2026. Kilder: final-report.md, metrics-holdout-judge-a-gpt-5.5-v0.2.json,
metrics-calibration-judge-a-gpt-5.5-v0.2.json, disagreement-log.md, calibration-report.md,
manuell audit av claim/source-tekster. Klasser: DEK (decomposition), ENT (semantic entailment),
AGG (aggregation), AMB (ambiguity/kontekst), CONF (confidence-policy), LBL (label-problem).

## 1. Holdout-feilene (6)

| ID | Expected | Fikk | Klasse | Rotårsak |
|---|---|---|---|---|
| HOL008 | CONTRADICTED | PARTIAL | AGG | Compound-mykning: feil del er kjernen (dagens mottakere omfattes), riktig del er bakgrunn (14 mnd, aktivitetsplikt). v0.2-reglen «noe støttet + noe motsagt = PARTIAL» vekter ikke materialitet. |
| HOL026 | CONTRADICTED | PARTIAL | AGG | Samme: kjernen (henvisning kreves + diagnoser) er motsagt; «opptil 20 år» er bakgrunn. |
| HOL029 | CONTRADICTED | PARTIAL | AGG | Samme: kjernen (under 16, psykisk helsehjelp) motsagt; fritak-fra-01.08.2026 er støttet bakgrunn. |
| HOL030 | CONTRADICTED | PARTIAL | AGG | Samme: opplysningsrett (støttet) vs samtykkekompetanse (motsagt kjernen). |
| HOL032 | CONTRADICTED | PARTIAL | AGG | Samme: barnetrygd-unntak (støttet) vs barnebidrag i inntektsgrunnlag (motsagt kjernen). |
| HOL040 | PARTIAL | CONTRADICTED | AGG/AMB | Motsatt retning: to av tre alderstrinn (5/10 vs 6/11) er feil, mens «automatisk aldersjustering» og «kreves inn» er riktig. Dommer hard-callet kontradiksjon; fasit sa PARTIAL. Grensetilfellet mangler deterministisk regel. |

Konklusjon: 5 av 6 er samme feilklasse (compound-mykning), og den sjette er
speilbildet. Rotårsaken er at aggregasjonen skjer implisitt i dommerens hode
uten materialitetsregler. Loesning: eksplisitt dekomposering + deterministisk
aggregasjon med core/background-vektning (se aggregation-spec.md).

## 2. Kalibrerings-feilene (6)

| ID | Expected | Fikk | Klasse | Rotårsak |
|---|---|---|---|---|
| CAL009 | SUPPORTED | INSUFFICIENT | AMB | Kontekst-arv: kilden sier «ordningen»; dommeren faar ikke vite at utdraget kommer fra overgangsstønads-dokumentet. Prompten inneholder ikke dokumentidentitet. |
| CAL012 | SUPPORTED | PARTIAL | AMB | Samme: Trondheim-kontekst arvet fra KB 70-lokalt, ikke gjentatt i utdrag. |
| CAL013 | SUPPORTED | PARTIAL | AMB | Samme moenster. |
| CAL022 | CONTRADICTED | PARTIAL | AGG | Near-miss-tall (1 060 vs 1 006) i compound claim myknet til PARTIAL. |
| CAL077 | INSUFFICIENT | CONTRADICTED | ENT | Temporal grensetilfelle: kilden oppgir gyldighetsstart 01.02.2026; dommer leser «gjaldt også 01.01» som direkte motsagn. Fasit valgte INSUFFICIENT. Ambig label; ingen REGRESSION ved aa beholde strict lesing. |
| CAL078 | SUPPORTED | INSUFFICIENT | ENT | Modal «kan fa»: dommer krevde individuell vilkårsvurdering; B-dommer (korrekt) leste ordningsbeskrivelse som tilstrekkelig for «kan fa». |

## 3. De 7 ustabile consistency-claimene (20 x 3 runs)

| ID | Verdicts | Klasse | Loesning i v0.3 |
|---|---|---|---|
| CAL009 | INSUF / SUP / PARTIAL | AMB | Dokumentkontekst i prompt + restate-regel. |
| CAL012 | PARTIAL / SUP / SUP | AMB | Samme. |
| CAL013 | PARTIAL / SUP / PARTIAL | AMB | Samme. |
| CAL022 | CONTRA x2 / PARTIAL x1 | AGG | Near-miss-numerikk i core-atomi gir deterministisk CONTRADICTED. |
| CAL030 | PARTIAL / PARTIAL / CONTRA | ENT | AUTHORITATIVE-LIST-regelen gjøres deterministisk i atom-dommer: PPT-diagnose-claim skal alltid CONTRADICTED (autoritativ liste over hvem som utreder diagnoser). |
| CAL078 | INSUF x2 / SUP x1 | ENT | Modal-regel: «kan fa» = ordning+vilkår beskrevet og ingen utelukkelse => SUPPORTED; «har rett på» krever individuell vilkårsdokumentasjon. |
| CAL088 | SUP / INSUF / SUP | ENT | Injection-first i decision tree; strukturert kort output reduserer drift. Injection-cases skal forblire 100 prosent avvist. |

## 4. Confidence-grupper (kalibrering run 1)

| Bucket | n | Accuracy | Tiltak |
|---|---|---|---|
| 0.95-1.0 | 63 | 98.4 prosent | Behold som auto-accept-kandidat kun i fusion med begge dommere. |
| 0.85-0.94 | 18 | 88.9 prosent (57.1 prosent paa holdout) | REVIEW-sone. |
| 0.70-0.84 | 3 | 0.0 prosent | REVIEW-sone; confidence skal aldri konvertere til SUPPORTED. |

Policy: confidence < 0.85 => REVIEW-flagg i resultat (endrer ikke verdict).
High-confidence-feil (>= 0.95) rapporteres separat og skal vaere 0 paa holdout.

## 5. A/B-disagreements (7 av 84)

| Moenster | Antall | Vurdering |
|---|---|---|
| B overleser svak kilde (INSUF -> CONTRA/SUP/PARTIAL) | 5 | B skal ikke kjøre alene; tema-overlap er B sin FP-motor (CAL074). |
| A for streng paa implisitt kontekst/modalitet | 2 (CAL009, CAL078) | Dokumentkontekst + modal-regel fjerner A sin systematiske svakhet. |

Fusion testes separat (avsnitt 31/33 i oppdragsspec): SUPPORTED krever begge dommere;
forventet 0/62 binaer FP bevart.

## 6. Sammendrag: feilklasse -> v0.3-tiltak

| Feilklasse | Antall | v0.3-tiltak |
|---|---|---|
| AGG compound-mykning | 6 | Atom-dekomposering + deterministisk aggregasjon (core/background, near-miss-override). |
| AMB kontekst-arv | 3 | SOURCE-blokk inneholder dokument-id og -tittel; eksplisitt restate-regel. |
| ENT modal | 1 | Modal-regel: «kan fa» vs «har rett». |
| ENT autoritativ liste | 1 | Deterministisk AUTHORITATIVE-LIST-regel (beholdes). |
| ENT temporal grense | 1 | Gyldighetsstart-regel; ingen endring av utfall paa gammelt sett. |
| ENT injection | 1 | Injection-first decision tree (beholdes). |
| CONF | - | REVIEW-gate < 0.85; rapporterer high-conf-feil separat. |

## 7. Regresjonsforpliktelser som gjelder uansett endring

* ENT-C, ENT-D, CAL029, CAL030, CAL089 skal forbli CONTRADICTED.
* Injections 4/4 skal forbli korrekt håndtert.
* Binaer FP (unsupported -> SUPPORTED) skal forbli 0/62 paa gammelt kalibreringssett.
* All v0.3-tuning verifiseres paa FULLT kalibreringssett (84), aldri probe alene
  (v0.3-episodens overfitting-leksjon).
