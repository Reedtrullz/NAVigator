# V2.4 FRESH HOLDOUT - LOCAL DISCOVERY RUNTIME

Task: `NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-V2_4-FRESH-HOLDOUT`

Terminal status: **LOCAL_DISCOVERY_RUNTIME_V2_4_FRESH_HOLDOUT_FAIL**

One-shot fresh holdout of the frozen V2.4 site-direct runtime (candidate manifest
`6f7e7ab3...393a2d`, unchanged throughout) on 15 fresh municipalities / 30 cells
(19-year and 22-year scenarios per municipality), centrality classes 2-6, selected by
deterministic ordinal municipality-number selection. Class 1 excluded by preregistered
pool exhaustion.

## Pipeline (strict H0-H11, completed in order)

H0 candidate integrity -> historical integrity -> H1 capability readiness (burned data only)
-> failure policy freeze -> H2 exposure registry -> H3/H4 sample freeze -> H5 one-shot
execution (30/30) -> H6 prediction freeze -> H7 independent blind audit (2 GPT-5.6-Luna
subagents, 30/30 resolved) -> H8 audit freeze -> H9 mechanical scoring -> H10 official
score freeze -> H11 error analysis.

## Result summary

| Metric | Result | Gate | Verdict |
|---|---|---|---|
| Complete discovery | 24/30 | >= 29/30 | FAIL |
| Route recovery | 24/30 (80%) | >= 90% | FAIL |
| FULLY_VERIFIED precision | 3/10 (30%) | >= 95% | FAIL |
| Access precision | 8/15 (53%) | >= 95% | FAIL |
| Unsupported FULLY_VERIFIED | 7 | = 0 | FAIL |
| Critical false-no-route | 0 | = 0 | PASS |
| Provenance completeness | 10/10 (100%) | = 100% | PASS |
| Epistemic-state accuracy | 3/30 (10%) | >= 90% | FAIL |
| Materially overconfident outputs | 14 | = 0 | FAIL |

Gates passed: 14 of 21 (integrity, readiness, sample, freeze, audit, safety and provenance
gates all held; the failures are discovery robustness and epistemic-state quality).

## Root causes (error analysis only after score freeze; no patching performed)

1. Six discovery misses (Klepp, Kvitsøy, Tysvær): root + sitemap attempts only, zero
   content pages extracted, renderer never triggered; runtime returned canonical
   DISCOVERY_INCOMPLETE (fail-closed, not false no-route). Auditor found documented routes
   on the same or adjacent official sources, incl. 3 intermunicipal + 1 specialist gateway.
2. Seven FULLY_VERIFIED overclaims: service provenance landed on section-level pages
   instead of audit-cited specific service pages; two lacked confirmed age eligibility.
3. User-facing uncertainty wording asserts certain access on 14 EXISTENCE_ONLY cells.

## Integrity notes

- External search calls: 0. Historical writes: 0. Candidate unchanged after run.
- Deviations preserved permanently: `h5-kill-deviation.json` (operator killed frozen
  1146-C process at 175s by bookkeeping error; no evidence consumed before the single
  authorized identical rerun) and crash-resume SKIP lines (one official run per cell).

## Key artifacts

- `official-score-v2-4.json` (SHA `0aa3fb08...c11e4`) - all hard gates, frozen before error analysis
- `mechanical-score-v2-4.json`, `mismatch-analysis-v2-4.json`
- `runtime-predictions-v2-4.json` (SHA `dea6c215...31fda`), `audit-reference-v2-4.json` (SHA `6b2ff2fb...b720`)
- `final-report.md` - 110-point sluttrapport
- `security-observations.json`, `network-call-audit.json`

No reruns, no patching, no sample extension, no runtime modification were performed
after score freeze. Recommended next stage: separate engineering task with fresh lineage
(discovery fallback chain, stricter FV semantics, access extraction, wording harmonization),
then a new fresh holdout.
