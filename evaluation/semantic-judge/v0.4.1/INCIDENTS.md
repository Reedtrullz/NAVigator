# INCIDENTS - v0.4.1 run

## 2026-08-31T22:11 - freeze-manifest.md regenerert ved uhell under pre-flight

Bakgrunn: Ved frys-verifisering ble v0.3/freeze_manifest.py kjort for a verifisere manifestet.
Skriptet skriver manifestet pa nytt; det er ikke et skrivebeskyttet verifiseringsverktoy.

Konsekvens: freeze-manifest.md fikk nytt "generated:"-tidsstempel (2026-08-31T20:11:33Z; lokal tid 22:11:33 CEST).

Konsekvensanalyse (fullstendig):

1. De 13 kildefilene er uendret: alle 13 SHA256-verdier i det regenererte manifestet matcher
   uavhengig shasum-kontroll gjennomfort samme minutt. De to hashene som ble registrert
   i denne sesjonen FOR overskrivingen (holdout-v2-answer-key 6c6c355b4e92d1c8bf20555dd357896a950086f328744b10c5e1e79fa552e3b7,
   holdout-v2-claims 49e274820799354f855c23314223a1b961b9cc3454fffc69e28a2d37ec92046a) er identiske foer/etter.
2. Metadata-seksjonen (model/judge/prompt-SHA256/aggregator) leses fra
   results/v03-results-calibration-A-judge-a-gpt-5.5.json, hvis mtime er 05:42 i dag
   (foer denne hendelsen, SHA256 e35dc24cd75674bc6d67855a22bc7aaa7d06b22a1ce23804331fe81ead54e16c) - kilde uendret.
3. Skriptet er deterministisk gitt uendrede inputs; eneste variable felt er "generated:".
   Det gamle manifestets SHA256 var b34be366a27bac095f4dc66b5418417a712006c630fa372bdbff8a97794c489e
   (registrert foer overskriving). Ny SHA256: 4548c28c881339807cd6595fa96bd8c38c861a8bf6b510d1cfcb6cee771fe733.
   Differansen reduseres dermed beviselig til tidsstempellinjen.
4. Ingen andre frosne filer ble rort av hendelsen.

Klassifisering: BENIGN - manifestets bevisverdi (13 frosne hasher + terskler) er intakt og uendret.
Prosedyrefiks: Aldri kjor freeze_manifest.py igjen under v0.4.1; verifisering skjer utelukkende med
shasum -a 256 mot de registrerte hashene.
