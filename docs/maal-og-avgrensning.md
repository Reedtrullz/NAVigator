# Mål og avgrensning – første referanseutgave (mål C)

**Dato:** 20.09.2026. **Autoritet:** eierbeslutning samme dag; plan i
`~/Downloads/NAVigator-tilstand-og-veikart-2026-09-20.md` (§ 2.2, Del 4).
**Repo-versjon verifisert mot:** commit ed156f1 (lokal arbeidskopi).

## Valgt mål

NAVigator ferdigstilles først som en **versjonert, avgrenset norsk referansebase**
(mål C). Ingen chatflate, ingen live-ruting, ingen ny evaluator- eller
blindaktivitet inngår. Runtime-feilene (G05/G08/G09) forblir sperrer for et
eventuelt senere brukerprodukt og repareres ikke her.

## Faglig kjerne

Kjernen for første utgave er **familie, barn/unge og tilknyttede helse-, skole-
og økonomiinnganger**: beslutningstrærne og fagrapportene med sammenhengende
dekning for disse behovene. Andre NAV-temaer beholdes som tydelig merket
orientering og arver ikke kjernens verifikasjonsstatus automatisk.

## Lokalt scope

Lokal handlingsstøtte begrenses til de samme **12 kommunene** i gjeldende
TASK-LOCK-18-23-ROUTING-GAP (frosset utvalg i
`data/municipal-mental-health-sample-v1.json`). Annet allerede innsamlet
kommunestoff (inkludert de 24 i grunnutvalget) beholdes som datert bakgrunn og
utvider ikke oppdraget.

## Utgivelseskrav

1. **Dekning er endelig avgrenset.** Et godkjent manifest navngir temaer,
   kommuner, alders-/målgrupper og dokumentversjoner. Hver inngang er merket
   `kontrollert`, `delvis`, `historisk` eller `ikke dekket` for dette formålet.
2. **Handlingsbærende påstander er etterprøvbare.** Første kontakt,
   henvisningskrav, rettighetsvilkår, frister og beløp som får stå i godkjent
   beslutningsstøtte, har kilde, relevant versjon/dato, anvendelsesområde og
   navngitt kontrollør. Føres i `data/verifikasjonsregister-v1.json`. Et åpent
   kritisk hull betyr at handlingen ikke presenteres som avklart.
3. **Dokumentene er samstemte.** Støttede ruter i fil 00, 26 og 45 motsier ikke
   hverandre eller tilhørende regler. Historiske regresjonsrapporter beholdes;
   ny kontroll dokumenteres separat (eksempel: fil 47 seksjon 3b).
4. **Personlig materiale er privat.** Generell profil inneholder verken
   journalfakta eller avledede personopplysninger. Privat profil er eksplisitt
   valgt og får ikke status som generell rettskilde. Se
   `data/publiseringsprofil-v1.json`. **Per 20.09.2026 er generell distribusjon
   BLOCKED**: uavhengig personvernaudit fant navngitte personseksjoner
   (fil 63 § 9, 64 § 10, 65 § 6, 66 § 6) og kryssreferanser til private filer i
   kjernefiler; scrub-oppgavene i profilen må utføres og re-auditeres før
   porten åpnes.
5. **Usikkerhet og vedlikehold virker i praksis.** Manglende lokal rute,
   utilgjengelig kilde og ukjent ventetid fremgår som slike tilstander. Hver
   handlingsbærende påstand har ansvarlig kontrollør, nykontrolldato og en regel
   for å trekke utdatert handlingsråd tilbake (registeret, felt `recheck`).

## Full kommuneoversikt er ikke krav

Full kommuneoversikt og observerte lokale ventetider er **ikke** absolutte krav
for denne utgaven. Manglende data skal derimot uttrykkes korrekt som manglende
data, ikke som positiv dekning.

## Ikke-mål

Retting av runtime-kode, ny juridisk research utover lagret evidens,
kommunekontakt, nye kommuner, modellkall mot SUT, ny blindmåling, bred
renderer-opprydding og chatflate. Eventuell evaluatoråpning krever egen
begrunnelse og eksplisitt åpning av evaluatorlåsen.
