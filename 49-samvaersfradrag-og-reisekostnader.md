# 49. Samvaersfradrag og reisekostnader

**Etappe**: Barnebidrag, bidragsforskudd, samvaersokonomi (batch 2)
**Sist verifisert**: 29.08.2026
**Status**: Satser verifisert mot Lovdata rundskriv v1-55-02 (fulltekst hentet via r.jina.ai-proxy 29.08.2026) og nav.no/barnebidrag (oppdatert 25.08.2026). Klassegrensene (netter/mnd per klasse) er IKKE offisielt tabellfestet av NAV; de fastsettes av NAVs samvaersalkulator. Dette er et notert kunnskapshull.
**Kryssreferanser**: 48-barnebidrag-i-dybden.md (beregningsmodellen), 35-foreldreansvar-bosted-samvar.md, 51-familieokonomi-etter-samlivsbrudd.md, 53-kildedokumentasjon-okonomi.md

---

## 1. Hvorfor samvaersfradrag finnes

Nar bidragspliktig har samvar med barnet, har hen reelle kostnader i samvarsperiodene (mat, transport, fritid, hygien). Barnets underholdskostnad m da dekkes av begge foreldre i de periodene barnet er hos samvarsforelderen. Fradraget i barnebidraget speiler dette.

Grunnlaget i rundskrivet (punkt 4) er samvaersutgifter satt opp av SSB forbruksundersokelse: mat og drikke, helse og hygiene, lek og fritid, transport. Ved klasse 3 og 4 kommer ogsa boutgifter med (overanalyseres ikke her; satsene under inkluderer dette).

## 2. Nar gis fradraget

Fra nav.no/barnebidrag:

- Samvar pa MER enn 2 dager i gjennomsnitt per maned gir grunnlag for fradrag.
- Samvaret m enten vare avtalt (muntlig eller skriftlig samvaersavtale) eller offentlig fastsatt (rettsforlik, dom, eller avtale Statsforvalteren har fastsatt).
- Samvaret m FAKTISK gjennomfores. Avtalt men ikke gjennomfort samvar gir ikke fradrag.
- Samvar uten overnatting gir alltid samvaersklasse 1.
- Ved DELT FAST BOSTED er samvaersfradrag som hovedregel IKKE aktuelt; da fordeles underholdskostnaden etter inntekt i stedet.

## 3. Samvaersklasser

Klassene er bygd opp av regelmessig samvar gjennom aret pluss ferier og hoytider. NAVs samvaersalkulator (live per 29.08.2026) regner ut hvilken klasse som skal legges til grunn ut fra det regelmessige samvaret og samvar i ferier/hoytider. NAV publiserer ikke en offisiell tabell over nøyaktige netter per klasse; bruk kalkulatoren. Det er likevel kjent at:

- Klasse 0: ingen/ubetydelig samvar (ingen fradrag)
- Klasse 1: lavt samvar; inkluderer alt samvar uten overnatting
- Klasse 2: middels samvar
- Klasse 3: hoyt samvar; boutgifter regles med
- Klasse 4: svaert hoyt samvar (men fortsatt ikke delt fast bosted); boutgifter regles med

Fradragssatser per barnets alder, fra 1. juli 2026 (kr per maned):

| Alder | Klasse 1 | Klasse 2 | Klasse 3 | Klasse 4 |
| --- | --- | --- | --- | --- |
| 0-5 ar | 386 | 1 277 | 3 249 | 4 078 |
| 6-10 ar | 510 | 1 690 | 3 825 | 4 801 |
| 11-14 ar | 627 | 2 078 | 4 366 | 5 481 |
| 15+ ar | 696 | 2 306 | 4 684 | 5 880 |

Til sammenligning, satser fra 1. juli 2025 (for historikk): K1: 332/469/578/656; K2: 1 099/1 553/1 915/2 172; K3: 2 950/3 582/4 088/4 446; K4: 3 703/4 497/5 133/5 582. Sjablongene justeres 1. juli hvert ar.

