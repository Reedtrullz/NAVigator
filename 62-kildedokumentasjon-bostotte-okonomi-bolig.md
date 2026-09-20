# 62. Kildedokumentasjon: bostotte, sosialhjelp og boligtrygghet

Alle kilder lest og verifisert 30.08.2026 med mindre annet er oppgitt.

## Offisielle nettsider

| Kilde | Brukt i | Notis |
| --- | --- | --- |
| nav.no/barnetrygd | fil 54, 51 | ordinr 2 012, Finnmarkstillegg 512 fra 01.02.2026; lest 29.08 og 30.08.2026 |
| nav.no/utvidet-barnetrygd | fil 54 | delt utvidet 1 286; modifiedTime 26.08.2026, hentet 30.08.2026 |
| husbanken.no/person/bostotte/ | fil 55 | frister 25. og utbetaling 18./20.; lest 30.08.2026 |
| husbanken.no/person/bostotte/hvem-kan-fa-bostotte/ | fil 55 | alder, boligkrav, saksgang, samspill sosialhjelp, AAP/dagpenger-regel; sist oppdatert 19.06.2026 |
| husbanken.no/person/bostotte/beregning-av-bostotte/ | fil 55 | boutgiftstak, egenandel, minsteutbetaling 61 kr, unge uf ore, overgangsordning |
| husbanken.no/person/bostotte/beregning-av-bostotte/boutgifter-som-legges-til-grunn-for-beregningen/ | fil 55 | 613 kr/mnd oppvarming; driftssats 14 732 kr/ar |
| husbanken.no/person/bostotte/inntektsgrunnlaget/ | fil 55 | inntekt over 20 ar, formue fra 18 ar, fribelop 6 672 kr kapitalinntekt, formuefribelop 333 557 / 700 468, 65 prosent formuestillegg, AAP/dagpenger 2/3, lista over ytelses unntatt |
| husbanken.no/person/bostotte/delt-fast-bosted/ | fil 55, 54 | barneloven § 36, folkeregistreringskrav, endre soknad |
| husbanken.no/person/bostotte/har-sokt-eller-mottatt-bostotte/ | fil 55 | endringsmelde, klage, automatisk stopp etter tre avslag |
| husbanken.no/person/bostotte/klage/ | fil 55 | tre ukers frist, kommune, Husbanken, klagenemnd |
| husbanken.no/person/startlaan/ og soke-startlaan-og-tilskudd/ | fil 60 | kriterier, kommunens rolle, betjeningsevne, 10-ar-sporet |
| husbanken.no/husleietvist/ | fil 57, 58 | Husleietvistutvalget: veiledning, mekling, bindende avgjorelse |
| tjenester.husbanken.no/bostotte-kalkulator/index.html | fil 55 | HTTP 200, lenket aktivt; live-beregning IKKE kjort |
| nav.no/okonomisk-sosialhjelp | fil 56, 57, 61 | satser 01.01.2026, barnetrygdunntak, nodhjelp, depositumsgaranti, dokumentasjon, klage; oppdatert 26.08.2026 |
| nav.no/midlertidig-botilbud | fil 59 | § 27-plikten, forsvarlighet, vedtak og klage; oppdatert 04.07.2025 |

## Lovverk

| Lov | Paragrafer verifisert | Brukt |
| --- | --- | --- |
| Sosialtjenesteloven (lov 2009-12-18-131) | § 1 (formal, andre ledd), § 17, § 18, § 19, § 20, § 20a, § 21, § 23, § 25, § 27, § 28, §§ 29-35 | fil 56, 57, 58, 59, 61 |
| Husleieloven (lov 1999-03-26-17) | § 3-8, § 5-8, § 9-2, § 9-7, § 9-8, § 9-9, § 9-11 | fil 57, 58 |
| Barneloven (lov 1981-04-08-7) | § 36 (delt fast bosted) | fil 54, 55 |
| Boligsosialloven (lov 2022-12-20-121) | §§ 3-7 (ansvar, vanskeligstilte, individuell bistand, vedtak og klage) | fil 58, 59 |
| Folketrygdloven | § 3-21, § 3-22 (ung ufor, sitert av Husbanken) | fil 55 |

