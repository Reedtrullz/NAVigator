# Source Fidelity Report - RC2 Blind V3

Date: 2026-09-04. Tooling: deterministic verbatim-span check; per-candidate results in construction/fidelity-report.json and construction/fidelity-gap-wave.json.

## Gate result: PASS

| Item | Value |
|---|---|
| Candidates checked | 282 (277 reused + 5 gap-wave) |
| Fidelity failures | 0 |
| All spans verbatim | yes |

Every claim is supported by source excerpts copied verbatim from the knowledge base (kb_ref and line ranges retained per source_id). The check is byte-exact on excerpt text: no paraphrase, no normalization, no silently merged spans. Fidelity failure would have failed construction QA (hard gate); the QA input carried failures=0.

The gap-wave cases (RC2B-0278 through RC2B-0282) were checked with the same checker against their authored sources and are included in the 282 total (construction/fidelity-gap-wave.json, all verbatim).