### Maskinlesbar tabell (JSON)

```json
{
  "tabell_id": "samvaersfradrag-satser",
  "gyldig_fra": "2026-07-01",
  "sist_verifisert": "2026-08-29",
  "kilde": "Lovdata rundskriv v1-55-02 punkt 4; nav.no/barnebidrag",
  "enhet": "NOK_per_maned",
  "alder_grupper": ["0-5", "6-10", "11-14", "15+"],
  "klasser": {
    "klasse_1": {"0-5": 386, "6-10": 510, "11-14": 627, "15+": 696},
    "klasse_2": {"0-5": 1277, "6-10": 1690, "11-14": 2078, "15+": 2306},
    "klasse_3": {"0-5": 3249, "6-10": 3825, "11-14": 4366, "15+": 4684},
    "klasse_4": {"0-5": 4078, "6-10": 4801, "11-14": 5481, "15+": 5880}
  },
  "regel_gjennomfort_samvar": true,
  "regel_ingen_fradrag_delt_fast_bosted": true,
  "regel_samvar_uten_overnatting_klasse": 1
}
```

Verifiseringsspor: navikt/bidrag-bidragskalkulator-api SjablonService.kt bekrefter at samvaersfradrag er punkt 4 i rundskriv v1-55-02, og /tmp/bk-api-29 + /tmp/bk-ui-29 e2e-mocks matcher de historiske satsene.

## 4. Avtalt samvar vs faktisk samvar

Dette er ett av de vanskeligste praktiske punktene.

| Situasjon | Konsekvens i bidragssaken |
| --- | --- |
| Avtalt 8 netter, faktisk 2 netter | Fradrag etter FAKTISK klasse (lavere), forutsatt at det er dokumentert |
| Samvar avtalt men aldri gjennomfort | Ingen fradrag; ingen kostnader for samvarsforelderen |
| Samvarsforelderen onsker samvar, men motparten nekter | Ingen fradrag sa lenge samvaret ikke gjennomfores. Saken kan sokes endret. Dersom det finnes dom/rettsforlik/bindende avtale og samvar blokkeres av uenighet, kan samvarsforelderen kreve tvangsbot hos tingretten (familierettslig spor, ikke o kolonomisk) |
| Barnet selv nekter a dra | Okonomisk: fradrag bortfaller nar samvar ikke gjennomfores. Familierettslig: alderen veies; fra 12 ar veies barnets mening tungt (barnekonvensjonen par. 12); det finnes ingen generell okonomisk konsekvens for barnet i seg selv |
| Foreldrene er uenige om hvor mye samvar som faktisk skjer | NAV vektlegger dokumentasjon (overleveringsavtaler, oppmote, meldinger). Bevisbyrden praksis: parten som onsker endring, dokumenterer; NAV vurderer. Ved uenighet kan NAV endre ut fra opplysningene som foreligger |
| Endring av samvarsfradrag | Soknad om endring; hovedregel fremover i tid; 12-prosentterskelen gjelder bidraget samlet |

Kilder: nav.no/barnebidrag (oppdatert 25.08.2026), verifisert 29.08.2026.

### Bevisbyrde og dokumentasjon

- NAV veier hva som er dokumentert: skriftlig avtale, dom, rettsforlik, meldingslogg, kalender, oppmotesedler.
- Ved uenighet om faktisk samvar kan NAV fastsette ut fra de mest sannsynlige opplysningene; partene kan klage (3 uker).
- Bidragssaken skal IKKE brukes til a konkludere om hvem som har skyld i en foreldrekonflikt; det er familierettslig spor (se fil 35, 37).

## 5. Bostedsmatrise

