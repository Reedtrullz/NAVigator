# Polarity Wobble Audit (spec section 4)

Data: v0.4.1/results/v041-results-stability-C-judge-c-gpt-5.6-luna.json (150 rader, 30 claims x 5 runs, judge C = gpt-5.6-luna, sluttkode). Fasit: v0.3/expected-stability.json. Alle 30x5-rader er ferske under v0.4.1-sluttkode.

## Metode

For hvert wobble-id (9 id-er med modal verdict-konsistens < 100%): lest claim, source, forventet label, alle 5 runers ekstraherte primitiver (affirms/negates/modality/relations), og sammenlignet med de deterministiske signalene som faktisk finnes i claim/source-teksten. Ingen kode ble endret under auditen (forbudt: case-id-patches).

## Per-case funn

### CAL007 - expected SUPPORTED (numeric)
- Claim: "Barnetilsynsstønad dekker 64 prosent ... ingen stønad ved pensjonsgivende inntekt over 6 G."
- Source: "64 prosent av dokumenterte utgifter ...; ingen stønad ved pensjonsgivende inntekt over 6 G."
- Run-variasjon: A2 polarity flag flipper (aff=True neg=False -> aff=False neg=True) mellom runs; verdict S<->P.
- Deterministisk lesing: source inneholder både "64 prosent" (claim-numer: lik) og "ingen stønad ... over 6 G" (claim-negasjon: lik). Begge atomer er negasjonsenige med source. Quote-aligner: numeric EQUAL + negation AGREEMENT = SUPPORTED, deterministisk.

### CAL012 - expected SUPPORTED (local)
- Claim: "Ungdom 12-18 år i psykisk krise i Trondheim kan kontaktes via BUP Akuttenheten på 72 82 27 80."
- Source: "Ungdom 12-18 år i psykisk krise: BUP Akuttenheten 72 82 27 80; henvisning via legevakt/fastlege/poliklinikk."
- Run-variasjon: aff=True i alle runs, men verdict I<->S (runs 1/3: insuff). Ekstraktor-ubesluttsomhet om hvorvidt telefonnummer+alder+sted er "ekplisitt affirmasjon".
- Deterministisk lesing: claim-subjektstreng "Ungdom 12-18 år i psykisk krise" forekommer nesten verbatim i source; tallet 72 82 27 80 forekommer i begge; claim-modalitet "kan kontaktes" = MAY, source gir direkte kontaktinfo. Span-tilpasning: full støtte.

### CAL013 - expected SUPPORTED (local)
- Lik CAL012-mønster: "Barnevernvakta 90 28 70 37, døgnåpen" matcher både nummer- og døgnåpen-del. Run 3 kollapset til INSUFFICIENT uten at noen primitive flagg endret seg - ren run-flakring i ekstraksjonen.

### CAL035 - expected CONTRADICTED (legal)
- Claim: "Kommunene må gi RPH til alle fra 16 år." Source: "27 prosent har eget RPH-tilbud og 59 prosent svarte at de ikke har RPH" + "RPH er ikke standardtilbudet for barn".
- Run-variasjon: neg=False (runs 1/2/4/5) vs neg=True (run 3). Verdict I<->C.
- Deterministisk lesing: claim universal-kvantor "alle fra 16 år" + MUST ("må gi"); source har eksplisitt fravær-span "59 prosent svarte at de ikke har RPH" (eksistens-negation av tilbudet) + statistisk majoritet uten tilbud. Universal møter dokumentert eksistens-negation = contradiction med konkret span.

### CAL039 - expected CONTRADICTED (legal; samtykkes-regel, safety-relevant)
- Claim: "Barn under 16 år kan selv samtykke to BUP-utredning uten foreldres samtykke."
- Source: "Foreldre med foreldreansvar samtykker for barn under 16 år ... BUP: foreldrene under 16 år (begge med foreldreansvar). PRL § 4-3: barn over 16 år kan normalt selv gi samtykke."
- Run-variasjon: s_mod UNKNOWN (runs 1/3/4) vs MAY (runs 2/5); m_rel UNKNOWN vs CONFLICT. Verdict I<->C.
- Deterministisk lesing: age-opposisjon - claim gir under-16 selv-samtykke; source tildeler samtykke for under-16 til foreldre og gir selv-samtykke kun "over 16 år". Aldersintervall-disjunksjon (under-16 vs over-16) + tildelt aktør (foreldre) = contradiction med span "Foreldre med foreldreansvar samtykker for barn under 16 år".

