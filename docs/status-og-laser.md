# Status og låser – autoritativt kart per 20.09.2026

**Repo-versjon:** commit ed156f1 (fjern) = lokal arbeidskopi før 20.09-implementeringen.
Dette dokumentet er **statuskart og autoritetskjede**, ikke en endring av historiske
låser. Frosne filer, låsefiler og historiske resultater er uendret.

## Låsekart

| Lås / oppgave | Status i fil | Gyldig omfang | Autoritativ avklaring (20.09) |
|---|---|---|---|
| `TASK-LOCK.json` (NAV-EXPLORE-MUNICIPAL-MENTAL-HEALTH-SAMPLE-V1) | `ACTIVE` | 24-kommuners grunnutvalg, frosset 2026-09-08; ingen ny juss/BUP/evaluator | Eiers oppgave 18-23 er en **deltagrense** av dette utvalget; låsen forblir aktiv som råvarehus for de 24, men denne videreføringen berører bare de 12. Ingen nye kommuner åpnes. |
| `TASK-LOCK-18-23-ROUTING-GAP.json` | `ACTIVE` | 12 kommuner, lokal rutingsleveranse; forbud mot ny juss/blindverk/kontakt | Står `ACTIVE` mens fil 72 omtaler arbeidet som `COMPLETE`. Det er ikke dokumentert at låsen er lukket. Låsefilen inneholder ingen human-gold-/kjøreport; den porten gjelder den separate reviewer-oppgaven (`evaluation/reviewer-minimum-tier-fresh-batch-v1/TASK-LOCK.json`). Fil 72s `COMPLETE` gjelder leveranseinnhold, ikke låsestatus. Eventuell administrativ lukking av lokaloppgaven krever eierbeslutning. |
| `TASK-LOCK-LOCAL-ACCESS-DISCOVERY-V1.json` | `COMPLETE` | Tilgangsmodell/oppdagelsesprotokoll; parent_task = 18-23 | Konsistent: underoppgave fullført innenfor parent-låsens ACTIVE-ramme. Ingen konflikt. |
| `parent_sample`-sti i 18-23-låsen | `data/municipality-sample.json` | — | **Sti-pekefeil, ikke manglende fil:** fila finnes på rotnivå (24 oppføringer, verifisert 20.09 ved commit 4d911e2); låsen skriver feilaktig `data/`-prefiks. Datasett i leveransen er `data/municipal-mental-health-sample-v1.json`. Dokumentert i `data/18-23-korrigeringsprotokoll-v1.json`; låsefilen endres ikke. |

## Komponentstatus (faktisk inngang, ikke versjonsnummer)

| Komponent | Status 20.09 | Kommentar |
|---|---|---|
| Kunnskapssenter (Markdown, fil 00–73) | Delvis samstemt | Akuttgrunnlag rettet 20.09 (fil 00/45/47). Øvrig samstemming følger fase 3. |
| `data/rules-v1.json` + juridisk index | Lagret evidens | Verifisert 29.–30.08.2026;Lovdata-kjede i `data/legal-index.json`. Ny nasjonal kontroll krever eget unntak. |
| 12-kommuners rutingsleveranse | Historisk, identitetskonflikt dokumentert | 12 koder korrigert via protokoll; 8/24 baseline-celler avvik i fil 72 §3; frosset utvalg forblir autoritativ baseline. |
| Runtime V1 replay | Eneste SUT-inngang | V1-replay er inngang for fasens målinger; qa_check dekker grep-mønstre. |
| Runtime V2.5 | Blokkert | Separat CLI; dokumenterte defekter (G05/G08/G09) er produktsperrer, ikke med i mål C. |
| Evaluator / blindmåling | Lukket | Ingen åpning; historiske resultater er ikke faglig attest. |
| Publiseringsprofil | Under bygging, **distribusjon BLOCKED** | `data/publiseringsprofil-v1.json`: navngitte personseksjoner og private kryssreferanser i kjernefiler skal scrubbes i egen oppgave før generell eksport. |
| Verifikasjonsregister | Under bygging | `data/verifikasjonsregister-v1.json` (handlingsbærende påstander i kjerne). |

## Fil-/leselister

Fil- og leselister per nivå samles i `README.md` /
`INNHOLD.md` (innhold), `data/qa-log.md` (kontrollhistorikk) og
`evaluation/README.md` (måleartefakter). Dette dokumentet peker, dupliserer
ikke; dekningen i pekerne er ikke verifisert komplett. Råresultater i
`evaluation/` er metadata-/innholdslesing hver for seg;
ingen er automatisk faglig attest for dagens innhold.

## Kjent avvik: hash-pinner i kunnskapindeksen (notert 20.09, ikke fikset)

`data/knowledge-index-v1.json` har foreldede sha256-pinner for
`00-BESLUTNINGSTRE.md` (`f886cb95…`) og `45-beslutningstre-hvem-ringer-jeg.md`
(`7624bffe…`); faktiske filer og `data/release-manifest-v1.json` har
`9d1d4187…` henholdsvis `ca9048f0…`. `runtime/sut/phase2/knowledge.py` er
fail-closed ved SHA-mismatch, så indeksen gir ikke usikret tilgang, men pins
kan ikke fikses uten eierbeslutning (låsgrense).

## Manifest-disposisjon (notert 20.09, etter commit 6e1f78a)

`data/release-manifest-v1.json` er et historisk kilde-manifest: hashene er
bundet til filtilstanden ved gjenoppbyggingen 20.09 (før korreksjonsrunden).
`sha256`/`bytes` for `data/18-23-korrigeringsprotokoll-v1.json`,
`data/verifikasjonsregister-v1.json`, `data/publiseringsprofil-v1.json` og
`docs/status-og-laser.md` er dermed foreldet. Manifestet er bevart uendret
og er ikke rehashet; det skal ikke fremsettes som bevis for nåværende
filinnhold. Nytt kilde-manifest lages kun ved neste eierautoriserte kandidat.
Eksport-manifestene (lokale pakker) og den frosne runtime-kunnskapindeksen er
separate artefakter og blandes ikke med kilde-manifestet.

## Lokal arbeidskopi

Lokal arbeidskopi var identisk med commit ed156f1 før 20.09-endringene
(akuttretting, korrigeringsprotokoll, statusdokumenter). Differansen er
implementeringens egen diff og er rekonstruerbar via git.

## Personvernaudit 20.09 (uavhengig agent)

Audit fant navngitte Mari-seksjoner med avledede saksfakta i fil 63 (§ 9),
64 (§ 10), 65 (§ 6) og 66 (§ 6), personhenvisning i fil 00 (linje 56) og
69 (linje 85), og kryssreferanser til private/avledede filer i flere
kjernefiler (bl.a. 48, 51, 68 og data/legal-index.json). Telling med
`grep -rliw "Mari"`: 170 filer totalt, 24 utenfor evaluation/, 146 i
evaluation/. Konsekvens: generell distribusjon er BLOCKED til scrub-oppgavene
som er listet i `data/publiseringsprofil-v1.json` (`pre_export_scrub`) er
utført og re-auditeres. Ingen scrub er utført i denne etappen.