| Ordning | Samvaersfradrag | Kommentar |
| --- | --- | --- |
| Barnet bor fast hos en forelder | Ja, hvis samvar > 2 dager/mnd og gjennomfores | Klassen fastsettes ut fra faktisk samvar |
| Mye samvar (men fortsatt ett fast bosted) | Ja, klasse 2-4 etter kalkulator | Narmer seg ikke delt fast bosted med mindre avtale/vilkar oppfylt |
| Delt fast bosted (par. 36) | Som hovedregel NEI | Underholdskostnaden fordeles etter inntekt i stedet |
| Avtalt delt fast bosted som ikke folges | Ja; saken beregnes som fast bosted | Faktisk omsorg slår avtale |
| 50/50 tidsfordeling uten par. 36-delt bosted | Ja | Tidsfordeling alene gir ikke delt fast bosted |
| Samvar uten overnatting | Klasse 1 | Alltid, uavhengig av antall dager |

## 6. Reisekostnader ved samvar

Verifisert mot nav.no/barnebidrag (29.08.2026):

- Reisekostnader ved samvar er IKKE en del av barnebidraget og IKKE en del av samvaersfradraget.
- Hovedregelen: foreldrene skal dele reisekostnadene forholdsmessig etter inntekt.
- Det er altsa en egen fordelingsregel, uavhengig av barnebidragssaken.
- Foreldrene kan avtale annen fordeling enn hovedregelen.
- NAV kan i FA TILFELLER fastsette fordelingen av reisekostnader, men NAV kan IKKE kreve dem inn. Det er en vesentlig forskjell fra barnebidrag.
- Dersom det er uenighet og partene ikke finner frem til en avtale: reisekostnadssporsmalet kan avklares gjennom familierettslige kanaler (avtale, rettsforlik, dom ved foreldretvist). Statsforvalteren behandler bosted/samvar, men fastsetter normalt ikke pengebelop i reisekostnader. Se fil 35/37.

### Hva regnes som reisekostnad

- barnets reise mellom foreldrene (tog, buss, fly, bil, bomring, ferge)
- foreldres reise for henting/levering (kjorelengde, drivstoff, bom, ferge)
- andre nodvendige kostnader direkte knyttet til gjennomforing av samvar

### Praktisk

- Avtale fordelingen skriftlig (for eksempel i foreldresamarbeidsavtalen).
- Dokumenter: billetter, kvitteringer, kjorebok med km, bom- og fergekostnader.
- Ved uenighet: dokumenter og ta saken opp i mekling eller familierettslig prosess; evt. sok NAV om fastsetting i de fa tilfellene der NAV kan fastsette.

## 7. Grensetilfeller

- Uregelmessig samvar: NAVs samvaersalkulator tar utgangspunkt i regelmessig samvar pluss ferier/hoytider; svart uregelmessig samvar kan gi klasse 1 eller ingen fradrag. Dokumenter det faktiske monsteret.
- Ferier/hoytider: legges inn i kalkulatoren som del av arlig samvar.
- Hvis samvar ikke gjennomfores i en periode (for eksempel sykdom), kan fradraget avvike i den perioden; endringssoknad gjelder ved varig endring.
- Flerbarnssaker: fradraget beregnes per barn.

## 8. Kunnskapshull

- NAVs samvaersalkulator: de interne klassegrensene (netter/mnd per klasse) er ikke offisielt tabellfestet. NAV omtaler bare klassene og at kalkulatoren fastsetter dem. Notert i fil 53.
- Reisekostnader: grensene for nar NAV kan fastsette fordeling er ikke detaljert tabellfestet i kildene som er hentet; NAV understreker at inkreving ikke er mulig.
- Forskriftens eksakte Lovdata-ID er ikke funnet; rundskriv r55-02 og v1-55-02 er brukt som autoritative mellomkilder.

---

## Kilder (batch 2)

- Lovdata rundskriv v1-55-02 (rundskriv til barnelova, punkt 4), fulltekst hentet 29.08.2026
- nav.no/barnebidrag (oppdatert 25.08.2026)
- nav.no samvaersalkulator (live per 29.08.2026)
- navikt/bidrag-bidragskalkulator-api (SjablonService.kt) og -ui (e2e-mocks)