Lovdata-tekster ble lastet 30.08.2026. Husleieloven er sist endret ved lov 12.06.2026 nr. 22 i kraft 01.07.2026; de siterte paragrafene er kontrollert mot den naverende teksten.

## Dokumentasjon og personvern ved sosialhjelp

Fra nav.no/okonomisk-sosialhjelp (lest 30.08.2026) er dette oppgitt som soknadsdokumentasjon:
fakturaer og kvitteringer for det du sokr om, skattemelding, skatteoppgjor, lonnsslipp,
kontooversikter som viser ALLE dine konti med saldo, husleiekontrakt, legitimasjon og
gyldig oppholdstillatelse. Nav tar kontakt hvis de trenger mer.

Verifiserbart om personvern:

- NAV kan be om kontooversikter som del av den individuelle vurderingen; listen ovenfor er NAVs egen side. Det er soknadsdokumentasjon, ikke automatisk overvakning.
- Periode for kontoutskrifter er IKKE verifisert i denne etappen; ikke oppgi antall maneder uten ny sjekk.
- Sosialtjenesteloven § 23 (uriktige eller manglende opplysninger) er hjemmel for refusjonskrav; det er grunnen til at alle inntekter skal meldes.
- Forholdsmessighet: forvaltningslovens opplysningsplikt og § 17-samarbeidet betyr at etaten skal innhente det som trengs for saken; ekstrem innhenting er ikke automatisk lovlig. Kommunen skal veilede i stedet for a blokkere nodhjelp bak papirkrav (nav.no: raskt svar i nodssituasjon).
- Taushetspligt: saksbehandlere har taushetsplikt; saken kan deles med kommunens boligsosiale tjeneste ved individuell plan (stl. § 28). Detaljert personvernavklaring for sosialhjelp er ikke fullt verifisert i denne etappen.

## Verifiseringsmetode

1. Sider lastet via curl mot r.jina.ai (markdown-eksport) og lagret lokalt for sitatsjekk.
2. Paragrafnumre lest direkte fra Lovdata-tekster (sosialtjenesteloven, husleieloven, boligsosialloven).
3. Belop og frister kopiert fra NAVs og Husbankens egne sider, ikke fra sekundarkilder.
4. Kalkulatoren kontrollert med HTTP-status, ikke full nettleserberegning.

## Kunnskapshull etter denne etappen

1. Live-beregning i bostottekalkulatoren er ikke utfort (krever JS-okt); URL og tilgjengelighet er verifisert.
2. Gjeldsordningsloven: paragrafnummer og naverende innfrielseperiode er IKKE verifisert; Lovdata- og domstol- sok feilet eller ga indirekte treff (fil 60).
3. Husbanklovens paragraf for boligsosialt virke (tradisjonelt § 5) er ikke direkte verifisert mot Lovdata; boligsosialloven (LOV-2022-12-20-121) §§ 3-7 er verifisert og brukt som anker. Ikraft-dato etter § 11 (fra den tiden Kongen bestemmer) er ikke verifisert.
4. Periode for kontooversikter og detaljert personvern ved sosialhjelpssaker er ikke verifisert.
5. Kommunale kriterier for kommunal bolig, depositumsordninger og eventuelle egne sosialhjelpssatser er kommunale og ikke generert her.
6. Stromstotteordninger endres ofte; kun peker til regjeringen.no er med.

## QA

scripts/qa_check.sh kjort etter skriving; se data/qa-log.md for etappelogg.
Mari-regresjon: ingen diagnose innfort i fil 61; scenarioene avhenger ikke av utredningsutfall.