### CAL048 - expected PARTIALLY_SUPPORTED (safety)
- A1 som CAL013 (støtte). A2: "barnevernet krever foreldrenes samtykke før undersøkelse" vs source "Ingen samtykke nødvendig for undersøkelse" = eksplisitt negasjonskonflikt med span.
- Run-variasjon: A2 primitiver identiske i alle 5 runs (neg=True, conflict), men verdict P<->C - fusionsregelen (SUP+CONTRA co-equal = PARTIAL) ble kun brukt i runs 1/2; runs 3-5 aggregerte til CONTRA til tross for støttet A1.
- Deterministisk lesing: begge atomer deterministisk løsbare; v0.3-aggregasjon regel 3c gir PARTIAL.

### CAL054 - expected PARTIALLY_SUPPORTED (legal)
- A1 "Barnets mening skal høres fra 7 år" = direkte støtte (verbatim span). A2 "barn under 16 år kan selv gi samtykke til BUP-utredning" - source tildeler samtykke til foreldre uten CAL039s eksplisitte selv-samtykke-over-16-kontrast i nærheten? Source har "PRL § 4-3: barn over 16 år kan normalt selv gi samtykke" - men i CAL054-source mangler dette spanet (kun foreldre-tildeling). 
- Run-variasjon: A2 aff=False i alle runs; verdict P<->I (run 5 kollapset hele til INSUFF).
- Deterministisk lesing: A1 SUPPORT (verbatim align); A2: ingen affirmasjonspan + alder/tildeling = INSUFFICIENT. Fusion: PARTIAL.

### CAL067 - expected CONTRADICTED (safety, korrigert fasit v0.3)
- Claim: "Helsesykepleieren kan love en 15-åring full taushet uansett hva som skjer."
- Source: "Taushetsplikt kan kun brytes av lovfestet unntak, for eksempel hpl § 23, eller med samtykke."
- Run-variasjon: verdict C<->I<->C<->C<->C; run 3 la til neg=True.
- Deterministisk lesing: claim universal absolutt-løfte "full taushet uansett hva som skjer"; source predikat "kan kun brytes av lovfestet unntak" = eksplisitt begrenset sekretess - universal absolutt-claim møter eksplisitt unntaksbetingelse ("kun ved lovfestet unntak") = contradiction med span.

### CAL079 - expected INSUFFICIENT_EVIDENCE (numeric)
- Claim: "≈ 12 000 kr/mnd" ved 40 000/mnd lønn. Source: kun eksempel ved 30 000/mnd -> 14 663 kr/mnd.
- Run-variasjon: verdict C<->I (runs 1/2/5: CONTRA via near-miss tall).
- Deterministisk lesing: claim-tall 12 000 kan ikke alignes til source-tall 14 663 fordi de gjelder ulike inntektsgrunnlag (40 000 vs 30 000). numeric_comparable = false (forskjellig beregningsgrunnlag), ingen affirmasjon av claim-tallet -> INSUFFICIENT.

## Tverrgående mønster

1. Affirm/negate-flagg fra Luna er den eneste rullekilden: subject/scope-matching var 100% stabile på tvers av alle 150 rader.
2. 7/9 wobble-id-er kan løses fullt deterministisk fra quote-signaler: verbatim tall-paritet (CAL007/012/013/079), eksplisitt negasjonsspan (CAL035/048), aldersintervall-opposisjon (CAL039/054), universal-vs-unntak (CAL067).
3. 2/9 (CAL048/054) er fusions-avvik der atomverdicts var deterministisk løsbare men aggregatoren fikk motstridende flagg-input.
4. Ingen wobble krever case-id-logikk; alle mønstre er generaliserbare tekstsignaler.

## Konklusjon for design (spec seksjoner 5-24)

- Quote-aligner må levere deterministisk polarity fra: verbatim term/tall-alignment, negasjons-scope, aldersintervall, modalitet (gjenbruk v0.4.1 modality.py), universal/unntak-kvantorer.
- Fusion må følge v0.3 aggregation-spec regel 1-5 med atom-verdicts fra quote-aligner (SUP+CONTRA co-equal = PARTIAL).
- Luna-span-finder er kun fallback når ingen span kan alignes; fidelity-sjekk (verbatim) er obligatorisk.
