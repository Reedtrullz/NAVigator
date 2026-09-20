# Evaluation – hva målingene beviser (og ikke beviser) (per 20.09.2026)

**Autoritet:** planen (G11/G12, Fase 4). Dette er et lesingskart over
historiske målearbefider. Ingen av dem er faglig attest for dagens innhold, og
ingen ny måling er startet i denne etappen.

## Oversikt over målearbeider

| Artefakt | Hva det målte | Siste rapporterte resultat | Hva det IKKE beviser |
|---|---|---|---|
| `baseline-results.json`, `final-results.json` | KB-regresjon (gulnruter) mot V1-replay | 48/48 BESTÅTT (30.08) | Ikke semantisk korrekthet; lexikalsk scorering. |
| `evaluator-regression/` | Evaluator-selvkalibrering: positive/negative kontroller, mutasjoner, akronymer | TP=24, TN=96, FP=0, FN=0 (30.08) | Ikke SUT-kvalitet; den måler scorens egen diskriminering. |
| `full-sut-implementation-phase2/-phase3/` | Strukturell 120-cases kjøring + replay mot V1 | Rapportert i respektive `final-report.md`/metrics | Ingen blindmåling; case er ikke uavhengig; resultater er datert. |
| `full-sut-repair-wave-1..4-v1/` | Reparasjonsbølger mot V1-replay | Wave 4: se `final-report.md` | Defektene G05/G08/G09 er ikke fikset; wave-resultat gjelder V1-sti. |
| `semantic-judge/` | Semantisk dommer-kalibrering/stabilitet (RC1-RC4-sett) | Rapportert per versjon i `results/` | Ikke fullstendig uavhengig re-sertifisering av juridiske påstander. |
| `scenarios.json`, `expected-routing.json` | Case- og gulnrutedefinisjoner | S43 lukket 30.08 | Definisjoner er ikke bevis for runtime-atferd. |

## Felles begrensninger

1. **Datert:** alle resultater gjelder kontrolltidspunktet i hver rapport
   (hovedsakelig 29.–31.08.2026). Innholdsendringer etterpå (f.eks. akutt-
   rettingen 20.09) er ikke re-målt.
2. **Ikke blind:** case, forventninger og SUT deler opphav i dette repoet;
   ingen uavhengig blindmåling er gjennomført.
3. **Lexikalsk grunnlag:** scorer er term-basert; semantisk entailment er bare
   delvis dekket av judge-kalibreringene.
4. **Låsgrense:** evaluatorlåsen er lukket. Ny måling, blindopplegg eller
   semantisk kampanje krever egen begrunnelse og eksplisitt åpning.

## Tillatt bruk

Historiske resultater kan siteres som **datert kvalitetsindikasjon** for
V1-replay. De skal ikke fremsettes som "QA godkjent" for dagens referansebase,
og de åpner ikke for brukerprodukt (runtime-sperrene i
`runtime/README.md` gjelder fortsatt).
