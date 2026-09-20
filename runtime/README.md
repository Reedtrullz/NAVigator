# Runtime – status og innganger (per 20.09.2026)

**Autoritet:** planen (G05/G06/G09, Fase 4). Denne fila dokumenterer faktisk
inngang og kjente defekter. Den endrer ingen kode, frosne kontrakter eller
låser.

## V1 replay (SUT-inngang for fasemålinger)

- `runtime/sut/pipeline.py` med `runtime/sut/phase2/` er den faktiske
  inngangen som evalueringskjøringene i `evaluation/` har brukt (V1-replay).
- Testmengde: `runtime/sut/test_*.py` (pipeline, schemas, sikkerhet,
  nasjonale ruter, normalisering, separasjon, evidens).
- Kunnskapstilgang skjer via `runtime/sut/phase2/knowledge.py`; regler i
  `data/rules-v1.json`.

## V2.5 (separat CLI, blokkert)

`runtime/discovery_v2` / orchestrator V2.5 er en separat kjede og er **ikke**
inngang for fase 3-målingene. Dokumenterte defekter (plan G05/G08/G09):

1. `runtime/discovery_v2/orchestrator_v25.py` (linje ~128, 138, 172, 207):
   fabrikerte fasit-/ruteelementer i discovery-stien.
2. `runtime/sut/phase2/knowledge.py` (`retrieve`, linje ~153): Mari-journal
   (`data/knowledge-index-v1.json`, klassifisert `SOURCE_DOCUMENTATION`)
   hentes uten privatport; journalfakta kan lekke i generell modus.
3. Oppgavelås-sti-feil (task-lock path) i V2.5-kjøringen.

Disse er **sperrender for brukerprodukt** (G05/G08/G09). De repareres ikke her;
det krever en egen eierautorisert oppgave utenfor COMPLETE-protokollåsen.

## Hva som ikke er dokumentert her

Ingen ytelsestall, ingen "ferdig"-status og ingen garanti for at V2.5 kan
kjøre. Historiske evalueringsresultater i `evaluation/` gjelder V1-replay ved
deres kontrolltidspunkt og er ikke attest for dagens innhold.
