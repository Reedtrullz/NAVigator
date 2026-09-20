# Novelty Report

Mechanical novelty check (construction_tools.check_novelty) compared
all 231 authored candidates against the disallowed corpora (Blind V1,
Blind V4, old dev, RC2/RC3 regressions, compound dev corpus, holdout-v2,
novel-40, diagnostic-20, operator regressions).

- Candidates: 231. Rejects: 0. Max similarity: 0.529 (threshold 0.60).
- Per-case rows: construction-audit.sealed (novelty-pass1.json).
- Case authoring never read the disallowed corpora; only the checker did
  (development data firewall, spec 12).
