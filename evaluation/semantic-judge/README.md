# Semantic judge pilot (NAV Explore)

Separat semantisk evalueringslag ved siden av den eksisterende leksikalske
scoreren. Versjon: semantic-judge-v0.2 (laast; se judge-spec.md).

## Filer

| Fil | Innhold |
|---|---|
| judge-spec.md | Låst spec v0.2: prompt, terskler, versjonshistorikk |
| calibration-set.json | 84 kalibrerings-claims (inkl. 4 injections) |
| expected-results.json | Ground truth (aldri judge-input; 3 label-korreksjoner dokumentert) |
| holdout-set.json | Blindt holdout-sett (40 claims, bygget av separat subagent) |
| run_semantic_judge.py | Runner (codex exec via lokal proxy; resumable; JUDGE_VERSION-stttet) |
| compute_metrics.py | 4x4 confusion, per-klasse P/R/F1, binaer FP, grupper, confidence, konsistens |
| compare_judges.py | A/B-sammenligning + fusion-analyse |
| judge-results-*.json | Råresultater per sett/dommer/versjon (v0.1 arkivert) |
| metrics-*.json | Beregnede metrikker |
| comparison-calibration-v0.2.json | A/B agreement, A/B/C/D-grupper, fusion-FP |
| calibration-report.md | Hovedrapport for kalibrering |
| disagreement-log.md | Alle A/B-avvik med vurdering |
| final-report.md | Sluttrapport med alle 33 obligatoriske punkter og gate-vurdering |
| ent-controls-set.json + ent-controls-expected.json | ENT-A..D kontroller |

## Kjoring

    python3 evaluation/semantic-judge/run_semantic_judge.py --set calibration --judge A --runs 1
    JUDGE_VERSION=v0.2 python3 evaluation/semantic-judge/run_semantic_judge.py --set holdout --judge A --runs 1
    JUDGE_VERSION=v0.2 python3 evaluation/semantic-judge/compute_metrics.py
    python3 evaluation/semantic-judge/compare_judges.py

Krever at lokal proxy kjører på 127.0.0.1:10100. Auth kopies til mktemp-mappe
ved kjoretid og lagres aldri i workspace.
