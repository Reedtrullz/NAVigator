# Novelty report - RC2 blind set V2 construction

Mechanical checker (novelty-checker.py) compared every candidate claim against the four prior benchmark corpora (Blind V1, old development cases, operator regressions, RC2 regressions). The checker returned similarity scores and rejection categories only; the case author never saw old claim text.

Pre-registered thresholds: token Jaccard 0.55, char-3-gram 0.80, skeleton entity overlap 0.5, exact 1.0.

| Wave | Candidates | Exact rejects | Near rejects | Skeleton rejects | Retained | Max similarity retained |
|---|---|---|---|---|---|---|
| a1 | 32 | 0 | 0 | 0 | 32 | 0.3750 |
| a2 | 34 | 0 | 0 | 0 | 34 | 0.3636 |
| b1 | 40 | 0 | 0 | 0 | 40 | 0.5000 |
| c | 48 | 0 | 0 | 0 | 48 | 0.4444 |
| d | 65 | 0 | 0 | 0 | 65 | 0.5385 |
| e | 58 | 0 | 0 | 0 | 58 | 0.5000 |
| Total | 277 | 0 | 0 | 0 | 277 | 0.5385 |

All 277 candidates passed the pre-registered novelty gates and were retained for annotation. Maximum similarity among retained candidates is 0.5385 (wave d), below the 0.55 Jaccard gate. Source-fidelity rejects: 0 (277 checks, all verbatim). No candidate was rejected after annotation; all 277 cases (160 CORE + 117 reserve) are covered by the sealed answer key. Per-case labels are not disclosed in this report.
